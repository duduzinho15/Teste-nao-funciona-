#!/usr/bin/env python3
"""
Script para verificar a estrutura do banco de dados PostgreSQL.
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
}

# String de conexão
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def get_table_info(engine, table_name):
    """Obtém informações detalhadas sobre uma tabela específica."""
    inspector = inspect(engine)
    
    # Verifica se a tabela existe
    if not inspector.has_table(table_name):
        return None
    
    # Obtém as colunas
    columns = inspector.get_columns(table_name)
    
    # Obtém as chaves primárias
    pk_constraint = inspector.get_pk_constraint(table_name)
    
    # Obtém as chaves estrangeiras
    fk_constraints = inspector.get_foreign_keys(table_name)
    
    # Obtém os índices
    indexes = inspector.get_indexes(table_name)
    
    return {
        'exists': True,
        'columns': [{'name': col['name'], 'type': str(col['type']), 'nullable': col['nullable']} for col in columns],
        'primary_key': pk_constraint.get('constrained_columns', []),
        'foreign_keys': [{'columns': fk['constrained_columns'], 'referred_table': fk['referred_table']} for fk in fk_constraints],
        'indexes': [{'name': idx['name'], 'columns': idx['column_names'], 'unique': idx.get('unique', False)} for idx in indexes]
    }

def check_database_structure():
    """Verifica a estrutura do banco de dados."""
    try:
        # Cria a conexão com o banco de dados
        engine = create_engine(DATABASE_URL)
        
        # Lista todas as tabelas no banco de dados
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        print(f"📊 Tabelas encontradas no banco de dados ({len(all_tables)}):")
        for table in sorted(all_tables):
            print(f"- {table}")
        
        # Verifica tabelas específicas de interesse
        tables_to_check = [
            'alembic_version',  # Tabela do Alembic
            'clubes',
            'posts_redes_sociais',
            'jogadores',
            'noticias_clubes'
        ]
        
        print("\n🔍 Verificando tabelas específicas:")
        for table in tables_to_check:
            info = get_table_info(engine, table)
            if info is None:
                print(f"❌ Tabela '{table}' não existe no banco de dados.")
            else:
                print(f"✅ Tabela '{table}' encontrada com {len(info['columns'])} colunas.")
        
        # Verifica a versão do Alembic
        if 'alembic_version' in all_tables:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version;"))
                version = result.scalar()
                print(f"\n🔧 Versão do Alembic: {version}")
        else:
            print("\n⚠️ Tabela 'alembic_version' não encontrada. O Alembic pode não estar configurado corretamente.")
        
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    print("🔍 Verificando estrutura do banco de dados...")
    check_database_structure()
