import psycopg2
from psycopg2 import sql
import sys
import os

def testar_conexao_avancada():
    """Testa diferentes abordagens para conectar ao PostgreSQL"""
    print("🔍 Iniciando teste avançado de conexão ao PostgreSQL...")
    
    # Lista de configurações para testar
    configs = [
        {
            'name': 'Conexão direta com tratamento de erros',
            'host': 'localhost',
            'port': 5432,
            'dbname': 'postgres',  # Primeiro tentamos conectar ao banco padrão
            'user': 'postgres',
            'password': 'postgres',
            'client_encoding': 'UTF8',
            'options': '-c client_encoding=UTF8',
            'connect_timeout': 5
        },
        {
            'name': 'Conexão sem especificar encoding',
            'host': 'localhost',
            'port': 5432,
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'connect_timeout': 5
        },
        {
            'name': 'Conexão via Unix socket (Windows)',
            'host': '/var/run/postgresql',  # Caminho típico para socket no Windows
            'port': 5432,
            'dbname': 'postgres',
            'user': 'postgres',
            'password': 'postgres',
            'connect_timeout': 5
        }
    ]
    
    for config in configs:
        # Extrair o nome da configuração e remover do dicionário de conexão
        config_name = config.pop('name', 'Configuração sem nome')
        print(f"\n🔧 Testando configuração: {config_name}")
        print(f"📌 Parâmetros: { {k: v for k, v in config.items() if k != 'password'} }")
        
        try:
            # Tentar conexão com tratamento de erros específico para encoding
            conn = psycopg2.connect(**{k: v for k, v in config.items() if k != 'name'})
            print("✅ Conexão bem-sucedida!")
            
            # Obter informações do servidor
            with conn.cursor() as cur:
                # Versão do PostgreSQL
                cur.execute("SELECT version();")
                print(f"📊 {cur.fetchone()[0]}")
                
                # Encoding atual
                cur.execute("SHOW server_encoding;")
                print(f"🔤 Server Encoding: {cur.fetchone()[0]}")
                
                cur.execute("SHOW client_encoding;")
                print(f"🔤 Client Encoding: {cur.fetchone()[0]}")
                
                # Listar bancos de dados
                cur.execute("SELECT datname, pg_encoding_to_char(encoding), datcollate, datctype FROM pg_database;")
                print("\n📊 Bancos de dados:")
                for db in cur.fetchall():
                    print(f" - {db[0]} (Encoding: {db[1]}, Collate: {db[2]}, Ctype: {db[3]})")
            
            conn.close()
            return True
            
        except UnicodeDecodeError as e:
            print(f"❌ Erro de decodificação: {e}")
            print("   Tentando com tratamento de erros...")
            
            try:
                # Tentar novamente com tratamento de erros de decodificação
                conn = psycopg2.connect(**config)
                conn.set_client_encoding('UTF8')
                
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    print(f"✅ Conexão bem-sucedida com tratamento de erros!")
                    print(f"📊 {cur.fetchone()[0]}")
                
                conn.close()
                return True
                
            except Exception as inner_e:
                print(f"❌ Falha mesmo com tratamento de erros: {inner_e}")
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
    
    print("\n❌ Nenhuma das configurações de conexão funcionou.")
    return False

def verificar_servico_windows():
    """Verifica o status do serviço PostgreSQL no Windows"""
    print("\n🔍 Verificando status do serviço PostgreSQL no Windows...")
    
    try:
        # Usar o comando 'sc' para verificar o status do serviço
        service_name = "postgresql-x64-17"  # Nome padrão para PostgreSQL 17
        
        # Verificar se o serviço existe
        result = os.popen(f'sc query {service_name}').read()
        
        if '1060' in result:
            print(f"❌ O serviço '{service_name}' não foi encontrado.")
            print("   Tente executar como administrador ou verifique o nome do serviço.")
            return False
            
        print(f"✅ Serviço encontrado: {service_name}")
        
        # Verificar status
        if 'RUNNING' in result:
            print("✅ O serviço está em execução.")
        else:
            print("⚠️  O serviço NÃO está em execução.")
            print("   Para iniciar o serviço, execute como administrador:")
            print(f"   net start {service_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar o serviço: {e}")
        return False

if __name__ == "__main__":
    print("""
🛠️  Ferramenta Avançada de Diagnóstico de Conexão PostgreSQL
""" + "=" * 70)
    
    # Verificar status do serviço no Windows
    verificar_servico_windows()
    
    # Testar diferentes configurações de conexão
    if not testar_conexao_avancada():
        print("\n🔧 Recomendações:")
        print("1. Verifique se o serviço PostgreSQL está em execução")
        print("2. Confirme se o usuário/senha estão corretos")
        print("3. Tente conectar manualmente com: psql -h localhost -p 5432 -U postgres")
        print("4. Verifique se a porta 5432 não está bloqueada pelo firewall")
        print("5. Consulte os logs do PostgreSQL para erros de inicialização")
    
    input("\nPressione Enter para sair...")
