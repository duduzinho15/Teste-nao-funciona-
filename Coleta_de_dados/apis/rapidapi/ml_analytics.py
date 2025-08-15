#!/usr/bin/env python3
"""
Sistema de Machine Learning para Análise Preditiva RapidAPI

Este módulo implementa:
- Análise preditiva de falhas de APIs
- Otimização automática de thresholds de alerta
- Detecção de anomalias em tempo real
- Modelos de ML para previsão de performance
- Auto-tuning de parâmetros do sistema
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pickle
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Importa módulos do sistema
from .production_config import load_production_config
from .performance_monitor import get_performance_monitor
from .alert_system import get_alert_manager
from .notification_system import get_notification_manager, NotificationMessage

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    from sklearn.cluster import KMeans
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  Scikit-learn não disponível. Funcionalidades de ML limitadas.")

@dataclass
class MLModel:
    """Modelo de Machine Learning"""
    name: str
    model_type: str  # 'anomaly', 'prediction', 'clustering'
    model: Any
    scaler: Optional[Any] = None
    features: List[str] = field(default_factory=list)
    accuracy: float = 0.0
    last_trained: Optional[datetime] = None
    training_samples: int = 0
    
    def save(self, filepath: str):
        """Salva o modelo"""
        try:
            model_data = {
                'name': self.name,
                'model_type': self.model_type,
                'features': self.features,
                'accuracy': self.accuracy,
                'last_trained': self.last_trained.isoformat() if self.last_trained else None,
                'training_samples': self.training_samples
            }
            
            # Salva metadados
            with open(f"{filepath}_metadata.json", 'w') as f:
                json.dump(model_data, f, indent=2, default=str)
            
            # Salva modelo
            if self.model_type == 'anomaly':
                joblib.dump(self.model, f"{filepath}_model.pkl")
            elif self.model_type == 'prediction':
                joblib.dump(self.model, f"{filepath}_model.pkl")
                if self.scaler:
                    joblib.dump(self.scaler, f"{filepath}_scaler.pkl")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar modelo {self.name}: {e}")
            return False
    
    def load(self, filepath: str):
        """Carrega o modelo"""
        try:
            # Carrega metadados
            with open(f"{filepath}_metadata.json", 'r') as f:
                metadata = json.load(f)
                self.name = metadata['name']
                self.model_type = metadata['model_type']
                self.features = metadata['features']
                self.accuracy = metadata['accuracy']
                self.last_trained = datetime.fromisoformat(metadata['last_trained']) if metadata['last_trained'] else None
                self.training_samples = metadata['training_samples']
            
            # Carrega modelo
            if self.model_type == 'anomaly':
                self.model = joblib.load(f"{filepath}_model.pkl")
            elif self.model_type == 'prediction':
                self.model = joblib.load(f"{filepath}_model.pkl")
                try:
                    self.scaler = joblib.load(f"{filepath}_scaler.pkl")
                except:
                    self.scaler = None
            
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar modelo {self.name}: {e}")
            return False

@dataclass
class PredictionResult:
    """Resultado de uma predição"""
    timestamp: datetime
    api_name: str
    metric: str
    predicted_value: float
    confidence: float
    actual_value: Optional[float] = None
    error: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "api_name": self.api_name,
            "metric": self.metric,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "actual_value": self.actual_value,
            "error": self.error
        }

@dataclass
class AnomalyResult:
    """Resultado de detecção de anomalia"""
    timestamp: datetime
    api_name: str
    metric: str
    value: float
    anomaly_score: float
    is_anomaly: bool
    severity: str  # 'low', 'medium', 'high'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "api_name": self.api_name,
            "metric": str(self.metric),
            "value": self.value,
            "anomaly_score": self.anomaly_score,
            "is_anomaly": self.is_anomaly,
            "severity": self.severity
        }

class MLAnalytics:
    """Sistema de Machine Learning para Analytics"""
    
    def __init__(self):
        self.config = load_production_config()
        self.performance_monitor = get_performance_monitor()
        self.alert_manager = get_alert_manager()
        self.notification_manager = get_notification_manager()
        self.logger = logging.getLogger("ml.analytics")
        
        # Modelos ML
        self.models: Dict[str, MLModel] = {}
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Dados históricos
        self.historical_data: List[Dict[str, Any]] = []
        self.data_window_hours = 168  # 1 semana
        
        # Configurações
        self.auto_training_enabled = True
        self.training_interval_hours = 24
        self.min_training_samples = 100
        self.anomaly_threshold = 0.7
        
        # Inicializa modelos
        self._initialize_models()
        
        # Inicia coleta de dados
        self._start_data_collection()
    
    def _initialize_models(self):
        """Inicializa modelos de ML"""
        if not ML_AVAILABLE:
            self.logger.warning("⚠️  ML não disponível - usando modelos básicos")
            return
        
        try:
            # Modelo de detecção de anomalias
            anomaly_model = MLModel(
                name="anomaly_detector",
                model_type="anomaly",
                model=IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                ),
                features=["success_rate", "response_time", "error_rate", "requests_per_minute"]
            )
            self.models["anomaly_detector"] = anomaly_model
            
            # Modelo de predição de performance
            prediction_model = MLModel(
                name="performance_predictor",
                model_type="prediction",
                model=RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                ),
                features=["hour", "day_of_week", "previous_success_rate", "previous_response_time"]
            )
            self.models["performance_predictor"] = prediction_model
            
            # Modelo de clustering para padrões
            clustering_model = MLModel(
                name="pattern_clusterer",
                model_type="clustering",
                model=KMeans(n_clusters=5, random_state=42),
                features=["success_rate", "response_time", "error_rate"]
            )
            self.models["pattern_clusterer"] = clustering_model
            
            self.logger.info(f"✅ {len(self.models)} modelos ML inicializados")
            
            # Tenta carregar modelos salvos
            self._load_saved_models()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar modelos ML: {e}")
    
    def _load_saved_models(self):
        """Carrega modelos salvos anteriormente"""
        for model_name, model in self.models.items():
            model_path = self.models_dir / model_name
            if model_path.with_suffix("_metadata.json").exists():
                if model.load(str(model_path)):
                    self.logger.info(f"✅ Modelo {model_name} carregado")
                else:
                    self.logger.warning(f"⚠️  Falha ao carregar modelo {model_name}")
    
    def _start_data_collection(self):
        """Inicia coleta automática de dados"""
        try:
            # Não inicia automaticamente - será iniciado quando necessário
            self.logger.info("🔄 Coleta automática de dados configurada")
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar coleta de dados: {e}")
    
    async def start_data_collection(self):
        """Inicia coleta de dados quando chamado explicitamente"""
        try:
            asyncio.create_task(self._data_collection_loop())
            self.logger.info("🔄 Coleta automática de dados iniciada")
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar coleta de dados: {e}")
    
    async def _data_collection_loop(self):
        """Loop de coleta de dados"""
        while True:
            try:
                await self._collect_current_data()
                await asyncio.sleep(300)  # 5 minutos
            except Exception as e:
                self.logger.error(f"❌ Erro na coleta de dados: {e}")
                await asyncio.sleep(600)  # 10 minutos
    
    async def _collect_current_data(self):
        """Coleta dados atuais do sistema"""
        try:
            # Obtém métricas de performance
            performance_data = self.performance_monitor.get_performance_summary()
            
            # Obtém dados do sistema
            system_data = {
                "timestamp": datetime.now(),
                "hour": datetime.now().hour,
                "day_of_week": datetime.now().weekday(),
                "overall_success_rate": performance_data.get("overall_success_rate", 0),
                "overall_response_time": performance_data.get("overall_average_response_time", 0),
                "total_requests": performance_data.get("total_requests", 0),
                "active_apis": len(performance_data.get("apis", {}))
            }
            
            # Adiciona dados por API
            for api_name, api_data in performance_data.get("apis", {}).items():
                api_record = {
                    **system_data,
                    "api_name": api_name,
                    "success_rate": api_data.get("success_rate", 0),
                    "response_time": api_data.get("average_response_time", 0),
                    "error_rate": 100 - api_data.get("success_rate", 0),
                    "requests_per_minute": api_data.get("requests_per_minute", 0)
                }
                
                self.historical_data.append(api_record)
            
            # Mantém apenas dados recentes
            cutoff_time = datetime.now() - timedelta(hours=self.data_window_hours)
            self.historical_data = [
                record for record in self.historical_data
                if record["timestamp"] >= cutoff_time
            ]
            
            # Log de coleta
            if len(self.historical_data) % 100 == 0:
                self.logger.info(f"📊 Dados coletados: {len(self.historical_data)} registros")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar dados: {e}")
    
    def _prepare_features(self, data: List[Dict[str, Any]], target_metric: str = "success_rate") -> Tuple[np.ndarray, np.ndarray]:
        """Prepara features para treinamento"""
        try:
            if not data:
                return np.array([]), np.array([])
            
            # Converte para DataFrame
            df = pd.DataFrame(data)
            
            # Seleciona features numéricas
            feature_columns = ["hour", "day_of_week", "success_rate", "response_time", "error_rate", "requests_per_minute"]
            feature_columns = [col for col in feature_columns if col in df.columns]
            
            # Remove linhas com valores NaN
            df = df.dropna(subset=feature_columns + [target_metric])
            
            if df.empty:
                return np.array([]), np.array([])
            
            # Prepara X e y
            X = df[feature_columns].values
            y = df[target_metric].values
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao preparar features: {e}")
            return np.array([]), np.array([])
    
    async def train_anomaly_detector(self):
        """Treina modelo de detecção de anomalias"""
        if not ML_AVAILABLE or "anomaly_detector" not in self.models:
            return False
        
        try:
            model = self.models["anomaly_detector"]
            
            # Prepara dados
            X, _ = self._prepare_features(self.historical_data)
            
            if len(X) < self.min_training_samples:
                self.logger.info(f"⚠️  Dados insuficientes para treinar {model.name}: {len(X)} < {self.min_training_samples}")
                return False
            
            # Treina modelo
            model.model.fit(X)
            model.last_trained = datetime.now()
            model.training_samples = len(X)
            
            # Salva modelo
            model_path = self.models_dir / model.name
            model.save(str(model_path))
            
            self.logger.info(f"✅ Modelo {model.name} treinado com {len(X)} amostras")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao treinar modelo de anomalias: {e}")
            return False
    
    async def train_performance_predictor(self):
        """Treina modelo de predição de performance"""
        if not ML_AVAILABLE or "performance_predictor" not in self.models:
            return False
        
        try:
            model = self.models["performance_predictor"]
            
            # Prepara dados
            X, y = self._prepare_features(self.historical_data, "success_rate")
            
            if len(X) < self.min_training_samples:
                self.logger.info(f"⚠️  Dados insuficientes para treinar {model.name}: {len(X)} < {self.min_training_samples}")
                return False
            
            # Split treino/teste
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Treina modelo
            model.model.fit(X_train, y_train)
            
            # Avalia modelo
            y_pred = model.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            model.accuracy = 1 / (1 + mse)  # Converte MSE para score de 0-1
            model.last_trained = datetime.now()
            model.training_samples = len(X)
            
            # Salva modelo
            model_path = self.models_dir / model.name
            model.save(str(model_path))
            
            self.logger.info(f"✅ Modelo {model.name} treinado - MSE: {mse:.4f}, MAE: {mae:.4f}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao treinar modelo de predição: {e}")
            return False
    
    async def train_pattern_clusterer(self):
        """Treina modelo de clustering de padrões"""
        if not ML_AVAILABLE or "pattern_clusterer" not in self.models:
            return False
        
        try:
            model = self.models["pattern_clusterer"]
            
            # Prepara dados
            X, _ = self._prepare_features(self.historical_data)
            
            if len(X) < self.min_training_samples:
                self.logger.info(f"⚠️  Dados insuficientes para treinar {model.name}: {len(X)} < {self.min_training_samples}")
                return False
            
            # Treina modelo
            model.model.fit(X)
            model.last_trained = datetime.now()
            model.training_samples = len(X)
            
            # Salva modelo
            model_path = self.models_dir / model.name
            model.save(str(model_path))
            
            self.logger.info(f"✅ Modelo {model.name} treinado com {len(X)} amostras")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao treinar modelo de clustering: {e}")
            return False
    
    async def train_all_models(self):
        """Treina todos os modelos"""
        self.logger.info("🚀 Iniciando treinamento de todos os modelos...")
        
        results = {
            "anomaly_detector": await self.train_anomaly_detector(),
            "performance_predictor": await self.train_performance_predictor(),
            "pattern_clusterer": await self.train_pattern_clusterer()
        }
        
        success_count = sum(results.values())
        self.logger.info(f"✅ Treinamento concluído: {success_count}/{len(results)} modelos")
        
        return results
    
    def detect_anomalies(self, api_name: str = None) -> List[AnomalyResult]:
        """Detecta anomalias nos dados"""
        if not ML_AVAILABLE or "anomaly_detector" not in self.models:
            return []
        
        try:
            model = self.models["anomaly_detector"]
            
            if not model.last_trained:
                self.logger.warning("⚠️  Modelo de anomalias não treinado")
                return []
            
            # Filtra dados por API se especificado
            data = self.historical_data
            if api_name:
                data = [record for record in data if record.get("api_name") == api_name]
            
            if not data:
                return []
            
            # Prepara features
            X, _ = self._prepare_features(data)
            if len(X) == 0:
                return []
            
            # Prediz anomalias
            anomaly_scores = model.model.decision_function(X)
            predictions = model.model.predict(X)
            
            # Converte scores para probabilidades (0-1)
            anomaly_scores = 1 - (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min())
            
            # Cria resultados
            results = []
            for i, record in enumerate(data):
                if i < len(anomaly_scores):
                    score = anomaly_scores[i]
                    is_anomaly = score > self.anomaly_threshold
                    
                    # Determina severidade
                    if score > 0.9:
                        severity = "high"
                    elif score > 0.7:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    result = AnomalyResult(
                        timestamp=record["timestamp"],
                        api_name=record.get("api_name", "unknown"),
                        metric="overall",
                        value=record.get("success_rate", 0),
                        anomaly_score=score,
                        is_anomaly=is_anomaly,
                        severity=severity
                    )
                    
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao detectar anomalias: {e}")
            return []
    
    def predict_performance(self, api_name: str, hours_ahead: int = 1) -> List[PredictionResult]:
        """Prediz performance futura"""
        if not ML_AVAILABLE or "performance_predictor" not in self.models:
            return []
        
        try:
            model = self.models["performance_predictor"]
            
            if not model.last_trained:
                self.logger.warning("⚠️  Modelo de predição não treinado")
                return []
            
            # Filtra dados da API
            api_data = [record for record in self.historical_data if record.get("api_name") == api_name]
            
            if not api_data:
                return []
            
            # Obtém dados mais recentes para features
            latest_record = max(api_data, key=lambda x: x["timestamp"])
            
            predictions = []
            current_time = datetime.now()
            
            for hour in range(1, hours_ahead + 1):
                # Calcula hora futura
                future_time = current_time + timedelta(hours=hour)
                
                # Prepara features para predição
                features = np.array([[
                    future_time.hour,
                    future_time.weekday(),
                    latest_record.get("success_rate", 0),
                    latest_record.get("response_time", 0)
                ]])
                
                # Faz predição
                predicted_value = model.model.predict(features)[0]
                
                # Calcula confiança baseada na variância dos dados
                confidence = min(0.95, max(0.5, 1 - abs(predicted_value - 50) / 100))
                
                result = PredictionResult(
                    timestamp=future_time,
                    api_name=api_name,
                    metric="success_rate",
                    predicted_value=predicted_value,
                    confidence=confidence
                )
                
                predictions.append(result)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao predizer performance: {e}")
            return []
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analisa padrões nos dados usando clustering"""
        if not ML_AVAILABLE or "pattern_clusterer" not in self.models:
            return {}
        
        try:
            model = self.models["pattern_clusterer"]
            
            if not model.last_trained:
                return {}
            
            # Prepara dados
            X, _ = self._prepare_features(self.historical_data)
            if len(X) == 0:
                return {}
            
            # Faz clustering
            clusters = model.model.predict(X)
            
            # Analisa padrões por cluster
            df = pd.DataFrame(X, columns=model.features)
            df['cluster'] = clusters
            
            pattern_analysis = {}
            for cluster_id in range(model.model.n_clusters):
                cluster_data = df[df['cluster'] == cluster_id]
                
                if len(cluster_data) > 0:
                    pattern_analysis[f"cluster_{cluster_id}"] = {
                        "size": len(cluster_data),
                        "percentage": len(cluster_data) / len(df) * 100,
                        "avg_success_rate": cluster_data['success_rate'].mean(),
                        "avg_response_time": cluster_data['response_time'].mean(),
                        "avg_error_rate": cluster_data['error_rate'].mean(),
                        "characteristics": self._describe_cluster(cluster_data)
                    }
            
            return pattern_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao analisar padrões: {e}")
            return {}
    
    def _describe_cluster(self, cluster_data: pd.DataFrame) -> str:
        """Descreve características de um cluster"""
        try:
            avg_success = cluster_data['success_rate'].mean()
            avg_response = cluster_data['response_time'].mean()
            
            if avg_success > 90 and avg_response < 1.0:
                return "Alta performance - APIs estáveis e rápidas"
            elif avg_success > 80 and avg_response < 2.0:
                return "Performance boa - APIs funcionando bem"
            elif avg_success > 60:
                return "Performance moderada - Alguns problemas"
            else:
                return "Performance baixa - Problemas significativos"
                
        except Exception:
            return "Características não disponíveis"
    
    async def optimize_alert_thresholds(self) -> Dict[str, Any]:
        """Otimiza thresholds de alerta baseado em análise ML"""
        try:
            # Analisa padrões históricos
            patterns = self.analyze_patterns()
            
            if not patterns:
                return {"message": "Dados insuficientes para otimização"}
            
            # Calcula thresholds otimizados
            optimized_thresholds = {}
            
            # Threshold para taxa de sucesso
            success_rates = []
            for cluster_info in patterns.values():
                success_rates.append(cluster_info['avg_success_rate'])
            
            if success_rates:
                # Threshold baseado no percentil 25 dos dados
                success_threshold = np.percentile(success_rates, 25)
                optimized_thresholds['success_rate'] = max(60, min(85, success_threshold))
            
            # Threshold para tempo de resposta
            response_times = []
            for cluster_info in patterns.values():
                response_times.append(cluster_info['avg_response_time'])
            
            if response_times:
                # Threshold baseado no percentil 75 dos dados
                response_threshold = np.percentile(response_times, 75)
                optimized_thresholds['response_time'] = max(1.0, min(10.0, response_threshold))
            
            # Threshold para taxa de erro
            if 'success_rate' in optimized_thresholds:
                optimized_thresholds['error_rate'] = 100 - optimized_thresholds['success_rate']
            
            # Aplica thresholds otimizados
            if optimized_thresholds:
                await self._apply_optimized_thresholds(optimized_thresholds)
            
            return {
                "optimized_thresholds": optimized_thresholds,
                "patterns_analyzed": len(patterns),
                "optimization_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao otimizar thresholds: {e}")
            return {"error": str(e)}
    
    async def _apply_optimized_thresholds(self, thresholds: Dict[str, float]):
        """Aplica thresholds otimizados ao sistema de alertas"""
        try:
            alert_manager = get_alert_manager()
            
            # Atualiza regras existentes
            for rule in alert_manager.alert_rules:
                if rule.metric in thresholds:
                    old_threshold = rule.threshold
                    new_threshold = thresholds[rule.metric]
                    
                    # Atualiza threshold
                    rule.threshold = new_threshold
                    
                    self.logger.info(f"🔄 Threshold otimizado para {rule.name}: {old_threshold:.2f} → {new_threshold:.2f}")
            
            # Envia notificação de otimização
            notification = NotificationMessage(
                title="🔧 Thresholds Otimizados",
                content=f"Thresholds de alerta foram otimizados automaticamente: {thresholds}",
                severity="info",
                metadata={
                    "optimization_type": "ml_optimization",
                    "thresholds": thresholds,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            await self.notification_manager.send_notification(notification)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar thresholds otimizados: {e}")
    
    async def generate_ml_report(self) -> Dict[str, Any]:
        """Gera relatório completo de ML"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "models_status": {},
                "data_summary": {
                    "total_records": len(self.historical_data),
                    "data_window_hours": self.data_window_hours,
                    "apis_monitored": len(set(record.get("api_name") for record in self.historical_data if record.get("api_name")))
                },
                "anomalies": {
                    "recent_detections": len([r for r in self.detect_anomalies() if r.is_anomaly])
                },
                "predictions": {},
                "patterns": self.analyze_patterns(),
                "optimization": await self.optimize_alert_thresholds()
            }
            
            # Status dos modelos
            for model_name, model in self.models.items():
                report["models_status"][model_name] = {
                    "trained": model.last_trained is not None,
                    "last_trained": model.last_trained.isoformat() if model.last_trained else None,
                    "training_samples": model.training_samples,
                    "accuracy": model.accuracy
                }
            
            # Predições para APIs principais
            apis = set(record.get("api_name") for record in self.historical_data if record.get("api_name"))
            for api_name in list(apis)[:5]:  # Top 5 APIs
                predictions = self.predict_performance(api_name, hours_ahead=3)
                if predictions:
                    report["predictions"][api_name] = [p.to_dict() for p in predictions]
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar relatório ML: {e}")
            return {"error": str(e)}
    
    async def auto_maintenance(self):
        """Executa manutenção automática dos modelos"""
        try:
            self.logger.info("🔧 Iniciando manutenção automática dos modelos...")
            
            # Verifica se precisa treinar
            needs_training = False
            for model in self.models.values():
                if (not model.last_trained or 
                    (datetime.now() - model.last_trained).total_seconds() > self.training_interval_hours * 3600):
                    needs_training = True
                    break
            
            if needs_training:
                self.logger.info("🔄 Treinando modelos...")
                await self.train_all_models()
            
            # Otimiza thresholds
            self.logger.info("⚡ Otimizando thresholds...")
            optimization_result = await self.optimize_alert_thresholds()
            
            # Gera relatório
            report = await self.generate_ml_report()
            
            self.logger.info("✅ Manutenção automática concluída")
            
            return {
                "maintenance_timestamp": datetime.now().isoformat(),
                "models_trained": needs_training,
                "thresholds_optimized": bool(optimization_result.get("optimized_thresholds")),
                "report_generated": bool(report)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na manutenção automática: {e}")
            return {"error": str(e)}

# Instância global do sistema ML
ml_analytics = MLAnalytics()

def get_ml_analytics() -> MLAnalytics:
    """Retorna a instância global do sistema ML"""
    return ml_analytics

# Funções de conveniência
async def train_ml_models():
    """Treina todos os modelos ML"""
    analytics = get_ml_analytics()
    return await analytics.train_all_models()

async def detect_api_anomalies(api_name: str = None):
    """Detecta anomalias em APIs"""
    analytics = get_ml_analytics()
    return analytics.detect_anomalies(api_name)

async def predict_api_performance(api_name: str, hours_ahead: int = 1):
    """Prediz performance de uma API"""
    analytics = get_ml_analytics()
    return analytics.predict_performance(api_name, hours_ahead)

async def optimize_system_thresholds():
    """Otimiza thresholds do sistema"""
    analytics = get_ml_analytics()
    return await analytics.optimize_alert_thresholds()

async def generate_ml_insights():
    """Gera insights de ML"""
    analytics = get_ml_analytics()
    return await analytics.generate_ml_report()

if __name__ == "__main__":
    # Demonstração do sistema ML
    async def demo_ml_system():
        """Demonstra o sistema de ML"""
        print("🤖 Demonstração do Sistema de Machine Learning")
        print("=" * 60)
        
        analytics = get_ml_analytics()
        
        # Mostra status dos modelos
        print(f"📊 Modelos disponíveis: {len(analytics.models)}")
        for name, model in analytics.models.items():
            status = "✅ Treinado" if model.last_trained else "⚠️  Não treinado"
            print(f"  • {name}: {status}")
        
        # Coleta dados por um tempo
        print(f"\n📈 Coletando dados...")
        await asyncio.sleep(10)
        
        # Treina modelos
        print(f"\n🚀 Treinando modelos...")
        training_results = await analytics.train_all_models()
        
        # Detecta anomalias
        print(f"\n🔍 Detectando anomalias...")
        anomalies = analytics.detect_anomalies()
        print(f"  • Anomalias detectadas: {len([a for a in anomalies if a.is_anomaly])}")
        
        # Prediz performance
        print(f"\n🔮 Predizendo performance...")
        apis = set(record.get("api_name") for record in analytics.historical_data if record.get("api_name"))
        if apis:
            api_name = list(apis)[0]
            predictions = analytics.predict_performance(api_name, hours_ahead=2)
            print(f"  • Predições para {api_name}: {len(predictions)}")
        
        # Analisa padrões
        print(f"\n📊 Analisando padrões...")
        patterns = analytics.analyze_patterns()
        print(f"  • Padrões identificados: {len(patterns)}")
        
        # Otimiza thresholds
        print(f"\n⚡ Otimizando thresholds...")
        optimization = await analytics.optimize_alert_thresholds()
        print(f"  • Thresholds otimizados: {bool(optimization.get('optimized_thresholds'))}")
        
        print(f"\n✅ Demonstração concluída!")
    
    asyncio.run(demo_ml_system())
