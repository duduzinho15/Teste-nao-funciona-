"""
VERIFICAÇÃO DA TABELA ALEMBIC_VERSION
=====================================

Script para verificar se a tabela alembic_version existe no banco de dados.
"""

import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa as configurações do banco de dados
from Coleta_de_dados.database.config import DatabaseSettings

def check_alembic_version():
    """Verifica se a tabela alembic_version existe no banco de dados."""
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Obtém as configurações do banco de dados
    settings = DatabaseSettings()
    
    # Cria a URL de conexão
    db_url = settings.database_url or f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    print(f"🔍 Conectando ao banco de dados: {db_url.replace(settings.db_password, '***')}")
    
    try:
        # Cria o engine do SQLAlchemy
        engine = create_engine(db_url)
        
        # Verifica se a tabela alembic_version existe
        with engine.connect() as conn:
            # Verifica se a tabela existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
            """))
            
            exists = result.scalar()
            
            if exists:
                print("✅ A tabela 'alembic_version' EXISTE no banco de dados.")
                
                # Se existir, mostra o conteúdo
                result = conn.execute(text("SELECT * FROM alembic_version"))
                version = result.first()
                if version:
                    print(f"📋 Versão atual do Alembic: {version[0]}")
                else:
                    print("ℹ️  A tabela 'alembic_version' está vazia.")
            else:
                print("❌ A tabela 'alembic_version' NÃO EXISTE no banco de dados.")
                
                # Verifica se há migrações pendentes
                print("\n🔍 Verificando migrações pendentes...")
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """))
                
                tables = [row[0] for row in result]
                print(f"\n📋 Tabelas existentes no banco de dados ({len(tables)}):")
                for table in sorted(tables):
                    print(f"  - {table}")
                
                print("\nℹ️  Para sincronizar o Alembic com o estado atual do banco de dados, execute:")
                print("   1. Crie uma migração vazia: `alembic revision -m 'Initial migration'`")
                print("   2. Marque como aplicada: `alembic stamp head`")
                
    except Exception as e:
        print(f"❌ Erro ao verificar a tabela 'alembic_version': {e}")

if __name__ == "__main__":
    check_alembic_version()
