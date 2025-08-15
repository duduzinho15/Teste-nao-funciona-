#!/usr/bin/env python3
"""
Sistema de monitoramento e produção para Machine Learning
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import threading
from dataclasses import dataclass, asdict
import sqlite3
import sqlite3
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .database_integration import DatabaseIntegration

logger = logging.getLogger(__name__)

@dataclass
class ModelPerformance:
    """Métricas de performance de um modelo"""
    model_type: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    prediction_count: int
    error_count: int
    avg_inference_time: float
    memory_usage: float
    cpu_usage: float

@dataclass
class SystemHealth:
    """Status de saúde do sistema"""
    timestamp: datetime
    overall_status: str  # 'healthy', 'warning', 'critical'
    models_status: Dict[str, str]
    database_status: str
    cache_status: str
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int
    errors_last_hour: int
    warnings_last_hour: int

@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    timestamp: datetime
    level: str  # 'info', 'warning', 'error', 'critical'
    category: str
    message: str
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

class ProductionMonitoring:
    """Sistema de monitoramento e produção para ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.db_integration = DatabaseIntegration()
        
        # Diretórios
        self.monitoring_dir = Path(self.config.monitoring_dir)
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        self.dashboards_dir = self.monitoring_dir / "dashboards"
        self.dashboards_dir.mkdir(exist_ok=True)
        
        self.alerts_dir = self.monitoring_dir / "alerts"
        self.alerts_dir.mkdir(exist_ok=True)
        
        # Banco de dados de monitoramento
        self.monitoring_db = self.monitoring_dir / "monitoring.db"
        self._init_monitoring_db()
        
        # Configurações de alertas
        self.alert_thresholds = {
            'accuracy_threshold': 0.7,
            'error_rate_threshold': 0.1,
            'response_time_threshold': 2.0,  # segundos
            'memory_threshold': 0.8,  # 80% do uso de memória
            'cpu_threshold': 0.9,  # 90% do uso de CPU
            'disk_threshold': 0.9   # 90% do uso de disco
        }
        
        # Cache de métricas
        self.metrics_cache = {}
        self.health_cache = {}
        
        # Thread de monitoramento contínuo
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Inicializar monitoramento
        self.start_continuous_monitoring()
    
    def _init_monitoring_db(self):
        """Inicializa banco de dados de monitoramento"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            cursor = conn.cursor()
            
            # Tabela de performance dos modelos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    prediction_count INTEGER,
                    error_count INTEGER,
                    avg_inference_time REAL,
                    memory_usage REAL,
                    cpu_usage REAL
                )
            ''')
            
            # Tabela de saúde do sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_status TEXT NOT NULL,
                    models_status TEXT,
                    database_status TEXT,
                    cache_status TEXT,
                    memory_usage REAL,
                    cpu_usage REAL,
                    disk_usage REAL,
                    active_connections INTEGER,
                    errors_last_hour INTEGER,
                    warnings_last_hour INTEGER
                )
            ''')
            
            # Tabela de alertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabela de métricas em tempo real
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS real_time_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Banco de dados de monitoramento inicializado")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de monitoramento: {e}")
    
    def start_continuous_monitoring(self):
        """Inicia monitoramento contínuo em background"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.info("Monitoramento já está rodando")
            return
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Monitoramento contínuo iniciado")
    
    def stop_continuous_monitoring(self):
        """Para monitoramento contínuo"""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoramento contínuo parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self.stop_monitoring:
            try:
                # Coletar métricas
                self._collect_system_metrics()
                
                # Verificar saúde do sistema
                self._check_system_health()
                
                # Verificar alertas
                self._check_alerts()
                
                # Salvar métricas
                self._save_metrics()
                
                # Aguardar próximo ciclo
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguardar menos tempo em caso de erro
    
    def _collect_system_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # Métricas de sistema
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de rede
            network = psutil.net_io_counters()
            
            # Métricas de processos
            processes = len(psutil.pids())
            
            # Salvar métricas em tempo real
            self._save_real_time_metric('cpu_usage', cpu_percent, 'percent')
            self._save_real_time_metric('memory_usage', memory.percent, 'percent')
            self._save_real_time_metric('disk_usage', disk.percent, 'percent')
            self._save_real_time_metric('active_processes', processes, 'count')
            self._save_real_time_metric('network_bytes_sent', network.bytes_sent, 'bytes')
            self._save_real_time_metric('network_bytes_recv', network.bytes_recv, 'bytes')
            
            # Atualizar cache
            self.metrics_cache.update({
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'active_processes': processes,
                'network_io': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            })
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def _check_system_health(self):
        """Verifica saúde geral do sistema"""
        try:
            # Status dos modelos
            models_status = self._check_models_health()
            
            # Status do banco de dados
            database_status = self._check_database_health()
            
            # Status do cache
            cache_status = self._check_cache_health()
            
            # Determinar status geral
            overall_status = self._determine_overall_status(
                models_status, database_status, cache_status
            )
            
            # Criar objeto de saúde
            health = SystemHealth(
                timestamp=datetime.now(),
                overall_status=overall_status,
                models_status=models_status,
                database_status=database_status,
                cache_status=cache_status,
                memory_usage=self.metrics_cache.get('memory_usage', 0),
                cpu_usage=self.metrics_cache.get('cpu_usage', 0),
                disk_usage=self.metrics_cache.get('disk_usage', 0),
                active_connections=self._get_active_connections(),
                errors_last_hour=self._count_errors_last_hour(),
                warnings_last_hour=self._count_warnings_last_hour()
            )
            
            # Salvar no banco
            self._save_system_health(health)
            
            # Atualizar cache
            self.health_cache = asdict(health)
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do sistema: {e}")
    
    def _check_models_health(self) -> Dict[str, str]:
        """Verifica saúde dos modelos ML"""
        models_status = {}
        
        try:
            # Verificar se os modelos estão disponíveis
            models_dir = Path(self.config.models_dir)
            
            if not models_dir.exists():
                models_status['overall'] = 'critical'
                return models_status
            
            # Verificar cada tipo de modelo
            model_types = ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']
            
            for model_type in model_types:
                model_file = models_dir / f"{model_type}_model.joblib"
                metrics_file = models_dir / f"{model_type}_metrics.json"
                
                if model_file.exists() and metrics_file.exists():
                    # Verificar performance recente
                    performance = self._get_model_performance(model_type)
                    
                    if performance:
                        accuracy = performance.get('accuracy', 0)
                        if accuracy >= self.alert_thresholds['accuracy_threshold']:
                            models_status[model_type] = 'healthy'
                        elif accuracy >= 0.6:
                            models_status[model_type] = 'warning'
                        else:
                            models_status[model_type] = 'critical'
                    else:
                        models_status[model_type] = 'unknown'
                else:
                    models_status[model_type] = 'missing'
            
            # Status geral baseado na maioria
            healthy_count = sum(1 for s in models_status.values() if s == 'healthy')
            total_count = len(models_status)
            
            if healthy_count == total_count:
                models_status['overall'] = 'healthy'
            elif healthy_count >= total_count * 0.7:
                models_status['overall'] = 'warning'
            else:
                models_status['overall'] = 'critical'
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde dos modelos: {e}")
            models_status['overall'] = 'error'
        
        return models_status
    
    def _check_database_health(self) -> str:
        """Verifica saúde da conexão com banco de dados"""
        try:
            if self.db_integration.test_connection():
                return 'healthy'
            else:
                return 'critical'
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do banco: {e}")
            return 'error'
    
    def _check_cache_health(self) -> str:
        """Verifica saúde do sistema de cache"""
        try:
            from .cache_manager import get_cache_stats
            stats = get_cache_stats()
            
            if stats:
                hit_rate = stats.get('hit_rate', 0)
                if hit_rate >= 70:
                    return 'healthy'
                elif hit_rate >= 50:
                    return 'warning'
                else:
                    return 'critical'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do cache: {e}")
            return 'error'
    
    def _determine_overall_status(self, 
                                models_status: Dict[str, str],
                                database_status: str,
                                cache_status: str) -> str:
        """Determina status geral do sistema"""
        # Contar status críticos
        critical_count = 0
        warning_count = 0
        
        # Verificar modelos
        if models_status.get('overall') == 'critical':
            critical_count += 1
        elif models_status.get('overall') == 'warning':
            warning_count += 1
        
        # Verificar banco
        if database_status == 'critical':
            critical_count += 1
        elif database_status == 'warning':
            warning_count += 1
        
        # Verificar cache
        if cache_status == 'critical':
            critical_count += 1
        elif cache_status == 'warning':
            warning_count += 1
        
        # Determinar status geral
        if critical_count > 0:
            return 'critical'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'healthy'
    
    def _check_alerts(self):
        """Verifica e gera alertas"""
        try:
            # Verificar métricas de sistema
            self._check_system_alerts()
            
            # Verificar métricas dos modelos
            self._check_model_alerts()
            
            # Verificar métricas de negócio
            self._check_business_alerts()
            
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
    
    def _check_system_alerts(self):
        """Verifica alertas do sistema"""
        # CPU
        cpu_usage = self.metrics_cache.get('cpu_usage', 0)
        if cpu_usage > self.alert_thresholds['cpu_threshold'] * 100:
            self._create_alert(
                level='warning',
                category='system',
                message=f'Uso de CPU alto: {cpu_usage:.1f}%',
                details={'cpu_usage': cpu_usage, 'threshold': self.alert_thresholds['cpu_threshold'] * 100}
            )
        
        # Memória
        memory_usage = self.metrics_cache.get('memory_usage', 0)
        if memory_usage > self.alert_thresholds['memory_threshold'] * 100:
            self._create_alert(
                level='warning',
                category='system',
                message=f'Uso de memória alto: {memory_usage:.1f}%',
                details={'memory_usage': memory_usage, 'threshold': self.alert_thresholds['memory_threshold'] * 100}
            )
        
        # Disco
        disk_usage = self.metrics_cache.get('disk_usage', 0)
        if disk_usage > self.alert_thresholds['disk_threshold'] * 100:
            self._create_alert(
                level='warning',
                category='system',
                message=f'Uso de disco alto: {disk_usage:.1f}%',
                details={'disk_usage': disk_usage, 'threshold': self.alert_thresholds['disk_threshold'] * 100}
            )
    
    def _check_model_alerts(self):
        """Verifica alertas dos modelos"""
        try:
            # Verificar performance dos modelos
            for model_type in ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']:
                performance = self._get_model_performance(model_type)
                
                if performance:
                    accuracy = performance.get('accuracy', 0)
                    if accuracy < self.alert_thresholds['accuracy_threshold']:
                        self._create_alert(
                            level='warning',
                            category='model',
                            message=f'Performance baixa do modelo {model_type}: {accuracy:.3f}',
                            details={'model_type': model_type, 'accuracy': accuracy, 'threshold': self.alert_thresholds['accuracy_threshold']}
                        )
                    
                    error_rate = performance.get('error_count', 0) / max(performance.get('prediction_count', 1), 1)
                    if error_rate > self.alert_thresholds['error_rate_threshold']:
                        self._create_alert(
                            level='error',
                            category='model',
                            message=f'Taxa de erro alta do modelo {model_type}: {error_rate:.3f}',
                            details={'model_type': model_type, 'error_rate': error_rate, 'threshold': self.alert_thresholds['error_rate_threshold']}
                        )
        
        except Exception as e:
            logger.error(f"Erro ao verificar alertas dos modelos: {e}")
    
    def _check_business_alerts(self):
        """Verifica alertas de negócio"""
        try:
            # Verificar precisão das predições recentes
            recent_accuracy = self._get_recent_prediction_accuracy()
            
            if recent_accuracy and recent_accuracy < 0.6:
                self._create_alert(
                    level='warning',
                    category='business',
                    message=f'Precisão das predições baixa: {recent_accuracy:.3f}',
                    details={'recent_accuracy': recent_accuracy, 'threshold': 0.6}
                )
            
            # Verificar volume de predições
            prediction_volume = self._get_prediction_volume_last_hour()
            
            if prediction_volume < 10:  # Menos de 10 predições na última hora
                self._create_alert(
                    level='info',
                    category='business',
                    message=f'Volume baixo de predições: {prediction_volume} na última hora',
                    details={'prediction_volume': prediction_volume, 'threshold': 10}
                )
        
        except Exception as e:
            logger.error(f"Erro ao verificar alertas de negócio: {e}")
    
    def _create_alert(self, level: str, category: str, message: str, details: Dict[str, Any]):
        """Cria um novo alerta"""
        try:
            alert_id = f"{category}_{int(time.time())}"
            
            alert = Alert(
                id=alert_id,
                timestamp=datetime.now(),
                level=level,
                category=category,
                message=message,
                details=details
            )
            
            # Salvar no banco
            self._save_alert(alert)
            
            # Log do alerta
            if level in ['error', 'critical']:
                logger.error(f"ALERTA {level.upper()}: {message}")
            elif level == 'warning':
                logger.warning(f"ALERTA: {message}")
            else:
                logger.info(f"ALERTA: {message}")
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
    
    def get_system_dashboard(self) -> Dict[str, Any]:
        """Gera dashboard do sistema"""
        try:
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'system_health': self.health_cache,
                'current_metrics': self.metrics_cache,
                'recent_alerts': self._get_recent_alerts(limit=10),
                'model_performance': self._get_all_models_performance(),
                'system_stats': self._get_system_stats()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard: {e}")
            return {'error': str(e)}
    
    def generate_performance_report(self, 
                                  start_date: str = None,
                                  end_date: str = None) -> Dict[str, Any]:
        """Gera relatório de performance"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Obter dados do período
            conn = sqlite3.connect(self.monitoring_db)
            
            # Performance dos modelos
            query = '''
                SELECT * FROM model_performance 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            '''
            
            df_performance = pd.read_sql_query(query, conn, params=[start_date, end_date])
            
            # Saúde do sistema
            query = '''
                SELECT * FROM system_health 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            '''
            
            df_health = pd.read_sql_query(query, conn, params=[start_date, end_date])
            
            # Alertas
            query = '''
                SELECT * FROM alerts 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            '''
            
            df_alerts = pd.read_sql_query(query, conn, params=[start_date, end_date])
            
            conn.close()
            
            # Gerar relatório
            report = {
                'period': f"{start_date} a {end_date}",
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_predictions': df_performance['prediction_count'].sum() if not df_performance.empty else 0,
                    'avg_accuracy': df_performance['accuracy'].mean() if not df_performance.empty else 0,
                    'system_uptime': self._calculate_uptime(df_health),
                    'total_alerts': len(df_alerts),
                    'critical_alerts': len(df_alerts[df_alerts['level'] == 'critical'])
                },
                'model_performance': self._analyze_model_performance(df_performance),
                'system_health': self._analyze_system_health(df_health),
                'alerts_analysis': self._analyze_alerts(df_alerts)
            }
            
            # Salvar relatório
            self._save_performance_report(report, start_date, end_date)
            
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de performance: {e}")
            return {'error': str(e)}
    
    def _analyze_model_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa performance dos modelos"""
        if df.empty:
            return {'error': 'Nenhum dado de performance disponível'}
        
        analysis = {}
        
        for model_type in df['model_type'].unique():
            model_data = df[df['model_type'] == model_type]
            
            analysis[model_type] = {
                'total_predictions': model_data['prediction_count'].sum(),
                'avg_accuracy': model_data['accuracy'].mean(),
                'avg_precision': model_data['precision'].mean(),
                'avg_recall': model_data['recall'].mean(),
                'avg_f1_score': model_data['f1_score'].mean(),
                'avg_inference_time': model_data['avg_inference_time'].mean(),
                'trend': self._calculate_trend(model_data['accuracy'])
            }
        
        return analysis
    
    def _analyze_system_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa saúde do sistema"""
        if df.empty:
            return {'error': 'Nenhum dado de saúde disponível'}
        
        analysis = {
            'uptime_percentage': self._calculate_uptime(df),
            'avg_cpu_usage': df['cpu_usage'].mean(),
            'avg_memory_usage': df['memory_usage'].mean(),
            'avg_disk_usage': df['disk_usage'].mean(),
            'status_distribution': df['overall_status'].value_counts().to_dict(),
            'health_trend': self._calculate_trend(df['overall_status'].map({'healthy': 1, 'warning': 0.5, 'critical': 0}))
        }
        
        return analysis
    
    def _analyze_alerts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa alertas do sistema"""
        if df.empty:
            return {'total_alerts': 0, 'analysis': 'Nenhum alerta no período'}
        
        analysis = {
            'total_alerts': len(df),
            'level_distribution': df['level'].value_counts().to_dict(),
            'category_distribution': df['category'].value_counts().to_dict(),
            'resolved_alerts': df['resolved'].sum(),
            'acknowledged_alerts': df['acknowledged'].sum(),
            'avg_resolution_time': self._calculate_avg_resolution_time(df)
        }
        
        return analysis
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calcula tendência de uma série temporal"""
        if len(series) < 2:
            return 'stable'
        
        # Calcular correlação com tempo
        x = np.arange(len(series))
        correlation = np.corrcoef(x, series)[0, 1]
        
        if correlation > 0.1:
            return 'up'
        elif correlation < -0.1:
            return 'down'
        else:
            return 'stable'
    
    def _calculate_uptime(self, df: pd.DataFrame) -> float:
        """Calcula uptime do sistema"""
        if df.empty:
            return 0.0
        
        healthy_count = len(df[df['overall_status'] == 'healthy'])
        total_count = len(df)
        
        return (healthy_count / total_count) * 100 if total_count > 0 else 0.0
    
    def _calculate_avg_resolution_time(self, df: pd.DataFrame) -> float:
        """Calcula tempo médio de resolução de alertas"""
        # Implementar cálculo de tempo de resolução
        return 0.0
    
    def _get_model_performance(self, model_type: str) -> Optional[Dict[str, Any]]:
        """Obtém performance de um modelo específico"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            query = '''
                SELECT * FROM model_performance 
                WHERE model_type = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            '''
            
            df = pd.read_sql_query(query, conn, params=[model_type])
            conn.close()
            
            if not df.empty:
                return df.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter performance do modelo {model_type}: {e}")
            return None
    
    def _get_all_models_performance(self) -> Dict[str, Any]:
        """Obtém performance de todos os modelos"""
        performance = {}
        
        for model_type in ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']:
            performance[model_type] = self._get_model_performance(model_type)
        
        return performance
    
    def _get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém alertas recentes"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            query = '''
                SELECT * FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas recentes: {e}")
            return []
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do sistema"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            
            # Total de predições
            query = "SELECT SUM(prediction_count) as total FROM model_performance"
            total_predictions = pd.read_sql_query(query, conn).iloc[0]['total'] or 0
            
            # Total de alertas
            query = "SELECT COUNT(*) as total FROM alerts"
            total_alerts = pd.read_sql_query(query, conn).iloc[0]['total'] or 0
            
            # Alertas não resolvidos
            query = "SELECT COUNT(*) as total FROM alerts WHERE resolved = FALSE"
            unresolved_alerts = pd.read_sql_query(query, conn).iloc[0]['total'] or 0
            
            conn.close()
            
            return {
                'total_predictions': total_predictions,
                'total_alerts': total_alerts,
                'unresolved_alerts': unresolved_alerts,
                'system_start_time': self._get_system_start_time()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do sistema: {e}")
            return {}
    
    def _get_system_start_time(self) -> str:
        """Obtém tempo de início do sistema"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            query = "SELECT MIN(timestamp) as start_time FROM system_health"
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            if not result.empty and result.iloc[0]['start_time']:
                return result.iloc[0]['start_time']
            
            return datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Erro ao obter tempo de início: {e}")
            return datetime.now().isoformat()
    
    def _get_active_connections(self) -> int:
        """Obtém número de conexões ativas"""
        try:
            import psutil
            connections = psutil.net_connections()
            return len([c for c in connections if c.status == 'ESTABLISHED'])
        except:
            return 0
    
    def _count_errors_last_hour(self) -> int:
        """Conta erros na última hora"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            query = "SELECT COUNT(*) as count FROM alerts WHERE level IN ('error', 'critical') AND timestamp > ?"
            result = pd.read_sql_query(query, conn, params=[one_hour_ago])
            conn.close()
            
            return result.iloc[0]['count'] or 0
            
        except Exception as e:
            logger.error(f"Erro ao contar erros: {e}")
            return 0
    
    def _count_warnings_last_hour(self) -> int:
        """Conta warnings na última hora"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            query = "SELECT COUNT(*) as count FROM alerts WHERE level = 'warning' AND timestamp > ?"
            result = pd.read_sql_query(query, conn, params=[one_hour_ago])
            conn.close()
            
            return result.iloc[0]['count'] or 0
            
        except Exception as e:
            logger.error(f"Erro ao contar warnings: {e}")
            return 0
    
    def _get_recent_prediction_accuracy(self) -> Optional[float]:
        """Obtém precisão das predições recentes"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            query = "SELECT AVG(accuracy) as avg_accuracy FROM model_performance WHERE timestamp > ?"
            result = pd.read_sql_query(query, conn, params=[one_hour_ago])
            conn.close()
            
            return result.iloc[0]['avg_accuracy']
            
        except Exception as e:
            logger.error(f"Erro ao obter precisão recente: {e}")
            return None
    
    def _get_prediction_volume_last_hour(self) -> int:
        """Obtém volume de predições na última hora"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            query = "SELECT SUM(prediction_count) as total FROM model_performance WHERE timestamp > ?"
            result = pd.read_sql_query(query, conn, params=[one_hour_ago])
            conn.close()
            
            return result.iloc[0]['total'] or 0
            
        except Exception as e:
            logger.error(f"Erro ao obter volume de predições: {e}")
            return 0
    
    def _save_metrics(self):
        """Salva métricas coletadas"""
        # Implementar salvamento de métricas
        pass
    
    def _save_system_health(self, health: SystemHealth):
        """Salva saúde do sistema no banco"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_health (
                    timestamp, overall_status, models_status, database_status, 
                    cache_status, memory_usage, cpu_usage, disk_usage,
                    active_connections, errors_last_hour, warnings_last_hour
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                health.timestamp.isoformat(),
                health.overall_status,
                json.dumps(health.models_status),
                health.database_status,
                health.cache_status,
                health.memory_usage,
                health.cpu_usage,
                health.disk_usage,
                health.active_connections,
                health.errors_last_hour,
                health.warnings_last_hour
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar saúde do sistema: {e}")
    
    def _save_alert(self, alert: Alert):
        """Salva alerta no banco"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO alerts (
                    id, timestamp, level, category, message, details
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                alert.id,
                alert.timestamp.isoformat(),
                alert.level,
                alert.category,
                alert.message,
                json.dumps(alert.details)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar alerta: {e}")
    
    def _save_real_time_metric(self, name: str, value: float, unit: str):
        """Salva métrica em tempo real"""
        try:
            conn = sqlite3.connect(self.monitoring_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO real_time_metrics (timestamp, metric_name, metric_value, metric_unit)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), name, value, unit))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar métrica em tempo real: {e}")
    
    def _save_performance_report(self, report: Dict[str, Any], start_date: str, end_date: str):
        """Salva relatório de performance"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_report_{start_date}_to_{end_date}_{timestamp}.json"
            filepath = self.monitoring_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Relatório de performance salvo em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório de performance: {e}")

# Instância global
production_monitoring = ProductionMonitoring()

# Funções de conveniência
def get_system_dashboard() -> Dict[str, Any]:
    """Obtém dashboard do sistema"""
    return production_monitoring.get_system_dashboard()

def generate_performance_report(**kwargs) -> Dict[str, Any]:
    """Gera relatório de performance"""
    return production_monitoring.generate_performance_report(**kwargs)

def start_monitoring():
    """Inicia monitoramento"""
    production_monitoring.start_continuous_monitoring()

def stop_monitoring():
    """Para monitoramento"""
    production_monitoring.stop_continuous_monitoring()
