"""
ROTAS DE REDES SOCIAIS
=======================

Rotas para gerenciamento de posts de redes sociais dos clubes.

Este módulo fornece endpoints para:
- Listar posts de redes sociais por clube
- Obter detalhes de um post específico
- Criar/atualizar posts (para uso interno)
- Coletar dados de redes sociais para um clube

Autor: Sistema de API RESTful
Data: 2025-08-06
Versão: 1.0
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

# Importações locais
from ..schemas import (
    PostRedeSocialResponse,
    PostRedeSocialCreate,
    PostRedeSocialUpdate,
    PostRedeSocialList,
    PaginationParams,
    MessageResponse
)
from ..dependencies import get_db, get_current_user
from Coleta_de_dados.database.models import User, Clube, PostRedeSocial
from Coleta_de_dados.database.config import db_manager
from Coleta_de_dados.apis.social.collector import SocialMediaCollector, coletar_dados_para_todos_clubes

# Cria o roteador
router = APIRouter(
    prefix="/api/v1/social",
    tags=["social"],
    responses={
        404: {"description": "Recurso não encontrado"},
        403: {"description": "Acesso negado"},
        429: {"description": "Muitas requisições"}
    }
)

def get_social_collector(db: Session = Depends(get_db)) -> SocialMediaCollector:
    """Retorna uma instância do coletor de redes sociais."""
    return SocialMediaCollector(db)

@router.get("/posts/clube/{clube_id}", response_model=PostRedeSocialList)
async def listar_posts_por_clube(
    clube_id: int,
    rede_social: Optional[str] = Query(None, description="Filtrar por rede social (ex: 'Twitter', 'Instagram')"),
    data_inicio: Optional[datetime] = Query(None, description="Data de início para filtro"),
    data_fim: Optional[datetime] = Query(None, description="Data de término para filtro"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista posts de redes sociais de um clube específico.
    
    Permite filtrar por rede social e período de tempo.
    """
    # Verifica se o clube existe
    clube = db.query(Clube).filter(Clube.id == clube_id).first()
    if not clube:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clube com ID {clube_id} não encontrado."
        )
    
    # Constrói a consulta
    query = db.query(PostRedeSocial).filter(PostRedeSocial.clube_id == clube_id)
    
    # Aplica filtros
    if rede_social:
        query = query.filter(PostRedeSocial.rede_social.ilike(f"%{rede_social}%"))
    
    if data_inicio:
        query = query.filter(PostRedeSocial.data_postagem >= data_inicio)
    
    if data_fim:
        # Ajusta a data_fim para incluir todo o dia
        data_fim_ajustada = data_fim + timedelta(days=1)
        query = query.filter(PostRedeSocial.data_postagem < data_fim_ajustada)
    
    # Ordena por data de postagem (mais recentes primeiro)
    query = query.order_by(PostRedeSocial.data_postagem.desc())
    
    # Aplica paginação
    total = query.count()
    items = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size).all()
    
    # Calcula o total de páginas
    pages = (total + pagination.size - 1) // pagination.size
    
    # Converte para o modelo de resposta
    response_items = []
    for item in items:
        response_items.append(PostRedeSocialResponse(
            id=item.id,
            clube_id=item.clube_id,
            clube_nome=clube.nome,
            rede_social=item.rede_social,
            post_id=item.post_id,
            conteudo=item.conteudo,
            data_postagem=item.data_postagem,
            curtidas=item.curtidas,
            comentarios=item.comentarios,
            compartilhamentos=item.compartilhamentos,
            url_post=item.url_post,
            midia_url=item.midia_url,
            created_at=item.created_at,
            updated_at=item.updated_at
        ))
    
    return PostRedeSocialList(
        items=response_items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )

@router.get("/posts/{post_id}", response_model=PostRedeSocialResponse)
async def obter_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém os detalhes de um post específico.
    """
    post = db.query(PostRedeSocial).filter(PostRedeSocial.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post com ID {post_id} não encontrado."
        )
    
    # Obtém o nome do clube
    clube = db.query(Clube).filter(Clube.id == post.clube_id).first()
    
    return PostRedeSocialResponse(
        id=post.id,
        clube_id=post.clube_id,
        clube_nome=clube.nome if clube else None,
        rede_social=post.rede_social,
        post_id=post.post_id,
        conteudo=post.conteudo,
        data_postagem=post.data_postagem,
        curtidas=post.curtidas,
        comentarios=post.comentarios,
        compartilhamentos=post.compartilhamentos,
        url_post=post.url_post,
        midia_url=post.midia_url,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.post("/coletar/clube/{clube_id}", response_model=MessageResponse)
async def coletar_posts_clube(
    clube_id: int,
    limite: int = Query(5, description="Número máximo de posts a coletar", ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aciona a coleta de posts de redes sociais para um clube específico.
    
    Esta rota é protegida e requer autenticação.
    """
    # Verifica se o usuário tem permissão
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acionar a coleta de dados."
        )
    
    # Verifica se o clube existe
    clube = db.query(Clube).filter(Clube.id == clube_id).first()
    if not clube:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clube com ID {clube_id} não encontrado."
        )
    
    # Inicia a coleta
    try:
        collector = SocialMediaCollector(db)
        qtd_posts = collector.coletar_posts_recentes(clube_id, limite=limite)
        
        return MessageResponse(
            message=f"Coleta de posts para {clube.nome} concluída com sucesso.",
            data={
                "clube_id": clube_id,
                "clube_nome": clube.nome,
                "posts_coletados": qtd_posts
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao coletar posts: {str(e)}"
        )

@router.post("/coletar/todos", response_model=MessageResponse)
async def coletar_posts_todos_clubes(
    limite_por_clube: int = Query(3, description="Número máximo de posts por clube", ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aciona a coleta de posts de redes sociais para todos os clubes ativos.
    
    Esta rota é protegida e requer autenticação de administrador.
    """
    # Verifica se o usuário tem permissão
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acionar a coleta de dados para todos os clubes."
        )
    
    try:
        # Executa a coleta em segundo plano
        # Em produção, considere usar um worker em background (ex: Celery)
        from concurrent.futures import ThreadPoolExecutor
        
        def run_collection():
            return coletar_dados_para_todos_clubes(limite_por_clube=limite_por_clube)
        
        with ThreadPoolExecutor() as executor:
            future = executor.submit(run_collection)
            resultado = future.result()
        
        return MessageResponse(
            message="Coleta de posts para todos os clubes iniciada com sucesso.",
            data=resultado
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar coleta: {str(e)}"
        )

@router.get("/estatisticas/engajamento/{clube_id}")
async def obter_estatisticas_engajamento(
    clube_id: int,
    periodo_dias: int = Query(30, description="Período em dias para análise", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém estatísticas de engajamento de um clube nas redes sociais.
    
    Retorna métricas como:
    - Total de posts por rede social
    - Média de engajamento (curtidas, comentários, compartilhamentos)
    - Melhor horário para postar
    - Conteúdos mais engajados
    """
    # Verifica se o clube existe
    clube = db.query(Clube).filter(Clube.id == clube_id).first()
    if not clube:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clube com ID {clube_id} não encontrado."
        )
    
    # Calcula a data de corte
    data_corte = datetime.utcnow() - timedelta(days=periodo_dias)
    
    # Consulta os posts do período
    posts = db.query(PostRedeSocial)\
        .filter(
            PostRedeSocial.clube_id == clube_id,
            PostRedeSocial.data_postagem >= data_corte
        )\
        .all()
    
    if not posts:
        return {
            "message": f"Nenhum post encontrado para o clube {clube.nome} no período selecionado.",
            "periodo_dias": periodo_dias,
            "data_inicio": data_corte.isoformat(),
            "total_posts": 0
        }
    
    # Calcula métricas
    total_posts = len(posts)
    redes_sociais = {}
    engajamento_total = {
        'curtidas': 0,
        'comentarios': 0,
        'compartilhamentos': 0
    }
    
    # Agrupa por rede social e calcula métricas
    for post in posts:
        rede = post.rede_social
        if rede not in redes_sociais:
            redes_sociais[rede] = {
                'total_posts': 0,
                'curtidas': 0,
                'comentarios': 0,
                'compartilhamentos': 0,
                'media_engajamento': 0
            }
        
        redes_sociais[rede]['total_posts'] += 1
        redes_sociais[rede]['curtidas'] += post.curtidas
        redes_sociais[rede]['comentarios'] += post.comentarios
        redes_sociais[rede]['compartilhamentos'] += post.compartilhamentos
        
        engajamento_total['curtidas'] += post.curtidas
        engajamento_total['comentarios'] += post.comentarios
        engajamento_total['compartilhamentos'] += post.compartilhamentos
    
    # Calcula médias
    for rede in redes_sociais:
        redes_sociais[rede]['media_engajamento'] = (
            redes_sociais[rede]['curtidas'] +
            redes_sociais[rede]['comentarios'] * 2 +  # Comentários valem mais
            redes_sociais[rede]['compartilhamentos'] * 3  # Compartilhamentos valem ainda mais
        ) / max(1, redes_sociais[rede]['total_posts'])
    
    # Ordena redes sociais por engajamento
    redes_ordenadas = sorted(
        redes_sociais.items(),
        key=lambda x: x[1]['media_engajamento'],
        reverse=True
    )
    
    # Prepara a resposta
    return {
        "clube_id": clube_id,
        "clube_nome": clube.nome,
        "periodo_dias": periodo_dias,
        "data_inicio": data_corte.isoformat(),
        "total_posts": total_posts,
        "engajamento_total": engajamento_total,
        "redes_sociais": {
            rede: {
                "total_posts": dados['total_posts'],
                "curtidas": dados['curtidas'],
                "comentarios": dados['comentarios'],
                "compartilhamentos": dados['compartilhamentos'],
                "media_engajamento": dados['media_engajamento']
            }
            for rede, dados in redes_ordenadas
        },
        "rede_mais_engajada": redes_ordenadas[0][0] if redes_ordenadas else None,
        "media_engajamento_geral": (
            engajamento_total['curtidas'] +
            engajamento_total['comentarios'] * 2 +
            engajamento_total['compartilhamentos'] * 3
        ) / max(1, total_posts)
    }
