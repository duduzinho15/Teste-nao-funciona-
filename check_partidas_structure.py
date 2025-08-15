"""
Script para verificar a estrutura da tabela 'partidas'.
"""
import sys
import psycopg2
from psycopg2 import sql

def check_partidas_structure():
    """Verifica a estrutura da tabela 'partidas'."""
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
                WHERE table_name = 'partidas'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("❌ A tabela 'partidas' não existe no banco de dados.")
            return 1
        
        # Se a tabela existir, verifica sua estrutura
        print("\n📋 Estrutura da tabela 'partidas':")
        print("=" * 50)
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'partidas'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        # Exibe a estrutura da tabela
        for col in columns:
            print(f"- {col[0]}: {col[1]} (nullable: {col[2]}){' DEFAULT: ' + str(col[3]) if col[3] else ''}")
        
        # Verifica as restrições de chave estrangeira
        print("\n🔑 Restrições de chave estrangeira:")
        cur.execute("""
            SELECT
                tc.constraint_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'partidas';
        """)
        
        fks = cur.fetchall()
        
        if fks:
            for fk in fks:
                print(f"- {fk[1]} → {fk[2]}({fk[3]}) [constraint: {fk[0]}]")
        else:
            print("- Nenhuma restrição de chave estrangeira encontrada.")
        
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
    print("🔍 Verificando a estrutura da tabela 'partidas'...")
    sys.exit(check_partidas_structure())
