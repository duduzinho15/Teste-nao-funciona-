"""
SCRIPT PARA INICIAR A API FASTAPI DO APOSTAPRO
===============================================

Script simplificado para iniciar a API FastAPI do ApostaPro.
Este script evita problemas de importação relativa configurando
corretamente o PYTHONPATH antes de importar os módulos da aplicação.

Uso:
    python run_api.py
"""

import uvicorn
import os
import sys

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando a API FastAPI do ApostaPro...")
    print("📍 Endpoint principal: http://localhost:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/health")
    print("\n" + "="*80)
    
    # Iniciar o servidor
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
