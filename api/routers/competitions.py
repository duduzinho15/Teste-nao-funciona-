"""
ROUTER DE COMPETIÇÕES - API FASTAPI
===================================

Endpoints para operações relacionadas a competições esportivas.
Implementa CRUD completo com filtros, paginação e validação.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
import logging

from api.schemas import (
    CompeticaoResponse, CompeticaoList, CompeticaoCreate, 
    CompeticaoUpdate, CompeticaoFilter, ErrorResponse
)
from api.security import get_current_api_key
from Coleta_de_dados.database import SessionLocal
from Coleta_de_dados.database.models import Competicao

def get_db() -> Session:
    """
    Fornece uma sessão do banco de dados para cada requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuração
router = APIRouter(prefix="/competitions", tags=["competitions"])
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE COMPETIÇÕES
# ============================================================================

@router.get(
    "/",
    response_model=CompeticaoList,
    summary="Listar competições",
    description="Retorna uma lista paginada de competições com filtros opcionais",
    responses={
        200: {"description": "Lista de competições retornada com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def list_competitions(
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    size: int = Query(50, ge=1, le=100, description="Itens por página (máximo 100)"),
    nome: Optional[str] = Query(None, description="Filtrar por nome (busca parcial)"),
    contexto: Optional[str] = Query(None, description="Filtrar por contexto"),
    ativa: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista todas as competições com filtros e paginação.
    
    - **page**: Página a ser retornada (padrão: 1)
    - **size**: Número de itens por página (padrão: 50, máximo: 100)
    - **nome**: Filtro por nome da competição (busca parcial)
    - **contexto**: Filtro por contexto (Masculino, Feminino, etc.)
    - **ativa**: Filtro por status ativo (true/false)
    """
    try:
        # Construir query base
        query = db.query(Competicao)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Competicao.nome.ilike(f"%{nome}%"))
        
        if contexto:
            query = query.filter(Competicao.contexto == contexto)
            
        if ativa is not None:
            query = query.filter(Competicao.ativa == ativa)
        
        # Contar total de registros
        total = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * size
        competitions = query.offset(offset).limit(size).all()
        
        # Calcular número de páginas
        pages = (total + size - 1) // size
        
        logger.info(f"Listagem de competições: {len(competitions)} itens (página {page}/{pages})")
        
        return CompeticaoList(
            items=[CompeticaoResponse.model_validate(comp) for comp in competitions],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar competições: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar competições"
        )

@router.get(
    "/{competition_id}",
    response_model=CompeticaoResponse,
    summary="Obter competição por ID",
    description="Retorna os detalhes de uma competição específica",
    responses={
        200: {"description": "Competição encontrada"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Competição não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_competition(
    competition_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Obtém uma competição específica pelo ID.
    
    - **competition_id**: ID único da competição
    """
    try:
        competition = db.query(Competicao).filter(Competicao.id == competition_id).first()
        
        if not competition:
            logger.warning(f"Competição não encontrada: ID {competition_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competição com ID {competition_id} não encontrada"
            )
        
        logger.info(f"Competição encontrada: {competition.nome} (ID: {competition_id})")
        return CompeticaoResponse.model_validate(competition)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar competição {competition_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar competição"
        )

@router.post(
    "/",
    response_model=CompeticaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova competição",
    description="Cria uma nova competição no sistema",
    responses={
        201: {"description": "Competição criada com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        409: {"model": ErrorResponse, "description": "Competição já existe"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def create_competition(
    competition_data: CompeticaoCreate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova competição.
    
    - **nome**: Nome da competição (obrigatório)
    - **url**: URL da competição no FBRef (opcional)
    - **contexto**: Contexto da competição (Masculino/Feminino/Desconhecido)
    - **ativa**: Se a competição está ativa (padrão: true)
    """
    try:
        # Verificar se já existe competição com o mesmo nome
        existing = db.query(Competicao).filter(Competicao.nome == competition_data.nome).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Competição '{competition_data.nome}' já existe"
            )
        
        # Criar nova competição
        new_competition = Competicao(**competition_data.model_dump())
        db.add(new_competition)
        db.commit()
        db.refresh(new_competition)
        
        logger.info(f"Nova competição criada: {new_competition.nome} (ID: {new_competition.id})")
        return CompeticaoResponse.model_validate(new_competition)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar competição: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar competição"
        )

@router.put(
    "/{competition_id}",
    response_model=CompeticaoResponse,
    summary="Atualizar competição",
    description="Atualiza os dados de uma competição existente",
    responses={
        200: {"description": "Competição atualizada com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Competição não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def update_competition(
    competition_id: int,
    competition_data: CompeticaoUpdate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma competição existente.
    
    - **competition_id**: ID da competição a ser atualizada
    - Apenas os campos fornecidos serão atualizados
    """
    try:
        competition = db.query(Competicao).filter(Competicao.id == competition_id).first()
        
        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competição com ID {competition_id} não encontrada"
            )
        
        # Atualizar apenas campos fornecidos
        update_data = competition_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(competition, field, value)
        
        db.commit()
        db.refresh(competition)
        
        logger.info(f"Competição atualizada: {competition.nome} (ID: {competition_id})")
        return CompeticaoResponse.model_validate(competition)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar competição {competition_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar competição"
        )

@router.delete(
    "/{competition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir competição",
    description="Remove uma competição do sistema",
    responses={
        204: {"description": "Competição excluída com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Competição não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def delete_competition(
    competition_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Exclui uma competição do sistema.
    
    - **competition_id**: ID da competição a ser excluída
    """
    try:
        competition = db.query(Competicao).filter(Competicao.id == competition_id).first()
        
        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competição com ID {competition_id} não encontrada"
            )
        
        db.delete(competition)
        db.commit()
        
        logger.info(f"Competição excluída: {competition.nome} (ID: {competition_id})")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir competição {competition_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao excluir competição"
        )

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@router.get(
    "/stats/summary",
    summary="Estatísticas de competições",
    description="Retorna estatísticas gerais das competições",
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_competitions_stats(
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais das competições.
    """
    try:
        stats = {
            "total_competitions": db.query(Competicao).count(),
            "active_competitions": db.query(Competicao).filter(Competicao.ativa == True).count(),
            "inactive_competitions": db.query(Competicao).filter(Competicao.ativa == False).count(),
            "by_context": {}
        }
        
        # Estatísticas por contexto
        context_stats = db.query(
            Competicao.contexto, 
            func.count(Competicao.id)
        ).group_by(Competicao.contexto).all()
        
        for context, count in context_stats:
            stats["by_context"][context or "Desconhecido"] = count
        
        logger.info("Estatísticas de competições geradas")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas de competições: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar estatísticas"
        )
