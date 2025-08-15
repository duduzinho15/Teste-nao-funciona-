#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISTEMA DE LOGS CENTRALIZADO
============================

Sistema centralizado de logging para todas as APIs e módulos do ApostaPro.
Fornece logs estruturados, monitoramento em tempo real e alertas automáticos.

Funcionalidades:
- Logs estruturados em JSON
- Rotação automática de arquivos
- Monitoramento de performance
- Alertas para falhas
- Dashboard de status

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import logging
import logging.handlers
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict, deque

@dataclass
class LogEntry:
    """Estrutura padronizada para entradas de log."""
    timestamp: str
    level: str
    module: str
    function: str
    message: str
    data: Dict[str, Any]
    execution_time: Optional[float] = None
    error_details: Optional[str] = None
    api_status: Optional[str] = None

class CentralizedLogger:
    """
    Sistema centralizado de logging para o ApostaPro.
    
    Funcionalidades:
    - Logs estruturados em JSON
    - Monitoramento de performance
    - Alertas automáticos
    - Dashboard de status
    """
    
    def __init__(self, log_dir: str = "logs", max_log_size: int = 10 * 1024 * 1024, backup_count: int = 5):
        """
        Inicializa o sistema de logging centralizado.
        
        Args:
            log_dir: Diretório para armazenar logs
            max_log_size: Tamanho máximo do arquivo de log (bytes)
            backup_count: Número de arquivos de backup
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        
        # Estatísticas de logging
        self.stats = {
            "total_logs": 0,
            "logs_por_nivel": defaultdict(int),
            "logs_por_modulo": defaultdict(int),
            "erros_por_modulo": defaultdict(int),
            "performance_media": deque(maxlen=1000),
            "ultima_atualizacao": datetime.now().isoformat()
        }
        
        # Alertas e notificações
        self.alertas = []
        self.alertas_por_modulo = defaultdict(list)
        
        # Configurar logging
        self._setup_logging()
        
        # Thread para monitoramento
        self.monitoring_thread = None
        self.monitoring_active = False
        
        self.logger.info("🚀 Sistema de logs centralizado inicializado")
    
    def _setup_logging(self):
        """Configura o sistema de logging."""
        # Logger principal
        self.logger = logging.getLogger("apostapro")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo principal
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "apostapro_main.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.INFO)
        
        # Handler para arquivo de erros
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "apostapro_errors.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Handler para arquivo de debug
        debug_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "apostapro_debug.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        
        # Formatter JSON
        json_formatter = JSONFormatter()
        main_handler.setFormatter(json_formatter)
        error_handler.setFormatter(json_formatter)
        debug_handler.setFormatter(json_formatter)
        
        # Adicionar handlers
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        
        # Handler para console (apenas em desenvolvimento)
        if os.getenv("ENVIRONMENT", "dev") == "dev":
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def log(self, level: str, module: str, function: str, message: str, 
            data: Dict[str, Any] = None, execution_time: float = None, 
            api_status: str = None):
        """
        Registra um log estruturado.
        
        Args:
            level: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            module: Nome do módulo
            function: Nome da função
            message: Mensagem do log
            data: Dados adicionais
            execution_time: Tempo de execução em segundos
            api_status: Status da API (se aplicável)
        """
        if data is None:
            data = {}
        
        # Criar entrada de log
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.upper(),
            module=module,
            function=function,
            message=message,
            data=data,
            execution_time=execution_time,
            api_status=api_status
        )
        
        # Registrar no logger apropriado
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(asdict(log_entry), ensure_ascii=False))
        
        # Atualizar estatísticas
        self._update_stats(log_entry)
        
        # Verificar alertas
        self._check_alerts(log_entry)
    
    def _update_stats(self, log_entry: LogEntry):
        """Atualiza as estatísticas de logging."""
        try:
            self.stats["total_logs"] += 1
            self.stats["logs_por_nivel"][log_entry.level] += 1
            self.stats["logs_por_modulo"][log_entry.module] += 1
            
            if log_entry.level in ["ERROR", "CRITICAL"]:
                self.stats["erros_por_modulo"][log_entry.module] += 1
            
            if log_entry.execution_time:
                self.stats["performance_media"].append(log_entry.execution_time)
            
            self.stats["ultima_atualizacao"] = datetime.now().isoformat()
        except Exception as e:
            # Fallback para print se houver erro
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def _check_alerts(self, log_entry: LogEntry):
        """Verifica se deve gerar alertas baseado no log."""
        # Alerta para erros críticos
        if log_entry.level == "CRITICAL":
            alerta = {
                "timestamp": log_entry.timestamp,
                "tipo": "ERRO_CRITICO",
                "modulo": log_entry.module,
                "funcao": log_entry.function,
                "mensagem": log_entry.message,
                "dados": log_entry.data
            }
            self.alertas.append(alerta)
            self.alertas_por_modulo[log_entry.module].append(alerta)
        
        # Alerta para múltiplos erros em um módulo
        if (log_entry.level == "ERROR" and 
            self.stats["erros_por_modulo"][log_entry.module] >= 5):
            alerta = {
                "timestamp": log_entry.timestamp,
                "tipo": "MULTIPLOS_ERROS",
                "modulo": log_entry.module,
                "funcao": log_entry.function,
                "mensagem": f"Múltiplos erros detectados em {log_entry.module}",
                "dados": {"total_erros": self.stats["erros_por_modulo"][log_entry.module]}
            }
            self.alertas.append(alerta)
            self.alertas_por_modulo[log_entry.module].append(alerta)
    
    def start_monitoring(self):
        """Inicia o monitoramento em background."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        if hasattr(self, 'logger'):
            self.logger.info("🔍 Monitoramento de logs iniciado")
        else:
            print("🔍 Monitoramento de logs iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento em background."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        if hasattr(self, 'logger'):
            self.logger.info("⏹️ Monitoramento de logs parado")
        else:
            print("⏹️ Monitoramento de logs parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring_active:
            try:
                # Verificar performance
                self._check_performance_alerts()
                
                # Limpar alertas antigos (mais de 24h)
                self._cleanup_old_alerts()
                
                # Aguardar próxima verificação
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Erro no loop de monitoramento: {e}")
                else:
                    print(f"Erro no loop de monitoramento: {e}")
    
    def _check_performance_alerts(self):
        """Verifica alertas de performance."""
        if len(self.stats["performance_media"]) > 0:
            performance_media = sum(self.stats["performance_media"]) / len(self.stats["performance_media"])
            
            # Alerta para performance baixa
            if performance_media > 10.0:  # Mais de 10 segundos
                alerta = {
                    "timestamp": datetime.now().isoformat(),
                    "tipo": "PERFORMANCE_BAIXA",
                    "modulo": "SISTEMA",
                    "funcao": "MONITORAMENTO",
                    "mensagem": f"Performance baixa detectada: {performance_media:.2f}s",
                    "dados": {"performance_media": performance_media}
                }
                self.alertas.append(alerta)
    
    def _cleanup_old_alerts(self):
        """Remove alertas antigos (mais de 24h)."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Limpar alertas gerais
        self.alertas = [
            alerta for alerta in self.alertas
            if datetime.fromisoformat(alerta["timestamp"]) > cutoff_time
        ]
        
        # Limpar alertas por módulo
        for modulo in self.alertas_por_modulo:
            self.alertas_por_modulo[modulo] = [
                alerta for alerta in self.alertas_por_modulo[modulo]
                if datetime.fromisoformat(alerta["timestamp"]) > cutoff_time
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de logging."""
        return dict(self.stats)
    
    def get_alerts(self, modulo: str = None) -> List[Dict[str, Any]]:
        """Retorna alertas ativos."""
        if modulo:
            return self.alertas_por_modulo.get(modulo, [])
        return self.alertas
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance."""
        if len(self.stats["performance_media"]) == 0:
            return {"media": 0, "min": 0, "max": 0, "total": 0}
        
        performances = list(self.stats["performance_media"])
        return {
            "media": sum(performances) / len(performances),
            "min": min(performances),
            "max": max(performances),
            "total": len(performances)
        }
    
    def export_logs(self, start_date: str = None, end_date: str = None, 
                   level: str = None, module: str = None) -> List[Dict[str, Any]]:
        """
        Exporta logs filtrados.
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            level: Nível do log
            module: Módulo específico
            
        Returns:
            Lista de logs filtrados
        """
        # Implementar exportação de logs filtrados
        # Por enquanto retorna estatísticas
        return [self.get_stats()]

class JSONFormatter(logging.Formatter):
    """Formatador JSON para logs."""
    
    def format(self, record):
        """Formata o record como JSON."""
        try:
            # Tentar fazer parse se já for JSON
            if isinstance(record.msg, str) and record.msg.startswith('{'):
                return record.msg
            
            # Formatar como JSON
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "module": getattr(record, 'module', record.name),
                "function": getattr(record, 'funcName', 'unknown'),
                "message": record.getMessage(),
                "data": getattr(record, 'data', {}),
                "execution_time": getattr(record, 'execution_time', None),
                "api_status": getattr(record, 'api_status', None)
            }
            
            return json.dumps(log_data, ensure_ascii=False)
            
        except Exception as e:
            # Fallback para formato padrão
            return super().format(record)

# Instância global do logger centralizado
centralized_logger = CentralizedLogger()

# Funções de conveniência
def log_info(module: str, function: str, message: str, data: Dict[str, Any] = None, 
             execution_time: float = None, api_status: str = None):
    """Log de informação."""
    centralized_logger.log("INFO", module, function, message, data, execution_time, api_status)

def log_warning(module: str, function: str, message: str, data: Dict[str, Any] = None, 
                execution_time: float = None, api_status: str = None):
    """Log de aviso."""
    centralized_logger.log("WARNING", module, function, message, data, execution_time, api_status)

def log_error(module: str, function: str, message: str, data: Dict[str, Any] = None, 
              execution_time: float = None, api_status: str = None, error_details: str = None):
    """Log de erro."""
    if data is None:
        data = {}
    data["error_details"] = error_details
    centralized_logger.log("ERROR", module, function, message, data, execution_time, api_status)

def log_critical(module: str, function: str, message: str, data: Dict[str, Any] = None, 
                 execution_time: float = None, api_status: str = None, error_details: str = None):
    """Log crítico."""
    if data is None:
        data = {}
    data["error_details"] = error_details
    centralized_logger.log("CRITICAL", module, function, message, data, execution_time, api_status)

def log_performance(module: str, function: str, execution_time: float, 
                   message: str = None, data: Dict[str, Any] = None):
    """Log de performance."""
    if message is None:
        message = f"Função {function} executada em {execution_time:.2f}s"
    
    centralized_logger.log("INFO", module, function, message, data, execution_time)

# Decorator para logging automático de performance
def log_performance_decorator(module: str):
    """Decorator para logging automático de performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log_performance(module, func.__name__, execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log_error(module, func.__name__, f"Erro em {func.__name__}", 
                         {"args": str(args), "kwargs": str(kwargs)}, 
                         execution_time, error_details=str(e))
                raise
        return wrapper
    return decorator
