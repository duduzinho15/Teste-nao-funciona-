"""
Script para testar a inicialização da API principal com logs detalhados.
"""
import logging
import sys
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

def test_api_startup():
    """Testa a inicialização da API principal."""
    try:
        # Adiciona o diretório raiz ao path do Python
        project_root = str(Path(__file__).parent.absolute())
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        logger.info("🔍 Verificando importações...")
        
        # Testa importações básicas primeiro
        try:
            logger.info("  - Importando módulos básicos...")
            import fastapi
            import uvicorn
            from fastapi import FastAPI
            logger.info("  ✅ Módulos básicos importados com sucesso.")
        except ImportError as e:
            logger.error(f"  ❌ Falha ao importar módulos básicos: {e}")
            logger.error(traceback.format_exc())
            return False
        
        # Tenta importar o módulo principal da API
        try:
            logger.info("  - Importando módulo api.main...")
            from api.main import create_app
            logger.info("  ✅ Módulo api.main importado com sucesso.")
        except Exception as e:
            logger.error(f"  ❌ Falha ao importar api.main: {e}")
            logger.error(traceback.format_exc())
            return False
        
        # Tenta criar a aplicação
        try:
            logger.info("🚀 Criando aplicativo FastAPI...")
            app = create_app()
            logger.info("✅ Aplicativo criado com sucesso!")
            
            # Lista as rotas disponíveis
            logger.info("\n🛣️  Rotas disponíveis:")
            for route in app.routes:
                if hasattr(route, 'methods'):
                    methods = ", ".join(route.methods)
                    logger.info(f"  {methods}: {route.path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar o aplicativo: {e}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🔍 INICIANDO TESTE DE INICIALIZAÇÃO DA API PRINCIPAL")
    print("=" * 80)
    
    if test_api_startup():
        print("\n" + "✅" * 20)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("✅" * 20)
    else:
        print("\n" + "❌" * 20)
        print("❌ FALHA AO INICIALIZAR A API. VERIFIQUE OS LOGS ACIMA.")
        print("❌" * 20)
    
    print("\nPressione Enter para sair...")
    input()
