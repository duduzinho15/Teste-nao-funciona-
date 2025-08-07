#!/usr/bin/env python3
"""
Sistema de Rotação de IP/Proxies para evitar detecção e bloqueios.

Suporta proxies residenciais e de datacenter com rotação inteligente.
"""

import logging
import random
import time
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Informações de um proxy."""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http, https, socks5
    is_residential: bool = False
    last_used: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    is_blocked: bool = False
    response_time: float = 0.0

    @property
    def proxy_url(self) -> str:
        """Retorna URL do proxy formatada."""
        if self.username and self.password:
            return f"{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.proxy_type}://{self.host}:{self.port}"
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso do proxy."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    def record_success(self, response_time: float = 0.0):
        """Registra uso bem-sucedido."""
        self.success_count += 1
        self.last_used = datetime.now()
        self.response_time = response_time
        self.is_blocked = False
    
    def record_failure(self):
        """Registra falha."""
        self.failure_count += 1
        self.last_used = datetime.now()
        
        # Marcar como bloqueado se muitas falhas
        if self.failure_count >= 5 and self.success_rate < 0.3:
            self.is_blocked = True
            logger.warning(f"Proxy {self.host}:{self.port} marcado como bloqueado")

class ProxyRotationSystem:
    """
    Sistema de rotação de proxies com inteligência anti-detecção.
    
    Características:
    - Rotação inteligente baseada em performance
    - Detecção automática de proxies bloqueados
    - Priorização de proxies residenciais
    - Cooldown entre usos do mesmo proxy
    """
    
    def __init__(self):
        self.proxies: List[ProxyInfo] = []
        self.current_proxy_index = 0
        self.min_cooldown_minutes = 5  # Mínimo entre usos do mesmo proxy
        self.max_failures_before_block = 3
        self.lock = threading.Lock()
        
        logger.info("Sistema de rotacao de proxies inicializado")
    
    def add_proxy(self, host: str, port: int, username: str = None, password: str = None, 
                  proxy_type: str = "http", is_residential: bool = False):
        """Adiciona um proxy ao pool."""
        proxy = ProxyInfo(
            host=host,
            port=port,
            username=username,
            password=password,
            proxy_type=proxy_type,
            is_residential=is_residential
        )
        
        with self.lock:
            self.proxies.append(proxy)
        
        proxy_desc = "residencial" if is_residential else "datacenter"
        logger.info(f"Proxy {proxy_desc} adicionado: {host}:{port}")
    
    def load_proxies_from_config(self, config: Dict):
        """Carrega proxies de configuração."""
        if 'proxies' not in config:
            logger.info("Nenhum proxy configurado - usando conexao direta")
            return
        
        for proxy_config in config['proxies']:
            self.add_proxy(
                host=proxy_config['host'],
                port=proxy_config['port'],
                username=proxy_config.get('username'),
                password=proxy_config.get('password'),
                proxy_type=proxy_config.get('type', 'http'),
                is_residential=proxy_config.get('residential', False)
            )
        
        logger.info(f"Carregados {len(self.proxies)} proxies da configuracao")
    
    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """
        Seleciona o próximo proxy para uso.
        
        Algoritmo:
        1. Filtra proxies não bloqueados
        2. Prioriza proxies residenciais
        3. Considera cooldown e taxa de sucesso
        4. Rotaciona de forma inteligente
        
        Returns:
            ProxyInfo ou None se não há proxies disponíveis
        """
        with self.lock:
            if not self.proxies:
                return None
            
            # Filtrar proxies disponíveis (não bloqueados e fora do cooldown)
            available_proxies = []
            now = datetime.now()
            
            for proxy in self.proxies:
                if proxy.is_blocked:
                    continue
                
                # Verificar cooldown
                if proxy.last_used:
                    time_since_use = now - proxy.last_used
                    if time_since_use < timedelta(minutes=self.min_cooldown_minutes):
                        continue
                
                available_proxies.append(proxy)
            
            if not available_proxies:
                logger.warning("Nenhum proxy disponivel - todos em cooldown ou bloqueados")
                return None
            
            # Ordenar por prioridade: residenciais primeiro, depois por taxa de sucesso
            available_proxies.sort(key=lambda p: (
                not p.is_residential,  # Residenciais primeiro (False < True)
                -p.success_rate,       # Maior taxa de sucesso primeiro
                p.failure_count        # Menos falhas primeiro
            ))
            
            # Selecionar com alguma aleatoriedade entre os melhores
            top_proxies = available_proxies[:min(3, len(available_proxies))]
            selected_proxy = random.choice(top_proxies)
            
            logger.debug(f"Proxy selecionado: {selected_proxy.host}:{selected_proxy.port} "
                        f"(residencial: {selected_proxy.is_residential}, "
                        f"taxa_sucesso: {selected_proxy.success_rate:.2f})")
            
            return selected_proxy
    
    def get_proxy_dict(self, proxy: ProxyInfo) -> Dict[str, str]:
        """
        Converte ProxyInfo para formato dict usado pelo requests.
        
        Args:
            proxy: Informações do proxy
            
        Returns:
            Dict no formato {'http': 'proxy_url', 'https': 'proxy_url'}
        """
        proxy_url = proxy.proxy_url
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def test_proxy(self, proxy: ProxyInfo, test_url: str = "http://httpbin.org/ip", 
                   timeout: int = 10) -> bool:
        """
        Testa se um proxy está funcionando.
        
        Args:
            proxy: Proxy para testar
            test_url: URL para teste
            timeout: Timeout em segundos
            
        Returns:
            bool: True se proxy funciona
        """
        try:
            start_time = time.time()
            
            response = requests.get(
                test_url,
                proxies=self.get_proxy_dict(proxy),
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                proxy.record_success(response_time)
                logger.debug(f"Proxy {proxy.host}:{proxy.port} OK ({response_time:.2f}s)")
                return True
            else:
                proxy.record_failure()
                logger.warning(f"Proxy {proxy.host}:{proxy.port} retornou {response.status_code}")
                return False
                
        except Exception as e:
            proxy.record_failure()
            logger.warning(f"Proxy {proxy.host}:{proxy.port} falhou: {e}")
            return False
    
    def test_all_proxies(self) -> Dict[str, bool]:
        """
        Testa todos os proxies do pool.
        
        Returns:
            Dict com resultados dos testes
        """
        logger.info("Testando todos os proxies...")
        results = {}
        
        for proxy in self.proxies:
            if proxy.is_blocked:
                results[f"{proxy.host}:{proxy.port}"] = False
                continue
            
            is_working = self.test_proxy(proxy)
            results[f"{proxy.host}:{proxy.port}"] = is_working
        
        working_count = sum(1 for working in results.values() if working)
        logger.info(f"Teste concluido: {working_count}/{len(self.proxies)} proxies funcionando")
        
        return results
    
    def record_proxy_result(self, proxy: ProxyInfo, success: bool, response_time: float = 0.0):
        """Registra resultado de uso de um proxy."""
        if success:
            proxy.record_success(response_time)
        else:
            proxy.record_failure()
    
    def get_proxy_stats(self) -> Dict:
        """Retorna estatísticas dos proxies."""
        with self.lock:
            total_proxies = len(self.proxies)
            working_proxies = sum(1 for p in self.proxies if not p.is_blocked)
            residential_proxies = sum(1 for p in self.proxies if p.is_residential and not p.is_blocked)
            
            avg_success_rate = 0.0
            if self.proxies:
                avg_success_rate = sum(p.success_rate for p in self.proxies) / len(self.proxies)
            
            return {
                'total_proxies': total_proxies,
                'working_proxies': working_proxies,
                'blocked_proxies': total_proxies - working_proxies,
                'residential_proxies': residential_proxies,
                'datacenter_proxies': working_proxies - residential_proxies,
                'average_success_rate': avg_success_rate,
                'proxies_detail': [
                    {
                        'host': p.host,
                        'port': p.port,
                        'type': 'residential' if p.is_residential else 'datacenter',
                        'success_rate': p.success_rate,
                        'is_blocked': p.is_blocked,
                        'last_used': p.last_used.isoformat() if p.last_used else None
                    }
                    for p in self.proxies
                ]
            }
    
    def unblock_all_proxies(self):
        """Desbloqueia todos os proxies (para reset)."""
        with self.lock:
            for proxy in self.proxies:
                proxy.is_blocked = False
                proxy.failure_count = 0
        
        logger.info("Todos os proxies desbloqueados")
    
    def has_available_proxies(self) -> bool:
        """Verifica se há proxies disponíveis."""
        return self.get_next_proxy() is not None

# Configuração de exemplo para proxies
EXAMPLE_PROXY_CONFIG = {
    "proxies": [
        # Exemplo de proxies residenciais (mais caros, mas mais eficazes)
        {
            "host": "residential-proxy1.example.com",
            "port": 8080,
            "username": "user1",
            "password": "pass1",
            "type": "http",
            "residential": True
        },
        # Exemplo de proxies de datacenter (mais baratos)
        {
            "host": "datacenter-proxy1.example.com", 
            "port": 3128,
            "type": "http",
            "residential": False
        }
    ]
}
