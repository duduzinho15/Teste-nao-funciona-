"""
MÓDULO DATABASE - SISTEMA FBREF POSTGRESQL
==========================================

Módulo centralizado para acesso ao banco de dados PostgreSQL com SQLAlchemy.
Substitui as conexões SQLite diretas por ORM moderno e pool de conexões.

Componentes principais:
- config: Configuração centralizada e pool de conexões
- models: Modelos SQLAlchemy (ORM)
- Base, engine, SessionLocal: Aliases para compatibilidade

Uso básico:
    from Coleta_de_dados.database import SessionLocal, engine
    from Coleta_de_dados.database.models import Competicao, Partida
    
    # Usar sessão
    with SessionLocal() as session:
        competicoes = session.query(Competicao).all()

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

# Importar apenas configuração básica
from .config import (
    get_db_manager,
    get_db,
    init_database,
    SessionLocal
)

# Criar instância global do db_manager
db_manager = get_db_manager()

# Versão do módulo
__version__ = "1.0.0"

# Exports principais
__all__ = [
    # Configuração
    "get_db_manager",
    "get_db",
    "init_database",
    "SessionLocal",
    "db_manager",
]
