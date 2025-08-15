"""
Script para verificar a estrutura da tabela 'paises_clubes'.
"""
import sys
import psycopg2
from psycopg2 import sql

def check_paises_clubes_structure():
    """Verifica a estrutura da tabela 'paises_clubes'."""
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
                WHERE table_name = 'paises_clubes'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ A tabela 'paises_clubes' não existe no banco de dados.")
            return 1
        
        # Se a tabela existir, verifica sua estrutura
        print("\n📋 Estrutura da tabela 'paises_clubes':")
        print("=" * 50)
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'paises_clubes'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        # Exibe a estrutura da tabela
        for col in columns:
            print(f"- {col[0]}: {col[1]} (nullable: {col[2]}){' DEFAULT: ' + str(col[3]) if col[3] else ''}")
        
        # Verifica se existem restrições de chave primária
        print("\n🔑 Restrições de chave primária:")
        cur.execute("""
            SELECT kcu.column_name, ccu.constraint_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.table_name = 'paises_clubes' AND tc.constraint_type = 'PRIMARY KEY';
        """)
        
        pks = cur.fetchall()
        
        if pks:
            for pk in pks:
                print(f"- {pk[0]} [constraint: {pk[1]}]")
        else:
            print("- Nenhuma restrição de chave primária encontrada.")
        
        # Verifica os dados atuais na tabela
        print("\n📊 Dados atuais na tabela 'paises_clubes':")
        cur.execute("SELECT * FROM paises_clubes;")
        rows = cur.fetchall()
        
        if rows:
            print(f"\nTotal de registros: {len(rows)}")
            print("\nPrimeiros 5 registros:")
            for i, row in enumerate(rows[:5], 1):
                print(f"{i}. {row}")
        else:
            print("- A tabela está vazia.")
        
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
    print("🔍 Verificando a estrutura da tabela 'paises_clubes'...")
    sys.exit(check_paises_clubes_structure())
