"""
ROUTER DE CLUBES - API FASTAPI
==============================

Endpoints para operações relacionadas a clubes de futebol.
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

from api.schemas import (
    ClubeResponse, ClubeList, ClubeCreate, 
    ClubeUpdate, ClubeFilter, ErrorResponse
)
from api.security import get_current_api_key
from Coleta_de_dados.database import SessionLocal
from Coleta_de_dados.database.models import Clube, Jogador

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
router = APIRouter(prefix="/clubs", tags=["clubs"])
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE CLUBES
# ============================================================================

@router.get(
    "/",
    response_model=ClubeList,
    summary="Listar clubes",
    description="Retorna uma lista paginada de clubes com filtros opcionais",
    responses={
        200: {"description": "Lista de clubes retornada com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def list_clubs(
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    size: int = Query(50, ge=1, le=100, description="Itens por página (máximo 100)"),
    nome: Optional[str] = Query(None, description="Filtrar por nome (busca parcial)"),
    pais: Optional[str] = Query(None, description="Filtrar por país"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista todos os clubes com filtros e paginação.
    
    - **page**: Página a ser retornada (padrão: 1)
    - **size**: Número de itens por página (padrão: 50, máximo: 100)
    - **nome**: Filtro por nome do clube (busca parcial)
    - **pais**: Filtro por país do clube
    """
    try:
        # Construir query base
        query = db.query(Clube)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Clube.nome.ilike(f"%{nome}%"))
        
        if pais:
            query = query.filter(Clube.pais.ilike(f"%{pais}%"))
        
        # Contar total de registros
        total = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * size
        clubs = query.offset(offset).limit(size).all()
        
        # Calcular número de páginas
        pages = (total + size - 1) // size
        
        # Enriquecer dados com contagem de jogadores
        enriched_clubs = []
        for club in clubs:
            club_data = ClubeResponse.model_validate(club)
            # Contar jogadores do clube
            total_jogadores = db.query(Jogador).filter(Jogador.clube_id == club.id).count()
            club_data.total_jogadores = total_jogadores
            enriched_clubs.append(club_data)
        
        logger.info(f"Listagem de clubes: {len(clubs)} itens (página {page}/{pages})")
        
        return ClubeList(
            items=enriched_clubs,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar clubes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar clubes"
        )

@router.get(
    "/{club_id}",
    response_model=ClubeResponse,
    summary="Obter clube por ID",
    description="Retorna os detalhes de um clube específico",
    responses={
        200: {"description": "Clube encontrado"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_club(
    club_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Obtém um clube específico pelo ID.
    
    - **club_id**: ID único do clube
    """
    try:
        club = db.query(Clube).filter(Clube.id == club_id).first()
        
        if not club:
            logger.warning(f"Clube não encontrado: ID {club_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clube com ID {club_id} não encontrado"
            )
        
        # Enriquecer com dados adicionais
        club_data = ClubeResponse.model_validate(club)
        club_data.total_jogadores = db.query(Jogador).filter(Jogador.clube_id == club.id).count()
        
        logger.info(f"Clube encontrado: {club.nome} (ID: {club_id})")
        return club_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar clube {club_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar clube"
        )

@router.post(
    "/",
    response_model=ClubeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo clube",
    description="Cria um novo clube no sistema",
    responses={
        201: {"description": "Clube criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        409: {"model": ErrorResponse, "description": "Clube já existe"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def create_club(
    club_data: ClubeCreate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Cria um novo clube.
    
    - **nome**: Nome do clube (obrigatório)
    - **url_fbref**: URL do clube no FBRef (opcional)
    - **pais**: País do clube (opcional)
    """
    try:
        # Verificar se já existe clube com o mesmo nome
        existing = db.query(Clube).filter(Clube.nome == club_data.nome).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Clube '{club_data.nome}' já existe"
            )
        
        # Criar novo clube
        new_club = Clube(**club_data.model_dump())
        db.add(new_club)
        db.commit()
        db.refresh(new_club)
        
        logger.info(f"Novo clube criado: {new_club.nome} (ID: {new_club.id})")
        return ClubeResponse.model_validate(new_club)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar clube: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar clube"
        )

@router.get(
    "/{club_id}/players",
    summary="Listar jogadores do clube",
    description="Retorna todos os jogadores de um clube específico",
    responses={
        200: {"description": "Jogadores do clube retornados com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_club_players(
    club_id: int,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=100, description="Itens por página"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista todos os jogadores de um clube específico.
    
    - **club_id**: ID do clube
    - **page**: Página a ser retornada (padrão: 1)
    - **size**: Número de itens por página (padrão: 50)
    """
    try:
        # Verificar se o clube existe
        club = db.query(Clube).filter(Clube.id == club_id).first()
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clube com ID {club_id} não encontrado"
            )
        
        # Buscar jogadores do clube
        query = db.query(Jogador).filter(Jogador.clube_id == club_id)
        total = query.count()
        
        offset = (page - 1) * size
        players = query.offset(offset).limit(size).all()
        
        pages = (total + size - 1) // size
        
        # Enriquecer dados dos jogadores
        from ..schemas import JogadorResponse
        enriched_players = []
        for player in players:
            player_data = JogadorResponse.model_validate(player)
            player_data.clube_nome = club.nome
            enriched_players.append(player_data)
        
        logger.info(f"Jogadores do clube {club.nome}: {len(players)} itens")
        
        return {
            "club_id": club_id,
            "club_name": club.nome,
            "players": {
                "items": enriched_players,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar jogadores do clube {club_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar jogadores do clube"
        )

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@router.get(
    "/stats/summary",
    summary="Estatísticas de clubes",
    description="Retorna estatísticas gerais dos clubes",
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_clubs_stats(
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais dos clubes.
    """
    try:
        stats = {
            "total_clubs": db.query(Clube).count(),
            "clubs_with_players": db.query(Clube).join(Jogador).distinct().count(),
            "by_country": {},
            "top_clubs_by_players": []
        }
        
        # Estatísticas por país
        country_stats = db.query(
            Clube.pais, 
            func.count(Clube.id)
        ).group_by(Clube.pais).all()
        
        for country, count in country_stats:
            stats["by_country"][country or "Desconhecido"] = count
        
        # Top clubes por número de jogadores
        top_clubs = db.query(
            Clube.nome,
            func.count(Jogador.id).label('player_count')
        ).outerjoin(Jogador).group_by(Clube.id, Clube.nome).order_by(
            func.count(Jogador.id).desc()
        ).limit(10).all()
        
        stats["top_clubs_by_players"] = [
            {"club_name": name, "player_count": count}
            for name, count in top_clubs
        ]
        
        logger.info("Estatísticas de clubes geradas")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas de clubes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar estatísticas"
        )
