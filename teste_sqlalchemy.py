import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações de conexão
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'dbname': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'Canjica@@2025')
}

# URL de conexão para SQLAlchemy
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

try:
    # Criar engine com configurações explícitas
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            "application_name": "TesteConexao"
        }
    )
    
    # Testar conexão
    with engine.connect() as conn:
        print("✅ Conexão SQLAlchemy bem-sucedida!")
        print("📊 Executando consulta de teste...")
        
        # Testar consulta simples
        result = conn.execute("SELECT version()")
        print(f" - PostgreSQL: {result.scalar()}")
        
        # Verificar tabelas
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print("\n📋 Tabelas no banco de dados:")
        for row in result:
            print(f" - {row[0]}")
            
    print("\n✅ Tudo funcionando perfeitamente!")
    
except Exception as e:
    print(f"❌ Erro na conexão SQLAlchemy: {e}")