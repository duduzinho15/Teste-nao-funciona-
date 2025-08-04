"""
MÓDULO DE ESTATÍSTICAS AVANÇADAS DO FBREF
========================================

Este módulo fornece funcionalidades para extrair estatísticas avançadas de partidas
do FBRef, incluindo:
- xG (Expected Goals)
- xA (Expected Assists)
- Formações táticas
- Outras métricas avançadas

Utiliza uma abordagem híbrida com Selenium para renderização de conteúdo dinâmico
e BeautifulSoup para análise estática do HTML.

Autor: Sistema de Análise de Dados
Data: 2025-08-03
Versão: 1.0
"""

import os
import re
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .selenium_config import SeleniumConfig, driver_context
from .fbref_utils import fazer_requisicao, extrair_conteudo_comentarios_html, processar_soup_com_comentarios

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class AdvancedMatchStats:
    """Classe para armazenar estatísticas avançadas de uma partida."""
    match_url: str
    home_team: str
    away_team: str
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    home_xa: Optional[float] = None
    away_xa: Optional[float] = None
    home_formation: Optional[str] = None
    away_formation: Optional[str] = None
    home_players_stats: Optional[List[Dict[str, Any]]] = None
    away_players_stats: Optional[List[Dict[str, Any]]] = None
    match_date: Optional[str] = None
    competition: Optional[str] = None
    extracted_at: str = datetime.utcnow().isoformat()

class AdvancedStatsExtractor:
    """Classe para extrair estatísticas avançadas de partidas do FBRef."""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """Inicializa o extrator de estatísticas avançadas.
        
        Args:
            headless: Se True, executa o navegador em modo headless.
            timeout: Tempo máximo de espera para carregamento de elementos (segundos).
        """
        self.headless = headless
        self.timeout = timeout
        self.selenium_config = SeleniumConfig(
            headless=headless,
            page_load_timeout=timeout,
            default_timeout=timeout
        )
        logger.info(f"AdvancedStatsExtractor inicializado (headless={headless}, timeout={timeout}s)")
    
    def extract_from_url(self, match_url: str) -> Optional[AdvancedMatchStats]:
        """Extrai estatísticas avançadas a partir da URL de uma partida.
        
        Args:
            match_url: URL da partida no FBRef.
            
        Returns:
            AdvancedMatchStats com as estatísticas extraídas ou None em caso de falha.
        """
        logger.info(f"Iniciando extração de estatísticas avançadas: {match_url}")
        
        # Primeiro, tenta com requisição HTTP simples (mais rápido)
        soup = fazer_requisicao(match_url, use_selenium=False)
        
        # Se falhar ou não encontrar dados suficientes, tenta com Selenium
        if not self._has_advanced_stats(soup):
            logger.info("Dados avançados não encontrados no HTML estático, tentando com Selenium...")
            soup = self._get_page_with_selenium(match_url)
            
            if not soup:
                logger.error("Falha ao carregar a página com Selenium")
                return None
        
        # Processa o HTML para extrair os dados
        return self._parse_advanced_stats(match_url, soup)
    
    def _get_page_with_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Obtém o conteúdo da página usando Selenium para renderização completa."""
        with driver_context(headless=self.headless) as driver:
            if not driver:
                logger.error("Falha ao inicializar o WebDriver")
                return None
                
            try:
                logger.debug(f"Acessando URL com Selenium: {url}")
                driver.get(url)
                
                # Aguarda o carregamento da página
                WebDriverWait(driver, self.timeout).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                # Aguarda um pouco mais para garantir que os dados dinâmicos sejam carregados
                time.sleep(3)
                
                # Tenta localizar elementos que contêm estatísticas avançadas
                try:
                    # Aguarda o carregamento dos elementos de estatísticas avançadas
                    WebDriverWait(driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".scorebox, .shots, .stats, .lineup"))
                    )
                except TimeoutException:
                    logger.warning("Elementos de estatísticas avançadas não encontrados na página")
                
                # Obtém o HTML renderizado
                page_source = driver.page_source
                return BeautifulSoup(page_source, 'lxml')
                
            except Exception as e:
                logger.error(f"Erro ao acessar a página com Selenium: {str(e)}")
                return None
    
    def _has_advanced_stats(self, soup: BeautifulSoup) -> bool:
        """Verifica se o HTML contém estatísticas avançadas."""
        if not soup:
            return False
            
        # Verifica a presença de elementos que indicam estatísticas avançadas
        stats_indicators = [
            "Expected Goals", "xG", "Expected Assists", "xA",
            "Shot Creating Actions", "Passes Attempted", "Progressive Passes"
        ]
        
        page_text = soup.get_text()
        return any(indicator in page_text for indicator in stats_indicators)
    
    def _parse_advanced_stats(self, match_url: str, soup: BeautifulSoup) -> Optional[AdvancedMatchStats]:
        """Analisa o HTML e extrai as estatísticas avançadas."""
        try:
            # Processa comentários HTML que podem conter dados importantes
            soup = processar_soup_com_comentarios(soup)
            
            # Extrai informações básicas da partida
            match_info = self._extract_match_info(soup)
            if not match_info:
                logger.error("Não foi possível extrair informações básicas da partida")
                return None
            
            # Cria o objeto de estatísticas avançadas
            stats = AdvancedMatchStats(
                match_url=match_url,
                home_team=match_info.get('home_team', ''),
                away_team=match_info.get('away_team', ''),
                match_date=match_info.get('match_date'),
                competition=match_info.get('competition')
            )
            
            # Extrai estatísticas avançadas
            self._extract_expected_goals(stats, soup)
            self._extract_expected_assists(stats, soup)
            self._extract_formations(stats, soup)
            self._extract_players_advanced_stats(stats, soup)
            
            logger.info(f"Estatísticas avançadas extraídas com sucesso para {stats.home_team} vs {stats.away_team}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao analisar estatísticas avançadas: {str(e)}", exc_info=True)
            return None
    
    def _extract_match_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai informações básicas da partida."""
        try:
            # Tenta extrair do scorebox
            scorebox = soup.select_one(".scorebox")
            if not scorebox:
                return {}
            
            # Extrai nomes dos times
            home_team = scorebox.select_one(".scores .scorebox .scorebox_meta strong")
            away_team = scorebox.select(".scores .scorebox .scorebox_meta strong")[1] if scorebox.select(".scores .scorebox .scorebox_meta strong") else None
            
            # Extrai data da partida
            match_date = None
            date_elem = soup.select_one("div.scores .scorebox_meta div:first-child")
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Tenta extrair a data do texto (formato pode variar)
                date_match = re.search(r'\w+\s+\w+\s+\d{1,2},\s+\d{4}', date_text)
                if date_match:
                    match_date = date_match.group(0)
            
            # Extrai competição
            competition = None
            comp_elem = soup.select_one("div.scores .scorebox_meta a")
            if comp_elem:
                competition = comp_elem.get_text(strip=True)
            
            return {
                'home_team': home_team.get_text(strip=True) if home_team else 'Desconhecido',
                'away_team': away_team.get_text(strip=True) if away_team else 'Desconhecido',
                'match_date': match_date,
                'competition': competition
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações da partida: {str(e)}")
            return {}
    
    def _extract_expected_goals(self, stats: AdvancedMatchStats, soup: BeautifulSoup) -> None:
        """Extrai estatísticas de expected goals (xG)."""
        try:
            # Procura por tabelas que contenham estatísticas de xG
            tables = soup.select("table.stats_table")
            
            for table in tables:
                # Verifica se a tabela contém estatísticas de xG
                headers = [th.get_text(strip=True) for th in table.select("thead th")]
                if "xG" not in ' '.join(headers):
                    continue
                
                # Encontra as linhas de xG para cada time
                rows = table.select("tbody tr")
                for row in rows:
                    cells = row.select("th, td")
                    if len(cells) < 2:
                        continue
                        
                    team = cells[0].get_text(strip=True)
                    xg_cell = next((cell for cell in cells if 'xG' in cell.get('data-stat', '')), None)
                    
                    if not xg_cell:
                        continue
                        
                    try:
                        xg_value = float(xg_cell.get_text(strip=True))
                        if team == stats.home_team:
                            stats.home_xg = xg_value
                        elif team == stats.away_team:
                            stats.away_xg = xg_value
                    except (ValueError, TypeError):
                        logger.warning(f"Valor de xG inválido para {team}")
                
                # Se encontrou estatísticas para ambos os times, pode parar de procurar
                if stats.home_xg is not None and stats.away_xg is not None:
                    break
                    
        except Exception as e:
            logger.error(f"Erro ao extrair expected goals: {str(e)}")
    
    def _extract_expected_assists(self, stats: AdvancedMatchStats, soup: BeautifulSoup) -> None:
        """Extrai estatísticas de expected assists (xA)."""
        try:
            # Procura por tabelas que contenham estatísticas de xA
            # Nota: xA pode estar em uma tabela separada ou na mesma tabela de xG
            tables = soup.select("table.stats_table")
            
            for table in tables:
                # Verifica se a tabela contém estatísticas de xA
                headers = [th.get_text(strip=True) for th in table.select("thead th")]
                if "xA" not in ' '.join(headers):
                    continue
                
                # Encontra as linhas de xA para cada time
                rows = table.select("tbody tr")
                for row in rows:
                    cells = row.select("th, td")
                    if len(cells) < 2:
                        continue
                        
                    team = cells[0].get_text(strip=True)
                    xa_cell = next((cell for cell in cells if 'xA' in cell.get('data-stat', '')), None)
                    
                    if not xa_cell:
                        continue
                        
                    try:
                        xa_value = float(xa_cell.get_text(strip=True))
                        if team == stats.home_team:
                            stats.home_xa = xa_value
                        elif team == stats.away_team:
                            stats.away_xa = xa_value
                    except (ValueError, TypeError):
                        logger.warning(f"Valor de xA inválido para {team}")
                
                # Se encontrou estatísticas para ambos os times, pode parar de procurar
                if stats.home_xa is not None and stats.away_xa is not None:
                    break
                    
        except Exception as e:
            logger.error(f"Erro ao extrair expected assists: {str(e)}")
    
    def _extract_formations(self, stats: AdvancedMatchStats, soup: BeautifulSoup) -> None:
        """Extrai as formações táticas dos times."""
        try:
            # Tenta encontrar as formações no campo de jogo
            field_wrap = soup.select_one("#field_wrap")
            if not field_wrap:
                logger.warning("Elemento field_wrap não encontrado")
                return
            
            # Extrai as formações dos times
            # Nota: Esta é uma implementação simplificada e pode precisar de ajustes
            # dependendo da estrutura exata do HTML do FBRef
            
            # Tenta encontrar as formações no texto da página
            page_text = soup.get_text()
            
            # Padrão para encontrar formações (ex: "4-4-2", "4-3-3", etc.)
            formation_pattern = r"\b\d-\d(-\d+)?\b"
            
            # Tenta encontrar formações próximas aos nomes dos times
            home_formation = None
            away_formation = None
            
            # Procura formações em elementos de texto próximos aos nomes dos times
            for elem in soup.find_all(string=re.compile(formation_pattern)):
                parent_text = elem.parent.get_text()
                if stats.home_team in parent_text:
                    match = re.search(formation_pattern, parent_text)
                    if match:
                        home_formation = match.group(0)
                elif stats.away_team in parent_text:
                    match = re.search(formation_pattern, parent_text)
                    if match:
                        away_formation = match.group(0)
            
            # Se não encontrou nos textos, tenta deduzir das posições dos jogadores
            if not home_formation or not away_formation:
                home_formation = self._deduce_formation_from_positions(field_wrap, is_home=True)
                away_formation = self._deduce_formation_from_positions(field_wrap, is_home=False)
            
            stats.home_formation = home_formation
            stats.away_formation = away_formation
            
        except Exception as e:
            logger.error(f"Erro ao extrair formações táticas: {str(e)}")
    
    def _deduce_formation_from_positions(self, field_wrap, is_home: bool = True) -> Optional[str]:
        """Tenta deduzir a formação com base nas posições dos jogadores no campo."""
        try:
            # Esta é uma implementação simplificada que conta jogadores por linha
            # Pode precisar de ajustes dependendo da estrutura exata do HTML
            
            # Seleciona os elementos dos jogadores (ajuste o seletor conforme necessário)
            player_elements = field_wrap.select(f".{'a' if is_home else 'b'}")
            
            if not player_elements:
                return None
            
            # Extrai as posições Y (altura) dos jogadores
            y_positions = []
            for player in player_elements:
                style = player.get('style', '')
                y_match = re.search(r'top:\s*calc\((\d+)%', style)
                if y_match:
                    y_positions.append(int(y_match.group(1)))
            
            if not y_positions:
                return None
            
            # Agrupa as posições em linhas (agrupamentos de jogadores na mesma altura)
            y_positions_sorted = sorted(y_positions)
            lines = []
            current_line = [y_positions_sorted[0]]
            
            for y in y_positions_sorted[1:]:
                if abs(y - current_line[-1]) < 5:  # Tolerância de 5% para estar na mesma linha
                    current_line.append(y)
                else:
                    lines.append(len(current_line))
                    current_line = [y]
            
            if current_line:
                lines.append(len(current_line))
            
            # Remove o goleiro (geralmente o primeiro número)
            if len(lines) > 1 and lines[0] == 1:
                lines = lines[1:]
            
            # Retorna a formação como string (ex: "4-4-2")
            return '-'.join(map(str, lines))
            
        except Exception as e:
            logger.warning(f"Erro ao deduzir formação: {str(e)}")
            return None
    
    def _extract_players_advanced_stats(self, stats: AdvancedMatchStats, soup: BeautifulSoup) -> None:
        """Extrai estatísticas avançadas dos jogadores."""
        try:
            # Inicializa as listas de estatísticas dos jogadores
            stats.home_players_stats = []
            stats.away_players_stats = []
            
            # Encontra as tabelas de estatísticas dos jogadores
            # Nota: O FBRef pode ter várias tabelas com diferentes estatísticas
            player_tables = soup.select("table.stats_table")
            
            for table in player_tables:
                # Verifica se é uma tabela de estatísticas de jogadores
                if not any(th.get_text(strip=True) in ["Player", "Jogador"] for th in table.select("thead th")):
                    continue
                
                # Determina se é a tabela do time da casa ou visitante
                # (isso pode variar dependendo da estrutura da página)
                is_home_table = "home" in table.get('id', '').lower() or "_h" in table.get('id', '').lower()
                
                # Extrai as estatísticas dos jogadores
                rows = table.select("tbody tr")
                for row in rows:
                    # Pula linhas de cabeçalho ou totais
                    if row.get('class') and any(c in row.get('class') for c in ['thead', 'sum', 'total']):
                        continue
                    
                    # Extrai o nome do jogador
                    player_cell = row.select_one("th[data-stat='player']")
                    if not player_cell:
                        continue
                    
                    player_name = player_cell.get_text(strip=True)
                    if not player_name or player_name == "Player":
                        continue
                    
                    # Extrai as estatísticas do jogador
                    player_stats = {'name': player_name}
                    
                    # Adiciona estatísticas básicas
                    for cell in row.select("td[data-stat]"):
                        stat_name = cell.get('data-stat')
                        stat_value = cell.get_text(strip=True)
                        
                        # Converte valores numéricos quando apropriado
                        if stat_value.replace('.', '').isdigit():
                            if '.' in stat_value:
                                player_stats[stat_name] = float(stat_value)
                            else:
                                player_stats[stat_name] = int(stat_value)
                        else:
                            player_stats[stat_name] = stat_value
                    
                    # Adiciona estatísticas avançadas adicionais, se disponíveis
                    self._extract_additional_player_stats(player_stats, row)
                    
                    # Adiciona às estatísticas do time apropriado
                    if is_home_table:
                        stats.home_players_stats.append(player_stats)
                    else:
                        stats.away_players_stats.append(player_stats)
            
        except Exception as e:
            logger.error(f"Erro ao extrair estatísticas dos jogadores: {str(e)}")
    
    def _extract_additional_player_stats(self, player_stats: Dict[str, Any], row) -> None:
        """Extrai estatísticas adicionais específicas dos jogadores."""
        try:
            # Extrai xG (expected goals) do jogador, se disponível
            xg_cell = row.select_one("td[data-stat='xg']")
            if xg_cell:
                try:
                    player_stats['xg'] = float(xg_cell.get_text(strip=True) or 0)
                except (ValueError, TypeError):
                    player_stats['xg'] = 0.0
            
            # Extrai xA (expected assists) do jogador, se disponível
            xa_cell = row.select_one("td[data-stat='xa']")
            if xa_cell:
                try:
                    player_stats['xa'] = float(xa_cell.get_text(strip=True) or 0)
                except (ValueError, TypeError):
                    player_stats['xa'] = 0.0
            
            # Extrai outras métricas avançadas conforme necessário
            # Exemplo: passes progressivos, duelos ganhos, etc.
            
        except Exception as e:
            logger.warning(f"Erro ao extrair estatísticas adicionais do jogador: {str(e)}")

def extract_advanced_match_stats(match_url: str, headless: bool = True) -> Optional[AdvancedMatchStats]:
    """Função de conveniência para extrair estatísticas avançadas de uma partida.
    
    Args:
        match_url: URL da partida no FBRef.
        headless: Se True, executa o navegador em modo headless.
        
    Returns:
        AdvancedMatchStats com as estatísticas extraídas ou None em caso de falha.
    """
    extractor = AdvancedStatsExtractor(headless=headless)
    return extractor.extract_from_url(match_url)

# Exemplo de uso
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemplo de URL de partida (substitua por uma URL real)
    SAMPLE_MATCH_URL = "https://fbref.com/en/matches/..."
    
    print("🔍 Iniciando extração de estatísticas avançadas...")
    stats = extract_advanced_match_stats(SAMPLE_MATCH_URL)
    
    if stats:
        print("\n✅ Estatísticas avançadas extraídas com sucesso!")
        print(f"🏠 {stats.home_team} {stats.home_xg or 'N/A'} - {stats.away_xg or 'N/A'} {stats.away_team} 🏠")
        print(f"📅 Data: {stats.match_date or 'N/A'}")
        print(f"🏆 Competição: {stats.competition or 'N/A'}")
        print(f"🔢 Formações: {stats.home_team} {stats.home_formation or 'N/A'} vs {stats.away_team} {stats.away_formation or 'N/A'}")
        
        # Exemplo de estatísticas de jogadores (apenas os primeiros 3 de cada time)
        if stats.home_players_stats:
            print("\n👥 Estatísticas dos jogadores (casa - primeiros 3):")
            for player in stats.home_players_stats[:3]:
                print(f"- {player.get('name')}: {player.get('xg', 0):.2f} xG, {player.get('xa', 0):.2f} xA")
        
        if stats.away_players_stats:
            print("\n👥 Estatísticas dos jogadores (visitante - primeiros 3):")
            for player in stats.away_players_stats[:3]:
                print(f"- {player.get('name')}: {player.get('xg', 0):.2f} xG, {player.get('xa', 0):.2f} xA")
    else:
        print("❌ Falha ao extrair estatísticas avançadas.")
