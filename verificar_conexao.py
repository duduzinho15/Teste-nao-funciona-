import psycopg2
from psycopg2 import sql
import sys

def testar_conexao(host, port, user, password, database=None):
    """Testa a conexão com o banco de dados PostgreSQL"""
    try:
        conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password
        }
        
        if database:
            conn_params['database'] = database
            
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Testar versão do PostgreSQL
            cur.execute('SELECT version();')
            version = cur.fetchone()
            print(f"✅ Conectado ao PostgreSQL: {version[0]}")
            
            # Verificar se o banco de dados existe
            if database:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s", 
                    (database,)
                )
                if cur.fetchone():
                    print(f"✅ Banco de dados '{database}' existe")
                else:
                    print(f"❌ Banco de dados '{database}' não encontrado")
            
            # Verificar se o usuário existe
            cur.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = 'apostapro_user'"
            )
            if cur.fetchone():
                print("✅ Usuário 'apostapro_user' existe")
            else:
                print("❌ Usuário 'apostapro_user' não encontrado")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return False

def main():
    # Testar conexão com o banco de dados postgres
    print("\n🔍 Testando conexão com o PostgreSQL...")
    if not testar_conexao('localhost', '5432', 'postgres', '12345'):
        print("\n❌ Não foi possível conectar ao PostgreSQL. Verifique as credenciais e tente novamente.")
        sys.exit(1)
    
    # Testar conexão com o banco de dados apostapro_db
    print("\n🔍 Verificando banco de dados 'apostapro_db'...")
    if not testar_conexao('localhost', '5432', 'postgres', '12345', 'apostapro_db'):
        print("\n⚠️  O banco de dados 'apostapro_db' não existe ou não está acessível.")
        print("   Execute o script setup_database.sql para criar o banco de dados e o usuário.")
        sys.exit(1)
    
    print("\n✅ Todas as verificações foram concluídas com sucesso!")

if __name__ == "__main__":
    main()
