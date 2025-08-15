"""
Script para verificar a estrutura e os dados da tabela 'estadios'.
"""
import sys
import psycopg2
from psycopg2 import sql

def check_estadios_table():
    """Verifica a estrutura e os dados da tabela 'estadios'."""
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
        
        # Verifica se a tabela existe
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'estadios'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ A tabela 'estadios' não existe no banco de dados.")
            return 1
        
        # Se a tabela existir, verifica sua estrutura
        print("\n📋 Estrutura da tabela 'estadios':")
        print("=" * 50)
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'estadios'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        # Exibe a estrutura da tabela
        for col in columns:
            print(f"- {col[0]}: {col[1]} (nullable: {col[2]}){' DEFAULT: ' + str(col[3]) if col[3] else ''}")
        
        # Conta os registros
        cur.execute("SELECT COUNT(*) FROM estadios;")
        count = cur.fetchone()[0]
        print(f"\n📊 Total de estádios cadastrados: {count}")
        
        # Mostra os primeiros 5 estádios, se houver
        if count > 0:
            print("\n🏟️  Primeiros estádios cadastrados:")
            cur.execute("SELECT * FROM estadios LIMIT 5;")
            estadios = cur.fetchall()
            
            # Obtém os nomes das colunas
            col_names = [desc[0] for desc in cur.description]
            
            # Exibe os dados formatados
            for estadio in estadios:
                print("\n" + "-" * 50)
                for i, value in enumerate(estadio):
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
    print("🔍 Verificando a tabela 'estadios'...")
    sys.exit(check_estadios_table())
