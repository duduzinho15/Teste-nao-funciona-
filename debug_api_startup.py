"""
Script avançado de depuração para a inicialização da API FastAPI.
"""
import os
import sys
import logging
import traceback
from pathlib import Path

# Configuração de logging detalhada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def print_header(text):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"{text}")
    print("=" * 80)

def check_imports():
    """Verifica as importações necessárias."""
    print_header("🔍 VERIFICANDO IMPORTAÇÕES")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'pydantic',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'alembic'
    ]
    
    all_ok = True
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            logger.info(f"✅ {module} importado com sucesso")
        except ImportError as e:
            logger.error(f"❌ Falha ao importar {module}: {e}")
            all_ok = False
    
    return all_ok

def test_database_connection():
    """Testa a conexão com o banco de dados."""
    print_header("🧪 TESTANDO CONEXÃO COM O BANCO DE DADOS")
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.sql import text
        from dotenv import load_dotenv
        
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Obtém as configurações do banco de dados
        db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        
        logger.info(f"Conectando ao banco de dados: {db_url.replace(os.getenv('DB_PASSWORD'), '*****')}")
        
        # Cria a engine e testa a conexão
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"✅ Conexão bem-sucedida! Versão do PostgreSQL: {version}")
            
            # Verifica se as tabelas existem
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            
            """))
            tables = [row[0] for row in result]
            logger.info(f"✅ Tabelas encontradas: {', '.join(tables) if tables else 'Nenhuma tabela encontrada'}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Falha na conexão com o banco de dados: {e}")
        logger.debug(traceback.format_exc())
        return False

def test_api_creation():
    """Testa a criação da aplicação FastAPI."""
    print_header("🚀 TESTANDO CRIAÇÃO DA APLICAÇÃO FASTAPI")
    
    try:
        # Adiciona o diretório raiz ao path do Python
        project_root = str(Path(__file__).parent.absolute())
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Tenta importar o módulo principal
        try:
            from api.main import create_app
            logger.info("✅ Módulo api.main importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Falha ao importar api.main: {e}")
            logger.debug(traceback.format_exc())
            return False
        
        # Tenta criar a aplicação
        try:
            app = create_app()
            logger.info("✅ Aplicativo FastAPI criado com sucesso")
            
            # Lista as rotas disponíveis
            logger.info("\n🛣️  ROTAS DISPONÍVEIS:")
            for route in app.routes:
                if hasattr(route, 'methods'):
                    methods = ", ".join(route.methods)
                    logger.info(f"  {methods}: {route.path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar o aplicativo: {e}")
            logger.debug(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        logger.debug(traceback.format_exc())
        return False

def run_test_server():
    """Inicia um servidor de teste."""
    print_header("🌐 INICIANDO SERVIDOR DE TESTE")
    
    try:
        import uvicorn
        from api.main import create_app
        
        app = create_app()
        
        # Configuração do servidor
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", 8000))
        
        logger.info(f"Iniciando servidor em http://{host}:{port}")
        logger.info(f"Documentação disponível em: http://{host}:{port}/docs")
        logger.info("Pressione Ctrl+C para encerrar o servidor")
        
        # Inicia o servidor em uma thread separada
        import threading
        import time
        
        def run_server():
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="debug",
                access_log=True
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Aguarda um pouco para o servidor iniciar
        time.sleep(3)
        
        # Tenta acessar o endpoint de saúde
        try:
            import requests
            response = requests.get(f"http://{host}:{port}/api/v1/health")
            logger.info(f"✅ Endpoint de saúde retornou: {response.status_code} {response.json()}")
        except Exception as e:
            logger.error(f"❌ Falha ao acessar o endpoint de saúde: {e}")
        
        # Mantém o script em execução
        input("Pressione Enter para encerrar o servidor...")
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o servidor: {e}")
        logger.debug(traceback.format_exc())
        return False

def main():
    """Função principal."""
    print_header("🔧 DIAGNÓSTICO DA API FASTAPI")
    
    # Verifica as importações
    if not check_imports():
        print("\n❌ Verificação de importações falhou. Corrija os erros acima.")
        return
    
    # Testa a conexão com o banco de dados
    if not test_database_connection():
        print("\n❌ Teste de conexão com o banco de dados falhou. Verifique as configurações.")
        return
    
    # Testa a criação da aplicação
    if not test_api_creation():
        print("\n❌ Teste de criação da aplicação falhou. Verifique os logs acima.")
        return
    
    # Inicia o servidor de teste
    print("\n" + "✅" * 20)
    print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("✅" * 20)
    
    # Pergunta se o usuário deseja iniciar o servidor
    if input("\nDeseja iniciar o servidor de teste? (s/n): ").lower() == 's':
        run_test_server()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        logger.debug(traceback.format_exc())
    finally:
        input("\nPressione Enter para sair...")
