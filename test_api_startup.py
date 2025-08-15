"""
Script para testar a inicialização da API FastAPI.
"""
import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, os.path.abspath('.'))

def create_test_app():
    """Cria uma aplicação FastAPI de teste."""
    app = FastAPI(
        title="ApostaPro API - Teste",
        description="API de teste para verificação de inicialização",
        version="1.0.0"
    )
    
    # Configuração básica de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rota de health check simples
    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "ok", "message": "API funcionando corretamente"}
    
    return app

def main():
    """Função principal para testar a inicialização da API."""
    print("🚀 Iniciando teste de inicialização da API...")
    
    # Tenta criar a aplicação de teste
    try:
        app = create_test_app()
        print("✅ Aplicação FastAPI criada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao criar a aplicação FastAPI: {e}")
        return False
    
    # Tenta iniciar o servidor em uma porta diferente
    port = 8001
    print(f"\n🌐 Iniciando servidor de teste na porta {port}...")
    print(f"🔗 Acesse: http://localhost:{port}/api/v1/health")
    print("Pressione Ctrl+C para encerrar o servidor.")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        return False
    finally:
        print("\n🛑 Servidor encerrado.")

if __name__ == "__main__":
    main()
