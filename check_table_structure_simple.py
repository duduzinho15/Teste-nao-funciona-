"""
Script para verificar a estrutura de uma tabela específica.
"""
import psycopg2

def check_table_structure(table_name):
    # Configurações do banco de dados
    db_config = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'apostapro_user',
        'password': 'senha_segura_123',
        'port': '5432'
    }
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print(f"🔍 Verificando a estrutura da tabela '{table_name}'...")
        
        # Verifica se a tabela existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table_name,))
        
        if not cur.fetchone()[0]:
            print(f"❌ A tabela '{table_name}' não existe no banco de dados.")
            return
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cur.fetchall()
        
        print(f"\n📋 Estrutura da tabela '{table_name}':")
        print("-" * 70)
        print(f"{'Coluna':<25} {'Tipo':<20} {'Pode ser nulo':<15} {'Valor padrão'}")
        print("-" * 70)
        for col in columns:
            print(f"{col[0]:<25} {col[1]:<20} {col[2]:<15} {col[3] or 'Nenhum'}")
        
        # Verifica as restrições de chave primária
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_name = %s;
        """, (table_name,))
        
        pk_columns = [row[0] for row in cur.fetchall()]
        print(f"\n🔑 Colunas de chave primária: {', '.join(pk_columns) if pk_columns else 'Nenhuma'}")
        
        # Verifica as restrições de chave estrangeira
        cur.execute("""
            SELECT
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
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name = %s;
        """, (table_name,))
        
        fks = cur.fetchall()
        if fks:
            print("\n🔗 Chaves estrangeiras:")
            for fk in fks:
                print(f"- {fk[0]} → {fk[1]}({fk[2]})")
        
        # Conta o número de registros
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cur.fetchone()[0]
        print(f"\n📊 Total de registros na tabela: {count}")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
    except psycopg2.Error as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    tables = ['paises_clubes', 'clubes', 'competicoes', 'estadios', 'partidas', 'estatisticas_partidas']
    for table in tables:
        check_table_structure(table)
        print("\n" + "="*80 + "\n")
