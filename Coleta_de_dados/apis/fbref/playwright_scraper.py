"""
SCRAPER DO FBREF COM PLAYWRIGHT
================================

Scraper avançado para o FBRef usando Playwright da Microsoft.
Oferece melhor performance, estabilidade e funcionalidades avançadas.

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

class FBRefPlaywrightScraper(PlaywrightBaseScraper):
    """
    Scraper do FBRef usando Playwright.
    
    Funcionalidades:
    - Coleta de estatísticas de clubes
    - Coleta de dados de partidas
    - Coleta de estatísticas de jogadores
    - Anti-detecção avançado
    - Screenshots automáticos para debug
    - Interceptação de requisições
    """
    
    def __init__(self, **kwargs):
        """Inicializa o scraper do FBRef."""
        # Configurações padrão
        default_config = {
            "browser_type": "chromium",
            "headless": True,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "timeout": 60000,
            "screenshot_dir": "screenshots/fbref",
            "enable_video": False,
            "enable_har": True
        }
        
        # Atualizar com kwargs (permitindo override)
        default_config.update(kwargs)
        
        super().__init__(**default_config)
        
        # URLs base do FBRef
        self.base_url = "https://fbref.com"
        self.competitions_url = f"{self.base_url}/en/comps"
        
        # Seletores CSS para elementos principais
        self.selectors = {
            "competition_link": "a[href*='/en/comps/']",
            "club_link": "a[href*='/en/squad/']",
            "player_link": "a[href*='/en/players/']",
            "match_link": "a[href*='/en/matches/']",
            "stats_table": "table.stats_table",
            "pagination": ".pagination",
            "next_page": "a[aria-label='Next page']",
            "loading": ".loading, .spinner",
            "error": ".error, .alert"
        }
        
        # Configurações específicas do FBRef
        self.rate_limit_delay = 2.0  # Delay entre requisições
        self.max_pages_per_session = 50  # Máximo de páginas por sessão
        self.session_page_count = 0
        
        logger.info("🎭 FBRefPlaywrightScraper inicializado")
    
    async def start_session(self):
        """Inicia uma nova sessão de scraping."""
        await self.start()
        self.session_page_count = 0
        
        # Configurar headers específicos do FBRef
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        logger.info("🚀 Sessão de scraping iniciada")
    
    async def end_session(self):
        """Finaliza a sessão de scraping."""
        await self.stop()
        logger.info(f"🛑 Sessão finalizada. Páginas processadas: {self.session_page_count}")
    
    async def collect_competitions(self) -> List[Dict[str, Any]]:
        """
        Coleta lista de competições disponíveis.
        
        Returns:
            Lista de competições com informações básicas
        """
        try:
            logger.info("🏆 Coletando lista de competições...")
            
            if not await self.navigate_to(self.competitions_url):
                raise Exception("Falha na navegação para página de competições")
            
            # Aguardar carregamento da página
            await self.wait_for_element(self.selectors["competition_link"])
            
            # Coletar links das competições
            competition_elements = await self.page.query_selector_all(self.selectors["competition_link"])
            
            competitions = []
            for element in competition_elements:
                try:
                    href = await element.get_attribute("href")
                    text = await element.text_content()
                    
                    if href and text:
                        competition = {
                            "name": text.strip(),
                            "url": f"{self.base_url}{href}",
                            "slug": href.split("/")[-1],
                            "collected_at": datetime.now().isoformat()
                        }
                        competitions.append(competition)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar elemento de competição: {e}")
                    continue
            
            logger.info(f"✅ {len(competitions)} competições coletadas")
            return competitions
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar competições: {e}")
            await self.take_screenshot("error_competitions.png")
            return []
    
    async def collect_competition_details(self, competition_url: str) -> Dict[str, Any]:
        """
        Coleta detalhes de uma competição específica.
        
        Args:
            competition_url: URL da competição
        
        Returns:
            Dicionário com detalhes da competição
        """
        try:
            logger.info(f"🏆 Coletando detalhes da competição: {competition_url}")
            
            if not await self.navigate_to(competition_url):
                raise Exception(f"Falha na navegação para: {competition_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["stats_table"])
            
            # Coletar informações básicas
            title = await self.get_text("h1")
            season = await self.get_text("h1 + p")
            
            # Coletar estatísticas da tabela
            stats_table = await self.page.query_selector(self.selectors["stats_table"])
            if stats_table:
                stats_data = await self._extract_table_data(stats_table)
            else:
                stats_data = []
            
            competition_details = {
                "title": title,
                "season": season,
                "url": competition_url,
                "stats": stats_data,
                "collected_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Detalhes da competição coletados: {title}")
            return competition_details
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar detalhes da competição: {e}")
            await self.take_screenshot("error_competition_details.png")
            return {}
    
    async def collect_club_stats(self, club_url: str) -> Dict[str, Any]:
        """
        Coleta estatísticas de um clube específico.
        
        Args:
            club_url: URL do clube
        
        Returns:
            Dicionário com estatísticas do clube
        """
        try:
            logger.info(f"⚽ Coletando estatísticas do clube: {club_url}")
            
            if not await self.navigate_to(club_url):
                raise Exception(f"Falha na navegação para: {club_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["stats_table"])
            
            # Coletar informações básicas
            club_name = await self.get_text("h1")
            
            # Coletar estatísticas das tabelas
            stats_tables = await self.page.query_selector_all(self.selectors["stats_table"])
            
            club_stats = {
                "name": club_name,
                "url": club_url,
                "tables": []
            }
            
            for i, table in enumerate(stats_tables):
                try:
                    table_data = await self._extract_table_data(table)
                    table_title = await self._get_table_title(table)
                    
                    club_stats["tables"].append({
                        "title": table_title,
                        "data": table_data
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar tabela {i}: {e}")
                    continue
            
            club_stats["collected_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Estatísticas do clube coletadas: {club_name}")
            return club_stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas do clube: {e}")
            await self.take_screenshot("error_club_stats.png")
            return {}
    
    async def collect_player_stats(self, player_url: str) -> Dict[str, Any]:
        """
        Coleta estatísticas de um jogador específico.
        
        Args:
            player_url: URL do jogador
        
        Returns:
            Dicionário com estatísticas do jogador
        """
        try:
            logger.info(f"👤 Coletando estatísticas do jogador: {player_url}")
            
            if not await self.navigate_to(player_url):
                raise Exception(f"Falha na navegação para: {player_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["stats_table"])
            
            # Coletar informações básicas
            player_name = await self.get_text("h1")
            position = await self.get_text("p:has-text('Position:')")
            
            # Coletar estatísticas das tabelas
            stats_tables = await self.page.query_selector_all(self.selectors["stats_table"])
            
            player_stats = {
                "name": player_name,
                "position": position,
                "url": player_url,
                "tables": []
            }
            
            for i, table in enumerate(stats_tables):
                try:
                    table_data = await self._extract_table_data(table)
                    table_title = await self._get_table_title(table)
                    
                    player_stats["tables"].append({
                        "title": table_title,
                        "data": table_data
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar tabela {i}: {e}")
                    continue
            
            player_stats["collected_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ Estatísticas do jogador coletadas: {player_name}")
            return player_stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas do jogador: {e}")
            await self.take_screenshot("error_player_stats.png")
            return {}
    
    async def collect_matches(self, competition_url: str, season: str = None) -> List[Dict[str, Any]]:
        """
        Coleta dados de partidas de uma competição.
        
        Args:
            competition_url: URL da competição
            season: Temporada específica (opcional)
        
        Returns:
            Lista de partidas com dados
        """
        try:
            logger.info(f"⚽ Coletando partidas da competição: {competition_url}")
            
            # Navegar para página de partidas
            matches_url = competition_url.replace("/Stats", "/Scores-and-Fixtures")
            if not await self.navigate_to(matches_url):
                raise Exception(f"Falha na navegação para: {matches_url}")
            
            # Aguardar carregamento
            await self.wait_for_element(self.selectors["stats_table"])
            
            matches = []
            page = 1
            
            while page <= self.max_pages_per_session:
                try:
                    logger.info(f"📄 Processando página {page} de partidas")
                    
                    # Coletar partidas da página atual
                    page_matches = await self._extract_matches_from_page()
                    matches.extend(page_matches)
                    
                    # Verificar se há próxima página
                    next_button = await self.page.query_selector(self.selectors["next_page"])
                    if not next_button or not await next_button.is_visible():
                        logger.info("📄 Última página de partidas alcançada")
                        break
                    
                    # Navegar para próxima página
                    await next_button.click()
                    await self.wait_for_element(self.selectors["stats_table"])
                    
                    page += 1
                    self.session_page_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar página {page}: {e}")
                    break
            
            logger.info(f"✅ {len(matches)} partidas coletadas de {page} páginas")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar partidas: {e}")
            await self.take_screenshot("error_matches.png")
            return []
    
    async def _extract_table_data(self, table_element) -> List[Dict[str, Any]]:
        """
        Extrai dados de uma tabela HTML.
        
        Args:
            table_element: Elemento da tabela
        
        Returns:
            Lista de linhas com dados
        """
        try:
            # Obter cabeçalhos
            headers = []
            header_elements = await table_element.query_selector_all("thead th, tr:first-child th")
            
            for header in header_elements:
                header_text = await header.text_content()
                if header_text:
                    headers.append(header_text.strip())
            
            # Obter linhas de dados
            rows = []
            row_elements = await table_element.query_selector_all("tbody tr, tr:not(:first-child)")
            
            for row in row_elements:
                try:
                    cell_elements = await row.query_selector_all("td, th")
                    row_data = {}
                    
                    for i, cell in enumerate(cell_elements):
                        if i < len(headers):
                            cell_text = await cell.text_content()
                            row_data[headers[i]] = cell_text.strip() if cell_text else ""
                    
                    if row_data:
                        rows.append(row_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar linha da tabela: {e}")
                    continue
            
            return rows
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados da tabela: {e}")
            return []
    
    async def _get_table_title(self, table_element) -> str:
        """
        Obtém título de uma tabela.
        
        Args:
            table_element: Elemento da tabela
        
        Returns:
            Título da tabela
        """
        try:
            # Tentar encontrar título acima da tabela
            title_element = await table_element.query_selector("h2, h3, caption")
            if title_element:
                return await title_element.text_content()
            
            # Tentar encontrar título no elemento pai
            parent = await table_element.query_selector("xpath=..")
            if parent:
                title_element = await parent.query_selector("h2, h3, caption")
                if title_element:
                    return await title_element.text_content()
            
            return "Tabela sem título"
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao obter título da tabela: {e}")
            return "Tabela sem título"
    
    async def _extract_matches_from_page(self) -> List[Dict[str, Any]]:
        """
        Extrai dados de partidas de uma página.
        
        Returns:
            Lista de partidas da página
        """
        try:
            matches = []
            
            # Encontrar tabela de partidas
            table = await self.page.query_selector(self.selectors["stats_table"])
            if not table:
                return matches
            
            # Extrair dados da tabela
            table_data = await self._extract_table_data(table)
            
            # Processar cada linha como uma partida
            for row in table_data:
                if "Date" in row and "Home" in row and "Away" in row:
                    match = {
                        "date": row.get("Date", ""),
                        "home_team": row.get("Home", ""),
                        "away_team": row.get("Away", ""),
                        "score": row.get("Score", ""),
                        "competition": row.get("Comp", ""),
                        "venue": row.get("Venue", ""),
                        "attendance": row.get("Attendance", ""),
                        "referee": row.get("Referee", ""),
                        "collected_at": datetime.now().isoformat()
                    }
                    matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair partidas da página: {e}")
            return []
    
    async def collect_all_data(self, competition_urls: List[str]) -> Dict[str, Any]:
        """
        Coleta todos os dados de múltiplas competições.
        
        Args:
            competition_urls: Lista de URLs de competições
        
        Returns:
            Dicionário com todos os dados coletados
        """
        try:
            logger.info(f"🚀 Iniciando coleta completa de {len(competition_urls)} competições")
            
            all_data = {
                "competitions": [],
                "clubs": [],
                "players": [],
                "matches": [],
                "collection_info": {
                    "started_at": datetime.now().isoformat(),
                    "total_competitions": len(competition_urls),
                    "successful_collections": 0,
                    "failed_collections": 0
                }
            }
            
            for i, comp_url in enumerate(competition_urls):
                try:
                    logger.info(f"🏆 Processando competição {i+1}/{len(competition_urls)}: {comp_url}")
                    
                    # Coletar detalhes da competição
                    comp_details = await self.collect_competition_details(comp_url)
                    if comp_details:
                        all_data["competitions"].append(comp_details)
                        all_data["collection_info"]["successful_collections"] += 1
                    
                    # Coletar partidas
                    matches = await self.collect_matches(comp_url)
                    all_data["matches"].extend(matches)
                    
                    # Rate limiting entre competições
                    if i < len(competition_urls) - 1:
                        await asyncio.sleep(self.rate_limit_delay * 2)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar competição {comp_url}: {e}")
                    all_data["collection_info"]["failed_collections"] += 1
                    continue
            
            all_data["collection_info"]["finished_at"] = datetime.now().isoformat()
            all_data["collection_info"]["total_matches"] = len(all_data["matches"])
            
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
                filename = f"fbref_data_{timestamp}.json"
            
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
def run_fbref_scraper(competition_urls: List[str], **kwargs) -> Dict[str, Any]:
    """
    Executa o scraper do FBRef de forma síncrona.
    
    Args:
        competition_urls: Lista de URLs de competições
        **kwargs: Argumentos para o scraper
    
    Returns:
        Dados coletados
    """
    async def _run():
        async with FBRefPlaywrightScraper(**kwargs) as scraper:
            return await scraper.collect_all_data(competition_urls)
    
    return asyncio.run(_run())

# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # URLs de exemplo
    competition_urls = [
        "https://fbref.com/en/comps/9/Premier-League-Stats",
        "https://fbref.com/en/comps/12/La-Liga-Stats"
    ]
    
    # Executar scraper
    data = run_fbref_scraper(competition_urls, headless=False)
    
    # Salvar dados
    if data:
        scraper = FBRefPlaywrightScraper()
        asyncio.run(scraper.save_data(data))
