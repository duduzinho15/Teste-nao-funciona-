"""
INICIALIZAÇÃO DO BANCO DE DADOS
===============================

Script para criar todas as tabelas no banco de dados PostgreSQL com base nos modelos SQLAlchemy.

Uso:
    python init_db.py
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa os modelos para garantir que todas as tabelas sejam criadas
from Coleta_de_dados.database.models import Base
from Coleta_de_dados.database.config import DatabaseSettings

def init_database():
    """Inicializa o banco de dados e cria todas as tabelas."""
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Obtém as configurações do banco de dados
    settings = DatabaseSettings()
    
    # Cria a URL de conexão
    db_url = settings.database_url or f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    print(f"🔍 Conectando ao banco de dados: {db_url.replace(settings.db_password, '***')}")
    
    # Cria o engine do SQLAlchemy
    engine = create_engine(db_url)
    
    # Verifica se o banco de dados existe, se não existir, cria
    if not database_exists(engine.url):
        print("ℹ️  Banco de dados não encontrado. Criando...")
        create_database(engine.url)
        print("✅ Banco de dados criado com sucesso!")
    
    # Cria todas as tabelas
    print("🔄 Criando tabelas...")
    Base.metadata.create_all(engine)
    print("✅ Tabelas criadas com sucesso!")
    
    # Lista as tabelas criadas
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        
        """))
        tables = [row[0] for row in result]
        
        print("\n📋 Tabelas criadas:")
        for table in sorted(tables):
            print(f"  - {table}")
    
    print("\n✨ Inicialização do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    init_database()
