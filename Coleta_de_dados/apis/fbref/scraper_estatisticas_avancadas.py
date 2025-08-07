"""
SCRAPER DE ESTATÍSTICAS AVANÇADAS DO FBREF
==========================================

Módulo para extrair estatísticas avançadas de partidas do FBRef:
- Expected Goals (xG) e Expected Assists (xA)
- Formações táticas dos times
- Estatísticas detalhadas de jogadores

Autor: Sistema de Coleta de Dados
Data: 2025-08-03
Versão: 1.0
"""

import logging
from typing import Dict, List, Tuple, Optional
import re
from bs4 import BeautifulSoup
import pandas as pd

# Configuração de logging
logger = logging.getLogger(__name__)

class AdvancedMatchScraper:
    """Classe para extrair estatísticas avançadas de partidas do FBRef."""
    
    def __init__(self, session):
        """Inicializa o scraper com uma sessão HTTP."""
        self.session = session
        self.base_url = "https://fbref.com"
    
    async def get_match_report_page(self, match_url: str) -> Optional[BeautifulSoup]:
        """
        Obtém a página de relatório da partida.
        
        Args:
            match_url: URL da partida no FBRef
            
        Returns:
            BeautifulSoup da página de relatório ou None em caso de erro
        """
        try:
            # Garante que temos a URL completa
            if not match_url.startswith('http'):
                match_url = f"{self.base_url}{match_url}"
                
            # Adiciona sufixo para a página de relatório se necessário
            if '/match/' in match_url and not match_url.endswith('/matchreport'):
                match_url = match_url.replace('/match/', '/matchreport/')
            
            logger.info(f"Obtendo página de relatório: {match_url}")
            
            async with self.session.get(match_url) as response:
                response.raise_for_status()
                html = await response.text()
                return BeautifulSoup(html, 'html.parser')
                
        except Exception as e:
            logger.error(f"Erro ao obter relatório da partida {match_url}: {e}")
            return None
    
    def extract_match_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai metadados da partida, incluindo formações táticas."""
        metadata = {
            'formacao_casa': None,
            'formacao_visitante': None,
            'arbitro': None,
            'estadio': None,
            'publico': None
        }
        
        try:
            # Tenta encontrar as formações táticas
            scorebox = soup.find('div', class_='scorebox')
            if scorebox:
                # Encontra os elementos que contêm as formações
                formations = scorebox.find_all('div', class_='lineup')
                if len(formations) >= 2:
                    # Extrai a formação do time da casa (primeiro elemento)
                    home_formation = formations[0].find('div', class_='lineup')
                    if home_formation:
                        metadata['formacao_casa'] = home_formation.get_text(strip=True)
                    
                    # Extrai a formação do time visitante (segundo elemento)
                    away_formation = formations[1].find('div', class_='lineup')
                    if away_formation:
                        metadata['formacao_visitante'] = away_formation.get_text(strip=True)
            
            # Extrai outras informações de metadados
            game_info = soup.find('div', class_='scorebox_meta')
            if game_info:
                for div in game_info.find_all('div'):
                    text = div.get_text(strip=True)
                    if 'Referee:' in text:
                        metadata['arbitro'] = text.replace('Referee:', '').strip()
                    elif 'Venue:' in text:
                        metadata['estadio'] = text.replace('Venue:', '').strip()
                    elif 'Attendance:' in text:
                        metadata['publico'] = text.replace('Attendance:', '').strip()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erro ao extrair metadados da partida: {e}")
            return metadata
    
    def extract_expected_goals(self, soup: BeautifulSoup) -> Dict[str, float]:
        """
        Extrai as estatísticas de Expected Goals (xG) da partida.
        
        Returns:
            Dicionário com xG do time da casa e visitante
        """
        xg_data = {
            'xg_casa': None,
            'xg_visitante': None,
            'xa_casa': None,
            'xa_visitante': None
        }
        
        try:
            # Encontra a tabela de estatísticas de chutes
            shot_table = soup.find('table', id='shots_all')
            if not shot_table:
                return xg_data
            
            # Converte a tabela para DataFrame
            df = pd.read_html(str(shot_table))[0]
            
            # Verifica se a tabela tem as colunas esperadas
            if 'xG' in df.columns:
                # Soma os xG por time
                xg_by_team = df.groupby('Squad')['xG'].sum()
                
                # Atribui os valores aos times corretos
                teams = xg_by_team.index.tolist()
                if len(teams) >= 2:
                    xg_data['xg_casa'] = float(xg_by_team[teams[0]])
                    xg_data['xg_visitante'] = float(xg_by_team[teams[1]])
            
            # Tenta extrair xA (Expected Assists) se disponível
            if 'xAG' in df.columns:
                xa_by_team = df.groupby('Squad')['xAG'].sum()
                teams = xa_by_team.index.tolist()
                if len(teams) >= 2:
                    xg_data['xa_casa'] = float(xa_by_team[teams[0]])
                    xg_data['xa_visitante'] = float(xa_by_team[teams[1]])
            
            return xg_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair xG/xA: {e}")
            return xg_data
    
    def extract_player_advanced_stats(self, soup: BeautifulSoup) -> Dict[str, List[Dict]]:
        """
        Extrai estatísticas avançadas de jogadores da partida.
        
        Returns:
            Dicionário com estatísticas dos jogadores de cada time
        """
        stats = {
            'home_players': [],
            'away_players': []
        }
        
        try:
            # Encontra as tabelas de estatísticas dos jogadores
            tables = soup.find_all('table', class_='miniscorebox')
            
            for table in tables:
                # Determina se é do time da casa ou visitante
                is_home = 'home' in table.get('id', '').lower()
                team_stats = 'home_players' if is_home else 'away_players'
                
                # Extrai as estatísticas dos jogadores
                rows = table.find_all('tr')
                for row in rows[1:]:  # Pula o cabeçalho
                    cols = row.find_all(['th', 'td'])
                    if not cols:
                        continue
                        
                    # Extrai dados básicos do jogador
                    player_name = cols[0].get_text(strip=True)
                    
                    # Extrai estatísticas avançadas
                    player_stats = {
                        'nome': player_name,
                        'minutos': cols[1].get_text(strip=True) if len(cols) > 1 else None,
                        'xg': self._parse_float(cols[10].get_text(strip=True)) if len(cols) > 10 else None,
                        'xa': self._parse_float(cols[11].get_text(strip=True)) if len(cols) > 11 else None,
                        'chutes': self._parse_int(cols[5].get_text(strip=True)) if len(cols) > 5 else None,
                        'chutes_no_gol': self._parse_int(cols[6].get_text(strip=True)) if len(cols) > 6 else None,
                        'passes_chave': self._parse_int(cols[7].get_text(strip=True)) if len(cols) > 7 else None,
                        'cruzamentos': self._parse_int(cols[8].get_text(strip=True)) if len(cols) > 8 else None,
                    }
                    
                    stats[team_stats].append(player_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao extrair estatísticas de jogadores: {e}")
            return stats
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Converte uma string para float, retornando None em caso de erro."""
        try:
            # Remove caracteres não numéricos, exceto ponto e sinal de menos
            cleaned = re.sub(r'[^\d.-]', '', value)
            return float(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Converte uma string para int, retornando None em caso de erro."""
        try:
            # Remove caracteres não numéricos
            cleaned = re.sub(r'[^\d-]', '', value)
            return int(cleaned) if cleaned else None
        except (ValueError, TypeError):
            return None
    
    async def get_advanced_match_stats(self, match_url: str) -> Dict:
        """
        Obtém todas as estatísticas avançadas de uma partida.
        
        Args:
            match_url: URL da partida no FBRef
            
        Returns:
            Dicionário com todas as estatísticas avançadas coletadas
        """
        soup = await self.get_match_report_page(match_url)
        if not soup:
            return {}
        
        # Extrai metadados da partida
        metadata = self.extract_match_metadata(soup)
        
        # Extrai estatísticas de xG/xA
        xg_stats = self.extract_expected_goals(soup)
        
        # Extrai estatísticas avançadas de jogadores
        player_stats = self.extract_player_advanced_stats(soup)
        
        # Combina todos os dados em um único dicionário
        return {
            'metadata': metadata,
            'expected_goals': {
                'xg_casa': xg_stats.get('xg_casa'),
                'xg_visitante': xg_stats.get('xg_visitante'),
                'xa_casa': xg_stats.get('xa_casa'),
                'xa_visitante': xg_stats.get('xa_visitante'),
            },
            'formacoes': {
                'casa': metadata.get('formacao_casa'),
                'visitante': metadata.get('formacao_visitante')
            },
            'jogadores': player_stats
        }
