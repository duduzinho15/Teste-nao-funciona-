"""
Script simples para listar todas as tabelas no banco de dados.
"""
import psycopg2

def list_tables():
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
        
        # Obtém a lista de tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        # Exibe as tabelas
        print("\n📋 Tabelas no banco de dados:")
        print("-" * 40)
        for table in cur.fetchall():
            print(f"- {table[0]}")
        
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
    print("🔍 Listando tabelas no banco de dados...")
    if list_tables():
        print("\n✅ Listagem concluída com sucesso!")
    else:
        print("\n❌ Ocorreu um erro ao listar as tabelas.")
