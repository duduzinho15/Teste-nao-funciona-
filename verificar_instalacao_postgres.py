#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a instalação e configuração do PostgreSQL no Windows
"""
import os
import sys
import subprocess
import re

def executar_comando(comando):
    """Executa um comando no shell e retorna a saída"""
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando: {e}")
        if e.stderr:
            print(f"Mensagem de erro: {e.stderr}")
        return None

def verificar_servico_postgres():
    """Verifica se o serviço do PostgreSQL está em execução"""
    print("\n🔍 Verificando status do serviço PostgreSQL...")
    
    # Tenta encontrar o nome do serviço PostgreSQL
    resultado = subprocess.run(
        'sc query | findstr /i "postgres"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    if resultado.returncode == 0 and resultado.stdout.strip():
        print("✅ Serviço PostgreSQL encontrado:")
        print(resultado.stdout)
        
        # Verifica se o serviço está rodando
        if "RUNNING" in resultado.stdout.upper():
            print("✅ O serviço PostgreSQL está em execução.")
            return True
        else:
            print("⚠️ O serviço PostgreSQL NÃO está em execução.")
            return False
    else:
        print("❌ Nenhum serviço PostgreSQL encontrado.")
        return False

def verificar_instalacao_postgres():
    """Verifica se o PostgreSQL está instalado no sistema"""
    print("🔍 Verificando instalação do PostgreSQL...")
    
    # Verifica diretórios comuns de instalação no Windows
    diretorios_comuns = [
        os.environ.get('ProgramFiles'),
        os.environ.get('ProgramFiles(x86)'),
        os.environ.get('ProgramData'),
        r"C:\Program Files\PostgreSQL",
        r"C:\Program Files (x86)\PostgreSQL",
        r"C:\PostgreSQL"
    ]
    
    encontrado = False
    for diretorio in diretorios_comuns:
        if not diretorio:
            continue
            
        if os.path.exists(diretorio):
            # Verifica se há pastas que começam com 'PostgreSQL' ou 'Postgres'
            for item in os.listdir(diretorio):
                caminho_completo = os.path.join(diretorio, item)
                if os.path.isdir(caminho_completo) and 'postgres' in item.lower():
                    print(f"✅ PostgreSQL encontrado em: {caminho_completo}")
                    encontrado = True
                    
                    # Tenta encontrar o executável psql
                    for root, dirs, files in os.walk(caminho_completo):
                        if 'psql.exe' in files:
                            psql_path = os.path.join(root, 'psql.exe')
                            print(f"  - psql.exe encontrado em: {psql_path}")
                            
                            # Tenta obter a versão do PostgreSQL
                            try:
                                versao = subprocess.check_output(
                                    f'"{psql_path}" --version',
                                    shell=True,
                                    stderr=subprocess.STDOUT,
                                    text=True
                                )
                                print(f"  - {versao.strip()}")
                            except:
                                pass
    
    if not encontrado:
        print("❌ PostgreSQL não encontrado nos diretórios comuns.")
    
    return encontrado

def verificar_variaveis_ambiente():
    """Verifica as variáveis de ambiente relacionadas ao PostgreSQL"""
    print("\n🔍 Verificando variáveis de ambiente...")
    
    variaveis = [
        'PGDATA', 'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD',
        'PGDATABASE', 'PGSERVICE', 'PGSSLMODE', 'PGREQUIRESSL'
    ]
    
    encontradas = False
    for var in variaveis:
        valor = os.environ.get(var)
        if valor:
            print(f"✅ {var} = {valor}")
            encontradas = True
    
    if not encontradas:
        print("ℹ️ Nenhuma variável de ambiente do PostgreSQL encontrada.")

def verificar_arquivo_pg_hba():
    """Tenta localizar e verificar o arquivo pg_hba.conf"""
    print("\n🔍 Procurando por arquivo pg_hba.conf...")
    
    # Verifica o diretório de dados do PostgreSQL
    diretorio_dados = os.environ.get('PGDATA')
    locais_comuns = [
        diretorio_dados,
        r"C:\Program Files\PostgreSQL\*\data",
        r"C:\Program Files (x86)\PostgreSQL\*\data",
        r"C:\PostgreSQL\*\data"
    ]
    
    encontrado = False
    for local in locais_comuns:
        if not local:
            continue
            
        # Expande o caminho com curinga
        from glob import glob
        for caminho in glob(local):
            caminho_hba = os.path.join(caminho, 'pg_hba.conf')
            if os.path.isfile(caminho_hba):
                print(f"✅ Arquivo pg_hba.conf encontrado em: {caminho_hba}")
                encontrado = True
                
                # Exibe as primeiras linhas do arquivo
                try:
                    with open(caminho_hba, 'r', encoding='utf-8', errors='replace') as f:
                        print("\nConteúdo do pg_hba.conf (primeiras 20 linhas):")
                        print("-" * 50)
                        for i, linha in enumerate(f):
                            if i >= 20:  # Limita a 20 linhas
                                print("... (arquivo continua)")
                                break
                            print(linha.rstrip())
                        print("-" * 50)
                except Exception as e:
                    print(f"❌ Erro ao ler o arquivo pg_hba.conf: {e}")
    
    if not encontrado:
        print("❌ Arquivo pg_hba.conf não encontrado nos locais comuns.")

def verificar_conexao_psql():
    """Tenta conectar ao PostgreSQL usando psql"""
    print("\n🔍 Testando conexão com psql...")
    
    # Tenta encontrar o psql no PATH
    try:
        resultado = subprocess.run(
            'where psql',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if resultado.returncode == 0 and resultado.stdout.strip():
            psql_path = resultado.stdout.split('\n')[0].strip()
            print(f"✅ psql encontrado em: {psql_path}")
            
            # Tenta conectar ao banco de dados
            print("\nTentando conectar ao banco de dados 'postgres'...")
            try:
                # Usa variáveis de ambiente para autenticação se disponíveis
                comando = 'psql -U postgres -d postgres -c "SELECT version();"'
                resultado = subprocess.run(
                    comando,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if resultado.returncode == 0:
                    print("✅ Conexão bem-sucedida!")
                    print("\nSaída do comando 'SELECT version()':")
                    print(resultado.stdout)
                    return True
                else:
                    print(f"❌ Falha na conexão. Código de saída: {resultado.returncode}")
                    if resultado.stderr:
                        print("\nMensagem de erro:")
                        print(resultado.stderr)
            except Exception as e:
                print(f"❌ Erro ao tentar conectar: {e}")
        else:
            print("❌ psql não encontrado no PATH.")
            print("Certifique-se de que o diretório bin do PostgreSQL está no PATH do sistema.")
    except Exception as e:
        print(f"❌ Erro ao procurar por psql: {e}")
    
    return False

def main():
    """Função principal"""
    print("=== Verificador de Instalação do PostgreSQL no Windows ===\n")
    
    # Verifica se está rodando como administrador
    try:
        import ctypes
        admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not admin:
            print("⚠️  Este script deve ser executado como administrador para algumas verificações.")
    except:
        pass
    
    # Executa as verificações
    verificar_instalacao_postgres()
    verificar_servico_postgres()
    verificar_variaveis_ambiente()
    verificar_arquivo_pg_hba()
    verificar_conexao_psql()
    
    print("\n✅ Verificação concluída.")

if __name__ == "__main__":
    main()
