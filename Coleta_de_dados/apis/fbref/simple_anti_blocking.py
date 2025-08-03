#!/usr/bin/env python3
"""
Sistema Anti-Bloqueio Simplificado e Confiável

Versão simplificada que funciona sem travamentos, focada em:
- Delays inteligentes mas limitados
- Rotação de User-Agents
- Timeouts agressivos
- Fallback rápido
"""

import time
import random
import logging
from datetime import datetime
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class SimpleAntiBlocking:
    """Sistema anti-bloqueio simplificado e confiável."""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        self.last_request_time = None
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0
        
        logger.info("Sistema anti-bloqueio simplificado inicializado")
    
    def get_smart_delay(self) -> float:
        """Calcula delay inteligente mas sempre limitado."""
        base_delay = 3.0  # Delay base de 3 segundos
        
        # Aumentar delay se muitas falhas consecutivas
        if self.consecutive_failures > 0:
            failure_multiplier = min(self.consecutive_failures * 0.5, 3.0)  # Máximo 3x
            base_delay += failure_multiplier
        
        # Adicionar variação aleatória
        variation = random.uniform(-0.5, 1.0)
        delay = base_delay + variation
        
        # SEMPRE limitar delay máximo
        max_delay = 8.0  # Máximo 8 segundos
        delay = max(1.0, min(delay, max_delay))
        
        return delay
    
    def get_random_user_agent(self) -> str:
        """Retorna User-Agent aleatório."""
        return random.choice(self.user_agents)
    
    def should_wait(self) -> float:
        """Determina se deve aguardar e por quanto tempo."""
        if self.last_request_time is None:
            return 0.0
        
        time_since_last = time.time() - self.last_request_time
        min_interval = 2.0  # Mínimo 2 segundos entre requisições
        
        if time_since_last < min_interval:
            return min_interval - time_since_last
        
        return 0.0
    
    def create_session(self) -> requests.Session:
        """Cria sessão otimizada com timeouts agressivos."""
        session = requests.Session()
        
        # Configurar retry strategy mais agressiva
        retry_strategy = Retry(
            total=2,  # Apenas 2 tentativas
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers básicos
        session.headers.update({
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        })
        
        return session
    
    def make_request(self, url: str) -> Optional[requests.Response]:
        """Faz requisição com proteções anti-bloqueio."""
        
        # Aguardar se necessário
        wait_time = self.should_wait()
        if wait_time > 0:
            logger.debug(f"Aguardando {wait_time:.2f}s antes da requisição")
            time.sleep(wait_time)
        
        # Delay inteligente
        smart_delay = self.get_smart_delay()
        logger.debug(f"Aplicando delay inteligente: {smart_delay:.2f}s")
        time.sleep(smart_delay)
        
        self.total_requests += 1
        self.last_request_time = time.time()
        
        try:
            session = self.create_session()
            
            # Timeout MUITO agressivo para evitar travamentos
            timeout = (5, 10)  # 5s para conectar, 10s para ler
            
            logger.debug(f"Fazendo requisição para {url} com timeout {timeout}")
            
            response = session.get(url, timeout=timeout)
            
            if response.status_code == 200:
                self.successful_requests += 1
                self.consecutive_failures = 0
                logger.debug(f"Requisição bem-sucedida: {url}")
                return response
            
            elif response.status_code == 429:
                self.consecutive_failures += 1
                logger.warning(f"Rate limit (429) para {url}")
                
                # Verificar Retry-After
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_seconds = min(int(retry_after), 30)  # Máximo 30s
                        logger.info(f"Aguardando Retry-After: {wait_seconds}s")
                        time.sleep(wait_seconds)
                    except ValueError:
                        pass
                
                return None
            
            else:
                self.consecutive_failures += 1
                logger.warning(f"Erro HTTP {response.status_code} para {url}")
                return None
                
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            logger.warning(f"Timeout na requisição para {url}")
            return None
            
        except requests.exceptions.ConnectionError:
            self.consecutive_failures += 1
            logger.warning(f"Erro de conexão para {url}")
            return None
            
        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"Erro inesperado na requisição para {url}: {e}")
            return None
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do sistema."""
        success_rate = self.successful_requests / max(1, self.total_requests)
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'success_rate': success_rate,
            'consecutive_failures': self.consecutive_failures
        }

# Instância global
_simple_anti_blocking = None

def get_simple_anti_blocking() -> SimpleAntiBlocking:
    """Retorna instância global do sistema anti-bloqueio simplificado."""
    global _simple_anti_blocking
    if _simple_anti_blocking is None:
        _simple_anti_blocking = SimpleAntiBlocking()
    return _simple_anti_blocking

def make_safe_request(url: str) -> Optional[requests.Response]:
    """Função de conveniência para fazer requisição segura."""
    system = get_simple_anti_blocking()
    return system.make_request(url)

def get_anti_blocking_stats() -> dict:
    """Função de conveniência para obter estatísticas."""
    system = get_simple_anti_blocking()
    return system.get_stats()
