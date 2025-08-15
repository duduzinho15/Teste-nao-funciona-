"""
Script Python para executar o SQL de criação e seed do banco de dados.
"""
import psycopg2
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "database": "apostapro_db",
    "user": "postgres",  # Usando usuário padrão com mais privilégios
    "password": "postgres",  # Senha padrão do PostgreSQL
    "port": "5432"
}

def execute_sql_file(file_path):
    """Executa um arquivo SQL no banco de dados"""
    try:
        # Conecta ao banco de dados
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info(f"📄 Lendo arquivo SQL: {file_path}")
        
        # Lê o conteúdo do arquivo SQL
        with open(file_path, 'r', encoding='utf-8') as sql_file:
            sql_commands = sql_file.read()
        
        # Divide os comandos SQL por ponto-e-vírgula
        commands = sql_commands.split(';')
        
        # Remove comandos vazios
        commands = [cmd.strip() for cmd in commands if cmd.strip()]
        
        # Executa cada comando individualmente
        for i, command in enumerate(commands, 1):
            try:
                if command.upper().startswith('SELECT'):
                    # Para comandos SELECT, executa e mostra os resultados
                    logger.info(f"\n🔍 Executando consulta {i}:")
                    cursor.execute(command)
                    rows = cursor.fetchall()
                    
                    # Exibe os resultados em formato de tabela
                    if rows:
                        # Obtém os nomes das colunas
                        colnames = [desc[0] for desc in cursor.description]
                        
                        # Calcula a largura de cada coluna
                        col_widths = [len(str(col)) for col in colnames]
                        for row in rows:
                            for i, cell in enumerate(row):
                                col_widths[i] = max(col_widths[i], len(str(cell)))
                        
                        # Imprime o cabeçalho
                        header = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(colnames))
                        print("\n" + "-" * len(header))
                        print(header)
                        print("-" * len(header))
                        
                        # Imprime as linhas
                        for row in rows:
                            print(" | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)))
                        
                        print("-" * len(header) + "\n")
                    else:
                        print("Nenhum resultado encontrado.\n")
                else:
                    # Para outros comandos, apenas executa
                    cursor.execute(command)
                    logger.info(f"✅ Comando {i} executado com sucesso")
            except psycopg2.Error as e:
                logger.error(f"❌ Erro ao executar comando {i}: {e}")
                logger.error(f"Comando: {command[:200]}...")
                # Continua para o próximo comando mesmo se houver erro
                continue
        
        logger.info("\n✨ Todos os comandos foram processados!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar o arquivo SQL: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sql_file = Path(__file__).parent / "create_and_seed.sql"
    
    if not sql_file.exists():
        logger.error(f"❌ Arquivo SQL não encontrado: {sql_file}")
        exit(1)
    
    logger.info(f"🚀 Iniciando execução do arquivo SQL: {sql_file}")
    
    if execute_sql_file(sql_file):
        logger.info("✅ Script de seed concluído com sucesso!")
    else:
        logger.error("❌ Ocorreram erros durante a execução do script de seed.")
        exit(1)
