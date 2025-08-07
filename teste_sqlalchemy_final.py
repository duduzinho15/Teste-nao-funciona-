import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import psycopg2

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

def test_connection():
    # Testar conexão direta com psycopg2
    print("🔍 Testando conexão direta com psycopg2...")
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        print("✅ Conexão direta com psycopg2 bem-sucedida!")
        
        # Testar consulta direta
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(f" - PostgreSQL: {cur.fetchone()[0]}")
            
            # Listar tabelas
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            print("\n📋 Tabelas no banco de dados:")
            for row in cur.fetchall():
                print(f" - {row[0]}")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão direta: {e}")
        return False

def test_sqlalchemy():
    print("\n🔍 Testando conexão com SQLAlchemy...")
    try:
        # Criar engine SQLAlchemy
        engine = create_engine(
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}",
            pool_pre_ping=True
        )
        
        # Testar conexão
        with engine.connect() as conn:
            print("✅ Conexão SQLAlchemy bem-sucedida!")
            
            # Usar text() para executar SQL bruto
            result = conn.execute(text("SELECT version()"))
            print(f" - PostgreSQL: {result.scalar()}")
            
            # Listar tabelas
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            print("\n📋 Tabelas no banco de dados:")
            for row in result:
                print(f" - {row[0]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão SQLAlchemy: {e}")
        print("\n📌 Dica: Verifique se o SQLAlchemy está na versão correta:")
        print("pip install --upgrade sqlalchemy psycopg2-binary")
        return False

if __name__ == "__main__":
    print("🔧 Iniciando testes de conexão...")
    test_connection()
    test_sqlalchemy()
    
    print("\n📌 Se a conexão direta funcionou mas a do SQLAlchemy não, tente:")
    print("1. Atualizar o SQLAlchemy: pip install --upgrade sqlalchemy")
    print("2. Verificar se há múltiplas versões do Python instaladas")
    print("3. Executar em um ambiente virtual limpo")