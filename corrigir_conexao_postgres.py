import os
import subprocess
import sys
import psycopg2
from psycopg2 import sql

def executar_comando(comando, mensagem_erro=None):
    """Executa um comando no shell e retorna True se for bem-sucedido"""
    try:
        print(f"🚀 Executando: {comando}")
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado.stdout:
            print(f"✅ Saída: {resultado.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        if mensagem_erro:
            print(f"❌ {mensagem_erro}")
        print(f"   Erro: {e.stderr.strip() if e.stderr else 'Sem mensagem de erro'}")
        return False

def verificar_servico_postgres():
    """Verifica se o serviço do PostgreSQL está em execução"""
    print("\n🔍 Verificando status do serviço PostgreSQL...")
    return executar_comando(
        'Get-Service -Name postgresql* | Select-Object Name, Status',
        "Não foi possível verificar o status do serviço PostgreSQL."
    )

def verificar_conexao_tcp():
    """Verifica se é possível conectar ao PostgreSQL via TCP/IP"""
    print("\n🔍 Testando conexão TCP/IP com o PostgreSQL...")
    try:
        # Tentar conectar ao banco de dados 'postgres' primeiro
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="postgres",
            user="postgres",
            password="postgres",
            connect_timeout=5
        )
        print("✅ Conexão TCP/IP bem-sucedida!")
        
        # Verificar versão do PostgreSQL
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            print(f"📊 {cur.fetchone()[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão TCP/IP: {e}")
        return False

def verificar_arquivo_pg_hba():
    """Verifica as configurações do arquivo pg_hba.conf"""
    print("\n🔍 Verificando configurações do pg_hba.conf...")
    
    # Localização típica do pg_hba.conf no Windows
    locais_pg_hba = [
        os.path.join(os.environ.get('PGDATA', ''), 'pg_hba.conf'),
        'C:\\Program Files\\PostgreSQL\\17\\data\\pg_hba.conf',
        'C:\\Program Files (x86)\\PostgreSQL\\17\\data\\pg_hba.conf',
        'C:\\Program Files\\PostgreSQL\\16\\data\\pg_hba.conf',
        'C:\\Program Files (x86)\\PostgreSQL\\16\\data\\pg_hba.conf',
    ]
    
    pg_hba_path = None
    for path in locais_pg_hba:
        if os.path.exists(path):
            pg_hba_path = path
            break
    
    if not pg_hba_path:
        print("❌ Arquivo pg_hba.conf não encontrado nos locais comuns.")
        return False
    
    print(f"📄 Arquivo pg_hba.conf encontrado em: {pg_hba_path}")
    
    # Verificar se há entradas para conexão TCP/IP
    with open(pg_hba_path, 'r', encoding='utf-8', errors='replace') as f:
        linhas = f.readlines()
    
    entradas_tcp = [linha for linha in linhas if 'host' in linha and '127.0.0.1' in linha]
    
    if not entradas_tcp:
        print("⚠️  Não foram encontradas entradas para conexão TCP/IP (host 127.0.0.1) no pg_hba.conf")
        return False
    
    print("✅ Entradas TCP/IP encontradas no pg_hba.conf:")
    for entrada in entradas_tcp:
        print(f"   - {entrada.strip()}")
    
    return True

def verificar_postgresql_conf():
    """Verifica as configurações do postgresql.conf"""
    print("\n🔍 Verificando configurações do postgresql.conf...")
    
    # Localização típica do postgresql.conf no Windows
    locais_conf = [
        os.path.join(os.environ.get('PGDATA', ''), 'postgresql.conf'),
        'C:\\Program Files\\PostgreSQL\\17\\data\\postgresql.conf',
        'C:\\Program Files (x86)\\PostgreSQL\\17\\data\\postgresql.conf',
        'C:\\Program Files\\PostgreSQL\\16\\data\\postgresql.conf',
        'C:\\Program Files (x86)\\PostgreSQL\\16\\data\\postgresql.conf',
    ]
    
    conf_path = None
    for path in locais_conf:
        if os.path.exists(path):
            conf_path = path
            break
    
    if not conf_path:
        print("❌ Arquivo postgresql.conf não encontrado nos locais comuns.")
        return False
    
    print(f"📄 Arquivo postgresql.conf encontrado em: {conf_path}")
    
    # Verificar configurações importantes
    with open(conf_path, 'r', encoding='utf-8', errors='replace') as f:
        linhas = f.readlines()
    
    configs_importantes = {
        'listen_addresses': "'*'",
        'port': '5432',
        'max_connections': '100',
        'shared_buffers': '128MB',
        'dynamic_shared_memory_type': 'windows',
    }
    
    configs_encontradas = {}
    
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue
            
        for config in configs_importantes:
            if linha.startswith(f"{config} "):
                configs_encontradas[config] = linha
    
    print("\n🔧 Configurações atuais:")
    for config, valor_padrao in configs_importantes.items():
        if config in configs_encontradas:
            print(f"✅ {configs_encontradas[config]}")
        else:
            print(f"⚠️  {config} não encontrado (deveria ser {config} = {valor_padrao})")
    
    return True

def reiniciar_servico_postgres():
    """Reinicia o serviço do PostgreSQL"""
    print("\n🔄 Reiniciando o serviço PostgreSQL...")
    return executar_comando(
        'Restart-Service -Name postgresql* -Force',
        "Não foi possível reiniciar o serviço PostgreSQL."
    )

def main():
    print("""
🛠️  Ferramenta de Diagnóstico e Correção de Conexão PostgreSQL no Windows
""" + "=" * 70)
    
    # 1. Verificar se o serviço está rodando
    if not verificar_servico_postgres():
        print("\n❌ O serviço PostgreSQL não está em execução. Iniciando o serviço...")
        executar_comando('Start-Service -Name postgresql*', "Não foi possível iniciar o serviço PostgreSQL.")
    
    # 2. Verificar configurações do pg_hba.conf
    verificar_arquivo_pg_hba()
    
    # 3. Verificar configurações do postgresql.conf
    verificar_postgresql_conf()
    
    # 4. Reiniciar o serviço para aplicar as configurações
    if reiniciar_servico_postgres():
        print("\n🔄 Aguardando 5 segundos para o serviço reiniciar...")
        import time
        time.sleep(5)
    
    # 5. Testar conexão TCP/IP
    if verificar_conexao_tcp():
        print("\n✅ Configuração de conexão TCP/IP está funcionando corretamente!")
    else:
        print("\n❌ Ainda há problemas com a conexão TCP/IP. Verifique as configurações acima.")
    
    print("\n📌 Próximos passos:")
    print("1. Verifique se o firewall não está bloqueando a porta 5432")
    print("2. Confirme se o usuário 'postgres' tem permissão para conectar")
    print("3. Tente conectar usando o comando: psql -h localhost -p 5432 -U postgres")
    print("4. Se necessário, ajuste manualmente os arquivos de configuração")
    print("   - pg_hba.conf: Adicione 'host all all 127.0.0.1/32 md5'")
    print("   - postgresql.conf: Defina 'listen_addresses = '*'")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")
