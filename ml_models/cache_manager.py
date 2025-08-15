#!/usr/bin/env python3
"""
Sistema de cache inteligente para otimizar operações de Machine Learning
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union
from pathlib import Path
import logging
from functools import wraps
import time

from .config import get_ml_config

logger = logging.getLogger(__name__)

class MLCacheManager:
    """Gerenciador de cache para operações de ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'expired': 0,
            'total_requests': 0
        }
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Gera uma chave única para o cache baseada nos argumentos"""
        # Converter argumentos para string e criar hash
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Retorna o caminho do arquivo de cache"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Verifica se o cache ainda é válido"""
        if not cache_file.exists():
            return False
        
        # Verificar TTL
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(hours=self.config.cache_ttl_hours)
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Recupera dados do cache"""
        if not self.config.enable_caching:
            return None
        
        self._cache_stats['total_requests'] += 1
        cache_file = self._get_cache_file_path(cache_key)
        
        if not self._is_cache_valid(cache_file):
            if cache_file.exists():
                self._cache_stats['expired'] += 1
                cache_file.unlink()  # Remover cache expirado
            self._cache_stats['misses'] += 1
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self._cache_stats['hits'] += 1
                logger.debug(f"Cache hit para chave: {cache_key}")
                return cached_data
        except Exception as e:
            logger.warning(f"Erro ao ler cache {cache_key}: {e}")
            self._cache_stats['misses'] += 1
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, cache_key: str, data: Any) -> bool:
        """Armazena dados no cache"""
        if not self.config.enable_caching:
            return False
        
        try:
            cache_file = self._get_cache_file_path(cache_key)
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Dados armazenados no cache: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Erro ao armazenar cache {cache_key}: {e}")
            return False
    
    def invalidate(self, cache_key: str) -> bool:
        """Invalida um item específico do cache"""
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Cache invalidado: {cache_key}")
            return True
        return False
    
    def clear_all(self) -> bool:
        """Limpa todo o cache"""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            logger.info("Todo o cache foi limpo")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do cache"""
        stats = self._cache_stats.copy()
        if stats['total_requests'] > 0:
            stats['hit_rate'] = round((stats['hits'] / stats['total_requests']) * 100, 2)
        else:
            stats['hit_rate'] = 0
        return stats
    
    def cleanup_expired(self) -> int:
        """Remove todos os caches expirados"""
        removed_count = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            if not self._is_cache_valid(cache_file):
                cache_file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"{removed_count} arquivos de cache expirados foram removidos")
        
        return removed_count

# Instância global do cache manager
cache_manager = MLCacheManager()

def cache_result(ttl_hours: Optional[int] = None):
    """Decorator para cachear resultados de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            cache_key = cache_manager._generate_cache_key(func.__name__, *args, **kwargs)
            
            # Tentar recuperar do cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            
            # Usar TTL personalizado se especificado
            if ttl_hours is not None:
                original_ttl = cache_manager.config.cache_ttl_hours
                cache_manager.config.cache_ttl_hours = ttl_hours
                cache_manager.set(cache_key, result)
                cache_manager.config.cache_ttl_hours = original_ttl
            else:
                cache_manager.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

def timed_cache_result(ttl_hours: int = 24):
    """Decorator para cachear resultados com TTL específico"""
    return cache_result(ttl_hours=ttl_hours)

# Funções utilitárias
def get_cache_stats() -> Dict[str, int]:
    """Retorna estatísticas do cache"""
    return cache_manager.get_stats()

def clear_ml_cache() -> bool:
    """Limpa todo o cache de ML"""
    return cache_manager.clear_all()

def cleanup_expired_cache() -> int:
    """Remove caches expirados"""
    return cache_manager.cleanup_expired()
