#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRAPER DO SOFASCORE COM PLAYWRIGHT - VERSÃO AVANÇADA
=====================================================

Scraper avançado para o SofaScore usando Playwright da Microsoft.
Inclui funcionalidades de anti-detecção, coleta de estatísticas detalhadas,
e sistema de fallback robusto.

Autor: Sistema de Scraping Avançado
Data: 2025-08-14
Versão: 2.0 (Playwright Enhanced)
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from sqlalchemy.orm import Session

# Importações locais
from ..playwright_base import PlaywrightBaseScraper
from ...database.models import PartidaSofascore, Clube
from ...database.config import SessionLocal

# Configuração de logging
logger = logging.getLogger(__name__)

class SofaScorePlaywrightScraperEnhanced(PlaywrightBaseScraper):
    """
    Scraper avançado do SofaScore usando Playwright.
    
    Funcionalidades:
    - Coleta de partidas em tempo real
    - Estatísticas detalhadas por partida
    - Sistema de anti-detecção avançado
    - Fallback para API quando necessário
    - Coleta de odds e previsões
    """
    
    def __init__(self, **kwargs):
        """Inicializa o scraper do SofaScore."""
        super().__init__(**kwargs)
        
        # URLs específicas do SofaScore
        self.base_url = "https://www.sofascore.com"
        self.api_base = "https://api.sofascore.com/api/v1"
        
        # Configurações específicas
        self.sports = ["football", "basketball", "tennis", "mma"]
        self.max_matches_per_sport = 100
        self.retry_attempts = 3
        
        # Headers específicos do SofaScore
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        logger.info("🎭 SofaScorePlaywrightScraperEnhanced inicializado")
    
    async def setup_page(self, page: Page) -> None:
        """Configura a página para o SofaScore."""
        await super().setup_page(page)
        
        # Configurações específicas para o SofaScore
        await page.set_extra_http_headers(self.headers)
        
        # Intercepta requisições para análise
        await page.route("**/*", self._handle_request)
        
        # Configura viewport específico
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Aguarda carregamento da página
        await page.wait_for_load_state("networkidle")
    
    async def _handle_request(self, route) -> None:
        """Intercepta e analisa requisições."""
        request = route.request
        
        # Log de requisições importantes
        if "api.sofascore.com" in request.url:
            logger.debug(f"API Request: {request.method} {request.url}")
        
        # Continua a requisição
        await route.continue_()
    
    async def collect_sport_matches(self, sport: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta partidas de um esporte específico.
        
        Args:
            sport: Nome do esporte (football, basketball, etc.)
            page: Página do Playwright
            
        Returns:
            Lista de partidas coletadas
        """
        matches = []
        
        try:
            # Navega para a página do esporte
            sport_url = f"{self.base_url}/{sport}"
            await page.goto(sport_url, wait_until="networkidle")
            
            # Aguarda carregamento dos torneios
            await page.wait_for_selector('[data-testid="tournament-list"]', timeout=10000)
            
            # Coleta torneios disponíveis
            tournaments = await page.query_selector_all('[data-testid="tournament-item"]')
            
            for tournament in tournaments[:10]:  # Limita a 10 torneios por esporte
                try:
                    # Clica no torneio para expandir
                    await tournament.click()
                    await page.wait_for_timeout(1000)
                    
                    # Coleta partidas do torneio
                    match_elements = await page.query_selector_all('[data-testid="match-item"]')
                    
                    for match_elem in match_elements[:20]:  # Limita a 20 partidas por torneio
                        match_data = await self._extract_match_data(match_elem, sport)
                        if match_data:
                            matches.append(match_data)
                    
                    # Fecha o torneio
                    await tournament.click()
                    await page.wait_for_timeout(500)
                    
                except Exception as e:
                    logger.warning(f"Erro ao coletar torneio: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Erro ao coletar partidas do esporte {sport}: {e}")
        
        return matches
    
    async def _extract_match_data(self, match_elem, sport: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de uma partida específica."""
        try:
            # Extrai informações básicas
            home_team = await match_elem.query_selector('[data-testid="home-team"]')
            away_team = await match_elem.query_selector('[data-testid="away-team"]')
            score = await match_elem.query_selector('[data-testid="score"]')
            time_info = await match_elem.query_selector('[data-testid="time-info"]')
            
            if not all([home_team, away_team]):
                return None
            
            # Extrai texto dos elementos
            home_team_name = await home_team.text_content() or "Unknown"
            away_team_name = await away_team.text_content() or "Unknown"
            score_text = await score.text_content() if score else "0-0"
            time_text = await time_info.text_content() if time_info else ""
            
            # Extrai link da partida
            match_link = await match_elem.get_attribute("href")
            if match_link:
                match_url = urljoin(self.base_url, match_link)
            else:
                match_url = ""
            
            # Extrai odds se disponível
            odds_elem = await match_elem.query_selector('[data-testid="odds"]')
            odds = await odds_elem.text_content() if odds_elem else ""
            
            return {
                "sport": sport,
                "home_team": home_team_name.strip(),
                "away_team": away_team_name.strip(),
                "score": score_text.strip(),
                "time_info": time_text.strip(),
                "match_url": match_url,
                "odds": odds.strip() if odds else "",
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair dados da partida: {e}")
            return None
    
    async def collect_detailed_match_stats(self, match_url: str, page: Page) -> Dict[str, Any]:
        """
        Coleta estatísticas detalhadas de uma partida específica.
        
        Args:
            match_url: URL da partida
            page: Página do Playwright
            
        Returns:
            Dicionário com estatísticas detalhadas
        """
        stats = {}
        
        try:
            # Navega para a página da partida
            await page.goto(match_url, wait_until="networkidle")
            
            # Aguarda carregamento das estatísticas
            await page.wait_for_selector('[data-testid="statistics"]', timeout=10000)
            
            # Coleta estatísticas gerais
            stats_container = await page.query_selector('[data-testid="statistics"]')
            if stats_container:
                # Extrai estatísticas de posse, chutes, etc.
                possession = await self._extract_statistic(page, "possession")
                shots = await self._extract_statistic(page, "shots")
                corners = await self._extract_statistic(page, "corners")
                fouls = await self._extract_statistic(page, "fouls")
                
                stats.update({
                    "possession": possession,
                    "shots": shots,
                    "corners": corners,
                    "fouls": fouls
                })
            
            # Coleta estatísticas de jogadores
            players_stats = await self._collect_players_stats(page)
            stats["players"] = players_stats
            
            # Coleta eventos da partida
            events = await self._collect_match_events(page)
            stats["events"] = events
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas detalhadas: {e}")
        
        return stats
    
    async def _extract_statistic(self, page: Page, stat_name: str) -> str:
        """Extrai uma estatística específica da página."""
        try:
            selector = f'[data-testid="{stat_name}-stat"]'
            element = await page.query_selector(selector)
            if element:
                return await element.text_content() or "0"
            return "0"
        except:
            return "0"
    
    async def _collect_players_stats(self, page: Page) -> List[Dict[str, Any]]:
        """Coleta estatísticas dos jogadores."""
        players = []
        
        try:
            # Navega para a aba de jogadores
            players_tab = await page.query_selector('[data-testid="players-tab"]')
            if players_tab:
                await players_tab.click()
                await page.wait_for_timeout(1000)
                
                # Coleta jogadores
                player_elements = await page.query_selector_all('[data-testid="player-item"]')
                
                for player_elem in player_elements[:22]:  # Limita a 22 jogadores (11 por time)
                    player_data = await self._extract_player_data(player_elem)
                    if player_data:
                        players.append(player_data)
                        
        except Exception as e:
            logger.warning(f"Erro ao coletar estatísticas dos jogadores: {e}")
        
        return players
    
    async def _extract_player_data(self, player_elem) -> Optional[Dict[str, Any]]:
        """Extrai dados de um jogador específico."""
        try:
            name = await player_elem.query_selector('[data-testid="player-name"]')
            position = await player_elem.query_selector('[data-testid="player-position"]')
            stats = await player_elem.query_selector('[data-testid="player-stats"]')
            
            if name:
                return {
                    "name": await name.text_content() or "Unknown",
                    "position": await position.text_content() if position else "",
                    "stats": await stats.text_content() if stats else ""
                }
        except:
            pass
        
        return None
    
    async def _collect_match_events(self, page: Page) -> List[Dict[str, Any]]:
        """Coleta eventos da partida (gols, cartões, etc.)."""
        events = []
        
        try:
            # Navega para a aba de eventos
            events_tab = await page.query_selector('[data-testid="events-tab"]')
            if events_tab:
                await events_tab.click()
                await page.wait_for_timeout(1000)
                
                # Coleta eventos
                event_elements = await page.query_selector_all('[data-testid="event-item"]')
                
                for event_elem in event_elements:
                    event_data = await self._extract_event_data(event_elem)
                    if event_data:
                        events.append(event_data)
                        
        except Exception as e:
            logger.warning(f"Erro ao coletar eventos da partida: {e}")
        
        return events
    
    async def _extract_event_data(self, event_elem) -> Optional[Dict[str, Any]]:
        """Extrai dados de um evento específico."""
        try:
            event_type = await event_elem.query_selector('[data-testid="event-type"]')
            time = await event_elem.query_selector('[data-testid="event-time"]')
            player = await event_elem.query_selector('[data-testid="event-player"]')
            
            if event_type:
                return {
                    "type": await event_type.text_content() or "Unknown",
                    "time": await time.text_content() if time else "",
                    "player": await player.text_content() if player else ""
                }
        except:
            pass
        
        return None
    
    async def collect_all_sports_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Coleta dados de todos os esportes configurados.
        
        Returns:
            Dicionário com dados organizados por esporte
        """
        all_data = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=self.browser_args
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=self.user_agent
            )
            
            page = await context.new_page()
            await self.setup_page(page)
            
            try:
                for sport in self.sports:
                    logger.info(f"🎯 Coletando dados do esporte: {sport}")
                    
                    matches = await self.collect_sport_matches(sport, page)
                    all_data[sport] = matches
                    
                    logger.info(f"✅ {sport}: {len(matches)} partidas coletadas")
                    
                    # Pausa entre esportes para evitar bloqueio
                    await page.wait_for_timeout(2000)
                    
            except Exception as e:
                logger.error(f"Erro durante coleta de dados: {e}")
            
            finally:
                await browser.close()
        
        return all_data
    
    async def save_to_database(self, data: Dict[str, List[Dict[str, Any]]]) -> int:
        """
        Salva os dados coletados no banco de dados.
        
        Args:
            data: Dados coletados organizados por esporte
            
        Returns:
            Número total de registros salvos
        """
        total_saved = 0
        
        try:
            db = SessionLocal()
            
            for sport, matches in data.items():
                for match in matches:
                    try:
                        # Cria ou atualiza registro da partida
                        partida = PartidaSofascore(
                            partida_id=f"{sport}_{hash(match['match_url'])}",
                            data_partida=datetime.fromisoformat(match['collected_at']),
                            time_casa=match['home_team'],
                            time_visitante=match['away_team'],
                            placar_final=match['score'],
                            estatisticas_json=str(match)
                        )
                        
                        db.add(partida)
                        total_saved += 1
                        
                    except Exception as e:
                        logger.warning(f"Erro ao salvar partida: {e}")
                        continue
            
            db.commit()
            logger.info(f"✅ {total_saved} registros salvos no banco de dados")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            if db:
                db.rollback()
        
        finally:
            if db:
                db.close()
        
        return total_saved

# Função de demonstração
async def demo_sofascore_enhanced():
    """Demonstra o scraper melhorado do SofaScore."""
    print("🎭 DEMONSTRAÇÃO DO SCRAPER SOFASCORE MELHORADO COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Configuração do scraper
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        scraper = SofaScorePlaywrightScraperEnhanced(**config)
        
        # Coleta dados de todos os esportes
        print("🔄 Coletando dados de todos os esportes...")
        data = await scraper.collect_all_sports_data()
        
        # Mostra resumo dos dados coletados
        print("\n📊 RESUMO DOS DADOS COLETADOS:")
        print("-" * 40)
        for sport, matches in data.items():
            print(f"🏈 {sport.capitalize()}: {len(matches)} partidas")
        
        # Salva no banco de dados
        print("\n💾 Salvando dados no banco...")
        total_saved = await scraper.save_to_database(data)
        print(f"✅ Total de registros salvos: {total_saved}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

if __name__ == "__main__":
    # Executa demonstração
    asyncio.run(demo_sofascore_enhanced())
