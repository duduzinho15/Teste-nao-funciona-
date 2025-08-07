import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from dotenv import load_dotenv
import psycopg2

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'apostapro_db',
    'username': 'apostapro_user',
    'password': 'Canjica@@2025',
    'drivername': 'postgresql+psycopg2'
}

def test_sqlalchemy_tcp():
    print("\n🔍 Testando conexão com SQLAlchemy via TCP...")
    try:
        # Criar URL de conexão manualmente
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=DB_CONFIG['username'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database']
        )
        
        # Forçar TCP/IP
        url = url._replace(
            query={"client_encoding": "utf8", "connect_timeout": "10"}
        )
        
        # Criar engine
        engine = create_engine(
            url,
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        )
        
        # Testar conexão
        with engine.connect() as conn:
            print("✅ Conexão SQLAlchemy via TCP bem-sucedida!")
            
            # Usar text() para executar SQL bruto
            result = conn.execute(text("SELECT version()"))
            print(f" - PostgreSQL: {result.scalar()}")
            
            # Listar tabelas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            
            print("\n📋 Tabelas no banco de dados:")
            for row in result:
                print(f" - {row[0]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão SQLAlchemy: {e}")
        print("\n📌 Vamos tentar uma abordagem alternativa...")
        return test_alternative_approach()

def test_alternative_approach():
    print("\n🔄 Tentando abordagem alternativa...")
    try:
        # Usar psycopg2 diretamente com SQLAlchemy
        from sqlalchemy.engine import create_engine
        from sqlalchemy import text
        
        # Usar string de conexão direta
        conn_str = (
            f"postgresql+psycopg2://{DB_CONFIG['username']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            "?client_encoding=utf8&connect_timeout=10"
        )
        
        engine = create_engine(conn_str)
        
        with engine.connect() as conn:
            print("✅ Conexão alternativa bem-sucedida!")
            result = conn.execute(text("SELECT version()"))
            print(f" - PostgreSQL: {result.scalar()}")
            return True
            
    except Exception as e:
        print(f"❌ Falha na abordagem alternativa: {e}")
        print("\n📌 Possíveis soluções:")
        print("1. Verificar se o PostgreSQL está configurado para aceitar conexões TCP/IP")
        print("2. Verificar o arquivo pg_hba.conf para garantir que as conexões locais são permitidas")
        print("3. Tentar reiniciar o serviço do PostgreSQL")
        return False

if __name__ == "__main__":
    test_sqlalchemy_tcp()
