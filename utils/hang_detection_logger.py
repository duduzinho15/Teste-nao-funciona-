#!/usr/bin/env python3
"""
Sistema de Logging para Detecção de Travamentos

Sistema especializado para identificar onde e por que o código está travando.
Inclui timeouts, heartbeats e logging detalhado de operações críticas.
"""

import logging
import time
import threading
import functools
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
import traceback
import sys
import os

# Logger especializado para detecção de travamentos
hang_logger = logging.getLogger("hang_detection")

class HangDetectionLogger:
    """Logger especializado para detectar travamentos."""
    
    def __init__(self):
        self.active_operations = {}
        self.operation_timeouts = {}
        self.heartbeat_thread = None
        self.monitoring = False
        
        # Configurar logger
        if not hang_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - HANG_DETECTION - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            hang_logger.addHandler(handler)
            hang_logger.setLevel(logging.INFO)
    
    def start_monitoring(self):
        """Inicia monitoramento de travamentos."""
        if not self.monitoring:
            self.monitoring = True
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
            self.heartbeat_thread.start()
            hang_logger.info("🔍 Sistema de detecção de travamentos ATIVADO")
    
    def stop_monitoring(self):
        """Para monitoramento de travamentos."""
        self.monitoring = False
        hang_logger.info("🔍 Sistema de detecção de travamentos DESATIVADO")
    
    def _heartbeat_monitor(self):
        """Monitor que verifica operações em andamento."""
        while self.monitoring:
            try:
                current_time = datetime.now()
                
                # Verificar operações que podem estar travadas
                for op_id, start_time in list(self.active_operations.items()):
                    duration = (current_time - start_time).total_seconds()
                    timeout = self.operation_timeouts.get(op_id, 300)  # 5 min default
                    
                    if duration > timeout:
                        hang_logger.error(f"🚨 POSSÍVEL TRAVAMENTO DETECTADO!")
                        hang_logger.error(f"   Operação: {op_id}")
                        hang_logger.error(f"   Duração: {duration:.1f}s (timeout: {timeout}s)")
                        hang_logger.error(f"   Iniciada em: {start_time}")
                        
                        # Remover da lista para evitar spam
                        del self.active_operations[op_id]
                        if op_id in self.operation_timeouts:
                            del self.operation_timeouts[op_id]
                
                time.sleep(10)  # Verificar a cada 10 segundos
                
            except Exception as e:
                hang_logger.error(f"Erro no monitor de travamentos: {e}")
                time.sleep(30)
    
    def log_operation_start(self, operation_name: str, details: str = "", timeout_seconds: int = 300):
        """Registra início de operação que pode travar."""
        op_id = f"{operation_name}_{int(time.time())}"
        self.active_operations[op_id] = datetime.now()
        self.operation_timeouts[op_id] = timeout_seconds
        
        hang_logger.info(f"🔄 INICIANDO: {operation_name}")
        if details:
            hang_logger.info(f"   Detalhes: {details}")
        hang_logger.info(f"   Timeout: {timeout_seconds}s")
        hang_logger.info(f"   ID: {op_id}")
        
        return op_id
    
    def log_operation_end(self, op_id: str, success: bool = True, details: str = ""):
        """Registra fim de operação."""
        if op_id in self.active_operations:
            start_time = self.active_operations[op_id]
            duration = (datetime.now() - start_time).total_seconds()
            
            status = "✅ CONCLUÍDA" if success else "❌ FALHOU"
            hang_logger.info(f"{status}: {op_id.split('_')[0]}")
            hang_logger.info(f"   Duração: {duration:.2f}s")
            if details:
                hang_logger.info(f"   Detalhes: {details}")
            
            # Remover da lista de operações ativas
            del self.active_operations[op_id]
            if op_id in self.operation_timeouts:
                del self.operation_timeouts[op_id]
        else:
            hang_logger.warning(f"⚠️ Tentativa de finalizar operação não registrada: {op_id}")
    
    def log_http_request_start(self, url: str, timeout: int = 30):
        """Registra início de requisição HTTP."""
        return self.log_operation_start(
            "HTTP_REQUEST", 
            f"URL: {url}", 
            timeout + 10  # Timeout um pouco maior que o da requisição
        )
    
    def log_http_request_end(self, op_id: str, status_code: Optional[int] = None, error: str = ""):
        """Registra fim de requisição HTTP."""
        details = ""
        if status_code:
            details = f"Status: {status_code}"
        if error:
            details += f" | Erro: {error}"
        
        success = status_code and 200 <= status_code < 400
        self.log_operation_end(op_id, success, details)
    
    def log_database_operation_start(self, operation: str, table: str = ""):
        """Registra início de operação de banco."""
        details = f"Tabela: {table}" if table else ""
        return self.log_operation_start(f"DB_{operation}", details, 60)
    
    def log_selenium_operation_start(self, operation: str, url: str = ""):
        """Registra início de operação Selenium."""
        details = f"URL: {url}" if url else ""
        return self.log_operation_start(f"SELENIUM_{operation}", details, 120)

# Instância global
_hang_detector = None

def get_hang_detector() -> HangDetectionLogger:
    """Retorna instância global do detector de travamentos."""
    global _hang_detector
    if _hang_detector is None:
        _hang_detector = HangDetectionLogger()
        _hang_detector.start_monitoring()
    return _hang_detector

def log_operation(operation_name: str, timeout_seconds: int = 300):
    """Decorator para logging automático de operações."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            detector = get_hang_detector()
            
            # Extrair detalhes dos argumentos se possível
            details = ""
            if args:
                if isinstance(args[0], str) and args[0].startswith('http'):
                    details = f"URL: {args[0]}"
                elif len(str(args[0])) < 100:
                    details = f"Arg: {args[0]}"
            
            op_id = detector.log_operation_start(operation_name, details, timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                detector.log_operation_end(op_id, True)
                return result
            except Exception as e:
                detector.log_operation_end(op_id, False, str(e))
                raise
        
        return wrapper
    return decorator

def log_critical_section(section_name: str):
    """Context manager para seções críticas que podem travar."""
    detector = get_hang_detector()
    op_id = detector.log_operation_start(f"CRITICAL_SECTION_{section_name}", "", 180)
    
    class CriticalSectionContext:
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            success = exc_type is None
            error_details = str(exc_val) if exc_val else ""
            detector.log_operation_end(op_id, success, error_details)
    
    return CriticalSectionContext()

# Funções de conveniência
def log_http_start(url: str, timeout: int = 30) -> str:
    """Log início de requisição HTTP."""
    return get_hang_detector().log_http_request_start(url, timeout)

def log_http_end(op_id: str, status_code: Optional[int] = None, error: str = ""):
    """Log fim de requisição HTTP."""
    get_hang_detector().log_http_request_end(op_id, status_code, error)

def log_db_start(operation: str, table: str = "") -> str:
    """Log início de operação de banco."""
    return get_hang_detector().log_database_operation_start(operation, table)

def log_db_end(op_id: str, success: bool = True, details: str = ""):
    """Log fim de operação de banco."""
    get_hang_detector().log_operation_end(op_id, success, details)

def emergency_stack_trace():
    """Imprime stack trace de emergência para debug de travamentos."""
    hang_logger.critical("🚨 STACK TRACE DE EMERGÊNCIA:")
    for thread_id, frame in sys._current_frames().items():
        hang_logger.critical(f"Thread {thread_id}:")
        traceback.print_stack(frame, file=sys.stderr)
        hang_logger.critical("-" * 50)
