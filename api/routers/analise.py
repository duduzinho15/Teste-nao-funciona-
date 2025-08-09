"""
ROUTER DE ANÁLISE DE SENTIMENTO
==============================

Este módulo fornece endpoints para análise de sentimento de notícias e posts de redes sociais.
Permite a análise em tempo real e o processamento em lote de conteúdo textual.

Endpoints:
- POST /api/v1/analise/sentimento: Analisa o sentimento de um texto
- POST /api/v1/analise/noticias/{noticia_id}: Analisa o sentimento de uma notícia específica
- POST /api/v1/analise/noticias/lote: Processa análise de sentimento em lote para múltiplas notícias
- GET /api/v1/analise/estatisticas: Obtém estatísticas sobre as análises realizadas

Autor: Sistema de Análise de Sentimento
Data: 2025-08-10
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from Coleta_de_dados.database import get_db
from Coleta_de_dados.analise.sentimento import (
    analisar_sentimento_texto,
    analisar_noticia,
    analisar_lote_noticias
)
from ..schemas import (
    SentimentoClubeSchema,
    NoticiaClubeResponse,
    MessageResponse,
    ErrorResponse
)
from Coleta_de_dados.database.models import NoticiaClube

# Configuração de logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/analise",
    tags=["Análise de Sentimento"],
    responses={
        404: {"description": "Recurso não encontrado"},
        500: {"description": "Erro interno do servidor"}
    }
)

class AnaliseTextoRequest(BaseModel):
    """Schema para requisição de análise de texto."""
    texto: str = Field(..., description="Texto a ser analisado")
    titulo: Optional[str] = Field(None, description="Título do conteúdo (opcional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texto": "O time jogou muito bem e garantiu uma vitória espetacular no clássico.",
                "titulo": "Vitória espetacular no clássico"
            }
        }

class AnaliseLoteRequest(BaseModel):
    """Schema para requisição de análise em lote."""
    noticias: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de notícias para análise. Cada item deve conter 'id', 'titulo' e 'conteudo_completo'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "noticias": [
                    {
                        "id": 1,
                        "titulo": "Time vence partida emocionante",
                        "conteudo_completo": "Em um jogo emocionante, o time venceu por 2x1..."
                    },
                    {
                        "id": 2,
                        "titulo": "Derrota amarga no clássico",
                        "conteudo_completo": "O time perdeu por 3x0 em uma atuação abaixo do esperado..."
                    }
                ]
            }
        }

@router.post(
    "/sentimento",
    response_model=SentimentoClubeSchema,
    summary="Analisa o sentimento de um texto",
    description="""
    Realiza a análise de sentimento de um texto fornecido.
    Retorna uma pontuação de sentimento entre -1 (negativo) e 1 (positivo),
    juntamente com informações sobre a análise.
    """
)
async def analisar_texto(request: AnaliseTextoRequest):
    """
    Analisa o sentimento de um texto fornecido.
    
    Args:
        request: Objeto contendo o texto a ser analisado e título opcional
        
    Returns:
        Resultado da análise de sentimento
    """
    try:
        resultado = analisar_sentimento_texto(request.texto, request.titulo)
        return resultado
    except Exception as e:
        logger.error(f"Erro ao analisar texto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a análise de sentimento: {str(e)}"
        )

@router.post(
    "/noticias/{noticia_id}",
    response_model=NoticiaClubeResponse,
    summary="Analisa o sentimento de uma notícia específica",
    description="""
    Busca uma notícia pelo ID, realiza a análise de sentimento e atualiza
    os campos correspondentes no banco de dados.
    """
)
async def analisar_noticia_endpoint(
    noticia_id: int,
    db: Session = Depends(get_db)
):
    """
    Analisa o sentimento de uma notícia específica e atualiza o banco de dados.
    
    Args:
        noticia_id: ID da notícia a ser analisada
        db: Sessão do banco de dados
        
    Returns:
        Notícia atualizada com os resultados da análise de sentimento
    """
    try:
        # Busca a notícia no banco de dados
        noticia = db.query(NoticiaClube).filter(NoticiaClube.id == noticia_id).first()
        
        if not noticia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notícia com ID {noticia_id} não encontrada"
            )
        
        # Converte o objeto SQLAlchemy para dicionário para análise
        noticia_dict = {
            "id": noticia.id,
            "titulo": noticia.titulo,
            "conteudo_completo": noticia.conteudo_completo or "",
            "resumo": noticia.resumo or ""
        }
        
        # Realiza a análise de sentimento
        resultado = analisar_noticia(noticia_dict)
        
        # Atualiza os campos da notícia com os resultados da análise
        noticia.sentimento_geral = resultado["sentimento_geral"]
        noticia.confianca_sentimento = resultado["confianca"]
        noticia.polaridade = resultado["polaridade"]
        noticia.topicos = ", ".join(resultado["topicos"]) if resultado["topicos"] else None
        noticia.palavras_chave = ", ".join(resultado["palavras_chave"]) if resultado["palavras_chave"] else None
        noticia.modelo_analise = resultado["modelo"]
        noticia.analisado_em = datetime.now()
        
        # Salva as alterações no banco de dados
        db.commit()
        db.refresh(noticia)
        
        return noticia
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao analisar notícia {noticia_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a análise da notícia: {str(e)}"
        )

@router.post(
    "/noticias/lote",
    response_model=List[Dict[str, Any]],
    summary="Analisa o sentimento de múltiplas notícias em lote",
    description="""
    Processa a análise de sentimento para várias notícias de uma só vez.
    Retorna os resultados da análise para cada notícia processada.
    """
)
async def analisar_lote_noticias_endpoint(
    request: AnaliseLoteRequest,
    db: Session = Depends(get_db)
):
    """
    Analisa o sentimento de múltiplas notícias em lote.
    
    Args:
        request: Objeto contendo a lista de notícias a serem analisadas
        db: Sessão do banco de dados
        
    Returns:
        Lista de resultados da análise para cada notícia
    """
    try:
        if not request.noticias:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma notícia fornecida para análise"
            )
        
        # Realiza a análise em lote
        resultados = analisar_lote_noticias(request.noticias)
        
        # Atualiza as notícias no banco de dados (se tiverem IDs)
        for resultado in resultados:
            if 'noticia_id' in resultado:
                try:
                    noticia = db.query(NoticiaClube).get(resultado['noticia_id'])
                    if noticia:
                        noticia.sentimento_geral = resultado["sentimento_geral"]
                        noticia.confianca_sentimento = resultado["confianca"]
                        noticia.polaridade = resultado["polaridade"]
                        noticia.topicos = ", ".join(resultado["topicos"]) if resultado["topicos"] else None
                        noticia.palavras_chave = ", ".join(resultado["palavras_chave"]) if resultado["palavras_chave"] else None
                        noticia.modelo_analise = resultado["modelo"]
                        noticia.analisado_em = datetime.now()
                        
                        db.add(noticia)
                except Exception as e:
                    logger.error(f"Erro ao atualizar notícia {resultado.get('noticia_id')}: {str(e)}")
                    continue
        
        db.commit()
        
        return resultados
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao processar análise em lote: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a análise em lote: {str(e)}"
        )

@router.get(
    "/estatisticas",
    response_model=Dict[str, Any],
    summary="Obtém estatísticas sobre as análises realizadas",
    description="""
    Retorna estatísticas sobre as análises de sentimento realizadas,
    como total de análises, média de sentimento, distribuição de polaridades, etc.
    """
)
async def obter_estatisticas(
    dias: int = Query(30, description="Número de dias para análise (padrão: 30)", ge=1),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas sobre as análises de sentimento realizadas.
    
    Args:
        dias: Número de dias para análise (padrão: 30)
        db: Sessão do banco de dados
        
    Returns:
        Dicionário com estatísticas das análises
    """
    try:
        data_limite = datetime.now() - timedelta(days=dias)
        
        # Consulta para obter estatísticas básicas
        total_noticias = db.query(NoticiaClube).count()
        total_analisadas = db.query(NoticiaClube).filter(NoticiaClube.analisado_em.isnot(None)).count()
        
        # Média de sentimento
        media_sentimento = db.query(
            db.func.avg(NoticiaClube.sentimento_geral)
        ).filter(NoticiaClube.sentimento_geral.isnot(None)).scalar() or 0.0
        
        # Distribuição de polaridades
        polaridades = db.query(
            NoticiaClube.polaridade,
            db.func.count(NoticiaClube.id)
        ).filter(
            NoticiaClube.polaridade.isnot(None)
        ).group_by(NoticiaClube.polaridade).all()
        
        # Distribuição por confiança
        confianca_media = db.query(
            db.func.avg(NoticiaClube.confianca_sentimento)
        ).filter(NoticiaClube.confianca_sentimento.isnot(None)).scalar() or 0.0
        
        # Últimas análises
        ultimas_analises = db.query(NoticiaClube).filter(
            NoticiaClube.analisado_em.isnot(None)
        ).order_by(
            NoticiaClube.analisado_em.desc()
        ).limit(5).all()
        
        # Prepara a resposta
        estatisticas = {
            "total_noticias": total_noticias,
            "total_analisadas": total_analisadas,
            "porcentagem_analisada": (total_analisadas / total_noticias * 100) if total_noticias > 0 else 0,
            "media_sentimento": round(float(media_sentimento), 4),
            "confianca_media": round(float(confianca_media), 4),
            "distribuicao_polaridades": {
                polaridade: count for polaridade, count in polaridades
            },
            "ultimas_analises": [
                {
                    "id": n.id,
                    "titulo": n.titulo,
                    "sentimento_geral": n.sentimento_geral,
                    "polaridade": n.polaridade,
                    "analisado_em": n.analisado_em.isoformat() if n.analisado_em else None
                }
                for n in ultimas_analises
            ],
            "periodo_analisado": {
                "inicio": data_limite.isoformat(),
                "fim": datetime.now().isoformat(),
                "dias": dias
            }
        }
        
        return estatisticas
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )
