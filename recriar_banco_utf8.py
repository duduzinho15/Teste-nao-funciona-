import psycopg2
import subprocess
import os
from getpass import getpass
import sys
from datetime import datetime

def conectar(host, port, user, password, dbname='postgres'):
    """Conecta ao servidor PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def verificar_banco_existe(conn, dbname):
    """Verifica se o banco de dados já existe"""
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        return cur.fetchone() is not None

def listar_collations_disponiveis(conn):
    """Lista todos os collations disponíveis no servidor"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT collname, collcollate, collctype 
            FROM pg_collation 
            WHERE collname LIKE '%portuguese%' OR collname LIKE '%pt_%' OR collname LIKE '%utf%'
            ORDER BY collname;
        """)
        return cur.fetchall()

def criar_backup_estrutura(conn, dbname, backup_dir='backups'):
    """Cria um backup da estrutura do banco de dados"""
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{dbname}_backup_{timestamp}.sql")
        
        print(f"\n💾 Criando backup da estrutura do banco '{dbname}'...")
        
        # Usar pg_dump para fazer o backup apenas da estrutura (sem dados)
        cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-U', conn.info.user,
            '-d', dbname,
            '--schema-only',
            '-f', backup_file
        ]
        
        # Configurar a senha como variável de ambiente
        env = os.environ.copy()
        env['PGPASSWORD'] = conn.info.password
        
        # Executar o comando pg_dump
        result = subprocess.run(
            cmd, 
            env=env, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print(f"⚠️  Aviso ao criar backup: {result.stderr}")
            return None
        
        print(f"✅ Backup salvo em: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"⚠️  Erro ao criar backup: {e}")
        return None

def criar_novo_banco(conn, dbname, template='template0', encoding='UTF8', 
                    lc_collate='Portuguese_Brazil.1252', lc_ctype='Portuguese_Brazil.1252'):
    """Cria um novo banco de dados com as configurações especificadas"""
    print(f"\n🔧 Criando novo banco de dados '{dbname}'...")
    print(f" - Template: {template}")
    print(f" - Encoding: {encoding}")
    print(f" - Collation: {lc_collate}")
    print(f" - Ctype: {lc_ctype}")
    
    try:
        with conn.cursor() as cur:
            # Desconectar todos os usuários do banco de dados existente
            if verificar_banco_existe(conn, dbname):
                print(f"\n🔌 Desconectando usuários do banco '{dbname}'...")
                cur.execute(f"""
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE datname = '{dbname}';
                """)
                
                print(f"🗑️  Removendo banco de dados existente '{dbname}'...")
                cur.execute(f'DROP DATABASE IF EXISTS "{dbname}";')
            
            # Criar um novo banco de dados com as configurações corretas
            print(f"🆕 Criando novo banco de dados...")
            cur.execute(f"""
                CREATE DATABASE "{dbname}"
                WITH 
                ENCODING = '{encoding}'
                LC_COLLATE = '{lc_collate}'
                LC_CTYPE = '{lc_ctype}'
                TEMPLATE = {template};
            """)
            
            print(f"✅ Banco de dados '{dbname}' criado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar o banco de dados: {e}")
        return False

def restaurar_estrutura(conn, dbname, backup_file):
    """Restaura a estrutura do banco de dados a partir de um arquivo de backup"""
    if not backup_file or not os.path.exists(backup_file):
        print("⚠️  Arquivo de backup não encontrado. Pulando restauração.")
        return False
    
    print(f"\n🔄 Restaurando estrutura do banco de dados a partir de {backup_file}...")
    
    try:
        # Usar psql para restaurar o backup
        cmd = [
            'psql',
            '-h', 'localhost',
            '-U', conn.info.user,
            '-d', dbname,
            '-f', backup_file
        ]
        
        # Configurar a senha como variável de ambiente
        env = os.environ.copy()
        env['PGPASSWORD'] = conn.info.password
        
        # Executar o comando psql
        result = subprocess.run(
            cmd, 
            env=env, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print(f"⚠️  Aviso ao restaurar backup: {result.stderr}")
            return False
        
        print("✅ Estrutura do banco de dados restaurada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar backup: {e}")
        return False

def main():
    print("🔄 Recriador de Banco de Dados PostgreSQL")
    print("=" * 50)
    
    # Configurações
    config = {
        'host': 'localhost',
        'port': '5432',
        'user': input("Usuário (padrão: postgres): ") or "postgres",
        'password': getpass("Senha: "),
        'dbname': 'apostapro_db',
        'template': 'template0',
        'encoding': 'UTF8',
        'lc_collate': 'Portuguese_Brazil.1252',
        'lc_ctype': 'Portuguese_Brazil.1252'
    }
    
    # Conectar ao banco de dados postgres
    print("\n🔌 Conectando ao servidor PostgreSQL...")
    conn = conectar(**{k: config[k] for k in ['host', 'port', 'user', 'password']})
    if not conn:
        sys.exit(1)
    
    # Listar collations disponíveis
    print("\n📋 Collations disponíveis no servidor:")
    collations = listar_collations_disponiveis(conn)
    
    if not collations:
        print("⚠️  Nenhum collation compatível encontrado. Usando padrão do sistema.")
    else:
        print("\nCollations disponíveis (recomendado: Portuguese_Brazil.1252):")
        for i, (coll, collate, ctype) in enumerate(collations, 1):
            print(f"{i}. {coll} (Collate: {collate}, Ctype: {ctype})")
        
        escolha = input("\nDigite o número do collate desejado (ou Enter para usar o padrão): ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(collations):
            coll_info = collations[int(escolha)-1]
            config['lc_collate'] = coll_info[1]  # collcollate
            config['lc_ctype'] = coll_info[2]    # collctype
            print(f"✅ Collation selecionado: {coll_info[0]}")
    
    # Criar backup da estrutura atual
    if verificar_banco_existe(conn, config['dbname']):
        backup_file = criar_backup_estrutura(conn, config['dbname'])
    else:
        print(f"\nℹ️  O banco de dados '{config['dbname']}' não existe. Será criado um novo.")
        backup_file = None
    
    # Confirmar operação
    print("\n" + "="*50)
    print("⚠️  ATENÇÃO: Esta operação irá APAGAR o banco de dados existente e criar um novo.")
    print("="*50)
    confirm = input("\nDeseja continuar? (s/N): ").strip().lower()
    if confirm != 's':
        print("\nOperação cancelada pelo usuário.")
        sys.exit(0)
    
    # Criar o novo banco de dados
    if criar_novo_banco(conn, **{k: config[k] for k in ['dbname', 'template', 'encoding', 'lc_collate', 'lc_ctype']}):
        # Restaurar a estrutura do backup, se disponível
        if backup_file:
            restaurar_estrutura(conn, config['dbname'], backup_file)
        
        print("\n✅ Processo concluído com sucesso!")
        print("\n📌 Próximos passos:")
        
        # Verificar se o Alembic está configurado
        if os.path.exists('alembic.ini') and os.path.exists('alembic'):
            print("1. Execute as migrações do Alembic para recriar as tabelas:")
            print("   alembic upgrade head")
        else:
            print("1. Migrações do Alembic não encontradas. Execute seus scripts de criação de tabelas manualmente.")
        
        print("\n2. Importe os dados de volta para o banco")
    else:
        print("\n❌ Falha ao recriar o banco de dados. Verifique as mensagens de erro acima.")

    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    finally:
        input("\nPressione Enter para sair...")
