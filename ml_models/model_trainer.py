#!/usr/bin/env python3
"""
Sistema especializado para treinamento de modelos ML para apostas esportivas
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import joblib
from pathlib import Path
import json
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .data_collector import get_training_data, get_feature_importance_data
from .data_preparation import DataPreparationPipeline

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Treinador especializado de modelos ML para apostas esportivas"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.models_dir = Path(self.config.models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_pipeline = DataPreparationPipeline()
        self.trained_models = {}
        self.model_metrics = {}
        
        # Configurações de modelos por tipo de aposta
        self.model_configs = {
            'result_prediction': {
                'target_column': 'result',
                'problem_type': 'classification',
                'classes': ['home_win', 'draw', 'away_win'],
                'algorithms': ['random_forest', 'xgboost', 'lightgbm', 'logistic_regression'],
                'feature_importance': True
            },
            'total_goals_prediction': {
                'target_column': 'total_goals',
                'problem_type': 'regression',
                'algorithms': ['random_forest', 'xgboost', 'lightgbm'],
                'feature_importance': True
            },
            'both_teams_score_prediction': {
                'target_column': 'both_teams_score',
                'problem_type': 'classification',
                'classes': [0, 1],
                'algorithms': ['random_forest', 'xgboost', 'logistic_regression'],
                'feature_importance': True
            }
        }
    
    def train_all_models(self, force_retrain: bool = False) -> Dict[str, Dict]:
        """
        Treina todos os modelos para todos os tipos de aposta
        
        Args:
            force_retrain: Força retreinamento mesmo se modelos existirem
            
        Returns:
            Dicionário com resultados do treinamento
        """
        results = {}
        
        for model_type, config in self.model_configs.items():
            logger.info(f"Treinando modelo para: {model_type}")
            
            try:
                result = self.train_model_for_type(
                    model_type=model_type,
                    force_retrain=force_retrain
                )
                results[model_type] = result
                
            except Exception as e:
                logger.error(f"Erro ao treinar modelo {model_type}: {e}")
                results[model_type] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Salvar métricas consolidadas
        self._save_consolidated_metrics(results)
        
        return results
    
    def train_model_for_type(self, 
                            model_type: str,
                            force_retrain: bool = False,
                            use_ensemble: bool = True) -> Dict[str, Any]:
        """
        Treina modelo para um tipo específico de aposta
        
        Args:
            model_type: Tipo de modelo (result_prediction, total_goals_prediction, etc.)
            force_retrain: Força retreinamento
            use_ensemble: Usa ensemble de modelos
            
        Returns:
            Resultado do treinamento
        """
        if model_type not in self.model_configs:
            raise ValueError(f"Tipo de modelo inválido: {model_type}")
        
        config = self.model_configs[model_type]
        target_column = config['target_column']
        
        # Verificar se modelo já existe e não forçamos retreinamento
        model_path = self.models_dir / f"{model_type}_model.joblib"
        if not force_retrain and model_path.exists():
            logger.info(f"Modelo {model_type} já existe. Carregando...")
            return self._load_existing_model(model_type)
        
        # Coletar e preparar dados
        logger.info(f"Preparando dados para {model_type}...")
        X, y = get_training_data(target_column=target_column)
        
        if X is None or y is None:
            raise ValueError(f"Não foi possível obter dados para {model_type}")
        
        # Preparar dados usando pipeline
        X_processed = self.data_pipeline.run_full_pipeline(
            data=X,
            target_col=target_column,
            apply_pca=False  # Manter todas as features para análise
        )
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, 
            test_size=0.2, 
            random_state=self.config.random_state,
            stratify=y if config['problem_type'] == 'classification' else None
        )
        
        # Treinar modelos
        if use_ensemble:
            model, metrics = self._train_ensemble_model(
                model_type, config, X_train, X_test, y_train, y_test
            )
        else:
            model, metrics = self._train_single_model(
                model_type, config, X_train, X_test, y_train, y_test
            )
        
        # Salvar modelo
        self._save_model(model_type, model, metrics)
        
        # Análise de importância de features
        feature_importance = None
        if config.get('feature_importance', False):
            feature_importance = self._analyze_feature_importance(
                model, X_processed.columns, model_type
            )
        
        result = {
            'status': 'success',
            'model_type': model_type,
            'target_column': target_column,
            'problem_type': config['problem_type'],
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features_count': X_processed.shape[1],
            'metrics': metrics,
            'feature_importance': feature_importance,
            'timestamp': datetime.now().isoformat(),
            'model_path': str(model_path)
        }
        
        self.trained_models[model_type] = model
        self.model_metrics[model_type] = metrics
        
        logger.info(f"Modelo {model_type} treinado com sucesso!")
        return result
    
    def _train_ensemble_model(self, 
                             model_type: str,
                             config: Dict,
                             X_train: pd.DataFrame,
                             X_test: pd.DataFrame,
                             y_train: pd.Series,
                             y_test: pd.Series) -> Tuple[Any, Dict]:
        """Treina modelo ensemble"""
        from sklearn.ensemble import VotingClassifier, VotingRegressor
        
        # Criar modelos base
        base_models = self._create_base_models(config)
        
        if config['problem_type'] == 'classification':
            # Ensemble para classificação
            ensemble = VotingClassifier(
                estimators=[(name, model) for name, model in base_models.items()],
                voting='soft'  # Usar probabilidades
            )
        else:
            # Ensemble para regressão
            ensemble = VotingRegressor(
                estimators=[(name, model) for name, model in base_models.items()]
            )
        
        # Treinar ensemble
        ensemble.fit(X_train, y_train)
        
        # Avaliar
        metrics = self._evaluate_model(
            ensemble, X_test, y_test, config['problem_type']
        )
        
        return ensemble, metrics
    
    def _train_single_model(self, 
                           model_type: str,
                           config: Dict,
                           X_train: pd.DataFrame,
                           X_test: pd.DataFrame,
                           y_train: pd.Series,
                           y_test: pd.Series) -> Tuple[Any, Dict]:
        """Treina modelo único (melhor algoritmo)"""
        # Usar XGBoost como padrão (geralmente melhor performance)
        if 'xgboost' in config['algorithms']:
            model = self._create_xgboost_model(config)
        elif 'lightgbm' in config['algorithms']:
            model = self._create_lightgbm_model(config)
        elif 'random_forest' in config['algorithms']:
            model = self._create_random_forest_model(config)
        else:
            model = self._create_logistic_regression_model(config)
        
        # Treinar modelo
        model.fit(X_train, y_train)
        
        # Avaliar
        metrics = self._evaluate_model(
            model, X_test, y_test, config['problem_type']
        )
        
        return model, metrics
    
    def _create_base_models(self, config: Dict) -> Dict[str, Any]:
        """Cria modelos base para ensemble"""
        models = {}
        
        if 'random_forest' in config['algorithms']:
            models['rf'] = self._create_random_forest_model(config)
        
        if 'xgboost' in config['algorithms']:
            models['xgb'] = self._create_xgboost_model(config)
        
        if 'lightgbm' in config['algorithms']:
            models['lgb'] = self._create_lightgbm_model(config)
        
        if 'logistic_regression' in config['algorithms'] and config['problem_type'] == 'classification':
            models['lr'] = self._create_logistic_regression_model(config)
        
        return models
    
    def _create_random_forest_model(self, config: Dict) -> RandomForestClassifier:
        """Cria modelo Random Forest"""
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=self.config.random_state,
            n_jobs=-1
        )
    
    def _create_xgboost_model(self, config: Dict) -> Union[xgb.XGBClassifier, xgb.XGBRegressor]:
        """Cria modelo XGBoost"""
        if config['problem_type'] == 'classification':
            return xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.config.random_state,
                n_jobs=-1
            )
        else:
            return xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.config.random_state,
                n_jobs=-1
            )
    
    def _create_lightgbm_model(self, config: Dict) -> Union[lgb.LGBMClassifier, lgb.LGBMRegressor]:
        """Cria modelo LightGBM"""
        if config['problem_type'] == 'classification':
            return lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.config.random_state,
                n_jobs=-1
            )
        else:
            return lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.config.random_state,
                n_jobs=-1
            )
    
    def _create_logistic_regression_model(self, config: Dict) -> LogisticRegression:
        """Cria modelo de Regressão Logística"""
        return LogisticRegression(
            random_state=self.config.random_state,
            max_iter=1000,
            C=1.0
        )
    
    def _evaluate_model(self, 
                       model: Any,
                       X_test: pd.DataFrame,
                       y_test: pd.Series,
                       problem_type: str) -> Dict[str, float]:
        """Avalia modelo treinado"""
        try:
            if problem_type == 'classification':
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
                
                metrics = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision_macro': precision_score(y_test, y_pred, average='macro'),
                    'recall_macro': recall_score(y_test, y_pred, average='macro'),
                    'f1_macro': f1_score(y_test, y_pred, average='macro')
                }
                
                # ROC AUC se houver probabilidades
                if y_pred_proba is not None and len(np.unique(y_test)) == 2:
                    metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
                
            else:  # Regressão
                y_pred = model.predict(X_test)
                
                metrics = {
                    'mse': mean_squared_error(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mae': mean_absolute_error(y_test, y_pred),
                    'r2': r2_score(y_test, y_pred)
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro na avaliação do modelo: {e}")
            return {}
    
    def _analyze_feature_importance(self, 
                                   model: Any,
                                   feature_names: List[str],
                                   model_type: str) -> Dict[str, float]:
        """Analisa importância das features"""
        try:
            if hasattr(model, 'feature_importances_'):
                # Tree-based models
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                # Linear models
                importance = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
            else:
                return {}
            
            # Criar dicionário feature -> importância
            feature_importance = dict(zip(feature_names, importance))
            
            # Ordenar por importância
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return dict(sorted_features[:20])  # Top 20 features
            
        except Exception as e:
            logger.error(f"Erro na análise de importância: {e}")
            return {}
    
    def _save_model(self, model_type: str, model: Any, metrics: Dict) -> None:
        """Salva modelo treinado"""
        try:
            # Salvar modelo
            model_path = self.models_dir / f"{model_type}_model.joblib"
            joblib.dump(model, model_path)
            
            # Salvar métricas
            metrics_path = self.models_dir / f"{model_type}_metrics.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            # Salvar metadados
            metadata = {
                'model_type': model_type,
                'training_date': datetime.now().isoformat(),
                'features_count': model.n_features_in_ if hasattr(model, 'n_features_in_') else 'unknown',
                'model_class': model.__class__.__name__,
                'metrics': metrics
            }
            
            metadata_path = self.models_dir / f"{model_type}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Modelo {model_type} salvo em: {model_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo {model_type}: {e}")
    
    def _load_existing_model(self, model_type: str) -> Dict[str, Any]:
        """Carrega modelo existente"""
        try:
            model_path = self.models_dir / f"{model_type}_model.joblib"
            metrics_path = self.models_dir / f"{model_type}_metrics.json"
            metadata_path = self.models_dir / f"{model_type}_metadata.json"
            
            if not all(p.exists() for p in [model_path, metrics_path, metadata_path]):
                raise FileNotFoundError(f"Arquivos do modelo {model_type} incompletos")
            
            # Carregar modelo
            model = joblib.load(model_path)
            self.trained_models[model_type] = model
            
            # Carregar métricas
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # Carregar metadados
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return {
                'status': 'loaded',
                'model_type': model_type,
                'metrics': metrics,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_type}: {e}")
            raise
    
    def _save_consolidated_metrics(self, results: Dict[str, Dict]) -> None:
        """Salva métricas consolidadas de todos os modelos"""
        try:
            consolidated = {
                'training_session': datetime.now().isoformat(),
                'models_count': len(results),
                'results': results,
                'summary': {
                    'successful': len([r for r in results.values() if r.get('status') == 'success']),
                    'errors': len([r for r in results.values() if r.get('status') == 'error']),
                    'loaded': len([r for r in results.values() if r.get('status') == 'loaded'])
                }
            }
            
            metrics_file = self.models_dir / "consolidated_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(consolidated, f, indent=2)
            
            logger.info(f"Métricas consolidadas salvas em: {metrics_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas consolidadas: {e}")
    
    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance de todos os modelos"""
        summary = {
            'total_models': len(self.model_metrics),
            'models': {},
            'overall_performance': {}
        }
        
        for model_type, metrics in self.model_metrics.items():
            summary['models'][model_type] = {
                'metrics': metrics,
                'status': 'trained' if model_type in self.trained_models else 'missing'
            }
        
        # Calcular performance geral
        if self.model_metrics:
            if 'result_prediction' in self.model_metrics:
                summary['overall_performance']['classification'] = {
                    'avg_accuracy': np.mean([
                        m.get('accuracy', 0) for m in self.model_metrics.values() 
                        if 'accuracy' in m
                    ]),
                    'avg_f1': np.mean([
                        m.get('f1_macro', 0) for m in self.model_metrics.values() 
                        if 'f1_macro' in m
                    ])
                }
            
            if 'total_goals_prediction' in self.model_metrics:
                summary['overall_performance']['regression'] = {
                    'avg_r2': np.mean([
                        m.get('r2', 0) for m in self.model_metrics.values() 
                        if 'r2' in m
                    ]),
                    'avg_rmse': np.mean([
                        m.get('rmse', 0) for m in self.model_metrics.values() 
                        if 'rmse' in m
                    ])
                }
        
        return summary

# Instância global
model_trainer = ModelTrainer()

# Funções de conveniência
def train_all_models(force_retrain: bool = False) -> Dict[str, Dict]:
    """Treina todos os modelos"""
    return model_trainer.train_all_models(force_retrain)

def train_model_for_type(model_type: str, **kwargs) -> Dict[str, Any]:
    """Treina modelo para tipo específico"""
    return model_trainer.train_model_for_type(model_type, **kwargs)

def get_model_performance_summary() -> Dict[str, Any]:
    """Retorna resumo de performance dos modelos"""
    return model_trainer.get_model_performance_summary()
