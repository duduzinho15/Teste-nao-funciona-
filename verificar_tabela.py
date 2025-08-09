import sqlite3

def verificar_tabela():
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect('Coleta_de_dados/database/football_data.db')
        cursor = conn.cursor()
        
        # Verifica se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts_redes_sociais'")
        existe = cursor.fetchone() is not None
        print(f"Tabela 'posts_redes_sociais' existe: {existe}")
        
        if existe:
            # Obtém o esquema da tabela
            cursor.execute("PRAGMA table_info(posts_redes_sociais)")
            colunas = cursor.fetchall()
            print("\nEstrutura da tabela 'posts_redes_sociais':")
            for coluna in colunas:
                print(f"- {coluna[1]}: {coluna[2]}")
        else:
            print("\nA tabela 'posts_redes_sociais' não foi encontrada no banco de dados.")
            
        # Lista todas as tabelas no banco de dados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print("\nTabelas disponíveis no banco de dados:")
        for tabela in tabelas:
            print(f"- {tabela[0]}")
            
    except Exception as e:
        print(f"Erro ao verificar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verificar_tabela()
