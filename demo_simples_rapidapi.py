#!/usr/bin/env python3
"""
Demonstração Simples das Melhorias RapidAPI

Este script demonstra as funcionalidades básicas implementadas:
- Sistema de cache inteligente
- Gerenciador de fallback de APIs
- Monitoramento de performance
- Sistema de notificações
- Dashboard web
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def demo_cache_system():
    """Demonstra o sistema de cache"""
    logger.info("\n🔄 Demonstração do Sistema de Cache")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import (
            TodayFootballPredictionAPI,
            RapidAPICache
        )
        
        # Cria instância da API
        api = TodayFootballPredictionAPI()
        
        # Primeira requisição (cache miss)
        logger.info("📡 Primeira requisição (cache miss)...")
        start_time = datetime.now()
        result1 = await api.coletar_ligas()
        duration1 = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"  ⏱️  Tempo: {duration1:.3f}s")
        logger.info(f"  📊 Resultado: {len(result1) if result1 else 0} ligas")
        
        # Segunda requisição (cache hit)
        logger.info("📡 Segunda requisição (cache hit)...")
        start_time = datetime.now()
        result2 = await api.coletar_ligas()
        duration2 = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"  ⏱️  Tempo: {duration2:.3f}s")
        logger.info(f"  📊 Resultado: {len(result2) if result2 else 0} ligas")
        
        # Estatísticas do cache
        cache_stats = api._cache.get_stats()
        logger.info(f"  📈 Cache hits: {cache_stats['hits']}")
        logger.info(f"  📉 Cache misses: {cache_stats['misses']}")
        logger.info(f"  🎯 Taxa de hit: {cache_stats['hit_rate']:.1f}%")
        
        # Compara tempos
        speedup = duration1 / duration2 if duration2 > 0 else 0
        logger.info(f"  🚀 Aceleração: {speedup:.1f}x mais rápido")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração de cache: {e}")
        return False

async def demo_fallback_system():
    """Demonstra o sistema de fallback"""
    logger.info("\n🔄 Demonstração do Sistema de Fallback")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import (
            get_fallback_manager,
            APIFallbackConfig
        )
        
        manager = get_fallback_manager()
        
        # Registra APIs de teste
        configs = [
            APIFallbackConfig("api1", priority=1, retry_after=60, max_failures=3, health_check_interval=60),
            APIFallbackConfig("api2", priority=2, retry_after=120, max_failures=3, health_check_interval=60),
            APIFallbackConfig("api3", priority=3, retry_after=180, max_failures=3, health_check_interval=60)
        ]
        
        for config in configs:
            manager.register_api(config)
            logger.info(f"  ✅ API {config.api_name} registrada (prioridade: {config.priority})")
        
        # Simula falhas
        manager.record_failure("api1", "erro_simulado")
        manager.record_failure("api2", "erro_simulado")
        
        # Mostra status
        status = manager.get_status_report()
        logger.info(f"  📊 APIs ativas: {status['fallback_stats']['apis_active']}")
        logger.info(f"  📊 APIs falhando: {status['fallback_stats']['apis_failing']}")
        
        # Seleciona melhor API
        best_api = manager.get_best_api("teste")
        logger.info(f"  🎯 Melhor API para teste: {best_api}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração de fallback: {e}")
        return False

async def demo_performance_monitor():
    """Demonstra o monitor de performance"""
    logger.info("\n📊 Demonstração do Monitor de Performance")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import get_performance_monitor
        
        monitor = get_performance_monitor()
        
        # Registra algumas métricas
        start_time = monitor.record_request_start("test_api")
        await asyncio.sleep(0.1)
        monitor.record_request_success("test_api", start_time, 0.1)
        
        start_time = monitor.record_request_start("test_api")
        monitor.record_request_failure("test_api", start_time, "test_error", "Erro de teste")
        
        # Obtém resumo
        summary = monitor.get_performance_summary()
        logger.info(f"  📊 Total de requisições: {summary['total_requests']}")
        logger.info(f"  📈 Taxa de sucesso geral: {summary['overall_success_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração de performance: {e}")
        return False

async def demo_notification_system():
    """Demonstra o sistema de notificações"""
    logger.info("\n🔔 Demonstração do Sistema de Notificações")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import (
            get_notification_manager,
            NotificationMessage
        )
        
        manager = get_notification_manager()
        
        # Cria mensagem de teste
        message = NotificationMessage(
            title="Teste do Sistema",
            content="Sistema de notificações funcionando perfeitamente!",
            severity="info",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        # Envia notificação
        results = await manager.send_notification(message)
        logger.info(f"  📤 Notificação enviada: {results}")
        
        # Mostra estatísticas
        delivery_stats = manager.get_delivery_stats()
        logger.info(f"  📊 Total enviadas: {delivery_stats['total']}")
        logger.info(f"  📈 Taxa de sucesso: {delivery_stats['success_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração de notificações: {e}")
        return False

async def demo_dashboard():
    """Demonstra o dashboard web"""
    logger.info("\n🌐 Demonstração do Dashboard Web")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import (
            RapidAPIDashboard,
            DashboardConfig
        )
        
        # Cria configuração
        config = DashboardConfig(
            host="127.0.0.1",
            port=8081,
            debug=True,
            refresh_interval=30
        )
        
        # Cria instância
        dashboard = RapidAPIDashboard(config)
        logger.info("  ✅ Dashboard criado com sucesso")
        
        # Inicia dashboard
        runner = await dashboard.start()
        logger.info("  🚀 Dashboard iniciado")
        
        # Para o dashboard
        await dashboard.stop(runner)
        logger.info("  🛑 Dashboard parado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do dashboard: {e}")
        return False

async def demo_rapidapi_imports():
    """Demonstra imports das APIs"""
    logger.info("\n📡 Demonstração dos Imports das APIs")
    logger.info("=" * 50)
    
    try:
        from Coleta_de_dados.apis.rapidapi import (
            TodayFootballPredictionAPI,
            SoccerFootballInfoAPI,
            SportspageFeedsAPI,
            FootballPredictionAPI,
            PinnacleOddsAPI,
            FootballProAPI,
            SportAPI7
        )
        
        # Cria instâncias
        apis = [
            TodayFootballPredictionAPI(),
            SoccerFootballInfoAPI(),
            SportspageFeedsAPI(),
            FootballPredictionAPI(),
            PinnacleOddsAPI(),
            FootballProAPI(),
            SportAPI7()
        ]
        
        logger.info(f"  ✅ {len(apis)} APIs RapidAPI importadas com sucesso")
        
        for i, api in enumerate(apis, 1):
            logger.info(f"    {i}. {api.__class__.__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos imports: {e}")
        return False

async def run_all_demos():
    """Executa todas as demonstrações"""
    logger.info("🎬 Iniciando Demonstrações Simples das Melhorias RapidAPI")
    logger.info("=" * 70)
    
    demos = [
        ("Sistema de Cache", demo_cache_system),
        ("Sistema de Fallback", demo_fallback_system),
        ("Monitor de Performance", demo_performance_monitor),
        ("Sistema de Notificações", demo_notification_system),
        ("Dashboard Web", demo_dashboard),
        ("Imports das APIs", demo_rapidapi_imports)
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
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DAS DEMONSTRAÇÕES")
    logger.info("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for demo_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        logger.info(f"{status}: {demo_name}")
    
    logger.info(f"\n🎯 Resultado: {passed}/{total} demonstrações passaram")
    
    if passed == total:
        logger.info("🎉 Todas as demonstrações passaram! Sistema funcionando perfeitamente.")
    else:
        logger.error(f"⚠️  {total - passed} demonstrações falharam.")
    
    return passed == total

async def main():
    """Função principal"""
    try:
        success = await run_all_demos()
        if success:
            logger.info("\n🚀 Sistema pronto para uso!")
        else:
            logger.error("\n🔧 Sistema precisa de ajustes antes do uso.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
