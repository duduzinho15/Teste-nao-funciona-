#!/usr/bin/env python3
"""
Configuração das APIs de casas de apostas para integração com dados reais
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class APIConfig:
    """Configuração de uma API específica"""
    name: str
    base_url: str
    api_key: str
    rate_limit: int  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    enabled: bool = True

class BettingAPIsConfig:
    """Configuração centralizada para todas as APIs de apostas"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        # Configurações das principais APIs
        self.apis = {
            'football_data_org': APIConfig(
                name='Football Data Org',
                base_url='https://api.football-data.org/v4',
                api_key=self._get_env_var('FOOTBALL_DATA_API_KEY'),
                rate_limit=10,
                timeout=30
            ),
            
            'api_football': APIConfig(
                name='API Football',
                base_url='https://v3.football.api-sports.io',
                api_key=self._get_env_var('API_FOOTBALL_KEY'),
                rate_limit=100,
                timeout=45
            ),
            
            'odds_api': APIConfig(
                name='The Odds API',
                base_url='https://api.the-odds-api.com/v4',
                api_key=self._get_env_var('ODDS_API_KEY'),
                rate_limit=500,
                timeout=30
            ),
            
            'betfair': APIConfig(
                name='Betfair',
                base_url='https://api.betfair.com/exchange/betting/json/rpc/v1',
                api_key=self._get_env_var('BETFAIR_API_KEY'),
                rate_limit=50,
                timeout=60
            ),
            
            'pinnacle': APIConfig(
                name='Pinnacle Sports',
                base_url='https://api.pinnacle.com/0.1',
                api_key=self._get_env_var('PINNACLE_API_KEY'),
                rate_limit=20,
                timeout=30
            ),
            
            'william_hill': APIConfig(
                name='William Hill',
                base_url='https://api.williamhill.com/v1',
                api_key=self._get_env_var('WILLIAM_HILL_API_KEY'),
                rate_limit=30,
                timeout=45
            )
        }
        
        # Configurações de competições principais
        self.competitions = {
            'premier_league': {
                'id': 'PL',
                'name': 'Premier League',
                'country': 'England',
                'priority': 'high',
                'apis': ['football_data_org', 'api_football', 'odds_api']
            },
            'la_liga': {
                'id': 'PD',
                'name': 'La Liga',
                'country': 'Spain',
                'priority': 'high',
                'apis': ['football_data_org', 'api_football', 'odds_api']
            },
            'bundesliga': {
                'id': 'BL1',
                'name': 'Bundesliga',
                'country': 'Germany',
                'priority': 'high',
                'apis': ['football_data_org', 'api_football', 'odds_api']
            },
            'serie_a': {
                'id': 'SA',
                'name': 'Serie A',
                'country': 'Italy',
                'priority': 'high',
                'apis': ['football_data_org', 'api_football', 'odds_api']
            },
            'brasileirao': {
                'id': 'BSA',
                'name': 'Brasileirão',
                'country': 'Brazil',
                'priority': 'high',
                'apis': ['api_football', 'odds_api']
            },
            'champions_league': {
                'id': 'CL',
                'name': 'UEFA Champions League',
                'country': 'Europe',
                'priority': 'high',
                'apis': ['football_data_org', 'api_football', 'odds_api']
            }
        }
        
        # Configurações de tipos de apostas
        self.betting_types = {
            'match_winner': {
                'name': 'Vencedor da Partida',
                'markets': ['1', 'X', '2'],
                'priority': 'high'
            },
            'over_under': {
                'name': 'Mais/Menos Gols',
                'markets': ['Over 0.5', 'Over 1.5', 'Over 2.5', 'Under 2.5', 'Under 1.5'],
                'priority': 'high'
            },
            'both_teams_score': {
                'name': 'Ambas Equipes Marcam',
                'markets': ['Yes', 'No'],
                'priority': 'medium'
            },
            'double_chance': {
                'name': 'Dupla Chance',
                'markets': ['1X', '12', 'X2'],
                'priority': 'medium'
            },
            'correct_score': {
                'name': 'Placar Exato',
                'markets': ['1-0', '2-0', '2-1', '1-1', '0-0', '0-1', '1-2', '0-2'],
                'priority': 'low'
            }
        }
        
        # Configurações de coleta de dados
        self.data_collection = {
            'real_time_odds_interval': 300,  # 5 minutos
            'historical_data_days': 365,      # 1 ano
            'odds_history_days': 30,         # 30 dias
            'max_concurrent_requests': 5,
            'cache_duration': 1800,         # 30 minutos
            'retry_delay': 60               # 1 minuto
        }
        
        # Configurações de validação
        self.validation = {
            'min_odds_value': 1.01,
            'max_odds_value': 1000.0,
            'min_market_count': 3,
            'required_fields': ['home_team', 'away_team', 'match_date', 'odds'],
            'data_freshness_hours': 24
        }
    
    def _get_env_var(self, var_name: str) -> str:
        """Obtém variável de ambiente ou retorna valor padrão"""
        return os.getenv(var_name, f'your_{var_name.lower()}_here')
    
    def get_api_config(self, api_name: str) -> APIConfig:
        """Obtém configuração de uma API específica"""
        return self.apis.get(api_name)
    
    def get_enabled_apis(self) -> Dict[str, APIConfig]:
        """Obtém apenas as APIs habilitadas"""
        return {name: config for name, config in self.apis.items() if config.enabled}
    
    def get_competition_apis(self, competition_id: str) -> list:
        """Obtém APIs disponíveis para uma competição específica"""
        competition = self.competitions.get(competition_id)
        if competition:
            return [api for api in competition['apis'] if self.apis[api].enabled]
        return []
    
    def update_api_status(self, api_name: str, status: bool):
        """Atualiza status de uma API"""
        if api_name in self.apis:
            self.apis[api_name].enabled = status
    
    def get_rate_limit_info(self) -> Dict[str, Dict[str, Any]]:
        """Obtém informações sobre rate limits das APIs"""
        return {
            name: {
                'rate_limit': config.rate_limit,
                'enabled': config.enabled,
                'timeout': config.timeout
            }
            for name, config in self.apis.items()
        }
    
    def save_config(self):
        """Salva configuração em arquivo JSON"""
        import json
        
        config_data = {
            'apis': {name: {
                'name': config.name,
                'base_url': config.base_url,
                'rate_limit': config.rate_limit,
                'timeout': config.timeout,
                'enabled': config.enabled
            } for name, config in self.apis.items()},
            'competitions': self.competitions,
            'betting_types': self.betting_types,
            'data_collection': self.data_collection,
            'validation': self.validation
        }
        
        config_file = self.config_dir / "betting_apis_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """Carrega configuração de arquivo JSON"""
        import json
        
        config_file = self.config_dir / "betting_apis_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Atualizar configurações
                if 'apis' in config_data:
                    for name, api_data in config_data['apis'].items():
                        if name in self.apis:
                            for key, value in api_data.items():
                                if hasattr(self.apis[name], key):
                                    setattr(self.apis[name], key, value)
                
                logger.info("✅ Configuração carregada com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar configuração: {e}")

# Configuração global
betting_apis_config = BettingAPIsConfig()

if __name__ == "__main__":
    # Salvar configuração padrão
    betting_apis_config.save_config()
    print("✅ Configuração das APIs de apostas salva!")
