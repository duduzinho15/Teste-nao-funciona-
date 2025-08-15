"""
CONFIGURAÇÃO CENTRALIZADA DOS SCRAPERS
======================================

Arquivo de configuração para todos os scrapers usando Playwright.
Centraliza configurações de rate limiting, timeouts, seletores e URLs.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import os
from typing import Dict, List, Any
from pathlib import Path

class ScraperConfig:
    """Configuração centralizada para todos os scrapers."""
    
    # Configurações gerais do Playwright
    PLAYWRIGHT_CONFIG = {
        "browser_type": "chromium",  # chromium, firefox, webkit
        "headless": True,  # False para debug
        "viewport": {"width": 1920, "height": 1080},
        "timeout": 60000,  # 60 segundos
        "screenshot_dir": "screenshots",
        "enable_video": False,
        "enable_har": True,
        "max_retries": 3,
        "retry_delay": 2
    }
    
    # User agents para rotação
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    # Configurações específicas do FBRef
    FBREF_CONFIG = {
        "base_url": "https://fbref.com",
        "rate_limit_delay": 2.0,  # Delay entre requisições
        "max_pages_per_session": 50,
        "selectors": {
            "competition_link": "a[href*='/en/comps/']",
            "club_link": "a[href*='/en/squad/']",
            "player_link": "a[href*='/en/players/']",
            "match_link": "a[href*='/en/matches/']",
            "stats_table": "table.stats_table",
            "pagination": ".pagination",
            "next_page": "a[aria-label='Next page']",
            "loading": ".loading, .spinner",
            "error": ".error, .alert"
        },
        "competitions": [
            "https://fbref.com/en/comps/9/Premier-League-Stats",
            "https://fbref.com/en/comps/12/La-Liga-Stats",
            "https://fbref.com/en/comps/13/Ligue-1-Stats",
            "https://fbref.com/en/comps/20/Bundesliga-Stats",
            "https://fbref.com/en/comps/24/Serie-A-Stats",
            "https://fbref.com/en/comps/32/Primeira-Liga-Stats",
            "https://fbref.com/en/comps/33/Eredivisie-Stats",
            "https://fbref.com/en/comps/8/Champions-League-Stats",
            "https://fbref.com/en/comps/19/Europa-League-Stats",
            "https://fbref.com/en/comps/882/Conference-League-Stats"
        ]
    }
    
    # Configurações específicas do SofaScore
    SOFASCORE_CONFIG = {
        "base_url": "https://www.sofascore.com",
        "rate_limit_delay": 3.0,  # Mais conservador
        "max_pages_per_session": 30,
        "selectors": {
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
        },
        "teams": [
            "https://www.sofascore.com/team/manchester-united/17",
            "https://www.sofascore.com/team/liverpool/44",
            "https://www.sofascore.com/team/arsenal/35",
            "https://www.sofascore.com/team/chelsea/38",
            "https://www.sofascore.com/team/manchester-city/17",
            "https://www.sofascore.com/team/real-madrid/2817",
            "https://www.sofascore.com/team/barcelona/2817",
            "https://www.sofascore.com/team/atletico-madrid/2817",
            "https://www.sofascore.com/team/bayern-munich/35",
            "https://www.sofascore.com/team/borussia-dortmund/35"
        ],
        "tournaments": [
            "https://www.sofascore.com/tournament/england-premier-league/7",
            "https://www.sofascore.com/tournament/spain-la-liga/8",
            "https://www.sofascore.com/tournament/france-ligue-1/9",
            "https://www.sofascore.com/tournament/germany-bundesliga/35",
            "https://www.sofascore.com/tournament/italy-serie-a/23",
            "https://www.sofascore.com/tournament/uefa-champions-league/52",
            "https://www.sofascore.com/tournament/uefa-europa-league/53"
        ]
    }
    
    # Configurações específicas do FlashScore
    FLASHSCORE_CONFIG = {
        "base_url": "https://www.flashscore.com",
        "rate_limit_delay": 2.5,
        "max_pages_per_session": 40,
        "selectors": {
            "match_link": "a[href*='/match/']",
            "team_link": "a[href*='/team/']",
            "tournament_link": "a[href*='/tournament/']",
            "score": ".event__score",
            "time": ".event__time",
            "stats": ".stat__row",
            "odds": ".odds__row",
            "loading": ".loading, .spinner",
            "error": ".error, .alert"
        },
        "tournaments": [
            "https://www.flashscore.com/football/england/premier-league/",
            "https://www.flashscore.com/football/spain/la-liga/",
            "https://www.flashscore.com/football/france/ligue-1/",
            "https://www.flashscore.com/football/germany/bundesliga/",
            "https://www.flashscore.com/football/italy/serie-a/"
        ]
    }
    
    # Configurações específicas do WhoScored
    WHOSCORED_CONFIG = {
        "base_url": "https://www.whoscored.com",
        "rate_limit_delay": 3.0,
        "max_pages_per_session": 25,
        "selectors": {
            "match_link": "a[href*='/Matches/']",
            "team_link": "a[href*='/Teams/']",
            "player_link": "a[href*='/Players/']",
            "tournament_link": "a[href*='/Regions/']",
            "score": ".score",
            "time": ".time",
            "stats": ".stat",
            "loading": ".loading, .spinner",
            "error": ".error, .alert"
        },
        "regions": [
            "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League",
            "https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga",
            "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1",
            "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga",
            "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
        ]
    }
    
    # Configurações de rate limiting global
    RATE_LIMITING = {
        "global_delay": 1.0,  # Delay mínimo entre todas as requisições
        "max_requests_per_minute": 30,
        "max_requests_per_hour": 1000,
        "backoff_factor": 2.0,  # Fator de backoff exponencial
        "max_retries": 5
    }
    
    # Configurações de proxy (opcional)
    PROXY_CONFIG = {
        "enabled": False,
        "proxies": [
            # Adicionar proxies aqui se necessário
        ],
        "rotation": True,
        "timeout": 30
    }
    
    # Configurações de cache
    CACHE_CONFIG = {
        "enabled": True,
        "cache_dir": "cache",
        "max_cache_size": "1GB",
        "cache_ttl": 3600,  # 1 hora
        "compression": True
    }
    
    # Configurações de logging
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/scrapers.log",
        "max_file_size": "10MB",
        "backup_count": 5
    }
    
    # Configurações de monitoramento
    MONITORING_CONFIG = {
        "enabled": True,
        "metrics_interval": 60,  # segundos
        "alert_threshold": 0.8,  # 80% de falha
        "health_check_url": "https://httpbin.org/status/200",
        "notification_channels": ["email", "slack"]  # Implementar depois
    }
    
    @classmethod
    def get_playwright_config(cls, **overrides) -> Dict[str, Any]:
        """Retorna configuração do Playwright com overrides opcionais."""
        config = cls.PLAYWRIGHT_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_fbref_config(cls, **overrides) -> Dict[str, Any]:
        """Retorna configuração do FBRef com overrides opcionais."""
        config = cls.FBREF_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_sofascore_config(cls, **overrides) -> Dict[str, Any]:
        """Retorna configuração do SofaScore com overrides opcionais."""
        config = cls.SOFASCORE_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_flashscore_config(cls, **overrides) -> Dict[str, Any]:
        """Retorna configuração do FlashScore com overrides opcionais."""
        config = cls.FLASHSCORE_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_whoscored_config(cls, **overrides) -> Dict[str, Any]:
        """Retorna configuração do WhoScored com overrides opcionais."""
        config = cls.WHOSCORED_CONFIG.copy()
        config.update(overrides)
        return config
    
    @classmethod
    def get_user_agent(cls) -> str:
        """Retorna um user agent aleatório para rotação."""
        import random
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def create_directories(cls):
        """Cria diretórios necessários para os scrapers."""
        directories = [
            cls.PLAYWRIGHT_CONFIG["screenshot_dir"],
            cls.CACHE_CONFIG["cache_dir"],
            Path(cls.LOGGING_CONFIG["file"]).parent
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida se todas as configurações estão corretas."""
        try:
            # Validar URLs
            for config_name, config in [
                ("FBRef", cls.FBREF_CONFIG),
                ("SofaScore", cls.SOFASCORE_CONFIG),
                ("FlashScore", cls.FLASHSCORE_CONFIG),
                ("WhoScored", cls.WHOSCORED_CONFIG)
            ]:
                if not config["base_url"].startswith("https://"):
                    print(f"❌ {config_name}: URL base deve usar HTTPS")
                    return False
            
            # Validar timeouts
            if cls.PLAYWRIGHT_CONFIG["timeout"] < 1000:
                print("❌ Timeout muito baixo")
                return False
            
            # Validar delays
            if cls.RATE_LIMITING["global_delay"] < 0:
                print("❌ Delay global não pode ser negativo")
                return False
            
            print("✅ Todas as configurações estão válidas")
            return True
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False

# Configurações específicas para desenvolvimento
DEV_CONFIG = {
    "headless": False,  # Mostrar navegador para debug
    "timeout": 30000,   # Timeout menor para desenvolvimento
    "enable_video": True,  # Gravar vídeo para debug
    "screenshot_dir": "screenshots/dev"
}

# Configurações específicas para produção
PROD_CONFIG = {
    "headless": True,   # Executar em background
    "timeout": 120000,  # Timeout maior para estabilidade
    "enable_video": False,  # Não gravar vídeo em produção
    "screenshot_dir": "screenshots/prod"
}

# Função para obter configuração baseada no ambiente
def get_config_for_environment(environment: str = "dev") -> Dict[str, Any]:
    """
    Retorna configuração baseada no ambiente.
    
    Args:
        environment: 'dev' ou 'prod'
    
    Returns:
        Configuração do Playwright para o ambiente
    """
    if environment.lower() == "prod":
        return ScraperConfig.get_playwright_config(**PROD_CONFIG)
    else:
        return ScraperConfig.get_playwright_config(**DEV_CONFIG)

if __name__ == "__main__":
    # Validar configurações
    print("🔧 Validando configurações dos scrapers...")
    ScraperConfig.validate_config()
    
    # Criar diretórios
    print("📁 Criando diretórios necessários...")
    ScraperConfig.create_directories()
    
    # Mostrar configurações
    print("\n📋 Configurações disponíveis:")
    print(f"🎭 Playwright: {len(ScraperConfig.PLAYWRIGHT_CONFIG)} opções")
    print(f"🏆 FBRef: {len(ScraperConfig.FBREF_CONFIG['competitions'])} competições")
    print(f"⚽ SofaScore: {len(ScraperConfig.SOFASCORE_CONFIG['teams'])} times")
    print(f"📊 FlashScore: {len(ScraperConfig.FLASHSCORE_CONFIG['tournaments'])} torneios")
    print(f"📈 WhoScored: {len(ScraperConfig.WHOSCORED_CONFIG['regions'])} regiões")
    
    print("\n✅ Configuração dos scrapers carregada com sucesso!")
