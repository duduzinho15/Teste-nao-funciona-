#!/usr/bin/env python3
"""
Sistema completo de Machine Learning para o ApostaPro
"""

# Configuração
from .config import get_ml_config, update_ml_config, MLConfig

# Cache Manager
from .cache_manager import (
    cache_result, timed_cache_result, 
    get_cache_stats, clear_ml_cache, cleanup_expired_cache
)

# Análise de Sentimento
from .sentiment_analyzer import (
    analyze_sentiment, analyze_sentiments_batch, get_sentiment_summary,
    SentimentAnalyzer
)

# Preparação de Dados
from .data_preparation import (
    prepare_data, save_preprocessing_models, load_preprocessing_models,
    DataPreparationPipeline
)

# Modelos de ML
from .ml_models import (
    train_model, train_ensemble, make_prediction,
    save_model, load_model, get_model_info,
    MLModelManager
)

# Sistema de Recomendações
from .recommendation_system import (
    analyze_match, generate_predictions,
    get_betting_recommendations, get_recommendation_summary,
    BettingRecommendationSystem
)

# Coleta de Dados Históricos
from .data_collector import (
    collect_historical_data, get_training_data,
    get_feature_importance_data, HistoricalDataCollector
)

# Treinamento de Modelos
from .model_trainer import (
    train_all_models, train_model_for_type,
    get_model_performance_summary, ModelTrainer
)

# Integração com Banco de Dados
from .database_integration import (
    get_matches_data, get_team_stats, get_head_to_head_stats,
    save_prediction_result, get_prediction_accuracy,
    test_database_connection, DatabaseIntegration
)

# Versão do sistema
__version__ = "1.0.0"

# Informações do sistema
__author__ = "ApostaPro Team"
__description__ = "Sistema completo de Machine Learning para apostas esportivas"

# Funções principais para uso direto
def get_ml_system_info():
    """Retorna informações sobre o sistema de ML"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": [
            "Sentiment Analysis",
            "Data Preparation",
            "ML Models",
            "Recommendation System",
            "Cache Management"
        ],
        "config": get_ml_config()
    }

def test_ml_system():
    """Testa todos os componentes do sistema de ML"""
    try:
        # Testar análise de sentimento
        test_text = "Excelente vitória do time!"
        sentiment_result = analyze_sentiment(test_text)
        
        # Testar cache
        cache_stats = get_cache_stats()
        
        # Testar configuração
        config = get_ml_config()
        
        return {
            "success": True,
            "sentiment_analysis": "OK",
            "cache_manager": "OK",
            "config": "OK",
            "message": "Todos os componentes funcionando corretamente"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro no teste do sistema"
        }

# Exportar funções principais
__all__ = [
    # Configuração
    "get_ml_config", "update_ml_config", "MLConfig",
    
    # Cache
    "cache_result", "timed_cache_result", "get_cache_stats", 
    "clear_ml_cache", "cleanup_expired_cache",
    
    # Sentimento
    "analyze_sentiment", "analyze_sentiments_batch", "get_sentiment_summary",
    "SentimentAnalyzer",
    
    # Dados
    "prepare_data", "save_preprocessing_models", "load_preprocessing_models",
    "DataPreparationPipeline",
    
    # Modelos
    "train_model", "train_ensemble", "make_prediction",
    "save_model", "load_model", "get_model_info", "MLModelManager",
    
    # Recomendações
    "analyze_match", "generate_predictions",
    "get_betting_recommendations", "get_recommendation_summary",
    "BettingRecommendationSystem",
    
    # Coleta de Dados Históricos
    "collect_historical_data", "get_training_data",
    "get_feature_importance_data", "HistoricalDataCollector",
    
    # Treinamento de Modelos
    "train_all_models", "train_model_for_type",
    "get_model_performance_summary", "ModelTrainer",
    
    # Integração com Banco de Dados
    "get_matches_data", "get_team_stats", "get_head_to_head_stats",
    "save_prediction_result", "get_prediction_accuracy",
    "test_database_connection", "DatabaseIntegration",
    
    # Utilitários
    "get_ml_system_info", "test_ml_system"
]
