"""
ROUTER DE PARTIDAS - API FASTAPI
================================

Endpoints para operações relacionadas a partidas de futebol.
Inclui estatísticas avançadas como xG, xA, formações táticas, etc.

Autor: Sistema de API RESTful
Data: 2025-08-06
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from api import schemas
from api.security import get_current_api_key
from Coleta_de_dados.database import SessionLocal
from Coleta_de_dados.database.models import Partida, EstatisticaPartida, Clube, Competicao

# Configuração
router = APIRouter(
    prefix="/matches",
    tags=["matches"]
)
logger = logging.getLogger(__name__)

def get_db() -> Session:
    """Fornece uma sessão do banco de dados para cada requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/{match_id}",
    response_model=schemas.MatchDetailResponse,
    summary="Obter detalhes de uma partida",
    description="Retorna os detalhes completos de uma partida, incluindo estatísticas avançadas",
    responses={
        200: {"description": "Detalhes da partida retornados com sucesso"},
        404: {"description": "Partida não encontrada"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def get_match_details(
    match_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Retorna os detalhes completos de uma partida, incluindo estatísticas avançadas.
    
    - **match_id**: ID único da partida
    """
    try:
        # Busca a partida pelo ID
        match = db.query(Partida).filter(Partida.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Partida com ID {match_id} não encontrada"
            )
        
        # Busca as estatísticas avançadas da partida
        stats = db.query(EstatisticaPartida).filter(
            EstatisticaPartida.partida_id == match_id
        ).first()
        
        # Busca informações adicionais dos clubes e competição
        clube_casa = db.query(Clube).filter(Clube.id == match.clube_casa_id).first()
        clube_visitante = db.query(Clube).filter(Clube.id == match.clube_visitante_id).first()
        competicao = db.query(Competicao).filter(Competicao.id == match.competicao_id).first()
        
        # Prepara o dicionário de resposta
        response_data = {
            "id": match.id,
            "data_partida": match.data_partida,
            "hora_partida": match.horario,
            "competicao_id": match.competicao_id,
            "competicao_nome": competicao.nome if competicao else None,
            "clube_casa_id": match.clube_casa_id,
            "clube_casa_nome": clube_casa.nome if clube_casa else None,
            "clube_visitante_id": match.clube_visitante_id,
            "clube_visitante_nome": clube_visitante.nome if clube_visitante else None,
            "gols_casa": match.gols_casa,
            "gols_visitante": match.gols_visitante,
            "resultado": match.resultado,
            "rodada": match.rodada,
            "temporada": match.temporada,
            "url_fbref": match.url_fbref,
            "status": match.status,
            "estatisticas_avancadas": {
                "posse_bola_casa": stats.posse_bola_casa if stats else None,
                "posse_bola_visitante": stats.posse_bola_visitante if stats else None,
                "chutes_casa": stats.chutes_casa if stats else None,
                "chutes_visitante": stats.chutes_visitante if stats else None,
                "chutes_no_gol_casa": stats.chutes_no_gol_casa if stats else None,
                "chutes_no_gol_visitante": stats.chutes_no_gol_visitante if stats else None,
                "escanteios_casa": stats.escanteios_casa if stats else None,
                "escanteios_visitante": stats.escanteios_visitante if stats else None,
                "faltas_casa": stats.faltas_casa if stats else None,
                "faltas_visitante": stats.faltas_visitante if stats else None,
                "cartoes_amarelos_casa": stats.cartoes_amarelos_casa if stats else None,
                "cartoes_amarelos_visitante": stats.cartoes_amarelos_visitante if stats else None,
                "cartoes_vermelhos_casa": stats.cartoes_vermelhos_casa if stats else None,
                "cartoes_vermelhos_visitante": stats.cartoes_vermelhos_visitante if stats else None,
                "xg_casa": stats.xg_casa if stats else None,
                "xg_visitante": stats.xg_visitante if stats else None,
                "xa_casa": stats.xa_casa if stats else None,
                "xa_visitante": stats.xa_visitante if stats else None,
                "formacao_casa": stats.formacao_casa if stats else None,
                "formacao_visitante": stats.formacao_visitante if stats else None
            } if stats else None
        }
        
        logger.info(f"Detalhes da partida {match_id} retornados com sucesso")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da partida {match_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )

@router.get(
    "/",
    response_model=schemas.MatchList,
    summary="Listar partidas",
    description="Retorna uma lista de partidas com filtros opcionais",
    responses={
        200: {"description": "Lista de partidas retornada com sucesso"},
        500: {"description": "Erro interno do servidor"}
    }
)
async def list_matches(
    page: int = 1,
    size: int = 50,
    competition_id: Optional[int] = None,
    season: Optional[str] = None,
    status: Optional[str] = None,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Retorna uma lista de partidas com filtros opcionais.
    
    - **page**: Número da página (padrão: 1)
    - **size**: Itens por página (padrão: 50, máximo: 100)
    - **competition_id**: Filtrar por ID da competição
    - **season**: Filtrar por temporada (ex: "2024-2025")
    - **status**: Filtrar por status (ex: "finalizada", "agendada")
    """
    try:
        # Validação dos parâmetros
        if page < 1:
            page = 1
        if size < 1 or size > 100:
            size = 50
            
        # Construção da query
        query = db.query(Partida)
        
        # Aplicação dos filtros
        if competition_id is not None:
            query = query.filter(Partida.competicao_id == competition_id)
            
        if season:
            query = query.filter(Partida.temporada == season)
            
        if status:
            query = query.filter(Partida.status == status)
        
        # Ordenação e paginação
        query = query.order_by(Partida.data_partida.desc(), Partida.horario.desc())
        total = query.count()
        matches = query.offset((page - 1) * size).limit(size).all()
        
        # Cálculo do total de páginas
        pages = (total + size - 1) // size if total > 0 else 1
        
        # Prepara os itens da resposta
        items = []
        for match in matches:
            items.append({
                "id": match.id,
                "data_partida": match.data_partida,
                "hora_partida": match.horario,
                "competicao_id": match.competicao_id,
                "clube_casa_id": match.clube_casa_id,
                "clube_visitante_id": match.clube_visitante_id,
                "gols_casa": match.gols_casa,
                "gols_visitante": match.gols_visitante,
                "resultado": match.resultado,
                "rodada": match.rodada,
                "temporada": match.temporada,
                "status": match.status
            })
        
        # Cria a resposta usando o schema
        response_data = schemas.MatchList(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
        logger.info(f"Listadas {len(response_data.items)} de {total} partidas")
        return response_data
        
    except Exception as e:
        logger.error(f"Erro ao listar partidas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a requisição"
        )
