"""
Script para fazer backup do banco de dados PostgreSQL.
"""
import os
import subprocess
from datetime import datetime
from pathlib import Path

def main():
    # Configurações
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "apostapro_db"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"  # Altere para a senha do seu usuário postgres
    
    # Diretório de backup
    BACKUP_DIR = Path("backups")
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    BACKUP_FILE = BACKUP_DIR / f"{DB_NAME}_backup_{timestamp}.sql"
    
    # Configuração de ambiente para o pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    print(f"Iniciando backup do banco de dados {DB_NAME}...")
    
    try:
        # Comando para fazer o backup
        command = [
            'pg_dump',
            '-h', DB_HOST,
            '-p', DB_PORT,
            '-U', DB_USER,
            '-d', DB_NAME,
            '-f', str(BACKUP_FILE),
            '-F', 'p',  # Formato plain text
            '-v',       # Modo verboso
            '--encoding=UTF8',  # Força a codificação UTF-8
            '--no-owner',
            '--no-privileges'
        ]
        
        # Executa o comando
        result = subprocess.run(
            command,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Verifica se o arquivo foi criado
        if BACKUP_FILE.exists():
            size_mb = BACKUP_FILE.stat().st_size / (1024 * 1024)
            print(f"✅ Backup concluído com sucesso!")
            print(f"   Arquivo: {BACKUP_FILE}")
            print(f"   Tamanho: {size_mb:.2f} MB")
            return True
        else:
            print("❌ O arquivo de backup não foi criado.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o pg_dump: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    main()
