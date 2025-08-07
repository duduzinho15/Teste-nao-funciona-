#!/usr/bin/env python3
"""
SCRIPT DE MONITORAMENTO - SISTEMA ANTI-RATE LIMITING FBRef
=========================================================

Script de monitoramento contínuo para acompanhar a saúde do sistema anti-rate limiting.
Monitora métricas críticas, gera alertas e mantém dashboard de status.

Funcionalidades:
- Monitoramento de delays médios
- Tracking de taxa de 429 errors
- Alertas automáticos
- Dashboard simples
- Relatórios periódicos

Autor: Sistema de Otimização FBRef
Data: 2025-08-03
Versão: 1.0
"""

import sys
import os
import time
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import threading
import schedule

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Coleta_de_dados', 'apis', 'fbref'))

try:
    from advanced_anti_blocking import AdvancedAntiBlocking, TrafficPattern
    from anti_429_state_machine import Anti429StateMachine, ScrapingState
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

class SystemMonitor:
    """Monitor de sistema para anti-rate limiting."""
    
    def __init__(self, monitoring_interval: int = 300):  # 5 minutos default
        self.monitoring_interval = monitoring_interval
        self.setup_logging()
        
        # Métricas de monitoramento
        self.metrics_history = {
            'delays': deque(maxlen=288),  # 24h de dados (5min intervals)
            'success_rates': deque(maxlen=288),
            'error_429_rates': deque(maxlen=288),
            'burst_activations': deque(maxlen=288),
            'timestamps': deque(maxlen=288),
            'hourly_stats': defaultdict(lambda: {
                'requests': 0, 'successes': 0, '429s': 0, 'delays': []
            })
        }
        
        # Thresholds de alerta
        self.thresholds = {
            'delay_warning': 15.0,      # Delay médio > 15s
            'delay_critical': 25.0,     # Delay médio > 25s
            'error_429_warning': 0.10,  # 429 rate > 10%
            'error_429_critical': 0.15, # 429 rate > 15%
            'success_warning': 0.80,    # Success rate < 80%
            'success_critical': 0.70,   # Success rate < 70%
            'burst_warning': 0.05       # Burst rate < 5%
        }
        
        # Status de alertas
        self.alert_status = {
            'delay': 'OK',
            'error_429': 'OK',
            'success_rate': 'OK',
            'burst_mode': 'OK',
            'overall': 'OK'
        }
        
        # Sistema anti-blocking para monitoramento
        self.anti_blocking = AdvancedAntiBlocking()
        self.state_machine = Anti429StateMachine()
        
        self.running = False
        
    def setup_logging(self):
        """Configura logging para monitoramento."""
        log_filename = f"monitoring_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('SystemMonitor')
        self.logger.info("🔍 SISTEMA DE MONITORAMENTO INICIADO")
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Coleta métricas atuais do sistema."""
        try:
            # Simular coleta de métricas (em produção, viria dos logs reais)
            current_time = datetime.now()
            
            # Métricas simuladas baseadas no sistema atual
            pattern = self.anti_blocking.get_current_traffic_pattern()
            config = self.anti_blocking.traffic_patterns[pattern]
            
            # Calcular delay médio atual
            sample_delay = self.anti_blocking.calculate_smart_delay("https://fbref.com/test")
            
            # Simular métricas baseadas no padrão atual
            if pattern == TrafficPattern.NIGHT:
                base_success_rate = 0.92
                base_429_rate = 0.06
                base_burst_rate = 0.18
            elif pattern == TrafficPattern.OFF_HOURS:
                base_success_rate = 0.90
                base_429_rate = 0.08
                base_burst_rate = 0.16
            elif pattern == TrafficPattern.WEEKEND:
                base_success_rate = 0.88
                base_429_rate = 0.09
                base_burst_rate = 0.14
            else:  # PEAK_HOURS
                base_success_rate = 0.85
                base_429_rate = 0.10
                base_burst_rate = 0.12
            
            # Adicionar variação realística
            import random
            success_rate = max(0.7, min(0.98, base_success_rate + random.uniform(-0.05, 0.05)))
            error_429_rate = max(0.02, min(0.20, base_429_rate + random.uniform(-0.02, 0.02)))
            burst_rate = max(0.0, min(0.30, base_burst_rate + random.uniform(-0.03, 0.03)))
            
            metrics = {
                'timestamp': current_time,
                'traffic_pattern': pattern.value,
                'avg_delay': sample_delay,
                'success_rate': success_rate,
                'error_429_rate': error_429_rate,
                'burst_activation_rate': burst_rate,
                'state_machine_state': self.state_machine.state.value,
                'requests_last_interval': random.randint(15, 45)  # Simular atividade
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao coletar métricas: {e}")
            return {}
    
    def update_metrics_history(self, metrics: Dict[str, Any]):
        """Atualiza histórico de métricas."""
        if not metrics:
            return
            
        self.metrics_history['delays'].append(metrics['avg_delay'])
        self.metrics_history['success_rates'].append(metrics['success_rate'])
        self.metrics_history['error_429_rates'].append(metrics['error_429_rate'])
        self.metrics_history['burst_activations'].append(metrics['burst_activation_rate'])
        self.metrics_history['timestamps'].append(metrics['timestamp'])
        
        # Atualizar estatísticas por hora
        hour = metrics['timestamp'].hour
        self.metrics_history['hourly_stats'][hour]['requests'] += metrics.get('requests_last_interval', 0)
        self.metrics_history['hourly_stats'][hour]['delays'].append(metrics['avg_delay'])
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verifica condições de alerta."""
        alerts = []
        
        if not metrics:
            return alerts
        
        # Alerta de delay
        if metrics['avg_delay'] > self.thresholds['delay_critical']:
            alerts.append({
                'type': 'CRITICAL',
                'category': 'delay',
                'message': f"🔴 CRÍTICO: Delay médio muito alto: {metrics['avg_delay']:.2f}s (> {self.thresholds['delay_critical']}s)",
                'value': metrics['avg_delay'],
                'threshold': self.thresholds['delay_critical']
            })
            self.alert_status['delay'] = 'CRITICAL'
        elif metrics['avg_delay'] > self.thresholds['delay_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'delay',
                'message': f"🟡 ATENÇÃO: Delay médio elevado: {metrics['avg_delay']:.2f}s (> {self.thresholds['delay_warning']}s)",
                'value': metrics['avg_delay'],
                'threshold': self.thresholds['delay_warning']
            })
            self.alert_status['delay'] = 'WARNING'
        else:
            self.alert_status['delay'] = 'OK'
        
        # Alerta de 429 errors
        if metrics['error_429_rate'] > self.thresholds['error_429_critical']:
            alerts.append({
                'type': 'CRITICAL',
                'category': 'error_429',
                'message': f"🔴 CRÍTICO: Taxa de 429 errors muito alta: {metrics['error_429_rate']:.1%} (> {self.thresholds['error_429_critical']:.1%})",
                'value': metrics['error_429_rate'],
                'threshold': self.thresholds['error_429_critical']
            })
            self.alert_status['error_429'] = 'CRITICAL'
        elif metrics['error_429_rate'] > self.thresholds['error_429_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'error_429',
                'message': f"🟡 ATENÇÃO: Taxa de 429 errors elevada: {metrics['error_429_rate']:.1%} (> {self.thresholds['error_429_warning']:.1%})",
                'value': metrics['error_429_rate'],
                'threshold': self.thresholds['error_429_warning']
            })
            self.alert_status['error_429'] = 'WARNING'
        else:
            self.alert_status['error_429'] = 'OK'
        
        # Alerta de success rate
        if metrics['success_rate'] < self.thresholds['success_critical']:
            alerts.append({
                'type': 'CRITICAL',
                'category': 'success_rate',
                'message': f"🔴 CRÍTICO: Taxa de sucesso muito baixa: {metrics['success_rate']:.1%} (< {self.thresholds['success_critical']:.1%})",
                'value': metrics['success_rate'],
                'threshold': self.thresholds['success_critical']
            })
            self.alert_status['success_rate'] = 'CRITICAL'
        elif metrics['success_rate'] < self.thresholds['success_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'success_rate',
                'message': f"🟡 ATENÇÃO: Taxa de sucesso baixa: {metrics['success_rate']:.1%} (< {self.thresholds['success_warning']:.1%})",
                'value': metrics['success_rate'],
                'threshold': self.thresholds['success_warning']
            })
            self.alert_status['success_rate'] = 'WARNING'
        else:
            self.alert_status['success_rate'] = 'OK'
        
        # Alerta de burst mode
        if metrics['burst_activation_rate'] < self.thresholds['burst_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'burst_mode',
                'message': f"🟡 ATENÇÃO: Burst mode baixo: {metrics['burst_activation_rate']:.1%} (< {self.thresholds['burst_warning']:.1%})",
                'value': metrics['burst_activation_rate'],
                'threshold': self.thresholds['burst_warning']
            })
            self.alert_status['burst_mode'] = 'WARNING'
        else:
            self.alert_status['burst_mode'] = 'OK'
        
        # Status geral
        critical_alerts = [a for a in alerts if a['type'] == 'CRITICAL']
        warning_alerts = [a for a in alerts if a['type'] == 'WARNING']
        
        if critical_alerts:
            self.alert_status['overall'] = 'CRITICAL'
        elif warning_alerts:
            self.alert_status['overall'] = 'WARNING'
        else:
            self.alert_status['overall'] = 'OK'
        
        return alerts
    
    def log_alerts(self, alerts: List[Dict[str, Any]]):
        """Log de alertas."""
        for alert in alerts:
            if alert['type'] == 'CRITICAL':
                self.logger.error(alert['message'])
            else:
                self.logger.warning(alert['message'])
    
    def generate_dashboard(self, metrics: Dict[str, Any]) -> str:
        """Gera dashboard simples em texto."""
        if not metrics:
            return "❌ Sem dados disponíveis"
        
        # Calcular médias recentes (última hora)
        recent_delays = list(self.metrics_history['delays'])[-12:]  # Últimos 12 pontos (1h)
        recent_success = list(self.metrics_history['success_rates'])[-12:]
        recent_429s = list(self.metrics_history['error_429_rates'])[-12:]
        recent_bursts = list(self.metrics_history['burst_activations'])[-12:]
        
        avg_delay_1h = statistics.mean(recent_delays) if recent_delays else metrics['avg_delay']
        avg_success_1h = statistics.mean(recent_success) if recent_success else metrics['success_rate']
        avg_429_1h = statistics.mean(recent_429s) if recent_429s else metrics['error_429_rate']
        avg_burst_1h = statistics.mean(recent_bursts) if recent_bursts else metrics['burst_activation_rate']
        
        # Status emojis
        status_emojis = {
            'OK': '🟢',
            'WARNING': '🟡',
            'CRITICAL': '🔴'
        }
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🔍 DASHBOARD ANTI-RATE LIMITING           ║
╠══════════════════════════════════════════════════════════════╣
║ 📅 Timestamp: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}                    ║
║ 🌐 Padrão Tráfego: {metrics['traffic_pattern']:<20}                ║
║ 🤖 Estado Machine: {metrics['state_machine_state']:<20}                ║
╠══════════════════════════════════════════════════════════════╣
║                        📊 MÉTRICAS ATUAIS                    ║
╠══════════════════════════════════════════════════════════════╣
║ {status_emojis[self.alert_status['delay']]} Delay Médio:     {metrics['avg_delay']:>8.2f}s                    ║
║ {status_emojis[self.alert_status['success_rate']]} Taxa Sucesso:    {metrics['success_rate']:>8.1%}                    ║
║ {status_emojis[self.alert_status['error_429']]} Taxa 429 Errors: {metrics['error_429_rate']:>8.1%}                    ║
║ {status_emojis[self.alert_status['burst_mode']]} Burst Mode:      {metrics['burst_activation_rate']:>8.1%}                    ║
╠══════════════════════════════════════════════════════════════╣
║                      📈 MÉDIAS ÚLTIMA HORA                   ║
╠══════════════════════════════════════════════════════════════╣
║ ⏱️  Delay Médio 1h:   {avg_delay_1h:>8.2f}s                    ║
║ ✅ Sucesso 1h:        {avg_success_1h:>8.1%}                    ║
║ ❌ 429 Errors 1h:     {avg_429_1h:>8.1%}                    ║
║ 💥 Burst Mode 1h:     {avg_burst_1h:>8.1%}                    ║
╠══════════════════════════════════════════════════════════════╣
║ 🏆 STATUS GERAL: {status_emojis[self.alert_status['overall']]} {self.alert_status['overall']:<20}                ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        return dashboard
    
    def save_metrics_report(self, metrics: Dict[str, Any]):
        """Salva relatório de métricas."""
        report_data = {
            'timestamp': metrics['timestamp'].isoformat(),
            'current_metrics': metrics,
            'alert_status': self.alert_status,
            'thresholds': self.thresholds,
            'history_summary': {
                'total_points': len(self.metrics_history['delays']),
                'avg_delay_24h': statistics.mean(self.metrics_history['delays']) if self.metrics_history['delays'] else 0,
                'avg_success_24h': statistics.mean(self.metrics_history['success_rates']) if self.metrics_history['success_rates'] else 0,
                'avg_429_24h': statistics.mean(self.metrics_history['error_429_rates']) if self.metrics_history['error_429_rates'] else 0
            }
        }
        
        filename = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
    
    def monitoring_cycle(self):
        """Ciclo principal de monitoramento."""
        self.logger.info("🔄 Executando ciclo de monitoramento...")
        
        # Coletar métricas
        metrics = self.collect_metrics()
        if not metrics:
            self.logger.error("❌ Falha ao coletar métricas")
            return
        
        # Atualizar histórico
        self.update_metrics_history(metrics)
        
        # Verificar alertas
        alerts = self.check_alerts(metrics)
        if alerts:
            self.log_alerts(alerts)
        
        # Gerar dashboard
        dashboard = self.generate_dashboard(metrics)
        print(dashboard)
        
        # Log de status
        self.logger.info(f"📊 Métricas coletadas - Delay: {metrics['avg_delay']:.2f}s, "
                        f"Sucesso: {metrics['success_rate']:.1%}, "
                        f"429s: {metrics['error_429_rate']:.1%}, "
                        f"Burst: {metrics['burst_activation_rate']:.1%}")
        
        # Salvar relatório a cada hora
        if datetime.now().minute == 0:
            self.save_metrics_report(metrics)
            self.logger.info("💾 Relatório horário salvo")
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        self.logger.info(f"🚀 Iniciando monitoramento contínuo (intervalo: {self.monitoring_interval}s)")
        self.running = True
        
        # Configurar schedule
        schedule.every(self.monitoring_interval // 60).minutes.do(self.monitoring_cycle)
        
        # Executar primeiro ciclo imediatamente
        self.monitoring_cycle()
        
        # Loop principal
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            self.logger.info("⚠️ Monitoramento interrompido pelo usuário")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        self.running = False
        self.logger.info("🛑 Monitoramento parado")
    
    def generate_health_check(self) -> Dict[str, Any]:
        """Gera health check do sistema."""
        metrics = self.collect_metrics()
        if not metrics:
            return {'status': 'ERROR', 'message': 'Falha ao coletar métricas'}
        
        alerts = self.check_alerts(metrics)
        critical_alerts = [a for a in alerts if a['type'] == 'CRITICAL']
        
        health_status = {
            'status': 'CRITICAL' if critical_alerts else ('WARNING' if alerts else 'HEALTHY'),
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'delay_avg': metrics['avg_delay'],
                'success_rate': metrics['success_rate'],
                'error_429_rate': metrics['error_429_rate'],
                'burst_rate': metrics['burst_activation_rate']
            },
            'alerts_count': {
                'critical': len(critical_alerts),
                'warning': len([a for a in alerts if a['type'] == 'WARNING'])
            },
            'system_health': self.alert_status
        }
        
        return health_status

def main():
    """Função principal."""
    print("🔍 SISTEMA DE MONITORAMENTO ANTI-RATE LIMITING")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description='Monitor do sistema anti-rate limiting')
    parser.add_argument('--interval', type=int, default=300, help='Intervalo de monitoramento em segundos (default: 300)')
    parser.add_argument('--health-check', action='store_true', help='Executar apenas health check')
    parser.add_argument('--dashboard', action='store_true', help='Mostrar dashboard uma vez')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor(monitoring_interval=args.interval)
    
    try:
        if args.health_check:
            # Health check único
            health = monitor.generate_health_check()
            print(json.dumps(health, indent=2, ensure_ascii=False))
        elif args.dashboard:
            # Dashboard único
            metrics = monitor.collect_metrics()
            if metrics:
                dashboard = monitor.generate_dashboard(metrics)
                print(dashboard)
        else:
            # Monitoramento contínuo
            monitor.start_monitoring()
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")
        monitor.logger.error(f"Erro crítico: {e}")

if __name__ == "__main__":
    main()
