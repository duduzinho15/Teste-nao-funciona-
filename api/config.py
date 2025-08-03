"""
CONFIGURAÇÃO DA API FASTAPI
===========================

Configurações centralizadas para a API RESTful do ApostaPro.
Integra com o sistema de configuração existente e adiciona configurações específicas da API.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from pydantic import BaseSettings, Field
from typing import Optional
import os
from pathlib import Path

class APISettings(BaseSettings):
    """Configurações da API FastAPI."""
    
    # Informações da API
    api_title: str = Field(default="ApostaPro API", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_description: str = Field(default="API RESTful para dados de futebol do ApostaPro", env="API_DESCRIPTION")
    
    # Servidor
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Segurança
    api_key: str = Field(default="apostapro-api-key-change-in-production", env="API_KEY")
    secret_key: str = Field(default="your-secret-key-for-jwt-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    api_rate_limit: int = Field(default=100, env="API_RATE_LIMIT")
    api_rate_limit_period: int = Field(default=60, env="API_RATE_LIMIT_PERIOD")
    
    # Configurações gerais
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

# Instância global das configurações
api_settings = APISettings()

# Configurações de documentação
DOCS_CONFIG = {
    "title": api_settings.api_title,
    "description": f"""
## {api_settings.api_description}

### 🚀 Funcionalidades:
- **Competições**: Consultar competições esportivas
- **Clubes**: Informações de clubes e estatísticas  
- **Jogadores**: Dados de jogadores e performance
- **Partidas**: Resultados e estatísticas de partidas

### 🔐 Autenticação:
Esta API utiliza autenticação por **API Key**. Inclua o header:
```
X-API-Key: sua-api-key-aqui
```

### 📊 Rate Limiting:
- **Limite**: {api_settings.api_rate_limit} requests por {api_settings.api_rate_limit_period} segundos
- **Recomendação**: Implemente cache local para otimizar uso

### 🔗 Endpoints Principais:
- `/api/v1/competitions/` - Listar competições
- `/api/v1/clubs/` - Listar clubes  
- `/api/v1/players/` - Listar jogadores
- `/api/v1/matches/` - Consultar partidas

### 📝 Versioning:
Esta é a **versão {api_settings.api_version}** da API. Todas as rotas estão sob `/api/v1/`.
    """,
    "version": api_settings.api_version,
    "contact": {
        "name": "ApostaPro Team",
        "email": "api@apostapro.com",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "tags_metadata": [
        {
            "name": "competitions",
            "description": "Operações relacionadas a competições esportivas",
        },
        {
            "name": "clubs", 
            "description": "Informações de clubes e estatísticas",
        },
        {
            "name": "players",
            "description": "Dados de jogadores e performance",
        },
        {
            "name": "matches",
            "description": "Resultados e estatísticas de partidas",
        },
        {
            "name": "health",
            "description": "Endpoints de saúde e status da API",
        },
    ]
}

# Configurações de middleware
MIDDLEWARE_CONFIG = {
    "cors": {
        "allow_origins": api_settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": api_settings.cors_methods,
        "allow_headers": api_settings.cors_headers,
    },
    "rate_limit": {
        "times": api_settings.api_rate_limit,
        "seconds": api_settings.api_rate_limit_period,
    }
}

def get_api_settings() -> APISettings:
    """Retorna as configurações da API."""
    return api_settings
