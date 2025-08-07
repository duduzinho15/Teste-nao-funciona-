"""
SCRIPT PARA INICIAR A API FASTAPI DO APOSTAPRO
===============================================

Script simplificado para iniciar a API FastAPI do ApostaPro.
Este script evita problemas de importação relativa configurando
corretamente o PYTHONPATH antes de importar os módulos da aplicação.

Uso:
    python run_api.py
"""

import os
import sys
from pathlib import Path

# Configurar o PYTHONPATH para incluir o diretório raiz do projeto
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Configurar logging básico
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar configurações da API
from api.config import get_api_settings

# Obter configurações
settings = get_api_settings()

# Exibir informações da API
print("🚀 INICIALIZANDO API FASTAPI DO APOSTAPRO")
print("=" * 50)
print(f"📦 Versão: {settings.api_version}")
print(f"🌐 Host: {settings.api_host}:{settings.api_port}")
print(f"🔧 Ambiente: {settings.environment}")
print(f"🐛 Debug: {settings.debug}")
print(f"📚 Documentação: http://{settings.api_host}:{settings.api_port}/docs")
print("=" * 50)

# Iniciar o servidor uvicorn
if __name__ == "__main__":
    try:
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
