"""
Script para listar tabelas e verificar a codificação do banco de dados.
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

def main():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações de conexão
    conn_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'client_encoding': 'UTF8'  # Força a codificação UTF-8
    }
    
    print("Conectando ao banco de dados...")
    
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**conn_params)
        print("✅ Conexão bem-sucedida!")
        
        # Cria um cursor
        with conn.cursor() as cur:
            # Obtém a versão do PostgreSQL
            cur.execute("SELECT version();")
            db_version = cur.fetchone()[0]
            print(f"\n📊 Versão do PostgreSQL: {db_version}")
            
            # Obtém a codificação do banco de dados atual
            cur.execute("""
                SELECT current_database() AS database,
                       pg_encoding_to_char(encoding) AS encoding,
                       datcollate,
                       datctype
                FROM pg_database 
                WHERE datname = current_database();
            """)
            
            db_info = cur.fetchone()
            print("\n🔍 Informações do banco de dados:")
            print(f"   Nome: {db_info[0]}")
            print(f"   Codificação: {db_info[1]}")
            print(f"   Collation: {db_info[2]}")
            print(f"   Character Type: {db_info[3]}")
            
            # Lista as tabelas no esquema público
            print("\n📋 Tabelas no esquema 'public':")
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
                
                # Para cada tabela, conta os registros
                print("\n📊 Contagem de registros por tabela:")
                for table in tables:
                    table_name = table[0]
                    try:
                        cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                            sql.Identifier(table_name)
                        ))
                        count = cur.fetchone()[0]
                        print(f"- {table_name}: {count} registros")
                    except Exception as e:
                        print(f"- {table_name}: Erro ao contar registros - {e}")
            else:
                print("Nenhuma tabela encontrada no esquema 'public'.")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar o banco de dados: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
