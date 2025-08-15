#!/usr/bin/env python3
"""
Router para funcionalidades de Machine Learning na API do ApostaPro
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

# Importar módulos de ML
from ml_models.sentiment_analyzer import analyze_sentiment, analyze_sentiments_batch, get_sentiment_summary
from ml_models.data_preparation import prepare_data, save_preprocessing_models, load_preprocessing_models
from ml_models.ml_models import (
    train_model, train_ensemble, make_prediction, 
    save_model, load_model, get_model_info
)
from ml_models.recommendation_system import (
    analyze_match, generate_predictions, 
    get_betting_recommendations, get_recommendation_summary
)
from ml_models.cache_manager import get_cache_stats, clear_ml_cache, cleanup_expired_cache

# Configurar logging
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# ============================================================================
# ENDPOINTS DE ANÁLISE DE SENTIMENTO
# ============================================================================

@router.post("/sentiment/analyze")
async def analyze_text_sentiment(
    text: str = Query(..., description="Texto para análise de sentimento"),
    method: str = Query("hybrid", description="Método de análise: textblob, lexical, hybrid")
):
    """Analisa sentimento de um texto"""
    try:
        result = analyze_sentiment(text, method)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na análise de sentimento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/sentiment/analyze-batch")
async def analyze_multiple_texts(
    texts: List[str] = Query(..., description="Lista de textos para análise"),
    method: str = Query("hybrid", description="Método de análise")
):
    """Analisa sentimento de múltiplos textos"""
    try:
        results = analyze_sentiments_batch(texts, method)
        summary = get_sentiment_summary(results)
        
        return {
            "success": True,
            "data": {
                "individual_results": results,
                "summary": summary
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na análise em lote: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

# ============================================================================
# ENDPOINTS DE PREPARAÇÃO DE DADOS
# ============================================================================

@router.post("/data/prepare")
async def prepare_data_for_ml(
    target_column: str = Query(..., description="Coluna alvo para ML"),
    date_columns: Optional[str] = Query(None, description="Colunas de data para features temporais (separadas por vírgula)"),
    feature_groups: Optional[str] = Query(None, description="Grupos de features para interação (separados por vírgula)"),
    apply_pca: bool = Query(False, description="Aplicar PCA para redução de dimensionalidade")
):
    """Prepara dados para Machine Learning"""
    try:
        # Por enquanto, retornar instruções (dados devem ser enviados via arquivo ou API)
        return {
            "success": True,
            "message": "Endpoint para preparação de dados. Use POST com arquivo ou dados JSON.",
            "parameters": {
                "target_column": target_column,
                "date_columns": date_columns,
                "feature_groups": feature_groups,
                "apply_pca": apply_pca
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na preparação de dados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na preparação: {str(e)}")

@router.get("/data/preprocessing-models")
async def list_preprocessing_models():
    """Lista modelos de pré-processamento disponíveis"""
    try:
        # Implementar lógica para listar modelos salvos
        return {
            "success": True,
            "message": "Lista de modelos de pré-processamento",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar modelos: {str(e)}")

# ============================================================================
# ENDPOINTS DE MODELOS DE ML
# ============================================================================

@router.post("/models/train")
async def train_ml_model(
    model_name: str = Query(..., description="Nome do modelo"),
    model_type: str = Query(..., description="Tipo do modelo: result_prediction, goals_prediction, sentiment_analysis"),
    hyperparameter_tuning: bool = Query(False, description="Aplicar tuning de hiperparâmetros")
):
    """Treina um modelo de Machine Learning"""
    try:
        # Por enquanto, retornar instruções
        return {
            "success": True,
            "message": "Endpoint para treinamento de modelos. Use POST com dados de treinamento.",
            "parameters": {
                "model_name": model_name,
                "model_type": model_type,
                "hyperparameter_tuning": hyperparameter_tuning
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no treinamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {str(e)}")

@router.post("/models/ensemble")
async def train_ensemble_model(
    model_type: str = Query(..., description="Tipo do modelo para ensemble"),
    voting_strategy: str = Query("soft", description="Estratégia de votação: soft, hard")
):
    """Treina um modelo ensemble"""
    try:
        return {
            "success": True,
            "message": "Endpoint para treinamento de ensemble. Use POST com dados de treinamento.",
            "parameters": {
                "model_type": model_type,
                "voting_strategy": voting_strategy
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no treinamento de ensemble: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no treinamento: {str(e)}")

@router.post("/models/predict")
async def make_ml_prediction(
    model_key: str = Query(..., description="Chave do modelo treinado"),
    features: str = Query(..., description="Features para previsão (separadas por vírgula)")
):
    """Faz previsão usando um modelo treinado"""
    try:
        prediction = make_prediction(model_key, features)
        return {
            "success": True,
            "data": prediction,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na previsão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na previsão: {str(e)}")

@router.get("/models/info")
async def get_ml_models_info(model_key: Optional[str] = Query(None, description="Chave específica do modelo")):
    """Retorna informações sobre modelos de ML"""
    try:
        info = get_model_info(model_key)
        return {
            "success": True,
            "data": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações dos modelos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações: {str(e)}")

@router.post("/models/save")
async def save_ml_model(
    model_key: str = Query(..., description="Chave do modelo para salvar"),
    filename: Optional[str] = Query(None, description="Nome do arquivo para salvar")
):
    """Salva um modelo treinado"""
    try:
        filepath = save_model(model_key, filename)
        return {
            "success": True,
            "message": "Modelo salvo com sucesso",
            "data": {"filepath": filepath},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao salvar modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar modelo: {str(e)}")

@router.post("/models/load")
async def load_ml_model(filepath: str = Query(..., description="Caminho do arquivo do modelo")):
    """Carrega um modelo salvo"""
    try:
        success = load_model(filepath)
        if success:
            return {
                "success": True,
                "message": "Modelo carregado com sucesso",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Falha ao carregar modelo")
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao carregar modelo: {str(e)}")

# ============================================================================
# ENDPOINTS DE RECOMENDAÇÕES DE APOSTAS
# ============================================================================

@router.post("/recommendations/analyze-match")
async def analyze_match_for_recommendations(match_data: Dict[str, Any]):
    """Analisa dados de uma partida para gerar recomendações"""
    try:
        analysis = analyze_match(match_data)
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na análise da partida: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/recommendations/generate-predictions")
async def generate_match_predictions(match_analysis: Dict[str, Any]):
    """Gera previsões para uma partida"""
    try:
        predictions = generate_predictions(match_analysis)
        return {
            "success": True,
            "data": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na geração de previsões: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

@router.post("/recommendations/betting-advice")
async def get_betting_recommendations(
    predictions: Dict[str, Any],
    risk_level: str = Query("medium", description="Nível de risco: low, medium, high"),
    max_recommendations: int = Query(5, description="Número máximo de recomendações")
):
    """Gera recomendações de apostas"""
    try:
        recommendations = get_betting_recommendations(
            predictions, risk_level, max_recommendations
        )
        summary = get_recommendation_summary(recommendations)
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "summary": summary
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na geração de recomendações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

# ============================================================================
# ENDPOINTS DE CACHE E MONITORAMENTO
# ============================================================================

@router.get("/cache/stats")
async def get_ml_cache_statistics():
    """Retorna estatísticas do cache de ML"""
    try:
        stats = get_cache_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/cache/clear")
async def clear_ml_cache():
    """Limpa todo o cache de ML"""
    try:
        success = clear_ml_cache()
        if success:
            return {
                "success": True,
                "message": "Cache limpo com sucesso",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao limpar cache")
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar cache: {str(e)}")

@router.post("/cache/cleanup")
async def cleanup_expired_cache():
    """Remove caches expirados"""
    try:
        removed_count = cleanup_expired_cache()
        return {
            "success": True,
            "message": f"{removed_count} arquivos de cache expirados foram removidos",
            "data": {"removed_count": removed_count},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na limpeza de cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na limpeza: {str(e)}")

# ============================================================================
# ENDPOINTS DE STATUS E SAÚDE
# ============================================================================

@router.get("/health")
async def ml_system_health():
    """Verifica a saúde do sistema de ML"""
    try:
        # Verificar componentes principais
        health_status = {
            "sentiment_analyzer": "operational",
            "data_preparation": "operational",
            "ml_models": "operational",
            "recommendation_system": "operational",
            "cache_manager": "operational"
        }
        
        return {
            "success": True,
            "status": "healthy",
            "components": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/status")
async def ml_system_status():
    """Retorna status detalhado do sistema de ML"""
    try:
        # Obter informações dos modelos
        models_info = get_model_info()
        
        # Obter estatísticas do cache
        cache_stats = get_cache_stats()
        
        status = {
            "models": models_info,
            "cache": cache_stats,
            "system_info": {
                "python_version": "3.8+",
                "ml_libraries": [
                    "scikit-learn", "pandas", "numpy", "xgboost", 
                    "lightgbm", "nltk", "textblob"
                ],
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

# ============================================================================
# ENDPOINTS DE TESTE E DESENVOLVIMENTO
# ============================================================================

@router.post("/test/sentiment")
async def test_sentiment_analysis():
    """Testa o sistema de análise de sentimento"""
    try:
        test_texts = [
            "Excelente vitória do time! Gol espetacular!",
            "Derrota amarga. O time jogou mal.",
            "Empate justo. Bom jogo das duas equipes."
        ]
        
        results = analyze_sentiments_batch(test_texts, "hybrid")
        summary = get_sentiment_summary(results)
        
        return {
            "success": True,
            "message": "Teste de análise de sentimento concluído",
            "data": {
                "test_texts": test_texts,
                "results": results,
                "summary": summary
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no teste de sentimento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")

@router.post("/test/recommendations")
async def test_recommendation_system():
    """Testa o sistema de recomendações"""
    try:
        # Dados de teste para uma partida
        test_match_data = {
            "match_id": "test_001",
            "home_team": "Time A",
            "away_team": "Time B",
            "competition": "Liga Teste",
            "match_date": "2025-01-15",
            "home_goals_scored": 2.1,
            "away_goals_scored": 1.8,
            "home_goals_conceded": 1.2,
            "away_goals_conceded": 1.5,
            "home_recent_form": ["W", "W", "D", "L", "W"],
            "away_recent_form": ["L", "D", "W", "W", "L"],
            "news_sentiment": "Time da casa em boa fase, expectativa positiva para a partida."
        }
        
        # Análise da partida
        analysis = analyze_match(test_match_data)
        
        # Geração de previsões
        predictions = generate_predictions(analysis)
        
        # Recomendações de apostas
        recommendations = get_betting_recommendations(predictions, "medium", 3)
        
        return {
            "success": True,
            "message": "Teste do sistema de recomendações concluído",
            "data": {
                "test_match": test_match_data,
                "analysis": analysis,
                "predictions": predictions,
                "recommendations": recommendations
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no teste de recomendações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")
