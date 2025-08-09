import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def testar_conexao():
    print("=== Teste de Conexão com PostgreSQL ===")
    
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
        # Tenta conectar ao banco de dados
        print(f"Tentando conectar ao banco de dados {db_config['database']} em {db_config['host']}:{db_config['port']}...")
        conn = psycopg2.connect(**db_config)
        
        # Cria um cursor para executar consultas
        cur = conn.cursor()
        
        # Executa uma consulta simples para testar a conexão
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"✅ Conectado com sucesso ao PostgreSQL: {db_version[0]}")
        
        # Lista todas as tabelas no esquema público
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tabelas = cur.fetchall()
        
        if not tabelas:
            print("\nNenhuma tabela encontrada no esquema público.")
        else:
            print("\nTabelas no esquema público:")
            for tabela in tabelas:
                print(f"- {tabela[0]}")
        
        # Fecha a conexão
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar ao banco de dados: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. As credenciais de acesso estão corretas")
        print("3. O banco de dados e o usuário existem")
        print(f"\nDetalhes do erro: {str(e)}")

if __name__ == "__main__":
    testar_conexao()
