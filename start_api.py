"""
SCRIPT DE INICIALIZAÇÃO DA API FASTAPI
======================================

Script para inicializar a API RESTful do ApostaPro.
Verifica dependências, configurações e inicia o servidor.

Uso:
    python start_api.py

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'psycopg2',
        'python-dotenv',
        'python-jose',
        'passlib',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependências faltando:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Instale com: pip install -r requirements_api.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def check_environment():
    """Verifica se o arquivo .env existe e tem as configurações necessárias."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        print("💡 Crie o arquivo .env com as configurações necessárias")
        return False
    
    # Verificar configurações essenciais
    required_vars = [
        'DB_HOST',
        'DB_NAME', 
        'DB_USER',
        'API_KEY'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variáveis de ambiente faltando no .env:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Configurações do ambiente verificadas")
    return True

def check_database():
    """Verifica conectividade com o banco de dados."""
    try:
        from Coleta_de_dados.database import test_connection
        
        if test_connection():
            print("✅ Conectividade com o banco verificada")
            return True
        else:
            print("❌ Falha na conectividade com o banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def main():
    """Função principal para inicializar a API."""
    print("🚀 INICIALIZANDO API FASTAPI DO APOSTAPRO")
    print("=" * 50)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Verificações pré-inicialização
    print("\n🔍 VERIFICAÇÕES PRÉ-INICIALIZAÇÃO:")
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    if not check_database():
        print("⚠️ Aviso: Problemas na conectividade do banco")
        print("   A API será iniciada, mas alguns endpoints podem falhar")
    
    print("\n✅ TODAS AS VERIFICAÇÕES PASSARAM")
    print("=" * 50)
    
    # Inicializar API
    try:
        from api import run_server
        print("\n🎉 Iniciando servidor da API...")
        run_server()
        
    except KeyboardInterrupt:
        print("\n\n🔄 Servidor interrompido pelo usuário")
        print("✅ API finalizada com sucesso")
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
