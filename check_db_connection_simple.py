"""
Script simples para verificar a conexão com o banco de dados e listar as tabelas existentes.
"""
import psycopg2

def main():
    # Configurações do banco de dados
    db_params = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'postgres',  # Usuário com privilégios
        'password': 'postgres',  # Senha do usuário postgres
        'port': '5432'
    }
    
    print("🔍 Tentando conectar ao banco de dados...")
    
    try:
        # Tenta conectar ao banco de dados
        conn = psycopg2.connect(**db_params)
        print("✅ Conexão bem-sucedida!")
        
        # Cria um cursor para executar consultas
        cur = conn.cursor()
        
        # Lista todas as tabelas no esquema público
        print("\n📋 Tabelas no banco de dados:")
        print("=" * 50)
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        if tables:
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("Nenhuma tabela encontrada no esquema público.")
        
        # Fecha o cursor e a conexão
        cur.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")
    finally:
        print("\n🔒 Conexão encerrada.")

if __name__ == "__main__":
    main()
