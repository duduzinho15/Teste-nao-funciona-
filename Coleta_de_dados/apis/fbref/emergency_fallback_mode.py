#!/usr/bin/env python3
"""
Modo de Emergência - Fallback Total

Sistema que detecta falhas sistemáticas e força uso de fallback/cache
quando o FBRef está bloqueando todas as requisições.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

logger = logging.getLogger(__name__)

class EmergencyFallbackMode:
    """Sistema de emergência que detecta bloqueios sistemáticos."""
    
    def __init__(self):
        self.failure_count = 0
        self.success_count = 0
        self.consecutive_failures = 0
        self.last_success = None
        self.emergency_mode = False
        self.emergency_until = None
        self.failure_threshold = 10  # 10 falhas consecutivas = emergência
        self.success_rate_threshold = 0.1  # Menos de 10% sucesso = emergência
        
        logger.info("Sistema de emergência inicializado")
    
    def record_request_result(self, url: str, success: bool, content_received: bool = False):
        """Registra resultado de uma requisição."""
        
        if success and content_received:
            # Sucesso real (não apenas HTTP 200, mas conteúdo útil)
            self.success_count += 1
            self.consecutive_failures = 0
            self.last_success = datetime.now()
            
            # Sair do modo de emergência se estava ativo
            if self.emergency_mode:
                logger.info("✅ Saindo do modo de emergência - requisições funcionando novamente")
                self.emergency_mode = False
                self.emergency_until = None
        
        else:
            # Falha (HTTP erro, timeout, ou conteúdo vazio)
            self.failure_count += 1
            self.consecutive_failures += 1
            
            # Verificar se deve entrar em modo de emergência
            self._check_emergency_conditions()
    
    def _check_emergency_conditions(self):
        """Verifica se deve ativar modo de emergência."""
        
        total_requests = self.success_count + self.failure_count
        
        # Condição 1: Muitas falhas consecutivas
        if self.consecutive_failures >= self.failure_threshold:
            self._activate_emergency_mode(f"{self.consecutive_failures} falhas consecutivas")
            return
        
        # Condição 2: Taxa de sucesso muito baixa (após pelo menos 20 tentativas)
        if total_requests >= 20:
            success_rate = self.success_count / total_requests
            if success_rate < self.success_rate_threshold:
                self._activate_emergency_mode(f"Taxa de sucesso: {success_rate:.1%}")
                return
        
        # Condição 3: Muito tempo sem sucesso
        if self.last_success:
            time_since_success = datetime.now() - self.last_success
            if time_since_success > timedelta(minutes=30):
                self._activate_emergency_mode(f"Sem sucesso há {time_since_success}")
                return
    
    def _activate_emergency_mode(self, reason: str):
        """Ativa modo de emergência."""
        if not self.emergency_mode:
            self.emergency_mode = True
            self.emergency_until = datetime.now() + timedelta(hours=2)  # 2 horas
            
            logger.error("🚨 MODO DE EMERGÊNCIA ATIVADO!")
            logger.error(f"   Razão: {reason}")
            logger.error(f"   Ativo até: {self.emergency_until}")
            logger.error("   TODAS as requisições usarão fallback/cache")
    
    def should_use_fallback_only(self) -> bool:
        """Verifica se deve usar apenas fallback."""
        
        if self.emergency_mode:
            if self.emergency_until and datetime.now() < self.emergency_until:
                return True
            else:
                # Tempo de emergência expirou
                logger.info("⏰ Tempo de emergência expirou - tentando requisições novamente")
                self.emergency_mode = False
                self.emergency_until = None
                self.consecutive_failures = 0  # Reset
        
        return False
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do sistema."""
        total = self.success_count + self.failure_count
        success_rate = self.success_count / max(1, total)
        
        return {
            'total_requests': total,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': success_rate,
            'consecutive_failures': self.consecutive_failures,
            'emergency_mode': self.emergency_mode,
            'emergency_until': self.emergency_until.isoformat() if self.emergency_until else None,
            'last_success': self.last_success.isoformat() if self.last_success else None
        }
    
    def force_emergency_mode(self, hours: int = 2):
        """Força modo de emergência por um período específico."""
        self._activate_emergency_mode(f"Forçado manualmente por {hours}h")
        self.emergency_until = datetime.now() + timedelta(hours=hours)
    
    def disable_emergency_mode(self):
        """Desativa modo de emergência."""
        if self.emergency_mode:
            logger.info("🔄 Modo de emergência desativado manualmente")
            self.emergency_mode = False
            self.emergency_until = None
            self.consecutive_failures = 0

# Instância global
_emergency_system = None

def get_emergency_system() -> EmergencyFallbackMode:
    """Retorna instância global do sistema de emergência."""
    global _emergency_system
    if _emergency_system is None:
        _emergency_system = EmergencyFallbackMode()
    return _emergency_system

def record_request_result(url: str, success: bool, content_received: bool = False):
    """Registra resultado de requisição no sistema de emergência."""
    system = get_emergency_system()
    system.record_request_result(url, success, content_received)

def should_use_emergency_fallback() -> bool:
    """Verifica se deve usar apenas fallback devido a emergência."""
    system = get_emergency_system()
    return system.should_use_fallback_only()

def get_emergency_stats() -> Dict:
    """Retorna estatísticas do sistema de emergência."""
    system = get_emergency_system()
    return system.get_stats()

def force_emergency_mode(hours: int = 2):
    """Força modo de emergência."""
    system = get_emergency_system()
    system.force_emergency_mode(hours)

def disable_emergency_mode():
    """Desativa modo de emergência."""
    system = get_emergency_system()
    system.disable_emergency_mode()

def log_emergency_status():
    """Loga status atual do sistema de emergência."""
    stats = get_emergency_stats()
    
    logger.info("📊 STATUS DO SISTEMA DE EMERGÊNCIA:")
    logger.info(f"   Total de requisições: {stats['total_requests']}")
    logger.info(f"   Taxa de sucesso: {stats['success_rate']:.1%}")
    logger.info(f"   Falhas consecutivas: {stats['consecutive_failures']}")
    logger.info(f"   Modo emergência: {stats['emergency_mode']}")
    
    if stats['emergency_mode']:
        logger.warning("🚨 MODO DE EMERGÊNCIA ATIVO - Usando apenas fallback/cache")
    else:
        logger.info("✅ Modo normal - Tentando requisições reais")
