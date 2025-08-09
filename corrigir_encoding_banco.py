import os
import subprocess
import sys
import psycopg2
from psycopg2 import sql

def executar_comando_sql(comando, dbname='postgres', user='postgres', password='Canjica@@2025'):
    """Executa um comando SQL usando psql"""
    try:
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', user,
            '-d', dbname,
            '-c', comando
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='latin1',  # Usar latin1 para evitar erros de decodificação
            errors='replace',
            env=env
        )
        
        if resultado.returncode != 0:
            print(f"❌ Erro ao executar comando: {resultado.stderr}")
            return None
            
        return resultado.stdout
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def verificar_encoding_banco():
    """Verifica o encoding atual do banco de dados"""
    print("\n🔍 Verificando encoding do banco de dados...")
    
    # Obter lista de bancos de dados
    resultado = executar_comando_sql(
        "SELECT datname, pg_encoding_to_char(encoding), datcollate, datctype FROM pg_database;"
    )
    
    if not resultado:
        print("❌ Não foi possível obter informações dos bancos de dados")
        return False
        
    print("\n📊 Bancos de dados e seus encodings:")
    print(resultado)
    
    return True

def corrigir_encoding_banco():
    """Tenta corrigir o encoding do banco de dados"""
    print("\n🔄 Iniciando correção de encoding do banco de dados...")
    
    # 1. Criar um novo banco de dados com encoding correto
    print("\n🔧 Criando novo banco de dados com encoding correto...")
    novo_banco = "apostapro_db_utf8"
    
    # Verificar se o banco já existe
    resultado = executar_comando_sql(
        f"SELECT 1 FROM pg_database WHERE datname = '{novo_banco}';"
    )
    
    if resultado and '1' in resultado:
        print(f"ℹ️  O banco de dados '{novo_banco}' já existe. Removendo...")
        executar_comando_sql(f"DROP DATABASE {novo_banco};")
    
    # Criar novo banco com encoding UTF8
    print(f"🔄 Criando novo banco de dados '{novo_banco}' com encoding UTF8...")
    comando_criar = f"""
    CREATE DATABASE {novo_banco}
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'Portuguese_Brazil.1252'
    LC_CTYPE = 'Portuguese_Brazil.1252'
    TEMPLATE = template0;
    """
    
    if not executar_comando_sql(comando_criar):
        print("❌ Falha ao criar novo banco de dados")
        return False
    
    print(f"✅ Novo banco de dados '{novo_banco}' criado com sucesso!")
    
    # 2. Exportar e importar dados com pg_dump/pg_restore
    print("\n🔄 Exportando e importando dados com pg_dump/pg_restore...")
    
    # Exportar dados do banco antigo
    arquivo_dump = "dump_apostapro_db.sql"
    print(f"💾 Exportando dados para {arquivo_dump}...")
    
    try:
        with open(arquivo_dump, 'w', encoding='latin1') as f:
            subprocess.run(
                ['pg_dump', '-h', 'localhost', '-p', '5432', '-U', 'postgres', 'apostapro_db'],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding='latin1',
                errors='replace'
            )
        
        print(f"✅ Dados exportados para {arquivo_dump}")
        
        # Importar dados para o novo banco
        print(f"🔄 Importando dados para {novo_banco}...")
        
        with open(arquivo_dump, 'r', encoding='latin1', errors='replace') as f:
            subprocess.run(
                ['psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', novo_banco],
                stdin=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding='latin1',
                errors='replace'
            )
        
        print(f"✅ Dados importados para {novo_banco}")
        
    except Exception as e:
        print(f"❌ Erro durante exportação/importação: {e}")
        return False
    
    print("\n✅ Processo de correção de encoding concluído!")
    print(f"\n📌 Próximos passos:")
    print(f"1. Verifique o conteúdo do banco {novo_banco}")
    print("2. Se estiver tudo correto, você pode remover o banco antigo e renomear o novo")
    print("3. Atualize as configurações da aplicação para usar o novo banco")
    
    return True

if __name__ == "__main__":
    print("""
🛠️  Ferramenta de Correção de Encoding do Banco de Dados PostgreSQL
""" + "=" * 70)
    
    # Verificar encoding atual
    if verificar_encoding_banco():
        # Oferecer opção para corrigir
        resposta = input("\nDeseja tentar corrigir o encoding do banco de dados? (s/n): ")
        if resposta.lower() == 's':
            corrigir_encoding_banco()
    
    input("\nPressione Enter para sair...")
