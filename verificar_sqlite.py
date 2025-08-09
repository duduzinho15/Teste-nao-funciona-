import sqlite3
import os

def verificar_banco_sqlite():
    print("Verificando banco de dados SQLite...")
    
    # Caminho para o arquivo SQLite
    db_path = os.path.join(os.getcwd(), 'fbref_data.db')
    
    if not os.path.exists(db_path):
        print(f"Arquivo do banco de dados não encontrado em: {db_path}")
        return
    
    print(f"Encontrado arquivo do banco de dados em: {db_path}")
    
    try:
        # Conecta ao banco de dados SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("Nenhuma tabela encontrada no banco de dados.")
            return
        
        print("\nTabelas encontradas no banco de dados:")
        for table in tables:
            table_name = table[0]
            print(f"\nTabela: {table_name}")
            
            # Obtém informações sobre as colunas
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("Colunas:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  - {col_name}: {col_type} {'PRIMARY KEY' if pk else ''} {'NOT NULL' if not_null else ''} {f'DEFAULT {default_val}' if default_val is not None else ''}")
            
            # Conta o número de linhas na tabela
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Total de registros: {count:,}")
            
            # Se for a tabela de migrações, lista as migrações aplicadas
            if table_name == 'alembic_version':
                cursor.execute("SELECT * FROM alembic_version;")
                version = cursor.fetchone()
                if version:
                    print(f"\nVersão do Alembic: {version[0]}")
        
        # Verifica se a tabela posts_redes_sociais existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts_redes_sociais';")
        posts_table_exists = cursor.fetchone() is not None
        
        if posts_table_exists:
            print("\nA tabela 'posts_redes_sociais' EXISTE no banco de dados SQLite.")
        else:
            print("\nA tabela 'posts_redes_sociais' NÃO existe no banco de dados SQLite.")
        
        conn.close()
        
    except Exception as e:
        print(f"\nErro ao acessar o banco de dados SQLite: {e}")

if __name__ == "__main__":
    verificar_banco_sqlite()
