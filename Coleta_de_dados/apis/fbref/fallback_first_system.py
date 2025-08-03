#!/usr/bin/env python3
"""
Sistema Fallback-First para FBRef

Sistema que prioriza fallback e só tenta requisições reais em condições muito controladas.
Evita travamentos priorizando dados em cache/fallback.
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class FallbackFirstSystem:
    """Sistema que prioriza fallback sobre requisições reais."""
    
    def __init__(self):
        self.last_successful_request = None
        self.consecutive_failures = 0
        self.total_attempts = 0
        self.successful_attempts = 0
        self.fallback_mode = False
        self.fallback_until = None
        
        logger.info("Sistema Fallback-First inicializado")
    
    def should_attempt_real_request(self, url: str) -> bool:
        """Determina se deve tentar requisição real ou usar fallback."""
        
        # Se estamos em modo fallback temporário
        if self.fallback_mode and self.fallback_until:
            if datetime.now() < self.fallback_until:
                logger.debug("Em modo fallback temporário - não fazendo requisição real")
                return False
            else:
                # Sair do modo fallback
                self.fallback_mode = False
                self.fallback_until = None
                logger.info("Saindo do modo fallback temporário")
        
        # Se muitas falhas consecutivas, entrar em modo fallback
        if self.consecutive_failures >= 3:
            self._enter_fallback_mode(minutes=10)
            return False
        
        # Se taxa de sucesso muito baixa, usar fallback
        if self.total_attempts > 5:
            success_rate = self.successful_attempts / self.total_attempts
            if success_rate < 0.3:  # Menos de 30% de sucesso
                self._enter_fallback_mode(minutes=15)
                return False
        
        # Limitar tentativas por tempo
        if self.last_successful_request:
            time_since_success = datetime.now() - self.last_successful_request
            if time_since_success > timedelta(minutes=30):
                # Muito tempo sem sucesso - usar fallback
                self._enter_fallback_mode(minutes=20)
                return False
        
        return True
    
    def _enter_fallback_mode(self, minutes: int):
        """Entra em modo fallback por um período."""
        self.fallback_mode = True
        self.fallback_until = datetime.now() + timedelta(minutes=minutes)
        logger.warning(f"Entrando em modo fallback por {minutes} minutos")
    
    def make_safe_request(self, url: str, timeout_seconds: int = 10) -> Optional[requests.Response]:
        """Faz requisição com timeout rigoroso usando threading."""
        
        if not self.should_attempt_real_request(url):
            return None
        
        logger.debug(f"Tentando requisição real para: {url}")
        
        # Usar threading para garantir timeout
        result = {'response': None, 'error': None}
        
        def make_request():
            try:
                session = requests.Session()
                
                # Retry strategy muito conservadora
                retry_strategy = Retry(
                    total=1,  # Apenas 1 tentativa
                    backoff_factor=0,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # Headers básicos
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive'
                })
                
                # Timeout muito agressivo
                response = session.get(url, timeout=(3, 5))  # 3s conectar, 5s ler
                result['response'] = response
                
            except Exception as e:
                result['error'] = str(e)
        
        # Executar em thread com timeout
        thread = threading.Thread(target=make_request, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)
        
        self.total_attempts += 1
        
        if thread.is_alive():
            # Thread ainda rodando - timeout
            logger.warning(f"Timeout na requisição para {url} após {timeout_seconds}s")
            self.consecutive_failures += 1
            return None
        
        if result['error']:
            # Erro na requisição
            logger.warning(f"Erro na requisição para {url}: {result['error']}")
            self.consecutive_failures += 1
            return None
        
        if result['response'] and result['response'].status_code == 200:
            # Sucesso!
            logger.debug(f"Requisição bem-sucedida para {url}")
            self.successful_attempts += 1
            self.consecutive_failures = 0
            self.last_successful_request = datetime.now()
            return result['response']
        
        elif result['response'] and result['response'].status_code == 429:
            # Rate limiting
            logger.warning(f"Rate limit (429) para {url}")
            self.consecutive_failures += 1
            self._enter_fallback_mode(minutes=30)  # Fallback longo para 429
            return None
        
        else:
            # Outros erros
            status = result['response'].status_code if result['response'] else 'None'
            logger.warning(f"Erro HTTP {status} para {url}")
            self.consecutive_failures += 1
            return None
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do sistema."""
        success_rate = self.successful_attempts / max(1, self.total_attempts)
        
        return {
            'total_attempts': self.total_attempts,
            'successful_attempts': self.successful_attempts,
            'success_rate': success_rate,
            'consecutive_failures': self.consecutive_failures,
            'fallback_mode': self.fallback_mode,
            'fallback_until': self.fallback_until.isoformat() if self.fallback_until else None,
            'last_successful_request': self.last_successful_request.isoformat() if self.last_successful_request else None
        }
    
    def force_fallback_mode(self, minutes: int = 60):
        """Força modo fallback por um período específico."""
        self._enter_fallback_mode(minutes)
        logger.info(f"Modo fallback forçado por {minutes} minutos")

# Instância global
_fallback_first_system = None

def get_fallback_first_system() -> FallbackFirstSystem:
    """Retorna instância global do sistema fallback-first."""
    global _fallback_first_system
    if _fallback_first_system is None:
        _fallback_first_system = FallbackFirstSystem()
    return _fallback_first_system

def should_use_fallback(url: str) -> bool:
    """Verifica se deve usar fallback em vez de requisição real."""
    system = get_fallback_first_system()
    return not system.should_attempt_real_request(url)

def make_controlled_request(url: str) -> Optional[requests.Response]:
    """Faz requisição controlada com fallback automático."""
    system = get_fallback_first_system()
    return system.make_safe_request(url)

def get_fallback_stats() -> dict:
    """Retorna estatísticas do sistema fallback-first."""
    system = get_fallback_first_system()
    return system.get_stats()

def force_fallback_mode(minutes: int = 60):
    """Força o sistema a usar apenas fallback por um período."""
    system = get_fallback_first_system()
    system.force_fallback_mode(minutes)
