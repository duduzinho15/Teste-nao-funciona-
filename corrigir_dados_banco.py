import psycopg2
from psycopg2 import sql, errors
import sys

def get_db_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="postgres",  # Conectar ao banco 'postgres' primeiro
            user="postgres",
            password="postgres",
            client_encoding="UTF8"
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)

def verificar_banco_dados(conn):
    """Verifica se o banco de dados existe e obtém informações"""
    try:
        with conn.cursor() as cur:
            # Verificar se o banco de dados existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro_db'")
            if not cur.fetchone():
                print("❌ O banco de dados 'apostapro_db' não existe.")
                return False
                
            # Obter informações do banco de dados
            cur.execute("""
                SELECT datname, pg_encoding_to_char(encoding), datcollate, datctype 
                FROM pg_database 
                WHERE datname = 'apostapro_db'
            """)
            db_info = cur.fetchone()
            
            if db_info:
                print(f"\n📊 Informações do banco de dados 'apostapro_db':")
                print(f" - Nome: {db_info[0]}")
                print(f" - Encoding: {db_info[1]}")
                print(f" - Collation: {db_info[2]}")
                print(f" - Ctype: {db_info[3]}")
                return True
            else:
                print("❌ Não foi possível obter informações do banco de dados.")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")
        return False

def listar_tabelas(conn):
    """Lista todas as tabelas no banco de dados"""
    try:
        # Conectar ao banco de dados apostapro_db
        conn_db = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="apostapro_db",
            user="postgres",
            password="postgres"
        )
        conn_db.autocommit = True
        
        with conn_db.cursor() as cur:
            # Listar tabelas
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tabelas = [row[0] for row in cur.fetchall()]
            
            if tabelas:
                print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
                for tabela in tabelas:
                    print(f" - {tabela}")
                return tabelas
            else:
                print("ℹ️  Nenhuma tabela encontrada no banco de dados.")
                return []
                
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []
    finally:
        if 'conn_db' in locals():
            conn_db.close()

def corrigir_banco():
    """Tenta corrigir problemas no banco de dados"""
    print("🔍 Iniciando diagnóstico e correção do banco de dados...")
    
    # Conectar ao banco de dados 'postgres'
    conn = get_db_connection()
    
    try:
        # Verificar informações do banco de dados
        if not verificar_banco_dados(conn):
            print("\n❌ Não foi possível continuar com a correção.")
            return False
        
        # Listar tabelas
        tabelas = listar_tabelas(conn)
        
        if not tabelas:
            print("\nℹ️  Nenhuma tabela para verificar. O banco de dados está vazio.")
            return True
            
        print("\n🔧 Tentando corrigir problemas de encoding...")
        
        # 1. Tentar corrigir o encoding do banco de dados
        try:
            with conn.cursor() as cur:
                # Forçar terminação de conexões ao banco
                print("🔌 Encerrando conexões ativas...")
                cur.execute("""
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE datname = 'apostapro_db' AND pid <> pg_backend_pid();
                """)
                
                # Recriar o banco de dados com encoding correto
                print("🔄 Recriando banco de dados com encoding correto...")
                cur.execute("""
                    DROP DATABASE IF EXISTS apostapro_db;
                    CREATE DATABASE apostapro_db 
                    WITH 
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'Portuguese_Brazil.1252'
                    LC_CTYPE = 'Portuguese_Brazil.1252'
                    TEMPLATE = template0;
                """)
                print("✅ Banco de dados recriado com sucesso!")
                
        except Exception as e:
            print(f"❌ Erro ao recriar o banco de dados: {e}")
            return False
            
        print("\n✅ Processo de correção concluído.")
        print("\n📌 Próximos passos:")
        print("1. Execute as migrações do Alembic para recriar as tabelas:")
        print("   alembic upgrade head")
        print("2. Importe os dados de volta para o banco")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o processo de correção: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    print("🛠️  Ferramenta de Diagnóstico e Correção de Banco de Dados")
    print("=" * 70)
    
    if corrigir_banco():
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Ocorreram erros durante o processo de correção.")
    
    input("\nPressione Enter para sair...")
