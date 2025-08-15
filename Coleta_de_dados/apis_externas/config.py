# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO CENTRALIZADA PARA APIS EXTERNAS E SCRAPING
=======================================================

Este arquivo centraliza todas as configurações para:
- APIs externas (RapidAPI, etc.)
- Sistemas de scraping
- Configurações de banco de dados
- Chaves de API e credenciais

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-08-14
Versão: 2.0
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class APIConfig:
    """Configuração para uma API específica"""
    nome: str
    host: str
    endpoint: str
    chave: str
    limite_diario: int
    limite_minuto: int
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1


@dataclass
class ScrapingConfig:
    """Configuração para sistemas de scraping"""
    nome: str
    tipo: str  # 'playwright', 'selenium', 'requests', 'beautifulsoup'
    url_base: str
    user_agent: str
    delay_min: float
    delay_max: float
    max_retries: int = 3


class APIsConfig:
    """Configuração centralizada para todas as APIs externas"""
    
    def __init__(self):
        # Chave principal do RapidAPI
        self.rapidapi_key = os.getenv(
            "RAPIDAPI_KEY", 
            "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6"
        )
        
        # Configuração das APIs RapidAPI
        rapidapi = {
            "today_football_prediction": {
                "nome": "Today Football Prediction",
                "host": "today-football-prediction.p.rapidapi.com",
                "endpoint": "/leagues/",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "soccer_football_info": {
                "nome": "Soccer Football Info",
                "host": "soccer-football-info.p.rapidapi.com",
                "endpoint": "/emulation/totalcorner/match/schedule/",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "sportspage_feeds": {
                "nome": "Sportspage Feeds",
                "host": "sportspage-feeds.p.rapidapi.com",
                "endpoint": "/rankings",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "football_prediction": {
                "nome": "Football Prediction",
                "host": "football-prediction-api.p.rapidapi.com",  # Corrigido baseado no playground
                "endpoint": "/api/v2/predictions",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "pinnacle_odds": {
                "nome": "Pinnacle Odds",
                "host": "pinnacle-odds-api.p.rapidapi.com",  # Corrigido baseado no playground
                "endpoint": "/pinnacle/health-check",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "football_pro": {
                "nome": "Football Pro",
                "host": "football-pro.p.rapidapi.com",
                "endpoint": "/api/v2.0/corrections/season/17141",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            },
            "sportapi7": {
                "nome": "SportAPI7",
                "host": "sportapi7.p.rapidapi.com",
                "endpoint": "/api/v1/player/817181/unique-tournament/132/season/65360/ratings",  # Corrigido baseado no playground
                "chave": "76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6",
                "limite_requisicoes_dia": 1000,
                "limite_requisicoes_minuto": 60
            }
        }
        
        # Configurações de scraping
        self.scraping = {
            "fbref": ScrapingConfig(
                nome="FBRef",
                tipo="playwright",
                url_base="https://fbref.com",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                delay_min=2.0,
                delay_max=5.0
            ),
            
            "sofascore": ScrapingConfig(
                nome="SofaScore",
                tipo="playwright",
                url_base="https://www.sofascore.com",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                delay_min=1.0,
                delay_max=3.0
            ),
            
            "social_media": ScrapingConfig(
                nome="Social Media",
                tipo="playwright",
                url_base="https://twitter.com",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                delay_min=3.0,
                delay_max=7.0
            ),
            
            "news": ScrapingConfig(
                nome="News",
                tipo="playwright",
                url_base="https://ge.globo.com",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                delay_min=2.0,
                delay_max=4.0
            )
        }
        
        # Configurações de banco de dados
        self.database = {
            "postgresql": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "apostapro"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", ""),
                "sslmode": os.getenv("DB_SSLMODE", "prefer")
            },
            "sqlite": {
                "database": os.getenv("SQLITE_DB", "apostapro.db"),
                "timeout": 30
            }
        }
        
        # Configurações de cache
        self.cache = {
            "enabled": True,
            "ttl": 3600,  # 1 hora
            "max_size": 1000,
            "directory": "cache"
        }
        
        # Configurações de logs
        self.logging = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/coleta.log",
            "max_size": 10 * 1024 * 1024,  # 10MB
            "backup_count": 5
        }
    
    def get_api_config(self, api_name: str) -> APIConfig:
        """Retorna configuração de uma API específica"""
        return self.rapidapi.get(api_name)
    
    def get_scraping_config(self, scraper_name: str) -> ScrapingConfig:
        """Retorna configuração de um scraper específico"""
        return self.scraping.get(scraper_name)
    
    def get_all_apis(self) -> List[str]:
        """Retorna lista de todas as APIs disponíveis"""
        return list(self.rapidapi.keys())
    
    def get_all_scrapers(self) -> List[str]:
        """Retorna lista de todos os scrapers disponíveis"""
        return list(self.scraping.keys())
    
    def validate_config(self) -> Dict[str, Any]:
        """Valida todas as configurações e retorna status"""
        status = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validar chaves de API
        for api_name, config in self.rapidapi.items():
            if not config.chave:
                status["errors"].append(f"API {api_name}: Chave não configurada")
                status["valid"] = False
            elif len(config.chave) < 20:
                status["warnings"].append(f"API {api_name}: Chave parece ser muito curta")
        
        # Validar configurações de scraping
        for scraper_name, config in self.scraping.items():
            if not config.url_base.startswith(("http://", "https://")):
                status["errors"].append(f"Scraper {scraper_name}: URL base inválida")
                status["valid"] = False
        
        return status


# Instância global da configuração
apis_config = APIsConfig()


def get_config() -> APIsConfig:
    """Retorna a instância global da configuração"""
    return apis_config


def reload_config():
    """Recarrega as configurações do arquivo"""
    global apis_config
    apis_config = APIsConfig()


if __name__ == "__main__":
    # Teste da configuração
    config = get_config()
    print("🔧 CONFIGURAÇÃO DE APIS EXTERNAS")
    print("=" * 50)
    
    print(f"📊 Total de APIs RapidAPI: {len(config.get_all_apis())}")
    print(f"🕷️  Total de Scrapers: {len(config.get_all_scrapers())}")
    
    # Validar configuração
    validation = config.validate_config()
    print(f"\n✅ Configuração válida: {validation['valid']}")
    
    if validation["errors"]:
        print("\n❌ Erros encontrados:")
        for error in validation["errors"]:
            print(f"  - {error}")
    
    if validation["warnings"]:
        print("\n⚠️  Avisos:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    print("\n🚀 Sistema configurado e pronto para uso!")
