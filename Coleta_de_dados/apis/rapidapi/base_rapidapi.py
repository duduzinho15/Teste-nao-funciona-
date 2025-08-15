#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLASSE BASE PARA APIS RAPIDAPI
==============================

Classe base que implementa as funções padronizadas para todas as APIs do RapidAPI.
Fornece funcionalidades comuns como autenticação, rate limiting, retry e logging.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import aiohttp
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class RapidAPIConfig:
    nome: str
    host: str
    endpoint_base: str
    chaves: List[str]
    limite_requisicoes_dia: int
    limite_requisicoes_minuto: int
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class CacheEntry:
    def __init__(self, data: Any, timestamp: float, ttl: int = 3600):
        self.data = data
        self.timestamp = timestamp
        self.ttl = ttl  # Time to live em segundos
    
    def is_valid(self) -> bool:
        return time.time() - self.timestamp < self.ttl

class RapidAPICache:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém um item do cache se ainda for válido"""
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_valid():
                self._cache_stats["hits"] += 1
                return entry.data
            else:
                # Item expirado, remove do cache
                del self._cache[key]
                self._cache_stats["evictions"] += 1
        
        self._cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, data: Any, ttl: int = 3600):
        """Armazena um item no cache com TTL"""
        self._cache[key] = CacheEntry(data, time.time(), ttl)
    
    def clear(self):
        """Limpa todo o cache"""
        self._cache.clear()
        self._cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            **self._cache_stats,
            "size": len(self._cache),
            "hit_rate": self._cache_stats["hits"] / max(1, self._cache_stats["hits"] + self._cache_stats["misses"])
        }

class RapidAPIBase(ABC):
    def __init__(self, config: RapidAPIConfig):
        self.config = config
        self.logger = logging.getLogger(f"rapidapi.{config.nome}")
        self._current_key_index = 0
        self._request_counts = {"daily": 0, "minute": 0}
        self._last_request_time = 0
        self._cache = RapidAPICache()
        
        # Reset contadores diários à meia-noite
        self._schedule_daily_reset()
    
    def _schedule_daily_reset(self):
        """Agenda reset dos contadores diários"""
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        delay = (next_midnight - now).total_seconds()
        
        asyncio.create_task(self._delayed_reset(delay))
    
    async def _delayed_reset(self, delay: float):
        """Executa reset após delay"""
        await asyncio.sleep(delay)
        self._request_counts["daily"] = 0
        self._schedule_daily_reset()
    
    def _get_next_api_key(self) -> str:
        """Rotaciona entre as chaves da API disponíveis"""
        if not self.config.chaves:
            raise ValueError("Nenhuma chave de API configurada")
        
        key = self.config.chaves[self._current_key_index]
        self._current_key_index = (self._current_key_index + 1) % len(self.config.chaves)
        return key
    
    def _check_rate_limits(self) -> bool:
        """Verifica se os limites de rate foram atingidos"""
        now = time.time()
        
        # Reset contador de minuto se necessário
        if now - self._last_request_time >= 60:
            self._request_counts["minute"] = 0
        
        # Verifica limites
        if (self._request_counts["daily"] >= self.config.limite_requisicoes_dia or
            self._request_counts["minute"] >= self.config.limite_requisicoes_minuto):
            return False
        
        return True
    
    def _update_request_counts(self):
        """Atualiza contadores de requisições"""
        now = time.time()
        
        if now - self._last_request_time >= 60:
            self._request_counts["minute"] = 0
        
        self._request_counts["daily"] += 1
        self._request_counts["minute"] += 1
        self._last_request_time = now
    
    async def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None, 
                           headers: Optional[Dict[str, Any]] = None, 
                           cache_key: Optional[str] = None, cache_ttl: int = 3600) -> Optional[Dict[str, Any]]:
        """Faz uma requisição HTTP com cache, rate limiting e retry"""
        
        # Verifica cache primeiro
        if cache_key:
            cached_data = self._cache.get(cache_key)
            if cached_data is not None:
                self.logger.info(f"Cache hit para {cache_key}")
                return cached_data
        
        # Verifica rate limits
        if not self._check_rate_limits():
            self.logger.warning("Rate limit atingido")
            return None
        
        # Prepara headers
        if headers is None:
            headers = {}
        
        headers.update({
            "X-RapidAPI-Key": self._get_next_api_key(),
            "X-RapidAPI-Host": self.config.host
        })
        
        # Faz requisição com retry
        for attempt in range(self.config.retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Atualiza contadores
                            self._update_request_counts()
                            
                            # Armazena no cache se especificado
                            if cache_key:
                                self._cache.set(cache_key, data, cache_ttl)
                                self.logger.info(f"Dados armazenados no cache: {cache_key}")
                            
                            return data
                        
                        elif response.status == 403:
                            error_data = await response.json()
                            self.logger.error(f"Erro na requisição: {response.status} - {error_data}")
                            if "You are not subscribed to this API" in str(error_data):
                                self.logger.error("API não inscrita - verificar subscrição")
                            return None
                        
                        elif response.status == 429:
                            error_data = await response.json()
                            self.logger.warning(f"Rate limit atingido: {error_data}")
                            return None
                        
                        else:
                            self.logger.error(f"Erro na requisição: {response.status} - {await response.text()}")
                            
            except Exception as e:
                self.logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    self.logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                    return None
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return self._cache.get_stats()
    
    def clear_cache(self):
        """Limpa o cache"""
        self._cache.clear()
        self.logger.info("Cache limpo")
    
    # Métodos abstratos que devem ser implementados pelas classes filhas
    @abstractmethod
    async def coletar_jogos(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta jogos da API"""
        pass
    
    @abstractmethod
    async def coletar_jogadores(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta jogadores da API"""
        pass
    
    @abstractmethod
    async def coletar_ligas(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta ligas da API"""
        pass
    
    @abstractmethod
    async def coletar_estatisticas(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta estatísticas da API"""
        pass
    
    @abstractmethod
    async def coletar_odds(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta odds da API"""
        pass
    
    @abstractmethod
    async def coletar_noticias(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta notícias da API"""
        pass
