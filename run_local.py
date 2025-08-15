"""
Script para iniciar a API FastAPI localmente para testes.
"""
import uvicorn
import logging
import sys
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Inicia o servidor FastAPI."""
    # Adiciona o diretório raiz ao path do Python
    project_root = str(Path(__file__).parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Configuração do servidor
    host = "0.0.0.0"
    port = 8000
    
    logger.info("🚀 Iniciando servidor FastAPI...")
    logger.info(f"📡 URL: http://{host}:{port}")
    logger.info(f"📚 Documentação: http://{host}:{port}/docs")
    logger.info("🛑 Pressione Ctrl+C para encerrar o servidor")
    
    # Inicia o servidor
    uvicorn.run(
        "api.main:create_app",
        factory=True,
        host=host,
        port=port,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o servidor: {e}", exc_info=True)
        sys.exit(1)
