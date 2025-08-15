#!/usr/bin/env python3
"""
Sistema avançado de modelos de Machine Learning para previsões esportivas
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime, timedelta
import warnings
from pathlib import Path
import joblib
import json

# Modelos de ML
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .data_preparation import DataPreparationPipeline

# Configurar logging
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class MLModelManager:
    """Gerenciador de modelos de Machine Learning"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.models = {}
        self.model_metadata = {}
        self.best_model = None
        self.data_pipeline = DataPreparationPipeline()
        
        # Criar diretórios necessários
        self.models_dir = Path(self.config.models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar modelos base
        self._setup_base_models()
    
    def _setup_base_models(self):
        """Configura modelos base para diferentes tipos de previsão"""
        self.base_models = {
            'result_prediction': {
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state
                ),
                'logistic_regression': LogisticRegression(
                    random_state=self.config.random_state,
                    max_iter=1000
                ),
                'xgboost': xgb.XGBClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state,
                    eval_metric='logloss'
                ),
                'lightgbm': lgb.LGBMClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state,
                    verbose=-1
                )
            },
            'goals_prediction': {
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=self.config.random_state
                ),
                'neural_network': MLPClassifier(
                    hidden_layer_sizes=(100, 50),
                    random_state=self.config.random_state,
                    max_iter=500
                )
            },
            'sentiment_analysis': {
                'naive_bayes': GaussianNB(),
                'logistic_regression': LogisticRegression(
                    random_state=self.config.random_state,
                    max_iter=1000
                ),
                'svm': SVC(
                    probability=True,
                    random_state=self.config.random_state
                )
            }
        }
    
    def prepare_training_data(self, data: Union[pd.DataFrame, str, Path],
                            target_col: str,
                            **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Prepara dados para treinamento"""
        try:
            # Usar pipeline de preparação de dados
            prepared_data = self.data_pipeline.run_full_pipeline(data, target_col, **kwargs)
            
            # Separar features e target
            X = prepared_data.drop(columns=[target_col])
            y = prepared_data[target_col]
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=1 - self.config.train_test_split,
                random_state=self.config.config.random_state,
                stratify=y if len(y.unique()) <= 10 else None
            )
            
            logger.info(f"Dados preparados: Treino {X_train.shape}, Teste {X_test.shape}")
            return prepared_data, X_train, X_test, y_train, y_test
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados de treinamento: {e}")
            raise
    
    def train_model(self, model_name: str,
                   model_type: str,
                   X_train: pd.DataFrame,
                   y_train: pd.Series,
                   hyperparameter_tuning: bool = False) -> Dict[str, Any]:
        """Treina um modelo específico"""
        try:
            if model_type not in self.base_models:
                raise ValueError(f"Tipo de modelo '{model_type}' não suportado")
            
            if model_name not in self.base_models[model_type]:
                raise ValueError(f"Modelo '{model_name}' não encontrado para tipo '{model_type}'")
            
            model = self.base_models[model_type][model_name]
            
            # Hiperparâmetros para tuning
            param_grids = {
                'random_forest': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10]
                },
                'gradient_boosting': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                'xgboost': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                },
                'lightgbm': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            }
            
            if hyperparameter_tuning and model_name in param_grids:
                logger.info(f"Aplicando GridSearch para {model_name}")
                grid_search = GridSearchCV(
                    model,
                    param_grids[model_name],
                    cv=5,
                    scoring='accuracy',
                    n_jobs=-1
                )
                grid_search.fit(X_train, y_train)
                model = grid_search.best_estimator_
                best_params = grid_search.best_params_
                logger.info(f"Melhores parâmetros: {best_params}")
            else:
                best_params = {}
            
            # Treinar modelo
            start_time = datetime.now()
            model.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Avaliar modelo
            train_score = model.score(X_train, y_train)
            
            # Salvar modelo
            model_key = f"{model_type}_{model_name}"
            self.models[model_key] = model
            
            # Metadata do modelo
            model_metadata = {
                'model_name': model_name,
                'model_type': model_type,
                'training_date': datetime.now().isoformat(),
                'training_time_seconds': training_time,
                'train_score': train_score,
                'best_params': best_params,
                'feature_names': list(X_train.columns),
                'n_features': X_train.shape[1],
                'n_samples': X_train.shape[0]
            }
            
            self.model_metadata[model_key] = model_metadata
            
            logger.info(f"Modelo {model_key} treinado com sucesso. Score: {train_score:.4f}")
            
            return {
                'model': model,
                'metadata': model_metadata,
                'model_key': model_key
            }
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo {model_name}: {e}")
            raise
    
    def train_ensemble_model(self, model_type: str,
                           X_train: pd.DataFrame,
                           y_train: pd.Series,
                           voting_strategy: str = 'soft') -> Dict[str, Any]:
        """Treina um modelo ensemble"""
        try:
            if model_type not in self.base_models:
                raise ValueError(f"Tipo de modelo '{model_type}' não suportado")
            
            # Treinar todos os modelos base
            trained_models = []
            for model_name in self.base_models[model_type].keys():
                try:
                    result = self.train_model(model_name, model_type, X_train, y_train)
                    trained_models.append((model_name, result['model']))
                except Exception as e:
                    logger.warning(f"Erro ao treinar {model_name}: {e}")
                    continue
            
            if len(trained_models) < 2:
                raise ValueError("Pelo menos 2 modelos devem ser treinados para ensemble")
            
            # Criar ensemble
            ensemble = VotingClassifier(
                estimators=trained_models,
                voting=voting_strategy
            )
            
            # Treinar ensemble
            start_time = datetime.now()
            ensemble.fit(X_train, y_train)
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Avaliar ensemble
            train_score = ensemble.score(X_train, y_train)
            
            # Salvar ensemble
            ensemble_key = f"{model_type}_ensemble"
            self.models[ensemble_key] = ensemble
            
            # Metadata do ensemble
            ensemble_metadata = {
                'model_name': 'ensemble',
                'model_type': model_type,
                'training_date': datetime.now().isoformat(),
                'training_time_seconds': training_time,
                'train_score': train_score,
                'voting_strategy': voting_strategy,
                'base_models': [name for name, _ in trained_models],
                'feature_names': list(X_train.columns),
                'n_features': X_train.shape[1],
                'n_samples': X_train.shape[0]
            }
            
            self.model_metadata[ensemble_key] = ensemble_metadata
            
            logger.info(f"Ensemble {ensemble_key} treinado com sucesso. Score: {train_score:.4f}")
            
            return {
                'model': ensemble,
                'metadata': ensemble_metadata,
                'model_key': ensemble_key
            }
            
        except Exception as e:
            logger.error(f"Erro ao treinar ensemble: {e}")
            raise
    
    def evaluate_model(self, model_key: str,
                      X_test: pd.DataFrame,
                      y_test: pd.Series) -> Dict[str, Any]:
        """Avalia um modelo treinado"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Modelo '{model_key}' não encontrado")
            
            model = self.models[model_key]
            
            # Previsões
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            # Métricas de classificação
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
                'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0),
                'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0)
            }
            
            # ROC AUC se disponível
            if y_pred_proba is not None and len(y_test.unique()) == 2:
                try:
                    metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
                except:
                    metrics['roc_auc'] = None
            
            # Matriz de confusão
            cm = confusion_matrix(y_test, y_test)
            
            # Relatório de classificação
            classification_rep = classification_report(y_test, y_pred, output_dict=True)
            
            # Atualizar metadata
            self.model_metadata[model_key].update({
                'test_metrics': metrics,
                'confusion_matrix': cm.tolist(),
                'classification_report': classification_rep,
                'evaluation_date': datetime.now().isoformat()
            })
            
            logger.info(f"Modelo {model_key} avaliado. Accuracy: {metrics['accuracy']:.4f}")
            
            return {
                'metrics': metrics,
                'confusion_matrix': cm,
                'classification_report': classification_rep,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
            
        except Exception as e:
            logger.error(f"Erro ao avaliar modelo {model_key}: {e}")
            raise
    
    def make_prediction(self, model_key: str,
                       features: Union[pd.DataFrame, np.ndarray, List],
                       return_probability: bool = True) -> Dict[str, Any]:
        """Faz previsão usando um modelo treinado"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Modelo '{model_key}' não encontrado")
            
            model = self.models[model_key]
            
            # Converter features para DataFrame se necessário
            if isinstance(features, (list, np.ndarray)):
                if isinstance(features, list):
                    features = np.array(features).reshape(1, -1)
                features = pd.DataFrame(features, columns=self.model_metadata[model_key]['feature_names'])
            
            # Verificar se features têm as colunas corretas
            expected_features = set(self.model_metadata[model_key]['feature_names'])
            actual_features = set(features.columns)
            
            if expected_features != actual_features:
                missing_features = expected_features - actual_features
                extra_features = actual_features - expected_features
                raise ValueError(f"Features não correspondem. Faltando: {missing_features}, Extras: {extra_features}")
            
            # Fazer previsão
            prediction = model.predict(features)
            probability = model.predict_proba(features) if return_probability and hasattr(model, 'predict_proba') else None
            
            # Calcular confiança
            confidence = 1.0
            if probability is not None:
                confidence = np.max(probability, axis=1)[0]
            
            result = {
                'prediction': prediction[0] if len(prediction) == 1 else prediction,
                'confidence': confidence,
                'model_key': model_key,
                'timestamp': datetime.now().isoformat()
            }
            
            if probability is not None:
                result['probabilities'] = probability[0] if len(probability) == 1 else probability
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao fazer previsão com {model_key}: {e}")
            raise
    
    def save_model(self, model_key: str, filename: str = None) -> str:
        """Salva um modelo treinado"""
        try:
            if model_key not in self.models:
                raise ValueError(f"Modelo '{model_key}' não encontrado")
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{model_key}_{timestamp}.joblib"
            
            filepath = self.models_dir / filename
            
            # Salvar modelo e metadata
            model_data = {
                'model': self.models[model_key],
                'metadata': self.model_metadata[model_key]
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Modelo {model_key} salvo em: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo {model_key}: {e}")
            raise
    
    def load_model(self, filepath: str) -> bool:
        """Carrega um modelo salvo"""
        try:
            model_data = joblib.load(filepath)
            
            model = model_data['model']
            metadata = model_data['metadata']
            
            model_key = metadata['model_key']
            
            self.models[model_key] = model
            self.model_metadata[model_key] = metadata
            
            logger.info(f"Modelo {model_key} carregado de: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return False
    
    def get_model_info(self, model_key: str = None) -> Dict[str, Any]:
        """Retorna informações sobre modelos"""
        if model_key:
            if model_key in self.model_metadata:
                return self.model_metadata[model_key]
            else:
                return {'error': f"Modelo '{model_key}' não encontrado"}
        
        return {
            'total_models': len(self.models),
            'model_types': list(set([meta['model_type'] for meta in self.model_metadata.values()])),
            'models': {
                key: {
                    'name': meta['model_name'],
                    'type': meta['model_type'],
                    'training_date': meta['training_date'],
                    'train_score': meta.get('train_score', 'N/A'),
                    'test_accuracy': meta.get('test_metrics', {}).get('accuracy', 'N/A')
                }
                for key, meta in self.model_metadata.items()
            }
        }
    
    def cleanup_models(self, keep_best: bool = True) -> int:
        """Remove modelos antigos, mantendo apenas os melhores"""
        try:
            if not keep_best:
                removed_count = len(self.models)
                self.models.clear()
                self.model_metadata.clear()
                logger.info(f"Todos os {removed_count} modelos foram removidos")
                return removed_count
            
            # Manter apenas o melhor modelo de cada tipo
            best_models = {}
            for model_key, metadata in self.model_metadata.items():
                model_type = metadata['model_type']
                test_accuracy = metadata.get('test_metrics', {}).get('accuracy', 0)
                
                if model_type not in best_models or test_accuracy > best_models[model_type]['accuracy']:
                    best_models[model_type] = {
                        'model_key': model_key,
                        'accuracy': test_accuracy
                    }
            
            # Remover modelos não-ótimos
            models_to_remove = []
            for model_key in self.models.keys():
                model_type = self.model_metadata[model_key]['model_type']
                if model_key != best_models[model_type]['model_key']:
                    models_to_remove.append(model_key)
            
            for model_key in models_to_remove:
                del self.models[model_key]
                del self.model_metadata[model_key]
            
            logger.info(f"{len(models_to_remove)} modelos foram removidos, mantendo os melhores")
            return len(models_to_remove)
            
        except Exception as e:
            logger.error(f"Erro ao limpar modelos: {e}")
            return 0

# Instância global
ml_model_manager = MLModelManager()

# Funções de conveniência
def train_model(model_name: str, model_type: str, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> Dict:
    """Treina um modelo específico"""
    return ml_model_manager.train_model(model_name, model_type, X_train, y_train, **kwargs)

def train_ensemble(model_type: str, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> Dict:
    """Treina um modelo ensemble"""
    return ml_model_manager.train_ensemble_model(model_type, X_train, y_train, **kwargs)

def make_prediction(model_key: str, features: Union[pd.DataFrame, np.ndarray, List], **kwargs) -> Dict:
    """Faz previsão usando um modelo treinado"""
    return ml_model_manager.make_prediction(model_key, features, **kwargs)

def save_model(model_key: str, filename: str = None) -> str:
    """Salva um modelo treinado"""
    return ml_model_manager.save_model(model_key, filename)

def load_model(filepath: str) -> bool:
    """Carrega um modelo salvo"""
    return ml_model_manager.load_model(filepath)

def get_model_info(model_key: str = None) -> Dict:
    """Retorna informações sobre modelos"""
    return ml_model_manager.get_model_info(model_key)
