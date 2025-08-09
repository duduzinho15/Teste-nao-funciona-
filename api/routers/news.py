"""
ROUTER DE NOTÍCIAS - API FASTAPI
==============================

Endpoints para operações relacionadas a notícias de clubes de futebol.
Implementa CRUD completo com filtros, paginação e validação.

Autor: Sistema de API RESTful
Data: 2025-08-06
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
import logging
from datetime import datetime, timedelta

from api.schemas import (
    NoticiaClubeResponse, NoticiaClubeList, NoticiaClubeCreate, 
    NoticiaClubeUpdate, ErrorResponse
)
from api.security import get_current_api_key
from Coleta_de_dados.database import SessionLocal
from Coleta_de_dados.database.models import NoticiaClube, Clube

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
router = APIRouter(prefix="/news", tags=["news"])
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE NOTÍCIAS
# ============================================================================

@router.get(
    "/",
    response_model=NoticiaClubeList,
    summary="Listar notícias",
    description="Retorna uma lista paginada de notícias com filtros opcionais",
    responses={
        200: {"description": "Lista de notícias retornada com sucesso"},
        400: {"model": ErrorResponse, "description": "Parâmetros inválidos"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def list_news(
    clube_id: Optional[int] = Query(None, description="Filtrar por ID do clube"),
    fonte: Optional[str] = Query(None, description="Filtrar por fonte da notícia"),
    data_inicio: Optional[datetime] = Query(None, description="Data de início para filtrar notícias (inclusive)"),
    data_fim: Optional[datetime] = Query(None, description="Data de término para filtrar notícias (inclusive)"),
    busca: Optional[str] = Query(None, description="Busca textual no título e resumo da notícia"),
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista notícias de clubes com filtros opcionais.
    
    - **clube_id**: Filtrar por ID do clube
    - **fonte**: Filtrar por fonte da notícia
    - **data_inicio/data_fim**: Filtrar por intervalo de datas
    - **busca**: Busca textual no título e resumo
    - **page**: Número da página (padrão: 1)
    - **size**: Itens por página (padrão: 20, máximo: 100)
    """
    try:
        # Inicia a query
        query = db.query(NoticiaClube)
        
        # Aplica filtros
        if clube_id is not None:
            query = query.filter(NoticiaClube.clube_id == clube_id)
            
        if fonte:
            query = query.filter(NoticiaClube.fonte.ilike(f"%{fonte}%"))
            
        if data_inicio:
            query = query.filter(NoticiaClube.data_publicacao >= data_inicio)
            
        if data_fim:
            # Adiciona 1 dia para incluir todo o dia final
            data_fim = data_fim + timedelta(days=1)
            query = query.filter(NoticiaClube.data_publicacao <= data_fim)
            
        if busca:
            search = f"%{busca}%"
            query = query.filter(
                or_(
                    NoticiaClube.titulo.ilike(search),
                    NoticiaClube.resumo.ilike(search),
                    NoticiaClube.conteudo_completo.ilike(search)
                )
            )
        
        # Ordena por data de publicação (mais recentes primeiro)
        query = query.order_by(NoticiaClube.data_publicacao.desc())
        
        # Calcula a paginação
        total = query.count()
        offset = (page - 1) * size
        pages = (total + size - 1) // size  # Arredonda para cima a divisão
        
        # Aplica a paginação
        noticias = query.offset(offset).limit(size).all()
        
        # Prepara a resposta
        items = []
        for noticia in noticias:
            # Adiciona o nome do clube a cada notícia
            item = NoticiaClubeResponse.from_orm(noticia)
            if noticia.clube:
                item.clube_nome = noticia.clube.nome
            items.append(item)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar notícias: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.get(
    "/{noticia_id}",
    response_model=NoticiaClubeResponse,
    summary="Obter notícia por ID",
    description="Retorna os detalhes de uma notícia específica pelo seu ID",
    responses={
        200: {"description": "Notícia encontrada"},
        404: {"model": ErrorResponse, "description": "Notícia não encontrada"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_news(
    noticia_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Obtém uma notícia específica pelo ID.
    
    - **noticia_id**: ID único da notícia
    """
    try:
        noticia = db.query(NoticiaClube).filter(NoticiaClube.id == noticia_id).first()
        
        if not noticia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Notícia não encontrada", "message": f"Nenhuma notícia encontrada com o ID {noticia_id}"}
            )
        
        # Converte para o modelo de resposta e adiciona o nome do clube
        response = NoticiaClubeResponse.from_orm(noticia)
        if noticia.clube:
            response.clube_nome = noticia.clube.nome
            
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter notícia {noticia_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.get(
    "/clube/{clube_id}",
    response_model=NoticiaClubeList,
    summary="Listar notícias por clube",
    description="Retorna as notícias de um clube específico",
    responses={
        200: {"description": "Notícias do clube retornadas com sucesso"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_club_news(
    clube_id: int,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=50, description="Itens por página"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista as notícias de um clube específico.
    
    - **clube_id**: ID do clube
    - **page**: Número da página (padrão: 1)
    - **size**: Itens por página (padrão: 10, máximo: 50)
    """
    try:
        # Verifica se o clube existe
        clube = db.query(Clube).filter(Clube.id == clube_id).first()
        if not clube:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Clube não encontrado", "message": f"Nenhum clube encontrado com o ID {clube_id}"}
            )
        
        # Query para as notícias do clube
        query = db.query(NoticiaClube).filter(NoticiaClube.clube_id == clube_id)
        
        # Ordena por data de publicação (mais recentes primeiro)
        query = query.order_by(NoticiaClube.data_publicacao.desc())
        
        # Calcula a paginação
        total = query.count()
        offset = (page - 1) * size
        pages = (total + size - 1) // size  # Arredonda para cima a divisão
        
        # Aplica a paginação
        noticias = query.offset(offset).limit(size).all()
        
        # Prepara a resposta
        items = [NoticiaClubeResponse.from_orm(noticia) for noticia in noticias]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar notícias do clube {clube_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.get(
    "/recentes/ultimas-24h",
    response_model=NoticiaClubeList,
    summary="Notícias das últimas 24 horas",
    description="Retorna as notícias publicadas nas últimas 24 horas",
    responses={
        200: {"description": "Notícias recentes retornadas com sucesso"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def get_recent_news(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=50, description="Itens por página"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Lista as notícias publicadas nas últimas 24 horas.
    
    - **page**: Número da página (padrão: 1)
    - **size**: Itens por página (padrão: 10, máximo: 50)
    """
    try:
        # Calcula a data de 24 horas atrás
        data_limite = datetime.utcnow() - timedelta(hours=24)
        
        # Query para notícias recentes
        query = db.query(NoticiaClube).filter(NoticiaClube.data_publicacao >= data_limite)
        
        # Ordena por data de publicação (mais recentes primeiro)
        query = query.order_by(NoticiaClube.data_publicacao.desc())
        
        # Calcula a paginação
        total = query.count()
        offset = (page - 1) * size
        pages = (total + size - 1) // size  # Arredonda para cima a divisão
        
        # Aplica a paginação
        noticias = query.offset(offset).limit(size).all()
        
        # Prepara a resposta
        items = []
        for noticia in noticias:
            # Adiciona o nome do clube a cada notícia
            item = NoticiaClubeResponse.from_orm(noticia)
            if noticia.clube:
                item.clube_nome = noticia.clube.nome
            items.append(item)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar notícias recentes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=NoticiaClubeResponse,
    summary="Criar nova notícia",
    description="Cria uma nova notícia para um clube",
    responses={
        201: {"description": "Notícia criada com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        409: {"model": ErrorResponse, "description": "Notícia já existe"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def create_news(
    noticia_data: NoticiaClubeCreate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Cria uma nova notícia para um clube.
    
    - **titulo**: Título da notícia (obrigatório)
    - **url_noticia**: URL da notícia (obrigatório)
    - **fonte**: Fonte da notícia (obrigatório)
    - **data_publicacao**: Data de publicação (padrão: agora)
    - **resumo**: Resumo da notícia (opcional)
    - **conteudo_completo**: Conteúdo completo da notícia (opcional)
    - **autor**: Autor da notícia (opcional)
    - **imagem_destaque**: URL da imagem de destaque (opcional)
    - **clube_id**: ID do clube (obrigatório)
    """
    try:
        # Verifica se o clube existe
        clube = db.query(Clube).filter(Clube.id == noticia_data.clube_id).first()
        if not clube:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Clube não encontrado", "message": f"Nenhum clube encontrado com o ID {noticia_data.clube_id}"}
            )
        
        # Verifica se já existe uma notícia com a mesma URL
        existente = db.query(NoticiaClube).filter(
            NoticiaClube.url_noticia == noticia_data.url_noticia
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Notícia já existe", "message": f"Já existe uma notícia com a URL fornecida (ID: {existente.id})"}
            )
        
        # Cria a nova notícia
        nova_noticia = NoticiaClube(
            **noticia_data.dict(exclude_unset=True),
            created_at=datetime.utcnow()
        )
        
        db.add(nova_noticia)
        db.commit()
        db.refresh(nova_noticia)
        
        # Prepara a resposta com o nome do clube
        response = NoticiaClubeResponse.from_orm(nova_noticia)
        response.clube_nome = clube.nome
        
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar notícia: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.put(
    "/{noticia_id}",
    response_model=NoticiaClubeResponse,
    summary="Atualizar notícia",
    description="Atualiza uma notícia existente",
    responses={
        200: {"description": "Notícia atualizada com sucesso"},
        400: {"model": ErrorResponse, "description": "Dados inválidos"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        404: {"model": ErrorResponse, "description": "Notícia não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def update_news(
    noticia_id: int,
    noticia_data: NoticiaClubeUpdate,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Atualiza uma notícia existente.
    
    - **noticia_id**: ID da notícia a ser atualizada
    - **titulo**: Novo título (opcional)
    - **url_noticia**: Nova URL (opcional)
    - **fonte**: Nova fonte (opcional)
    - **data_publicacao**: Nova data de publicação (opcional)
    - **resumo**: Novo resumo (opcional)
    - **conteudo_completo**: Novo conteúdo completo (opcional)
    - **autor**: Novo autor (opcional)
    - **imagem_destaque**: Nova URL de imagem (opcional)
    - **clube_id**: Novo ID do clube (opcional)
    """
    try:
        # Busca a notícia
        noticia = db.query(NoticiaClube).filter(NoticiaClube.id == noticia_id).first()
        
        if not noticia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Notícia não encontrada", "message": f"Nenhuma notícia encontrada com o ID {noticia_id}"}
            )
        
        # Verifica se o clube existe se estiver sendo atualizado
        if noticia_data.clube_id is not None and noticia_data.clube_id != noticia.clube_id:
            clube = db.query(Clube).filter(Clube.id == noticia_data.clube_id).first()
            if not clube:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": "Clube não encontrado", "message": f"Nenhum clube encontrado com o ID {noticia_data.clube_id}"}
                )
        
        # Verifica se a nova URL já existe em outra notícia
        if noticia_data.url_noticia is not None and noticia_data.url_noticia != noticia.url_noticia:
            existente = db.query(NoticiaClube).filter(
                NoticiaClube.url_noticia == noticia_data.url_noticia,
                NoticiaClube.id != noticia_id
            ).first()
            
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": "URL já em uso", "message": f"A URL fornecida já está sendo usada por outra notícia (ID: {existente.id})"}
                )
        
        # Atualiza os campos fornecidos
        for field, value in noticia_data.dict(exclude_unset=True).items():
            setattr(noticia, field, value)
        
        # Atualiza a data de atualização
        noticia.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(noticia)
        
        # Prepara a resposta com o nome do clube
        response = NoticiaClubeResponse.from_orm(noticia)
        if noticia.clube:
            response.clube_nome = noticia.clube.nome
            
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar notícia {noticia_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

@router.delete(
    "/{noticia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir notícia",
    description="Remove uma notícia do sistema",
    responses={
        204: {"description": "Notícia excluída com sucesso"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        404: {"model": ErrorResponse, "description": "Notícia não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def delete_news(
    noticia_id: int,
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Remove uma notícia do sistema.
    
    - **noticia_id**: ID da notícia a ser removida
    """
    try:
        # Busca a notícia
        noticia = db.query(NoticiaClube).filter(NoticiaClube.id == noticia_id).first()
        
        if not noticia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Notícia não encontrada", "message": f"Nenhuma notícia encontrada com o ID {noticia_id}"}
            )
        
        # Remove a notícia
        db.delete(noticia)
        db.commit()
        
        return None
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao excluir notícia {noticia_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno do servidor", "message": str(e)}
        )

# ============================================================================
# ENDPOINTS DE COLETA DE NOTÍCIAS
# ============================================================================

@router.post(
    "/coletar/clube/{clube_id}",
    summary="Coletar notícias para um clube",
    description="Aciona a coleta de notícias para um clube específico",
    responses={
        200: {"description": "Coleta de notícias iniciada com sucesso"},
        404: {"model": ErrorResponse, "description": "Clube não encontrado"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def coletar_noticias_clube(
    clube_id: int,
    limite: int = Query(10, ge=1, le=50, description="Número máximo de notícias a coletar"),
    api_key: str = Depends(get_current_api_key),
    db: Session = Depends(get_db)
):
    """
    Aciona a coleta de notícias para um clube específico.
    
    - **clube_id**: ID do clube para coletar notícias
    - **limite**: Número máximo de notícias a coletar (padrão: 10, máximo: 50)
    """
    try:
        from Coleta_de_dados.apis.news.collector import NewsCollector
        
        # Verifica se o clube existe
        clube = db.query(Clube).filter(Clube.id == clube_id).first()
        if not clube:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Clube não encontrado", "message": f"Nenhum clube encontrado com o ID {clube_id}"}
            )
        
        # Inicia o coletor
        collector = NewsCollector(db)
        
        # Executa a coleta
        resultado = collector.coletar_noticias_clube(clube_id, limite)
        
        return {
            "message": "Coleta de notícias concluída com sucesso",
            "clube_id": clube_id,
            "clube_nome": clube.nome,
            "noticias_coletadas": resultado.get("noticias_coletadas", 0),
            "status": resultado.get("status", "desconhecido")
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar notícias para o clube {clube_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro ao coletar notícias", "message": str(e)}
        )

@router.post(
    "/coletar/todos",
    summary="Coletar notícias para todos os clubes",
    description="Aciona a coleta de notícias para todos os clubes ativos",
    responses={
        200: {"description": "Coleta de notícias iniciada com sucesso"},
        401: {"model": ErrorResponse, "description": "Não autorizado"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    }
)
async def coletar_noticias_todos(
    limite_por_clube: int = Query(5, ge=1, le=20, description="Número máximo de notícias por clube"),
    api_key: str = Depends(get_current_api_key)
):
    """
    Aciona a coleta de notícias para todos os clubes ativos.
    
    - **limite_por_clube**: Número máximo de notícias a coletar por clube (padrão: 5, máximo: 20)
    """
    try:
        from Coleta_de_dados.apis.news.collector import coletar_noticias_para_todos_clubes
        
        # Executa a coleta para todos os clubes
        resultado = coletar_noticias_para_todos_clubes(limite_por_clube)
        
        return {
            "message": "Coleta de notícias para todos os clubes concluída",
            "total_clubes": resultado.get("total_clubes", 0),
            "total_noticias_coletadas": resultado.get("total_noticias_coletadas", 0),
            "status": resultado.get("status", "desconhecido")
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar notícias para todos os clubes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro ao coletar notícias", "message": str(e)}
        )
