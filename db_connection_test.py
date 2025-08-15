"""
Script para testar a conexão com o banco de dados e listar as tabelas disponíveis.
"""
import sys
import psycopg2
from psycopg2 import sql

def test_db_connection():
    """Testa a conexão com o banco de dados e lista as tabelas disponíveis."""
    try:
        # Parâmetros de conexão
        db_params = {
            'host': 'localhost',
            'database': 'apostapro_db',
            'user': 'apostapro_user',
            'password': 'senha_segura_123',
            'port': '5432'
        }
        
        print("🔍 Tentando conectar ao banco de dados...")
        
        # Tenta estabelecer a conexão
        conn = psycopg2.connect(**db_params)
        print("✅ Conexão bem-sucedida!")
        
        # Cria um cursor para executar consultas
        cur = conn.cursor()
        
        # Lista todas as tabelas no esquema público
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        # Obtém os resultados
        tables = cur.fetchall()
        
        if tables:
            print("\n📋 Tabelas disponíveis no banco de dados:")
            print("=" * 50)
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("\nℹ️  Nenhuma tabela encontrada no banco de dados.")
        
        # Fecha o cursor e a conexão
        cur.close()
        conn.close()
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_db_connection())
