"""
Script para testar a conexão com o banco de dados PostgreSQL e verificar problemas de codificação.
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def test_connection():
    """Testa a conexão com o banco de dados e verifica a codificação."""
    try:
        # Tenta conectar usando as credenciais do .env
        conn = psycopg2.connect(
            dbname='apostapro_db',
            user='postgres',
            password='postgres',
            host='localhost',
            port=5432,
            client_encoding='utf8'  # Força a codificação UTF-8
        )
        
        # Define o nível de isolamento
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Cria um cursor
        with conn.cursor() as cur:
            # Verifica a versão do PostgreSQL
            cur.execute('SELECT version()')
            version = cur.fetchone()[0]
            print(f"✅ Conexão bem-sucedida com o PostgreSQL: {version}")
            
            # Verifica a codificação do banco de dados
            cur.execute("SHOW server_encoding;")
            encoding = cur.fetchone()[0]
            print(f"🔤 Codificação do servidor: {encoding}")
            
            # Verifica a codificação do cliente
            cur.execute("SHOW client_encoding;")
            client_encoding = cur.fetchone()[0]
            print(f"🔡 Codificação do cliente: {client_encoding}")
            
            # Lista os bancos de dados existentes
            print("\n📊 Bancos de dados disponíveis:")
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            for db in cur.fetchall():
                print(f"- {db[0]}")
            
            # Verifica as tabelas no banco de dados atual
            print("\n📋 Tabelas no banco de dados 'apostapro_db':")
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            for table in cur.fetchall():
                print(f"- {table[0]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        print(f"Tipo de erro: {type(e).__name__}")
        if hasattr(e, 'pgcode'):
            print(f"Código de erro PostgreSQL: {e.pgcode}")
        if hasattr(e, 'pgerror') and e.pgerror:
            print(f"Mensagem de erro PostgreSQL: {e.pgerror}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Testando conexão com o banco de dados PostgreSQL...")
    success = test_connection()
    sys.exit(0 if success else 1)
