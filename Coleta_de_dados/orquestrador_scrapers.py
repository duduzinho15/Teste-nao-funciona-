"""
ORQUESTRADOR DE SCRAPERS COM PLAYWRIGHT
========================================

Sistema centralizado para orquestrar a execução de todos os scrapers
usando Playwright. Gerencia rate limiting, agendamento, monitoramento
e consolidação de dados.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import signal
import sys

# Importar scrapers
from apis.playwright_base import PlaywrightBaseScraper
from apis.fbref.playwright_scraper import FBRefPlaywrightScraper
from apis.sofascore.playwright_scraper import SofaScorePlaywrightScraper
from apis.scraper_config import ScraperConfig

logger = logging.getLogger(__name__)

class OrquestradorScrapers:
    """
    Orquestrador principal para todos os scrapers.
    
    Funcionalidades:
    - Execução coordenada de múltiplos scrapers
    - Rate limiting inteligente
    - Agendamento automático
    - Monitoramento de saúde
    - Consolidação de dados
    - Tratamento de erros
    """
    
    def __init__(self, environment: str = "dev"):
        """
        Inicializa o orquestrador.
        
        Args:
            environment: Ambiente de execução ('dev' ou 'prod')
        """
        self.environment = environment
        self.config = ScraperConfig()
        self.scrapers = {}
        self.running = False
        self.stats = {
            "started_at": None,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_success": None,
            "last_error": None
        }
        
        # Configurar logging
        self._setup_logging()
        
        # Configurar signal handlers
        self._setup_signal_handlers()
        
        logger.info(f"🎭 OrquestradorScrapers inicializado para ambiente: {environment}")
    
    def _setup_logging(self):
        """Configura sistema de logging."""
        log_config = self.config.LOGGING_CONFIG
        
        # Criar diretório de logs
        log_file = Path(log_config["file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema."""
        def signal_handler(signum, frame):
            logger.info(f"📡 Sinal {signum} recebido, parando orquestrador...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Inicia o orquestrador."""
        try:
            logger.info("🚀 Iniciando orquestrador de scrapers...")
            
            # Validar configurações
            if not self.config.validate_config():
                raise Exception("Configurações inválidas")
            
            # Criar diretórios necessários
            self.config.create_directories()
            
            # Inicializar scrapers
            await self._initialize_scrapers()
            
            self.running = True
            self.stats["started_at"] = datetime.now().isoformat()
            
            logger.info("✅ Orquestrador iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar orquestrador: {e}")
            raise
    
    async def stop(self):
        """Para o orquestrador."""
        try:
            logger.info("🛑 Parando orquestrador...")
            
            self.running = False
            
            # Parar todos os scrapers
            for scraper_name, scraper in self.scrapers.items():
                try:
                    await scraper.stop()
                    logger.info(f"✅ {scraper_name} parado")
                except Exception as e:
                    logger.error(f"❌ Erro ao parar {scraper_name}: {e}")
            
            # Salvar estatísticas finais
            await self._save_final_stats()
            
            logger.info("✅ Orquestrador parado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar orquestrador: {e}")
    
    async def _initialize_scrapers(self):
        """Inicializa todos os scrapers."""
        try:
            logger.info("🔧 Inicializando scrapers...")
            
            # Configuração base do Playwright
            playwright_config = get_config_for_environment(self.environment)
            
            # Inicializar FBRef scraper
            self.scrapers["FBRef"] = FBRefPlaywrightScraper(**playwright_config)
            logger.info("✅ FBRef scraper inicializado")
            
            # Inicializar SofaScore scraper
            self.scrapers["SofaScore"] = SofaScorePlaywrightScraper(**playwright_config)
            logger.info("✅ SofaScore scraper inicializado")
            
            # Adicionar mais scrapers aqui conforme necessário
            
            logger.info(f"✅ {len(self.scrapers)} scrapers inicializados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar scrapers: {e}")
            raise
    
    async def run_collection_cycle(self, cycle_name: str = "default"):
        """
        Executa um ciclo completo de coleta.
        
        Args:
            cycle_name: Nome do ciclo para identificação
        """
        try:
            logger.info(f"🔄 Iniciando ciclo de coleta: {cycle_name}")
            
            cycle_start = time.time()
            cycle_stats = {
                "cycle_name": cycle_name,
                "started_at": datetime.now().isoformat(),
                "scrapers": {},
                "total_data_collected": 0
            }
            
            # Executar FBRef scraper
            if "FBRef" in self.scrapers:
                logger.info("🏆 Executando FBRef scraper...")
                fbref_stats = await self._run_fbref_scraper()
                cycle_stats["scrapers"]["FBRef"] = fbref_stats
                cycle_stats["total_data_collected"] += fbref_stats.get("data_count", 0)
            
            # Executar SofaScore scraper
            if "SofaScore" in self.scrapers:
                logger.info("⚽ Executando SofaScore scraper...")
                sofascore_stats = await self._run_sofascore_scraper()
                cycle_stats["scrapers"]["SofaScore"] = sofascore_stats
                cycle_stats["total_data_collected"] += sofascore_stats.get("data_count", 0)
            
            # Rate limiting entre scrapers
            await asyncio.sleep(self.config.RATE_LIMITING["global_delay"])
            
            # Finalizar ciclo
            cycle_duration = time.time() - cycle_start
            cycle_stats["duration"] = cycle_duration
            cycle_stats["finished_at"] = datetime.now().isoformat()
            
            # Salvar estatísticas do ciclo
            await self._save_cycle_stats(cycle_stats)
            
            logger.info(f"✅ Ciclo {cycle_name} concluído em {cycle_duration:.2f}s")
            logger.info(f"📊 Total de dados coletados: {cycle_stats['total_data_collected']}")
            
            return cycle_stats
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de coleta {cycle_name}: {e}")
            return None
    
    async def _run_fbref_scraper(self) -> Dict[str, Any]:
        """Executa o scraper do FBRef."""
        try:
            scraper = self.scrapers["FBRef"]
            
            # Configuração específica do FBRef
            fbref_config = self.config.get_fbref_config()
            
            # Coletar dados
            data = await scraper.collect_all_data(fbref_config["competitions"])
            
            # Salvar dados
            if data:
                filename = f"fbref_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = await scraper.save_data(data, filename)
                
                stats = {
                    "status": "success",
                    "data_count": len(data.get("matches", [])),
                    "competitions_processed": len(data.get("competitions", [])),
                    "file_saved": filepath,
                    "collected_at": datetime.now().isoformat()
                }
                
                self.stats["successful_requests"] += 1
                self.stats["last_success"] = datetime.now().isoformat()
                
                return stats
            else:
                stats = {
                    "status": "no_data",
                    "data_count": 0,
                    "competitions_processed": 0,
                    "file_saved": None,
                    "collected_at": datetime.now().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Erro no scraper FBRef: {e}")
            
            self.stats["failed_requests"] += 1
            self.stats["last_error"] = datetime.now().isoformat()
            
            return {
                "status": "error",
                "error": str(e),
                "data_count": 0,
                "competitions_processed": 0,
                "file_saved": None,
                "collected_at": datetime.now().isoformat()
            }
    
    async def _run_sofascore_scraper(self) -> Dict[str, Any]:
        """Executa o scraper do SofaScore."""
        try:
            scraper = self.scrapers["SofaScore"]
            
            # Configuração específica do SofaScore
            sofascore_config = self.config.get_sofascore_config()
            
            # URLs organizadas por tipo
            urls = {
                "live": [f"{sofascore_config['base_url']}/football/live"],
                "teams": sofascore_config["teams"][:3],  # Limitar a 3 times por ciclo
                "tournaments": sofascore_config["tournaments"][:2]  # Limitar a 2 torneios por ciclo
            }
            
            # Coletar dados
            data = await scraper.collect_all_data(urls)
            
            # Salvar dados
            if data:
                filename = f"sofascore_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = await scraper.save_data(data, filename)
                
                stats = {
                    "status": "success",
                    "data_count": (
                        len(data.get("live_matches", [])) +
                        len(data.get("team_matches", [])) +
                        len(data.get("tournament_matches", []))
                    ),
                    "live_matches": len(data.get("live_matches", [])),
                    "team_matches": len(data.get("team_matches", [])),
                    "tournament_matches": len(data.get("tournament_matches", [])),
                    "file_saved": filepath,
                    "collected_at": datetime.now().isoformat()
                }
                
                self.stats["successful_requests"] += 1
                self.stats["last_success"] = datetime.now().isoformat()
                
                return stats
            else:
                stats = {
                    "status": "no_data",
                    "data_count": 0,
                    "live_matches": 0,
                    "team_matches": 0,
                    "tournament_matches": 0,
                    "file_saved": None,
                    "collected_at": datetime.now().isoformat()
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Erro no scraper SofaScore: {e}")
            
            self.stats["failed_requests"] += 1
            self.stats["last_error"] = datetime.now().isoformat()
            
            return {
                "status": "error",
                "error": str(e),
                "data_count": 0,
                "live_matches": 0,
                "team_matches": 0,
                "tournament_matches": 0,
                "file_saved": None,
                "collected_at": datetime.now().isoformat()
            }
    
    async def _save_cycle_stats(self, cycle_stats: Dict[str, Any]):
        """Salva estatísticas de um ciclo."""
        try:
            stats_dir = Path("stats")
            stats_dir.mkdir(exist_ok=True)
            
            filename = f"cycle_{cycle_stats['cycle_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = stats_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cycle_stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Estatísticas do ciclo salvas: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estatísticas do ciclo: {e}")
    
    async def _save_final_stats(self):
        """Salva estatísticas finais do orquestrador."""
        try:
            stats_dir = Path("stats")
            stats_dir.mkdir(exist_ok=True)
            
            # Adicionar estatísticas finais
            self.stats["finished_at"] = datetime.now().isoformat()
            if self.stats["started_at"]:
                start_time = datetime.fromisoformat(self.stats["started_at"])
                end_time = datetime.now()
                self.stats["total_duration"] = (end_time - start_time).total_seconds()
            
            filename = f"orchestrator_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = stats_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Estatísticas finais salvas: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estatísticas finais: {e}")
    
    async def run_scheduled_collection(self, interval_minutes: int = 60):
        """
        Executa coleta agendada.
        
        Args:
            interval_minutes: Intervalo entre coletas em minutos
        """
        try:
            logger.info(f"⏰ Iniciando coleta agendada a cada {interval_minutes} minutos")
            
            cycle_count = 0
            
            while self.running:
                try:
                    cycle_count += 1
                    cycle_name = f"scheduled_{cycle_count:04d}"
                    
                    logger.info(f"🔄 Executando ciclo agendado {cycle_count}")
                    
                    # Executar ciclo de coleta
                    cycle_stats = await self.run_collection_cycle(cycle_name)
                    
                    if cycle_stats:
                        logger.info(f"✅ Ciclo {cycle_count} concluído com sucesso")
                    else:
                        logger.warning(f"⚠️ Ciclo {cycle_count} falhou")
                    
                    # Aguardar próximo ciclo
                    if self.running:
                        logger.info(f"⏳ Aguardando {interval_minutes} minutos para próximo ciclo...")
                        await asyncio.sleep(interval_minutes * 60)
                    
                except asyncio.CancelledError:
                    logger.info("🛑 Coleta agendada cancelada")
                    break
                except Exception as e:
                    logger.error(f"❌ Erro no ciclo agendado {cycle_count}: {e}")
                    
                    # Aguardar antes de tentar novamente
                    if self.running:
                        await asyncio.sleep(5 * 60)  # 5 minutos
            
            logger.info("🛑 Coleta agendada parada")
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta agendada: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do orquestrador."""
        try:
            current_time = datetime.now()
            
            # Calcular tempo desde última execução
            last_success_age = None
            if self.stats["last_success"]:
                last_success = datetime.fromisoformat(self.stats["last_success"])
                last_success_age = (current_time - last_success).total_seconds()
            
            last_error_age = None
            if self.stats["last_error"]:
                last_error = datetime.fromisoformat(self.stats["last_error"])
                last_error_age = (current_time - last_error).total_seconds()
            
            # Calcular taxa de sucesso
            total_requests = self.stats["successful_requests"] + self.stats["failed_requests"]
            success_rate = (
                self.stats["successful_requests"] / total_requests 
                if total_requests > 0 else 0
            )
            
            # Determinar status geral
            if success_rate >= 0.8:
                overall_status = "healthy"
            elif success_rate >= 0.5:
                overall_status = "warning"
            else:
                overall_status = "critical"
            
            health_status = {
                "overall_status": overall_status,
                "running": self.running,
                "success_rate": success_rate,
                "total_requests": total_requests,
                "successful_requests": self.stats["successful_requests"],
                "failed_requests": self.stats["failed_requests"],
                "last_success_age_seconds": last_success_age,
                "last_error_age_seconds": last_error_age,
                "uptime_seconds": (
                    (current_time - datetime.fromisoformat(self.stats["started_at"])).total_seconds()
                    if self.stats["started_at"] else None
                ),
                "scrapers": {
                    name: "active" if scraper.page else "inactive"
                    for name, scraper in self.scrapers.items()
                },
                "timestamp": current_time.isoformat()
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter status de saúde: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Função principal para execução
async def main():
    """Função principal para executar o orquestrador."""
    try:
        # Criar orquestrador
        orchestrator = OrquestradorScrapers(environment="dev")
        
        # Iniciar
        await orchestrator.start()
        
        # Executar ciclo único de teste
        print("🧪 Executando ciclo único de teste...")
        cycle_stats = await orchestrator.run_collection_cycle("test_cycle")
        
        if cycle_stats:
            print("✅ Ciclo de teste concluído com sucesso!")
            print(f"📊 Dados coletados: {cycle_stats['total_data_collected']}")
        else:
            print("❌ Ciclo de teste falhou")
        
        # Parar orquestrador
        await orchestrator.stop()
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executar orquestrador
    asyncio.run(main())
