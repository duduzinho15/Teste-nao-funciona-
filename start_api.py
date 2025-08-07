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
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Configurar logging básico imediatamente
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    import importlib.util
    import sys
    
    # Mapeamento de pacotes para nomes de importação
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'sqlalchemy': 'sqlalchemy',
        'psycopg2_binary': 'psycopg2',  # Nome do pacote vs. nome do módulo
        'python_dotenv': 'dotenv',       # Nome do pacote vs. nome do módulo
        'python_jose': 'jose',           # Nome do pacote vs. nome do módulo
        'passlib': 'passlib',
        'psutil': 'psutil'
    }
    
    missing_packages = []
    
    print("\n🔍 Verificando dependências...")
    
    for package_name, import_name in required_packages.items():
        try:
            # Tenta importar o módulo
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                raise ImportError(f"Módulo {import_name} não encontrado")
                
            # Se chegou aqui, o módulo foi encontrado
            module = importlib.import_module(import_name)
            print(f"✅ {package_name} ({import_name}) encontrado em: {module.__file__}")
            
        except ImportError as e:
            print(f"❌ {package_name} ({import_name}) não encontrado: {e}")
            missing_packages.append(package_name.replace('_', '-'))
    
    if missing_packages:
        print("\n❌ Dependências faltando:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Instale com: pip install -r requirements_api.txt")
        return False
    
    print("\n✅ Todas as dependências estão instaladas")
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
        from Coleta_de_dados.database import db_manager
        
        if db_manager.test_connection():
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
        from api.config import get_api_settings
        settings = get_api_settings()
        
        print("\n🎉 Iniciando servidor da API...")
        print(f"📍 Host: {settings.api_host}:{settings.api_port}")
        print(f"🔧 Environment: {settings.environment}")
        print(f"🐛 Debug: {settings.debug}")
        print(f"📚 Docs: http://{settings.api_host}:{settings.api_port}/docs")
        
        # Executar o servidor diretamente com uvicorn
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload and settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🔄 Servidor interrompido pelo usuário")
        print("✅ API finalizada com sucesso")
        
    except Exception as e:
        print(f"\n❌ Erro ao inicializar API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
