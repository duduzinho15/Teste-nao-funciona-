"""
Módulo de APIs Externas para Coleta de Dados Esportivos
========================================================

Este módulo contém integrações com APIs externas para coleta de dados esportivos,
incluindo estatísticas, odds, informações de clubes, jogadores e ligas.

APIs Disponíveis:
- API-Football (api-sports.io)
- Football-Data.org
- TheSportsDB
- StatsBomb
- SofaScore (scraping)
- FlashScore (scraping)
- RapidAPI (múltiplas APIs)

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-01-15
Versão: 2.0
"""

from .api_football import APIFootballCollector
from .football_data_org import FootballDataOrgCollector
from .thesportsdb_api import TheSportsDBCollector
from .statsbomb_api import StatsBombCollector
from .sofascore_scraper import SofaScoreCollector
from .flashscore_scraper import FlashScoreCollector
from .rapidapi_collector import RapidAPICollector

__all__ = [
    'APIFootballCollector',
    'FootballDataOrgCollector', 
    'TheSportsDBCollector',
    'StatsBombCollector',
    'SofaScoreCollector',
    'FlashScoreCollector',
    'RapidAPICollector'
]

__version__ = '2.0.0'
