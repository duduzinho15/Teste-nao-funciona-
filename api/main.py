"""
APLICATIVO PRINCIPAL DA API FASTAPI
===================================

Aplicativo FastAPI principal que integra todos os routers, middleware e configurações.
Serve como ponto de entrada para a API RESTful do ApostaPro.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime
import uvicorn

# Imports locais
from .config import get_api_settings, DOCS_CONFIG, MIDDLEWARE_CONFIG
from .security import rate_limiter, init_api_keys
from .routers import competitions, clubs, players, health, matches, social, news, analise

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO DO LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    
    Startup:
    - Inicializa API keys
    - Configura logging
    - Verifica conectividade do banco
    
    Shutdown:
    - Limpa recursos
    - Fecha conexões
    """
    # Startup
    logger.info("🚀 Iniciando API FastAPI do ApostaPro...")
    
    try:
        # Inicializar sistema de API keys
        init_api_keys()
        logger.info("✅ Sistema de API Keys inicializado")
        
        # Verificar conectividade do banco
        from Coleta_de_dados.database import db_manager
        if db_manager.test_connection():
            logger.info("✅ Conectividade do banco verificada")
        else:
            logger.warning("⚠️ Problema na conectividade do banco")
        
        logger.info("🎉 API FastAPI iniciada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Finalizando API FastAPI...")
    logger.info("✅ API FastAPI finalizada")

# ============================================================================
# CRIAÇÃO DA APLICAÇÃO FASTAPI
# ============================================================================

def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.
    
    Returns:
        FastAPI: Aplicação configurada
    """
    settings = get_api_settings()
    
    # Criar aplicação FastAPI
    app = FastAPI(
        title=DOCS_CONFIG["title"],
        description=DOCS_CONFIG["description"],
        version=DOCS_CONFIG["version"],
        contact=DOCS_CONFIG["contact"],
        license_info=DOCS_CONFIG["license_info"],
        openapi_tags=DOCS_CONFIG["tags_metadata"],
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # ========================================================================
    # MIDDLEWARE
    # ========================================================================
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        **MIDDLEWARE_CONFIG["cors"]
    )
    
    # Trusted Host Middleware (segurança)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.apostapro.com"]
        )
    
    # Rate Limiting Middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Middleware de rate limiting."""
        client_ip = request.client.host
        api_key = request.headers.get("X-API-Key")
        
        # Verificar rate limit
        if rate_limiter.is_rate_limited(client_ip, api_key):
            rate_info = rate_limiter.get_rate_limit_info(client_ip, api_key)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Limite de {rate_info['limit']} requests por {rate_info['reset_in']}s excedido",
                    "rate_limit": rate_info,
                    "timestamp": datetime.now().isoformat()
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info['limit']),
                    "X-RateLimit-Remaining": str(rate_info['remaining']),
                    "X-RateLimit-Reset": str(rate_info['reset_in']),
                    "Retry-After": str(rate_info['reset_in'])
                }
            )
        
        # Processar requisição
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Adicionar headers de rate limit e performance
        rate_info = rate_limiter.get_rate_limit_info(client_ip, api_key)
        response.headers["X-RateLimit-Limit"] = str(rate_info['limit'])
        response.headers["X-RateLimit-Remaining"] = str(rate_info['remaining'])
        response.headers["X-RateLimit-Reset"] = str(rate_info['reset_in'])
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response
    
    # Logging Middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Middleware de logging de requisições."""
        start_time = time.time()
        
        # Log da requisição
        logger.info(
            f"📥 {request.method} {request.url.path} - "
            f"IP: {request.client.host} - "
            f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
        )
        
        # Processar requisição
        response = await call_next(request)
        
        # Log da resposta
        process_time = time.time() - start_time
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response
    
    # ========================================================================
    # EXCEPTION HANDLERS
    # ========================================================================
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handler para HTTPException."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler para exceções gerais."""
        logger.error(f"❌ Erro não tratado: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "Erro interno do servidor" if not settings.debug else str(exc),
                "status_code": 500,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        )
    
    # ========================================================================
    # ROUTERS
    # ========================================================================
    
    # Incluir routers com prefixo /api/v1
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(competitions.router, prefix="/api/v1")
    app.include_router(clubs.router, prefix="/api/v1")
    app.include_router(players.router, prefix="/api/v1")
    app.include_router(matches.router, prefix="/api/v1")
    app.include_router(social.router, prefix="/api/v1")
    app.include_router(news.router, prefix="/api/v1")
    app.include_router(analise.router, prefix="/api/v1")
    
    # ========================================================================
    # ENDPOINTS RAIZ
    # ========================================================================
    
    @app.get("/", tags=["root"])
    async def root():
        """Endpoint raiz da API."""
        return {
            "message": "🚀 ApostaPro API",
            "version": settings.api_version,
            "description": "API RESTful para dados de futebol",
            "docs_url": "/docs" if settings.debug else "Documentação disponível apenas em desenvolvimento",
            "health_check": "/api/v1/health",
            "endpoints": {
                "competitions": "/api/v1/competitions",
                "clubs": "/api/v1/clubs", 
                "players": "/api/v1/players",
                "matches": "/api/v1/matches",
                "social": "/api/v1/social",
                "news": "/api/v1/news",
                "analysis": "/api/v1/analise",
                "health": "/api/v1/health"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/api", tags=["root"])
    async def api_info():
        """Informações da API."""
        return {
            "api": "ApostaPro API",
            "version": settings.api_version,
            "environment": settings.environment,
            "endpoints": {
                "v1": "/api/v1",
                "health": "/api/v1/health",
                "competitions": "/api/v1/competitions",
                "clubs": "/api/v1/clubs",
                "players": "/api/v1/players",
                "matches": "/api/v1/matches",
                "social": "/api/v1/social",
                "news": "/api/v1/news"
            },
            "authentication": "API Key required (X-API-Key header)",
            "rate_limit": f"{settings.api_rate_limit} requests per {settings.api_rate_limit_period} seconds",
            "timestamp": datetime.now().isoformat()
        }
    
    # ========================================================================
    # DOCUMENTAÇÃO CUSTOMIZADA
    # ========================================================================
    
    def custom_openapi():
        """Gera schema OpenAPI customizado."""
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=DOCS_CONFIG["title"],
            version=DOCS_CONFIG["version"],
            description=DOCS_CONFIG["description"],
            routes=app.routes,
        )
        
        # Adicionar configuração de segurança
        openapi_schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API Key para autenticação"
            }
        }
        
        # Aplicar segurança globalmente
        for path in openapi_schema["paths"].values():
            for method in path.values():
                if isinstance(method, dict) and "tags" in method:
                    if "health" not in method["tags"]:  # Health endpoints são públicos
                        method["security"] = [{"ApiKeyAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app

# ============================================================================
# INSTÂNCIA DA APLICAÇÃO
# ============================================================================

# Criar aplicação
app = create_app()

# ============================================================================
# FUNÇÃO PARA EXECUTAR O SERVIDOR
# ============================================================================

def run_server():
    """
    Executa o servidor da API.
    
    Configurações baseadas nas variáveis de ambiente.
    """
    settings = get_api_settings()
    
    logger.info(f"🚀 Iniciando servidor da API ApostaPro...")
    logger.info(f"📍 Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🐛 Debug: {settings.debug}")
    logger.info(f"📚 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

if __name__ == "__main__":
    run_server()
