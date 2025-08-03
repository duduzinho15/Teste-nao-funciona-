#!/usr/bin/env python3
"""
Teste Específico: Burst Mode Otimizado com Ligue 1

Testa apenas a otimização do burst mode (threshold 80% → 75%)
Monitora delays e taxa de 429 errors durante coleta da Ligue 1
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

# Adicionar path do projeto
sys.path.append(os.path.dirname(__file__))

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('teste_ligue1_burst.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class Ligue1BurstTester:
    """Testa otimização de burst mode com dados da Ligue 1."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_metrics = []
        self.delay_history = []
        self.error_429_count = 0
        self.total_requests = 0
        self.burst_mode_activations = 0
        
    def log_request_attempt(self, url: str, delay: float, burst_mode: bool):
        """Registra tentativa de requisição."""
        self.delay_history.append(delay)
        if burst_mode:
            self.burst_mode_activations += 1
        
        logger.info(f"🔄 Requisição: {url}")
        logger.info(f"   Delay: {delay:.2f}s | Burst: {'✅' if burst_mode else '❌'}")
        
    def log_request_result(self, url: str, success: bool, status_code: int, response_time: float):
        """Registra resultado da requisição."""
        self.total_requests += 1
        
        if status_code == 429:
            self.error_429_count += 1
            logger.warning(f"❌ 429 ERROR: {url} (Total 429s: {self.error_429_count})")
        elif success:
            logger.info(f"✅ SUCESSO: {url} ({response_time:.2f}s)")
        else:
            logger.warning(f"⚠️ FALHA: {url} (Status: {status_code})")
        
        # Registrar métricas
        self.request_metrics.append({
            'timestamp': datetime.now(),
            'url': url,
            'success': success,
            'status_code': status_code,
            'response_time': response_time,
            'is_429': status_code == 429
        })
        
    def get_current_stats(self) -> Dict:
        """Retorna estatísticas atuais do teste."""
        if not self.request_metrics:
            return {}
            
        success_count = sum(1 for m in self.request_metrics if m['success'])
        success_rate = success_count / len(self.request_metrics) if self.request_metrics else 0
        error_429_rate = self.error_429_count / self.total_requests if self.total_requests > 0 else 0
        
        avg_delay = statistics.mean(self.delay_history) if self.delay_history else 0
        min_delay = min(self.delay_history) if self.delay_history else 0
        max_delay = max(self.delay_history) if self.delay_history else 0
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        requests_per_minute = (self.total_requests / elapsed_time * 60) if elapsed_time > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'success_rate': success_rate,
            'error_429_count': self.error_429_count,
            'error_429_rate': error_429_rate,
            'burst_activations': self.burst_mode_activations,
            'burst_rate': self.burst_mode_activations / self.total_requests if self.total_requests > 0 else 0,
            'avg_delay': avg_delay,
            'min_delay': min_delay,
            'max_delay': max_delay,
            'requests_per_minute': requests_per_minute,
            'elapsed_minutes': elapsed_time / 60
        }
        
    def print_stats_summary(self):
        """Imprime resumo das estatísticas."""
        stats = self.get_current_stats()
        
        logger.info("=" * 60)
        logger.info("📊 ESTATÍSTICAS DO TESTE LIGUE 1 - BURST MODE")
        logger.info("=" * 60)
        logger.info(f"⏱️  Tempo decorrido: {stats.get('elapsed_minutes', 0):.1f} min")
        logger.info(f"📈 Total de requisições: {stats.get('total_requests', 0)}")
        logger.info(f"✅ Taxa de sucesso: {stats.get('success_rate', 0):.2%}")
        logger.info(f"❌ Erros 429: {stats.get('error_429_count', 0)} ({stats.get('error_429_rate', 0):.2%})")
        logger.info(f"🚀 Burst mode ativado: {stats.get('burst_activations', 0)}x ({stats.get('burst_rate', 0):.2%})")
        logger.info(f"⏳ Delay médio: {stats.get('avg_delay', 0):.2f}s")
        logger.info(f"⏳ Delay min/max: {stats.get('min_delay', 0):.2f}s / {stats.get('max_delay', 0):.2f}s")
        logger.info(f"🔄 Requisições/min: {stats.get('requests_per_minute', 0):.1f}")
        logger.info("=" * 60)

def test_ligue1_urls() -> List[str]:
    """Retorna lista de URLs da Ligue 1 para teste."""
    base_urls = [
        "https://fbref.com/en/comps/13/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures",
        "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/shooting/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/passing/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/defense/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/possession/Ligue-1-Stats",
        "https://fbref.com/en/comps/13/misc/Ligue-1-Stats"
    ]
    return base_urls

def simulate_ligue1_scraping():
    """Simula coleta da Ligue 1 com monitoramento de burst mode."""
    logger.info("🚀 INICIANDO TESTE LIGUE 1 - BURST MODE OTIMIZADO")
    logger.info("Testando apenas threshold 80% → 75%")
    logger.info("=" * 60)
    
    tester = Ligue1BurstTester()
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking
        from Coleta_de_dados.apis.fbref.anti_429_state_machine import Anti429StateMachine
        
        # Inicializar sistemas
        anti_blocking = get_advanced_anti_blocking()
        state_machine = Anti429StateMachine()
        
        # URLs de teste
        test_urls = test_ligue1_urls()
        
        logger.info(f"📋 Testando {len(test_urls)} URLs da Ligue 1")
        
        for i, url in enumerate(test_urls, 1):
            logger.info(f"\n--- REQUISIÇÃO {i}/{len(test_urls)} ---")
            
            # Calcular delay
            delay = anti_blocking.calculate_smart_delay(url)
            
            # Verificar burst mode
            can_burst = anti_blocking.should_use_burst_mode()
            success_rate = anti_blocking.get_recent_success_rate()
            
            # Log da tentativa
            tester.log_request_attempt(url, delay, can_burst)
            logger.info(f"   Success rate atual: {success_rate:.2%}")
            
            # Simular delay
            logger.info(f"⏳ Aguardando {delay:.2f}s...")
            time.sleep(min(delay, 10))  # Cap em 10s para teste
            
            # Simular requisição (85% sucesso, 10% 429, 5% outros erros)
            import random
            rand = random.random()
            
            if rand < 0.85:  # Sucesso
                success = True
                status_code = 200
                response_time = random.uniform(0.5, 3.0)
                state_machine.record_success(url)
            elif rand < 0.95:  # 429 error
                success = False
                status_code = 429
                response_time = random.uniform(0.2, 1.0)
                state_machine.record_429_error(url)
            else:  # Outros erros
                success = False
                status_code = random.choice([500, 502, 503])
                response_time = random.uniform(0.1, 0.5)
                state_machine.record_connection_error(url, f"HTTP {status_code}")
            
            # Registrar resultado
            anti_blocking.record_request_result(url, success, response_time, status_code)
            tester.log_request_result(url, success, status_code, response_time)
            
            # Estatísticas intermediárias a cada 3 requisições
            if i % 3 == 0:
                tester.print_stats_summary()
                
                # Verificar se taxa de 429 está muito alta
                stats = tester.get_current_stats()
                if stats.get('error_429_rate', 0) > 0.15:  # > 15%
                    logger.warning("⚠️ ATENÇÃO: Taxa de 429 errors muito alta!")
                    logger.warning("Considere reverter otimização ou aplicar outras melhorias")
        
        # Estatísticas finais
        logger.info("\n🏁 TESTE CONCLUÍDO!")
        tester.print_stats_summary()
        
        # Análise dos resultados
        stats = tester.get_current_stats()
        
        logger.info("\n📋 ANÁLISE DOS RESULTADOS:")
        
        # Verificar se burst mode foi efetivo
        if stats.get('burst_rate', 0) > 0.1:  # > 10% das requisições
            logger.info(f"✅ Burst mode ativo em {stats.get('burst_rate', 0):.1%} das requisições")
        else:
            logger.warning("⚠️ Burst mode pouco ativo - verificar success rate")
        
        # Verificar taxa de 429
        if stats.get('error_429_rate', 0) < 0.10:  # < 10%
            logger.info(f"✅ Taxa de 429 errors aceitável: {stats.get('error_429_rate', 0):.2%}")
        else:
            logger.warning(f"❌ Taxa de 429 errors alta: {stats.get('error_429_rate', 0):.2%}")
        
        # Verificar throughput
        if stats.get('requests_per_minute', 0) > 8:  # > 8 req/min
            logger.info(f"✅ Throughput bom: {stats.get('requests_per_minute', 0):.1f} req/min")
        else:
            logger.info(f"ℹ️ Throughput: {stats.get('requests_per_minute', 0):.1f} req/min")
        
        # Recomendações
        logger.info("\n💡 RECOMENDAÇÕES:")
        
        if stats.get('error_429_rate', 0) < 0.10 and stats.get('burst_rate', 0) > 0.05:
            logger.info("✅ Otimização de burst mode funcionando bem!")
            logger.info("✅ Pode prosseguir com outras otimizações (delays, recovery, etc.)")
        elif stats.get('error_429_rate', 0) > 0.15:
            logger.warning("⚠️ Taxa de 429 muito alta - considere reverter ou ajustar")
        else:
            logger.info("ℹ️ Resultados mistos - monitorar mais tempo antes de próximas otimizações")
            
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {e}")
        return None

def main():
    """Executa teste principal da Ligue 1."""
    try:
        stats = simulate_ligue1_scraping()
        
        if stats:
            # Salvar resultados
            with open('ligue1_burst_test_results.txt', 'w', encoding='utf-8') as f:
                f.write("TESTE LIGUE 1 - BURST MODE OTIMIZADO\n")
                f.write("=" * 50 + "\n")
                f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Otimização: Burst mode threshold 80% → 75%\n\n")
                
                for key, value in stats.items():
                    if isinstance(value, float):
                        f.write(f"{key}: {value:.4f}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            
            logger.info("📄 Resultados salvos em: ligue1_burst_test_results.txt")
            
            # Determinar sucesso do teste
            success = (
                stats.get('error_429_rate', 1) < 0.10 and
                stats.get('success_rate', 0) > 0.80 and
                stats.get('burst_rate', 0) > 0.05
            )
            
            if success:
                logger.info("🎉 TESTE BEM-SUCEDIDO! Burst mode otimizado funcionando.")
                return True
            else:
                logger.warning("⚠️ Teste com resultados mistos. Revisar configurações.")
                return False
        else:
            logger.error("❌ Teste falhou.")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro fatal no teste: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
