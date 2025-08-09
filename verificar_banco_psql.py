import subprocess
import os
import json

def executar_comando_psql(comando, dbname='postgres'):
    """Executa um comando SQL usando psql e retorna o resultado como JSON"""
    try:
        # Comando base
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', 'postgres',
            '-d', dbname,
            '-t',  # Apenas tuplas
            '-A',  # Sem alinhamento
            '-F', ',',  # Separador de campos
            '-X',  # Não ler ~/.psqlrc
            '-c', f"COPY (SELECT row_to_json(t) FROM ({comando}) t) TO STDOUT;"
        ]
        
        # Configurar ambiente
        env = os.environ.copy()
        env['PGPASSWORD'] = '123456789'
        env['PGCLIENTENCODING'] = 'LATIN1'  # Forçar LATIN1 para evitar erros de codificação
        
        # Executar comando
        resultado = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='latin1',
            errors='replace',
            env=env
        )
        
        if resultado.returncode != 0:
            print(f"❌ Erro ao executar comando: {resultado.stderr}")
            return None
            
        # Processar resultado
        linhas = [linha.strip() for linha in resultado.stdout.split('\n') if linha.strip()]
        dados = [json.loads(linha) for linha in linhas if linha]
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def verificar_tabelas():
    """Verifica as tabelas no banco de dados"""
    print("\n🔍 Verificando tabelas no banco de dados...")
    
    # Obter lista de tabelas
    tabelas = executar_comando_psql(
        "SELECT table_name, table_type "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public'"
    )
    
    if tabelas is None:
        print("❌ Não foi possível obter a lista de tabelas")
        return
        
    if not tabelas:
        print("ℹ️  Nenhuma tabela encontrada no banco de dados.")
        return
        
    print(f"\n📋 Tabelas encontradas ({len(tabelas)}):")
    
    for tabela in tabelas:
        nome = tabela['table_name']
        tipo = tabela['table_type']
        
        print(f"\n📊 Tabela: {nome} ({tipo})")
        
        # Contar registros
        contagem = executar_comando_psql(f"SELECT COUNT(*) AS total FROM \"{nome}\"")
        if contagem and len(contagem) > 0:
            print(f"   📝 Total de registros: {contagem[0]['count']}")
            
            # Se tiver poucos registros, mostrar alguns dados
            if contagem[0]['count'] > 0 and contagem[0]['count'] <= 5:
                dados = executar_comando_psql(f"SELECT * FROM \"{nome}\" LIMIT 3")
                if dados:
                    print("   📄 Dados de exemplo:")
                    for i, linha in enumerate(dados[:3], 1):
                        print(f"      {i}. {str(linha)[:100]}...")

def verificar_encoding():
    """Verifica o encoding do banco de dados"""
    print("\n🔍 Verificando encoding do banco de dados...")
    
    # Obter encoding do banco
    resultado = executar_comando_psql(
        "SELECT datname, pg_encoding_to_char(encoding) AS encoding, datcollate, datctype "
        "FROM pg_database "
        "WHERE datname = current_database()"
    )
    
    if resultado and len(resultado) > 0:
        print("\n📊 Configurações de encoding:")
        for linha in resultado:
            print(f"   - Banco: {linha['datname']}")
            print(f"     Encoding: {linha['encoding']}")
            print(f"     Collation: {linha['datcollate']}")
            print(f"     Ctype: {linha['datctype']}")
    else:
        print("❌ Não foi possível obter informações de encoding")

if __name__ == "__main__":
    print("\n🔄 Verificação Completa do Banco de Dados")
    print("=" * 50)
    
    # Verificar encoding primeiro
    verificar_encoding()
    
    # Verificar tabelas
    verificar_tabelas()
    
    input("\nPressione Enter para sair...")
