"""
Script para verificar a estrutura da tabela paises_clubes.
"""
import psycopg2

def check_table_structure():
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
        
        print("🔍 Verificando a estrutura da tabela 'paises_clubes'...")
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'paises_clubes';
        """)
        
        columns = cur.fetchall()
        
        if not columns:
            print("❌ A tabela 'paises_clubes' não existe no banco de dados.")
            return
            
        print("\n📋 Estrutura da tabela 'paises_clubes':")
        print("-" * 50)
        for col in columns:
            print(f"Coluna: {col[0]}")
            print(f"  Tipo: {col[1]}")
            print(f"  Pode ser nulo: {col[2]}")
            print(f"  Valor padrão: {col[3]}")
            print("-" * 50)
            
        # Verifica as restrições de chave primária
        cur.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_name = 'paises_clubes';
        """)
        
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
            AND tc.table_name = 'paises_clubes';
        """)
        
        fks = cur.fetchall()
        if fks:
            print("\n🔗 Chaves estrangeiras:")
            for fk in fks:
                print(f"- {fk[0]} → {fk[1]}({fk[2]})")
        else:
            print("\nℹ️ Nenhuma chave estrangeira encontrada.")
            
        # Verifica os índices
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'paises_clubes';
        """)
        
        indexes = cur.fetchall()
        if indexes:
            print("\n📊 Índices:")
            for idx in indexes:
                print(f"- {idx[0]}: {idx[1][:100]}..." if len(idx[1]) > 100 else f"- {idx[0]}: {idx[1]}")
        else:
            print("\nℹ️ Nenhum índice encontrado.")
            
        # Conta o número de registros
        cur.execute("SELECT COUNT(*) FROM paises_clubes;")
        count = cur.fetchone()[0]
        print(f"\n📊 Total de registros na tabela: {count}")
        
        # Mostra alguns registros de exemplo (máximo 5)
        if count > 0:
            cur.execute("SELECT * FROM paises_clubes LIMIT 5;")
            print("\n📋 Registros de exemplo:")
            for row in cur.fetchall():
                print(f"- {row}")
        
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
    check_table_structure()
