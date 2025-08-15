#!/usr/bin/env python3
"""
Demonstração das Melhorias Implementadas no Sistema RapidAPI

Este script demonstra:
- Sistema de cache inteligente
- Gerenciador de fallback de APIs
- Monitoramento de performance
- Sistema de notificações multi-canal
- Dashboard web para monitoramento
- Rate limiting e retry automático
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Coleta_de_dados.apis.rapidapi import (
    # APIs RapidAPI
    TodayFootballPredictionAPI,
    SoccerFootballInfoAPI,
    SportspageFeedsAPI,
    FootballPredictionAPI,
    PinnacleOddsAPI,
    FootballProAPI,
    SportAPI7,
    
    # Sistema de cache
    RapidAPICache,
    
    # Gerenciador de fallback
    APIFallbackManager,
    APIFallbackConfig,
    get_fallback_manager,
    
    # Monitor de performance
    PerformanceMonitor,
    PerformanceMetrics,
    AlertThreshold,
    monitor_performance,
    get_performance_monitor,
    
    # Sistema de notificações
    NotificationManager,
    NotificationMessage,
    NotificationConfig,
    get_notification_manager,
    setup_email_notifications,
    setup_slack_notifications,
    setup_discord_notifications,
    setup_telegram_notifications,
    
    # Dashboard web
    RapidAPIDashboard,
    DashboardConfig,
    start_dashboard
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DemoRapidAPIMelhorias:
    """Classe para demonstrar todas as melhorias implementadas"""
    
    def __init__(self):
        self.logger = logging.getLogger("demo.melhorias")
        
        # Instâncias das APIs
        self.apis = {
            "today_football": TodayFootballPredictionAPI(),
            "soccer_football": SoccerFootballInfoAPI(),
            "sportspage": SportspageFeedsAPI(),
            "football_prediction": FootballPredictionAPI(),
            "pinnacle": PinnacleOddsAPI(),
            "football_pro": FootballProAPI(),
            "sportapi7": SportAPI7()
        }
        
        # Gerenciadores do sistema
        self.fallback_manager = get_fallback_manager()
        self.performance_monitor = get_performance_monitor()
        self.notification_manager = get_notification_manager()
        
        # Configuração do dashboard
        self.dashboard = None
        self.dashboard_runner = None
        
    async def setup_system(self):
        """Configura todo o sistema"""
        self.logger.info("🔧 Configurando sistema...")
        
        # 1. Configura sistema de fallback
        await self._setup_fallback_system()
        
        # 2. Configura monitor de performance
        await self._setup_performance_monitor()
        
        # 3. Configura sistema de notificações
        await self._setup_notification_system()
        
        # 4. Configura dashboard web
        await self._setup_dashboard()
        
        self.logger.info("✅ Sistema configurado com sucesso!")
    
    async def _setup_fallback_system(self):
        """Configura o sistema de fallback"""
        self.logger.info("📡 Configurando sistema de fallback...")
        
        # Configurações de fallback para cada API
        fallback_configs = [
            APIFallbackConfig(
                api_name="today_football",
                priority=1,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="soccer_football", 
                priority=2,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="sportspage",
                priority=3,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="football_prediction",
                priority=4,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="pinnacle",
                priority=5,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="football_pro",
                priority=6,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            ),
            APIFallbackConfig(
                api_name="sportapi7",
                priority=7,
                retry_after=300,
                max_failures=3,
                health_check_interval=300
            )
        ]
        
        # Registra todas as APIs no sistema de fallback
        for config in fallback_configs:
            self.fallback_manager.register_api(config)
            self.logger.info(f"  ✅ API {config.api_name} registrada (prioridade: {config.priority})")
        
        # Inicia monitoramento de saúde
        await self.fallback_manager.start_health_monitoring()
        self.logger.info("  ✅ Monitoramento de saúde iniciado")
    
    async def _setup_performance_monitor(self):
        """Configura o monitor de performance"""
        self.logger.info("📊 Configurando monitor de performance...")
        
        # Configura alertas personalizados
        alert_thresholds = {
            "response_time": 5.0,  # 5 segundos
            "success_rate": 80.0,   # 80%
            "error_rate": 20.0,    # 20%
            "rate_limit_threshold": 3  # 3 falhas consecutivas
        }
        
        # Define callback para alertas
        async def alert_callback(alert_data):
            """Callback executado quando um alerta é disparado"""
            self.logger.warning(f"🚨 ALERTA: {alert_data['message']}")
            
            # Envia notificação automática
            message = NotificationMessage(
                title=f"Alerta de Performance - {alert_data['api_name']}",
                content=alert_data['message'],
                severity="warning" if alert_data['severity'] == 'warning' else "error",
                metadata={
                    "api_name": alert_data['api_name'],
                    "metric": alert_data['metric'],
                    "value": alert_data['value'],
                    "threshold": alert_data['threshold']
                }
            )
            
            await self.notification_manager.send_notification(message)
        
        # Configura o monitor
        for metric, threshold in alert_thresholds.items():
            if metric == "response_time":
                alert_threshold = AlertThreshold("average_response_time", ">", threshold, "warning", 60)
            elif metric == "success_rate":
                alert_threshold = AlertThreshold("success_rate", "<", threshold, "warning", 60)
            elif metric == "error_rate":
                alert_threshold = AlertThreshold("failure_rate", ">", threshold, "warning", 60)
            else:
                continue
            
            self.performance_monitor.add_alert_threshold(alert_threshold)
        
        self.performance_monitor.add_alert_callback(alert_callback)
        
        self.logger.info("  ✅ Alertas configurados")
        self.logger.info("  ✅ Callback de alertas configurado")
    
    async def _setup_notification_system(self):
        """Configura o sistema de notificações"""
        self.logger.info("🔔 Configurando sistema de notificações...")
        
        # Configura notificações por email (exemplo)
        # Descomente e configure conforme necessário
        """
        setup_email_notifications(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            from_email="seu-email@gmail.com",
            username="seu-email@gmail.com", 
            password="sua-senha-app",
            use_tls=True
        )
        """
        
        # Configura notificações para Slack (exemplo)
        # Descomente e configure conforme necessário
        """
        setup_slack_notifications(
            webhook_url="https://hooks.slack.com/services/SEU/WEBHOOK/URL",
            channel_name="rapidapi-alerts"
        )
        """
        
        # Configura notificações para Discord (exemplo)
        # Descomente e configure conforme necessário
        """
        setup_discord_notifications(
            webhook_url="https://discord.com/api/webhooks/SEU/WEBHOOK/URL",
            channel_name="rapidapi-monitoring"
        )
        """
        
        # Configura notificações para Telegram (exemplo)
        # Descomente e configure conforme necessário
        """
        setup_telegram_notifications(
            bot_token="SEU_BOT_TOKEN",
            chat_id="SEU_CHAT_ID",
            channel_name="rapidapi-updates"
        )
        """
        
        # Envia notificação de teste
        test_message = NotificationMessage(
            title="Sistema RapidAPI Iniciado",
            content="Sistema de monitoramento e notificações configurado com sucesso!",
            severity="info",
            metadata={
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "features": ["cache", "fallback", "monitoring", "notifications", "dashboard"]
            }
        )
        
        await self.notification_manager.send_notification(test_message)
        self.logger.info("  ✅ Sistema de notificações configurado")
        self.logger.info("  ✅ Notificação de teste enviada")
    
    async def _setup_dashboard(self):
        """Configura o dashboard web"""
        self.logger.info("🌐 Configurando dashboard web...")
        
        # Configuração do dashboard
        dashboard_config = DashboardConfig(
            host="0.0.0.0",
            port=8080,
            debug=True,
            refresh_interval=30,
            max_history_hours=24
        )
        
        # Cria instância do dashboard
        self.dashboard = RapidAPIDashboard(dashboard_config)
        
        # Inicia o dashboard em background
        self.dashboard_runner = await self.dashboard.start()
        
        self.logger.info("  ✅ Dashboard iniciado em http://localhost:8080")
        self.logger.info("  ✅ Atualização automática a cada 30 segundos")
    
    async def demo_cache_system(self):
        """Demonstra o sistema de cache"""
        self.logger.info("\n🔄 Demonstração do Sistema de Cache")
        self.logger.info("=" * 50)
        
        api = self.apis["today_football"]
        
        # Primeira requisição (cache miss)
        self.logger.info("📡 Primeira requisição (cache miss)...")
        start_time = datetime.now()
        result1 = await api.coletar_ligas()
        duration1 = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"  ⏱️  Tempo: {duration1:.3f}s")
        self.logger.info(f"  📊 Resultado: {len(result1) if result1 else 0} ligas")
        
        # Segunda requisição (cache hit)
        self.logger.info("📡 Segunda requisição (cache hit)...")
        start_time = datetime.now()
        result2 = await api.coletar_ligas()
        duration2 = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(f"  ⏱️  Tempo: {duration2:.3f}s")
        self.logger.info(f"  📊 Resultado: {len(result2) if result2 else 0} ligas")
        
        # Estatísticas do cache
        cache_stats = api._cache.get_stats()
        self.logger.info(f"  📈 Cache hits: {cache_stats['hits']}")
        self.logger.info(f"  📉 Cache misses: {cache_stats['misses']}")
        self.logger.info(f"  🎯 Taxa de hit: {cache_stats['hit_rate']:.1f}%")
        
        # Compara tempos
        speedup = duration1 / duration2 if duration2 > 0 else 0
        self.logger.info(f"  🚀 Aceleração: {speedup:.1f}x mais rápido")
    
    async def demo_fallback_system(self):
        """Demonstra o sistema de fallback"""
        self.logger.info("\n🔄 Demonstração do Sistema de Fallback")
        self.logger.info("=" * 50)
        
        # Simula falha em algumas APIs
        self.logger.info("🔴 Simulando falhas em APIs...")
        
        # Registra falhas para demonstrar o sistema
        for api_name in ["today_football", "soccer_football"]:
            self.fallback_manager.record_failure(api_name, "Erro simulado para demonstração")
            self.logger.info(f"  ❌ Falha registrada em {api_name}")
        
        # Mostra status atual
        status = self.fallback_manager.get_status_report()
        self.logger.info(f"  📊 APIs ativas: {status['fallback_stats']['apis_active']}")
        self.logger.info(f"  📊 APIs falhando: {status['fallback_stats']['apis_failing']}")
        self.logger.info(f"  📊 APIs com rate limit: {status['fallback_stats']['apis_rate_limited']}")
        
        # Demonstra seleção de API
        best_api = self.fallback_manager.get_best_api("coletar_ligas")
        self.logger.info(f"  🎯 Melhor API para coletar_ligas: {best_api}")
        
        # Executa operação com fallback
        self.logger.info("🔄 Executando operação com fallback...")
        
        async def test_operation(api_name, *args, **kwargs):
            """Operação de teste para o sistema de fallback"""
            api = self.apis.get(api_name)
            if api and hasattr(api, 'coletar_ligas'):
                return await api.coletar_ligas()
            return []
        
        success, result, api_used = await self.fallback_manager.execute_with_fallback(
            test_operation,
            "coletar_ligas"
        )
        
        if success:
            self.logger.info(f"  ✅ Operação executada com sucesso via {api_used}")
            self.logger.info(f"  📊 Resultado: {len(result) if result else 0} ligas")
        else:
            self.logger.error(f"  ❌ Falha na operação: {result}")
    
    async def demo_performance_monitoring(self):
        """Demonstra o monitoramento de performance"""
        self.logger.info("\n📊 Demonstração do Monitoramento de Performance")
        self.logger.info("=" * 50)
        
        # Executa algumas operações para gerar métricas
        self.logger.info("📡 Executando operações para gerar métricas...")
        
        operations = [
            ("today_football", "coletar_ligas"),
            ("soccer_football", "coletar_jogos"),
            ("sportspage", "coletar_noticias")
        ]
        
        for api_name, operation in operations:
            try:
                api = self.apis[api_name]
                method = getattr(api, operation)
                
                # Executa com monitoramento
                start_time = datetime.now()
                result = await method()
                duration = (datetime.now() - start_time).total_seconds()
                
                # Registra sucesso
                self.performance_monitor.record_success(api_name, duration)
                self.logger.info(f"  ✅ {api_name}.{operation}: {duration:.3f}s")
                
            except Exception as e:
                # Registra falha
                start_time = time.time()
                self.performance_monitor.record_request_failure(api_name, start_time, "error", str(e))
                self.logger.error(f"  ❌ {api_name}.{operation}: {e}")
        
        # Mostra métricas coletadas
        self.logger.info("\n📊 Métricas de Performance:")
        summary = self.performance_monitor.get_performance_summary()
        
        self.logger.info(f"  📈 Taxa de sucesso geral: {summary['overall_success_rate']:.1f}%")
        self.logger.info(f"  ⏱️  Tempo médio de resposta: {summary['overall_average_response_time']:.3f}s")
        self.logger.info(f"  📊 Total de requisições: {summary['total_requests']}")
        self.logger.info(f"  🚨 Alertas recentes: {summary['recent_alerts']}")
        
        # Mostra métricas por API
        self.logger.info("\n📊 Performance por API:")
        all_metrics = self.performance_monitor.get_all_metrics()
        
        for api_name, metrics in all_metrics.items():
            if metrics.total_requests > 0:
                self.logger.info(f"  {api_name}:")
                self.logger.info(f"    📈 Taxa de sucesso: {metrics.success_rate:.1f}%")
                self.logger.info(f"    ⏱️  Tempo médio: {metrics.average_response_time:.3f}s")
                self.logger.info(f"    📊 Requisições/min: {metrics.requests_per_minute:.1f}")
    
    async def demo_rate_limiting(self):
        """Demonstra o sistema de rate limiting"""
        self.logger.info("\n⏱️  Demonstração do Sistema de Rate Limiting")
        self.logger.info("=" * 50)
        
        api = self.apis["today_football"]
        
        # Executa múltiplas requisições rapidamente
        self.logger.info("📡 Executando múltiplas requisições...")
        
        tasks = []
        for i in range(5):
            task = asyncio.create_task(api.coletar_ligas())
            tasks.append(task)
        
        # Executa todas as tarefas
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Analisa resultados
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        self.logger.info(f"  📊 Requisições executadas: {len(results)}")
        self.logger.info(f"  ✅ Sucessos: {successful}")
        self.logger.info(f"  ❌ Falhas: {failed}")
        self.logger.info(f"  ⏱️  Tempo total: {total_time:.3f}s")
        self.logger.info(f"  📈 Taxa de sucesso: {(successful/len(results)*100):.1f}%")
        
        # Mostra estatísticas de rate limiting
        cache_stats = api._cache.get_stats()
        self.logger.info(f"  🔄 Cache hits: {cache_stats['hits']}")
        self.logger.info(f"  📡 Requisições externas: {cache_stats['misses']}")
    
    async def demo_notification_system(self):
        """Demonstra o sistema de notificações"""
        self.logger.info("\n🔔 Demonstração do Sistema de Notificações")
        self.logger.info("=" * 50)
        
        # Envia diferentes tipos de notificações
        notifications = [
            NotificationMessage(
                title="Teste de Sistema",
                content="Sistema funcionando perfeitamente!",
                severity="info",
                metadata={"test": True, "timestamp": datetime.now().isoformat()}
            ),
            NotificationMessage(
                title="Aviso de Performance",
                content="Taxa de sucesso caiu para 75%",
                severity="warning",
                metadata={"metric": "success_rate", "value": 75.0, "threshold": 80.0}
            ),
            NotificationMessage(
                title="Erro Crítico",
                content="API principal não está respondendo",
                severity="error",
                metadata={"api": "today_football", "error_code": 500, "retries": 3}
            )
        ]
        
        for i, notification in enumerate(notifications, 1):
            self.logger.info(f"📤 Enviando notificação {i} ({notification.severity})...")
            
            results = await self.notification_manager.send_notification(notification)
            
            for channel, success in results.items():
                status = "✅" if success else "❌"
                self.logger.info(f"  {status} {channel}: {notification.title}")
        
        # Mostra estatísticas de entrega
        delivery_stats = self.notification_manager.get_delivery_stats()
        self.logger.info(f"\n📊 Estatísticas de Entrega:")
        self.logger.info(f"  📤 Total enviadas: {delivery_stats['total']}")
        self.logger.info(f"  📈 Taxa de sucesso: {delivery_stats['success_rate']:.1f}%")
        
        # Mostra estatísticas por canal
        for channel, stats in delivery_stats['channels'].items():
            self.logger.info(f"  {channel}: {stats['success_rate']:.1f}% ({stats['successful']}/{stats['total']})")
    
    async def demo_dashboard_integration(self):
        """Demonstra a integração com o dashboard"""
        self.logger.info("\n🌐 Demonstração da Integração com Dashboard")
        self.logger.info("=" * 50)
        
        if not self.dashboard:
            self.logger.error("❌ Dashboard não está configurado")
            return
        
        self.logger.info("📊 Dashboard disponível em: http://localhost:8080")
        self.logger.info("📈 Atualizando métricas em tempo real...")
        
        # Simula algumas operações para atualizar o dashboard
        for i in range(3):
            self.logger.info(f"  🔄 Ciclo {i+1}/3...")
            
            # Executa operações para gerar métricas
            for api_name in ["today_football", "soccer_football"]:
                try:
                    api = self.apis[api_name]
                    await api.coletar_ligas()
                    self.logger.info(f"    ✅ {api_name} atualizado")
                except Exception as e:
                    self.logger.info(f"    ❌ {api_name} falhou: {e}")
            
            # Aguarda um pouco
            await asyncio.sleep(2)
        
        self.logger.info("✅ Dashboard atualizado com métricas em tempo real")
        self.logger.info("🌐 Acesse http://localhost:8080 para visualizar")
    
    async def demo_integracao_completa(self):
        """Demonstra a integração completa de todos os sistemas"""
        self.logger.info("\n🚀 Demonstração da Integração Completa")
        self.logger.info("=" * 60)
        
        self.logger.info("🔄 Executando operação completa com todos os sistemas...")
        
        # 1. Seleciona melhor API via fallback
        best_api_name = self.fallback_manager.get_best_api("coletar_ligas")
        self.logger.info(f"🎯 API selecionada: {best_api_name}")
        
        # 2. Executa operação com monitoramento
        start_time = datetime.now()
        
        try:
            api = self.apis[best_api_name]
            result = await api.coletar_ligas()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # 3. Registra sucesso no monitor
            self.performance_monitor.record_success(best_api_name, duration)
            
            # 4. Envia notificação de sucesso
            success_message = NotificationMessage(
                title="Operação Executada com Sucesso",
                content=f"API {best_api_name} executou coletar_ligas em {duration:.3f}s",
                severity="info",
                metadata={
                    "api": best_api_name,
                    "operation": "coletar_ligas",
                    "duration": duration,
                    "result_count": len(result) if result else 0
                }
            )
            
            await self.notification_manager.send_notification(success_message)
            
            self.logger.info(f"✅ Operação executada com sucesso!")
            self.logger.info(f"⏱️  Tempo: {duration:.3f}s")
            self.logger.info(f"📊 Resultado: {len(result) if result else 0} ligas")
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            # 3. Registra falha no monitor
            self.performance_monitor.record_failure(best_api_name, str(e))
            
            # 4. Envia notificação de erro
            error_message = NotificationMessage(
                title="Erro na Operação",
                content=f"API {best_api_name} falhou ao executar coletar_ligas",
                severity="error",
                metadata={
                    "api": best_api_name,
                    "operation": "coletar_ligas",
                    "error": str(e),
                    "duration": duration
                }
            )
            
            await self.notification_manager.send_notification(error_message)
            
            self.logger.error(f"❌ Operação falhou: {e}")
        
        # 5. Mostra resumo final
        self.logger.info("\n📊 Resumo da Integração:")
        
        # Status do fallback
        fallback_status = self.fallback_manager.get_status_report()
        self.logger.info(f"  🔄 Fallback: {fallback_status['fallback_stats']['apis_active']} APIs ativas")
        
        # Performance
        perf_summary = self.performance_monitor.get_performance_summary()
        self.logger.info(f"  📈 Performance: {perf_summary['overall_success_rate']:.1f}% sucesso")
        
        # Notificações
        notif_stats = self.notification_manager.get_delivery_stats()
        self.logger.info(f"  🔔 Notificações: {notif_stats['success_rate']:.1f}% entrega")
        
        # Dashboard
        self.logger.info(f"  🌐 Dashboard: http://localhost:8080")
    
    async def run_all_demos(self):
        """Executa todas as demonstrações"""
        self.logger.info("🎬 Iniciando Demonstrações das Melhorias RapidAPI")
        self.logger.info("=" * 70)
        
        try:
            # Configura o sistema
            await self.setup_system()
            
            # Executa demonstrações
            await self.demo_cache_system()
            await self.demo_fallback_system()
            await self.demo_performance_monitoring()
            await self.demo_rate_limiting()
            await self.demo_notification_system()
            await self.demo_dashboard_integration()
            await self.demo_integracao_completa()
            
            self.logger.info("\n🎉 Todas as demonstrações concluídas com sucesso!")
            self.logger.info("🌐 Dashboard disponível em: http://localhost:8080")
            self.logger.info("⏸️  Pressione Ctrl+C para parar o dashboard")
            
            # Mantém o sistema rodando
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("\n🛑 Parando sistema...")
                
        except Exception as e:
            self.logger.error(f"❌ Erro durante demonstração: {e}")
            raise
        
        finally:
            # Limpeza
            if self.dashboard_runner:
                await self.dashboard.stop(self.dashboard_runner)
            await self.fallback_manager.stop_health_monitoring()

async def main():
    """Função principal"""
    demo = DemoRapidAPIMelhorias()
    await demo.run_all_demos()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
