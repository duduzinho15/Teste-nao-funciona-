import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote_plus

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'apostapro_db',
    'user': 'apostapro_user',
    'password': 'Canjica@@2025'
}

# Criar string de conexão para psycopg2
def get_connection_string():
    return f"""
        host='{DB_CONFIG['host']}' 
        port='{DB_CONFIG['port']}' 
        dbname='{DB_CONFIG['dbname']}' 
        user='{DB_CONFIG['user']}' 
        password='{DB_CONFIG['password']}'
        application_name='TesteConexao'
    """

# Testar conexão direta com psycopg2
print("🔍 Testando conexão direta com psycopg2...")
try:
    conn = psycopg2.connect(get_connection_string())
    print("✅ Conexão direta com psycopg2 bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"❌ Erro na conexão direta: {e}")

# Testar conexão com SQLAlchemy usando psycopg2
print("\n🔍 Testando conexão com SQLAlchemy...")
try:
    # Forçar o uso de psycopg2
    engine = create_engine(
        'postgresql+psycopg2://',
        creator=lambda: psycopg2.connect(get_connection_string()),
        pool_pre_ping=True
    )
    
    with engine.connect() as conn:
        print("✅ Conexão SQLAlchemy bem-sucedida!")
        result = conn.execute("SELECT version()")
        print(f" - PostgreSQL: {result.scalar()}")
        
        # Listar tabelas
        result = conn.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print("\n📋 Tabelas no banco de dados:")
        for row in result:
            print(f" - {row[0]}")
            
except Exception as e:
    print(f"❌ Erro na conexão SQLAlchemy: {e}")
    print("\n📌 Possíveis soluções:")
    print("1. Verifique se o PostgreSQL está rodando")
    print("2. Confirme se o usuário/senha estão corretos")
    print("3. Tente conectar manualmente: psql -h localhost -U apostapro_user -d apostapro_db")
    print("4. Verifique se o arquivo pg_hba.conf permite conexões locais")