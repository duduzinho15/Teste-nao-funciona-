"""
Script para corrigir a codificação do banco de dados PostgreSQL.
Versão simplificada para Windows.
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

def run_sql_command(sql, description):
    """Executa um comando SQL e retorna True se bem-sucedido."""
    print(f"\n🔧 {description}...")
    print(f"   SQL: {sql}")
    
    try:
        # Cria um comando psql com a string SQL entre aspas
        command = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d postgres -c "{sql}"'
        
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
        
        if result.stdout.strip():
            print(f"   Saída: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o comando SQL: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        return False

def backup_database():
    """Faz backup do banco de dados atual."""
    print(f"\n💾 Fazendo backup do banco de dados {DB_NAME}...")
    
    # Usando pg_dump com redirecionamento de saída para o arquivo
    command = f'pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -F p -b -v -f "{BACKUP_FILE}" {DB_NAME}'
    
    try:
        subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"✅ Backup criado com sucesso: {BACKUP_FILE}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao fazer backup do banco de dados: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        return False

def main():
    print("""
    🛠️  CORREÇÃO DE CODIFICAÇÃO DO BANCO DE DADOS
    ===========================================
    Este script irá:
    1. Fazer backup do banco de dados atual
    2. Encerrar conexões ativas
    3. Remover o banco de dados existente
    4. Criar um novo banco de dados com codificação UTF-8
    5. Restaurar os dados do backup
    """)
    
    # 1. Fazer backup
    if not backup_database():
        print("❌ Falha ao fazer backup do banco de dados. Abortando...")
        return
    
    # 2. Encerrar conexões ativas
    print("\n🚦 Encerrando conexões ativas...")
    if not run_sql_command(
        f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}';",
        "Encerrando conexões ativas"
    ):
        print("⚠️  Não foi possível encerrar todas as conexões. Continuando...")
    
    # 3. Remover banco de dados existente
    if not run_sql_command(
        f"DROP DATABASE IF EXISTS \"{DB_NAME}\";",
        f"Removendo banco de dados {DB_NAME}"
    ):
        print("❌ Falha ao remover o banco de dados. Abortando...")
        return
    
    # 4. Criar novo banco de dados com codificação correta
    if not run_sql_command(
        f"CREATE DATABASE \"{DB_NAME}\" WITH ENCODING='UTF8' LC_COLLATE='pt_BR.UTF-8' LC_CTYPE='pt_BR.UTF-8' TEMPLATE=template0;",
        f"Criando novo banco de dados {DB_NAME} com codificação UTF-8"
    ):
        print("❌ Falha ao criar o novo banco de dados. Abortando...")
        return
    
    # 5. Restaurar dados do backup
    print(f"\n🔄 Restaurando banco de dados {DB_NAME} a partir de {BACKUP_FILE}...")
    
    try:
        command = f'psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f "{BACKUP_FILE}"'
        
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
        
        if result.stderr:
            print(f"⚠️  Avisos durante a restauração: {result.stderr.strip()}")
        
        print(f"✅ Banco de dados {DB_NAME} restaurado com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao restaurar o banco de dados: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        print(f"\n⚠️  Você pode tentar restaurar manualmente com o comando:")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -f \"{BACKUP_FILE}\"")
        return
    
    print("\n✅ Processo concluído com sucesso!")
    print(f"   Backup salvo em: {BACKUP_FILE}")
    print("   O banco de dados foi recriado com codificação UTF-8")

if __name__ == "__main__":
    main()
