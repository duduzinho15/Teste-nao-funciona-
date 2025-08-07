"""
MÓDULO DE BANCO DE DADOS - API FASTAPI
======================================

Módulo para gerenciar conexões com o banco de dados PostgreSQL.
Fornece uma função de dependência para obter sessões do banco de dados.

Autor: Sistema de API RESTful
Data: 2025-08-06
Versão: 1.0
"""

from typing import Generator
from sqlalchemy.orm import Session
from Coleta_de_dados.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Fornece uma sessão do banco de dados para cada requisição.
    
    Uso:
        from .database import get_db
        
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
