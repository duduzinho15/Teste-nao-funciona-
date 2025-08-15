"""
Script para verificar a estrutura e os dados da tabela 'competicoes'.
"""
import sys
import psycopg2
from psycopg2 import sql

def check_competicoes_table():
    """Verifica a estrutura e os dados da tabela 'competicoes'."""
    try:
        # Parâmetros de conexão
        db_params = {
            'host': 'localhost',
            'database': 'apostapro_db',
            'user': 'apostapro_user',
            'password': 'senha_segura_123',
            'port': '5432'
        }
        
        print("🔍 Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Verifica a estrutura da tabela
        print("\n📋 Estrutura da tabela 'competicoes':")
        print("=" * 50)
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'competicoes'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        if not columns:
            print("❌ A tabela 'competicoes' não foi encontrada no banco de dados.")
            return 1
        
        # Exibe a estrutura da tabela
        for col in columns:
            print(f"- {col[0]}: {col[1]} (nullable: {col[2]}){' DEFAULT: ' + str(col[3]) if col[3] else ''}")
        
        # Conta os registros
        cur.execute("SELECT COUNT(*) FROM competicoes;")
        count = cur.fetchone()[0]
        print(f"\n📊 Total de competições cadastradas: {count}")
        
        # Mostra as primeiras 5 competições, se houver
        if count > 0:
            print("\n🏆 Primeiras competições cadastradas:")
            cur.execute("SELECT * FROM competicoes LIMIT 5;")
            competicoes = cur.fetchall()
            
            # Obtém os nomes das colunas
            col_names = [desc[0] for desc in cur.description]
            
            # Exibe os dados formatados
            for comp in competicoes:
                print("\n" + "-" * 50)
                for i, value in enumerate(comp):
                    print(f"{col_names[i]}: {value}")
        
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
    print("🔍 Verificando a tabela 'competicoes'...")
    sys.exit(check_competicoes_table())
