import os
import sys
import subprocess
from getpass import getpass

def executar_comando_sql(comando, user='postgres', password=None):
    """Executa um comando SQL usando psql."""
    try:
        # Configurar variáveis de ambiente para o psql
        env = os.environ.copy()
        if password:
            env['PGPASSWORD'] = password
        
        # Executar o comando psql
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', user,
            '-d', 'postgres',
            '-c', comando,
            '-v', 'ON_ERROR_STOP=1'
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='latin1'  # Forçar codificação latin1 para evitar erros
        )
        
        if result.returncode != 0:
            print(f"❌ Erro ao executar comando: {result.stderr}")
            return None
            
        return result.stdout
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def verificar_encoding():
    """Verifica o encoding atual do PostgreSQL."""
    print("🔍 Verificando configurações de encoding do PostgreSQL...")
    
    # Obter usuário e senha
    user = input("Usuário (padrão: postgres): ") or "postgres"
    password = getpass("Senha: ")
    
    # Verificar versão do PostgreSQL
    print("\n📊 Informações do servidor:")
    version = executar_comando_sql("SELECT version();", user, password)
    if version:
        print(version.strip())
    
    # Verificar encoding do servidor
    print("\n🔤 Configurações de encoding:")
    encoding = executar_comando_sql(
        "SHOW server_encoding;", user, password
    )
    if encoding:
        print(f"- Server Encoding: {encoding.strip()}")
    
    client_encoding = executar_comando_sql(
        "SHOW client_encoding;", user, password
    )
    if client_encoding:
        print(f"- Client Encoding: {client_encoding.strip()}")
    
    lc_collate = executar_comando_sql(
        "SHOW lc_collate;", user, password
    )
    if lc_collate:
        print(f"- LC_COLLATE: {lc_collate.strip()}")
    
    lc_ctype = executar_comando_sql(
        "SHOW lc_ctype;", user, password
    )
    if lc_ctype:
        print(f"- LC_CTYPE: {lc_ctype.strip()}")
    
    # Verificar bancos de dados
    print("\n📊 Bancos de dados existentes:")
    dbs = executar_comando_sql(
        "SELECT datname, pg_encoding_to_char(encoding) FROM pg_database;",
        user, password
    )
    if dbs:
        print(dbs.strip())

def corrigir_encoding():
    """Tenta corrigir problemas de encoding no PostgreSQL."""
    print("\n🛠️  Iniciando correção de encoding...")
    
    # Obter credenciais
    user = input("Usuário (padrão: postgres): ") or "postgres"
    password = getpass("Senha: ")
    
    # 1. Verificar se o banco de dados existe
    print("\n🔍 Verificando banco de dados 'apostapro_db'...")
    db_exists = executar_comando_sql(
        "SELECT 1 FROM pg_database WHERE datname = 'apostapro_db';",
        user, password
    )
    
    if db_exists and '1' in db_exists:
        print("ℹ️  O banco de dados 'apostapro_db' já existe.")
        
        # Verificar se existem conexões ativas
        print("\n🔌 Verificando conexões ativas...")
        connections = executar_comando_sql(
            "SELECT pid, application_name, state FROM pg_stat_activity WHERE datname = 'apostapro_db';",
            user, password
        )
        
        if connections and 'pid' in connections:
            print("⚠️  Existem conexões ativas no banco de dados. Desconectando...")
            executar_comando_sql(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'apostapro_db';",
                user, password
            )
        
        # Fazer backup do banco de dados
        print("\n💾 Fazendo backup do banco de dados...")
        backup_file = f"backup_apostapro_db_{os.getpid()}.sql"
        cmd = f'pg_dump -h localhost -p 5432 -U {user} -d apostapro_db -f {backup_file}'
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        try:
            subprocess.run(
                cmd,
                env=env,
                shell=True,
                check=True
            )
            print(f"✅ Backup salvo em: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Aviso: não foi possível fazer backup: {e}")
            if input("Deseja continuar mesmo assim? (s/N): ").lower() != 's':
                return
        
        # Remover o banco de dados existente
        print("\n🗑️  Removendo banco de dados existente...")
        executar_comando_sql(
            "DROP DATABASE IF EXISTS apostapro_db;",
            user, password
        )
    
    # 2. Criar um novo banco de dados com encoding correto
    print("\n🆕 Criando novo banco de dados com encoding correto...")
    executar_comando_sql(
        "CREATE DATABASE apostapro_db WITH ENCODING 'UTF8' LC_COLLATE 'Portuguese_Brazil.1252' LC_CTYPE 'Portuguese_Brazil.1252' TEMPLATE template0;",
        user, password
    )
    
    print("\n✅ Banco de dados 'apostapro_db' recriado com sucesso!")
    print("\n📌 Próximos passos:")
    print("1. Execute as migrações do Alembic para recriar as tabelas:")
    print("   alembic upgrade head")
    print("2. Importe os dados de volta para o banco")

def main():
    print("🛠️  Ferramenta de Diagnóstico e Correção de Encoding - PostgreSQL")
    print("=" * 70)
    
    while True:
        print("\n🔧 Menu Principal:")
        print("1. Verificar configurações de encoding")
        print("2. Corrigir problemas de encoding (recomendado)")
        print("3. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            verificar_encoding()
        elif opcao == '2':
            corrigir_encoding()
        elif opcao == '3':
            print("\n👋 Saindo...")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")
    
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    finally:
        input("\nPressione Enter para sair...")
