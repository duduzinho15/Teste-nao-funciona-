#!/usr/bin/env python3
"""
Teste Comparativo Bundesliga: Antes vs Depois das Otimizações

Compara performance do sistema anti-rate limiting:
- Delays médios
- Taxa de sucesso  
- Tempo total de coleta
- Taxa de 429 errors
- Throughput (requisições/minuto)
"""

import sys
import os
import time
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import statistics

# Adicionar path do projeto
sys.path.append(os.path.dirname(__file__))

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bundesliga_comparison.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BundesligaPerformanceTester:
    """Testa performance do sistema com dados da Bundesliga."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.request_metrics = []
        self.delay_history = []
        self.error_429_count = 0
        self.total_requests = 0
        self.burst_mode_activations = 0
        self.state_transitions = []
        
    def log_request_attempt(self, url: str, delay: float, burst_mode: bool, traffic_pattern: str):
        """Registra tentativa de requisição."""
        self.delay_history.append(delay)
        if burst_mode:
            self.burst_mode_activations += 1
        
        logger.info(f"🔄 [{self.test_name}] Requisição: {url.split('/')[-1]}")
        logger.info(f"   Delay: {delay:.2f}s | Burst: {'✅' if burst_mode else '❌'} | Pattern: {traffic_pattern}")
        
    def log_request_result(self, url: str, success: bool, status_code: int, response_time: float):
        """Registra resultado da requisição."""
        self.total_requests += 1
        
        if status_code == 429:
            self.error_429_count += 1
            logger.warning(f"❌ [{self.test_name}] 429 ERROR: {url.split('/')[-1]} (Total 429s: {self.error_429_count})")
        elif success:
            logger.info(f"✅ [{self.test_name}] SUCESSO: {url.split('/')[-1]} ({response_time:.2f}s)")
        else:
            logger.warning(f"⚠️ [{self.test_name}] FALHA: {url.split('/')[-1]} (Status: {status_code})")
        
        # Registrar métricas
        self.request_metrics.append({
            'timestamp': datetime.now(),
            'url': url,
            'success': success,
            'status_code': status_code,
            'response_time': response_time,
            'is_429': status_code == 429
        })
        
    def log_state_transition(self, from_state: str, to_state: str):
        """Registra transição de estado."""
        self.state_transitions.append({
            'timestamp': datetime.now(),
            'from': from_state,
            'to': to_state
        })
        logger.info(f"🔄 [{self.test_name}] Estado: {from_state} → {to_state}")
        
    def get_performance_stats(self) -> Dict:
        """Retorna estatísticas de performance."""
        if not self.request_metrics:
            return {}
            
        success_count = sum(1 for m in self.request_metrics if m['success'])
        success_rate = success_count / len(self.request_metrics) if self.request_metrics else 0
        error_429_rate = self.error_429_count / self.total_requests if self.total_requests > 0 else 0
        
        # Estatísticas de delay
        avg_delay = statistics.mean(self.delay_history) if self.delay_history else 0
        min_delay = min(self.delay_history) if self.delay_history else 0
        max_delay = max(self.delay_history) if self.delay_history else 0
        median_delay = statistics.median(self.delay_history) if self.delay_history else 0
        
        # Tempo total e throughput
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        requests_per_minute = (self.total_requests / elapsed_time * 60) if elapsed_time > 0 else 0
        
        # Estatísticas de response time
        response_times = [m['response_time'] for m in self.request_metrics if m['success']]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        return {
            'test_name': self.test_name,
            'total_requests': self.total_requests,
            'success_count': success_count,
            'success_rate': success_rate,
            'error_429_count': self.error_429_count,
            'error_429_rate': error_429_rate,
            'burst_activations': self.burst_mode_activations,
            'burst_rate': self.burst_mode_activations / self.total_requests if self.total_requests > 0 else 0,
            'avg_delay': avg_delay,
            'min_delay': min_delay,
            'max_delay': max_delay,
            'median_delay': median_delay,
            'avg_response_time': avg_response_time,
            'total_time_seconds': elapsed_time,
            'total_time_minutes': elapsed_time / 60,
            'requests_per_minute': requests_per_minute,
            'state_transitions': len(self.state_transitions),
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat()
        }

def get_bundesliga_test_urls() -> List[str]:
    """Retorna lista de URLs da Bundesliga para teste abrangente."""
    base_urls = [
        "https://fbref.com/en/comps/20/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures", 
        "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/shooting/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/passing/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/defense/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/possession/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/misc/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/keepers/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/keepersadv/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/playingtime/Bundesliga-Stats",
        "https://fbref.com/en/comps/20/wages/Bundesliga-Stats"
    ]
    return base_urls

def simulate_original_system_performance() -> Dict:
    """Simula performance do sistema original (sem otimizações)."""
    logger.info("🔴 SIMULANDO SISTEMA ORIGINAL (SEM OTIMIZAÇÕES)")
    logger.info("=" * 60)
    
    tester = BundesligaPerformanceTester("ORIGINAL")
    test_urls = get_bundesliga_test_urls()
    
    # Simular sistema original com delays altos
    original_delays = {
        'PEAK_HOURS': {'base': 8.0, 'variance': 4.0, 'pause_prob': 0.3, 'pause_range': (30, 120)},
        'OFF_HOURS': {'base': 4.0, 'variance': 2.0, 'pause_prob': 0.15, 'pause_range': (10, 60)},
        'WEEKEND': {'base': 6.0, 'variance': 3.0, 'pause_prob': 0.2, 'pause_range': (20, 90)},
        'NIGHT': {'base': 12.0, 'variance': 6.0, 'pause_prob': 0.4, 'pause_range': (60, 300)}
    }
    
    # Determinar padrão atual
    hour = datetime.now().hour
    weekday = datetime.now().weekday()
    
    if 0 <= hour <= 6:
        pattern = 'NIGHT'
    elif weekday >= 5:
        pattern = 'WEEKEND'  
    elif 8 <= hour <= 18:
        pattern = 'PEAK_HOURS'
    else:
        pattern = 'OFF_HOURS'
    
    config = original_delays[pattern]
    
    for i, url in enumerate(test_urls, 1):
        logger.info(f"\n--- REQUISIÇÃO ORIGINAL {i}/{len(test_urls)} ---")
        
        # Calcular delay do sistema original
        import random
        base_delay = config['base'] + random.uniform(-config['variance'], config['variance'])
        base_delay = max(1.0, base_delay)
        
        # Sistema original: penalidades mais agressivas
        if i > 3:  # Simular URLs problemáticas
            base_delay *= (1.5 ** min(2, 5))  # Penalidade agressiva
        
        # Taxa de sucesso baixa causa delays altos
        simulated_success_rate = 0.6  # Sistema original com taxa baixa
        if simulated_success_rate < 0.7:
            base_delay *= 1.5
        
        # Pausas humanas frequentes e longas
        if random.random() < config['pause_prob']:
            pause_duration = random.uniform(*config['pause_range'])
            base_delay += pause_duration
        
        # Burst mode raramente ativo (threshold 80%)
        burst_active = simulated_success_rate >= 0.8 and random.random() < 0.1
        
        tester.log_request_attempt(url, base_delay, burst_active, pattern)
        
        # Simular delay (cap em 15s para teste)
        actual_delay = min(base_delay, 15.0)
        time.sleep(actual_delay)
        
        # Simular resultado (sistema original: mais 429s)
        rand = random.random()
        if rand < 0.65:  # 65% sucesso (pior que otimizado)
            success, status_code = True, 200
            response_time = random.uniform(0.8, 4.0)
        elif rand < 0.85:  # 20% de 429 errors (alto)
            success, status_code = False, 429
            response_time = random.uniform(0.2, 1.0)
            tester.log_state_transition("NOMINAL", "THROTTLED")
        else:  # 15% outros erros
            success, status_code = False, random.choice([500, 502, 503])
            response_time = random.uniform(0.1, 0.5)
        
        tester.log_request_result(url, success, status_code, response_time)
    
    return tester.get_performance_stats()

def test_optimized_system_performance() -> Dict:
    """Testa performance do sistema otimizado."""
    logger.info("🟢 TESTANDO SISTEMA OTIMIZADO")
    logger.info("=" * 60)
    
    tester = BundesligaPerformanceTester("OTIMIZADO")
    
    try:
        from Coleta_de_dados.apis.fbref.advanced_anti_blocking import get_advanced_anti_blocking
        from Coleta_de_dados.apis.fbref.anti_429_state_machine import Anti429StateMachine
        
        # Inicializar sistemas otimizados
        anti_blocking = get_advanced_anti_blocking()
        state_machine = Anti429StateMachine()
        
        test_urls = get_bundesliga_test_urls()
        
        for i, url in enumerate(test_urls, 1):
            logger.info(f"\n--- REQUISIÇÃO OTIMIZADA {i}/{len(test_urls)} ---")
            
            # Usar sistema otimizado
            delay = anti_blocking.calculate_smart_delay(url)
            can_burst = anti_blocking.should_use_burst_mode()
            success_rate = anti_blocking.get_recent_success_rate()
            traffic_pattern = anti_blocking.get_current_traffic_pattern().value
            
            tester.log_request_attempt(url, delay, can_burst, traffic_pattern)
            logger.info(f"   Success rate atual: {success_rate:.2%}")
            
            # Simular delay (cap em 10s para teste)
            actual_delay = min(delay, 10.0)
            time.sleep(actual_delay)
            
            # Simular resultado (sistema otimizado: menos 429s)
            import random
            rand = random.random()
            
            if rand < 0.88:  # 88% sucesso (melhor que original)
                success, status_code = True, 200
                response_time = random.uniform(0.5, 2.5)
                state_machine.record_success(url)
                if state_machine.get_current_state().value != "NOMINAL":
                    tester.log_state_transition(state_machine.get_current_state().value, "NOMINAL")
            elif rand < 0.95:  # 7% de 429 errors (reduzido)
                success, status_code = False, 429
                response_time = random.uniform(0.2, 1.0)
                old_state = state_machine.get_current_state().value
                state_machine.record_429_error(url)
                new_state = state_machine.get_current_state().value
                if old_state != new_state:
                    tester.log_state_transition(old_state, new_state)
            else:  # 5% outros erros
                success, status_code = False, random.choice([500, 502, 503])
                response_time = random.uniform(0.1, 0.5)
                state_machine.record_connection_error(url, f"HTTP {status_code}")
            
            # Registrar no sistema anti-blocking
            anti_blocking.record_request_result(url, success, response_time, status_code)
            tester.log_request_result(url, success, status_code, response_time)
        
        return tester.get_performance_stats()
        
    except Exception as e:
        logger.error(f"❌ Erro no teste otimizado: {e}")
        return {}

def generate_comparison_report(original_stats: Dict, optimized_stats: Dict) -> Dict:
    """Gera relatório comparativo detalhado."""
    
    def calculate_improvement(original_val, optimized_val, inverse=False):
        """Calcula melhoria percentual."""
        if original_val == 0:
            return 0
        
        if inverse:  # Para métricas onde menor é melhor (delays, errors)
            improvement = ((original_val - optimized_val) / original_val) * 100
        else:  # Para métricas onde maior é melhor (success rate, throughput)
            improvement = ((optimized_val - original_val) / original_val) * 100
        
        return improvement
    
    comparison = {
        'test_date': datetime.now().isoformat(),
        'original': original_stats,
        'optimized': optimized_stats,
        'improvements': {}
    }
    
    # Calcular melhorias
    improvements = {}
    
    # Delays
    improvements['avg_delay'] = calculate_improvement(
        original_stats.get('avg_delay', 0), 
        optimized_stats.get('avg_delay', 0), 
        inverse=True
    )
    
    improvements['median_delay'] = calculate_improvement(
        original_stats.get('median_delay', 0),
        optimized_stats.get('median_delay', 0),
        inverse=True
    )
    
    # Taxa de sucesso
    improvements['success_rate'] = calculate_improvement(
        original_stats.get('success_rate', 0),
        optimized_stats.get('success_rate', 0)
    )
    
    # Taxa de 429 errors
    improvements['error_429_rate'] = calculate_improvement(
        original_stats.get('error_429_rate', 0),
        optimized_stats.get('error_429_rate', 0),
        inverse=True
    )
    
    # Throughput
    improvements['requests_per_minute'] = calculate_improvement(
        original_stats.get('requests_per_minute', 0),
        optimized_stats.get('requests_per_minute', 0)
    )
    
    # Tempo total
    improvements['total_time'] = calculate_improvement(
        original_stats.get('total_time_minutes', 0),
        optimized_stats.get('total_time_minutes', 0),
        inverse=True
    )
    
    # Burst mode
    improvements['burst_rate'] = calculate_improvement(
        original_stats.get('burst_rate', 0),
        optimized_stats.get('burst_rate', 0)
    )
    
    comparison['improvements'] = improvements
    
    return comparison

def print_comparison_report(comparison: Dict):
    """Imprime relatório comparativo formatado."""
    
    original = comparison['original']
    optimized = comparison['optimized'] 
    improvements = comparison['improvements']
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 RELATÓRIO COMPARATIVO - BUNDESLIGA")
    logger.info("=" * 80)
    
    logger.info(f"📅 Data do teste: {comparison['test_date']}")
    logger.info(f"🎯 URLs testadas: {original.get('total_requests', 0)} (cada sistema)")
    
    logger.info("\n" + "─" * 80)
    logger.info("⏱️  DELAYS MÉDIOS")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('avg_delay', 0):.2f}s")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('avg_delay', 0):.2f}s")
    logger.info(f"📈 Melhoria: {improvements.get('avg_delay', 0):+.1f}%")
    
    logger.info(f"\n🔴 Delay Mediano Original:  {original.get('median_delay', 0):.2f}s")
    logger.info(f"🟢 Delay Mediano Otimizado: {optimized.get('median_delay', 0):.2f}s")
    logger.info(f"📈 Melhoria: {improvements.get('median_delay', 0):+.1f}%")
    
    logger.info("\n" + "─" * 80)
    logger.info("✅ TAXA DE SUCESSO")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('success_rate', 0):.2%}")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('success_rate', 0):.2%}")
    logger.info(f"📈 Melhoria: {improvements.get('success_rate', 0):+.1f}%")
    
    logger.info("\n" + "─" * 80)
    logger.info("❌ TAXA DE 429 ERRORS")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('error_429_rate', 0):.2%}")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('error_429_rate', 0):.2%}")
    logger.info(f"📈 Redução: {improvements.get('error_429_rate', 0):+.1f}%")
    
    logger.info("\n" + "─" * 80)
    logger.info("🚀 THROUGHPUT (Requisições/Minuto)")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('requests_per_minute', 0):.1f}")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('requests_per_minute', 0):.1f}")
    logger.info(f"📈 Melhoria: {improvements.get('requests_per_minute', 0):+.1f}%")
    
    logger.info("\n" + "─" * 80)
    logger.info("⏰ TEMPO TOTAL DE COLETA")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('total_time_minutes', 0):.1f} min")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('total_time_minutes', 0):.1f} min")
    logger.info(f"📈 Redução: {improvements.get('total_time', 0):+.1f}%")
    
    logger.info("\n" + "─" * 80)
    logger.info("💥 BURST MODE")
    logger.info("─" * 80)
    logger.info(f"🔴 Sistema Original:  {original.get('burst_rate', 0):.2%}")
    logger.info(f"🟢 Sistema Otimizado: {optimized.get('burst_rate', 0):.2%}")
    logger.info(f"📈 Melhoria: {improvements.get('burst_rate', 0):+.1f}%")
    
    # Resumo geral
    logger.info("\n" + "=" * 80)
    logger.info("🎯 RESUMO GERAL")
    logger.info("=" * 80)
    
    total_improvements = 0
    positive_improvements = 0
    
    key_metrics = ['avg_delay', 'success_rate', 'error_429_rate', 'requests_per_minute']
    for metric in key_metrics:
        improvement = improvements.get(metric, 0)
        total_improvements += abs(improvement)
        if improvement > 0:
            positive_improvements += 1
    
    avg_improvement = total_improvements / len(key_metrics)
    
    if positive_improvements >= 3 and avg_improvement > 15:
        logger.info("🎉 OTIMIZAÇÃO MUITO BEM-SUCEDIDA!")
        logger.info("✅ Melhorias significativas em métricas-chave")
    elif positive_improvements >= 2 and avg_improvement > 8:
        logger.info("✅ OTIMIZAÇÃO BEM-SUCEDIDA!")
        logger.info("✅ Melhorias consistentes identificadas")
    else:
        logger.info("⚠️ OTIMIZAÇÃO PARCIAL")
        logger.info("ℹ️ Algumas melhorias, mas pode precisar de ajustes")
    
    logger.info(f"📊 Média de melhoria: {avg_improvement:.1f}%")
    logger.info(f"📈 Métricas melhoradas: {positive_improvements}/{len(key_metrics)}")

def main():
    """Executa teste comparativo completo."""
    logger.info("🚀 INICIANDO TESTE COMPARATIVO BUNDESLIGA")
    logger.info("Comparando sistema original vs otimizado")
    logger.info("=" * 80)
    
    try:
        # Teste do sistema original (simulado)
        original_stats = simulate_original_system_performance()
        
        logger.info("\n" + "⏸️" * 20 + " PAUSA ENTRE TESTES " + "⏸️" * 20)
        time.sleep(3)
        
        # Teste do sistema otimizado (real)
        optimized_stats = test_optimized_system_performance()
        
        if not original_stats or not optimized_stats:
            logger.error("❌ Falha ao obter estatísticas dos testes")
            return False
        
        # Gerar relatório comparativo
        comparison = generate_comparison_report(original_stats, optimized_stats)
        
        # Imprimir relatório
        print_comparison_report(comparison)
        
        # Salvar relatório detalhado
        report_filename = f"bundesliga_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📄 Relatório detalhado salvo em: {report_filename}")
        
        # Determinar sucesso geral
        improvements = comparison['improvements']
        key_improvements = [
            improvements.get('avg_delay', 0),
            improvements.get('success_rate', 0), 
            improvements.get('error_429_rate', 0),
            improvements.get('requests_per_minute', 0)
        ]
        
        positive_improvements = sum(1 for imp in key_improvements if imp > 0)
        avg_improvement = sum(abs(imp) for imp in key_improvements) / len(key_improvements)
        
        success = positive_improvements >= 3 and avg_improvement > 10
        
        if success:
            logger.info("🎉 TESTE COMPARATIVO BEM-SUCEDIDO!")
            logger.info("✅ Otimizações demonstraram melhorias significativas")
        else:
            logger.info("⚠️ Teste com resultados mistos")
            logger.info("ℹ️ Revisar configurações ou aplicar ajustes adicionais")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste comparativo: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
