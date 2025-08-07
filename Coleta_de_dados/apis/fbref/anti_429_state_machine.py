#!/usr/bin/env python3
"""
Máquina de Estados Anti-429 para Scraping Resiliente do FBRef.

Estados: NOMINAL → THROTTLED → RECONFIGURING → HALTED
"""

import logging
import time
import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ScrapingState(Enum):
    """Estados da máquina de estados anti-429."""
    NOMINAL = "NOMINAL"           # Operação normal
    THROTTLED = "THROTTLED"       # Rate limited, aguardando
    RECONFIGURING = "RECONFIGURING"  # Mudando identidade
    HALTED = "HALTED"            # Parado por bloqueio severo

@dataclass
class StateMetrics:
    """Métricas do estado atual."""
    requests_made: int = 0
    errors_429: int = 0
    errors_connection: int = 0
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None
    current_delay: float = 2.0
    consecutive_failures: int = 0
    identity_changes: int = 0

class Anti429StateMachine:
    """
    Máquina de estados para scraping resiliente anti-429.
    
    Implementa o modelo descrito no documento "Erro 429 Scraping FBREF.md":
    - NOMINAL: Operação padrão com delays aleatórios
    - THROTTLED: Rate limited, aplicando backoff exponencial
    - RECONFIGURING: Mudando identidade (IP, User-Agent, sessão)
    - HALTED: Bloqueio severo, requer intervenção
    """
    
    def __init__(self):
        self.state = ScrapingState.NOMINAL
        self.metrics = StateMetrics()
        self.state_history = []
        self.max_consecutive_failures = 5
        self.max_identity_changes = 10
        
        # Configurações de delays
        self.base_delay = 2.0
        self.max_delay = 60.0
        self.random_factor = 0.5
        
        logger.info("Maquina de estados anti-429 inicializada em estado NOMINAL")
    
    def get_current_state(self) -> ScrapingState:
        """Retorna o estado atual."""
        return self.state
    
    def get_metrics(self) -> StateMetrics:
        """Retorna métricas atuais."""
        return self.metrics
    
    def calculate_delay(self) -> float:
        """
        Calcula delay baseado no estado atual.
        
        Returns:
            float: Tempo de delay em segundos
        """
        if self.state == ScrapingState.NOMINAL:
            # Delay aleatório normal (2-5 segundos)
            base = self.base_delay
            variation = base * self.random_factor
            return random.uniform(base, base + variation * 2)
        
        elif self.state == ScrapingState.THROTTLED:
            # OTIMIZADO: Backoff menos agressivo para recovery mais rápido
            # Reduzido de 2^x para 1.6^x e cap reduzido
            exponential_delay = self.base_delay * (1.6 ** min(self.metrics.consecutive_failures, 4))
            capped_delay = min(exponential_delay, self.max_delay * 0.6)  # Cap reduzido para 60%
            
            # Adiciona aleatoriedade para evitar padrões
            variation = capped_delay * 0.2  # Reduzido de 0.3 para 0.2
            return random.uniform(capped_delay, capped_delay + variation)
        
        elif self.state == ScrapingState.RECONFIGURING:
            # Delay maior durante reconfiguração
            return random.uniform(10.0, 20.0)
        
        else:  # HALTED
            return 0.0  # Não deve fazer requisições
    
    def record_success(self, url: str):
        """Registra uma requisição bem-sucedida."""
        self.metrics.requests_made += 1
        self.metrics.last_success = datetime.now()
        self.metrics.consecutive_failures = 0
        self.metrics.current_delay = self.base_delay
        
        # Se estava em estado de erro, volta para NOMINAL
        if self.state in [ScrapingState.THROTTLED, ScrapingState.RECONFIGURING]:
            logger.info(f"Sucesso apos {self.state.value} - voltando para NOMINAL")
            self._transition_to(ScrapingState.NOMINAL)
        
        logger.debug(f"Sucesso registrado: {url} (total: {self.metrics.requests_made})")
    
    def record_429_error(self, url: str, retry_after: Optional[int] = None):
        """Registra erro 429 (rate limiting)."""
        self.metrics.errors_429 += 1
        self.metrics.last_error = datetime.now()
        self.metrics.consecutive_failures += 1
        
        logger.warning(f"Erro 429 detectado: {url} (consecutivos: {self.metrics.consecutive_failures})")
        
        # Determinar próximo estado
        if self.state == ScrapingState.NOMINAL:
            # Primeira detecção de rate limiting
            self._transition_to(ScrapingState.THROTTLED)
            if retry_after:
                self.metrics.current_delay = max(retry_after, self.calculate_delay())
        
        elif self.state == ScrapingState.THROTTLED:
            # Rate limiting persistente
            if self.metrics.consecutive_failures >= 3:
                logger.warning("Rate limiting persistente - mudando identidade")
                self._transition_to(ScrapingState.RECONFIGURING)
            else:
                # Aumentar delay no estado THROTTLED
                self.metrics.current_delay = self.calculate_delay()
        
        elif self.state == ScrapingState.RECONFIGURING:
            # Falha mesmo após reconfiguração
            if self.metrics.identity_changes >= self.max_identity_changes:
                logger.error("Multiplas falhas apos reconfiguracoes - HALT")
                self._transition_to(ScrapingState.HALTED)
    
    def record_connection_error(self, url: str, error_type: str):
        """Registra erro de conexão."""
        self.metrics.errors_connection += 1
        self.metrics.last_error = datetime.now()
        self.metrics.consecutive_failures += 1
        
        logger.warning(f"Erro de conexao ({error_type}): {url}")
        
        # Tratar como rate limiting se muitos erros consecutivos
        if self.metrics.consecutive_failures >= 3:
            if self.state == ScrapingState.NOMINAL:
                self._transition_to(ScrapingState.THROTTLED)
            elif self.state == ScrapingState.THROTTLED:
                self._transition_to(ScrapingState.RECONFIGURING)
    
    def request_identity_change(self) -> bool:
        """
        Solicita mudança de identidade (IP, User-Agent, sessão).
        
        Returns:
            bool: True se deve mudar identidade, False se deve parar
        """
        if self.state != ScrapingState.RECONFIGURING:
            return False
        
        self.metrics.identity_changes += 1
        
        if self.metrics.identity_changes >= self.max_identity_changes:
            logger.error("Limite de mudancas de identidade atingido")
            self._transition_to(ScrapingState.HALTED)
            return False
        
        logger.info(f"Mudanca de identidade #{self.metrics.identity_changes}")
        
        # Reset algumas métricas após mudança de identidade
        self.metrics.consecutive_failures = 0
        self.metrics.current_delay = self.base_delay
        
        # Volta para NOMINAL após reconfiguração
        self._transition_to(ScrapingState.NOMINAL)
        
        return True
    
    def should_continue_scraping(self) -> bool:
        """
        Verifica se deve continuar fazendo scraping.
        
        Returns:
            bool: True se deve continuar, False se deve parar
        """
        if self.state == ScrapingState.HALTED:
            return False
        
        # Verifica se há muitas falhas consecutivas
        if self.metrics.consecutive_failures >= self.max_consecutive_failures:
            logger.error("Muitas falhas consecutivas - recomendando parada")
            return False
        
        return True
    
    def get_wait_time(self) -> float:
        """
        Retorna tempo de espera antes da próxima requisição.
        
        Returns:
            float: Tempo em segundos
        """
        return self.calculate_delay()
    
    def _transition_to(self, new_state: ScrapingState):
        """Transição entre estados."""
        old_state = self.state
        self.state = new_state
        
        # Registrar transição
        transition = {
            'from': old_state.value,
            'to': new_state.value,
            'timestamp': datetime.now(),
            'metrics': {
                'requests': self.metrics.requests_made,
                'errors_429': self.metrics.errors_429,
                'consecutive_failures': self.metrics.consecutive_failures
            }
        }
        self.state_history.append(transition)
        
        logger.info(f"Transicao de estado: {old_state.value} -> {new_state.value}")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Retorna resumo do estado atual."""
        return {
            'current_state': self.state.value,
            'requests_made': self.metrics.requests_made,
            'errors_429': self.metrics.errors_429,
            'errors_connection': self.metrics.errors_connection,
            'consecutive_failures': self.metrics.consecutive_failures,
            'identity_changes': self.metrics.identity_changes,
            'current_delay': self.metrics.current_delay,
            'last_success': self.metrics.last_success.isoformat() if self.metrics.last_success else None,
            'last_error': self.metrics.last_error.isoformat() if self.metrics.last_error else None,
            'should_continue': self.should_continue_scraping()
        }
    
    def reset_to_nominal(self):
        """Reset para estado NOMINAL (para testes ou reinicialização)."""
        logger.info("Reset manual para estado NOMINAL")
        self.state = ScrapingState.NOMINAL
        self.metrics.consecutive_failures = 0
        self.metrics.current_delay = self.base_delay
