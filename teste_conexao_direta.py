import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

def testar_conexao():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            dbname=os.getenv('DB_NAME', 'apostapro_db'),
            user=os.getenv('DB_USER', 'apostapro_user'),
            password=os.getenv('DB_PASSWORD', 'Canjica@@2025')
        )
        
        print("✅ Conexão bem-sucedida!")
        print("📊 Informações do servidor:")
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(f" - {cur.fetchone()[0]}")
            
            cur.execute("SELECT current_database(), current_user;")
            db_info = cur.fetchone()
            print(f" - Banco de dados: {db_info[0]}")
            print(f" - Usuário: {db_info[1]}")
        
        return True
        
    except OperationalError as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    testar_conexao()