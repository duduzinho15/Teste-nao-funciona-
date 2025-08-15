#!/usr/bin/env python3
"""
Dashboard de Produção para RapidAPI

Este módulo implementa:
- Dashboard otimizado para produção
- Configurações de segurança
- Rate limiting
- Logs estruturados
- Métricas de produção
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import aiohttp
from aiohttp import web
import aiohttp_cors
from aiohttp_session import setup, get_session, Session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import hashlib
import hmac
import secrets

# Importa módulos do sistema
from .production_config import load_production_config
from .performance_monitor import get_performance_monitor
from .fallback_manager import get_fallback_manager
from .notification_system import get_notification_manager, NotificationMessage

@dataclass
class DashboardMetrics:
    """Métricas do dashboard"""
    uptime_seconds: int
    total_requests: int
    active_connections: int
    memory_usage_mb: float
    cpu_usage_percent: float
    api_health_score: float
    last_update: datetime

class RateLimiter:
    """Rate limiter para o dashboard"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        """Verifica se requisição é permitida"""
        now = time.time()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove requisições antigas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        # Verifica limite
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # Adiciona nova requisição
        self.requests[client_ip].append(now)
        return True
    
    def get_client_stats(self, client_ip: str) -> Dict[str, Any]:
        """Retorna estatísticas do cliente"""
        now = time.time()
        
        if client_ip not in self.requests:
            return {"requests": 0, "remaining": self.max_requests}
        
        # Remove requisições antigas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        current_requests = len(self.requests[client_ip])
        remaining = max(0, self.max_requests - current_requests)
        
        return {
            "requests": current_requests,
            "remaining": remaining,
            "reset_time": now + self.window_seconds
        }

class ProductionDashboard:
    """Dashboard otimizado para produção"""
    
    def __init__(self):
        self.config = load_production_config()
        self.app = web.Application()
        self.rate_limiter = RateLimiter(
            max_requests=self.config.dashboard.rate_limit,
            window_seconds=60
        )
        self.start_time = datetime.now()
        self.active_connections = 0
        
        # Configurações
        self._setup_middleware()
        self._setup_routes()
        self._setup_cors()
        self._setup_sessions()
        
        # Módulos do sistema
        self.performance_monitor = get_performance_monitor()
        self.fallback_manager = get_fallback_manager()
        self.notification_manager = get_notification_manager()
        
        # Logs
        self.logger = logging.getLogger("dashboard.production")
    
    def _setup_middleware(self):
        """Configura middleware de segurança"""
        
        @web.middleware
        async def security_middleware(request, handler):
            # Rate limiting
            client_ip = request.remote
            if not self.rate_limiter.is_allowed(client_ip):
                return web.json_response(
                    {"error": "Rate limit exceeded"}, 
                    status=429,
                    headers={"Retry-After": "60"}
                )
            
            # Headers de segurança
            response = await handler(request)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Log da requisição
            self._log_request(request, response)
            
            return response
        
        @web.middleware
        async def metrics_middleware(request, handler):
            # Conta conexões ativas
            self.active_connections += 1
            
            start_time = time.time()
            response = await handler(request)
            duration = time.time() - start_time
            
            # Atualiza métricas
            self._update_metrics(request, response, duration)
            
            self.active_connections -= 1
            return response
        
        self.app.middlewares.extend([
            security_middleware,
            metrics_middleware
        ])
    
    def _setup_routes(self):
        """Configura rotas da API"""
        # Rotas principais
        self.app.router.add_get("/", self._index_handler)
        self.app.router.add_get("/health", self._health_handler)
        self.app.router.add_get("/metrics", self._metrics_handler)
        
        # Rotas da API
        self.app.router.add_get("/api/status", self._api_status_handler)
        self.app.router.add_get("/api/performance", self._api_performance_handler)
        self.app.router.add_get("/api/fallback", self._api_fallback_handler)
        self.app.router.add_get("/api/notifications", self._api_notifications_handler)
        self.app.router.add_get("/api/alerts", self._api_alerts_handler)
        
        # Rotas de ação
        self.app.router.add_post("/api/notifications/send", self._api_send_notification_handler)
        self.app.router.add_post("/api/performance/clear", self._api_clear_performance_handler)
        self.app.router.add_post("/api/fallback/reset", self._api_reset_fallback_handler)
        
        # Rotas de administração
        self.app.router.add_get("/admin/config", self._admin_config_handler)
        self.app.router.add_post("/admin/restart", self._admin_restart_handler)
    
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
    
    def _setup_sessions(self):
        """Configura sessões seguras"""
        if self.config.dashboard.secret_key:
            secret_key = self.config.dashboard.secret_key.encode()
        else:
            secret_key = secrets.token_bytes(32)
        
        setup(self.app, EncryptedCookieStorage(secret_key))
    
    def _log_request(self, request, response):
        """Log estruturado da requisição"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "path": request.path,
            "status": response.status,
            "client_ip": request.remote,
            "user_agent": request.headers.get("User-Agent", ""),
            "duration_ms": getattr(response, 'duration_ms', 0)
        }
        
        self.logger.info("Request processed", extra=log_data)
    
    def _update_metrics(self, request, response, duration):
        """Atualiza métricas do dashboard"""
        response.duration_ms = int(duration * 1000)
    
    async def _index_handler(self, request):
        """Handler para página principal"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type="text/html")
    
    async def _health_handler(self, request):
        """Handler para health check"""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int((datetime.now() - self.start_time).total_seconds()),
            "version": "1.0.0"
        }
        
        return web.json_response(health_data)
    
    async def _metrics_handler(self, request):
        """Handler para métricas do sistema"""
        metrics = self._get_system_metrics()
        return web.json_response(metrics)
    
    async def _api_status_handler(self, request):
        """API para status geral do sistema"""
        try:
            # Coleta dados de todos os sistemas
            performance_summary = self.performance_monitor.get_performance_summary()
            fallback_status = self.fallback_manager.get_status_report()
            notification_stats = self.notification_manager.get_delivery_stats()
            
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "system_status": self._calculate_system_status(performance_summary),
                "performance": performance_summary,
                "fallback": fallback_status,
                "notifications": notification_stats,
                "uptime": self._get_uptime(),
                "active_connections": self.active_connections
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    def _calculate_system_status(self, performance_summary: Dict[str, Any]) -> str:
        """Calcula status geral do sistema"""
        overall_success_rate = performance_summary.get('overall_success_rate', 0)
        
        if overall_success_rate >= 95:
            return "excellent"
        elif overall_success_rate >= 80:
            return "healthy"
        elif overall_success_rate >= 60:
            return "warning"
        else:
            return "critical"
    
    def _get_uptime(self) -> str:
        """Retorna tempo de funcionamento"""
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do sistema"""
        import psutil
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            return {
                "memory_usage_mb": memory.used / 1024 / 1024,
                "memory_percent": memory.percent,
                "cpu_usage_percent": cpu,
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {"error": "psutil não disponível"}
    
    def _generate_dashboard_html(self) -> str:
        """Gera HTML do dashboard de produção"""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Produção - RapidAPI</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-card {{ min-height: 120px; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; }}
        .status-excellent {{ color: #28a745; }}
        .status-healthy {{ color: #17a2b8; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .refresh-indicator {{ position: fixed; top: 20px; right: 20px; z-index: 1000; }}
        .chart-container {{ height: 300px; }}
        .security-badge {{ position: fixed; bottom: 20px; right: 20px; }}
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
                <i class="fas fa-shield-alt"></i> Dashboard de Produção - RapidAPI
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
                        <h5>Uptime</h5>
                        <div class="metric-value" id="uptime">--</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card status-card">
                    <div class="card-body text-center">
                        <i class="fas fa-users fa-2x mb-2"></i>
                        <h5>Conexões Ativas</h5>
                        <div class="metric-value" id="activeConnections">--</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Métricas do Sistema -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> Performance das APIs</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="performanceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-server"></i> Recursos do Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div id="systemResources">
                            <div class="text-center text-muted">
                                <i class="fas fa-spinner fa-spin"></i> Carregando...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status de Segurança -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-shield-alt"></i> Status de Segurança</h5>
                    </div>
                    <div class="card-body">
                        <div id="securityStatus">
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
                        <h5><i class="fas fa-bell"></i> Alertas Ativos</h5>
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

    <!-- Badge de Segurança -->
    <div class="security-badge">
        <div class="badge bg-success fs-6">
            <i class="fas fa-lock"></i> Produção Seguro
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Configuração do dashboard
        const REFRESH_INTERVAL = 30000; // 30 segundos
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

                // Atualiza métricas do sistema
                const metricsData = await fetch('/metrics').then(r => r.json());
                updateSystemResources(metricsData);

                // Atualiza performance
                const performanceData = await fetch('/api/performance').then(r => r.json());
                updatePerformanceChart(performanceData);

                // Atualiza alertas
                const alertsData = await fetch('/api/alerts').then(r => r.json());
                updateActiveAlerts(alertsData);

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
            const statusClass = 'status-' + data.system_status;
            systemStatus.textContent = data.system_status.toUpperCase();
            systemStatus.className = 'metric-value ' + statusClass;

            // Taxa de sucesso
            document.getElementById('successRate').textContent =
                data.performance.overall_success_rate.toFixed(1) + '%';

            // Uptime
            document.getElementById('uptime').textContent = data.uptime;

            // Conexões ativas
            document.getElementById('activeConnections').textContent = data.active_connections;
        }}

        function updateSystemResources(data) {{
            const container = document.getElementById('systemResources');
            
            if (data.error) {{
                container.innerHTML = '<div class="text-center text-muted">Métricas não disponíveis</div>';
                return;
            }}

            const html = `
                <div class="row text-center">
                    <div class="col-6">
                        <div class="h4 text-primary">${{data.memory_usage_mb.toFixed(1)}} MB</div>
                        <small class="text-muted">Memória</small>
                    </div>
                    <div class="col-6">
                        <div class="h4 text-warning">${{data.cpu_usage_percent.toFixed(1)}}%</div>
                        <small class="text-muted">CPU</small>
                    </div>
                </div>
                <div class="mt-3">
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${{data.memory_percent}}%">
                            ${{data.memory_percent.toFixed(1)}}%
                        </div>
                    </div>
                    <div class="progress">
                        <div class="progress-bar bg-warning" style="width: ${{data.cpu_usage_percent}}%">
                            ${{data.cpu_usage_percent.toFixed(1)}}%
                        </div>
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }}

        function updatePerformanceChart(data) {{
            const ctx = document.getElementById('performanceChart').getContext('2d');

            if (performanceChart) {{
                performanceChart.destroy();
            }}

            const labels = Object.keys(data.apis || {{}});
            const successRates = labels.map(api => data.apis[api].success_rate);

            performanceChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: successRates,
                        backgroundColor: [
                            '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6c757d'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}

        function updateActiveAlerts(data) {{
            const container = document.getElementById('activeAlerts');

            if (!data.alerts || data.alerts.length === 0) {{
                container.innerHTML = '<div class="text-center text-success">✅ Nenhum alerta ativo</div>';
                return;
            }}

            const alertsHtml = data.alerts.slice(0, 5).map(alert => {{
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
    
    async def start(self):
        """Inicia o servidor web de produção"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            self.config.dashboard.host, 
            self.config.dashboard.port
        )
        await site.start()
        
        self.logger.info(f"🚀 Dashboard de produção iniciado em http://{self.config.dashboard.host}:{self.config.dashboard.port}")
        self.logger.info(f"📊 Monitoramento configurado para atualizar a cada 30s")
        self.logger.info(f"🔒 Rate limiting: {self.config.dashboard.rate_limit} req/min")
        
        return runner
    
    async def stop(self, runner):
        """Para o servidor web"""
        await runner.cleanup()
        self.logger.info("🛑 Dashboard de produção parado")

    async def _api_performance_handler(self, request):
        """API para métricas de performance"""
        try:
            performance_data = self.performance_monitor.get_performance_summary()
            return web.json_response(performance_data)
        except Exception as e:
            self.logger.error(f"Erro ao obter performance: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_fallback_handler(self, request):
        """API para status do sistema de fallback"""
        try:
            fallback_data = self.fallback_manager.get_status_report()
            return web.json_response(fallback_data)
        except Exception as e:
            self.logger.error(f"Erro ao obter fallback: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_notifications_handler(self, request):
        """API para estatísticas de notificações"""
        try:
            notification_data = self.notification_manager.get_delivery_stats()
            return web.json_response(notification_data)
        except Exception as e:
            self.logger.error(f"Erro ao obter notificações: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_alerts_handler(self, request):
        """API para alertas ativos"""
        try:
            from .alert_system import get_alert_manager
            alert_manager = get_alert_manager()
            alerts_data = {
                "alerts": [alert.to_dict() for alert in alert_manager.get_active_alerts()],
                "stats": alert_manager.get_alert_stats()
            }
            return web.json_response(alerts_data)
        except Exception as e:
            self.logger.error(f"Erro ao obter alertas: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_send_notification_handler(self, request):
        """API para enviar notificação manual"""
        try:
            data = await request.json()
            
            notification = NotificationMessage(
                title=data.get("title", "Notificação Manual"),
                content=data.get("content", ""),
                severity=data.get("severity", "info"),
                metadata=data.get("metadata", {})
            )

            results = await self.notification_manager.send_notification(notification)
            
            return web.json_response({
                "success": True,
                "results": results,
                "message": "Notificação enviada"
            })

        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_clear_performance_handler(self, request):
        """API para limpar métricas de performance"""
        try:
            self.performance_monitor.clear_metrics()
            return web.json_response({"success": True, "message": "Métricas limpas"})
        except Exception as e:
            self.logger.error(f"Erro ao limpar métricas: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _api_reset_fallback_handler(self, request):
        """API para resetar sistema de fallback"""
        try:
            self.fallback_manager.reset_all_apis()
            return web.json_response({"success": True, "message": "Fallback resetado"})
        except Exception as e:
            self.logger.error(f"Erro ao resetar fallback: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _admin_config_handler(self, request):
        """API para configurações administrativas"""
        try:
            config_data = self.config.to_dict()
            return web.json_response(config_data)
        except Exception as e:
            self.logger.error(f"Erro ao obter configuração: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _admin_restart_handler(self, request):
        """API para reiniciar serviços"""
        try:
            # Reinicia monitoramento
            self.performance_monitor.reset()
            self.fallback_manager.reset_all_apis()
            
            return web.json_response({
                "success": True,
                "message": "Serviços reiniciados",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar serviços: {e}")
            return web.json_response({"error": str(e)}, status=500)

# Função de conveniência
async def start_production_dashboard():
    """Inicia o dashboard de produção"""
    dashboard = ProductionDashboard()
    runner = await dashboard.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await dashboard.stop(runner)
        print("\n🛑 Dashboard parado pelo usuário")

if __name__ == "__main__":
    asyncio.run(start_production_dashboard())
