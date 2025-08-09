import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

def verificar_banco_postgresql():
    print("=== Verificando Banco de Dados PostgreSQL ===")
    
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
        print(f"Tentando conectar ao banco de dados {db_config['database']} em {db_config['host']}:{db_config['port']}...")
        conn = psycopg2.connect(**db_config)
        
        # Cria um cursor para executar consultas
        cursor = conn.cursor()
        
        # Verifica a versão do PostgreSQL
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"\nVersão do PostgreSQL: {db_version[0]}")
        
        # Lista todas as tabelas no esquema público
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        
        if not tabelas:
            print("\nNenhuma tabela encontrada no esquema público.")
        else:
            print("\nTabelas no esquema público:")
            for tabela in tabelas:
                print(f"- {tabela[0]}")
        
        # Verifica se a tabela alembic_version existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version'
            );
        """)
        
        alembic_version_exists = cursor.fetchone()[0]
        
        if alembic_version_exists:
            print("\nTabela 'alembic_version' encontrada.")
            
            # Obtém a versão atual do Alembic
            cursor.execute("SELECT version_num FROM alembic_version;")
            versao_alembic = cursor.fetchone()
            print(f"Versão do Alembic: {versao_alembic[0] if versao_alembic else 'N/A'}")
        else:
            print("\nTabela 'alembic_version' NÃO encontrada. Parece que nenhuma migração foi aplicada.")
        
        # Verifica se a tabela posts_redes_sociais existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'posts_redes_sociais'
            );
        """)
        
        posts_table_exists = cursor.fetchone()[0]
        
        if posts_table_exists:
            print("\nTabela 'posts_redes_sociais' encontrada.")
            
            # Conta o número de registros na tabela
            cursor.execute("SELECT COUNT(*) FROM posts_redes_sociais;")
            num_registros = cursor.fetchone()[0]
            print(f"Número de registros em 'posts_redes_sociais': {num_registros:,}")
            
            # Mostra as colunas da tabela
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'posts_redes_sociais'
                ORDER BY ordinal_position;
            """)
            
            colunas = cursor.fetchall()
            print("\nEstrutura da tabela 'posts_redes_sociais':")
            for coluna in colunas:
                print(f"- {coluna[0]} ({coluna[1]}) {'NULL' if coluna[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {coluna[3]}' if coluna[3] else ''}")
        else:
            print("\nTabela 'posts_redes_sociais' NÃO encontrada.")
        
        # Fecha a conexão
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nErro ao acessar o banco de dados: {e}")
        print("\nVerifique se:")
        print("1. O servidor PostgreSQL está em execução")
        print("2. As credenciais de acesso estão corretas")
        print("3. O banco de dados e o usuário existem")
        print("4. O usuário tem permissões adequadas")
        print(f"\nDetalhes do erro: {str(e)}")

if __name__ == "__main__":
    verificar_banco_postgresql()
