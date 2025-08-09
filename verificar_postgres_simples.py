#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para verificar a instalação do PostgreSQL no Windows
"""
import os
import subprocess
import sys

def executar_comando(comando):
    """Executa um comando e retorna a saída"""
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
        return f"ERRO: {e.stderr}" if e.stderr else f"ERRO: {e}"
    except Exception as e:
        return f"ERRO: {str(e)}"

def verificar_servico_postgres():
    """Verifica se o serviço do PostgreSQL está em execução"""
    print("\n🔍 Verificando status do serviço PostgreSQL...")
    
    # Comando para listar serviços do PostgreSQL
    comando = 'sc query | findstr /i "postgres"'
    resultado = executar_comando(comando)
    
    if resultado and not resultado.startswith("ERRO"):
        print("✅ Serviço PostgreSQL encontrado:")
        print(resultado)
        
        # Verifica se o serviço está rodando
        if "RUNNING" in resultado.upper():
            print("✅ O serviço PostgreSQL está em execução.")
            return True
        else:
            print("⚠️  O serviço PostgreSQL NÃO está em execução.")
            return False
    else:
        print("❌ Nenhum serviço PostgreSQL encontrado.")
        return False

def verificar_psql():
    """Verifica se o comando psql está disponível"""
    print("\n🔍 Verificando instalação do cliente psql...")
    
    # Tenta encontrar o caminho do psql
    comando = 'where psql' if os.name == 'nt' else 'which psql'
    resultado = executar_comando(comando)
    
    if resultado and not resultado.startswith("ERRO"):
        psql_path = resultado.split('\n')[0].strip()
        print(f"✅ psql encontrado em: {psql_path}")
        
        # Tenta obter a versão
        versao = executar_comando(f'"{psql_path}" --version')
        if versao and not versao.startswith("ERRO"):
            print(f"✅ {versao.strip()}")
        else:
            print("⚠️  Não foi possível obter a versão do psql")
        
        return True
    else:
        print("❌ psql não encontrado no PATH.")
        print("   Certifique-se de que o diretório bin do PostgreSQL está no PATH do sistema.")
        return False

def verificar_variaveis_ambiente():
    """Verifica as variáveis de ambiente do PostgreSQL"""
    print("\n🔍 Verificando variáveis de ambiente do PostgreSQL...")
    
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
        print("ℹ️  Nenhuma variável de ambiente do PostgreSQL encontrada.")

def testar_conexao():
    """Tenta conectar ao PostgreSQL"""
    print("\n🔍 Testando conexão com o PostgreSQL...")
    
    # Tenta encontrar o psql
    comando = 'where psql' if os.name == 'nt' else 'which psql'
    resultado = executar_comando(comando)
    
    if resultado and not resultado.startswith("ERRO"):
        psql_path = resultado.split('\n')[0].strip()
        
        # Tenta conectar usando psql
        comando = f'"{psql_path}" -U postgres -c "SELECT version();" -t'
        resultado = executar_comando(comando)
        
        if resultado and not resultado.startswith("ERRO"):
            print("✅ Conexão bem-sucedida!")
            print(f"   {resultado.strip()}")
            return True
        else:
            print("❌ Falha na conexão com o PostgreSQL:")
            print(f"   {resultado}")
            return False
    else:
        print("ℹ️  psql não encontrado, pulando teste de conexão.")
        return False

def main():
    """Função principal"""
    print("=== Verificador de Instalação do PostgreSQL ===\n")
    
    # Executa as verificações
    verificar_servico_postgres()
    verificar_psql()
    verificar_variaveis_ambiente()
    testar_conexao()
    
    print("\n✅ Verificação concluída.")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")
