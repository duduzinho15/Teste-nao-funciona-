#!/usr/bin/env python3
"""
Sistema de Cache Avançado para RapidAPI

Este módulo implementa:
- Cache distribuído com múltiplas camadas
- TTL inteligente baseado em padrões de uso
- Métricas avançadas de performance
- Limpeza automática otimizada
- Compressão de dados para economia de memória
"""

import asyncio
import json
import logging
import time
import hashlib
import pickle
import gzip
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import threading
import weakref

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Métricas avançadas do cache"""
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    expired: int = 0
    compressed: int = 0
    memory_usage_bytes: int = 0
    compression_ratio: float = 0.0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    average_ttl: float = 0.0
    last_cleanup: Optional[datetime] = None
    cleanup_count: int = 0
    
    def update_rates(self):
        """Atualiza taxas calculadas"""
        if self.total_requests > 0:
            self.hit_rate = (self.hits / self.total_requests) * 100
            self.miss_rate = (self.misses / self.total_requests) * 100

@dataclass
class CacheEntry:
    """Entrada do cache com metadados avançados"""
    key: str
    value: Any
    ttl: int  # Segundos
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    compressed: bool = False
    original_size: int = 0
    compressed_size: int = 0
    tags: List[str] = field(default_factory=list)
    priority: int = 1  # 1=baixa, 5=crítica
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    @property
    def age_seconds(self) -> float:
        """Idade da entrada em segundos"""
        return (datetime.now() - self.created_at).total_seconds()
    
    @property
    def time_to_live(self) -> float:
        """Tempo restante de vida em segundos"""
        return max(0, self.ttl - self.age_seconds)
    
    def access(self):
        """Registra acesso à entrada"""
        self.accessed_at = datetime.now()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "key": self.key,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "compressed": self.compressed,
            "original_size": self.original_size,
            "compressed_size": self.compressed_size,
            "tags": self.tags,
            "priority": self.priority,
            "is_expired": self.is_expired,
            "age_seconds": self.age_seconds,
            "time_to_live": self.time_to_live
        }

class AdvancedCacheManager:
    """Gerenciador de cache avançado"""
    
    def __init__(self, 
                 max_size: int = 10000,
                 default_ttl: int = 3600,
                 cleanup_interval: int = 300,
                 compression_threshold: int = 1024,
                 enable_compression: bool = True):
        
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        
        # Cache principal (LRU)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Cache de tags para busca rápida
        self.tag_index: Dict[str, set] = defaultdict(set)
        
        # Cache de prioridades
        self.priority_cache: Dict[int, List[str]] = defaultdict(list)
        
        # Métricas
        self.metrics = CacheMetrics()
        
        # Controle de limpeza
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Inicia limpeza automática
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Inicia tarefa de limpeza automática"""
        if not self.running:
            self.running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Loop de limpeza automática"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired()
                self.metrics.cleanup_count += 1
                self.metrics.last_cleanup = datetime.now()
                
            except Exception as e:
                logger.error(f"Erro na limpeza automática: {e}")
    
    def _compress_value(self, value: Any) -> Tuple[Any, bool, int, int]:
        """Comprime valor se necessário"""
        if not self.enable_compression:
            return value, False, 0, 0
        
        try:
            # Serializa valor
            serialized = pickle.dumps(value)
            original_size = len(serialized)
            
            # Comprime se acima do threshold
            if original_size > self.compression_threshold:
                compressed = gzip.compress(serialized)
                compressed_size = len(compressed)
                
                # Só usa se a compressão for efetiva
                if compressed_size < original_size * 0.8:
                    return compressed, True, original_size, compressed_size
            
            return value, False, original_size, len(serialized)
            
        except Exception as e:
            logger.warning(f"Erro ao comprimir valor: {e}")
            return value, False, 0, 0
    
    def _decompress_value(self, value: Any, compressed: bool) -> Any:
        """Descomprime valor se necessário"""
        if not compressed:
            return value
        
        try:
            # Descomprime
            decompressed = gzip.decompress(value)
            # Deserializa
            return pickle.loads(decompressed)
            
        except Exception as e:
            logger.error(f"Erro ao descomprimir valor: {e}")
            return None
    
    def set(self, 
            key: str, 
            value: Any, 
            ttl: Optional[int] = None, 
            tags: Optional[List[str]] = None,
            priority: int = 1) -> bool:
        """Define valor no cache"""
        try:
            with self._lock:
                # Remove entrada existente se houver
                if key in self.cache:
                    self._remove_entry(key)
                
                # Verifica limite de tamanho
                if len(self.cache) >= self.max_size:
                    self._evict_lru()
                
                # TTL padrão se não especificado
                if ttl is None:
                    ttl = self.default_ttl
                
                # Comprime valor se necessário
                compressed_value, is_compressed, orig_size, comp_size = self._compress_value(value)
                
                # Cria entrada
                entry = CacheEntry(
                    key=key,
                    value=compressed_value,
                    ttl=ttl,
                    created_at=datetime.now(),
                    accessed_at=datetime.now(),
                    compressed=is_compressed,
                    original_size=orig_size,
                    compressed_size=comp_size,
                    tags=tags or [],
                    priority=priority
                )
                
                # Adiciona ao cache
                self.cache[key] = entry
                
                # Atualiza índices
                self._update_indices(key, entry)
                
                # Atualiza métricas
                self.metrics.compressed += 1 if is_compressed else 0
                self.metrics.memory_usage_bytes += comp_size
                
                logger.debug(f"Cache SET: {key} (TTL: {ttl}s, Compressed: {is_compressed})")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao definir cache para {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        try:
            with self._lock:
                self.metrics.total_requests += 1
                
                if key not in self.cache:
                    self.metrics.misses += 1
                    return None
                
                entry = self.cache[key]
                
                # Verifica expiração
                if entry.is_expired:
                    self.metrics.expired += 1
                    self._remove_entry(key)
                    return None
                
                # Registra acesso
                entry.access()
                
                # Move para o final (LRU)
                self.cache.move_to_end(key)
                
                # Atualiza métricas
                self.metrics.hits += 1
                
                # Descomprime se necessário
                value = self._decompress_value(entry.value, entry.compressed)
                
                logger.debug(f"Cache HIT: {key} (Access count: {entry.access_count})")
                return value
                
        except Exception as e:
            logger.error(f"Erro ao recuperar cache para {key}: {e}")
            self.metrics.misses += 1
            return None
    
    def _remove_entry(self, key: str):
        """Remove entrada do cache"""
        if key in self.cache:
            entry = self.cache[key]
            
            # Remove dos índices
            for tag in entry.tags:
                if tag in self.tag_index:
                    self.tag_index[tag].discard(key)
            
            if entry.priority in self.priority_cache:
                self.priority_cache[entry.priority].remove(key)
            
            # Atualiza métricas de memória
            self.metrics.memory_usage_bytes -= entry.compressed_size
            
            # Remove do cache principal
            del self.cache[key]
    
    def _evict_lru(self):
        """Remove entrada menos recentemente usada"""
        if self.cache:
            # Remove a primeira entrada (LRU)
            key = next(iter(self.cache))
            self._remove_entry(key)
            logger.debug(f"Cache eviction: {key}")
    
    def _update_indices(self, key: str, entry: CacheEntry):
        """Atualiza índices de tags e prioridades"""
        # Índice de tags
        for tag in entry.tags:
            self.tag_index[tag].add(key)
        
        # Índice de prioridades
        self.priority_cache[entry.priority].append(key)
    
    def get_by_tag(self, tag: str) -> List[Tuple[str, Any]]:
        """Recupera todas as entradas com uma tag específica"""
        result = []
        with self._lock:
            if tag in self.tag_index:
                for key in self.tag_index[tag]:
                    value = self.get(key)
                    if value is not None:
                        result.append((key, value))
        return result
    
    def get_by_priority(self, priority: int) -> List[Tuple[str, Any]]:
        """Recupera todas as entradas com uma prioridade específica"""
        result = []
        with self._lock:
            if priority in self.priority_cache:
                for key in self.priority_cache[priority]:
                    value = self.get(key)
                    if value is not None:
                        result.append((key, value))
        return result
    
    def clear(self):
        """Limpa todo o cache"""
        with self._lock:
            self.cache.clear()
            self.tag_index.clear()
            self.priority_cache.clear()
            self.metrics.memory_usage_bytes = 0
            logger.info("Cache limpo completamente")
    
    async def cleanup_expired(self):
        """Remove entradas expiradas"""
        expired_keys = []
        
        with self._lock:
            for key, entry in list(self.cache.items()):
                if entry.is_expired:
                    expired_keys.append(key)
        
        # Remove entradas expiradas
        for key in expired_keys:
            self._remove_entry(key)
        
        if expired_keys:
            logger.info(f"Removidas {len(expired_keys)} entradas expiradas")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas detalhadas do cache"""
        with self._lock:
            # Atualiza taxas
            self.metrics.update_rates()
            
            # Calcula métricas adicionais
            total_entries = len(self.cache)
            total_tags = len(self.tag_index)
            total_priorities = len(self.priority_cache)
            
            # Distribuição por prioridade
            priority_distribution = {
                priority: len(keys) 
                for priority, keys in self.priority_cache.items()
            }
            
            # Top tags
            top_tags = sorted(
                [(tag, len(keys)) for tag, keys in self.tag_index.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "cache_size": total_entries,
                "max_size": self.max_size,
                "memory_usage_mb": self.metrics.memory_usage_bytes / (1024 * 1024),
                "compression_stats": {
                    "compressed_entries": self.metrics.compressed,
                    "compression_ratio": self.metrics.compression_ratio
                },
                "performance": {
                    "hit_rate": self.metrics.hit_rate,
                    "miss_rate": self.metrics.miss_rate,
                    "total_requests": self.metrics.total_requests,
                    "hits": self.metrics.hits,
                    "misses": self.metrics.misses,
                    "expired": self.metrics.expired
                },
                "structure": {
                    "total_tags": total_tags,
                    "total_priorities": total_priorities,
                    "priority_distribution": priority_distribution,
                    "top_tags": top_tags
                },
                "maintenance": {
                    "cleanup_count": self.metrics.cleanup_count,
                    "last_cleanup": self.metrics.last_cleanup.isoformat() if self.metrics.last_cleanup else None,
                    "cleanup_interval": self.cleanup_interval
                }
            }
    
    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Retorna informações de todas as entradas"""
        with self._lock:
            return [entry.to_dict() for entry in self.cache.values()]
    
    async def stop(self):
        """Para o gerenciador de cache"""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Gerenciador de cache parado")

# Instância global
_cache_manager: Optional[AdvancedCacheManager] = None

def get_advanced_cache_manager() -> AdvancedCacheManager:
    """Retorna instância global do gerenciador de cache"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = AdvancedCacheManager()
    return _cache_manager

# Funções de conveniência
def set_cache(key: str, value: Any, ttl: Optional[int] = None, tags: Optional[List[str]] = None, priority: int = 1) -> bool:
    """Define valor no cache avançado"""
    return get_advanced_cache_manager().set(key, value, ttl, tags, priority)

def get_cache(key: str) -> Optional[Any]:
    """Recupera valor do cache avançado"""
    return get_advanced_cache_manager().get(key)

def get_cache_by_tag(tag: str) -> List[Tuple[str, Any]]:
    """Recupera entradas por tag"""
    return get_advanced_cache_manager().get_by_tag(tag)

def get_cache_by_priority(priority: int) -> List[Tuple[str, Any]]:
    """Recupera entradas por prioridade"""
    return get_advanced_cache_manager().get_by_priority(priority)

def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache"""
    return get_advanced_cache_manager().get_stats()

def clear_cache():
    """Limpa todo o cache"""
    get_advanced_cache_manager().clear()

async def cleanup_cache():
    """Limpa entradas expiradas"""
    await get_advanced_cache_manager().cleanup_expired()

if __name__ == "__main__":
    # Teste do sistema de cache
    async def test_cache():
        cache = get_advanced_cache_manager()
        
        print("🧪 Testando Sistema de Cache Avançado...")
        
        # Teste básico
        cache.set("test_key", "test_value", ttl=60, tags=["test", "demo"], priority=3)
        value = cache.get("test_key")
        print(f"✅ Teste básico: {value}")
        
        # Teste com compressão
        large_data = "x" * 2000  # Acima do threshold
        cache.set("large_key", large_data, ttl=60, tags=["large", "demo"])
        value = cache.get("large_key")
        print(f"✅ Teste compressão: {len(value) if value else 0} caracteres")
        
        # Teste por tag
        tagged_entries = cache.get_by_tag("demo")
        print(f"✅ Entradas com tag 'demo': {len(tagged_entries)}")
        
        # Teste por prioridade
        priority_entries = cache.get_by_priority(3)
        print(f"✅ Entradas com prioridade 3: {len(priority_entries)}")
        
        # Estatísticas
        stats = cache.get_stats()
        print(f"✅ Estatísticas: {stats['performance']['hit_rate']:.1f}% hit rate")
        
        # Para o cache
        await cache.stop()
        print("✅ Teste concluído!")
    
    # Executa teste
    asyncio.run(test_cache())
