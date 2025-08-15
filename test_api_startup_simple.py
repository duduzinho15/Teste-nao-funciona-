"""
Script simplificado para testar a inicialização da API FastAPI.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cria uma aplicação FastAPI mínima
app = FastAPI(title="API Teste", version="1.0.0")

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
    return {"status": "ok", "message": "API de teste funcionando corretamente"}

# Rota raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de teste do ApostaPro"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste na porta 8001...")
    print("🔗 Acesse: http://localhost:8001/api/v1/health")
    print("Pressione Ctrl+C para encerrar o servidor.")
    
    uvicorn.run(
        "test_api_startup_simple:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="debug"
    )
