#!/usr/bin/env python3
"""
Sistema de Fallback Inteligente para APIs RapidAPI

Este módulo implementa um sistema que automaticamente alterna entre diferentes APIs
quando uma falha, garantindo alta disponibilidade e robustez na coleta de dados.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class APIStatus(Enum):
    """Status de uma API"""
    ACTIVE = "active"
    FAILING = "failing"
    RATE_LIMITED = "rate_limited"
    DISABLED = "disabled"

@dataclass
class APIFallbackConfig:
    """Configuração para fallback de API"""
    api_name: str
    priority: int  # Prioridade mais baixa = mais alta
    retry_after: int = 300  # Segundos para tentar novamente
    max_failures: int = 3  # Máximo de falhas antes de desabilitar
    health_check_interval: int = 60  # Intervalo para verificar saúde

class APIFallbackManager:
    """
    Gerencia fallback automático entre APIs RapidAPI
    
    Funcionalidades:
    - Monitoramento de saúde das APIs
    - Fallback automático quando uma API falha
    - Retry inteligente com backoff exponencial
    - Balanceamento de carga entre APIs ativas
    """
    
    def __init__(self):
        self.logger = logging.getLogger("rapidapi.fallback")
        self.apis: Dict[str, APIFallbackConfig] = {}
        self.api_status: Dict[str, APIStatus] = {}
        self.failure_counts: Dict[str, int] = {}
        self.last_failure: Dict[str, datetime] = {}
        self.last_success: Dict[str, datetime] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        
    def register_api(self, config: APIFallbackConfig):
        """Registra uma API para gerenciamento de fallback"""
        self.apis[config.api_name] = config
        self.api_status[config.api_name] = APIStatus.ACTIVE
        self.failure_counts[config.api_name] = 0
        self.last_success[config.api_name] = datetime.now()
        self.logger.info(f"API {config.api_name} registrada com prioridade {config.priority}")
    
    def unregister_api(self, api_name: str):
        """Remove uma API do gerenciamento de fallback"""
        if api_name in self.apis:
            del self.apis[api_name]
            del self.api_status[api_name]
            del self.failure_counts[api_name]
            del self.last_failure[api_name]
            del self.last_success[api_name]
            self.logger.info(f"API {api_name} removida do gerenciamento")
    
    def record_success(self, api_name: str):
        """Registra sucesso de uma API"""
        if api_name in self.apis:
            self.api_status[api_name] = APIStatus.ACTIVE
            self.failure_counts[api_name] = 0
            self.last_success[api_name] = datetime.now()
            self.logger.debug(f"Sucesso registrado para {api_name}")
    
    def record_failure(self, api_name: str, error_type: str = "general"):
        """Registra falha de uma API"""
        if api_name in self.apis:
            self.failure_counts[api_name] += 1
            self.last_failure[api_name] = datetime.now()
            
            # Determina novo status baseado no tipo de erro
            if error_type == "rate_limit":
                self.api_status[api_name] = APIStatus.RATE_LIMITED
                self.logger.warning(f"Rate limit atingido para {api_name}")
            elif self.failure_counts[api_name] >= self.apis[api_name].max_failures:
                self.api_status[api_name] = APIStatus.FAILING
                self.logger.error(f"API {api_name} marcada como falhando após {self.failure_counts[api_name]} falhas")
            else:
                self.api_status[api_name] = APIStatus.FAILING
                self.logger.warning(f"Falha registrada para {api_name} ({self.failure_counts[api_name]}/{self.apis[api_name].max_failures})")
    
    def get_best_api(self, operation_type: str = "general") -> Optional[str]:
        """
        Retorna a melhor API disponível para uma operação
        
        Args:
            operation_type: Tipo de operação (jogos, jogadores, etc.)
            
        Returns:
            Nome da melhor API ou None se nenhuma estiver disponível
        """
        available_apis = []
        
        for api_name, config in self.apis.items():
            status = self.api_status[api_name]
            
            # Verifica se a API está disponível
            if status == APIStatus.DISABLED:
                continue
                
            if status == APIStatus.FAILING:
                # Verifica se já pode tentar novamente
                if api_name in self.last_failure:
                    time_since_failure = (datetime.now() - self.last_failure[api_name]).total_seconds()
                    if time_since_failure < config.retry_after:
                        continue
            
            if status == APIStatus.RATE_LIMITED:
                # Verifica se já pode tentar novamente
                if api_name in self.last_failure:
                    time_since_failure = (datetime.now() - self.last_failure[api_name]).total_seconds()
                    if time_since_failure < config.retry_after:
                        continue
            
            # Calcula score baseado em prioridade e histórico
            score = self._calculate_api_score(api_name, config)
            available_apis.append((api_name, score))
        
        if not available_apis:
            return None
        
        # Retorna API com melhor score
        best_api = max(available_apis, key=lambda x: x[1])[0]
        self.logger.debug(f"Melhor API selecionada: {best_api}")
        return best_api
    
    def _calculate_api_score(self, api_name: str, config: APIFallbackConfig) -> float:
        """Calcula score de uma API baseado em prioridade e histórico"""
        base_score = 1000 - config.priority  # Prioridade mais baixa = score mais alto
        
        # Bônus por sucessos recentes
        if api_name in self.last_success:
            time_since_success = (datetime.now() - self.last_success[api_name]).total_seconds()
            if time_since_success < 3600:  # Última hora
                base_score += 100
            elif time_since_success < 86400:  # Último dia
                base_score += 50
        
        # Penalidade por falhas recentes
        if api_name in self.last_failure:
            time_since_failure = (datetime.now() - self.last_failure[api_name]).total_seconds()
            if time_since_failure < 300:  # Últimos 5 minutos
                base_score -= 200
            elif time_since_failure < 3600:  # Última hora
                base_score -= 100
        
        return base_score
    
    async def execute_with_fallback(self, operation: Callable, operation_name: str, 
                                  *args, **kwargs) -> Tuple[bool, Any, str]:
        """
        Executa uma operação com fallback automático
        
        Args:
            operation: Função a ser executada
            operation_name: Nome da operação para logging
            *args, **kwargs: Argumentos para a operação
            
        Returns:
            Tuple (sucesso, resultado, api_utilizada)
        """
        max_attempts = len(self.apis)
        attempts = 0
        
        while attempts < max_attempts:
            # Seleciona melhor API disponível
            api_name = self.get_best_api(operation_name)
            
            if not api_name:
                self.logger.error("Nenhuma API disponível para fallback")
                return False, None, "none"
            
            try:
                self.logger.info(f"Tentando {operation_name} com API {api_name} (tentativa {attempts + 1})")
                
                # Executa operação
                result = await operation(api_name, *args, **kwargs)
                
                # Registra sucesso
                self.record_success(api_name)
                self.logger.info(f"✅ {operation_name} executado com sucesso via {api_name}")
                
                return True, result, api_name
                
            except Exception as e:
                # Registra falha
                error_type = "rate_limit" if "rate limit" in str(e).lower() else "general"
                self.record_failure(api_name, error_type)
                
                self.logger.warning(f"❌ Falha na {operation_name} via {api_name}: {e}")
                attempts += 1
                
                # Aguarda antes da próxima tentativa
                if attempts < max_attempts:
                    wait_time = min(2 ** attempts, 30)  # Backoff exponencial, max 30s
                    self.logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                    await asyncio.sleep(wait_time)
        
        self.logger.error(f"❌ Todas as tentativas de {operation_name} falharam")
        return False, None, "all_failed"
    
    async def start_health_monitoring(self):
        """Inicia monitoramento de saúde das APIs"""
        if self.health_check_task and not self.health_check_task.done():
            return
        
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.logger.info("Monitoramento de saúde iniciado")
    
    async def stop_health_monitoring(self):
        """Para monitoramento de saúde das APIs"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            self.logger.info("Monitoramento de saúde parado")
    
    async def _health_check_loop(self):
        """Loop principal de verificação de saúde"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Verifica a cada minuto
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erro no loop de saúde: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self):
        """Executa verificações de saúde para todas as APIs"""
        for api_name, config in self.apis.items():
            if self.api_status[api_name] == APIStatus.DISABLED:
                continue
            
            # Verifica se pode tentar reativar APIs falhando
            if self.api_status[api_name] == APIStatus.FAILING:
                if api_name in self.last_failure:
                    time_since_failure = (datetime.now() - self.last_failure[api_name]).total_seconds()
                    if time_since_failure >= config.retry_after:
                        self.logger.info(f"Tentando reativar API {api_name}")
                        self.api_status[api_name] = APIStatus.ACTIVE
            
            # Verifica se pode reativar APIs com rate limit
            elif self.api_status[api_name] == APIStatus.RATE_LIMITED:
                if api_name in self.last_failure:
                    time_since_failure = (datetime.now() - self.last_failure[api_name]).total_seconds()
                    if time_since_failure >= config.retry_after:
                        self.logger.info(f"Reativando API {api_name} após rate limit")
                        self.api_status[api_name] = APIStatus.ACTIVE
    
    def get_status_report(self) -> Dict[str, Any]:
        """Retorna relatório completo do status das APIs"""
        report = {
            "total_apis": len(self.apis),
            "apis_status": {},
            "fallback_stats": {
                "total_failures": sum(self.failure_counts.values()),
                "apis_failing": len([s for s in self.api_status.values() if s == APIStatus.FAILING]),
                "apis_rate_limited": len([s for s in self.api_status.values() if s == APIStatus.RATE_LIMITED]),
                "apis_active": len([s for s in self.api_status.values() if s == APIStatus.ACTIVE])
            }
        }
        
        for api_name in self.apis:
            report["apis_status"][api_name] = {
                "status": self.api_status[api_name].value,
                "failures": self.failure_counts.get(api_name, 0),
                "last_success": self.last_success.get(api_name, "never").isoformat() if isinstance(self.last_success.get(api_name), datetime) else "never",
                "last_failure": self.last_failure.get(api_name, "never").isoformat() if isinstance(self.last_failure.get(api_name), datetime) else "never"
            }
        
        return report

# Instância global do gerenciador de fallback
fallback_manager = APIFallbackManager()

def get_fallback_manager() -> APIFallbackManager:
    """Retorna a instância global do gerenciador de fallback"""
    return fallback_manager
