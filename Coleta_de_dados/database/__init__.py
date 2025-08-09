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

from .config import (
    db_manager,
    engine,
    SessionLocal,
    Base,
    get_db,
    init_database
)

from .models import (
    # Modelos principais
    Competicao,
    LinkParaColeta,
    Partida,
    EstatisticaPartida,
    
    # Clubes
    PaisClube,
    Clube,
    EstatisticaClube,
    RecordVsOpponent,
    
    # Jogadores
    PaisJogador,
    Jogador,
    
    # Mixins
    TimestampMixin
)

# Versão do módulo
__version__ = "1.0.0"

# Exports principais
__all__ = [
    # Configuração
    "db_manager",
    "engine", 
    "SessionLocal",
    "Base",
    "get_db",
    "init_database",
    
    # Modelos
    "Competicao",
    "LinkParaColeta", 
    "Partida",
    "EstatisticaPartida",
    "PaisClube",
    "Clube",
    "EstatisticaClube",
    "RecordVsOpponent",
    "PaisJogador",
    "Jogador",
    "TimestampMixin",
]
