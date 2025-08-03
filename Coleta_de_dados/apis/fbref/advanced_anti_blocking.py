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
        
        # Padrões de tráfego por horário
        self.traffic_patterns = {
            TrafficPattern.PEAK_HOURS: RequestPattern(
                base_delay=8.0,
                variance=4.0,
                burst_probability=0.1,
                pause_probability=0.3,
                pause_duration=(30.0, 120.0)
            ),
            TrafficPattern.OFF_HOURS: RequestPattern(
                base_delay=4.0,
                variance=2.0,
                burst_probability=0.2,
                pause_probability=0.15,
                pause_duration=(10.0, 60.0)
            ),
            TrafficPattern.WEEKEND: RequestPattern(
                base_delay=6.0,
                variance=3.0,
                burst_probability=0.15,
                pause_probability=0.2,
                pause_duration=(20.0, 90.0)
            ),
            TrafficPattern.NIGHT: RequestPattern(
                base_delay=12.0,
                variance=6.0,
                burst_probability=0.05,
                pause_probability=0.4,
                pause_duration=(60.0, 300.0)
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
        """Calcula delay inteligente baseado em padrões e histórico."""
        pattern = self.get_current_traffic_pattern()
        config = self.traffic_patterns[pattern]
        
        # Delay base com variação
        base_delay = config.base_delay + random.uniform(-config.variance, config.variance)
        base_delay = max(1.0, base_delay)  # Mínimo 1 segundo
        
        # Ajustar baseado no histórico de bloqueios desta URL
        if url in self.blocking_analysis.blocked_urls:
            block_count = self.blocking_analysis.blocked_urls[url]
            # Aumentar delay exponencialmente para URLs problemáticas
            base_delay *= (1.5 ** min(block_count, 5))
        
        # Ajustar baseado na taxa de sucesso recente
        success_rate = self.get_recent_success_rate()
        if success_rate < 0.5:  # Taxa de sucesso baixa
            base_delay *= 2.0
        elif success_rate < 0.7:
            base_delay *= 1.5
        
        # Ajustar baseado no tempo desde a última requisição
        if last_request_time:
            time_since_last = (datetime.now() - last_request_time).total_seconds()
            if time_since_last < 2.0:  # Requisições muito próximas
                base_delay *= 2.0
        
        # Simular pausas humanas
        if random.random() < config.pause_probability:
            pause_duration = random.uniform(*config.pause_duration)
            logger.info(f"Simulando pausa humana: {pause_duration:.1f}s")
            base_delay += pause_duration
        
        return base_delay
    
    def should_use_burst_mode(self) -> bool:
        """Determina se deve usar modo rajada (várias requisições rápidas)."""
        pattern = self.get_current_traffic_pattern()
        config = self.traffic_patterns[pattern]
        
        # Só usar burst se a taxa de sucesso for alta
        success_rate = self.get_recent_success_rate()
        if success_rate < 0.8:
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
        self.request_history.append({
            'url': url,
            'success': success,
            'timestamp': timestamp,
            'response_time': response_time,
            'status_code': status_code
        })
        
        # Atualizar contadores
        self.requests_this_session += 1
        if success:
            self.successful_requests += 1
        else:
            self.blocked_requests += 1
            
            # Registrar bloqueio para análise
            if status_code == 429:
                self.blocking_analysis.blocked_urls[url] = \
                    self.blocking_analysis.blocked_urls.get(url, 0) + 1
                self.blocking_analysis.blocked_times.append(timestamp)
                
                # Analisar padrão de bloqueio
                hour_pattern = f"hour_{timestamp.hour}"
                self.blocking_analysis.blocked_patterns[hour_pattern] = \
                    self.blocking_analysis.blocked_patterns.get(hour_pattern, 0) + 1
    
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
    
    def reset_session(self):
        """Reinicia a sessão para nova identidade."""
        logger.info("Reiniciando sessão - nova identidade")
        self.session_start = datetime.now()
        self.requests_this_session = 0
        self.successful_requests = 0
        self.blocked_requests = 0
        
        # Manter histórico de bloqueios para análise, mas limpar contadores
        # Não resetar blocking_analysis completamente para manter aprendizado

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
