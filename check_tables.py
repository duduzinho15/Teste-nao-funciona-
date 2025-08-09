import os
from dotenv import load_dotenv
import psycopg2

def check_tables():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Conecta ao banco de dados
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    
    try:
        # Cria um cursor
        cur = conn.cursor()
        
        # Verifica se a tabela alembic_version existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            );
        """)
        alembic_version_exists = cur.fetchone()[0]
        print(f"Tabela alembic_version existe? {alembic_version_exists}")
        
        # Verifica se a tabela posts_redes_sociais existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = 'posts_redes_sociais'
            );
        """)
        posts_table_exists = cur.fetchone()[0]
        print(f"Tabela posts_redes_sociais existe? {posts_table_exists}")
        
        # Lista todas as tabelas no esquema público
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        print("\nTabelas no banco de dados:")
        for table in cur.fetchall():
            print(f"- {table[0]}")
            
    finally:
        # Fecha o cursor e a conexão
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_tables()
