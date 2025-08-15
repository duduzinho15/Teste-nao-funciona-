"""
Script para executar um arquivo SQL diretamente no banco de dados.
"""
import psycopg2
import sys
import os

def execute_sql_file(file_path):
    # Configurações do banco de dados
    db_config = {
        'host': 'localhost',
        'database': 'apostapro_db',
        'user': 'apostapro_user',
        'password': 'senha_segura_123',
        'port': '5432'
    }
    
    # Verifica se o arquivo existe
    if not os.path.isfile(file_path):
        print(f"❌ O arquivo {file_path} não foi encontrado.")
        return False
    
    try:
        # Lê o conteúdo do arquivo SQL
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        # Divide os comandos SQL por ponto e vírgula
        commands = sql_commands.split(';')
        
        # Conecta ao banco de dados
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False  # Desativa o autocommit para usar transações
        cur = conn.cursor()
        
        print(f"🚀 Executando comandos do arquivo: {file_path}")
        
        # Executa cada comando SQL
        for command in commands:
            # Remove espaços em branco no início e no fim
            command = command.strip()
            
            # Ignora linhas em branco e comentários
            if not command or command.startswith('--'):
                continue
                
            try:
                print(f"\n🔧 Executando comando: {command[:100]}...")
                cur.execute(command)
                
                # Se for um comando SELECT, exibe os resultados
                if command.strip().upper().startswith('SELECT'):
                    rows = cur.fetchall()
                    if rows:
                        print("\n📊 Resultados:")
                        # Exibe os nomes das colunas
                        colnames = [desc[0] for desc in cur.description]
                        print(" | ".join(colnames))
                        print("-" * 80)
                        
                        # Exibe as linhas
                        for row in rows:
                            print(" | ".join(str(value) for value in row))
            except Exception as e:
                print(f"❌ Erro ao executar comando: {e}")
                print(f"Comando problemático: {command[:200]}...")
                conn.rollback()  # Desfaz a transação em caso de erro
                return False
        
        # Confirma as alterações
        conn.commit()
        print("\n✅ Comandos SQL executados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar o arquivo SQL: {e}")
        if 'conn' in locals():
            conn.rollback()  # Desfaz a transação em caso de erro
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️  Uso: python execute_sql_direct.py <caminho_para_arquivo.sql>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"❌ O arquivo {file_path} não foi encontrado.")
        sys.exit(1)
    
    success = execute_sql_file(file_path)
    sys.exit(0 if success else 1)
