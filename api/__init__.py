"""
API FASTAPI DO APOSTAPRO
========================

Pacote da API RESTful construída com FastAPI para servir dados de futebol.
Integra com PostgreSQL via SQLAlchemy ORM e fornece endpoints seguros e documentados.

Módulos:
- main: Aplicativo principal FastAPI
- config: Configurações da API
- security: Sistema de autenticação e segurança
- schemas: Modelos Pydantic para validação
- routers: Endpoints organizados por domínio

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from .main import app, run_server
from .config import get_api_settings, api_settings
from .security import verify_api_key, get_current_api_key

__version__ = "1.0.0"
__author__ = "ApostaPro Team"
__description__ = "API RESTful para dados de futebol do ApostaPro"

# Exportar principais componentes
__all__ = [
    "app",
    "run_server", 
    "get_api_settings",
    "api_settings",
    "verify_api_key",
    "get_current_api_key"
]
