"""
Script para executar comandos SQL a partir de um arquivo.
"""
import sys
import psycopg2

def execute_sql_from_file(filename):
    """Executa comandos SQL a partir de um arquivo."""
    try:
        # Parâmetros de conexão
        db_params = {
            'host': 'localhost',
            'database': 'apostapro_db',
            'user': 'apostapro_user',
            'password': 'senha_segura_123',
            'port': '5432'
        }
        
        print("🔌 Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True  # Habilita o autocommit para comandos DDL
        cur = conn.cursor()
        
        print(f"📄 Lendo o arquivo SQL: {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("⚡ Executando os comandos SQL...")
        cur.execute(sql_script)
        
        # Se for uma consulta SELECT, exibe os resultados
        if sql_script.strip().upper().startswith('SELECT'):
            results = cur.fetchall()
            print("\n📊 Resultados:")
            for row in results:
                print(f"- {row[0]}: {row[1]} registros")
        
        print("\n✅ Script SQL executado com sucesso!")
        return 0
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return 1
    except psycopg2.Error as e:
        print(f"❌ Erro ao executar o script SQL: {e}")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Uso: python execute_sql_script.py <arquivo_sql>")
        sys.exit(1)
    
    filename = sys.argv[1]
    print(f"🚀 Iniciando a execução do arquivo SQL: {filename}")
    sys.exit(execute_sql_from_file(filename))
