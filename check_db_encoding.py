"""
Script para verificar a codificação do banco de dados PostgreSQL.
"""
import psycopg2
from psycopg2 import sql
import sys

def check_encoding():
    """Verifica a codificação do banco de dados PostgreSQL."""
    try:
        # Conecta ao banco de dados postgres (banco padrão)
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port=5432,
            client_encoding='UTF8'  # Força a codificação UTF-8 para a conexão
        )
        
        # Cria um cursor
        with conn.cursor() as cur:
            # Verifica a versão do PostgreSQL
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL: {version}")
            
            # Verifica a codificação do servidor
            cur.execute("SHOW server_encoding;")
            server_encoding = cur.fetchone()[0]
            print(f"🔤 Codificação do servidor: {server_encoding}")
            
            # Verifica a codificação do cliente
            cur.execute("SHOW client_encoding;")
            client_encoding = cur.fetchone()[0]
            print(f"🔡 Codificação do cliente: {client_encoding}")
            
            # Lista os bancos de dados e suas codificações
            print("\n📊 Bancos de dados e suas codificações:")
            cur.execute("""
                SELECT datname, 
                       pg_encoding_to_char(encoding) AS encoding,
                       datcollate,
                       datctype
                FROM pg_database 
                WHERE datistemplate = false;
            """)
            
            # Exibe os resultados em formato de tabela
            print(f"{'Nome do banco':<20} {'Codificação':<15} {'Collation':<20} {'Character Type':<20}")
            print("-" * 80)
            for db in cur.fetchall():
                print(f"{db[0]:<20} {db[1]:<15} {db[2]:<20} {db[3]:<20}")
            
            # Verifica se o banco de dados apostapro_db existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro_db';")
            if cur.fetchone():
                print("\n🔍 Verificando a codificação do banco apostapro_db...")
                
                # Tenta conectar ao banco de dados apostapro_db
                conn_db = psycopg2.connect(
                    dbname='apostapro_db',
                    user='postgres',
                    password='postgres',
                    host='localhost',
                    port=5432,
                    client_encoding='UTF8'
                )
                
                with conn_db.cursor() as cur_db:
                    # Verifica a codificação do banco de dados
                    cur_db.execute("SELECT current_database(), pg_encoding_to_char(encoding) FROM pg_database WHERE datname = current_database();")
                    db_info = cur_db.fetchone()
                    print(f"✅ Banco de dados: {db_info[0]}, Codificação: {db_info[1]}")
                    
                    # Verifica algumas tabelas e suas codificações
                    cur_db.execute("""
                        SELECT table_name, 
                               pg_encoding_to_char(encoding) AS encoding
                        FROM pg_tables t
                        JOIN pg_database d ON d.datname = current_database()
                        WHERE t.schemaname = 'public';
                    """)
                    
                    print("\n📋 Tabelas no banco de dados:")
                    for table in cur_db.fetchall():
                        print(f"- {table[0]} (Codificação: {table[1] if table[1] else 'Padrão'})")
                
                conn_db.close()
            else:
                print("\n❌ O banco de dados 'apostapro_db' não foi encontrado.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar a codificação do banco de dados: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Verificando a codificação do banco de dados PostgreSQL...")
    if not check_encoding():
        sys.exit(1)
