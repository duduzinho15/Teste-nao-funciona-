import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

def verificar_tabela_postgres():
    print("=== Verificando Tabela no PostgreSQL ===")
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    try:
        # Conecta ao banco de dados
        print(f"Conectando ao banco de dados {db_config['database']}...")
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Verifica se a tabela posts_redes_sociais existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'posts_redes_sociais'
                );
            """)
            
            tabela_existe = cur.fetchone()[0]
            print(f"Tabela 'posts_redes_sociais' existe: {'SIM' if tabela_existe else 'NÃO'}")
            
            if tabela_existe:
                # Obtém a estrutura da tabela
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'posts_redes_sociais'
                    ORDER BY ordinal_position;
                """)
                
                print("\nEstrutura da tabela 'posts_redes_sociais':")
                for coluna in cur.fetchall():
                    print(f"- {coluna[0]} ({coluna[1]}) {'NULL' if coluna[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {coluna[3]}' if coluna[3] else ''}")
            
            # Lista todas as tabelas no esquema público
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            
            print("\nTabelas no esquema público:")
            for tabela in cur.fetchall():
                print(f"- {tabela[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"\nErro ao verificar a tabela: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. As credenciais de acesso estão corretas")
        print("3. O banco de dados e o usuário existem")
        print("4. O usuário tem permissões adequadas")

if __name__ == "__main__":
    verificar_tabela_postgres()
