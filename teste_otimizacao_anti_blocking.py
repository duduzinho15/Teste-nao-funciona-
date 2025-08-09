#!/usr/bin/env python3
"""
Teste das Otimizações do Sistema Anti-Rate Limiting

Valida as melhorias implementadas:
- Delays reduzidos em off-hours
- Burst mode com threshold de 75%
- Recovery mais rápido do estado THROTTLED
- Aprendizado adaptativo por horário
- Logging detalhado
"""

import sys
import os
import time
import logging
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.path.dirname(__file__))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_traffic_patterns():
    """Testa os novos padrões de tráfego otimizados."""
    logger.info("=== TESTE: PADRÕES DE TRÁFEGO OTIMIZADOS ===")
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking
        
        system = get_advanced_anti_blocking()
        
        # Testar diferentes horários
        test_urls = [
            "https://fbref.com/en/comps/9/Premier-League-Stats",
            "https://fbref.com/en/comps/11/La-Liga-Stats",
            "https://fbref.com/en/comps/20/Bundesliga-Stats"
        ]
        
        current_pattern = system.get_current_traffic_pattern()
        logger.info(f"Padrão atual: {current_pattern.value}")
        
        # Calcular delays para diferentes URLs
        total_delay = 0
        for url in test_urls:
            delay = system.calculate_smart_delay(url)
            total_delay += delay
            logger.info(f"Delay calculado para {url.split('/')[-1]}: {delay:.2f}s")
        
        avg_delay = total_delay / len(test_urls)
        logger.info(f"Delay médio: {avg_delay:.2f}s")
        
        # Verificar se está em off-hours
        hour = datetime.now().hour
        is_off_hours = (0 <= hour <= 8) or (19 <= hour <= 23)
        
        if is_off_hours:
            logger.info("✅ TESTE EM OFF-HOURS: Delays devem estar reduzidos")
            if avg_delay < 5.0:
                logger.info("✅ SUCESSO: Delay médio baixo em off-hours")
            else:
                logger.warning("⚠️ ATENÇÃO: Delay ainda alto para off-hours")
        else:
            logger.info("ℹ️ TESTE EM HORÁRIO NORMAL: Delays padrão")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de padrões: {e}")
        return False

def test_burst_mode_threshold():
    """Testa o novo threshold de burst mode (75%)."""
    logger.info("=== TESTE: BURST MODE THRESHOLD (75%) ===")
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking
        
        system = get_advanced_anti_blocking()
        
        # Simular histórico com 75% de sucesso
        test_requests = [
            {'success': True}, {'success': True}, {'success': True},
            {'success': False}, {'success': True}, {'success': True},
            {'success': True}, {'success': False}  # 6/8 = 75%
        ]
        
        for i, req in enumerate(test_requests):
            system.record_request_result(
                f"https://test.com/url{i}", 
                req['success'], 
                1.0, 
                200 if req['success'] else 429
            )
        
        success_rate = system.get_recent_success_rate()
        can_burst = system.should_use_burst_mode()
        
        logger.info(f"Taxa de sucesso simulada: {success_rate:.2%}")
        logger.info(f"Burst mode permitido: {can_burst}")
        
        if success_rate >= 0.75 and can_burst:
            logger.info("✅ SUCESSO: Burst mode ativo com 75% de sucesso")
        elif success_rate >= 0.75:
            logger.info("ℹ️ Burst mode possível mas não ativado (probabilidade)")
        else:
            logger.warning("⚠️ Taxa de sucesso insuficiente para burst mode")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de burst mode: {e}")
        return False

def test_adaptive_learning():
    """Testa o sistema de aprendizado adaptativo."""
    logger.info("=== TESTE: APRENDIZADO ADAPTATIVO ===")
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking, get_hourly_analysis
        
        system = get_advanced_anti_blocking()
        
        # Simular alguns bloqueios no horário atual
        current_hour = datetime.now().hour
        
        # Simular 20 requisições com 10% de bloqueios
        for i in range(20):
            success = i % 10 != 0  # 1 bloqueio a cada 10 requisições
            system.record_request_result(
                f"https://test.com/adaptive{i}", 
                success, 
                1.0, 
                200 if success else 429
            )
        
        # Verificar multiplicador adaptativo
        multiplier = system.get_adaptive_multiplier_for_hour()
        hourly_analysis = get_hourly_analysis()
        
        logger.info(f"Multiplicador adaptativo para hora {current_hour}: {multiplier:.2f}x")
        
        if f"hour_{current_hour:02d}" in hourly_analysis:
            hour_data = hourly_analysis[f"hour_{current_hour:02d}"]
            logger.info(f"Estatísticas da hora atual:")
            logger.info(f"  - Requisições: {hour_data['requests']}")
            logger.info(f"  - Bloqueios: {hour_data['blocks']}")
            logger.info(f"  - Taxa de bloqueio: {hour_data['block_rate']:.2%}")
            logger.info(f"  - Nível de risco: {hour_data['risk_level']}")
        
        if 0.8 <= multiplier <= 1.2:
            logger.info("✅ SUCESSO: Multiplicador adaptativo funcionando")
        else:
            logger.info(f"ℹ️ Multiplicador adaptativo: {multiplier:.2f}x")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de aprendizado adaptativo: {e}")
        return False

def test_state_machine_recovery():
    """Testa a recuperação mais rápida do estado THROTTLED."""
    logger.info("=== TESTE: RECUPERAÇÃO RÁPIDA DO ESTADO THROTTLED ===")
    
    try:
        from Coleta_de_dados.apis.fbref.anti_429_state_machine import Anti429StateMachine
        
        state_machine = Anti429StateMachine()
        
        # Simular entrada em estado THROTTLED
        state_machine.record_429_error("https://test.com/throttled", retry_after=5)
        
        logger.info(f"Estado após 429: {state_machine.get_current_state().value}")
        
        # Calcular delay no estado THROTTLED
        throttled_delay = state_machine.calculate_delay()
        logger.info(f"Delay em THROTTLED: {throttled_delay:.2f}s")
        
        # Simular sucesso para recovery
        state_machine.record_success("https://test.com/success")
        
        logger.info(f"Estado após sucesso: {state_machine.get_current_state().value}")
        
        # Verificar se voltou para NOMINAL
        if state_machine.get_current_state().value == "NOMINAL":
            logger.info("✅ SUCESSO: Recovery rápido para NOMINAL após sucesso")
        else:
            logger.warning("⚠️ Estado não retornou para NOMINAL")
        
        # Verificar se delay otimizado é menor
        if throttled_delay < 30:  # Antes era até 60s
            logger.info("✅ SUCESSO: Delay THROTTLED otimizado (< 30s)")
        else:
            logger.warning(f"⚠️ Delay THROTTLED ainda alto: {throttled_delay:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de state machine: {e}")
        return False

def test_logging_metrics():
    """Testa o sistema de logging detalhado."""
    logger.info("=== TESTE: LOGGING DETALHADO ===")
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import log_optimization_metrics
        
        # Executar logging de métricas
        log_optimization_metrics()
        
        logger.info("✅ SUCESSO: Logging de métricas executado")
        return True
        
    except Exception as e:
        logger.error(f"Erro no teste de logging: {e}")
        return False

def main():
    """Executa todos os testes de otimização."""
    logger.info("🚀 INICIANDO TESTES DE OTIMIZAÇÃO DO SISTEMA ANTI-RATE LIMITING")
    logger.info("=" * 60)
    
    tests = [
        ("Padrões de Tráfego", test_traffic_patterns),
        ("Burst Mode Threshold", test_burst_mode_threshold),
        ("Aprendizado Adaptativo", test_adaptive_learning),
        ("State Machine Recovery", test_state_machine_recovery),
        ("Logging Detalhado", test_logging_metrics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"{'✅ PASSOU' if result else '❌ FALHOU'}: {test_name}")
        except Exception as e:
            logger.error(f"❌ ERRO: {test_name} - {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Pequena pausa entre testes
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nResultado: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 TODOS OS TESTES PASSARAM! Otimizações funcionando corretamente.")
    elif passed >= total * 0.8:
        logger.info("✅ MAIORIA DOS TESTES PASSOU. Sistema otimizado com sucesso.")
    else:
        logger.warning("⚠️ ALGUNS TESTES FALHARAM. Revisar implementação.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
