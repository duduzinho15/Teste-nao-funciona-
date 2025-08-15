"""
SCRAPER DO SOFASCORE COM PLAYWRIGHT
===================================

Scraper avançado para o SofaScore usando Playwright da Microsoft.
Oferece coleta de dados de partidas, estatísticas em tempo real e odds.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

from ..playwright_base import PlaywrightBaseScraper

logger = logging.getLogger(__name__)

class SofaScorePlaywrightScraper(PlaywrightBaseScraper):
    """
    Scraper do SofaScore usando Playwright.
    
    Funcionalidades:
    - Coleta de dados de partidas em tempo real
    - Estatísticas ao vivo
    - Odds e probabilidades
    - Histórico de confrontos
    - Anti-detecção avançado
    """
    
    def __init__(self, **kwargs):
        """Inicializa o scraper do SofaScore."""
        # Configurações padrão
        default_config = {
            "browser_type": "chromium",
            "headless": True,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "timeout": 60000,
            "screenshot_dir": "screenshots/sofascore",
            "enable_video": False,
            "enable_har": True
        }
        
        # Atualizar com kwargs (permitindo override)
        default_config.update(kwargs)
        
        super().__init__(**default_config)
        
        # URLs base do SofaScore
        self.base_url = "https://www.sofascore.com"
        self.football_url = f"{self.base_url}/football"
        
        # Seletores CSS para elementos principais
        self.selectors = {
            "match_link": "a[href*='/event/']",
            "team_link": "a[href*='/team/']",
            "player_link": "a[href*='/player/']",
            "tournament_link": "a[href*='/tournament/']",
            "score": ".sc-fqkvVR",
            "time": ".sc-dcJsrY",
            "stats": ".sc-gsFSXq",
            "odds": ".sc-hLBbgP",
            "loading": ".loading, .spinner",
            "error": ".error, .alert"
        }
        
        # Configurações específicas do SofaScore
        self.rate_limit_delay = 3.0  # Delay entre requisições (mais conservador)
        self.max_pages_per_session = 30  # Máximo de páginas por sessão
        self.session_page_count = 0
        
        logger.info("🎭 SofaScorePlaywrightScraper inicializado")
    
    async def start_session(self):
        """Inicia uma nova sessão de scraping."""
        await self.start()
        self.session_page_count = 0
        
        # Configurar headers específicos do SofaScore
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Simular comportamento humano
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en'],
            });
        """)
        
        logger.info("🚀 Sessão de scraping iniciada")
    
    async def collect_live_matches(self) -> List[Dict[str, Any]]:
        """
        Coleta partidas ao vivo.
        
        Returns:
            Lista de partidas ao vivo
        """
        try:
            logger.info("⚽ Coletando partidas ao vivo...")
            
            live_url = f"{self.football_url}/live"
            if not await self.navigate_to(live_url):
                raise Exception("Falha na navegação para página de partidas ao vivo")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["match_link"])
            
            # Coletar partidas ao vivo
            match_elements = await self.page.query_selector_all(self.selectors["match_link"])
            
            live_matches = []
            for element in match_elements[:20]:  # Limitar a 20 partidas
                try:
                    href = await element.get_attribute("href")
                    text = await element.text_content()
                    
                    if href and text:
                        match = {
                            "url": f"{self.base_url}{href}",
                            "title": text.strip(),
                            "status": "live",
                            "collected_at": datetime.now().isoformat()
                        }
                        live_matches.append(match)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar partida ao vivo: {e}")
                    continue
            
            logger.info(f"✅ {len(live_matches)} partidas ao vivo coletadas")
            return live_matches
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar partidas ao vivo: {e}")
            await self.take_screenshot("error_live_matches.png")
            return []
    
    async def collect_match_details(self, match_url: str) -> Dict[str, Any]:
        """
        Coleta detalhes de uma partida específica.
        
        Args:
            match_url: URL da partida
        
        Returns:
            Dicionário com detalhes da partida
        """
        try:
            logger.info(f"⚽ Coletando detalhes da partida: {match_url}")
            
            if not await self.navigate_to(match_url):
                raise Exception(f"Falha na navegação para: {match_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["score"])
            
            # Coletar informações básicas
            title = await self.get_text("h1")
            score = await self.get_text(self.selectors["score"])
            time_info = await self.get_text(self.selectors["time"])
            
            # Coletar estatísticas
            stats = await self._collect_match_stats()
            
            # Coletar odds se disponível
            odds = await self._collect_match_odds()
            
            match_details = {
                "title": title,
                "score": score,
                "time": time_info,
                "url": match_url,
                "stats": stats,
                "odds": odds,
                "collected_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Detalhes da partida coletados: {title}")
            return match_details
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar detalhes da partida: {e}")
            await self.take_screenshot("error_match_details.png")
            return {}
    
    async def collect_team_matches(self, team_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Coleta partidas de um time específico.
        
        Args:
            team_url: URL do time
            limit: Limite de partidas para coletar
        
        Returns:
            Lista de partidas do time
        """
        try:
            logger.info(f"⚽ Coletando partidas do time: {team_url}")
            
            # Navegar para página de partidas do time
            matches_url = f"{team_url}/matches"
            if not await self.navigate_to(matches_url):
                raise Exception(f"Falha na navegação para: {matches_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["match_link"])
            
            # Coletar partidas
            match_elements = await self.page.query_selector_all(self.selectors["match_link"])
            
            team_matches = []
            for element in match_elements[:limit]:
                try:
                    href = await element.get_attribute("href")
                    text = await element.text_content()
                    
                    if href and text:
                        match = {
                            "url": f"{self.base_url}{href}",
                            "title": text.strip(),
                            "team_url": team_url,
                            "collected_at": datetime.now().isoformat()
                        }
                        team_matches.append(match)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar partida do time: {e}")
                    continue
            
            logger.info(f"✅ {len(team_matches)} partidas do time coletadas")
            return team_matches
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar partidas do time: {e}")
            await self.take_screenshot("error_team_matches.png")
            return []
    
    async def collect_tournament_matches(self, tournament_url: str) -> List[Dict[str, Any]]:
        """
        Coleta partidas de um torneio específico.
        
        Args:
            tournament_url: URL do torneio
        
        Returns:
            Lista de partidas do torneio
        """
        try:
            logger.info(f"🏆 Coletando partidas do torneio: {tournament_url}")
            
            # Navegar para página de partidas do torneio
            matches_url = f"{tournament_url}/matches"
            if not await self.navigate_to(matches_url):
                raise Exception(f"Falha na navegação para: {matches_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["match_link"])
            
            tournament_matches = []
            page = 1
            
            while page <= self.max_pages_per_session:
                try:
                    logger.info(f"📄 Processando página {page} do torneio")
                    
                    # Coletar partidas da página atual
                    match_elements = await self.page.query_selector_all(self.selectors["match_link"])
                    
                    for element in match_elements:
                        try:
                            href = await element.get_attribute("href")
                            text = await element.text_content()
                            
                            if href and text:
                                match = {
                                    "url": f"{self.base_url}{href}",
                                    "title": text.strip(),
                                    "tournament_url": tournament_url,
                                    "collected_at": datetime.now().isoformat()
                                }
                                tournament_matches.append(match)
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao processar partida do torneio: {e}")
                            continue
                    
                    # Verificar se há mais páginas (implementar lógica específica)
                    # Por enquanto, limitar a uma página
                    break
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar página {page}: {e}")
                    break
            
            logger.info(f"✅ {len(tournament_matches)} partidas do torneio coletadas")
            return tournament_matches
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar partidas do torneio: {e}")
            await self.take_screenshot("error_tournament_matches.png")
            return []
    
    async def _collect_match_stats(self) -> Dict[str, Any]:
        """
        Coleta estatísticas de uma partida.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            stats = {}
            
            # Tentar encontrar tabela de estatísticas
            stats_elements = await self.page.query_selector_all(self.selectors["stats"])
            
            for element in stats_elements:
                try:
                    text = await element.text_content()
                    if text:
                        # Processar estatísticas (implementar parser específico)
                        stats["raw_stats"] = text.strip()
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar estatísticas: {e}")
                    continue
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas: {e}")
            return {}
    
    async def _collect_match_odds(self) -> Dict[str, Any]:
        """
        Coleta odds de uma partida.
        
        Returns:
            Dicionário com odds
        """
        try:
            odds = {}
            
            # Tentar encontrar elementos de odds
            odds_elements = await self.page.query_selector_all(self.selectors["odds"])
            
            for element in odds_elements:
                try:
                    text = await element.text_content()
                    if text:
                        # Processar odds (implementar parser específico)
                        odds["raw_odds"] = text.strip()
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar odds: {e}")
                    continue
            
            return odds
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar odds: {e}")
            return {}
    
    async def collect_all_data(self, urls: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Coleta todos os dados de múltiplas fontes.
        
        Args:
            urls: Dicionário com URLs organizadas por tipo
        
        Returns:
            Dicionário com todos os dados coletados
        """
        try:
            logger.info("🚀 Iniciando coleta completa do SofaScore...")
            
            all_data = {
                "live_matches": [],
                "team_matches": [],
                "tournament_matches": [],
                "collection_info": {
                    "started_at": datetime.now().isoformat(),
                    "total_urls": sum(len(url_list) for url_list in urls.values()),
                    "successful_collections": 0,
                    "failed_collections": 0
                }
            }
            
            # Coletar partidas ao vivo
            if "live" in urls:
                for url in urls["live"]:
                    try:
                        live_matches = await self.collect_live_matches()
                        all_data["live_matches"].extend(live_matches)
                        all_data["collection_info"]["successful_collections"] += 1
                    except Exception as e:
                        logger.error(f"❌ Erro ao coletar partidas ao vivo: {e}")
                        all_data["collection_info"]["failed_collections"] += 1
            
            # Coletar partidas de times
            if "teams" in urls:
                for url in urls["teams"]:
                    try:
                        team_matches = await self.collect_team_matches(url)
                        all_data["team_matches"].extend(team_matches)
                        all_data["collection_info"]["successful_collections"] += 1
                        
                        # Rate limiting
                        await asyncio.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao coletar partidas do time: {e}")
                        all_data["collection_info"]["failed_collections"] += 1
            
            # Coletar partidas de torneios
            if "tournaments" in urls:
                for url in urls["tournaments"]:
                    try:
                        tournament_matches = await self.collect_tournament_matches(url)
                        all_data["tournament_matches"].extend(tournament_matches)
                        all_data["collection_info"]["successful_collections"] += 1
                        
                        # Rate limiting
                        await asyncio.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao coletar partidas do torneio: {e}")
                        all_data["collection_info"]["failed_collections"] += 1
            
            all_data["collection_info"]["finished_at"] = datetime.now().isoformat()
            all_data["collection_info"]["total_live_matches"] = len(all_data["live_matches"])
            all_data["collection_info"]["total_team_matches"] = len(all_data["team_matches"])
            all_data["collection_info"]["total_tournament_matches"] = len(all_data["tournament_matches"])
            
            logger.info(f"🎉 Coleta completa finalizada: {all_data['collection_info']['successful_collections']} sucessos, {all_data['collection_info']['failed_collections']} falhas")
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta completa: {e}")
            return {}
    
    async def save_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Salva dados coletados em arquivo JSON.
        
        Args:
            data: Dados para salvar
            filename: Nome do arquivo (opcional)
        
        Returns:
            Caminho do arquivo salvo
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"sofascore_data_{timestamp}.json"
            
            filepath = Path("collected_data") / filename
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Dados salvos em: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados: {e}")
            return ""

# Função de conveniência para uso síncrono
def run_sofascore_scraper(urls: Dict[str, List[str]], **kwargs) -> Dict[str, Any]:
    """
    Executa o scraper do SofaScore de forma síncrona.
    
    Args:
        urls: Dicionário com URLs organizadas por tipo
        **kwargs: Argumentos para o scraper
    
    Returns:
        Dados coletados
    """
    async def _run():
        async with SofaScorePlaywrightScraper(**kwargs) as scraper:
            return await scraper.collect_all_data(urls)
    
    return asyncio.run(_run())

# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # URLs de exemplo
    urls = {
        "live": ["https://www.sofascore.com/football/live"],
        "teams": [
            "https://www.sofascore.com/team/manchester-united/17",
            "https://www.sofascore.com/team/liverpool/44"
        ],
        "tournaments": [
            "https://www.sofascore.com/tournament/england-premier-league/7"
        ]
    }
    
    # Executar scraper
    data = run_sofascore_scraper(urls, headless=False)
    
    # Salvar dados
    if data:
        scraper = SofaScorePlaywrightScraper()
        asyncio.run(scraper.save_data(data))
