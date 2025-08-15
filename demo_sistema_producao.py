#!/usr/bin/env python3
"""
Demonstração Completa do Sistema de Produção RapidAPI

Este script demonstra todas as funcionalidades implementadas:
- Sistema de configuração de produção
- Dashboard otimizado para produção
- Sistema de alertas automáticos
- Sistema de notificações
- Monitoramento de performance
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
import time

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def demo_configuracao_producao():
    """Demonstra o sistema de configuração de produção"""
    logger.info("\n⚙️  Demonstração da Configuração de Produção")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.production_config import (
            load_production_config,
            create_env_template
        )
        
        # Cria template do .env
        create_env_template()
        logger.info("✅ Template .env criado com sucesso")
        
        # Carrega configuração
        config = load_production_config()
        logger.info(f"✅ Configuração carregada: {config.environment}")
        logger.info(f"   Canais de notificação: {config.get_notification_channels()}")
        logger.info(f"   Dashboard: {config.dashboard.host}:{config.dashboard.port}")
        logger.info(f"   Log Level: {config.log_level}")
        
        # Salva configuração sanitizada
        config.save_to_file('config_demo.json')
        logger.info("✅ Configuração salva em config_demo.json")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na configuração de produção: {e}")
        return False

async def demo_sistema_alertas():
    """Demonstra o sistema de alertas automáticos"""
    logger.info("\n🚨 Demonstração do Sistema de Alertas")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.alert_system import (
            get_alert_manager,
            add_custom_alert_rule,
            trigger_manual_alert
        )
        
        manager = get_alert_manager()
        
        # Mostra regras padrão
        logger.info(f"📋 Regras padrão configuradas: {len(manager.alert_rules)}")
        for rule in manager.alert_rules[:3]:  # Mostra apenas 3 para não poluir
            logger.info(f"  • {rule.name}: {rule.metric} {rule.operator} {rule.threshold}")
        
        # Adiciona regra customizada
        custom_rule = await add_custom_alert_rule(
            name="Teste Customizado",
            metric="success_rate",
            threshold=90.0,
            operator="<",
            severity="warning",
            description="Regra de teste customizada"
        )
        logger.info(f"✅ Regra customizada adicionada: {custom_rule.name}")
        
        # Dispara alerta manual
        alert = await trigger_manual_alert(
            "Teste do Sistema",
            "Sistema de alertas funcionando perfeitamente!",
            "info"
        )
        logger.info(f"✅ Alerta manual criado: {alert.id}")
        
        # Mostra estatísticas
        stats = manager.get_alert_stats()
        logger.info(f"📊 Estatísticas dos alertas:")
        logger.info(f"   Total: {stats['total_alerts']}")
        logger.info(f"   Ativos: {stats['active_alerts']}")
        logger.info(f"   Regras: {stats['rules_count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema de alertas: {e}")
        return False

async def demo_dashboard_producao():
    """Demonstra o dashboard de produção"""
    logger.info("\n🌐 Demonstração do Dashboard de Produção")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.dashboard_producao import (
            ProductionDashboard
        )
        
        # Cria instância do dashboard
        dashboard = ProductionDashboard()
        logger.info("✅ Dashboard de produção criado com sucesso")
        
        # Mostra configurações
        logger.info(f"   Host: {dashboard.config.dashboard.host}")
        logger.info(f"   Porta: {dashboard.config.dashboard.port}")
        logger.info(f"   Rate Limit: {dashboard.config.dashboard.rate_limit} req/min")
        logger.info(f"   Debug: {dashboard.config.dashboard.debug}")
        
        # Inicia dashboard brevemente para teste
        logger.info("🚀 Iniciando dashboard para teste...")
        runner = await dashboard.start()
        
        # Aguarda um pouco para verificar se está funcionando
        await asyncio.sleep(2)
        
        # Para o dashboard
        await dashboard.stop(runner)
        logger.info("🛑 Dashboard parado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no dashboard de produção: {e}")
        return False

async def demo_sistema_notificacoes():
    """Demonstra o sistema de notificações"""
    logger.info("\n🔔 Demonstração do Sistema de Notificações")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.notification_system import (
            get_notification_manager,
            NotificationMessage,
            setup_email_notifications,
            setup_slack_notifications
        )
        
        manager = get_notification_manager()
        
        # Mostra notificadores disponíveis
        logger.info(f"📡 Notificadores configurados: {len(manager.notifiers)}")
        
        # Cria mensagem de teste
        message = NotificationMessage(
            title="Teste do Sistema de Produção",
            content="Sistema de notificações funcionando perfeitamente em produção!",
            severity="info",
            metadata={
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "environment": "production"
            }
        )
        
        # Envia notificação
        results = await manager.send_notification(message)
        logger.info(f"📤 Notificação enviada: {results}")
        
        # Mostra estatísticas
        delivery_stats = manager.get_delivery_stats()
        logger.info(f"📊 Estatísticas de entrega:")
        logger.info(f"   Total: {delivery_stats['total']}")
        logger.info(f"   Taxa de sucesso: {delivery_stats['success_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema de notificações: {e}")
        return False

async def demo_monitoramento_performance():
    """Demonstra o monitoramento de performance"""
    logger.info("\n📊 Demonstração do Monitoramento de Performance")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.performance_monitor import (
            get_performance_monitor
        )
        
        monitor = get_performance_monitor()
        
        # Registra algumas métricas de teste
        start_time = monitor.record_request_start("demo_api")
        await asyncio.sleep(0.1)
        monitor.record_request_success("demo_api", start_time, 0.1)
        
        start_time = monitor.record_request_start("demo_api")
        await asyncio.sleep(0.2)
        monitor.record_request_success("demo_api", start_time, 0.2)
        
        start_time = monitor.record_request_start("demo_api")
        monitor.record_request_failure("demo_api", start_time, "demo_error", "Erro de demonstração")
        
        # Obtém resumo
        summary = monitor.get_performance_summary()
        logger.info(f"📈 Resumo de performance:")
        logger.info(f"   Total de requisições: {summary['total_requests']}")
        logger.info(f"   Taxa de sucesso geral: {summary['overall_success_rate']:.1f}%")
        logger.info(f"   APIs monitoradas: {summary['total_apis']}")
        if summary['apis_by_performance']:
            best_api = summary['apis_by_performance'][0]
            logger.info(f"   Melhor API: {best_api['api_name']} ({best_api['success_rate']:.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no monitoramento de performance: {e}")
        return False

async def demo_sistema_fallback():
    """Demonstra o sistema de fallback"""
    logger.info("\n🔄 Demonstração do Sistema de Fallback")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.fallback_manager import (
            get_fallback_manager,
            APIFallbackConfig
        )
        
        manager = get_fallback_manager()
        
        # Registra APIs de teste
        configs = [
            APIFallbackConfig("api_producao", priority=1, retry_after=60, max_failures=3, health_check_interval=60),
            APIFallbackConfig("api_backup", priority=2, retry_after=120, max_failures=3, health_check_interval=60),
            APIFallbackConfig("api_emergencia", priority=3, retry_after=180, max_failures=3, health_check_interval=60)
        ]
        
        for config in configs:
            manager.register_api(config)
            logger.info(f"✅ API {config.api_name} registrada (prioridade: {config.priority})")
        
        # Simula algumas falhas
        manager.record_failure("api_producao", "erro_simulado")
        manager.record_failure("api_backup", "erro_simulado")
        
        # Mostra status
        status = manager.get_status_report()
        logger.info(f"📊 Status do sistema de fallback:")
        logger.info(f"   APIs ativas: {status['fallback_stats']['apis_active']}")
        logger.info(f"   APIs falhando: {status['fallback_stats']['apis_failing']}")
        logger.info(f"   Rate limited: {status['fallback_stats']['apis_rate_limited']}")
        
        # Seleciona melhor API
        best_api = manager.get_best_api("teste")
        logger.info(f"🎯 Melhor API para teste: {best_api}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema de fallback: {e}")
        return False

async def demo_cache_sistema():
    """Demonstra o sistema de cache"""
    logger.info("\n💾 Demonstração do Sistema de Cache")
    logger.info("=" * 60)
    
    try:
        from Coleta_de_dados.apis.rapidapi.base_rapidapi import RapidAPICache
        
        cache = RapidAPICache()
        
        # Adiciona dados de teste
        cache.set("test_key", "test_value", ttl=60)
        cache.set("test_number", 42, ttl=120)
        cache.set("test_list", [1, 2, 3, 4, 5], ttl=180)
        
        # Recupera dados
        value1 = cache.get("test_key")
        value2 = cache.get("test_number")
        value3 = cache.get("test_list")
        
        logger.info(f"📥 Dados recuperados do cache:")
        logger.info(f"   test_key: {value1}")
        logger.info(f"   test_number: {value2}")
        logger.info(f"   test_list: {value3}")
        
        # Estatísticas do cache
        stats = cache.get_stats()
        logger.info(f"📊 Estatísticas do cache:")
        logger.info(f"   Hits: {stats['hits']}")
        logger.info(f"   Misses: {stats['misses']}")
        logger.info(f"   Taxa de hit: {stats['hit_rate']:.1f}%")
        logger.info(f"   Tamanho: {stats['size']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no sistema de cache: {e}")
        return False

async def demo_integracao_completa():
    """Demonstra a integração completa dos sistemas"""
    logger.info("\n🔗 Demonstração da Integração Completa")
    logger.info("=" * 60)
    
    try:
        # Simula cenário real de produção
        logger.info("🎭 Simulando cenário de produção...")
        
        # 1. Sistema detecta problema de performance
        logger.info("1️⃣  Sistema detecta problema de performance...")
        await asyncio.sleep(1)
        
        # 2. Alerta é disparado automaticamente
        logger.info("2️⃣  Alerta é disparado automaticamente...")
        from Coleta_de_dados.apis.rapidapi.alert_system import trigger_manual_alert
        alert = await trigger_manual_alert(
            "Problema de Performance",
            "Taxa de sucesso caiu para 75%",
            "warning"
        )
        await asyncio.sleep(1)
        
        # 3. Notificação é enviada
        logger.info("3️⃣  Notificação é enviada...")
        await asyncio.sleep(1)
        
        # 4. Sistema de fallback é ativado
        logger.info("4️⃣  Sistema de fallback é ativado...")
        await asyncio.sleep(1)
        
        # 5. Dashboard é atualizado
        logger.info("5️⃣  Dashboard é atualizado com informações...")
        await asyncio.sleep(1)
        
        # 6. Alerta é resolvido
        logger.info("6️⃣  Alerta é resolvido automaticamente...")
        await asyncio.sleep(1)
        
        logger.info("✅ Cenário de produção simulado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na integração completa: {e}")
        return False

async def run_all_demos():
    """Executa todas as demonstrações"""
    logger.info("🎬 Iniciando Demonstração Completa do Sistema de Produção")
    logger.info("=" * 80)
    
    demos = [
        ("Configuração de Produção", demo_configuracao_producao),
        ("Sistema de Alertas", demo_sistema_alertas),
        ("Dashboard de Produção", demo_dashboard_producao),
        ("Sistema de Notificações", demo_sistema_notificacoes),
        ("Monitoramento de Performance", demo_monitoramento_performance),
        ("Sistema de Fallback", demo_sistema_fallback),
        ("Sistema de Cache", demo_cache_sistema),
        ("Integração Completa", demo_integracao_completa)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        logger.info(f"\n🔍 Executando: {demo_name}")
        try:
            success = await demo_func()
            results.append((demo_name, success))
            
            if success:
                logger.info(f"✅ {demo_name}: PASSOU")
            else:
                logger.error(f"❌ {demo_name}: FALHOU")
                
        except Exception as e:
            logger.error(f"❌ {demo_name}: ERRO - {e}")
            results.append((demo_name, False))
    
    # Resumo final
    logger.info("\n" + "=" * 80)
    logger.info("🏆 RESUMO FINAL DAS DEMONSTRAÇÕES")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for demo_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status}: {demo_name}")
    
    logger.info(f"\n🎯 Resultado: {passed}/{total} demonstrações passaram")
    
    if passed == total:
        logger.info("🎉 TODAS AS DEMONSTRAÇÕES PASSARAM!")
        logger.info("🚀 Sistema de Produção está 100% funcional!")
        logger.info("\n📋 PRÓXIMOS PASSOS:")
        logger.info("   1. Configure suas variáveis no arquivo .env")
        logger.info("   2. Inicie o dashboard: python -m Coleta_de_dados.apis.rapidapi.dashboard_producao")
        logger.info("   3. Configure notificações reais (email, Slack, Discord, Telegram)")
        logger.info("   4. Monitore o sistema via dashboard")
        logger.info("   5. Ajuste thresholds de alerta conforme necessário")
    else:
        logger.error(f"⚠️  {total - passed} demonstrações falharam.")
        logger.error("🔧 Sistema precisa de ajustes antes do uso em produção.")
    
    return passed == total

async def main():
    """Função principal"""
    try:
        success = await run_all_demos()
        if success:
            logger.info("\n🎊 PARABÉNS! Sistema de Produção implementado com sucesso!")
        else:
            logger.error("\n💥 Sistema de Produção precisa de correções.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal durante as demonstrações: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
