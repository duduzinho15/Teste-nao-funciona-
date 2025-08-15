#!/usr/bin/env python3
"""
Integração com APIs de casas de apostas para dados reais
"""
import logging
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import hashlib
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

logger = logging.getLogger(__name__)

@dataclass
class BettingOdds:
    """Dados de odds de uma casa de apostas"""
    bookmaker: str
    match_id: str
    home_team: str
    away_team: str
    competition: str
    match_date: str
    home_odds: float
    draw_odds: float
    away_odds: float
    over_25_odds: float
    under_25_odds: float
    both_teams_score_yes: float
    both_teams_score_no: float
    timestamp: datetime
    last_update: datetime

@dataclass
class MatchResult:
    """Resultado real de uma partida"""
    match_id: str
    home_team: str
    away_team: str
    competition: str
    match_date: str
    home_goals: int
    away_goals: int
    total_goals: int
    both_teams_score: bool
    result: str  # 'H', 'D', 'A'
    half_time_score: str
    full_time_score: str
    status: str  # 'finished', 'live', 'scheduled'
    timestamp: datetime

class BettingAPIIntegration:
    """Sistema de integração com APIs de casas de apostas"""
    
    def __init__(self):
        self.config = get_ml_config()
        
        # Diretórios
        self.data_dir = Path(self.config.data_dir)
        self.cache_dir = Path(self.config.cache_dir)
        
        # Configurações das APIs
        self.api_configs = {
            'football_data_org': {
                'base_url': 'https://api.football-data.org/v4',
                'api_key': self._get_api_key('FOOTBALL_DATA_API_KEY'),
                'rate_limit': 10,  # requests per minute
                'last_request_time': 0
            },
            'api_football': {
                'base_url': 'https://v3.football.api-sports.io',
                'api_key': self._get_api_key('API_FOOTBALL_KEY'),
                'rate_limit': 100,  # requests per day
                'last_request_time': 0
            },
            'odds_api': {
                'base_url': 'https://api.the-odds-api.com/v4',
                'api_key': self._get_api_key('ODDS_API_KEY'),
                'rate_limit': 500,  # requests per month
                'last_request_time': 0
            }
        }
        
        # Cache de dados
        self.odds_cache = {}
        self.results_cache = {}
        
        # Headers padrão
        self.default_headers = {
            'User-Agent': 'ApostaPro/1.0 (Machine Learning System)',
            'Accept': 'application/json'
        }
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """Obtém chave da API do ambiente ou arquivo de configuração"""
        import os
        from dotenv import load_dotenv
        
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Tentar obter do ambiente
        api_key = os.getenv(key_name)
        
        if api_key:
            return api_key
        
        # Tentar obter do arquivo de configuração
        config_file = Path('.env')
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(f'{key_name}='):
                        return line.split('=', 1)[1].strip()
        
        logger.warning(f"Chave da API {key_name} não encontrada")
        return None
    
    def _rate_limit_check(self, api_name: str) -> bool:
        """Verifica se pode fazer requisição respeitando rate limit"""
        config = self.api_configs.get(api_name)
        if not config:
            return False
        
        current_time = time.time()
        time_since_last = current_time - config['last_request_time']
        
        # Calcular intervalo mínimo entre requisições
        min_interval = 60 / config['rate_limit']  # segundos
        
        if time_since_last < min_interval:
            logger.info(f"Aguardando rate limit para {api_name}")
            time.sleep(min_interval - time_since_last)
        
        config['last_request_time'] = time.time()
        return True
    
    def _make_api_request(self, api_name: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para API respeitando rate limit"""
        try:
            if not self._rate_limit_check(api_name):
                return None
            
            config = self.api_configs[api_name]
            api_key = config['api_key']
            
            if not api_key:
                logger.error(f"Chave da API {api_name} não configurada")
                return None
            
            # Preparar headers
            headers = self.default_headers.copy()
            
            if api_name == 'football_data_org':
                headers['X-Auth-Token'] = api_key
            elif api_name == 'api_football':
                headers['x-rapidapi-key'] = api_key
                headers['x-rapidapi-host'] = 'v3.football.api-sports.io'
            
            # Fazer requisição
            url = f"{config['base_url']}{endpoint}"
            
            if api_name == 'odds_api':
                if params is None:
                    params = {}
                params['apiKey'] = api_key
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning(f"Rate limit atingido para {api_name}")
                return None
            else:
                logger.error(f"Erro na API {api_name}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao fazer requisição para {api_name}: {e}")
            return None
    
    @timed_cache_result(300)  # Cache por 5 minutos
    def get_live_matches(self, competition_id: str = None) -> List[Dict[str, Any]]:
        """
        Obtém partidas ao vivo
        
        Args:
            competition_id: ID da competição específica
            
        Returns:
            Lista de partidas ao vivo
        """
        try:
            logger.info("Obtendo partidas ao vivo")
            
            live_matches = []
            
            # Tentar Football Data API
            if self.api_configs['football_data_org']['api_key']:
                matches = self._get_live_matches_football_data(competition_id)
                if matches:
                    live_matches.extend(matches)
            
            # Tentar API Football
            if self.api_configs['api_football']['api_key']:
                matches = self._get_live_matches_api_football(competition_id)
                if matches:
                    live_matches.extend(matches)
            
            # Remover duplicatas
            unique_matches = self._remove_duplicate_matches(live_matches)
            
            logger.info(f"Encontradas {len(unique_matches)} partidas ao vivo")
            return unique_matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas ao vivo: {e}")
            return []
    
    def _get_live_matches_football_data(self, competition_id: str = None) -> List[Dict[str, Any]]:
        """Obtém partidas ao vivo da Football Data API"""
        try:
            endpoint = '/matches'
            params = {'status': 'LIVE'}
            
            if competition_id:
                endpoint = f'/competitions/{competition_id}/matches'
            
            data = self._make_api_request('football_data_org', endpoint, params)
            
            if not data or 'matches' not in data:
                return []
            
            matches = []
            for match in data['matches']:
                match_data = {
                    'match_id': str(match['id']),
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'competition': match.get('competition', {}).get('name', 'Unknown'),
                    'match_date': match['utcDate'],
                    'status': 'live',
                    'score': match.get('score', {}),
                    'api_source': 'football_data_org'
                }
                matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas ao vivo da Football Data: {e}")
            return []
    
    def _get_live_matches_api_football(self, competition_id: str = None) -> List[Dict[str, Any]]:
        """Obtém partidas ao vivo da API Football"""
        try:
            endpoint = '/fixtures'
            params = {'live': 'all'}
            
            if competition_id:
                params['league'] = competition_id
            
            data = self._make_api_request('api_football', endpoint, params)
            
            if not data or 'response' not in data:
                return []
            
            matches = []
            for fixture in data['response']:
                match_data = {
                    'match_id': str(fixture['fixture']['id']),
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'competition': fixture['league']['name'],
                    'match_date': fixture['fixture']['date'],
                    'status': 'live',
                    'score': fixture['goals'],
                    'api_source': 'api_football'
                }
                matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas ao vivo da API Football: {e}")
            return []
    
    @timed_cache_result(600)  # Cache por 10 minutos
    def get_match_odds(self, match_id: str, bookmaker: str = None) -> Optional[BettingOdds]:
        """
        Obtém odds para uma partida específica
        
        Args:
            match_id: ID da partida
            bookmaker: Casa de apostas específica
            
        Returns:
            Dados de odds ou None
        """
        try:
            logger.info(f"Obtendo odds para partida {match_id}")
            
            # Tentar Odds API
            if self.api_configs['odds_api']['api_key']:
                odds = self._get_odds_from_odds_api(match_id, bookmaker)
                if odds:
                    return odds
            
            # Tentar outras APIs
            if self.api_configs['football_data_org']['api_key']:
                odds = self._get_odds_from_football_data(match_id)
                if odds:
                    return odds
            
            logger.warning(f"Nenhuma odds encontrada para partida {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter odds para partida {match_id}: {e}")
            return None
    
    def _get_odds_from_odds_api(self, match_id: str, bookmaker: str = None) -> Optional[BettingOdds]:
        """Obtém odds da Odds API"""
        try:
            endpoint = '/sports/soccer/odds'
            params = {
                'regions': 'eu',
                'markets': 'h2h,totals,btts',
                'oddsFormat': 'decimal'
            }
            
            if bookmaker:
                params['bookmakers'] = bookmaker
            
            data = self._make_api_request('odds_api', endpoint, params)
            
            if not data:
                return None
            
            # Procurar pela partida específica
            for event in data:
                if str(event.get('id')) == match_id:
                    return self._parse_odds_api_event(event)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter odds da Odds API: {e}")
            return None
    
    def _get_odds_from_football_data(self, match_id: str) -> Optional[BettingOdds]:
        """Obtém odds da Football Data API"""
        try:
            endpoint = f'/matches/{match_id}'
            data = self._make_api_request('football_data_org', endpoint)
            
            if not data or 'odds' not in data:
                return None
            
            odds_data = data['odds']
            
            # Football Data API não fornece odds detalhadas gratuitamente
            # Retornar estrutura básica
            return BettingOdds(
                bookmaker='football_data_org',
                match_id=match_id,
                home_team=data['homeTeam']['name'],
                away_team=data['awayTeam']['name'],
                competition=data.get('competition', {}).get('name', 'Unknown'),
                match_date=data['utcDate'],
                home_odds=0.0,
                draw_odds=0.0,
                away_odds=0.0,
                over_25_odds=0.0,
                under_25_odds=0.0,
                both_teams_score_yes=0.0,
                both_teams_score_no=0.0,
                timestamp=datetime.now(),
                last_update=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter odds da Football Data: {e}")
            return None
    
    def _parse_odds_api_event(self, event: Dict[str, Any]) -> BettingOdds:
        """Converte evento da Odds API para BettingOdds"""
        try:
            # Obter odds do primeiro bookmaker disponível
            bookmakers = event.get('bookmakers', [])
            if not bookmakers:
                return None
            
            bookmaker_data = bookmakers[0]
            bookmaker_name = bookmaker_data['title']
            
            # Extrair odds
            odds = {
                'home': 0.0, 'draw': 0.0, 'away': 0.0,
                'over_25': 0.0, 'under_25': 0.0,
                'btts_yes': 0.0, 'btts_no': 0.0
            }
            
            for market in bookmaker_data['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Home':
                            odds['home'] = outcome['price']
                        elif outcome['name'] == 'Draw':
                            odds['draw'] = outcome['price']
                        elif outcome['name'] == 'Away':
                            odds['away'] = outcome['price']
                
                elif market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Over 2.5':
                            odds['over_25'] = outcome['price']
                        elif outcome['name'] == 'Under 2.5':
                            odds['under_25'] = outcome['price']
                
                elif market['key'] == 'btts':
                    for outcome in market['outcomes']:
                        if outcome['name'] == 'Yes':
                            odds['btts_yes'] = outcome['price']
                        elif outcome['name'] == 'No':
                            odds['btts_no'] = outcome['price']
            
            return BettingOdds(
                bookmaker=bookmaker_name,
                match_id=str(event['id']),
                home_team=event['home_team'],
                away_team=event['away_team'],
                competition=event.get('sport_title', 'Soccer'),
                match_date=event['commence_time'],
                home_odds=odds['home'],
                draw_odds=odds['draw'],
                away_odds=odds['away'],
                over_25_odds=odds['over_25'],
                under_25_odds=odds['under_25'],
                both_teams_score_yes=odds['btts_yes'],
                both_teams_score_no=odds['btts_no'],
                timestamp=datetime.now(),
                last_update=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse das odds: {e}")
            return None
    
    @timed_cache_result(1800)  # Cache por 30 minutos
    def get_competition_matches(self, competition_id: str, season: str = None) -> List[Dict[str, Any]]:
        """
        Obtém todas as partidas de uma competição
        
        Args:
            competition_id: ID da competição
            season: Temporada específica
            
        Returns:
            Lista de partidas
        """
        try:
            logger.info(f"Obtendo partidas da competição {competition_id}")
            
            matches = []
            
            # Tentar Football Data API
            if self.api_configs['football_data_org']['api_key']:
                comp_matches = self._get_competition_matches_football_data(competition_id, season)
                if comp_matches:
                    matches.extend(comp_matches)
            
            # Tentar API Football
            if self.api_configs['api_football']['api_key']:
                comp_matches = self._get_competition_matches_api_football(competition_id, season)
                if comp_matches:
                    matches.extend(comp_matches)
            
            # Remover duplicatas
            unique_matches = self._remove_duplicate_matches(matches)
            
            logger.info(f"Encontradas {len(unique_matches)} partidas na competição")
            return unique_matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas da competição: {e}")
            return []
    
    def _get_competition_matches_football_data(self, competition_id: str, season: str = None) -> List[Dict[str, Any]]:
        """Obtém partidas da competição da Football Data API"""
        try:
            endpoint = f'/competitions/{competition_id}/matches'
            params = {}
            
            if season:
                params['season'] = season
            
            data = self._make_api_request('football_data_org', endpoint, params)
            
            if not data or 'matches' not in data:
                return []
            
            matches = []
            for match in data['matches']:
                match_data = {
                    'match_id': str(match['id']),
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'competition': data.get('competition', {}).get('name', 'Unknown'),
                    'match_date': match['utcDate'],
                    'status': match['status'],
                    'score': match.get('score', {}),
                    'api_source': 'football_data_org'
                }
                matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas da Football Data: {e}")
            return []
    
    def _get_competition_matches_api_football(self, competition_id: str, season: str = None) -> List[Dict[str, Any]]:
        """Obtém partidas da competição da API Football"""
        try:
            endpoint = '/fixtures'
            params = {'league': competition_id}
            
            if season:
                params['season'] = season
            
            data = self._make_api_request('api_football', endpoint, params)
            
            if not data or 'response' not in data:
                return []
            
            matches = []
            for fixture in data['response']:
                match_data = {
                    'match_id': str(fixture['fixture']['id']),
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'competition': fixture['league']['name'],
                    'match_date': fixture['fixture']['date'],
                    'status': fixture['fixture']['status']['short'],
                    'score': fixture['goals'],
                    'api_source': 'api_football'
                }
                matches.append(match_data)
            
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao obter partidas da API Football: {e}")
            return []
    
    def get_match_result(self, match_id: str) -> Optional[MatchResult]:
        """
        Obtém resultado de uma partida
        
        Args:
            match_id: ID da partida
            
        Returns:
            Resultado da partida ou None
        """
        try:
            logger.info(f"Obtendo resultado da partida {match_id}")
            
            # Tentar Football Data API
            if self.api_configs['football_data_org']['api_key']:
                result = self._get_match_result_football_data(match_id)
                if result:
                    return result
            
            # Tentar API Football
            if self.api_configs['api_football']['api_key']:
                result = self._get_match_result_api_football(match_id)
                if result:
                    return result
            
            logger.warning(f"Resultado não encontrado para partida {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter resultado da partida {match_id}: {e}")
            return None
    
    def _get_match_result_football_data(self, match_id: str) -> Optional[MatchResult]:
        """Obtém resultado da partida da Football Data API"""
        try:
            endpoint = f'/matches/{match_id}'
            data = self._make_api_request('football_data_org', endpoint)
            
            if not data:
                return None
            
            score = data.get('score', {})
            home_goals = score.get('fullTime', {}).get('home', 0)
            away_goals = score.get('fullTime', {}).get('away', 0)
            
            if home_goals is None or away_goals is None:
                return None
            
            total_goals = home_goals + away_goals
            both_teams_score = home_goals > 0 and away_goals > 0
            
            # Determinar resultado
            if home_goals > away_goals:
                result = 'H'
            elif away_goals > home_goals:
                result = 'A'
            else:
                result = 'D'
            
            return MatchResult(
                match_id=str(data['id']),
                home_team=data['homeTeam']['name'],
                away_team=data['awayTeam']['name'],
                competition=data.get('competition', {}).get('name', 'Unknown'),
                match_date=data['utcDate'],
                home_goals=home_goals,
                away_goals=away_goals,
                total_goals=total_goals,
                both_teams_score=both_teams_score,
                result=result,
                half_time_score=f"{score.get('halfTime', {}).get('home', 0)}-{score.get('halfTime', {}).get('away', 0)}",
                full_time_score=f"{home_goals}-{away_goals}",
                status=data['status'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter resultado da Football Data: {e}")
            return None
    
    def _get_match_result_api_football(self, match_id: str) -> Optional[MatchResult]:
        """Obtém resultado da partida da API Football"""
        try:
            endpoint = f'/fixtures/id/{match_id}'
            data = self._make_api_request('api_football', endpoint)
            
            if not data or 'response' not in data or not data['response']:
                return None
            
            fixture = data['response'][0]
            goals = fixture.get('goals', {})
            
            home_goals = goals.get('home', 0)
            away_goals = goals.get('away', 0)
            
            if home_goals is None or away_goals is None:
                return None
            
            total_goals = home_goals + away_goals
            both_teams_score = home_goals > 0 and away_goals > 0
            
            # Determinar resultado
            if home_goals > away_goals:
                result = 'H'
            elif away_goals > home_goals:
                result = 'A'
            else:
                result = 'D'
            
            return MatchResult(
                match_id=str(fixture['fixture']['id']),
                home_team=fixture['teams']['home']['name'],
                away_team=fixture['teams']['away']['name'],
                competition=fixture['league']['name'],
                match_date=fixture['fixture']['date'],
                home_goals=home_goals,
                away_goals=away_goals,
                total_goals=total_goals,
                both_teams_score=both_teams_score,
                result=result,
                half_time_score=f"{goals.get('halftime', {}).get('home', 0)}-{goals.get('halftime', {}).get('away', 0)}",
                full_time_score=f"{home_goals}-{away_goals}",
                status=fixture['fixture']['status']['short'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao obter resultado da API Football: {e}")
            return None
    
    def _remove_duplicate_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove partidas duplicadas baseado no ID"""
        seen_ids = set()
        unique_matches = []
        
        for match in matches:
            match_id = match.get('match_id')
            if match_id and match_id not in seen_ids:
                seen_ids.add(match_id)
                unique_matches.append(match)
        
        return unique_matches
    
    def get_market_analysis(self, competition_id: str = None) -> Dict[str, Any]:
        """
        Obtém análise de mercado para uma competição
        
        Args:
            competition_id: ID da competição
            
        Returns:
            Análise de mercado
        """
        try:
            logger.info("Obtendo análise de mercado")
            
            # Obter partidas recentes
            if competition_id:
                matches = self.get_competition_matches(competition_id)
            else:
                # Usar competições populares
                matches = []
                popular_competitions = ['PL', 'BL1', 'SA', 'PD', 'FL1']  # Premier League, Bundesliga, etc.
                
                for comp_id in popular_competitions:
                    comp_matches = self.get_competition_matches(comp_id)
                    matches.extend(comp_matches)
            
            if not matches:
                return {'error': 'Nenhuma partida encontrada para análise'}
            
            # Analisar odds e resultados
            analysis = {
                'total_matches': len(matches),
                'competition_analysis': {},
                'market_trends': {},
                'value_betting_opportunities': []
            }
            
            # Agrupar por competição
            competitions = {}
            for match in matches:
                comp_name = match.get('competition', 'Unknown')
                if comp_name not in competitions:
                    competitions[comp_name] = []
                competitions[comp_name].append(match)
            
            # Analisar cada competição
            for comp_name, comp_matches in competitions.items():
                comp_analysis = self._analyze_competition_market(comp_matches)
                analysis['competition_analysis'][comp_name] = comp_analysis
            
            # Identificar oportunidades de value betting
            analysis['value_betting_opportunities'] = self._identify_value_betting_opportunities(matches)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao obter análise de mercado: {e}")
            return {'error': str(e)}
    
    def _analyze_competition_market(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa mercado de uma competição específica"""
        try:
            analysis = {
                'total_matches': len(matches),
                'home_win_rate': 0.0,
                'away_win_rate': 0.0,
                'draw_rate': 0.0,
                'avg_goals_per_match': 0.0,
                'both_teams_score_rate': 0.0,
                'market_efficiency': 'Unknown'
            }
            
            if not matches:
                return analysis
            
            # Calcular estatísticas
            home_wins = 0
            away_wins = 0
            draws = 0
            total_goals = 0
            btts_count = 0
            
            for match in matches:
                # Tentar obter resultado
                match_id = match.get('match_id')
                if match_id:
                    result = self.get_match_result(match_id)
                    if result:
                        if result.result == 'H':
                            home_wins += 1
                        elif result.result == 'A':
                            away_wins += 1
                        else:
                            draws += 1
                        
                        total_goals += result.total_goals
                        if result.both_teams_score:
                            btts_count += 1
            
            total_analyzed = home_wins + away_wins + draws
            
            if total_analyzed > 0:
                analysis['home_win_rate'] = home_wins / total_analyzed
                analysis['away_win_rate'] = away_wins / total_analyzed
                analysis['draw_rate'] = draws / total_analyzed
                analysis['avg_goals_per_match'] = total_goals / total_analyzed
                analysis['both_teams_score_rate'] = btts_count / total_analyzed
            
            # Determinar eficiência do mercado
            if analysis['home_win_rate'] > 0.5:
                analysis['market_efficiency'] = 'Home Bias'
            elif analysis['away_win_rate'] > 0.4:
                analysis['market_efficiency'] = 'Away Bias'
            else:
                analysis['market_efficiency'] = 'Balanced'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar mercado da competição: {e}")
            return {'error': str(e)}
    
    def _identify_value_betting_opportunities(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de value betting"""
        opportunities = []
        
        try:
            for match in matches:
                match_id = match.get('match_id')
                if not match_id:
                    continue
                
                # Obter odds
                odds = self.get_match_odds(match_id)
                if not odds:
                    continue
                
                # Obter resultado
                result = self.get_match_result(match_id)
                if not result:
                    continue
                
                # Calcular probabilidades implícitas
                home_prob = 1 / odds.home_odds if odds.home_odds > 0 else 0
                away_prob = 1 / odds.away_odds if odds.away_odds > 0 else 0
                draw_prob = 1 / odds.draw_odds if odds.draw_odds > 0 else 0
                
                # Normalizar
                total_prob = home_prob + away_prob + draw_prob
                if total_prob > 0:
                    home_prob_norm = home_prob / total_prob
                    away_prob_norm = away_prob / total_prob
                    draw_prob_norm = draw_prob / total_prob
                    
                    # Identificar value bets
                    if result.result == 'H' and home_prob_norm > 0.4 and odds.home_odds > 2.0:
                        opportunities.append({
                            'match': f"{match['home_team']} vs {match['away_team']}",
                            'bet_type': 'Home Win',
                            'odds': odds.home_odds,
                            'implied_probability': home_prob_norm,
                            'actual_result': 'Home Win',
                            'value_score': home_prob_norm - (1/odds.home_odds)
                        })
                    
                    if result.result == 'A' and away_prob_norm > 0.35 and odds.away_odds > 2.5:
                        opportunities.append({
                            'match': f"{match['home_team']} vs {match['away_team']}",
                            'bet_type': 'Away Win',
                            'odds': odds.away_odds,
                            'implied_probability': away_prob_norm,
                            'actual_result': 'Away Win',
                            'value_score': away_prob_norm - (1/odds.away_odds)
                        })
            
            # Ordenar por score de valor
            opportunities.sort(key=lambda x: x['value_score'], reverse=True)
            
            return opportunities[:10]  # Top 10 oportunidades
            
        except Exception as e:
            logger.error(f"Erro ao identificar oportunidades de value betting: {e}")
            return []
    
    def save_data_to_database(self, data: Union[List[BettingOdds], List[MatchResult]], data_type: str):
        """
        Salva dados no banco de dados
        
        Args:
            data: Dados para salvar
            data_type: Tipo de dados ('odds' ou 'results')
        """
        try:
            logger.info(f"Salvando {len(data)} registros de {data_type}")
            
            # Converter para DataFrame
            if data_type == 'odds':
                df = pd.DataFrame([vars(odds) for odds in data])
            elif data_type == 'results':
                df = pd.DataFrame([vars(result) for result in data])
            else:
                logger.error(f"Tipo de dados inválido: {data_type}")
                return
            
            # Salvar em arquivo CSV
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{data_type}_{timestamp}.csv"
            filepath = self.data_dir / filename
            
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Dados salvos em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")

# Instância global
betting_api_integration = BettingAPIIntegration()

# Funções de conveniência
def get_live_matches(**kwargs) -> List[Dict[str, Any]]:
    """Obtém partidas ao vivo"""
    return betting_api_integration.get_live_matches(**kwargs)

def get_match_odds(**kwargs) -> Optional[BettingOdds]:
    """Obtém odds de uma partida"""
    return betting_api_integration.get_match_odds(**kwargs)

def get_competition_matches(**kwargs) -> List[Dict[str, Any]]:
    """Obtém partidas de uma competição"""
    return betting_api_integration.get_competition_matches(**kwargs)

def get_match_result(**kwargs) -> Optional[MatchResult]:
    """Obtém resultado de uma partida"""
    return betting_api_integration.get_match_result(**kwargs)

def get_market_analysis(**kwargs) -> Dict[str, Any]:
    """Obtém análise de mercado"""
    return betting_api_integration.get_market_analysis(**kwargs)
