#!/usr/bin/env python3
"""
Integração com Prometheus e Grafana para Monitoramento Avançado

Este módulo implementa:
- Exportador de métricas Prometheus
- Métricas customizadas para RapidAPI
- Integração com Grafana
- Alertas baseados em Prometheus
- Histórico de métricas persistente
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
from aiohttp import web
import prometheus_client
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, REGISTRY
)

# Importa módulos do sistema
from .production_config import load_production_config
from .performance_monitor import get_performance_monitor
from .alert_system import get_alert_manager
from .ml_analytics import get_ml_analytics

@dataclass
class PrometheusMetric:
    """Métrica do Prometheus"""
    name: str
    description: str
    labels: List[str]
    metric_type: str  # 'counter', 'gauge', 'histogram', 'summary'
    metric_object: Any
    last_update: datetime = field(default_factory=datetime.now)
    
    def update(self, value: float, labels: Dict[str, str] = None):
        """Atualiza métrica"""
        try:
            if labels is None:
                labels = {}
            
            if self.metric_type == 'counter':
                self.metric_object.labels(**labels).inc(value)
            elif self.metric_type == 'gauge':
                self.metric_object.labels(**labels).set(value)
            elif self.metric_type == 'histogram':
                self.metric_object.labels(**labels).observe(value)
            elif self.metric_type == 'summary':
                self.metric_object.labels(**labels).observe(value)
            
            self.last_update = datetime.now()
            
        except Exception as e:
            logging.error(f"❌ Erro ao atualizar métrica {self.name}: {e}")

class PrometheusExporter:
    """Exportador de métricas para Prometheus"""
    
    def __init__(self):
        self.config = load_production_config()
        self.performance_monitor = get_performance_monitor()
        self.alert_manager = get_alert_manager()
        self.ml_analytics = get_ml_analytics()
        self.logger = logging.getLogger("prometheus.exporter")
        
        # Registry customizado para métricas
        self.registry = CollectorRegistry()
        
        # Métricas do sistema
        self.metrics: Dict[str, PrometheusMetric] = {}
        
        # Configurações
        self.export_interval = 15  # segundos
        self.metrics_retention_hours = 168  # 1 semana
        
        # Inicializa métricas
        self._initialize_metrics()
        
        # Inicia exportação automática
        self._start_auto_export()
    
    def _initialize_metrics(self):
        """Inicializa métricas do Prometheus"""
        try:
            # Métricas de performance das APIs
            api_success_rate = Gauge(
                'rapidapi_api_success_rate',
                'Taxa de sucesso por API',
                ['api_name', 'environment'],
                registry=self.registry
            )
            self.metrics['api_success_rate'] = PrometheusMetric(
                name='api_success_rate',
                description='Taxa de sucesso por API',
                labels=['api_name', 'environment'],
                metric_type='gauge',
                metric_object=api_success_rate
            )
            
            api_response_time = Histogram(
                'rapidapi_api_response_time_seconds',
                'Tempo de resposta por API',
                ['api_name', 'environment'],
                registry=self.registry
            )
            self.metrics['api_response_time'] = PrometheusMetric(
                name='api_response_time',
                description='Tempo de resposta por API',
                labels=['api_name', 'environment'],
                metric_type='histogram',
                metric_object=api_response_time
            )
            
            api_requests_total = Counter(
                'rapidapi_api_requests_total',
                'Total de requisições por API',
                ['api_name', 'status', 'environment'],
                registry=self.registry
            )
            self.metrics['api_requests_total'] = PrometheusMetric(
                name='api_requests_total',
                description='Total de requisições por API',
                labels=['api_name', 'status', 'environment'],
                metric_type='counter',
                metric_object=api_requests_total
            )
            
            # Métricas do sistema
            system_uptime = Gauge(
                'rapidapi_system_uptime_seconds',
                'Tempo de funcionamento do sistema',
                ['environment'],
                registry=self.registry
            )
            self.metrics['system_uptime'] = PrometheusMetric(
                name='system_uptime',
                description='Tempo de funcionamento do sistema',
                labels=['environment'],
                metric_type='gauge',
                metric_object=system_uptime
            )
            
            system_memory_usage = Gauge(
                'rapidapi_system_memory_bytes',
                'Uso de memória do sistema',
                ['environment'],
                registry=self.registry
            )
            self.metrics['system_memory_usage'] = PrometheusMetric(
                name='system_memory_usage',
                description='Uso de memória do sistema',
                labels=['environment'],
                metric_type='gauge',
                metric_object=system_memory_usage
            )
            
            system_cpu_usage = Gauge(
                'rapidapi_system_cpu_percent',
                'Uso de CPU do sistema',
                ['environment'],
                registry=self.registry
            )
            self.metrics['system_cpu_usage'] = PrometheusMetric(
                name='system_cpu_usage',
                description='Uso de CPU do sistema',
                labels=['environment'],
                metric_type='gauge',
                metric_object=system_cpu_usage
            )
            
            # Métricas de alertas
            alerts_active = Gauge(
                'rapidapi_alerts_active',
                'Alertas ativos por severidade',
                ['severity', 'environment'],
                registry=self.registry
            )
            self.metrics['alerts_active'] = PrometheusMetric(
                name='alerts_active',
                description='Alertas ativos por severidade',
                labels=['severity', 'environment'],
                metric_type='gauge',
                metric_object=alerts_active
            )
            
            # Métricas de ML
            ml_model_accuracy = Gauge(
                'rapidapi_ml_model_accuracy',
                'Precisão dos modelos de ML',
                ['model_name', 'environment'],
                registry=self.registry
            )
            self.metrics['ml_model_accuracy'] = PrometheusMetric(
                name='ml_model_accuracy',
                description='Precisão dos modelos de ML',
                labels=['model_name', 'environment'],
                metric_type='gauge',
                metric_object=ml_model_accuracy
            )
            
            ml_anomalies_detected = Counter(
                'rapidapi_ml_anomalies_total',
                'Total de anomalias detectadas',
                ['api_name', 'severity', 'environment'],
                registry=self.registry
            )
            self.metrics['ml_anomalies_detected'] = PrometheusMetric(
                name='ml_anomalies_detected',
                description='Total de anomalias detectadas',
                labels=['api_name', 'severity', 'environment'],
                metric_type='counter',
                metric_object=ml_anomalies_detected
            )
            
            # Métricas de notificações
            notifications_sent = Counter(
                'rapidapi_notifications_sent_total',
                'Total de notificações enviadas',
                ['channel', 'status', 'environment'],
                registry=self.registry
            )
            self.metrics['notifications_sent'] = PrometheusMetric(
                name='notifications_sent',
                description='Total de notificações enviadas',
                labels=['channel', 'status', 'environment'],
                metric_type='counter',
                metric_object=notifications_sent
            )
            
            self.logger.info(f"✅ {len(self.metrics)} métricas Prometheus inicializadas")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar métricas: {e}")
    
    def _start_auto_export(self):
        """Inicia exportação automática de métricas"""
        try:
            # Não inicia automaticamente - será iniciado quando necessário
            self.logger.info("🔄 Exportação automática de métricas configurada")
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar exportação automática: {e}")
    
    async def start_auto_export(self):
        """Inicia exportação automática quando chamado explicitamente"""
        try:
            asyncio.create_task(self._export_loop())
            self.logger.info("🔄 Exportação automática de métricas iniciada")
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar exportação automática: {e}")
    
    async def _export_loop(self):
        """Loop de exportação de métricas"""
        while True:
            try:
                await self._export_current_metrics()
                await asyncio.sleep(self.export_interval)
            except Exception as e:
                self.logger.error(f"❌ Erro na exportação de métricas: {e}")
                await asyncio.sleep(30)
    
    async def _export_current_metrics(self):
        """Exporta métricas atuais"""
        try:
            # Obtém dados de performance
            performance_data = self.performance_monitor.get_performance_summary()
            
            # Atualiza métricas das APIs
            for api_name, api_data in performance_data.get("apis", {}).items():
                # Taxa de sucesso
                self.metrics['api_success_rate'].update(
                    api_data.get("success_rate", 0),
                    {"api_name": api_name, "environment": self.config.environment}
                )
                
                # Tempo de resposta
                response_time = api_data.get("average_response_time", 0)
                if response_time > 0:
                    self.metrics['api_response_time'].update(
                        response_time,
                        {"api_name": api_name, "environment": self.config.environment}
                    )
                
                # Total de requisições
                total_requests = api_data.get("total_requests", 0)
                success_requests = int(total_requests * api_data.get("success_rate", 0) / 100)
                error_requests = total_requests - success_requests
                
                self.metrics['api_requests_total'].update(
                    success_requests,
                    {"api_name": api_name, "status": "success", "environment": self.config.environment}
                )
                
                self.metrics['api_requests_total'].update(
                    error_requests,
                    {"api_name": api_name, "status": "error", "environment": self.config.environment}
                )
            
            # Atualiza métricas do sistema
            import psutil
            try:
                # Uptime
                uptime = time.time()
                self.metrics['system_uptime'].update(
                    uptime,
                    {"environment": self.config.environment}
                )
                
                # Memória
                memory = psutil.virtual_memory()
                self.metrics['system_memory_usage'].update(
                    memory.used,
                    {"environment": self.config.environment}
                )
                
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics['system_cpu_usage'].update(
                    cpu_percent,
                    {"environment": self.config.environment}
                )
                
            except ImportError:
                pass
            
            # Atualiza métricas de alertas
            alert_stats = self.alert_manager.get_alert_stats()
            for severity, count in alert_stats.get("severity_distribution", {}).items():
                self.metrics['alerts_active'].update(
                    count,
                    {"severity": severity, "environment": self.config.environment}
                )
            
            # Atualiza métricas de ML
            for model_name, model in self.ml_analytics.models.items():
                if model.last_trained:
                    self.metrics['ml_model_accuracy'].update(
                        model.accuracy,
                        {"model_name": model_name, "environment": self.config.environment}
                    )
            
            # Detecta anomalias e atualiza métricas
            anomalies = self.ml_analytics.detect_anomalies()
            for anomaly in anomalies:
                if anomaly.is_anomaly:
                    self.metrics['ml_anomalies_detected'].update(
                        1,
                        {"api_name": anomaly.api_name, "severity": anomaly.severity, "environment": self.config.environment}
                    )
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao exportar métricas: {e}")
    
    def get_metrics_text(self) -> str:
        """Retorna métricas em formato texto para Prometheus"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar métricas: {e}")
            return ""
    
    def get_metrics_json(self) -> Dict[str, Any]:
        """Retorna métricas em formato JSON"""
        try:
            metrics_data = {}
            
            for metric_name, metric in self.metrics.items():
                metrics_data[metric_name] = {
                    "description": metric.description,
                    "labels": metric.labels,
                    "type": metric.metric_type,
                    "last_update": metric.last_update.isoformat()
                }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_metrics": len(metrics_data),
                "metrics": metrics_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar JSON de métricas: {e}")
            return {"error": str(e)}

class PrometheusServer:
    """Servidor HTTP para métricas Prometheus"""
    
    def __init__(self, exporter: PrometheusExporter):
        self.exporter = exporter
        self.app = web.Application()
        self.logger = logging.getLogger("prometheus.server")
        
        # Configura rotas
        self._setup_routes()
        
        # Configurações
        self.host = "0.0.0.0"
        self.port = 9090
    
    def _setup_routes(self):
        """Configura rotas do servidor"""
        # Métricas no formato Prometheus
        self.app.router.add_get("/metrics", self._metrics_handler)
        
        # Métricas em JSON
        self.app.router.add_get("/metrics/json", self._metrics_json_handler)
        
        # Health check
        self.app.router.add_get("/health", self._health_handler)
        
        # Status do sistema
        self.app.router.add_get("/status", self._status_handler)
    
    async def _metrics_handler(self, request):
        """Handler para métricas Prometheus"""
        try:
            metrics_text = self.exporter.get_metrics_text()
            
            return web.Response(
                text=metrics_text,
                content_type=CONTENT_TYPE_LATEST,
                headers={
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Erro no handler de métricas: {e}")
            return web.Response(
                text=f"Error: {str(e)}",
                status=500
            )
    
    async def _metrics_json_handler(self, request):
        """Handler para métricas em JSON"""
        try:
            metrics_json = self.exporter.get_metrics_json()
            
            return web.json_response(
                metrics_json,
                headers={
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Erro no handler JSON: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def _health_handler(self, request):
        """Handler para health check"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(self.exporter.metrics),
            "last_export": datetime.now().isoformat()
        }
        
        return web.json_response(health_data)
    
    async def _status_handler(self, request):
        """Handler para status do sistema"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "exporter_status": "running",
                "metrics_configured": len(self.exporter.metrics),
                "export_interval": self.exporter.export_interval,
                "environment": self.exporter.config.environment
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            self.logger.error(f"❌ Erro no handler de status: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def start(self):
        """Inicia o servidor Prometheus"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"🚀 Servidor Prometheus iniciado em http://{self.host}:{self.port}")
        self.logger.info(f"📊 Métricas disponíveis em /metrics")
        self.logger.info(f"📋 Status disponível em /status")
        
        return runner
    
    async def stop(self, runner):
        """Para o servidor"""
        await runner.cleanup()
        self.logger.info("🛑 Servidor Prometheus parado")

class GrafanaIntegration:
    """Integração com Grafana"""
    
    def __init__(self):
        self.config = load_production_config()
        self.logger = logging.getLogger("grafana.integration")
        
        # Configurações do Grafana
        self.grafana_url = getattr(self.config, 'grafana_url', 'http://localhost:3000')
        self.grafana_api_key = getattr(self.config, 'grafana_api_key', None)
        self.grafana_org_id = getattr(self.config, 'grafana_org_id', 1)
        
        # Dashboard templates
        self.dashboard_templates = self._load_dashboard_templates()
    
    def _load_dashboard_templates(self) -> Dict[str, Any]:
        """Carrega templates de dashboards"""
        return {
            "rapidapi_overview": {
                "title": "RapidAPI - Visão Geral",
                "panels": [
                    {
                        "title": "Taxa de Sucesso das APIs",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rapidapi_api_success_rate",
                                "legendFormat": "{{api_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Tempo de Resposta das APIs",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rapidapi_api_response_time_seconds_sum[5m]) / rate(rapidapi_api_response_time_seconds_count[5m])",
                                "legendFormat": "{{api_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Requisições por Minuto",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rapidapi_api_requests_total[5m])",
                                "legendFormat": "{{api_name}} - {{status}}"
                            }
                        ]
                    }
                ]
            },
            "rapidapi_alerts": {
                "title": "RapidAPI - Alertas e ML",
                "panels": [
                    {
                        "title": "Alertas Ativos por Severidade",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "rapidapi_alerts_active",
                                "legendFormat": "{{severity}}"
                            }
                        ]
                    },
                    {
                        "title": "Anomalias Detectadas",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(rapidapi_ml_anomalies_total[5m])",
                                "legendFormat": "{{api_name}} - {{severity}}"
                            }
                        ]
                    },
                    {
                        "title": "Precisão dos Modelos ML",
                        "type": "gauge",
                        "targets": [
                            {
                                "expr": "rapidapi_ml_model_accuracy",
                                "legendFormat": "{{model_name}}"
                            }
                        ]
                    }
                ]
            }
        }
    
    async def create_dashboard(self, dashboard_name: str) -> Dict[str, Any]:
        """Cria dashboard no Grafana"""
        if not self.grafana_api_key:
            return {"error": "API key do Grafana não configurada"}
        
        try:
            template = self.dashboard_templates.get(dashboard_name)
            if not template:
                return {"error": f"Template {dashboard_name} não encontrado"}
            
            # Prepara dados do dashboard
            dashboard_data = {
                "dashboard": {
                    "title": template["title"],
                    "panels": template["panels"],
                    "time": {
                        "from": "now-1h",
                        "to": "now"
                    },
                    "refresh": "30s"
                },
                "folderId": 0,
                "overwrite": True
            }
            
            # Cria dashboard via API
            headers = {
                "Authorization": f"Bearer {self.grafana_api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.grafana_url}/api/dashboards/db"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=dashboard_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"✅ Dashboard {dashboard_name} criado com sucesso")
                        return result
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Erro ao criar dashboard: {error_text}")
                        return {"error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar dashboard: {e}")
            return {"error": str(e)}
    
    async def create_all_dashboards(self) -> Dict[str, Any]:
        """Cria todos os dashboards disponíveis"""
        results = {}
        
        for dashboard_name in self.dashboard_templates.keys():
            self.logger.info(f"🔄 Criando dashboard: {dashboard_name}")
            result = await self.create_dashboard(dashboard_name)
            results[dashboard_name] = result
        
        return results

# Instâncias globais
prometheus_exporter = PrometheusExporter()
prometheus_server = PrometheusServer(prometheus_exporter)
grafana_integration = GrafanaIntegration()

def get_prometheus_exporter() -> PrometheusExporter:
    """Retorna o exportador Prometheus"""
    return prometheus_exporter

def get_prometheus_server() -> PrometheusServer:
    """Retorna o servidor Prometheus"""
    return prometheus_server

def get_grafana_integration() -> GrafanaIntegration:
    """Retorna a integração Grafana"""
    return grafana_integration

# Funções de conveniência
async def start_prometheus_server():
    """Inicia o servidor Prometheus"""
    server = get_prometheus_server()
    return await server.start()

async def create_grafana_dashboards():
    """Cria dashboards no Grafana"""
    grafana = get_grafana_integration()
    return await grafana.create_all_dashboards()

def get_prometheus_metrics():
    """Retorna métricas em formato Prometheus"""
    exporter = get_prometheus_exporter()
    return exporter.get_metrics_text()

if __name__ == "__main__":
    # Demonstração da integração Prometheus/Grafana
    async def demo_prometheus_integration():
        """Demonstra a integração Prometheus/Grafana"""
        print("📊 Demonstração da Integração Prometheus/Grafana")
        print("=" * 60)
        
        # Mostra métricas configuradas
        exporter = get_prometheus_exporter()
        print(f"📈 Métricas configuradas: {len(exporter.metrics)}")
        
        for name, metric in exporter.metrics.items():
            print(f"  • {name}: {metric.description}")
        
        # Inicia servidor Prometheus
        print(f"\n🚀 Iniciando servidor Prometheus...")
        server = get_prometheus_server()
        runner = await server.start()
        
        # Simula algumas métricas
        print(f"\n📊 Simulando métricas...")
        await asyncio.sleep(5)
        
        # Mostra métricas em formato Prometheus
        metrics_text = exporter.get_metrics_text()
        print(f"\n📋 Métricas Prometheus (primeiras 5 linhas):")
        for line in metrics_text.decode().split('\n')[:5]:
            if line.strip():
                print(f"  {line}")
        
        # Mostra métricas em JSON
        metrics_json = exporter.get_metrics_json()
        print(f"\n📋 Resumo das métricas:")
        print(f"  • Total: {metrics_json.get('total_metrics', 0)}")
        print(f"  • Timestamp: {metrics_json.get('timestamp', 'N/A')}")
        
        # Cria dashboards Grafana (se configurado)
        print(f"\n🎨 Criando dashboards Grafana...")
        grafana = get_grafana_integration()
        if grafana.grafana_api_key:
            dashboards_result = await grafana.create_all_dashboards()
            print(f"  • Dashboards criados: {len(dashboards_result)}")
        else:
            print(f"  ⚠️  API key do Grafana não configurada")
        
        print(f"\n✅ Demonstração concluída!")
        print(f"🌐 Servidor Prometheus rodando em http://localhost:9090")
        print(f"📊 Métricas disponíveis em /metrics")
        
        # Mantém servidor rodando
        try:
            while True:
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print(f"\n🛑 Parando servidor...")
            await server.stop(runner)
    
    asyncio.run(demo_prometheus_integration())
