"""
Script para verificar permissões e acessos do banco de dados PostgreSQL.
"""
import os
import psycopg2
from psycopg2 import sql
import sys
from dotenv import load_dotenv

def test_connection(conn_params):
    """Testa a conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(**conn_params)
        print("✅ Conexão bem-sucedida!")
        
        with conn.cursor() as cur:
            # Obtém informações do servidor
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"\n📊 Versão do PostgreSQL: {version}")
            
            # Obtém informações do banco de dados atual
            cur.execute("""
                SELECT 
                    current_database() AS database,
                    current_user AS user,
                    inet_server_addr() AS server_address,
                    inet_server_port() AS server_port,
                    pg_encoding_to_char(encoding) AS encoding,
                    datcollate,
                    datctype
                FROM pg_database 
                WHERE datname = current_database();
            """)
            
            db_info = cur.fetchone()
            print("\n🔍 Informações do banco de dados:")
            print(f"   Nome: {db_info[0]}")
            print(f"   Usuário: {db_info[1]}")
            print(f"   Endereço do servidor: {db_info[2]}")
            print(f"   Porta do servidor: {db_info[3]}")
            print(f"   Codificação: {db_info[4]}")
            print(f"   Collation: {db_info[5]}")
            print(f"   Character Type: {db_info[6]}")
            
            # Verifica permissões do usuário
            cur.execute("""
                SELECT 
                    rolname,
                    rolsuper,
                    rolinherit,
                    rolcreaterole,
                    rolcreatedb,
                    rolcanlogin
                FROM pg_roles 
                WHERE rolname = current_user;
            """)
            
            role_info = cur.fetchone()
            print("\n👤 Permissões do usuário:")
            print(f"   Nome: {role_info[0]}")
            print(f"   Superusuário: {'Sim' if role_info[1] else 'Não'}")
            print(f"   Pode herdar: {'Sim' if role_info[2] else 'Não'}")
            print(f"   Pode criar roles: {'Sim' if role_info[3] else 'Não'}")
            print(f"   Pode criar bancos: {'Sim' if role_info[4] else 'Não'}")
            print(f"   Pode fazer login: {'Sim' if role_info[5] else 'Não'}")
            
            # Lista as extensões instaladas
            cur.execute("SELECT * FROM pg_extension;")
            extensions = cur.fetchall()
            
            print("\n🔌 Extensões instaladas:")
            for ext in extensions:
                print(f"- {ext[0]} (versão: {ext[2] if ext[2] else 'N/A'})")
            
            # Verifica se o usuário pode criar bancos de dados
            cur.execute("SELECT has_database_privilege(current_user, 'CREATE');")
            can_create_db = cur.fetchone()[0]
            print(f"\n🔧 Pode criar bancos de dados: {'Sim' if can_create_db else 'Não'}")
            
            # Lista os bancos de dados existentes
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            dbs = [db[0] for db in cur.fetchall()]
            
            print("\n📚 Bancos de dados disponíveis:")
            for db in dbs:
                print(f"- {db}")
            
            return True
            
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações de conexão
    conn_params = {
        'dbname': os.getenv('DB_NAME', 'postgres'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'connect_timeout': 5
    }
    
    print("🔍 Verificando acesso ao banco de dados...")
    print(f"   Host: {conn_params['host']}")
    print(f"   Porta: {conn_params['port']}")
    print(f"   Banco: {conn_params['dbname']}")
    print(f"   Usuário: {conn_params['user']}")
    
    # Testa a conexão
    if not test_connection(conn_params):
        print("\n❌ Falha ao conectar ao banco de dados. Verifique as credenciais e tente novamente.")
        sys.exit(1)
    
    print("\n✅ Verificação concluída com sucesso!")

if __name__ == "__main__":
    main()
