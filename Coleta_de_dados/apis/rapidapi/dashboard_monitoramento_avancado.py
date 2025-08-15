#!/usr/bin/env python3
"""
Dashboard de Monitoramento Avançado para RapidAPI

Este módulo implementa:
- Dashboard em tempo real com WebSocket
- Métricas avançadas de performance
- Gráficos interativos
- Alertas visuais
- Histórico de métricas
- Exportação de dados
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiohttp
from aiohttp import web
import aiohttp_cors
# import aiohttp_sse
# from aiohttp_sse import sse_response
import psutil
import threading

# Importa módulos do sistema
from .performance_monitor import get_performance_monitor
from .fallback_manager import get_fallback_manager
from .notification_system import get_notification_manager
from .alert_system import get_alert_manager
from .cache_manager_avancado import get_advanced_cache_manager

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    process_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "disk_usage_percent": self.disk_usage_percent,
            "network_io": self.network_io,
            "process_count": self.process_count
        }

@dataclass
class APIMetrics:
    """Métricas das APIs"""
    api_name: str
    success_rate: float
    response_time: float
    requests_per_minute: float
    error_rate: float
    last_request: datetime
    status: str  # healthy, warning, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_name": self.api_name,
            "success_rate": self.success_rate,
            "response_time": self.response_time,
            "requests_per_minute": self.requests_per_minute,
            "error_rate": self.error_rate,
            "last_request": self.last_request.isoformat(),
            "status": self.status
        }

class AdvancedMonitoringDashboard:
    """Dashboard de monitoramento avançado"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.logger = logging.getLogger("dashboard.monitoring")
        
        # Módulos do sistema
        self.performance_monitor = get_performance_monitor()
        self.fallback_manager = get_fallback_manager()
        self.notification_manager = get_notification_manager()
        self.alert_manager = get_alert_manager()
        self.cache_manager = get_advanced_cache_manager()
        
        # Histórico de métricas
        self.metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Configura rotas
        self._setup_routes()
        self._setup_cors()
        self._setup_middleware()
        
        # Inicia coleta de métricas
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
    
    def _setup_routes(self):
        """Configura rotas da API"""
        # Rotas principais
        self.app.router.add_get("/", self._index_handler)
        self.app.router.add_get("/api/metrics", self._api_metrics_handler)
        self.app.router.add_get("/api/system", self._api_system_handler)
        self.app.router.add_get("/api/apis", self._api_apis_handler)
        self.app.router.add_get("/api/cache", self._api_cache_handler)
        self.app.router.add_get("/api/alerts", self._api_alerts_handler)
        self.app.router.add_get("/api/history", self._api_history_handler)
        
        # Rotas de streaming (comentadas por dependência)
        # self.app.router.add_get("/stream/metrics", self._stream_metrics_handler)
        # self.app.router.add_get("/stream/alerts", self._stream_alerts_handler)
        
        # Rotas de ação
        self.app.router.add_post("/api/clear-cache", self._api_clear_cache_handler)
        self.app.router.add_post("/api/trigger-alert", self._api_trigger_alert_handler)
        self.app.router.add_post("/api/export-data", self._api_export_data_handler)
    
    def _setup_cors(self):
        """Configura CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_middleware(self):
        """Configura middleware"""
        @web.middleware
        async def logging_middleware(request, handler):
            start_time = time.time()
            response = await handler(request)
            duration = time.time() - start_time
            
            self.logger.info(f"{request.method} {request.path} - {response.status} - {duration:.3f}s")
            return response
        
        self.app.middlewares.append(logging_middleware)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                process_count=len(psutil.pids())
            )
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                disk_usage_percent=0.0,
                network_io={},
                process_count=0
            )
    
    def _collect_api_metrics(self) -> List[APIMetrics]:
        """Coleta métricas das APIs"""
        try:
            all_metrics = self.performance_monitor.get_all_metrics()
            api_metrics = []
            
            for api_name, metrics in all_metrics.items():
                # Determina status baseado em thresholds
                if metrics.success_rate >= 80:
                    status = "healthy"
                elif metrics.success_rate >= 60:
                    status = "warning"
                else:
                    status = "critical"
                
                api_metrics.append(APIMetrics(
                    api_name=api_name,
                    success_rate=metrics.success_rate,
                    response_time=metrics.average_response_time,
                    requests_per_minute=metrics.requests_per_minute,
                    error_rate=100 - metrics.success_rate,
                    last_request=datetime.now(),  # TODO: Implementar timestamp real
                    status=status
                ))
            
            return api_metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas das APIs: {e}")
            return []
    
    async def _collect_all_metrics(self):
        """Coleta todas as métricas"""
        try:
            # Métricas do sistema
            system_metrics = self._collect_system_metrics()
            
            # Métricas das APIs
            api_metrics = self._collect_api_metrics()
            
            # Métricas do cache
            cache_stats = self.cache_manager.get_stats()
            
            # Status do fallback
            fallback_status = self.fallback_manager.get_status_report()
            
            # Alertas ativos
            active_alerts = self.alert_manager.get_active_alerts()
            
            # Compila métricas completas
            complete_metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": system_metrics.to_dict(),
                "apis": [api.to_dict() for api in api_metrics],
                "cache": cache_stats,
                "fallback": fallback_status,
                "alerts": {
                    "active_count": len(active_alerts),
                    "alerts": [alert.to_dict() for alert in active_alerts]
                }
            }
            
            # Adiciona ao histórico
            self.metrics_history.append(complete_metrics)
            
            # Mantém tamanho do histórico
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)
            
            return complete_metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
            return {}
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(5)  # Coleta a cada 5 segundos
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(10)
    
    async def _index_handler(self, request):
        """Handler para página principal"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type="text/html")
    
    async def _api_metrics_handler(self, request):
        """API para métricas em tempo real"""
        try:
            metrics = await self._collect_all_metrics()
            return web.json_response(metrics)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_system_handler(self, request):
        """API para métricas do sistema"""
        try:
            system_metrics = self._collect_system_metrics()
            return web.json_response(system_metrics.to_dict())
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas do sistema: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_apis_handler(self, request):
        """API para métricas das APIs"""
        try:
            api_metrics = self._collect_api_metrics()
            return web.json_response([api.to_dict() for api in api_metrics])
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas das APIs: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_cache_handler(self, request):
        """API para métricas do cache"""
        try:
            cache_stats = self.cache_manager.get_stats()
            return web.json_response(cache_stats)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas do cache: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_alerts_handler(self, request):
        """API para alertas ativos"""
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            return web.json_response({
                "alerts": [alert.to_dict() for alert in active_alerts],
                "count": len(active_alerts)
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao obter alertas: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_history_handler(self, request):
        """API para histórico de métricas"""
        try:
            hours = int(request.query.get("hours", 24))
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_history = [
                metrics for metrics in self.metrics_history
                if datetime.fromisoformat(metrics["timestamp"]) > cutoff_time
            ]
            
            return web.json_response({
                "history": filtered_history,
                "total_points": len(filtered_history),
                "time_range_hours": hours
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _stream_metrics_handler(self, request):
        """Stream de métricas em tempo real"""
        async def event_generator():
            while self.running:
                try:
                    metrics = await self._collect_all_metrics()
                    yield f"data: {json.dumps(metrics)}\n\n"
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    self.logger.error(f"Erro no stream de métricas: {e}")
                    await asyncio.sleep(10)
        
        return sse_response(request, event_generator())
    
    async def _stream_alerts_handler(self, request):
        """Stream de alertas em tempo real"""
        async def event_generator():
            last_alert_count = 0
            
            while self.running:
                try:
                    active_alerts = self.alert_manager.get_active_alerts()
                    current_count = len(active_alerts)
                    
                    if current_count != last_alert_count:
                        yield f"data: {json.dumps({'alert_count': current_count})}\n\n"
                        last_alert_count = current_count
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erro no stream de alertas: {e}")
                    await asyncio.sleep(5)
        
        return sse_response(request, event_generator())
    
    async def _api_clear_cache_handler(self, request):
        """API para limpar cache"""
        try:
            self.cache_manager.clear()
            return web.json_response({"success": True, "message": "Cache limpo com sucesso"})
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_trigger_alert_handler(self, request):
        """API para disparar alerta manual"""
        try:
            data = await request.json()
            
            alert = await self.alert_manager.trigger_manual_alert(
                name=data.get("name", "Alerta Manual"),
                message=data.get("message", "Alerta disparado via dashboard"),
                severity=data.get("severity", "warning")
            )
            
            return web.json_response({
                "success": True,
                "alert": alert.to_dict(),
                "message": "Alerta disparado com sucesso"
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao disparar alerta: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_export_data_handler(self, request):
        """API para exportar dados"""
        try:
            data = await request.json()
            export_type = data.get("type", "json")
            hours = data.get("hours", 24)
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_history = [
                metrics for metrics in self.metrics_history
                if datetime.fromisoformat(metrics["timestamp"]) > cutoff_time
            ]
            
            if export_type == "json":
                return web.json_response({
                    "export_type": "json",
                    "data": filtered_history,
                    "exported_at": datetime.now().isoformat(),
                    "time_range_hours": hours
                })
            else:
                return web.json_response({"error": "Tipo de exportação não suportado"}, status=400)
                
        except Exception as e:
            self.logger.error(f"Erro ao exportar dados: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def _generate_dashboard_html(self) -> str:
        """Gera HTML do dashboard"""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Monitoramento Avançado - RapidAPI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {{ min-height: 120px; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; }}
        .status-healthy {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .chart-container {{ height: 300px; }}
        .real-time-indicator {{ 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            z-index: 1000; 
            background: #17a2b8;
            color: white;
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="real-time-indicator" id="realTimeIndicator">
        <i class="fas fa-circle"></i> Tempo Real
    </div>

    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> Dashboard de Monitoramento Avançado
            </span>
            <span class="navbar-text" id="lastUpdate">
                Última atualização: --
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Métricas do Sistema -->
        <div class="row mb-4">
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-microchip fa-2x mb-2"></i>
                        <h6>CPU</h6>
                        <div class="metric-value" id="cpuPercent">--</div>
                        <small>%</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-memory fa-2x mb-2"></i>
                        <h6>Memória</h6>
                        <div class="metric-value" id="memoryPercent">--</div>
                        <small>%</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-hdd fa-2x mb-2"></i>
                        <h6>Disco</h6>
                        <div class="metric-value" id="diskPercent">--</div>
                        <small>%</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-network-wired fa-2x mb-2"></i>
                        <h6>Processos</h6>
                        <div class="metric-value" id="processCount">--</div>
                        <small>ativos</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <h6>Alertas</h6>
                        <div class="metric-value" id="alertCount">--</div>
                        <small>ativos</small>
                    </div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="card metric-card">
                    <div class="card-body text-center">
                        <i class="fas fa-database fa-2x mb-2"></i>
                        <h6>Cache</h6>
                        <div class="metric-value" id="cacheHitRate">--</div>
                        <small>% hit</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos de Performance -->
        <div class="row mb-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-area"></i> Performance das APIs</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="performanceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Status das APIs</h5>
                    </div>
                    <div class="card-body">
                        <div id="apiStatusList">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Métricas de Cache -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-database"></i> Métricas de Cache</h5>
                    </div>
                    <div class="card-body">
                        <div id="cacheMetrics">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-pie"></i> Distribuição por Prioridade</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="priorityChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alertas Ativos -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-exclamation-circle"></i> Alertas Ativos</h5>
                        <button class="btn btn-sm btn-warning" onclick="triggerTestAlert()">
                            <i class="fas fa-plus"></i> Teste
                        </button>
                    </div>
                    <div class="card-body">
                        <div id="activeAlerts">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Configuração
        const REFRESH_INTERVAL = 5000; // 5 segundos
        let performanceChart = null;
        let priorityChart = null;
        let eventSource = null;
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            initializeDashboard();
            startRealTimeUpdates();
        }});
        
        function initializeDashboard() {{
            updateDashboard();
            setInterval(updateDashboard, REFRESH_INTERVAL);
        }}
        
        function startRealTimeUpdates() {{
            // Conecta ao stream de métricas
            eventSource = new EventSource('/stream/metrics');
            eventSource.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                updateRealTimeMetrics(data);
            }};
            
            // Conecta ao stream de alertas
            const alertEventSource = new EventSource('/stream/alerts');
            alertEventSource.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                updateAlertCount(data.alert_count);
            }};
        }}
        
        async function updateDashboard() {{
            try {{
                const response = await fetch('/api/metrics');
                const data = await response.json();
                updateAllMetrics(data);
                
                // Atualiza timestamp
                document.getElementById('lastUpdate').textContent = 
                    'Última atualização: ' + new Date().toLocaleTimeString();
                    
            }} catch (error) {{
                console.error('Erro ao atualizar dashboard:', error);
            }}
        }}
        
        function updateRealTimeMetrics(data) {{
            // Atualiza métricas em tempo real
            if (data.system) {{
                updateSystemMetrics(data.system);
            }}
            if (data.apis) {{
                updateAPIMetrics(data.apis);
            }}
            if (data.cache) {{
                updateCacheMetrics(data.cache);
            }}
            if (data.alerts) {{
                updateAlertCount(data.alerts.active_count);
            }}
        }}
        
        function updateSystemMetrics(system) {{
            document.getElementById('cpuPercent').textContent = system.cpu_percent.toFixed(1);
            document.getElementById('memoryPercent').textContent = system.memory_percent.toFixed(1);
            document.getElementById('diskPercent').textContent = system.disk_usage_percent.toFixed(1);
            document.getElementById('processCount').textContent = system.process_count;
        }}
        
        function updateAPIMetrics(apis) {{
            updatePerformanceChart(apis);
            updateAPIStatusList(apis);
        }}
        
        function updateCacheMetrics(cache) {{
            document.getElementById('cacheHitRate').textContent = cache.performance.hit_rate.toFixed(1);
            updateCacheMetricsDisplay(cache);
            updatePriorityChart(cache.structure.priority_distribution);
        }}
        
        function updateAlertCount(count) {{
            document.getElementById('alertCount').textContent = count;
        }}
        
        function updatePerformanceChart(apis) {{
            const ctx = document.getElementById('performanceChart').getContext('2d');
            
            if (performanceChart) {{
                performanceChart.destroy();
            }}
            
            const labels = apis.map(api => api.api_name);
            const successRates = apis.map(api => api.success_rate);
            const responseTimes = apis.map(api => api.response_time);
            
            performanceChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Taxa de Sucesso (%)',
                            data: successRates,
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            yAxisID: 'y'
                        }},
                        {{
                            label: 'Tempo de Resposta (s)',
                            data: responseTimes,
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            min: 0,
                            max: 100
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            min: 0,
                            grid: {{
                                drawOnChartArea: false,
                            }},
                        }}
                    }}
                }}
            }});
        }}
        
        function updateAPIStatusList(apis) {{
            const container = document.getElementById('apiStatusList');
            
            const apiList = apis.map(api => {{
                const statusClass = api.status === 'healthy' ? 'text-success' : 
                                  api.status === 'warning' ? 'text-warning' : 'text-danger';
                
                return `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold">${{{{api.api_name}}}}</span>
                        <span class="${{{{statusClass}}}}">${{{{api.success_rate.toFixed(1)}}}}%</span>
                    </div>
                    <div class="progress mb-3" style="height: 8px;">
                                                <div class="progress-bar ${{{{statusClass.replace('text-', 'bg-')}}}}"
                             style="width: ${{{{api.success_rate}}}}%"></div>
                    </div>
                `;
            }}).join('');
            
            container.innerHTML = apiList;
        }}
        
        function updateCacheMetricsDisplay(cache) {{
            const container = document.getElementById('cacheMetrics');
            
            const html = `
                <div class="row text-center">
                    <div class="col-4">
                                            <div class="h4 text-primary">${{{{cache.cache_size}}}}</div>
                    <small class="text-muted">Entradas</small>
                </div>
                <div class="col-4">
                    <div class="h4 text-success">${{{{cache.performance.hit_rate.toFixed(1)}}}}%</div>
                    <small class="text-muted">Hit Rate</small>
                </div>
                <div class="col-4">
                    <div class="h4 text-info">${{{{cache.memory_usage_mb.toFixed(1)}}}} MB</small>
                    <small class="text-muted">Memória</small>
                </div>
            </div>
            <div class="mt-3">
                <small class="text-muted">
                    Comprimidas: ${{{{cache.compression_stats.compressed_entries}}}} |
                    Limpeza: ${{{{cache.maintenance.cleanup_count}}}}x
                </small>
                </div>
            `;
            
            container.innerHTML = html;
        }}
        
        function updatePriorityChart(priorityDistribution) {{
            const ctx = document.getElementById('priorityChart').getContext('2d');
            
            if (priorityChart) {{
                priorityChart.destroy();
            }}
            
            const labels = Object.keys(priorityDistribution).map(p => 'Prioridade ' + p);
            const data = Object.values(priorityDistribution);
            const colors = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'];
            
            priorityChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data,
                        backgroundColor: colors.slice(0, labels.length)
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false
                }}
            }});
        }}
        
        async function triggerTestAlert() {{
            try {{
                const response = await fetch('/api/trigger-alert', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        name: 'Teste do Dashboard',
                        message: 'Alerta de teste disparado via dashboard',
                        severity: 'warning'
                    }})
                }});
                
                const result = await response.json();
                if (result.success) {{
                    alert('Alerta de teste disparado com sucesso!');
                    updateDashboard();
                }}
                
            }} catch (error) {{
                console.error('Erro ao disparar alerta:', error);
                alert('Erro ao disparar alerta de teste');
            }}
        }}
        
        // Atualiza indicador de tempo real
        setInterval(() => {{
            const indicator = document.getElementById('realTimeIndicator');
            indicator.style.background = indicator.style.background === 'rgb(23, 162, 184)' ? '#28a745' : '#17a2b8';
        }}, 1000);
    </script>
</body>
</html>
        """
    
    async def start(self):
        """Inicia o dashboard"""
        try:
            # Inicia monitoramento
            self.running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Inicia servidor web
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            self.logger.info(f"🚀 Dashboard de Monitoramento iniciado em http://{self.host}:{self.port}")
            self.logger.info(f"📊 Coleta de métricas configurada para cada 5s")
            
            return runner
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar dashboard: {e}")
            raise
    
    async def stop(self):
        """Para o dashboard"""
        try:
            self.running = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("🛑 Dashboard de Monitoramento parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar dashboard: {e}")

# Função de conveniência
async def start_advanced_monitoring_dashboard(host: str = "0.0.0.0", port: int = 8081):
    """Inicia o dashboard de monitoramento avançado"""
    dashboard = AdvancedMonitoringDashboard(host=host, port=port)
    
    runner = await dashboard.start()
    
    try:
        # Mantém o servidor rodando
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await dashboard.stop()
        print("\\n🛑 Dashboard parado pelo usuário")

if __name__ == "__main__":
    asyncio.run(start_advanced_monitoring_dashboard())
