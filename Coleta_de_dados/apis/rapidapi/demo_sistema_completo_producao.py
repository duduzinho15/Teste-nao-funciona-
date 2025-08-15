#!/usr/bin/env python3
"""
Demonstração Completa do Sistema de Produção RapidAPI

Este script demonstra:
- Sistema de notificações multi-canal
- Dashboard web de produção
- Sistema de alertas automáticos
- Monitoramento de performance
- Sistema de fallback de APIs
- Configuração de produção
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importa módulos do sistema
from .production_config import load_production_config, create_env_template
from .notification_system import (
    get_notification_manager, 
    setup_email_notifications,
    setup_slack_notifications,
    setup_discord_notifications,
    setup_telegram_notifications
)
from .performance_monitor import get_performance_monitor
from .fallback_manager import get_fallback_manager
from .alert_system import get_alert_manager
from .dashboard_producao import start_production_dashboard

class SistemaCompletoProducao:
    """Sistema completo de produção integrado"""

    def __init__(self):
        self.logger = logging.getLogger("sistema.producao")
        self.config = None
        self.dashboard_task = None
        
        # Módulos do sistema
        self.notification_manager = None
        self.performance_monitor = None
        self.fallback_manager = None
        self.alert_manager = None

    async def inicializar(self):
        """Inicializa todos os sistemas"""
        try:
            self.logger.info("🚀 Inicializando Sistema de Produção...")
            
            # Carrega configuração
            await self._carregar_configuracao()
            
            # Inicializa módulos
            await self._inicializar_modulos()
            
            # Configura notificações
            await self._configurar_notificacoes()
            
            # Inicia dashboard
            await self._iniciar_dashboard()
            
            # Configura alertas
            await self._configurar_alertas()
            
            # Inicia monitoramento
            await self._iniciar_monitoramento()
            
            # Inicia monitoramento de alertas
            await self.alert_manager.start_monitoring()
            
            self.logger.info("✅ Sistema de Produção inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar sistema: {e}")
            raise

    async def _carregar_configuracao(self):
        """Carrega configuração de produção"""
        try:
            self.config = load_production_config()
            self.logger.info(f"📋 Configuração carregada: {self.config.environment}")
            self.logger.info(f"🔔 Canais de notificação: {self.config.get_notification_channels()}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configuração: {e}")
            # Cria configuração padrão
            self.config = load_production_config()

    async def _inicializar_modulos(self):
        """Inicializa todos os módulos do sistema"""
        try:
            # Performance Monitor
            self.performance_monitor = get_performance_monitor()
            self.logger.info("📊 Performance Monitor inicializado")
            
            # Fallback Manager
            self.fallback_manager = get_fallback_manager()
            self.logger.info("🔄 Fallback Manager inicializado")
            
            # Alert Manager
            self.alert_manager = get_alert_manager()
            self.logger.info("🚨 Alert Manager inicializado")
            
            # Notification Manager
            self.notification_manager = get_notification_manager()
            self.logger.info("📢 Notification Manager inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar módulos: {e}")
            raise

    async def _configurar_notificacoes(self):
        """Configura canais de notificação"""
        try:
            # Email (se configurado)
            if self.config.email:
                setup_email_notifications(
                    smtp_server=self.config.email.smtp_server,
                    smtp_port=self.config.email.smtp_port,
                    from_email=self.config.email.from_email,
                    username=self.config.email.username,
                    password=self.config.email.password,
                    use_tls=self.config.email.use_tls
                )
                self.logger.info("📧 Notificações por email configuradas")
            
            # Slack (se configurado)
            if self.config.slack:
                setup_slack_notifications(
                    webhook_url=self.config.slack.webhook_url,
                    channel_name="slack"
                )
                self.logger.info("💬 Notificações Slack configuradas")
            
            # Discord (se configurado)
            if self.config.discord:
                setup_discord_notifications(
                    webhook_url=self.config.discord.webhook_url,
                    channel_name="discord"
                )
                self.logger.info("🎮 Notificações Discord configuradas")
            
            # Telegram (se configurado)
            if self.config.telegram:
                setup_telegram_notifications(
                    bot_token=self.config.telegram.bot_token,
                    chat_id=self.config.telegram.chat_id,
                    channel_name="telegram"
                )
                self.logger.info("📱 Notificações Telegram configuradas")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar notificações: {e}")

    async def _iniciar_dashboard(self):
        """Inicia dashboard web de produção"""
        try:
            # Inicia dashboard em background
            self.dashboard_task = asyncio.create_task(
                start_production_dashboard()
            )
            
            # Aguarda um pouco para o dashboard inicializar
            await asyncio.sleep(2)
            
            self.logger.info(f"🌐 Dashboard iniciado em http://{self.config.dashboard.host}:{self.config.dashboard.port}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar dashboard: {e}")

    async def _configurar_alertas(self):
        """Configura sistema de alertas"""
        try:
            # Adiciona regras customizadas se necessário
            await self.alert_manager.add_custom_alert_rule(
                name="Taxa de Erro Crítica Customizada",
                metric="error_rate",
                threshold=50.0,
                operator=">",
                severity="critical",
                description="Taxa de erro acima de 50% (regra customizada)"
            )
            
            # Adiciona callback de escalação
            self.alert_manager.add_escalation_callback(self._callback_escalacao)
            
            self.logger.info("🚨 Sistema de alertas configurado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar alertas: {e}")

    async def _callback_escalacao(self, alert):
        """Callback para escalação de alertas"""
        try:
            self.logger.warning(f"🚨 ALERTA ESCALADO: {alert.rule.name}")
            
            # Envia notificação de escalação
            from .notification_system import NotificationMessage
            
            notification = NotificationMessage(
                title=f"🚨 ESCALAÇÃO: {alert.rule.name}",
                content=f"Alerta escalado após {alert.escalation_count} tentativas",
                severity="critical",
                metadata={
                    "alert_id": alert.id,
                    "escalation_count": alert.escalation_count,
                    "metric": alert.rule.metric,
                    "value": alert.value
                }
            )
            
            await self.notification_manager.send_notification(notification)
            
        except Exception as e:
            self.logger.error(f"❌ Erro no callback de escalação: {e}")

    async def _iniciar_monitoramento(self):
        """Inicia monitoramento contínuo"""
        try:
            # Inicia monitoramento de performance
            self.performance_monitor.start_monitoring()
            
            # Inicia monitoramento de saúde das APIs
            await self.fallback_manager.start_health_monitoring()
            
            self.logger.info("📈 Monitoramento contínuo iniciado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar monitoramento: {e}")

    async def executar_demonstracao(self):
        """Executa demonstração completa do sistema"""
        try:
            self.logger.info("🎭 Iniciando Demonstração do Sistema...")
            
            # Simula algumas operações para demonstrar o sistema
            await self._demonstrar_notificacoes()
            await self._demonstrar_alertas()
            await self._demonstrar_performance()
            await self._demonstrar_fallback()
            
            self.logger.info("✅ Demonstração concluída!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração: {e}")

    async def _demonstrar_notificacoes(self):
        """Demonstra sistema de notificações"""
        try:
            self.logger.info("📢 Demonstrando sistema de notificações...")
            
            from .notification_system import NotificationMessage
            
            # Notificação de teste
            notification = NotificationMessage(
                title="🧪 Teste do Sistema de Produção",
                content="Sistema funcionando perfeitamente!",
                severity="info",
                metadata={
                    "test_type": "notification_demo",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            results = await self.notification_manager.send_notification(notification)
            
            self.logger.info(f"📤 Notificação enviada: {results}")
            
            # Aguarda um pouco
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de notificações: {e}")

    async def _demonstrar_alertas(self):
        """Demonstra sistema de alertas"""
        try:
            self.logger.info("🚨 Demonstrando sistema de alertas...")
            
            # Dispara alerta manual para teste
            await self.alert_manager.trigger_manual_alert(
                name="Teste de Alerta Manual",
                message="Este é um teste do sistema de alertas",
                severity="warning"
            )
            
            # Aguarda um pouco
            await asyncio.sleep(2)
            
            # Mostra alertas ativos
            active_alerts = self.alert_manager.get_active_alerts()
            self.logger.info(f"📊 Alertas ativos: {len(active_alerts)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de alertas: {e}")

    async def _demonstrar_performance(self):
        """Demonstra monitoramento de performance"""
        try:
            self.logger.info("📊 Demonstrando monitoramento de performance...")
            
            # Simula algumas métricas
            self.performance_monitor.record_request_start("api_teste")
            await asyncio.sleep(0.1)
            self.performance_monitor.record_request_success("api_teste", 0.15)
            
            # Obtém resumo
            summary = self.performance_monitor.get_performance_summary()
            self.logger.info(f"📈 Resumo de performance: {summary.get('overall_success_rate', 0):.1f}%")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de performance: {e}")

    async def _demonstrar_fallback(self):
        """Demonstra sistema de fallback"""
        try:
            self.logger.info("🔄 Demonstrando sistema de fallback...")
            
            # Mostra status
            status = self.fallback_manager.get_status_report()
            self.logger.info(f"📋 Status do fallback: {len(status.get('apis', []))} APIs registradas")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de fallback: {e}")

    async def parar(self):
        """Para todos os sistemas"""
        try:
            self.logger.info("🛑 Parando Sistema de Produção...")
            
            # Para dashboard
            if self.dashboard_task:
                self.dashboard_task.cancel()
                try:
                    await self.dashboard_task
                except asyncio.CancelledError:
                    pass
            
            # Para monitoramento
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()
            
            if self.fallback_manager:
                await self.fallback_manager.stop_health_monitoring()
            
            self.logger.info("✅ Sistema de Produção parado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao parar sistema: {e}")

    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório completo do sistema"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": "running",
                "configuration": self.config.to_dict() if self.config else None,
                "performance": self.performance_monitor.get_performance_summary() if self.performance_monitor else None,
                "fallback": self.fallback_manager.get_status_report() if self.fallback_manager else None,
                "alerts": self.alert_manager.get_alert_stats() if self.alert_manager else None,
                "notifications": self.notification_manager.get_delivery_stats() if self.notification_manager else None
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {"error": str(e)}

async def main():
    """Função principal"""
    print("🚀 Sistema de Produção RapidAPI - Demonstração Completa")
    print("=" * 60)
    
    # Cria template do .env se não existir
    try:
        create_env_template()
        print("📝 Template .env criado/verificado")
    except Exception as e:
        print(f"⚠️  Erro ao criar template .env: {e}")
    
    # Inicializa sistema
    sistema = SistemaCompletoProducao()
    
    try:
        await sistema.inicializar()
        
        # Executa demonstração
        await sistema.executar_demonstracao()
        
        # Mostra relatório
        print("\n📊 RELATÓRIO DO SISTEMA:")
        print("-" * 40)
        relatorio = sistema.gerar_relatorio()
        print(json.dumps(relatorio, indent=2, default=str))
        
        # Mantém sistema rodando
        print(f"\n🌐 Dashboard disponível em: http://localhost:8080")
        print("⏹️  Pressione Ctrl+C para parar")
        
        while True:
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupção detectada...")
    except Exception as e:
        print(f"❌ Erro no sistema: {e}")
    finally:
        await sistema.parar()
        print("👋 Sistema finalizado!")

if __name__ == "__main__":
    asyncio.run(main())
