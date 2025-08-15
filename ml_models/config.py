#!/usr/bin/env python3
"""
Configuração centralizada para o sistema de Machine Learning do ApostaPro
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class MLConfig:
    """Configurações para o sistema de ML"""
    
    # Diretórios
    models_dir: str = "ml_models/saved_models"
    data_dir: str = "ml_models/data"
    cache_dir: str = "ml_models/cache"
    results_dir: str = "ml_models/results"
    monitoring_dir: str = "ml_models/monitoring"
    
    # Configurações de modelo
    model_version: str = "v1.0"
    confidence_threshold: float = 0.7
    max_predictions: int = 10
    
    # Configurações de treinamento
    train_test_split: float = 0.8
    validation_split: float = 0.2
    random_state: int = 42
    
    # Configurações de features
    feature_columns: List[str] = None
    target_columns: List[str] = None
    
    # Configurações de análise de sentimento
    sentiment_model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_batch_size: int = 32
    sentiment_max_length: int = 512
    
    # Configurações de cache
    cache_ttl_hours: int = 24
    enable_caching: bool = True
    
    def __post_init__(self):
        """Criar diretórios necessários"""
        for dir_path in [self.models_dir, self.data_dir, self.cache_dir, self.results_dir, self.monitoring_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Configurar features padrão se não especificadas
        if self.feature_columns is None:
            self.feature_columns = [
                'home_goals_scored', 'away_goals_scored',
                'home_goals_conceded', 'away_goals_conceded',
                'home_form', 'away_form',
                'home_attacking_strength', 'away_attacking_strength',
                'home_defensive_strength', 'away_defensive_strength',
                'home_xg', 'away_xg',
                'home_xa', 'away_xa',
                'home_possession', 'away_possession',
                'home_shots', 'away_shots',
                'home_shots_on_target', 'away_shots_on_target'
            ]
        
        if self.target_columns is None:
            self.target_columns = ['result', 'total_goals', 'both_teams_score']

# Configuração global
ml_config = MLConfig()

# Configurações específicas por ambiente
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    ml_config.confidence_threshold = 0.8
    ml_config.enable_caching = True
    ml_config.cache_ttl_hours = 48
elif ENVIRONMENT == 'testing':
    ml_config.confidence_threshold = 0.6
    ml_config.enable_caching = False

def get_ml_config() -> MLConfig:
    """Retorna a configuração de ML atual"""
    return ml_config

def update_ml_config(**kwargs) -> None:
    """Atualiza configurações específicas"""
    for key, value in kwargs.items():
        if hasattr(ml_config, key):
            setattr(ml_config, key, value)
        else:
            raise ValueError(f"Configuração '{key}' não existe")
