import os
from dotenv import load_dotenv
import psycopg2

def main():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações de conexão
    conn_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }
    
    print("Testando conexão com o banco de dados...")
    
    try:
        # Tenta conectar ao banco de dados
        conn = psycopg2.connect(**conn_params)
        print("✅ Conexão bem-sucedida!")
        
        # Executa uma consulta simples
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"Versão do PostgreSQL: {db_version[0]}")
        
        # Fecha a conexão
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False

if __name__ == "__main__":
    main()
