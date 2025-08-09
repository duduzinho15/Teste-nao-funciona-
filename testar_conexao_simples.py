import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def testar_conexao():
    print("Testando conexão com o banco de dados...")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Parâmetros de conexão
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    try:
        # Tenta conectar ao banco de dados
        print(f"Conectando a {conn_params['host']}:{conn_params['port']}...")
        conn = psycopg2.connect(**conn_params)
        print("Conexão bem-sucedida!")
        
        # Cria um cursor
        cur = conn.cursor()
        
        # Verifica se a tabela posts_redes_sociais existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'posts_redes_sociais'
            )
        """)
        
        posts_table_exists = cur.fetchone()[0]
        
        if posts_table_exists:
            print("\nA tabela 'posts_redes_sociais' EXISTE no banco de dados.")
            
            # Obtém informações sobre as colunas da tabela
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'posts_redes_sociais'
                ORDER BY ordinal_position
            """)
            
            print("\nEstrutura da tabela 'posts_redes_sociais':")
            for col in cur.fetchall():
                col_name, data_type, is_nullable, col_default = col
                print(f"  - {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}" + 
                      (f" DEFAULT {col_default}" if col_default else ""))
        else:
            print("\nA tabela 'posts_redes_sociais' NÃO existe no banco de dados.")
        
        # Fecha a conexão
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\nERRO ao conectar ao banco de dados: {e}")
        print("\nVerifique se:")
        print("1. O serviço PostgreSQL está em execução")
        print("2. As credenciais de acesso estão corretas")
        print("3. O banco de dados e o usuário existem")
        print("4. O usuário tem permissão para acessar o banco de dados")
        print("5. O firewall não está bloqueando a conexão")

if __name__ == "__main__":
    testar_conexao()
