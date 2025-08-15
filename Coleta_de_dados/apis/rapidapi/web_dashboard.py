#!/usr/bin/env python3
"""
Dashboard Web para Monitoramento das APIs RapidAPI

Este módulo implementa uma interface web para:
- Monitoramento em tempo real
- Visualização de métricas
- Gerenciamento de alertas
- Configuração de notificações
- Histórico de performance
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from aiohttp import web
import aiohttp_cors
import os

# Importa módulos do sistema
from .performance_monitor import get_performance_monitor
from .fallback_manager import get_fallback_manager
from .notification_system import get_notification_manager, NotificationMessage

@dataclass
class DashboardConfig:
    """Configuração do dashboard web"""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    refresh_interval: int = 30  # Segundos
    max_history_hours: int = 24

class RapidAPIDashboard:
    """Dashboard web para monitoramento das APIs RapidAPI"""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.logger = logging.getLogger("dashboard.web")
        self.app = web.Application()
        self.performance_monitor = get_performance_monitor()
        self.fallback_manager = get_fallback_manager()
        self.notification_manager = get_notification_manager()
        
        # Configura rotas
        self._setup_routes()
        self._setup_cors()
        self._setup_middleware()
        
        # Dados em cache para o dashboard
        self.cache: Dict[str, Any] = {
            "last_update": None,
            "performance_data": None,
            "fallback_data": None,
            "notification_data": None
        }
    
    def _setup_routes(self):
        """Configura rotas da API"""
        # Rotas principais
        self.app.router.add_get("/", self._index_handler)
        self.app.router.add_get("/api/status", self._api_status_handler)
        self.app.router.add_get("/api/performance", self._api_performance_handler)
        self.app.router.add_get("/api/fallback", self._api_fallback_handler)
        self.app.router.add_get("/api/notifications", self._api_notifications_handler)
        self.app.router.add_get("/api/alerts", self._api_alerts_handler)
        
        # Rotas de ação
        self.app.router.add_post("/api/notifications/send", self._api_send_notification_handler)
        self.app.router.add_post("/api/performance/clear", self._api_clear_performance_handler)
        self.app.router.add_post("/api/fallback/reset", self._api_reset_fallback_handler)
        
                            # Rotas estáticas (comentadas para evitar erros de diretório)
                    # self.app.router.add_static("/static", "static", append_version=True)
                    # self.app.router.add_static("/js", "js", append_version=True)
                    # self.app.router.add_static("/css", "css", append_version=True)
    
    def _setup_cors(self):
        """Configura CORS para permitir requisições do frontend"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Aplica CORS a todas as rotas
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    def _setup_middleware(self):
        """Configura middleware para logging e cache"""
        @web.middleware
        async def logging_middleware(request, handler):
            start_time = datetime.now()
            response = await handler(request)
            duration = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"{request.method} {request.path} - {response.status} - {duration:.3f}s")
            return response
        
        self.app.middlewares.append(logging_middleware)
    
    async def _index_handler(self, request):
        """Handler para página principal"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type="text/html")
    
    async def _api_status_handler(self, request):
        """API para status geral do sistema"""
        try:
            # Coleta dados de todos os sistemas
            performance_summary = self.performance_monitor.get_performance_summary()
            fallback_status = self.fallback_manager.get_status_report()
            notification_stats = self.notification_manager.get_delivery_stats()
            
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "system_status": "healthy",
                "performance": performance_summary,
                "fallback": fallback_status,
                "notifications": notification_stats,
                "uptime": self._get_uptime()
            }
            
            # Atualiza cache
            self.cache["last_update"] = datetime.now()
            self.cache["performance_data"] = performance_summary
            self.cache["fallback_data"] = fallback_status
            self.cache["notification_data"] = notification_stats
            
            return web.json_response(status_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_performance_handler(self, request):
        """API para dados de performance"""
        try:
            # Parâmetros de query
            api_name = request.query.get("api")
            hours = int(request.query.get("hours", 24))
            
            if api_name:
                # Dados de uma API específica
                metrics = self.performance_monitor.get_api_metrics(api_name)
                if metrics:
                    data = {
                        "api_name": api_name,
                        "metrics": {
                            "total_requests": metrics.total_requests,
                            "success_rate": metrics.success_rate,
                            "average_response_time": metrics.average_response_time,
                            "requests_per_minute": metrics.requests_per_minute
                        }
                    }
                else:
                    data = {"error": f"API {api_name} não encontrada"}
            else:
                # Dados de todas as APIs
                all_metrics = self.performance_monitor.get_all_metrics()
                data = {
                    "apis": {},
                    "summary": self.performance_monitor.get_performance_summary()
                }
                
                for name, metrics in all_metrics.items():
                    data["apis"][name] = {
                        "success_rate": metrics.success_rate,
                        "average_response_time": metrics.average_response_time,
                        "requests_per_minute": metrics.requests_per_minute
                    }
            
            return web.json_response(data)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter performance: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_fallback_handler(self, request):
        """API para dados do sistema de fallback"""
        try:
            fallback_data = self.fallback_manager.get_status_report()
            return web.json_response(fallback_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados de fallback: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_notifications_handler(self, request):
        """API para dados de notificações"""
        try:
            # Parâmetros de query
            hours = int(request.query.get("hours", 24))
            
            notification_data = {
                "stats": self.notification_manager.get_delivery_stats(),
                "recent": [
                    {
                        "title": msg.title,
                        "severity": msg.severity,
                        "timestamp": msg.timestamp.isoformat(),
                        "metadata": msg.metadata
                    }
                    for msg in self.notification_manager.get_recent_notifications(hours)
                ]
            }
            
            return web.json_response(notification_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter notificações: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_alerts_handler(self, request):
        """API para alertas ativos"""
        try:
            # Parâmetros de query
            severity = request.query.get("severity")
            hours = int(request.query.get("hours", 24))
            
            alerts = self.performance_monitor.get_alerts(
                severity=severity,
                hours=hours
            )
            
            return web.json_response({"alerts": alerts})
            
        except Exception as e:
            self.logger.error(f"Erro ao obter alertas: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_send_notification_handler(self, request):
        """API para enviar notificação de teste"""
        try:
            data = await request.json()
            
            message = NotificationMessage(
                title=data.get("title", "Teste do Dashboard"),
                content=data.get("content", "Notificação enviada via dashboard web"),
                severity=data.get("severity", "info"),
                metadata=data.get("metadata", {}),
                recipients=data.get("recipients", [])
            )
            
            # Envia notificação
            results = await self.notification_manager.send_notification(message)
            
            return web.json_response({
                "success": True,
                "results": results,
                "message": "Notificação enviada com sucesso"
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_clear_performance_handler(self, request):
        """API para limpar dados de performance"""
        try:
            # Limpa o cache local do dashboard
            self.cache["performance_data"] = None
            self.cache["last_update"] = None
            
            return web.json_response({"success": True, "message": "Cache de performance limpo"})
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar performance: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def _api_reset_fallback_handler(self, request):
        """API para resetar sistema de fallback"""
        try:
            # Reinicia monitoramento de saúde
            await self.fallback_manager.stop_health_monitoring()
            await self.fallback_manager.start_health_monitoring()
            
            return web.json_response({"success": True, "message": "Sistema de fallback resetado"})
            
        except Exception as e:
            self.logger.error(f"Erro ao resetar fallback: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def _generate_dashboard_html(self) -> str:
        """Gera HTML do dashboard"""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard RapidAPI - Monitoramento</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-card {{ min-height: 120px; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; }}
        .status-healthy {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
        .refresh-indicator {{ position: fixed; top: 20px; right: 20px; z-index: 1000; }}
        .chart-container {{ height: 300px; }}
    </style>
</head>
<body>
    <div class="refresh-indicator">
        <div class="alert alert-info" id="refreshStatus">
            <i class="fas fa-sync-alt"></i> Atualizando...
        </div>
    </div>

    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> Dashboard RapidAPI
            </span>
            <span class="navbar-text" id="lastUpdate">
                Última atualização: --
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Status Geral -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-server fa-2x mb-2"></i>
                        <h5>Status do Sistema</h5>
                        <div class="metric-value" id="systemStatus">--</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-tachometer-alt fa-2x mb-2"></i>
                        <h5>Taxa de Sucesso</h5>
                        <div class="metric-value" id="successRate">--</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-2x mb-2"></i>
                        <h5>Tempo Médio</h5>
                        <div class="metric-value" id="avgResponseTime">--</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                        <h5>Alertas Ativos</h5>
                        <div class="metric-value" id="activeAlerts">--</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gráficos e Métricas -->
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
                        <h5><i class="fas fa-list"></i> APIs por Performance</h5>
                    </div>
                    <div class="card-body">
                        <div id="apiPerformanceList">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Sistema de Fallback -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-exchange-alt"></i> Status do Fallback</h5>
                    </div>
                    <div class="card-body">
                        <div id="fallbackStatus">
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
                        <h5><i class="fas fa-bell"></i> Notificações</h5>
                    </div>
                    <div class="card-body">
                        <div id="notificationStats">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alertas Recentes -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-exclamation-circle"></i> Alertas Recentes</h5>
                    </div>
                    <div class="card-body">
                        <div id="recentAlerts">
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Configuração do dashboard
        const REFRESH_INTERVAL = {self.config.refresh_interval * 1000};
        let performanceChart = null;
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            initializeDashboard();
            setInterval(updateDashboard, REFRESH_INTERVAL);
        }});
        
        async function initializeDashboard() {{
            await updateDashboard();
        }}
        
        async function updateDashboard() {{
            try {{
                showRefreshStatus(true);
                
                // Atualiza dados principais
                const statusData = await fetch('/api/status').then(r => r.json());
                updateMainMetrics(statusData);
                
                // Atualiza performance
                const performanceData = await fetch('/api/performance').then(r => r.json());
                updatePerformanceChart(performanceData);
                updateApiPerformanceList(performanceData);
                
                // Atualiza fallback
                const fallbackData = await fetch('/api/fallback').then(r => r.json());
                updateFallbackStatus(fallbackData);
                
                // Atualiza notificações
                const notificationData = await fetch('/api/notifications').then(r => r.json());
                updateNotificationStats(notificationData);
                
                // Atualiza alertas
                const alertsData = await fetch('/api/alerts').then(r => r.json());
                updateRecentAlerts(alertsData);
                
                // Atualiza timestamp
                document.getElementById('lastUpdate').textContent = 
                    'Última atualização: ' + new Date().toLocaleTimeString();
                
                showRefreshStatus(false);
                
            }} catch (error) {{
                console.error('Erro ao atualizar dashboard:', error);
                showRefreshStatus(false);
            }}
        }}
        
        function updateMainMetrics(data) {{
            // Status do sistema
            const systemStatus = document.getElementById('systemStatus');
            systemStatus.textContent = data.system_status === 'healthy' ? 'Saudável' : 'Problemas';
            systemStatus.className = 'metric-value ' + 
                (data.system_status === 'healthy' ? 'status-healthy' : 'status-error');
            
            // Taxa de sucesso
            document.getElementById('successRate').textContent = 
                data.performance.overall_success_rate.toFixed(1) + '%';
            
            // Tempo médio de resposta
            document.getElementById('avgResponseTime').textContent = 
                data.performance.apis_by_performance[0]?.average_response_time.toFixed(3) + 's' || '--';
            
            // Alertas ativos
            document.getElementById('activeAlerts').textContent = data.performance.recent_alerts || 0;
        }}
        
        function updatePerformanceChart(data) {{
            const ctx = document.getElementById('performanceChart').getContext('2d');
            
            if (performanceChart) {{
                performanceChart.destroy();
            }}
            
            const labels = Object.keys(data.apis || {{}});
            const successRates = labels.map(api => data.apis[api].success_rate);
            const responseTimes = labels.map(api => data.apis[api].average_response_time);
            
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
        
        function updateApiPerformanceList(data) {{
            const container = document.getElementById('apiPerformanceList');
            
            if (!data.apis) {{
                container.innerHTML = '<div class="text-center text-muted">Nenhum dado disponível</div>';
                return;
            }}
            
            const apiList = Object.entries(data.apis)
                .sort(([,a], [,b]) => b.success_rate - a.success_rate)
                .map(([name, metrics]) => {{
                    const statusClass = metrics.success_rate >= 80 ? 'text-success' : 
                                      metrics.success_rate >= 60 ? 'text-warning' : 'text-danger';
                    
                    return `
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-bold">${{name}}</span>
                            <span class="${{statusClass}}">${{metrics.success_rate.toFixed(1)}}%</span>
                        </div>
                        <div class="progress mb-3" style="height: 8px;">
                            <div class="progress-bar ${{statusClass.replace('text-', 'bg-')}}" 
                                 style="width: ${{metrics.success_rate}}%"></div>
                        </div>
                    `;
                }}).join('');
            
            container.innerHTML = apiList;
        }}
        
        function updateFallbackStatus(data) {{
            const container = document.getElementById('fallbackStatus');
            
            const stats = data.fallback_stats;
            const html = `
                <div class="row text-center">
                    <div class="col-4">
                        <div class="h4 text-success">${{stats.apis_active}}</div>
                        <small class="text-muted">APIs Ativas</small>
                    </div>
                    <div class="col-4">
                        <div class="h4 text-warning">${{stats.apis_failing}}</div>
                        <small class="text-muted">APIs Falhando</small>
                    </div>
                    <div class="col-4">
                        <div class="h4 text-danger">${{stats.apis_rate_limited}}</div>
                        <small class="text-muted">Rate Limited</small>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        }}
        
        function updateNotificationStats(data) {{
            const container = document.getElementById('notificationStats');
            
            const stats = data.stats;
            const html = `
                <div class="row text-center">
                    <div class="col-6">
                        <div class="h4 text-primary">${{stats.total}}</div>
                        <small class="text-muted">Total Enviadas</small>
                    </div>
                    <div class="col-6">
                        <div class="h4 text-success">${{stats.success_rate.toFixed(1)}}%</div>
                        <small class="text-muted">Taxa de Sucesso</small>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        }}
        
        function updateRecentAlerts(data) {{
            const container = document.getElementById('recentAlerts');
            
            if (!data.alerts || data.alerts.length === 0) {{
                container.innerHTML = '<div class="text-center text-muted">Nenhum alerta recente</div>';
                return;
            }}
            
            const alertsHtml = data.alerts.slice(0, 10).map(alert => {{
                const severityClass = alert.severity === 'critical' ? 'danger' : 
                                    alert.severity === 'error' ? 'warning' : 'info';
                
                return `
                    <div class="alert alert-${{severityClass}} alert-dismissible fade show">
                        <strong>${{alert.api_name}}:</strong> ${{alert.message}}
                        <small class="text-muted float-end">
                            ${{new Date(alert.timestamp * 1000).toLocaleString()}}
                        </small>
                    </div>
                `;
            }}).join('');
            
            container.innerHTML = alertsHtml;
        }}
        
        function showRefreshStatus(show) {{
            const indicator = document.getElementById('refreshStatus');
            if (show) {{
                indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Atualizando...';
                indicator.style.display = 'block';
            }} else {{
                indicator.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>
        """
    
    def _get_uptime(self) -> str:
        """Retorna tempo de funcionamento do sistema"""
        # Implementar lógica de uptime real
        return "00:00:00"
    
    async def start(self):
        """Inicia o servidor web"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.config.host, self.config.port)
        await site.start()
        
        self.logger.info(f"🚀 Dashboard iniciado em http://{self.config.host}:{self.config.port}")
        self.logger.info(f"📊 Monitoramento configurado para atualizar a cada {self.config.refresh_interval}s")
        
        return runner
    
    async def stop(self, runner):
        """Para o servidor web"""
        await runner.cleanup()
        self.logger.info("🛑 Dashboard parado")

# Função de conveniência para iniciar o dashboard
async def start_dashboard(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """Inicia o dashboard web"""
    config = DashboardConfig(host=host, port=port, debug=debug)
    dashboard = RapidAPIDashboard(config)
    
    runner = await dashboard.start()
    
    try:
        # Mantém o servidor rodando
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await dashboard.stop(runner)
        print("\\n🛑 Dashboard parado pelo usuário")

if __name__ == "__main__":
    asyncio.run(start_dashboard())
