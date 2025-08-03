"""
ROUTER DE HEALTH CHECK - API FASTAPI
====================================

Endpoints para verificação de saúde e status da API.
Monitora conectividade do banco, performance e métricas gerais.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging
from datetime import datetime
import time
import psutil
import os

from ..schemas import HealthResponse, ErrorResponse
from ..security import get_optional_api_key
from ...database import get_session, get_database_manager
from ..config import get_api_settings

# Configuração
router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger(__name__)

# Tempo de inicialização da API
START_TIME = datetime.now()

# ============================================================================
# ENDPOINTS DE HEALTH CHECK
# ============================================================================

@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check Básico",
    description="Verifica o status básico da API",
    responses={
        200: {"description": "API funcionando normalmente"},
        503: {"model": ErrorResponse, "description": "Serviço indisponível"}
    }
)
async def health_check(
    api_key: Optional[str] = Depends(get_optional_api_key),
    db: Session = Depends(get_session)
):
    """
    Verifica o status básico da API e conectividade do banco.
    
    Este endpoint não requer autenticação e pode ser usado para:
    - Monitoramento de disponibilidade
    - Load balancer health checks
    - Verificação rápida de status
    """
    try:
        # Verificar conectividade do banco
        start_time = time.time()
        db.execute(text("SELECT 1"))
        db_response_time = round((time.time() - start_time) * 1000, 2)
        
        settings = get_api_settings()
        uptime = datetime.now() - START_TIME
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=settings.api_version,
            database=f"connected ({db_response_time}ms)",
            uptime=str(uptime).split('.')[0]  # Remove microsegundos
        )
        
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível"
        )

@router.get(
    "/detailed",
    summary="Health Check Detalhado",
    description="Verifica status detalhado da API com métricas de sistema",
    responses={
        200: {"description": "Status detalhado da API"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        503: {"model": ErrorResponse, "description": "Serviço indisponível"}
    }
)
async def detailed_health_check(
    api_key: Optional[str] = Depends(get_optional_api_key),
    db: Session = Depends(get_session)
):
    """
    Verifica status detalhado da API incluindo métricas de sistema.
    
    Inclui informações sobre:
    - Status do banco de dados
    - Métricas de sistema (CPU, memória)
    - Pool de conexões
    - Configurações da API
    """
    try:
        settings = get_api_settings()
        db_manager = get_database_manager()
        
        # Verificar banco de dados
        start_time = time.time()
        db.execute(text("SELECT version()"))
        db_response_time = round((time.time() - start_time) * 1000, 2)
        
        # Métricas de sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Status do pool de conexões
        pool_status = db_manager.get_pool_status()
        
        # Uptime
        uptime = datetime.now() - START_TIME
        
        detailed_status = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "version": settings.api_version,
            "environment": settings.environment,
            "uptime": str(uptime).split('.')[0],
            "database": {
                "status": "connected",
                "response_time_ms": db_response_time,
                "pool": pool_status
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 1)
                }
            },
            "api": {
                "debug": settings.debug,
                "log_level": settings.log_level,
                "rate_limit": f"{settings.api_rate_limit}/{settings.api_rate_limit_period}s"
            }
        }
        
        logger.info("Health check detalhado executado com sucesso")
        return detailed_status
        
    except Exception as e:
        logger.error(f"Health check detalhado falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao verificar status detalhado"
        )

@router.get(
    "/database",
    summary="Status do Banco de Dados",
    description="Verifica especificamente o status e performance do banco",
    responses={
        200: {"description": "Status do banco de dados"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        503: {"model": ErrorResponse, "description": "Banco indisponível"}
    }
)
async def database_health_check(
    api_key: Optional[str] = Depends(get_optional_api_key),
    db: Session = Depends(get_session)
):
    """
    Verifica especificamente o status e performance do banco de dados.
    
    Inclui:
    - Conectividade
    - Tempo de resposta
    - Informações da versão
    - Status do pool de conexões
    - Estatísticas básicas das tabelas
    """
    try:
        db_manager = get_database_manager()
        
        # Teste de conectividade e versão
        start_time = time.time()
        result = db.execute(text("SELECT version()")).fetchone()
        db_response_time = round((time.time() - start_time) * 1000, 2)
        
        # Pool status
        pool_status = db_manager.get_pool_status()
        
        # Estatísticas básicas das tabelas
        from ...database.models import Competicao, Clube, Jogador
        
        table_stats = {
            "competitions": db.query(Competicao).count(),
            "clubs": db.query(Clube).count(),
            "players": db.query(Jogador).count()
        }
        
        database_status = {
            "status": "healthy",
            "timestamp": datetime.now(),
            "connection": {
                "status": "connected",
                "response_time_ms": db_response_time,
                "version": result[0] if result else "unknown"
            },
            "pool": pool_status,
            "tables": table_stats,
            "total_records": sum(table_stats.values())
        }
        
        logger.info("Database health check executado com sucesso")
        return database_status
        
    except Exception as e:
        logger.error(f"Database health check falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível"
        )

@router.get(
    "/metrics",
    summary="Métricas da API",
    description="Retorna métricas de performance e uso da API",
    responses={
        200: {"description": "Métricas da API"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno"}
    }
)
async def api_metrics(
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """
    Retorna métricas de performance e uso da API.
    
    Útil para monitoramento e análise de performance.
    """
    try:
        settings = get_api_settings()
        uptime = datetime.now() - START_TIME
        
        # Métricas básicas
        metrics = {
            "timestamp": datetime.now(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],
            "version": settings.api_version,
            "environment": settings.environment,
            "process": {
                "pid": os.getpid(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2)
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        }
        
        logger.info("Métricas da API coletadas")
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao coletar métricas"
        )

# ============================================================================
# ENDPOINTS DE DIAGNÓSTICO
# ============================================================================

@router.get(
    "/ping",
    summary="Ping Simples",
    description="Endpoint de ping simples para verificação básica",
    responses={
        200: {"description": "Pong - API respondendo"},
    }
)
async def ping():
    """
    Endpoint de ping simples.
    
    Retorna uma resposta básica para verificar se a API está respondendo.
    Não requer autenticação.
    """
    return {
        "message": "pong",
        "timestamp": datetime.now(),
        "status": "ok"
    }

@router.get(
    "/version",
    summary="Versão da API",
    description="Retorna informações de versão da API",
    responses={
        200: {"description": "Informações de versão"},
    }
)
async def get_version():
    """
    Retorna informações de versão da API.
    
    Não requer autenticação.
    """
    settings = get_api_settings()
    
    return {
        "api_version": settings.api_version,
        "api_title": settings.api_title,
        "environment": settings.environment,
        "timestamp": datetime.now()
    }
