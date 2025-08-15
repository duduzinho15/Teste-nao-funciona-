"""
Script para corrigir a codificação do banco de dados PostgreSQL.
Versão final com tratamento de erros aprimorado.
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import getpass

def run_command(command, description, env=None, show_output=True):
    """Executa um comando e retorna (sucesso, saída)."""
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
            errors='replace',
            env=env
        )
        
        output = result.stdout.strip()
        if output and show_output:
            print(f"   Saída: {output}")
            
        if result.stderr:
            print(f"   Aviso: {result.stderr.strip()}")
            
        return True, output
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o comando: {e}")
        if e.stderr:
            print(f"   Erro: {e.stderr.strip()}")
        return False, e.stderr.strip()

def check_postgres_connection():
    """Verifica se é possível conectar ao PostgreSQL."""
    print("\n🔍 Verificando conexão com o PostgreSQL...")
    
    # Tenta conectar usando psql
    cmd = 'psql -h localhost -p 5432 -U postgres -c "SELECT version();"'
    success, _ = run_command(cmd, "Testando conexão com psql")
    
    if not success:
        print("\n❌ Não foi possível conectar ao PostgreSQL. Verifique:")
        print("1. Se o serviço PostgreSQL está em execução")
        print("2. Se o usuário 'postgres' existe e tem permissão para se conectar")
        print("3. Se a senha está correta")
        return False
    
    return True

def get_postgres_password():
    """Solicita a senha do PostgreSQL de forma segura."""
    print("\n🔑 Credenciais do PostgreSQL")
    print("-" * 40)
    print("Por favor, insira a senha do usuário 'postgres':")
    password = getpass.getpass("Senha: ")
    
    # Verifica a senha
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    cmd = 'psql -h localhost -p 5432 -U postgres -c "SELECT 1;"'
    success, _ = run_command(cmd, "Verificando credenciais", env=env, show_output=False)
    
    if not success:
        print("❌ Senha incorreta. Tente novamente.")
        return get_postgres_password()
    
    return password

def backup_database(db_name, password):
    """Faz backup do banco de dados."""
    # Cria o diretório de backup se não existir
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Nome do arquivo de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{db_name}_backup_{timestamp}.sql"
    
    # Configura o ambiente
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    # Comando para fazer o backup
    cmd = (
        f'pg_dump -h localhost -p 5432 -U postgres '
        f'-F p -b -v -f "{backup_file}" "{db_name}"'
    )
    
    success, _ = run_command(cmd, f"Fazendo backup do banco de dados {db_name}", env=env)
    
    if success and backup_file.exists():
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"✅ Backup concluído com sucesso!")
        print(f"   Arquivo: {backup_file}")
        print(f"   Tamanho: {size_mb:.2f} MB")
        return str(backup_file)
    else:
        print("❌ Falha ao fazer o backup do banco de dados.")
        return None

def recreate_database(db_name, password, backup_file=None):
    """Recria o banco de dados com a codificação correta."""
    # Configura o ambiente
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    # 1. Encerra todas as conexões ativas
    print("\n🚦 Encerrando conexões ativas...")
    cmd = (
        f'psql -h localhost -p 5432 -U postgres -d postgres '
        f'-c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = \'{db_name}\';"'
    )
    run_command(cmd, "Encerrando conexões ativas", env=env)
    
    # 2. Remove o banco de dados existente
    print("\n🗑️  Removendo banco de dados existente...")
    cmd = f'psql -h localhost -p 5432 -U postgres -d postgres -c "DROP DATABASE IF EXISTS \"{db_name}\";"'
    success, _ = run_command(cmd, f"Removendo banco de dados {db_name}", env=env)
    
    if not success:
        print("❌ Não foi possível remover o banco de dados. Abortando...")
        return False
    
    # 3. Cria um novo banco de dados com a codificação correta
    print("\n🆕 Criando novo banco de dados com codificação UTF-8...")
    cmd = (
        f'psql -h localhost -p 5432 -U postgres -d postgres '
        f'-c "CREATE DATABASE \"{db_name}\" WITH ENCODING=\'UTF8\' LC_COLLATE=\'pt_BR.UTF-8\' LC_CTYPE=\'pt_BR.UTF-8\' TEMPLATE=template0;"'
    )
    success, _ = run_command(cmd, f"Criando banco de dados {db_name}", env=env)
    
    if not success:
        print("❌ Não foi possível criar o novo banco de dados. Abortando...")
        return False
    
    # 4. Se houver um arquivo de backup, restaura os dados
    if backup_file and os.path.exists(backup_file):
        print(f"\n🔄 Restaurando banco de dados a partir de {backup_file}...")
        cmd = f'psql -h localhost -p 5432 -U postgres -d {db_name} -f "{backup_file}"'
        success, _ = run_command(cmd, f"Restaurando banco de dados {db_name}", env=env)
        
        if not success:
            print("⚠️  Ocorreram erros durante a restauração do backup.")
            print(f"   Você pode tentar restaurar manualmente com o comando:")
            print(f"   psql -h localhost -p 5432 -U postgres -d {db_name} -f \"{backup_file}\"")
    
    return True

def main():
    print("""
    🛠️  CORREÇÃO DE CODIFICAÇÃO DO BANCO DE DADOS
    ===========================================
    Este script irá ajudar a corrigir problemas de codificação no banco de dados PostgreSQL.
    """)
    
    # Verifica se o PostgreSQL está acessível
    if not check_postgres_connection():
        sys.exit(1)
    
    # Solicita a senha do PostgreSQL
    password = get_postgres_password()
    
    # Nome do banco de dados
    db_name = "apostapro_db"
    
    # 1. Faz backup do banco de dados atual
    backup_file = backup_database(db_name, password)
    
    # 2. Recria o banco de dados com a codificação correta
    if recreate_database(db_name, password, backup_file):
        print("\n✅ Processo concluído com sucesso!")
        if backup_file:
            print(f"   Backup salvo em: {backup_file}")
        print("   O banco de dados foi recriado com codificação UTF-8")
    else:
        print("\n❌ Ocorreu um erro durante o processo. Verifique as mensagens acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
