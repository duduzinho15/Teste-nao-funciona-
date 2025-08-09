import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def verificar_permissoes():
    print("=== Verificando Permissões do Usuário no PostgreSQL ===")
    
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações de conexão
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'apostapro_db'),
        'user': os.getenv('DB_USER', 'apostapro_user'),
        'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
    }
    
    try:
        # Tenta conectar ao banco de dados
        print(f"Conectando ao banco de dados {db_config['database']}...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. Verifica o usuário atual
        cursor.execute("SELECT current_user, current_database();")
        current_user, current_db = cursor.fetchone()
        print(f"\nUsuário atual: {current_user}")
        print(f"Banco de dados atual: {current_db}")
        
        # 2. Verifica as permissões do usuário
        cursor.execute("""
            SELECT 
                table_schema,
                table_name,
                privilege_type
            FROM 
                information_schema.role_table_grants
            WHERE 
                grantee = current_user
                AND table_schema = 'public'
            ORDER BY 
                table_name, privilege_type;
        """)
        
        permissoes = cursor.fetchall()
        
        if not permissoes:
            print("\nNenhuma permissão encontrada para o usuário no esquema público.")
        else:
            print("\nPermissões do usuário no esquema público:")
            for permissao in permissoes:
                print(f"- {permissao[0]}.{permissao[1]}: {permissao[2]}")
        
        # 3. Verifica se o usuário pode criar tabelas
        cursor.execute("""
            SELECT has_schema_privilege(current_user, 'public', 'CREATE');
        """)
        
        pode_criar = cursor.fetchone()[0]
        print(f"\nO usuário pode criar tabelas no esquema público: {'SIM' if pode_criar else 'NÃO'}")
        
        # 4. Verifica se o usuário é superusuário
        cursor.execute("SELECT usesuper FROM pg_user WHERE usename = current_user;")
        is_superuser = cursor.fetchone()[0]
        print(f"O usuário é superusuário: {'SIM' if is_superuser else 'NÃO'}")
        
        # 5. Verifica as permissões de conexão
        cursor.execute("""
            SELECT 
                rolcanlogin, 
                rolcreatedb, 
                rolcreaterole, 
                rolsuper
            FROM 
                pg_roles 
            WHERE 
                rolname = current_user;
        """)
        
        rolcanlogin, rolcreatedb, rolcreaterole, rolsuper = cursor.fetchone()
        print("\nPermissões de conexão do usuário:")
        print(f"- Pode fazer login: {'SIM' if rolcanlogin else 'NÃO'}")
        print(f"- Pode criar bancos de dados: {'SIM' if rolcreatedb else 'NÃO'}")
        print(f"- Pode criar funções: {'SIM' if rolcreaterole else 'NÃO'}")
        print(f"- É superusuário: {'SIM' if rolsuper else 'NÃO'}")
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nErro ao verificar permissões: {e}")

if __name__ == "__main__":
    verificar_permissoes()
