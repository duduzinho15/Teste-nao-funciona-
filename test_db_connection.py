import psycopg2
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Parâmetros de conexão
params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
}

try:
    # Tenta conectar ao banco de dados
    print(f"Tentando conectar ao banco de dados {params['database']} em {params['host']}:{params['port']}...")
    conn = psycopg2.connect(**params)
    
    # Cria um cursor
    cur = conn.cursor()
    
    # Executa uma consulta simples
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(f"Conexão bem-sucedida!")
    print(f"Versão do PostgreSQL: {db_version[0]}")
    
    # Lista as tabelas do banco de dados
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("\nTabelas no banco de dados:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Fecha a conexão
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
