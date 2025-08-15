#!/usr/bin/env python3
"""
Router para endpoints de recomendações de apostas geradas pelo sistema ML
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Adicionar o diretório raiz ao path para importar módulos ML
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.schemas import (
    RecomendacaoApostaSchema, 
    RecomendacaoResumoSchema, 
    GerarRecomendacoesRequest
)
from Coleta_de_dados.ml.gerar_recomendacoes import GeradorRecomendacoes

router = APIRouter(prefix="/recomendacoes", tags=["Recomendações de Apostas"])

# Configuração do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Banco_de_dados", "aposta.db")

def get_db_connection():
    """Retorna conexão com o banco SQLite"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Banco de dados não encontrado")
    return sqlite3.connect(DB_PATH)

@router.get("/", response_model=List[RecomendacaoApostaSchema])
async def listar_recomendacoes(
    limite: int = 50,
    offset: int = 0,
    mercado: str = None,
    data_inicio: str = None,
    data_fim: str = None
):
    """
    Lista todas as recomendações de apostas geradas pelo sistema ML
    
    Args:
        limite: Número máximo de recomendações a retornar
        offset: Número de recomendações a pular (para paginação)
        mercado: Filtrar por tipo de mercado (ex: 'Resultado Final')
        data_inicio: Data de início para filtrar (formato: YYYY-MM-DD)
        data_fim: Data de fim para filtrar (formato: YYYY-MM-DD)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query base
        query = """
        SELECT 
            r.id,
            r.partida_id,
            r.mercado_aposta,
            r.previsao,
            r.probabilidade,
            r.odd_justa,
            r.data_geracao,
            p.time_casa,
            p.time_visitante,
            p.data
        FROM recomendacoes_apostas r
        JOIN partidas p ON r.partida_id = p.id
        WHERE 1=1
        """
        
        params = []
        
        # Aplicar filtros
        if mercado:
            query += " AND r.mercado_aposta = ?"
            params.append(mercado)
        
        if data_inicio:
            query += " AND DATE(r.data_geracao) >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND DATE(r.data_geracao) <= ?"
            params.append(data_fim)
        
        # Ordenar e limitar
        query += " ORDER BY r.data_geracao DESC LIMIT ? OFFSET ?"
        params.extend([limite, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        recomendacoes = []
        for row in rows:
            recomendacoes.append(RecomendacaoApostaSchema(
                id=row[0],
                partida_id=row[1],
                mercado_aposta=row[2],
                previsao=row[3],
                probabilidade=row[4],
                odd_justa=row[5],
                data_geracao=datetime.fromisoformat(row[6]),
                time_casa=row[7],
                time_visitante=row[8],
                data_partida=row[9]
            ))
        
        conn.close()
        return recomendacoes
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar recomendações: {str(e)}")

@router.get("/resumo", response_model=RecomendacaoResumoSchema)
async def obter_resumo_recomendacoes():
    """
    Retorna um resumo estatístico das recomendações geradas
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de recomendações
        cursor.execute("SELECT COUNT(*) FROM recomendacoes_apostas")
        total = cursor.fetchone()[0]
        
        # Distribuição por mercado
        cursor.execute("""
            SELECT mercado_aposta, COUNT(*) 
            FROM recomendacoes_apostas 
            GROUP BY mercado_aposta
        """)
        mercados = dict(cursor.fetchall())
        
        # Probabilidade média
        cursor.execute("SELECT AVG(probabilidade) FROM recomendacoes_apostas")
        prob_media = cursor.fetchone()[0] or 0.0
        
        # Última atualização
        cursor.execute("SELECT MAX(data_geracao) FROM recomendacoes_apostas")
        ultima_atualizacao = cursor.fetchone()[0]
        
        conn.close()
        
        return RecomendacaoResumoSchema(
            total_recomendacoes=total,
            recomendacoes_por_mercado=mercados,
            probabilidade_media=round(prob_media, 4),
            ultima_atualizacao=datetime.fromisoformat(ultima_atualizacao) if ultima_atualizacao else datetime.now()
        )
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar resumo: {str(e)}")

@router.get("/partida/{partida_id}", response_model=List[RecomendacaoApostaSchema])
async def obter_recomendacoes_partida(partida_id: int):
    """
    Retorna todas as recomendações para uma partida específica
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            r.id,
            r.partida_id,
            r.mercado_aposta,
            r.previsao,
            r.probabilidade,
            r.odd_justa,
            r.data_geracao,
            p.time_casa,
            p.time_visitante,
            p.data
        FROM recomendacoes_apostas r
        JOIN partidas p ON r.partida_id = p.id
        WHERE r.partida_id = ?
        ORDER BY r.probabilidade DESC
        """
        
        cursor.execute(query, (partida_id,))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"Nenhuma recomendação encontrada para a partida {partida_id}")
        
        recomendacoes = []
        for row in rows:
            recomendacoes.append(RecomendacaoApostaSchema(
                id=row[0],
                partida_id=row[1],
                mercado_aposta=row[2],
                previsao=row[3],
                probabilidade=row[4],
                odd_justa=row[5],
                data_geracao=datetime.fromisoformat(row[6]),
                time_casa=row[7],
                time_visitante=row[8],
                data_partida=row[9]
            ))
        
        conn.close()
        return recomendacoes
        
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar recomendações da partida: {str(e)}")

@router.post("/gerar", response_model=Dict[str, Any])
async def gerar_recomendacoes(request: GerarRecomendacoesRequest):
    """
    Gera novas recomendações de apostas para partidas futuras usando o sistema ML
    
    Args:
        request: Parâmetros para geração de recomendações
    """
    try:
        # Inicializar gerador de recomendações
        gerador = GeradorRecomendacoes()
        
        # Carregar modelo treinado
        if not gerador.carregar_ultimo_modelo():
            raise HTTPException(status_code=500, detail="Não foi possível carregar modelo ML treinado")
        
        # Gerar recomendações
        resultado = gerador.gerar_recomendacoes_partidas_futuras(
            dias_futuros=request.dias_futuros
        )
        
        if not resultado:
            return {
                "mensagem": "Nenhuma recomendação foi gerada",
                "motivo": "Não há partidas futuras disponíveis ou todas já possuem recomendações",
                "dias_processados": request.dias_futuros,
                "recomendacoes_geradas": 0
            }
        
        return {
            "mensagem": "Recomendações geradas com sucesso",
            "dias_processados": request.dias_futuros,
            "recomendacoes_geradas": len(resultado),
            "partidas_processadas": len(set(r['partida_id'] for r in resultado)),
            "mercados_gerados": list(set(r['mercado_aposta'] for r in resultado)),
            "timestamp_geracao": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")

@router.get("/mercados", response_model=List[str])
async def listar_mercados_disponiveis():
    """
    Retorna lista de todos os tipos de mercado disponíveis nas recomendações
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT mercado_aposta 
            FROM recomendacoes_apostas 
            ORDER BY mercado_aposta
        """)
        
        mercados = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return mercados
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar mercados: {str(e)}")

@router.delete("/{recomendacao_id}")
async def deletar_recomendacao(recomendacao_id: int):
    """
    Remove uma recomendação específica
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se a recomendação existe
        cursor.execute("SELECT id FROM recomendacoes_apostas WHERE id = ?", (recomendacao_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Recomendação {recomendacao_id} não encontrada")
        
        # Deletar recomendação
        cursor.execute("DELETE FROM recomendacoes_apostas WHERE id = ?", (recomendacao_id,))
        conn.commit()
        conn.close()
        
        return {"mensagem": f"Recomendação {recomendacao_id} removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar recomendação: {str(e)}")
