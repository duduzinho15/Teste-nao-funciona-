#!/usr/bin/env python3
"""
Sistema de Monitoramento de Performance para APIs RapidAPI

Este módulo implementa monitoramento em tempo real de:
- Tempo de resposta das APIs
- Taxa de sucesso/falha
- Uso de recursos
- Alertas automáticos
- Métricas de performance
"""

import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import json

@dataclass
class PerformanceMetrics:
    """Métricas de performance de uma API"""
    api_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_counts: Dict[str, int] = field(default_factory=dict)
    last_request_time: Optional[datetime] = None
    first_request_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em porcentagem"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Taxa de falha em porcentagem"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    @property
    def average_response_time(self) -> float:
        """Tempo médio de resposta em segundos"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def median_response_time(self) -> float:
        """Tempo mediano de resposta em segundos"""
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        """95º percentil do tempo de resposta"""
        if len(self.response_times) < 20:
            return self.average_response_time
        
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    @property
    def requests_per_minute(self) -> float:
        """Requisições por minuto"""
        if not self.first_request_time or not self.last_request_time:
            return 0.0
        
        duration = (self.last_request_time - self.first_request_time).total_seconds() / 60
        if duration == 0:
            return 0.0
        
        return self.total_requests / duration

@dataclass
class AlertThreshold:
    """Configuração de alerta"""
    metric: str
    operator: str  # >, <, >=, <=, ==
    value: float
    severity: str = "warning"  # warning, error, critical
    cooldown: int = 300  # Segundos entre alertas

class PerformanceMonitor:
    """
    Monitor de performance para APIs RapidAPI
    
    Funcionalidades:
    - Coleta métricas em tempo real
    - Calcula estatísticas de performance
    - Gera alertas automáticos
    - Exporta relatórios
    - Monitoramento de tendências
    """
    
    def __init__(self):
        self.logger = logging.getLogger("rapidapi.performance")
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.alert_thresholds: List[AlertThreshold] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.alert_callbacks: List[Callable] = []
        
        # Configura alertas padrão
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Configura alertas padrão para monitoramento"""
        self.alert_thresholds = [
            AlertThreshold("success_rate", "<", 80.0, "warning"),
            AlertThreshold("success_rate", "<", 60.0, "error"),
            AlertThreshold("success_rate", "<", 40.0, "critical"),
            AlertThreshold("average_response_time", ">", 5.0, "warning"),
            AlertThreshold("average_response_time", ">", 10.0, "error"),
            AlertThreshold("average_response_time", ">", 20.0, "critical"),
            AlertThreshold("failure_rate", ">", 20.0, "warning"),
            AlertThreshold("failure_rate", ">", 40.0, "error"),
            AlertThreshold("failure_rate", ">", 60.0, "critical")
        ]
    
    def register_api(self, api_name: str):
        """Registra uma API para monitoramento"""
        if api_name not in self.metrics:
            self.metrics[api_name] = PerformanceMetrics(api_name)
            self.logger.info(f"API {api_name} registrada para monitoramento")
    
    def unregister_api(self, api_name: str):
        """Remove uma API do monitoramento"""
        if api_name in self.metrics:
            del self.metrics[api_name]
            self.logger.info(f"API {api_name} removida do monitoramento")
    
    def record_request_start(self, api_name: str) -> float:
        """Registra início de uma requisição e retorna timestamp"""
        if api_name not in self.metrics:
            self.register_api(api_name)
        
        timestamp = time.time()
        metrics = self.metrics[api_name]
        
        if not metrics.first_request_time:
            metrics.first_request_time = datetime.now()
        
        metrics.last_request_time = datetime.now()
        metrics.total_requests += 1
        
        return timestamp
    
    def record_request_success(self, api_name: str, start_time: float, response_time: float):
        """Registra sucesso de uma requisição"""
        if api_name in self.metrics:
            metrics = self.metrics[api_name]
            metrics.successful_requests += 1
            metrics.response_times.append(response_time)
            
            self.logger.debug(f"Requisição bem-sucedida para {api_name}: {response_time:.3f}s")
    
    def record_request_failure(self, api_name: str, start_time: float, error_type: str, error_message: str):
        """Registra falha de uma requisição"""
        if api_name in self.metrics:
            metrics = self.metrics[api_name]
            metrics.failed_requests += 1
            
            if error_type not in metrics.error_counts:
                metrics.error_counts[error_type] = 0
            metrics.error_counts[error_type] += 1
            
            response_time = time.time() - start_time
            metrics.response_times.append(response_time)
            
            self.logger.warning(f"Requisição falhou para {api_name}: {error_type} - {error_message}")
    
    def add_alert_threshold(self, threshold: AlertThreshold):
        """Adiciona um novo limiar de alerta"""
        self.alert_thresholds.append(threshold)
        self.logger.info(f"Novo limiar de alerta adicionado: {threshold.metric} {threshold.operator} {threshold.value}")
    
    def add_alert_callback(self, callback: Callable):
        """Adiciona callback para processamento de alertas"""
        self.alert_callbacks.append(callback)
        self.logger.info("Novo callback de alerta adicionado")
    
    async def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.monitoring_task and not self.monitoring_task.done():
            return
        
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Monitoramento de performance iniciado")
    
    async def stop_monitoring(self):
        """Para monitoramento contínuo"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            self.logger.info("Monitoramento de performance parado")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while True:
            try:
                await self._check_alerts()
                await self._cleanup_old_alerts()
                await asyncio.sleep(30)  # Verifica a cada 30 segundos
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(30)
    
    async def _check_alerts(self):
        """Verifica se algum limiar de alerta foi atingido"""
        current_time = time.time()
        
        for api_name, metrics in self.metrics.items():
            for threshold in self.alert_thresholds:
                # Obtém valor atual da métrica
                current_value = self._get_metric_value(metrics, threshold.metric)
                if current_value is None:
                    continue
                
                # Verifica se o limiar foi atingido
                if self._check_threshold(current_value, threshold.operator, threshold.value):
                    # Verifica cooldown
                    if self._can_trigger_alert(api_name, threshold, current_time):
                        await self._trigger_alert(api_name, threshold, current_value)
    
    def _get_metric_value(self, metrics: PerformanceMetrics, metric_name: str) -> Optional[float]:
        """Obtém valor atual de uma métrica específica"""
        if metric_name == "success_rate":
            return metrics.success_rate
        elif metric_name == "failure_rate":
            return metrics.failure_rate
        elif metric_name == "average_response_time":
            return metrics.average_response_time
        elif metric_name == "median_response_time":
            return metrics.median_response_time
        elif metric_name == "p95_response_time":
            return metrics.p95_response_time
        elif metric_name == "requests_per_minute":
            return metrics.requests_per_minute
        return None
    
    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Verifica se um valor atinge um limiar"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return abs(value - threshold) < 0.001
        return False
    
    def _can_trigger_alert(self, api_name: str, threshold: AlertThreshold, current_time: float) -> bool:
        """Verifica se um alerta pode ser disparado (cooldown)"""
        alert_key = f"{api_name}_{threshold.metric}_{threshold.operator}_{threshold.value}"
        
        # Procura último alerta similar
        for alert in reversed(self.alerts):
            if (alert["api_name"] == api_name and 
                alert["metric"] == threshold.metric and
                alert["operator"] == threshold.operator and
                alert["threshold"] == threshold.value):
                
                time_since_last = current_time - alert["timestamp"]
                return time_since_last >= threshold.cooldown
        
        return True
    
    async def _trigger_alert(self, api_name: str, threshold: AlertThreshold, current_value: float):
        """Dispara um alerta"""
        alert = {
            "timestamp": time.time(),
            "api_name": api_name,
            "metric": threshold.metric,
            "operator": threshold.operator,
            "threshold": threshold.value,
            "current_value": current_value,
            "severity": threshold.severity,
            "message": f"API {api_name}: {threshold.metric} {threshold.operator} {threshold.value} (atual: {current_value:.2f})"
        }
        
        self.alerts.append(alert)
        
        # Log do alerta
        if threshold.severity == "critical":
            self.logger.critical(alert["message"])
        elif threshold.severity == "error":
            self.logger.error(alert["message"])
        else:
            self.logger.warning(alert["message"])
        
        # Executa callbacks de alerta
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Erro no callback de alerta: {e}")
    
    async def _cleanup_old_alerts(self):
        """Remove alertas antigos (mais de 24 horas)"""
        current_time = time.time()
        cutoff_time = current_time - 86400  # 24 horas
        
        self.alerts = [alert for alert in self.alerts if alert["timestamp"] > cutoff_time]
    
    def get_api_metrics(self, api_name: str) -> Optional[PerformanceMetrics]:
        """Retorna métricas de uma API específica"""
        return self.metrics.get(api_name)
    
    def get_all_metrics(self) -> Dict[str, PerformanceMetrics]:
        """Retorna métricas de todas as APIs"""
        return self.metrics.copy()
    
    def get_alerts(self, severity: Optional[str] = None, 
                   api_name: Optional[str] = None, 
                   hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna alertas filtrados"""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        filtered_alerts = []
        for alert in self.alerts:
            if alert["timestamp"] < cutoff_time:
                continue
            
            if severity and alert["severity"] != severity:
                continue
            
            if api_name and alert["api_name"] != api_name:
                continue
            
            filtered_alerts.append(alert)
        
        return filtered_alerts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo geral de performance"""
        summary = {
            "total_apis": len(self.metrics),
            "total_requests": 0,
            "total_successful": 0,
            "total_failed": 0,
            "overall_success_rate": 0.0,
            "apis_by_performance": [],
            "recent_alerts": len([a for a in self.alerts if time.time() - a["timestamp"] < 3600])
        }
        
        if self.metrics:
            for api_name, metrics in self.metrics.items():
                summary["total_requests"] += metrics.total_requests
                summary["total_successful"] += metrics.successful_requests
                summary["total_failed"] += metrics.failed_requests
                
                summary["apis_by_performance"].append({
                    "api_name": api_name,
                    "success_rate": metrics.success_rate,
                    "average_response_time": metrics.average_response_time,
                    "requests_per_minute": metrics.requests_per_minute
                })
            
            if summary["total_requests"] > 0:
                summary["overall_success_rate"] = (summary["total_successful"] / summary["total_requests"]) * 100
            
            # Ordena APIs por performance
            summary["apis_by_performance"].sort(key=lambda x: x["success_rate"], reverse=True)
        
        return summary
    
    def export_metrics(self, format: str = "json") -> str:
        """Exporta métricas em diferentes formatos"""
        if format == "json":
            return json.dumps(self.get_performance_summary(), indent=2, default=str)
        elif format == "csv":
            return self._export_csv()
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _export_csv(self) -> str:
        """Exporta métricas em formato CSV"""
        lines = ["API,Total Requests,Success Rate,Avg Response Time,Requests/Min"]
        
        for api_name, metrics in self.metrics.items():
            line = f"{api_name},{metrics.total_requests},{metrics.success_rate:.2f}%,{metrics.average_response_time:.3f},{metrics.requests_per_minute:.2f}"
            lines.append(line)
        
        return "\n".join(lines)

# Instância global do monitor de performance
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Retorna a instância global do monitor de performance"""
    return performance_monitor

# Decorator para monitorar performance de funções
def monitor_performance(api_name: str):
    """Decorator para monitorar performance de funções de API"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = monitor.record_request_start(api_name)
            
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                monitor.record_request_success(api_name, start_time, response_time)
                return result
            except Exception as e:
                response_time = time.time() - start_time
                error_type = type(e).__name__
                monitor.record_request_failure(api_name, start_time, error_type, str(e))
                raise
        
        return wrapper
    return decorator
