#!/usr/bin/env python3
"""
Sistema Avançado Anti-Bloqueio para FBRef

Implementa estratégias sofisticadas para contornar bloqueios 429:
- Delays dinâmicos baseados em padrões de tráfego
- Distribuição temporal de requisições
- Simulação de comportamento humano
- Rotação de sessões e identidades
- Análise de padrões de bloqueio
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class TrafficPattern(Enum):
    """Padrões de tráfego para simulação humana."""
    PEAK_HOURS = "peak_hours"      # Horários de pico (mais lento)
    OFF_HOURS = "off_hours"        # Horários alternativos (mais rápido)
    WEEKEND = "weekend"            # Fins de semana (padrão diferente)
    NIGHT = "night"                # Madrugada (muito lento)

@dataclass
class RequestPattern:
    """Padrão de requisição para simulação humana."""
    base_delay: float
    variance: float
    burst_probability: float
    pause_probability: float
    pause_duration: Tuple[float, float]

@dataclass
class BlockingAnalysis:
    """Análise de padrões de bloqueio."""
    blocked_urls: Dict[str, int] = field(default_factory=dict)
    blocked_times: List[datetime] = field(default_factory=list)
    blocked_patterns: Dict[str, int] = field(default_factory=dict)
    success_patterns: Dict[str, int] = field(default_factory=dict)
    last_analysis: Optional[datetime] = None

class AdvancedAntiBlocking:
    """Sistema avançado para contornar bloqueios do FBRef."""
    
    def __init__(self):
        self.blocking_analysis = BlockingAnalysis()
        self.request_history = deque(maxlen=1000)
        self.session_start = datetime.now()
        self.requests_this_session = 0
        self.successful_requests = 0
        self.blocked_requests = 0
        
        # NOVO: Sistema de aprendizado adaptativo por horário
        self.hourly_blocking_stats = defaultdict(lambda: {'blocks': 0, 'requests': 0, 'last_updated': None})
        self.adaptive_multipliers = {}  # Cache de multiplicadores por horário
        
        # Padrões de tráfego por horário - OTIMIZADO para reduzir delays
        self.traffic_patterns = {
            TrafficPattern.PEAK_HOURS: RequestPattern(
                base_delay=6.0,  # Reduzido de 8.0 para 6.0 (25% redução)
                variance=3.0,    # Reduzido de 4.0 para 3.0
                burst_probability=0.15,  # Aumentado de 0.1 para 0.15
                pause_probability=0.2,   # Reduzido de 0.3 para 0.2
                pause_duration=(20.0, 80.0)  # Reduzido de (30.0, 120.0)
            ),
            TrafficPattern.OFF_HOURS: RequestPattern(
                base_delay=2.0,  # REDUÇÃO AGRESSIVA: 4.0 -> 2.0 (50% redução)
                variance=1.0,    # Reduzido de 2.0 para 1.0
                burst_probability=0.35,  # Aumentado de 0.2 para 0.35
                pause_probability=0.08,  # Reduzido de 0.15 para 0.08
                pause_duration=(5.0, 25.0)  # Reduzido de (10.0, 60.0)
            ),
            TrafficPattern.WEEKEND: RequestPattern(
                base_delay=3.0,  # Reduzido de 6.0 para 3.0 (50% redução)
                variance=1.5,    # Reduzido de 3.0 para 1.5
                burst_probability=0.25,  # Aumentado de 0.15 para 0.25
                pause_probability=0.12,  # Reduzido de 0.2 para 0.12
                pause_duration=(8.0, 40.0)  # Reduzido de (20.0, 90.0)
            ),
            TrafficPattern.NIGHT: RequestPattern(
                base_delay=4.0,  # REDUÇÃO AGRESSIVA: 12.0 -> 4.0 (67% redução)
                variance=2.0,    # Reduzido de 6.0 para 2.0
                burst_probability=0.2,   # Aumentado de 0.05 para 0.2
                pause_probability=0.15,  # Reduzido de 0.4 para 0.15
                pause_duration=(15.0, 60.0)  # Reduzido de (60.0, 300.0)
            )
        }
        
        logger.info("Sistema avançado anti-bloqueio inicializado")
    
    def get_current_traffic_pattern(self) -> TrafficPattern:
        """Determina o padrão de tráfego atual baseado no horário."""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        
        # Madrugada (0-6h)
        if 0 <= hour <= 6:
            return TrafficPattern.NIGHT
        
        # Fins de semana
        if weekday >= 5:  # Sábado e Domingo
            return TrafficPattern.WEEKEND
        
        # Horários de pico (8-18h em dias úteis)
        if 8 <= hour <= 18:
            return TrafficPattern.PEAK_HOURS
        
        # Horários alternativos
        return TrafficPattern.OFF_HOURS
    
    def calculate_smart_delay(self, url: str, last_request_time: Optional[datetime] = None) -> float:
        """Calcula delay inteligente baseado em padrões e histórico - OTIMIZADO."""
        pattern = self.get_current_traffic_pattern()
        config = self.traffic_patterns[pattern]
        
        # Delay base com variação
        base_delay = config.base_delay + random.uniform(-config.variance, config.variance)
        base_delay = max(0.5, base_delay)  # OTIMIZADO: Mínimo reduzido para 0.5s
        
        # OTIMIZADO: Penalidade menos agressiva para URLs problemáticas
        if url in self.blocking_analysis.blocked_urls:
            block_count = self.blocking_analysis.blocked_urls[url]
            # Penalidade reduzida: 1.5^x -> 1.2^x e cap em 3
            base_delay *= (1.2 ** min(block_count, 3))
        
        # OTIMIZADO: Taxa de sucesso menos punitiva com bonus para alta performance
        success_rate = self.get_recent_success_rate()
        if success_rate < 0.3:  # Apenas para taxa MUITO baixa
            base_delay *= 1.4  # Reduzido de 2.0x para 1.4x
        elif success_rate < 0.6:  # Faixa intermediária
            base_delay *= 1.2  # Reduzido de 1.5x para 1.2x
        elif success_rate > 0.8:  # NOVO: Bonus para alta taxa de sucesso
            base_delay *= 0.7  # 30% de redução para alta performance
        
        # OTIMIZADO: Ajuste temporal mais flexível
        if last_request_time:
            time_since_last = (datetime.now() - last_request_time).total_seconds()
            if time_since_last < 1.0:  # Reduzido de 2.0s para 1.0s
                base_delay *= 1.3  # Reduzido de 2.0x para 1.3x
        
        # OTIMIZADO: Pausas humanas adaptativas por horário
        hour = datetime.now().hour
        is_low_traffic = (0 <= hour <= 8) or (19 <= hour <= 23)
        
        pause_prob = config.pause_probability
        if is_low_traffic:
            pause_prob *= 0.5  # 50% menos pausas em horários de baixo tráfego
            
        if random.random() < pause_prob:
            pause_duration = random.uniform(*config.pause_duration)
            if is_low_traffic:
                pause_duration *= 0.6  # Pausas 40% mais curtas
            logger.info(f"Simulando pausa humana: {pause_duration:.1f}s ({'low-traffic' if is_low_traffic else 'normal'})")
            base_delay += pause_duration
        
        # Log detalhado para monitoramento
        logger.debug(f"Delay calculado: {base_delay:.2f}s (pattern: {pattern.value}, success_rate: {success_rate:.2f})")
        
        return base_delay
    
    def should_use_burst_mode(self) -> bool:
        """Determina se deve usar modo rajada (várias requisições rápidas)."""
        pattern = self.get_current_traffic_pattern()
        config = self.traffic_patterns[pattern]
        
        # OTIMIZADO: Threshold reduzido de 80% para 75% para burst mode mais agressivo
        success_rate = self.get_recent_success_rate()
        if success_rate < 0.75:
            return False
        
        return random.random() < config.burst_probability
    
    def get_recent_success_rate(self, window_minutes: int = 30) -> float:
        """Calcula taxa de sucesso recente."""
        if not self.request_history:
            return 1.0
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_requests = [
            req for req in self.request_history 
            if req['timestamp'] >= cutoff_time
        ]
        
        if not recent_requests:
            return 1.0
        
        successful = sum(1 for req in recent_requests if req['success'])
        return successful / len(recent_requests)
    
    def record_request_result(self, url: str, success: bool, response_time: float = 0.0, 
                            status_code: Optional[int] = None):
        """Registra resultado de uma requisição para análise."""
        timestamp = datetime.now()
        
        # Registrar no histórico
        request_record = {
            'url': url,
            'success': success,
            'timestamp': timestamp,
            'response_time': response_time,
            'status_code': status_code,
            'traffic_pattern': self.get_current_traffic_pattern().value
        }
        self.request_history.append(request_record)
        
        # NOVO: Atualizar estatísticas por horário para aprendizado adaptativo
        hour = timestamp.hour
        self.hourly_blocking_stats[hour]['requests'] += 1
        self.hourly_blocking_stats[hour]['last_updated'] = timestamp
        
        # Atualizar contadores da sessão
        self.requests_this_session += 1
        if success:
            self.successful_requests += 1
        else:
            self.blocked_requests += 1
            
            # NOVO: Registrar bloqueio por horário
            self.hourly_blocking_stats[hour]['blocks'] += 1
            
            # Registrar bloqueio para análise
            if url not in self.blocking_analysis.blocked_urls:
                self.blocking_analysis.blocked_urls[url] = 0
            self.blocking_analysis.blocked_urls[url] += 1
            self.blocking_analysis.blocked_times.append(timestamp)
            
            # Analisar padrão de bloqueio
            pattern_key = f"{timestamp.hour}h_{timestamp.weekday()}d"
            if pattern_key not in self.blocking_analysis.blocked_patterns:
                self.blocking_analysis.blocked_patterns[pattern_key] = 0
            self.blocking_analysis.blocked_patterns[pattern_key] += 1
        
        # NOVO: Invalidar cache de multiplicadores adaptativos quando há mudanças
        if hour in self.adaptive_multipliers:
            del self.adaptive_multipliers[hour]
        
        logger.debug(f"Resultado registrado: {url} - {'Sucesso' if success else 'Falha'} ({response_time:.2f}s)")
    
    def get_optimal_request_time(self) -> datetime:
        """Sugere o melhor horário para fazer requisições baseado no histórico."""
        if not self.blocking_analysis.blocked_times:
            return datetime.now()
        
        # Analisar horários com menos bloqueios
        hour_blocks = defaultdict(int)
        for blocked_time in self.blocking_analysis.blocked_times[-100:]:  # Últimos 100 bloqueios
            hour_blocks[blocked_time.hour] += 1
        
        # Encontrar horário com menos bloqueios
        if hour_blocks:
            best_hours = sorted(range(24), key=lambda h: hour_blocks.get(h, 0))
            best_hour = best_hours[0]
            
            now = datetime.now()
            optimal_time = now.replace(hour=best_hour, minute=0, second=0, microsecond=0)
            
            # Se o horário já passou hoje, agendar para amanhã
            if optimal_time <= now:
                optimal_time += timedelta(days=1)
            
            return optimal_time
        
        return datetime.now()
    
    def should_switch_identity(self) -> bool:
        """Determina se deve trocar identidade (proxy, headers, etc.)."""
        # Trocar identidade se muitos bloqueios recentes
        recent_blocks = sum(1 for req in list(self.request_history)[-20:] if not req['success'])
        
        if recent_blocks >= 5:  # 5 ou mais bloqueios nos últimos 20 requests
            return True
        
        # Trocar identidade periodicamente para evitar detecção
        if self.requests_this_session > 0 and self.requests_this_session % 50 == 0:
            return True
        
        return False
    
    def get_session_statistics(self) -> Dict:
        """Retorna estatísticas da sessão atual."""
        session_duration = (datetime.now() - self.session_start).total_seconds()
        success_rate = self.successful_requests / max(1, self.requests_this_session)
        
        return {
            'session_duration_minutes': session_duration / 60,
            'total_requests': self.requests_this_session,
            'successful_requests': self.successful_requests,
            'blocked_requests': self.blocked_requests,
            'success_rate': success_rate,
            'requests_per_minute': self.requests_this_session / max(1, session_duration / 60),
            'current_traffic_pattern': self.get_current_traffic_pattern().value,
            'recent_success_rate': self.get_recent_success_rate()
        }
    
    def analyze_blocking_patterns(self) -> Dict:
        """Analisa padrões de bloqueio para otimização."""
        if not self.blocking_analysis.blocked_times:
            return {'message': 'Nenhum bloqueio registrado ainda'}
        
        # Análise por horário
        hour_analysis = defaultdict(int)
        for blocked_time in self.blocking_analysis.blocked_times:
            hour_analysis[blocked_time.hour] += 1
        
        # Encontrar melhores e piores horários
        best_hours = sorted(hour_analysis.keys(), key=lambda h: hour_analysis[h])[:3]
        worst_hours = sorted(hour_analysis.keys(), key=lambda h: hour_analysis[h], reverse=True)[:3]
        
        # URLs mais problemáticas
        problematic_urls = sorted(
            self.blocking_analysis.blocked_urls.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_blocks': len(self.blocking_analysis.blocked_times),
            'best_hours': best_hours,
            'worst_hours': worst_hours,
            'problematic_urls': problematic_urls,
            'blocking_patterns': dict(self.blocking_analysis.blocked_patterns),
            'optimal_request_time': self.get_optimal_request_time().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_adaptive_multiplier_for_hour(self) -> float:
        """NOVO: Calcula multiplicador adaptativo baseado no histórico de bloqueios do horário atual."""
        current_hour = datetime.now().hour
        
        # Usar cache se disponível e recente
        if current_hour in self.adaptive_multipliers:
            return self.adaptive_multipliers[current_hour]
        
        # Calcular multiplicador baseado nas estatísticas do horário
        stats = self.hourly_blocking_stats[current_hour]
        
        if stats['requests'] < 10:  # Dados insuficientes
            multiplier = 1.0
        else:
            # Taxa de bloqueio para este horário
            block_rate = stats['blocks'] / stats['requests']
            
            if block_rate <= 0.05:  # Muito baixa (≤5%)
                multiplier = 0.8  # Reduzir delay em 20%
            elif block_rate <= 0.10:  # Baixa (≤10%)
                multiplier = 0.9  # Reduzir delay em 10%
            elif block_rate <= 0.20:  # Normal (≤20%)
                multiplier = 1.0  # Sem alteração
            elif block_rate <= 0.35:  # Alta (≤35%)
                multiplier = 1.3  # Aumentar delay em 30%
            else:  # Muito alta (>35%)
                multiplier = 1.6  # Aumentar delay em 60%
        
        # Cache do resultado
        self.adaptive_multipliers[current_hour] = multiplier
        
        logger.debug(f"Multiplicador adaptativo para hora {current_hour}: {multiplier:.2f} (taxa bloqueio: {stats['blocks']}/{stats['requests']})")
        return multiplier
    
    def get_hourly_blocking_analysis(self) -> Dict:
        """NOVO: Retorna análise detalhada de bloqueios por horário."""
        analysis = {}
        
        for hour in range(24):
            stats = self.hourly_blocking_stats[hour]
            if stats['requests'] > 0:
                block_rate = stats['blocks'] / stats['requests']
                analysis[f"hour_{hour:02d}"] = {
                    'requests': stats['requests'],
                    'blocks': stats['blocks'],
                    'block_rate': block_rate,
                    'risk_level': self._get_risk_level(block_rate),
                    'last_updated': stats['last_updated'].isoformat() if stats['last_updated'] else None
                }
        
        return analysis
    
    def _get_risk_level(self, block_rate: float) -> str:
        """NOVO: Determina nível de risco baseado na taxa de bloqueio."""
        if block_rate <= 0.05:
            return "VERY_LOW"
        elif block_rate <= 0.10:
            return "LOW"
        elif block_rate <= 0.20:
            return "MODERATE"
        elif block_rate <= 0.35:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def reset_session(self):
        """Reinicia a sessão para nova identidade."""
        logger.info("Reiniciando sessão - nova identidade")
        self.session_start = datetime.now()
        self.requests_this_session = 0
        self.successful_requests = 0
        self.blocked_requests = 0
        
        # Manter histórico de bloqueios para análise, mas limpar contadores
        # Não resetar blocking_analysis completamente para manter aprendizado
        # NOVO: Manter também as estatísticas horárias para aprendizado contínuo

# Instância global
_advanced_anti_blocking = None

def get_advanced_anti_blocking() -> AdvancedAntiBlocking:
    """Retorna instância global do sistema anti-bloqueio avançado."""
    global _advanced_anti_blocking
    if _advanced_anti_blocking is None:
        _advanced_anti_blocking = AdvancedAntiBlocking()
    return _advanced_anti_blocking

def calculate_intelligent_delay(url: str, last_request_time: Optional[datetime] = None) -> float:
    """Função de conveniência para calcular delay inteligente."""
    system = get_advanced_anti_blocking()
    return system.calculate_smart_delay(url, last_request_time)

def record_fbref_request(url: str, success: bool, response_time: float = 0.0, 
                        status_code: Optional[int] = None):
    """Função de conveniência para registrar resultado de requisição."""
    system = get_advanced_anti_blocking()
    system.record_request_result(url, success, response_time, status_code)

def should_change_identity() -> bool:
    """Função de conveniência para verificar se deve trocar identidade."""
    system = get_advanced_anti_blocking()
    return system.should_switch_identity()

def get_blocking_analysis() -> Dict:
    """Função de conveniência para obter análise de bloqueios."""
    system = get_advanced_anti_blocking()
    return system.analyze_blocking_patterns()

def get_session_stats() -> Dict:
    """Função de conveniência para obter estatísticas da sessão."""
    system = get_advanced_anti_blocking()
    return system.get_session_statistics()

def get_hourly_analysis() -> Dict:
    """NOVO: Função de conveniência para obter análise horária."""
    system = get_advanced_anti_blocking()
    return system.get_hourly_blocking_analysis()

def log_optimization_metrics():
    """NOVO: Log detalhado das métricas de otimização."""
    system = get_advanced_anti_blocking()
    
    # Estatísticas da sessão
    session_stats = system.get_session_statistics()
    logger.info(f"=== MÉTRICAS DE OTIMIZAÇÃO ===")
    logger.info(f"Taxa de sucesso: {session_stats['success_rate']:.2%}")
    logger.info(f"Requisições/min: {session_stats['requests_per_minute']:.1f}")
    logger.info(f"Padrão atual: {session_stats['current_traffic_pattern']}")
    
    # Análise horária
    hourly_analysis = system.get_hourly_blocking_analysis()
    current_hour = datetime.now().hour
    
    if f"hour_{current_hour:02d}" in hourly_analysis:
        hour_data = hourly_analysis[f"hour_{current_hour:02d}"]
        logger.info(f"Hora atual ({current_hour}h): {hour_data['block_rate']:.2%} bloqueios - Nível {hour_data['risk_level']}")
    
    # Multiplicador adaptativo
    adaptive_mult = system.get_adaptive_multiplier_for_hour()
    logger.info(f"Multiplicador adaptativo: {adaptive_mult:.2f}x")
    
    # Melhores e piores horários
    if hourly_analysis:
        sorted_hours = sorted(hourly_analysis.items(), key=lambda x: x[1]['block_rate'])
        best_hours = sorted_hours[:3]
        worst_hours = sorted_hours[-3:]
        
        logger.info(f"Melhores horários: {[h[0] for h in best_hours]}")
        logger.info(f"Piores horários: {[h[0] for h in worst_hours]}")
