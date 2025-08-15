"""
Script para verificar a estrutura das tabelas clubes e paises_clubes.
"""
import psycopg2

def get_table_definition(table_name):
    """Obtém a definição de uma tabela específica"""
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
        
        print(f"\n🔍 Estrutura da tabela '{table_name}':")
        print("=" * 80)
        
        # Obtém as colunas da tabela
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cur.fetchall()
        
        if not columns:
            print(f"❌ A tabela '{table_name}' não foi encontrada ou está vazia.")
            return
        
        # Exibe as colunas
        print(f"{'Coluna':<25} {'Tipo':<20} {'Pode ser nulo':<15} {'Valor padrão'}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<25} {col[1]:<20} {col[2]:<15} {col[3] or 'Nenhum'}")
        
        # Obtém as restrições de chave primária
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
        
        # Obtém as restrições de chave estrangeira
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
        
        # Se houver registros, mostra alguns exemplos (máximo 3)
        if count > 0:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            print("\n📋 Registros de exemplo:")
            for row in cur.fetchall():
                print(f"- {row}")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Verificando estruturas das tabelas...")
    
    # Verifica a tabela paises_clubes
    print("\n" + "="*80)
    print("TABELA: paises_clubes")
    print("="*80)
    get_table_definition("paises_clubes")
    
    # Verifica a tabela clubes
    print("\n" + "="*80)
    print("TABELA: clubes")
    print("="*80)
    get_table_definition("clubes")
    
    # Verifica a tabela competicoes
    print("\n" + "="*80)
    print("TABELA: competicoes")
    print("="*80)
    get_table_definition("competicoes")
    
    # Verifica a tabela estadios
    print("\n" + "="*80)
    print("TABELA: estadios")
    print("="*80)
    get_table_definition("estadios")
    
    # Verifica a tabela partidas
    print("\n" + "="*80)
    print("TABELA: partidas")
    print("="*80)
    get_table_definition("partidas")
    
    # Verifica a tabela estatisticas_partidas
    print("\n" + "="*80)
    print("TABELA: estatisticas_partidas")
    print("="*80)
    get_table_definition("estatisticas_partidas")
    
    print("\n✅ Verificação concluída!")
