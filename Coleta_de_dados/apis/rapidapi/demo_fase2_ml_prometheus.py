#!/usr/bin/env python3
"""
Demonstração Completa da FASE 2: ML + Prometheus/Grafana

Este script demonstra:
- Sistema de Machine Learning para análise preditiva
- Detecção automática de anomalias
- Otimização automática de thresholds
- Integração com Prometheus para métricas
- Dashboards Grafana automáticos
- Sistema completo de produção
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
from .notification_system import get_notification_manager
from .performance_monitor import get_performance_monitor
from .fallback_manager import get_fallback_manager
from .alert_system import get_alert_manager
from .ml_analytics import get_ml_analytics
from .prometheus_integration import get_prometheus_exporter, get_prometheus_server, get_grafana_integration
from .dashboard_producao import start_production_dashboard

class SistemaFase2Completo:
    """Sistema completo da FASE 2 com ML e Prometheus"""
    
    def __init__(self):
        self.logger = logging.getLogger("sistema.fase2")
        self.config = None
        self.dashboard_task = None
        self.prometheus_task = None
        
        # Módulos do sistema
        self.notification_manager = None
        self.performance_monitor = None
        self.fallback_manager = None
        self.alert_manager = None
        self.ml_analytics = None
        self.prometheus_exporter = None
        self.prometheus_server = None
        self.grafana_integration = None
        
        # Status
        self.ml_models_trained = False
        self.prometheus_running = False
        self.grafana_dashboards_created = False
    
    async def inicializar(self):
        """Inicializa todos os sistemas da FASE 2"""
        try:
            self.logger.info("🚀 Inicializando Sistema FASE 2 - ML + Prometheus...")
            
            # Carrega configuração
            await self._carregar_configuracao()
            
            # Inicializa módulos básicos
            await self._inicializar_modulos_basicos()
            
            # Inicializa sistema ML
            await self._inicializar_sistema_ml()
            
            # Inicializa Prometheus
            await self._inicializar_prometheus()
            
            # Inicializa Grafana
            await self._inicializar_grafana()
            
            # Inicia dashboard
            await self._iniciar_dashboard()
            
            # Configura alertas inteligentes
            await self._configurar_alertas_inteligentes()
            
            # Inicia monitoramento
            await self._iniciar_monitoramento()
            
            self.logger.info("✅ Sistema FASE 2 inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar sistema FASE 2: {e}")
            raise
    
    async def _carregar_configuracao(self):
        """Carrega configuração de produção"""
        try:
            self.config = load_production_config()
            self.logger.info(f"📋 Configuração carregada: {self.config.environment}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configuração: {e}")
            self.config = load_production_config()
    
    async def _inicializar_modulos_basicos(self):
        """Inicializa módulos básicos do sistema"""
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
            self.logger.error(f"❌ Erro ao inicializar módulos básicos: {e}")
            raise
    
    async def _inicializar_sistema_ml(self):
        """Inicializa sistema de Machine Learning"""
        try:
            self.logger.info("🤖 Inicializando Sistema de Machine Learning...")
            
            # Obtém instância do ML Analytics
            self.ml_analytics = get_ml_analytics()
            
            # Simula dados para treinamento
            await self._simular_dados_para_ml()
            
            # Treina modelos
            self.logger.info("🚀 Treinando modelos de ML...")
            training_results = await self.ml_analytics.train_all_models()
            
            success_count = sum(training_results.values())
            self.logger.info(f"✅ {success_count}/{len(training_results)} modelos treinados com sucesso")
            
            if success_count > 0:
                self.ml_models_trained = True
                
                # Otimiza thresholds automaticamente
                self.logger.info("⚡ Otimizando thresholds com ML...")
                optimization_result = await self.ml_analytics.optimize_alert_thresholds()
                
                if optimization_result.get("optimized_thresholds"):
                    self.logger.info("✅ Thresholds otimizados automaticamente")
                else:
                    self.logger.warning("⚠️  Falha na otimização automática de thresholds")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar sistema ML: {e}")
    
    async def _simular_dados_para_ml(self):
        """Simula dados para treinamento dos modelos ML"""
        try:
            self.logger.info("📊 Simulando dados para treinamento ML...")
            
            # Simula métricas de performance por 5 minutos
            start_time = time.time()
            while time.time() - start_time < 300:  # 5 minutos
                # Simula requisições para diferentes APIs
                apis = ["api_football", "the_sports_db", "stats_bomb", "sofascore", "news_api"]
                
                for api_name in apis:
                    # Simula sucesso/erro baseado em padrões
                    hour = datetime.now().hour
                    if 9 <= hour <= 18:  # Horário comercial
                        success_rate = 85 + (hour - 9) * 0.5  # Melhora durante o dia
                    else:
                        success_rate = 70 + (hour - 18) * 0.3  # Piora à noite
                    
                    # Adiciona variação aleatória
                    import random
                    success_rate += random.uniform(-5, 5)
                    success_rate = max(50, min(95, success_rate))
                    
                    # Simula tempo de resposta
                    response_time = 0.5 + (100 - success_rate) / 100 * 2
                    
                    # Registra métricas
                    self.performance_monitor.record_request_start(api_name)
                    time.sleep(0.1)  # Simula tempo de execução
                    
                    if random.random() * 100 < success_rate:
                        self.performance_monitor.record_request_success(api_name, response_time)
                    else:
                        self.performance_monitor.record_request_failure(api_name, "Simulated error")
                
                await asyncio.sleep(10)  # Atualiza a cada 10 segundos
            
            self.logger.info("✅ Dados simulados para ML concluídos")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao simular dados: {e}")
    
    async def _inicializar_prometheus(self):
        """Inicializa sistema Prometheus"""
        try:
            self.logger.info("📊 Inicializando Sistema Prometheus...")
            
            # Obtém exportador
            self.prometheus_exporter = get_prometheus_exporter()
            
            # Obtém servidor
            self.prometheus_server = get_prometheus_server()
            
            # Inicia servidor em background
            self.prometheus_task = asyncio.create_task(
                self.prometheus_server.start()
            )
            
            # Aguarda inicialização
            await asyncio.sleep(3)
            
            self.prometheus_running = True
            self.logger.info("✅ Sistema Prometheus inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Prometheus: {e}")
    
    async def _inicializar_grafana(self):
        """Inicializa integração Grafana"""
        try:
            self.logger.info("🎨 Inicializando Integração Grafana...")
            
            # Obtém integração
            self.grafana_integration = get_grafana_integration()
            
            # Tenta criar dashboards
            if self.grafana_integration.grafana_api_key:
                self.logger.info("🔄 Criando dashboards Grafana...")
                dashboards_result = await self.grafana_integration.create_all_dashboards()
                
                success_count = sum(1 for r in dashboards_result.values() if not r.get("error"))
                self.logger.info(f"✅ {success_count}/{len(dashboards_result)} dashboards criados")
                
                if success_count > 0:
                    self.grafana_dashboards_created = True
            else:
                self.logger.warning("⚠️  API key do Grafana não configurada")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar Grafana: {e}")
    
    async def _iniciar_dashboard(self):
        """Inicia dashboard web de produção"""
        try:
            # Inicia dashboard em background
            self.dashboard_task = asyncio.create_task(
                start_production_dashboard()
            )
            
            # Aguarda um pouco para o dashboard inicializar
            await asyncio.sleep(2)
            
            self.logger.info(f"🌐 Dashboard iniciado em http://localhost:8080")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar dashboard: {e}")
    
    async def _configurar_alertas_inteligentes(self):
        """Configura alertas inteligentes baseados em ML"""
        try:
            self.logger.info("🧠 Configurando Alertas Inteligentes...")
            
            if not self.ml_models_trained:
                self.logger.warning("⚠️  Modelos ML não treinados - usando alertas padrão")
                return
            
            # Adiciona regras de alerta baseadas em ML
            await self.alert_manager.add_custom_alert_rule(
                name="Anomalia ML Detectada",
                metric="ml_anomaly",
                threshold=0.7,
                operator=">",
                severity="warning",
                description="Alerta baseado em detecção de anomalia por ML"
            )
            
            # Adiciona regra para degradação gradual
            await self.alert_manager.add_custom_alert_rule(
                name="Degradação Gradual de Performance",
                metric="performance_trend",
                threshold=-5.0,
                operator="<",
                severity="warning",
                description="Alerta para degradação gradual de performance"
            )
            
            self.logger.info("✅ Alertas inteligentes configurados")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar alertas inteligentes: {e}")
    
    async def _iniciar_monitoramento(self):
        """Inicia monitoramento contínuo"""
        try:
            # Inicia monitoramento de performance
            self.performance_monitor.start_monitoring()
            
            # Inicia monitoramento de saúde das APIs
            await self.fallback_manager.start_health_monitoring()
            
            # Inicia monitoramento de alertas
            await self.alert_manager.start_monitoring()
            
            # Inicia manutenção automática ML
            asyncio.create_task(self._ml_maintenance_loop())
            
            # Inicia coleta de dados ML
            if self.ml_analytics:
                await self.ml_analytics.start_data_collection()
            
            # Inicia exportação automática Prometheus
            if self.prometheus_exporter:
                await self.prometheus_exporter.start_auto_export()
            
            self.logger.info("📈 Monitoramento contínuo iniciado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar monitoramento: {e}")
    
    async def _ml_maintenance_loop(self):
        """Loop de manutenção automática ML"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 hora
                
                if self.ml_models_trained:
                    self.logger.info("🔧 Executando manutenção automática ML...")
                    maintenance_result = await self.ml_analytics.auto_maintenance()
                    
                    if maintenance_result.get("models_trained"):
                        self.logger.info("✅ Modelos ML retreinados automaticamente")
                    
                    if maintenance_result.get("thresholds_optimized"):
                        self.logger.info("✅ Thresholds reotimizados automaticamente")
                
            except Exception as e:
                self.logger.error(f"❌ Erro na manutenção automática ML: {e}")
                await asyncio.sleep(1800)  # 30 minutos em caso de erro
    
    async def executar_demonstracao(self):
        """Executa demonstração completa da FASE 2"""
        try:
            self.logger.info("🎭 Iniciando Demonstração da FASE 2...")
            
            # Demonstra sistema ML
            await self._demonstrar_sistema_ml()
            
            # Demonstra Prometheus
            await self._demonstrar_prometheus()
            
            # Demonstra Grafana
            await self._demonstrar_grafana()
            
            # Demonstra alertas inteligentes
            await self._demonstrar_alertas_inteligentes()
            
            # Demonstra predições
            await self._demonstrar_predicoes()
            
            self.logger.info("✅ Demonstração da FASE 2 concluída!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração: {e}")
    
    async def _demonstrar_sistema_ml(self):
        """Demonstra sistema de Machine Learning"""
        try:
            self.logger.info("🤖 Demonstrando Sistema ML...")
            
            if not self.ml_models_trained:
                self.logger.warning("⚠️  Modelos ML não treinados")
                return
            
            # Detecta anomalias
            anomalies = self.ml_analytics.detect_anomalies()
            anomaly_count = len([a for a in anomalies if a.is_anomaly])
            self.logger.info(f"🔍 Anomalias detectadas: {anomaly_count}")
            
            # Analisa padrões
            patterns = self.ml_analytics.analyze_patterns()
            self.logger.info(f"📊 Padrões identificados: {len(patterns)}")
            
            # Gera relatório ML
            ml_report = await self.ml_analytics.generate_ml_report()
            self.logger.info(f"📋 Relatório ML gerado: {bool(ml_report)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração ML: {e}")
    
    async def _demonstrar_prometheus(self):
        """Demonstra sistema Prometheus"""
        try:
            self.logger.info("📊 Demonstrando Prometheus...")
            
            if not self.prometheus_running:
                self.logger.warning("⚠️  Prometheus não está rodando")
                return
            
            # Obtém métricas
            metrics_text = self.prometheus_exporter.get_metrics_text()
            metrics_lines = len(metrics_text.decode().split('\n'))
            self.logger.info(f"📈 Métricas Prometheus: {metrics_lines} linhas")
            
            # Obtém métricas JSON
            metrics_json = self.prometheus_exporter.get_metrics_json()
            self.logger.info(f"📋 Métricas configuradas: {metrics_json.get('total_metrics', 0)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração Prometheus: {e}")
    
    async def _demonstrar_grafana(self):
        """Demonstra integração Grafana"""
        try:
            self.logger.info("🎨 Demonstrando Grafana...")
            
            if not self.grafana_dashboards_created:
                self.logger.warning("⚠️  Dashboards Grafana não criados")
                return
            
            self.logger.info("✅ Dashboards Grafana disponíveis")
            self.logger.info("🌐 Acesse Grafana para visualizar dashboards")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração Grafana: {e}")
    
    async def _demonstrar_alertas_inteligentes(self):
        """Demonstra alertas inteligentes"""
        try:
            self.logger.info("🧠 Demonstrando Alertas Inteligentes...")
            
            # Dispara alerta de teste
            await self.alert_manager.trigger_manual_alert(
                name="Teste Alerta Inteligente",
                message="Este é um teste dos alertas inteligentes da FASE 2",
                severity="info"
            )
            
            # Mostra alertas ativos
            active_alerts = self.alert_manager.get_active_alerts()
            self.logger.info(f"📊 Alertas ativos: {len(active_alerts)}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de alertas: {e}")
    
    async def _demonstrar_predicoes(self):
        """Demonstra predições de ML"""
        try:
            self.logger.info("🔮 Demonstrando Predições ML...")
            
            if not self.ml_models_trained:
                self.logger.warning("⚠️  Modelos ML não treinados")
                return
            
            # Obtém APIs disponíveis
            apis = set(record.get("api_name") for record in self.ml_analytics.historical_data if record.get("api_name"))
            
            if apis:
                api_name = list(apis)[0]
                
                # Prediz performance
                predictions = self.ml_analytics.predict_performance(api_name, hours_ahead=3)
                self.logger.info(f"🔮 Predições para {api_name}: {len(predictions)}")
                
                for pred in predictions:
                    self.logger.info(f"  • {pred.timestamp.strftime('%H:%M')}: {pred.predicted_value:.1f}% (confiança: {pred.confidence:.2f})")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na demonstração de predições: {e}")
    
    async def parar(self):
        """Para todos os sistemas"""
        try:
            self.logger.info("🛑 Parando Sistema FASE 2...")
            
            # Para dashboard
            if self.dashboard_task:
                self.dashboard_task.cancel()
                try:
                    await self.dashboard_task
                except asyncio.CancelledError:
                    pass
            
            # Para Prometheus
            if self.prometheus_task:
                self.prometheus_task.cancel()
                try:
                    await self.prometheus_task
                except asyncio.CancelledError:
                    pass
            
            # Para monitoramento
            if self.performance_monitor:
                await self.performance_monitor.stop_monitoring()
            
            if self.fallback_manager:
                await self.fallback_manager.stop_health_monitoring()
            
            self.logger.info("✅ Sistema FASE 2 parado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao parar sistema: {e}")
    
    def gerar_relatorio_fase2(self) -> Dict[str, Any]:
        """Gera relatório completo da FASE 2"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "phase": "FASE 2 - ML + Prometheus",
                "system_status": "running",
                "ml_system": {
                    "models_trained": self.ml_models_trained,
                    "models_count": len(self.ml_analytics.models) if self.ml_analytics else 0,
                    "historical_data": len(self.ml_analytics.historical_data) if self.ml_analytics else 0
                },
                "prometheus": {
                    "running": self.prometheus_running,
                    "metrics_count": len(self.prometheus_exporter.metrics) if self.prometheus_exporter else 0,
                    "port": 9090
                },
                "grafana": {
                    "dashboards_created": self.grafana_dashboards_created,
                    "api_configured": bool(self.grafana_integration.grafana_api_key) if self.grafana_integration else False
                },
                "performance": self.performance_monitor.get_performance_summary() if self.performance_monitor else None,
                "alerts": self.alert_manager.get_alert_stats() if self.alert_manager else None
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {"error": str(e)}

async def main():
    """Função principal"""
    print("🚀 Sistema FASE 2 - ML + Prometheus/Grafana")
    print("=" * 60)
    
    # Cria template do .env se não existir
    try:
        create_env_template()
        print("📝 Template .env criado/verificado")
    except Exception as e:
        print(f"⚠️  Erro ao criar template .env: {e}")
    
    # Inicializa sistema
    sistema = SistemaFase2Completo()
    
    try:
        await sistema.inicializar()
        
        # Executa demonstração
        await sistema.executar_demonstracao()
        
        # Mostra relatório
        print("\n📊 RELATÓRIO DA FASE 2:")
        print("-" * 40)
        relatorio = sistema.gerar_relatorio_fase2()
        print(json.dumps(relatorio, indent=2, default=str))
        
        # Mostra URLs de acesso
        print(f"\n🌐 URLs de Acesso:")
        print(f"  • Dashboard: http://localhost:8080")
        print(f"  • Prometheus: http://localhost:9090/metrics")
        print(f"  • Grafana: http://localhost:3000 (se configurado)")
        
        print(f"\n⏹️  Pressione Ctrl+C para parar")
        
        # Mantém sistema rodando
        while True:
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupção detectada...")
    except Exception as e:
        print(f"❌ Erro no sistema: {e}")
    finally:
        await sistema.parar()
        print("👋 Sistema FASE 2 finalizado!")

if __name__ == "__main__":
    asyncio.run(main())
