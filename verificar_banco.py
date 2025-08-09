import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def main():
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Parâmetros de conexão
    conn_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    print("Tentando conectar ao banco de dados com os seguintes parâmetros:")
    print(f"Host: {conn_params['host']}")
    print(f"Porta: {conn_params['port']}")
    print(f"Banco de dados: {conn_params['database']}")
    print(f"Usuário: {conn_params['user']}")
    
    try:
        # Tenta conectar ao banco de dados
        conn = psycopg2.connect(**conn_params)
        print("\nConexão bem-sucedida!")
        
        # Cria um cursor
        cur = conn.cursor()
        
        # Obtém a versão do PostgreSQL
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(f"\nVersão do PostgreSQL: {db_version[0]}")
        
        # Lista as extensões instaladas
        print("\nExtensões instaladas:")
        cur.execute("SELECT extname, extversion FROM pg_extension")
        for ext in cur.fetchall():
            print(f"- {ext[0]} (versão {ext[1]})")
        
        # Lista as tabelas do banco de dados
        print("\nTabelas no banco de dados:")
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        if not tables:
            print("Nenhuma tabela encontrada no esquema 'public'.")
        else:
            for schema, table in tables:
                print(f"- {schema}.{table}")
                
                # Lista as colunas da tabela
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """, (schema, table))
                
                print(f"  Colunas da tabela {table}:")
                for col in cur.fetchall():
                    col_name, data_type, is_nullable, col_default = col
                    print(f"    - {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}" + 
                          (f" DEFAULT {col_default}" if col_default else ""))
        
        # Verifica se a tabela posts_redes_sociais existe
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'posts_redes_sociais'
            )
        """)
        posts_table_exists = cur.fetchone()[0]
        
        if posts_table_exists:
            print("\nA tabela 'posts_redes_sociais' existe. Verificando sua estrutura...")
            
            # Obtém informações sobre as colunas da tabela posts_redes_sociais
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'posts_redes_sociais'
                ORDER BY ordinal_position
            """)
            
            print("\nEstrutura da tabela 'posts_redes_sociais':")
            for col in cur.fetchall():
                col_name, data_type, is_nullable, col_default = col
                print(f"  - {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}" + 
                      (f" DEFAULT {col_default}" if col_default else ""))
        else:
            print("\nA tabela 'posts_redes_sociais' NÃO existe no banco de dados.")
        
        # Fecha a conexão
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\nErro ao conectar ao banco de dados: {e}")
        print("\nVerifique se:")
        print("1. O serviço PostgreSQL está em execução")
        print("2. As credenciais de acesso estão corretas")
        print("3. O banco de dados e o usuário existem")
        print("4. O usuário tem permissão para acessar o banco de dados")
        print("5. O firewall não está bloqueando a conexão")
        print("\nPara mais detalhes, consulte os logs do PostgreSQL.")

if __name__ == "__main__":
    main()
