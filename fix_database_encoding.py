"""
Script para corrigir a codificação do banco de dados PostgreSQL.

Este script:
1. Faz backup do banco de dados atual
2. Cria um novo banco de dados com a codificação UTF-8
3. Restaura os dados do backup
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configurações
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "apostapro_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # Altere para a senha do seu usuário postgres
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Nome do arquivo de backup com timestamp
BACKUP_FILE = BACKUP_DIR / f"{DB_NAME}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

# Configuração de ambiente para o psql
os.environ["PGPASSWORD"] = DB_PASSWORD

def run_command(command, description):
    """Executa um comando e retorna True se bem-sucedido."""
    print(f"\n🔧 {description}...")
    print(f"   Comando: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            print(f"   Saída: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o comando: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr}")
        return False

def backup_database():
    """Faz backup do banco de dados atual."""
    command = f'pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -F p -b -v -f "{BACKUP_FILE}" {DB_NAME}'
    if run_command(command, f"Fazendo backup do banco de dados {DB_NAME} para {BACKUP_FILE}"):
        print(f"✅ Backup criado com sucesso: {BACKUP_FILE}")
        return True
    return False

def drop_database():
    """Remove o banco de dados existente."""
    # Encerra todas as conexões ativas
    terminate_connections = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'{DB_NAME}\';"'
    run_command(terminate_connections, "Encerrando conexões ativas")
    
    # Remove o banco de dados
    drop_db = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "DROP DATABASE IF EXISTS \"{DB_NAME}\";"'
    if run_command(drop_db, f"Removendo banco de dados {DB_NAME}"):
        print(f"✅ Banco de dados {DB_NAME} removido com sucesso")
        return True
    return False

def create_database():
    """Cria um novo banco de dados com codificação UTF-8."""
    create_db = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "CREATE DATABASE \"{DB_NAME}\" WITH ENCODING=\'UTF8\' LC_COLLATE=\'pt_BR.UTF-8\' LC_CTYPE=\'pt_BR.UTF-8\' TEMPLATE=template0;"'
    if run_command(create_db, f"Criando novo banco de dados {DB_NAME} com codificação UTF-8"):
        print(f"✅ Banco de dados {DB_NAME} criado com sucesso com codificação UTF-8")
        return True
    return False

def restore_database():
    """Restaura o banco de dados a partir do backup."""
    command = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f "{BACKUP_FILE}"'
    if run_command(command, f"Restaurando banco de dados {DB_NAME} a partir de {BACKUP_FILE}"):
        print(f"✅ Banco de dados {DB_NAME} restaurado com sucesso")
        return True
    return False

def main():
    print("""
    🛠️  CORREÇÃO DE CODIFICAÇÃO DO BANCO DE DADOS
    ===========================================
    Este script irá:
    1. Fazer backup do banco de dados atual
    2. Remover o banco de dados existente
    3. Criar um novo banco de dados com codificação UTF-8
    4. Restaurar os dados do backup
    """)
    
    # 1. Fazer backup
    if not backup_database():
        print("❌ Falha ao fazer backup do banco de dados. Abortando...")
        return
    
    # 2. Remover banco de dados existente
    if not drop_database():
        print("❌ Falha ao remover o banco de dados. Abortando...")
        return
    
    # 3. Criar novo banco de dados com codificação correta
    if not create_database():
        print("❌ Falha ao criar o novo banco de dados. Abortando...")
        return
    
    # 4. Restaurar dados do backup
    if not restore_database():
        print("❌ Falha ao restaurar o banco de dados. Você pode restaurar manualmente com:")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f \"{BACKUP_FILE}\"")
        return
    
    print("\n✅ Processo concluído com sucesso!")
    print(f"   Backup salvo em: {BACKUP_FILE}")
    print("   O banco de dados foi recriado com codificação UTF-8")

if __name__ == "__main__":
    main()
