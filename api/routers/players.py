"""
ROUTER DE JOGADORES - API FASTAPI
=================================

Endpoints para operações relacionadas a jogadores de futebol.
Implementa CRUD completo com filtros, paginação e validação.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List
import logging

from ..schemas import (
    JogadorResponse, JogadorList, JogadorCreate, 
    JogadorUpdate, JogadorFilter, ErrorResponse
)
from ..security import get_current_api_key
from ...database import get_session
from ...database.models import Jogador, Clube

# Configuração
router = APIRouter(prefix="/players", tags=["players"])
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE JOGADORES
# ============================================================================

@router.get(
    "/",
    response_model=JogadorList,
    summary="Listar jogadores",
    description="Retorna uma lista paginada de jogadores com filtros opcionais",
    responses={
        200: {"description": "Lista de jogadores retornada com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def list_players(
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    size: int = Query(50, ge=1, le=100, description="Itens por página (máximo 100)"),
    nome: Optional[str] = Query(None, description="Filtrar por nome (busca parcial)"),
    posicao: Optional[str] = Query(None, description="Filtrar por posição"),
    clube_id: Optional[int] = Query(None, description="Filtrar por clube"),
    nacionalidade: Optional[str] = Query(None, description="Filtrar por nacionalidade"),
    idade_min: Optional[int] = Query(None, ge=15, description="Idade mínima"),
    idade_max: Optional[int] = Query(None, le=50, description="Idade máxima"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Lista todos os jogadores com filtros e paginação.
    
    - **page**: Página a ser retornada (padrão: 1)
    - **size**: Número de itens por página (padrão: 50, máximo: 100)
    - **nome**: Filtro por nome do jogador (busca parcial)
    - **posicao**: Filtro por posição do jogador
    - **clube_id**: Filtro por ID do clube
    - **nacionalidade**: Filtro por nacionalidade
    - **idade_min**: Idade mínima (15+)
    - **idade_max**: Idade máxima (50-)
    """
    try:
        # Construir query base com join para clube
        query = db.query(Jogador).outerjoin(Clube)
        
        # Aplicar filtros
        if nome:
            query = query.filter(Jogador.nome.ilike(f"%{nome}%"))
        
        if posicao:
            query = query.filter(Jogador.posicao.ilike(f"%{posicao}%"))
            
        if clube_id:
            query = query.filter(Jogador.clube_id == clube_id)
            
        if nacionalidade:
            query = query.filter(Jogador.nacionalidade.ilike(f"%{nacionalidade}%"))
            
        if idade_min:
            query = query.filter(Jogador.idade >= idade_min)
            
        if idade_max:
            query = query.filter(Jogador.idade <= idade_max)
        
        # Contar total de registros
        total = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * size
        players = query.offset(offset).limit(size).all()
        
        # Calcular número de páginas
        pages = (total + size - 1) // size
        
        # Enriquecer dados com nome do clube
        enriched_players = []
        for player in players:
            player_data = JogadorResponse.model_validate(player)
            if player.clube_id:
                clube = db.query(Clube).filter(Clube.id == player.clube_id).first()
                if clube:
                    player_data.clube_nome = clube.nome
            enriched_players.append(player_data)
        
        logger.info(f"Listagem de jogadores: {len(players)} itens (página {page}/{pages})")
        
        return JogadorList(
            items=enriched_players,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar jogadores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar jogadores"
        )

@router.get(
    "/{player_id}",
    response_model=JogadorResponse,
    summary="Obter jogador por ID",
    description="Retorna os detalhes de um jogador específico",
    responses={
        200: {"description": "Jogador encontrado"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Jogador não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_player(
    player_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Obtém um jogador específico pelo ID.
    
    - **player_id**: ID único do jogador
    """
    try:
        player = db.query(Jogador).filter(Jogador.id == player_id).first()
        
        if not player:
            logger.warning(f"Jogador não encontrado: ID {player_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jogador com ID {player_id} não encontrado"
            )
        
        # Enriquecer com dados do clube
        player_data = JogadorResponse.model_validate(player)
        if player.clube_id:
            clube = db.query(Clube).filter(Clube.id == player.clube_id).first()
            if clube:
                player_data.clube_nome = clube.nome
        
        logger.info(f"Jogador encontrado: {player.nome} (ID: {player_id})")
        return player_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar jogador {player_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar jogador"
        )

@router.post(
    "/",
    response_model=JogadorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo jogador",
    description="Cria um novo jogador no sistema",
    responses={
        201: {"description": "Jogador criado com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def create_player(
    player_data: JogadorCreate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Cria um novo jogador.
    
    - **nome**: Nome do jogador (obrigatório)
    - **url_fbref**: URL do jogador no FBRef (opcional)
    - **posicao**: Posição do jogador (opcional)
    - **idade**: Idade do jogador (15-50, opcional)
    - **nacionalidade**: Nacionalidade do jogador (opcional)
    - **clube_id**: ID do clube (opcional)
    """
    try:
        # Verificar se o clube existe (se fornecido)
        if player_data.clube_id:
            clube = db.query(Clube).filter(Clube.id == player_data.clube_id).first()
            if not clube:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Clube com ID {player_data.clube_id} não encontrado"
                )
        
        # Criar novo jogador
        new_player = Jogador(**player_data.model_dump())
        db.add(new_player)
        db.commit()
        db.refresh(new_player)
        
        # Enriquecer resposta com nome do clube
        player_response = JogadorResponse.model_validate(new_player)
        if new_player.clube_id:
            clube = db.query(Clube).filter(Clube.id == new_player.clube_id).first()
            if clube:
                player_response.clube_nome = clube.nome
        
        logger.info(f"Novo jogador criado: {new_player.nome} (ID: {new_player.id})")
        return player_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar jogador: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar jogador"
        )

@router.get(
    "/search/by-position",
    summary="Buscar jogadores por posição",
    description="Retorna jogadores filtrados por posição específica",
    responses={
        200: {"description": "Jogadores encontrados"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def search_players_by_position(
    posicao: str = Query(..., description="Posição do jogador"),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=100, description="Itens por página"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Busca jogadores por posição específica.
    
    - **posicao**: Posição a ser buscada (obrigatório)
    - **page**: Página a ser retornada (padrão: 1)
    - **size**: Número de itens por página (padrão: 50)
    """
    try:
        query = db.query(Jogador).filter(Jogador.posicao.ilike(f"%{posicao}%"))
        total = query.count()
        
        offset = (page - 1) * size
        players = query.offset(offset).limit(size).all()
        
        pages = (total + size - 1) // size
        
        # Enriquecer com dados do clube
        enriched_players = []
        for player in players:
            player_data = JogadorResponse.model_validate(player)
            if player.clube_id:
                clube = db.query(Clube).filter(Clube.id == player.clube_id).first()
                if clube:
                    player_data.clube_nome = clube.nome
            enriched_players.append(player_data)
        
        logger.info(f"Busca por posição '{posicao}': {len(players)} jogadores encontrados")
        
        return {
            "position": posicao,
            "players": {
                "items": enriched_players,
                "total": total,
                "page": page,
                "size": size,
                "pages": pages
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar jogadores por posição '{posicao}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar jogadores"
        )

# ============================================================================
# ENDPOINTS DE ESTATÍSTICAS
# ============================================================================

@router.get(
    "/stats/summary",
    summary="Estatísticas de jogadores",
    description="Retorna estatísticas gerais dos jogadores",
    responses={
        200: {"description": "Estatísticas retornadas com sucesso"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_players_stats(
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Retorna estatísticas gerais dos jogadores.
    """
    try:
        stats = {
            "total_players": db.query(Jogador).count(),
            "players_with_club": db.query(Jogador).filter(Jogador.clube_id.isnot(None)).count(),
            "by_position": {},
            "by_nationality": {},
            "age_distribution": {
                "under_20": db.query(Jogador).filter(Jogador.idade < 20).count(),
                "20_to_25": db.query(Jogador).filter(and_(Jogador.idade >= 20, Jogador.idade <= 25)).count(),
                "26_to_30": db.query(Jogador).filter(and_(Jogador.idade >= 26, Jogador.idade <= 30)).count(),
                "over_30": db.query(Jogador).filter(Jogador.idade > 30).count()
            }
        }
        
        # Estatísticas por posição
        position_stats = db.query(
            Jogador.posicao, 
            func.count(Jogador.id)
        ).group_by(Jogador.posicao).all()
        
        for position, count in position_stats:
            stats["by_position"][position or "Desconhecida"] = count
        
        # Estatísticas por nacionalidade (top 10)
        nationality_stats = db.query(
            Jogador.nacionalidade, 
            func.count(Jogador.id)
        ).group_by(Jogador.nacionalidade).order_by(
            func.count(Jogador.id).desc()
        ).limit(10).all()
        
        for nationality, count in nationality_stats:
            stats["by_nationality"][nationality or "Desconhecida"] = count
        
        logger.info("Estatísticas de jogadores geradas")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas de jogadores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar estatísticas"
        )

@router.get(
    "/stats/positions",
    summary="Estatísticas detalhadas por posição",
    description="Retorna estatísticas detalhadas agrupadas por posição",
    responses={
        200: {"description": "Estatísticas por posição retornadas"},
        401: {"model": ErrorResponse, "description": "API Key inválida"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_position_stats(
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_session)
):
    """
    Retorna estatísticas detalhadas agrupadas por posição.
    """
    try:
        # Estatísticas por posição com idade média
        position_stats = db.query(
            Jogador.posicao,
            func.count(Jogador.id).label('total'),
            func.avg(Jogador.idade).label('idade_media'),
            func.min(Jogador.idade).label('idade_min'),
            func.max(Jogador.idade).label('idade_max')
        ).group_by(Jogador.posicao).all()
        
        stats = {}
        for position, total, avg_age, min_age, max_age in position_stats:
            position_name = position or "Desconhecida"
            stats[position_name] = {
                "total_players": total,
                "average_age": round(float(avg_age), 1) if avg_age else None,
                "min_age": min_age,
                "max_age": max_age
            }
        
        logger.info("Estatísticas detalhadas por posição geradas")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas por posição: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao gerar estatísticas"
        )
