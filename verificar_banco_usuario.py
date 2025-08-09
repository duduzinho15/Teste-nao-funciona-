import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def verificar_banco_usuario():
    print("=== Verificação de Banco de Dados e Usuário PostgreSQL ===")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão (conecta ao banco 'postgres' padrão)
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': 'postgres',  # Conecta ao banco padrão
        'user': 'postgres',      # Usuário padrão do PostgreSQL
        'password': 'postgres'   # Senha padrão (altere conforme necessário)
    }
    
    try:
        # Tenta conectar ao banco de dados 'postgres'
        print(f"Conectando ao banco de dados 'postgres' em {db_config['host']}:{db_config['port']}...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Verifica se o banco de dados existe
            db_name = os.getenv('DB_NAME', 'apostapro_db')
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            db_exists = cur.fetchone() is not None
            
            print(f"\nBanco de dados '{db_name}': {'EXISTE' if db_exists else 'NÃO EXISTE'}")
            
            # Verifica se o usuário existe
            db_user = os.getenv('DB_USER', 'apostapro_user')
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            user_exists = cur.fetchone() is not None
            
            print(f"Usuário '{db_user}': {'EXISTE' if user_exists else 'NÃO EXISTE'}")
            
            # Se o banco de dados existe, verifica as permissões do usuário
            if db_exists and user_exists:
                try:
                    # Tenta conectar ao banco de dados específico com o usuário
                    db_config_test = {
                        'host': db_config['host'],
                        'port': db_config['port'],
                        'database': db_name,
                        'user': db_user,
                        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
                    }
                    
                    conn_test = psycopg2.connect(**db_config_test)
                    print(f"\n✅ Conexão bem-sucedida com o banco de dados '{db_name}' usando o usuário '{db_user}'")
                    
                    # Verifica as permissões do usuário no banco de dados
                    with conn_test.cursor() as cur_test:
                        # Verifica se o usuário tem permissão para criar tabelas
                        cur_test.execute("""
                            SELECT has_schema_privilege(%s, 'public', 'CREATE');
                        """, (db_user,))
                        can_create = cur_test.fetchone()[0]
                        
                        print(f"\nPermissões do usuário '{db_user}' no banco '{db_name}':")
                        print(f"- Pode criar tabelas no esquema público: {'SIM' if can_create else 'NÃO'}")
                        
                        # Lista as tabelas existentes
                        cur_test.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            ORDER BY table_name;
                        """)
                        
                        tabelas = cur_test.fetchall()
                        
                        if not tabelas:
                            print("\nNenhuma tabela encontrada no esquema público.")
                        else:
                            print("\nTabelas no esquema público:")
                            for tabela in tabelas:
                                print(f"- {tabela[0]}")
                    
                    conn_test.close()
                    
                except Exception as e:
                    print(f"\n❌ Falha ao conectar ao banco de dados '{db_name}' com o usuário '{db_user}': {e}")
                    print("\nPossíveis causas:")
                    print("1. A senha do usuário pode estar incorreta")
                    print("2. O usuário não tem permissão para acessar o banco de dados")
                    print(f"3. O banco de dados '{db_name}' pode estar em um estado inconsistente")
                    print(f"\nDetalhes do erro: {str(e)}")
            
            # Se o banco de dados não existe, sugere criá-lo
            if not db_exists:
                print("\n⚠️  O banco de dados não existe. Você pode criá-lo com o comando:")
                print(f"    createdb -h {db_config['host']} -p {db_config['port']} -U postgres {db_name}")
            
            # Se o usuário não existe, sugere criá-lo
            if not user_exists:
                print("\n⚠️  O usuário não existe. Você pode criá-lo com o comando:")
                print(f"    psql -h {db_config['host']} -p {db_config['port']} -U postgres -c \"CREATE USER {db_user} WITH PASSWORD 'sua_senha_segura';\"")
                print(f"    psql -h {db_config['host']} -p {db_config['port']} -U postgres -c \"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};\"")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar o banco de dados e o usuário: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. As credenciais de administrador (usuário 'postgres') estão corretas")
        print("3. O PostgreSQL está configurado para aceitar conexões TCP/IP")
        print(f"\nDetalhes do erro: {str(e)}")

if __name__ == "__main__":
    verificar_banco_usuario()
