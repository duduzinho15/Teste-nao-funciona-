#!/usr/bin/env python3
"""
Roteador para Endpoints de Análise de Sentimento
================================================

Este módulo fornece endpoints para análise de sentimento de notícias e posts
de redes sociais dos clubes.

Autor: Sistema de Análise de Sentimento ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import os

from api import schemas
from api.database import get_db

router = APIRouter(prefix="/analise", tags=["Análise"])

def get_db_path():
    """Obtém o caminho para o banco de dados."""
    possible_paths = [
        "Banco_de_dados/aposta.db",
        "Coleta_de_dados/database/football_data.db",
        "aposta.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

@router.get("/sentimento/{clube_id}", response_model=schemas.SentimentoClubeSchema)
def get_sentimento_clube(
    clube_id: int, 
    db: Session = Depends(get_db),
    incluir_posts: bool = Query(True, description="Incluir análise de posts de redes sociais")
):
    """
    Obtém a análise de sentimento para um clube específico.
    
    Args:
        clube_id: ID do clube
        incluir_posts: Se deve incluir análise de posts de redes sociais
        
    Returns:
        Análise de sentimento do clube
    """
    try:
        # Conectar ao banco SQLite
        db_path = get_db_path()
        if not db_path:
            raise HTTPException(status_code=500, detail="Banco de dados não encontrado")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se o clube existe
        cursor.execute("SELECT nome FROM clubes WHERE id = ?", (clube_id,))
        clube = cursor.fetchone()
        
        if not clube:
            raise HTTPException(status_code=404, detail="Clube não encontrado")
        
        nome_clube = clube[0]
        
        # Análise de sentimento das notícias
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(score_sentimento) as score_medio,
                AVG(confianca_sentimento) as confianca_media,
                MAX(analisado_em) as ultima_analise
            FROM noticias_clubes 
            WHERE clube_id = ? AND sentimento IS NOT NULL
        """, (clube_id,))
        
        stats_noticias = cursor.fetchone()
        total_noticias = stats_noticias[0] or 0
        score_medio_noticias = stats_noticias[1] or 0.0
        confianca_media = stats_noticias[3] or 0.0
        ultima_analise = stats_noticias[4]
        
        # Análise de sentimento dos posts (se solicitado)
        sentimento_medio_posts = None
        posts_analisados = None
        
        if incluir_posts:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(score_sentimento) as score_medio
                FROM posts_redes_sociais 
                WHERE clube_id = ? AND sentimento IS NOT NULL
            """, (clube_id,))
            
            stats_posts = cursor.fetchone()
            posts_analisados = stats_posts[0] or 0
            sentimento_medio_posts = stats_posts[1] or 0.0
        
        # Calcular sentimento geral
        scores = [score_medio_noticias]
        if sentimento_medio_posts is not None:
            scores.append(sentimento_medio_posts)
        
        score_medio_geral = sum(scores) / len(scores) if scores else 0.0
        
        if score_medio_geral > 0.1:
            sentimento_geral = 'positivo'
        elif score_medio_geral < -0.1:
            sentimento_geral = 'negativo'
        else:
            sentimento_geral = 'neutro'
        
        conn.close()
        
        return {
            "clube_id": clube_id,
            "nome_clube": nome_clube,
            "sentimento_medio_noticias": score_medio_noticias,
            "noticias_analisadas": total_noticias,
            "sentimento_medio_posts": sentimento_medio_posts,
            "posts_analisados": posts_analisados,
            "sentimento_geral": sentimento_geral,
            "confianca_media": confianca_media,
            "ultima_atualizacao": ultima_analise
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/sentimento/estatisticas", response_model=schemas.SentimentoEstatisticasSchema)
def get_estatisticas_sentimento(
    db: Session = Depends(get_db),
    dias_atras: int = Query(30, description="Número de dias para análise", ge=1, le=365)
):
    """
    Obtém estatísticas gerais de sentimento.
    
    Args:
        dias_atras: Número de dias para análise
        
    Returns:
        Estatísticas gerais de sentimento
    """
    try:
        # Conectar ao banco SQLite
        db_path = get_db_path()
        if not db_path:
            raise HTTPException(status_code=500, detail="Banco de dados não encontrado")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Data limite para análise
        data_limite = datetime.now() - timedelta(days=dias_atras)
        
        # Estatísticas de notícias
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivas,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativas,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutras,
                AVG(score_sentimento) as score_medio
            FROM noticias_clubes 
            WHERE sentimento IS NOT NULL AND created_at >= ?
        """, (data_limite,))
        
        stats_noticias = cursor.fetchone()
        total_noticias = stats_noticias[0] or 0
        score_medio_noticias = stats_noticias[4] or 0.0
        
        # Estatísticas de posts
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN sentimento = 'positivo' THEN 1 END) as positivos,
                COUNT(CASE WHEN sentimento = 'negativo' THEN 1 END) as negativos,
                COUNT(CASE WHEN sentimento = 'neutro' THEN 1 END) as neutros,
                AVG(score_sentimento) as score_medio
            FROM posts_redes_sociais 
            WHERE sentimento IS NOT NULL AND created_at >= ?
        """, (data_limite,))
        
        stats_posts = cursor.fetchone()
        total_posts = stats_posts[0] or 0
        score_medio_posts = stats_posts[4] or 0.0
        
        # Calcular score médio geral
        total_items = total_noticias + total_posts
        if total_items > 0:
            score_medio_geral = (
                (score_medio_noticias * total_noticias + score_medio_posts * total_posts) / total_items
            )
        else:
            score_medio_geral = 0.0
        
        # Distribuição de sentimento
        distribuicao_sentimento = {
            'positivo': (stats_noticias[1] or 0) + (stats_posts[1] or 0),
            'negativo': (stats_noticias[2] or 0) + (stats_posts[2] or 0),
            'neutro': (stats_noticias[3] or 0) + (stats_posts[3] or 0)
        }
        
        # Top clubes com sentimento positivo
        cursor.execute("""
            SELECT 
                c.nome as clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.sentimento = 'positivo' AND n.created_at >= ?
            GROUP BY c.id, c.nome
            ORDER BY score_medio DESC
            LIMIT 5
        """, (data_limite,))
        
        top_positivos = [
            {
                'nome': clube[0],
                'total_noticias': clube[1],
                'score_medio': clube[2] or 0.0
            }
            for clube in cursor.fetchall()
        ]
        
        # Top clubes com sentimento negativo
        cursor.execute("""
            SELECT 
                c.nome as clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            WHERE n.sentimento = 'negativo' AND n.created_at >= ?
            GROUP BY c.id, c.nome
            ORDER BY score_medio ASC
            LIMIT 5
        """, (data_limite,))
        
        top_negativos = [
            {
                'nome': clube[0],
                'total_noticias': clube[1],
                'score_medio': clube[2] or 0.0
            }
            for clube in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_noticias": total_noticias,
            "total_posts": total_posts,
            "distribuicao_sentimento": distribuicao_sentimento,
            "score_medio_geral": score_medio_geral,
            "top_clubes_positivos": top_positivos,
            "top_clubes_negativos": top_negativos,
            "ultima_atualizacao": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/sentimento/clubes/ranking", response_model=List[schemas.SentimentoClubeSchema])
def get_ranking_sentimento_clubes(
    db: Session = Depends(get_db),
    limite: int = Query(10, description="Número de clubes a retornar", ge=1, le=50),
    tipo_sentimento: Optional[str] = Query(None, description="Filtrar por tipo de sentimento (positivo, negativo, neutro)")
):
    """
    Obtém ranking de clubes por sentimento.
    
    Args:
        limite: Número de clubes a retornar
        tipo_sentimento: Filtrar por tipo de sentimento
        
    Returns:
        Ranking de clubes por sentimento
    """
    try:
        # Conectar ao banco SQLite
        db_path = get_db_path()
        if not db_path:
            raise HTTPException(status_code=500, detail="Banco de dados não encontrado")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Construir query baseada no filtro
        if tipo_sentimento:
            if tipo_sentimento not in ['positivo', 'negativo', 'neutro']:
                raise HTTPException(status_code=400, detail="Tipo de sentimento inválido")
            
            where_clause = "WHERE n.sentimento = ?"
            params = [tipo_sentimento]
        else:
            where_clause = "WHERE n.sentimento IS NOT NULL"
            params = []
        
        # Query para ranking
        query = f"""
            SELECT 
                c.id as clube_id,
                c.nome as nome_clube,
                COUNT(n.id) as total_noticias,
                AVG(n.score_sentimento) as score_medio,
                AVG(n.confianca_sentimento) as confianca_media,
                MAX(n.analisado_em) as ultima_analise
            FROM noticias_clubes n
            JOIN clubes c ON n.clube_id = c.id
            {where_clause}
            GROUP BY c.id, c.nome
            ORDER BY score_medio DESC
            LIMIT ?
        """
        
        params.append(limite)
        cursor.execute(query, params)
        
        ranking = []
        for row in cursor.fetchall():
            score_medio = row[3] or 0.0
            
            if score_medio > 0.1:
                sentimento_geral = 'positivo'
            elif score_medio < -0.1:
                sentimento_geral = 'negativo'
            else:
                sentimento_geral = 'neutro'
            
            ranking.append({
                "clube_id": row[0],
                "nome_clube": row[1],
                "sentimento_medio_noticias": score_medio,
                "noticias_analisadas": row[2],
                "sentimento_medio_posts": None,
                "posts_analisados": None,
                "sentimento_geral": sentimento_geral,
                "confianca_media": row[4],
                "ultima_atualizacao": row[5]
            })
        
        conn.close()
        
        return ranking
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/sentimento/reprocessar")
def reprocessar_sentimento(
    db: Session = Depends(get_db),
    clube_id: Optional[int] = Query(None, description="ID do clube específico (opcional)")
):
    """
    Reprocessa a análise de sentimento para todos os textos ou um clube específico.
    
    Args:
        clube_id: ID do clube específico (opcional)
        
    Returns:
        Resumo do reprocessamento
    """
    try:
        # Importar função de análise
        import sys
        sys.path.append('Coleta_de_dados/analise')
        
        from sentimento import analisar_sentimento_textos
        
        # Executar análise
        success = analisar_sentimento_textos()
        
        if success:
            return {
                "message": "Análise de sentimento reprocessada com sucesso",
                "success": True,
                "clube_id": clube_id
            }
        else:
            raise HTTPException(status_code=500, detail="Falha no reprocessamento")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reprocessar sentimento: {str(e)}")
