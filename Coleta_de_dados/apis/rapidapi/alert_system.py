#!/usr/bin/env python3
"""
Sistema de Alertas Automáticos para RapidAPI

Este módulo implementa:
- Thresholds configuráveis para diferentes métricas
- Escalação automática de alertas
- Notificações inteligentes baseadas em severidade
- Sistema de retry com backoff exponencial
- Integração com sistema de notificações
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import json

# Importa módulos do sistema
from .production_config import load_production_config
from .notification_system import get_notification_manager, NotificationMessage
from .performance_monitor import get_performance_monitor

class AlertSeverity(Enum):
    """Níveis de severidade dos alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status dos alertas"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    metric: str  # success_rate, response_time, error_rate, etc.
    threshold: float
    operator: str  # >, <, >=, <=, ==, !=
    severity: AlertSeverity
    description: str
    cooldown_seconds: int = 300  # 5 minutos
    escalation_threshold: int = 3  # Alertas antes de escalar
    escalation_delay: int = 1800  # 30 minutos
    enabled: bool = True
    
    def evaluate(self, value: float) -> bool:
        """Avalia se o valor dispara o alerta"""
        if not self.enabled:
            return False
            
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "!=":
            return value != self.threshold
        else:
            return False

@dataclass
class Alert:
    """Alerta individual"""
    id: str
    rule: AlertRule
    value: float
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    escalation_count: int = 0
    last_escalation: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte alerta para dicionário"""
        return {
            "id": self.id,
            "rule_name": self.rule.name,
            "metric": self.rule.metric,
            "threshold": self.rule.threshold,
            "operator": self.rule.operator,
            "value": self.value,
            "severity": self.rule.severity.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "escalation_count": self.escalation_count,
            "last_escalation": self.last_escalation.isoformat() if self.last_escalation else None
        }

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.config = load_production_config()
        self.notification_manager = get_notification_manager()
        self.performance_monitor = get_performance_monitor()
        self.logger = logging.getLogger("alerts.manager")
        
        # Estado dos alertas
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        
        # Configurações
        self.escalation_callbacks: List[Callable] = []
        self.auto_resolve_enabled = True
        self.auto_resolve_threshold = 3600  # 1 hora
        
        # Inicializa regras padrão
        self._setup_default_rules()
        
        # Inicia monitoramento automático
        self._start_monitoring()
    
    def _setup_default_rules(self):
        """Configura regras de alerta padrão"""
        default_rules = [
            AlertRule(
                name="Taxa de Sucesso Baixa",
                metric="success_rate",
                threshold=80.0,
                operator="<",
                severity=AlertSeverity.WARNING,
                description="Taxa de sucesso abaixo de 80%",
                cooldown_seconds=300
            ),
            AlertRule(
                name="Taxa de Sucesso Crítica",
                metric="success_rate",
                threshold=60.0,
                operator="<",
                severity=AlertSeverity.CRITICAL,
                description="Taxa de sucesso abaixo de 60%",
                cooldown_seconds=60,
                escalation_threshold=2
            ),
            AlertRule(
                name="Tempo de Resposta Alto",
                metric="response_time",
                threshold=2.0,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="Tempo de resposta acima de 2 segundos",
                cooldown_seconds=300
            ),
            AlertRule(
                name="Tempo de Resposta Crítico",
                metric="response_time",
                threshold=5.0,
                operator=">",
                severity=AlertSeverity.CRITICAL,
                description="Tempo de resposta acima de 5 segundos",
                cooldown_seconds=60
            ),
            AlertRule(
                name="Taxa de Erro Alta",
                metric="error_rate",
                threshold=20.0,
                operator=">",
                severity=AlertSeverity.WARNING,
                description="Taxa de erro acima de 20%",
                cooldown_seconds=300
            ),
            AlertRule(
                name="Taxa de Erro Crítica",
                metric="error_rate",
                threshold=40.0,
                operator=">",
                severity=AlertSeverity.CRITICAL,
                description="Taxa de erro acima de 40%",
                cooldown_seconds=60,
                escalation_threshold=2
            )
        ]
        
        for rule in default_rules:
            self.add_alert_rule(rule)
    
    def add_alert_rule(self, rule: AlertRule):
        """Adiciona regra de alerta"""
        self.alert_rules.append(rule)
        self.logger.info(f"✅ Regra de alerta adicionada: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """Remove regra de alerta"""
        self.alert_rules = [r for r in self.alert_rules if r.name != rule_name]
        self.logger.info(f"🗑️  Regra de alerta removida: {rule_name}")
    
    def add_escalation_callback(self, callback: Callable):
        """Adiciona callback para escalação"""
        self.escalation_callbacks.append(callback)
        self.logger.info("✅ Callback de escalação adicionado")
    
    def _start_monitoring(self):
        """Inicia monitoramento automático"""
        # Não inicia automaticamente - será iniciado quando necessário
        self.logger.info("🔄 Monitoramento automático configurado")
    
    async def start_monitoring(self):
        """Inicia monitoramento quando chamado explicitamente"""
        asyncio.create_task(self._monitor_loop())
        self.logger.info("🔄 Monitoramento automático iniciado")
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while True:
            try:
                await self._check_alerts()
                await asyncio.sleep(30)  # Verifica a cada 30 segundos
            except Exception as e:
                self.logger.error(f"❌ Erro no loop de monitoramento: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self):
        """Verifica todas as regras de alerta"""
        try:
            # Obtém métricas atuais
            performance_summary = self.performance_monitor.get_performance_summary()
            
            for rule in self.alert_rules:
                await self._evaluate_rule(rule, performance_summary)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar alertas: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule, performance_summary: Dict[str, Any]):
        """Avalia uma regra específica"""
        try:
            # Obtém valor da métrica
            metric_value = self._get_metric_value(rule.metric, performance_summary)
            
            if metric_value is None:
                return
            
            # Verifica se dispara alerta
            if rule.evaluate(metric_value):
                await self._trigger_alert(rule, metric_value, performance_summary)
            else:
                # Verifica se deve resolver alerta ativo
                await self._check_resolve_alert(rule, metric_value)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao avaliar regra {rule.name}: {e}")
    
    def _get_metric_value(self, metric: str, performance_summary: Dict[str, Any]) -> Optional[float]:
        """Obtém valor de uma métrica específica"""
        if metric == "success_rate":
            return performance_summary.get("overall_success_rate", 0)
        elif metric == "response_time":
            # Média dos tempos de resposta
            apis_data = performance_summary.get("apis_by_performance", [])
            if apis_data:
                response_times = [api.get("average_response_time", 0) for api in apis_data]
                return sum(response_times) / len(response_times) if response_times else 0
            return 0
        elif metric == "error_rate":
            # Calcula taxa de erro baseada na taxa de sucesso
            success_rate = performance_summary.get("overall_success_rate", 0)
            return 100 - success_rate
        else:
            return None
    
    async def _trigger_alert(self, rule: AlertRule, value: float, context: Dict[str, Any]):
        """Dispara um alerta"""
        try:
            # Verifica cooldown
            if self._is_in_cooldown(rule):
                return
            
            # Cria mensagem do alerta
            message = self._format_alert_message(rule, value, context)
            
            # Cria alerta
            alert = Alert(
                id=f"{rule.name}_{int(time.time())}",
                rule=rule,
                value=value,
                message=message,
                timestamp=datetime.now()
            )
            
            # Adiciona aos alertas ativos
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
            
            # Envia notificação
            await self._send_alert_notification(alert)
            
            # Log do alerta
            self.logger.warning(f"🚨 ALERTA DISPARADO: {rule.name} - {message}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao disparar alerta {rule.name}: {e}")
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Verifica se a regra está em cooldown"""
        now = datetime.now()
        
        # Procura alertas recentes para esta regra
        for alert in self.active_alerts.values():
            if (alert.rule.name == rule.name and 
                alert.status == AlertStatus.ACTIVE and
                (now - alert.timestamp).total_seconds() < rule.cooldown_seconds):
                return True
        
        return False
    
    def _format_alert_message(self, rule: AlertRule, value: float, context: Dict[str, Any]) -> str:
        """Formata mensagem do alerta"""
        if rule.metric == "success_rate":
            return f"Taxa de sucesso em {value:.1f}% (threshold: {rule.threshold}%)"
        elif rule.metric == "response_time":
            return f"Tempo de resposta em {value:.3f}s (threshold: {rule.threshold}s)"
        elif rule.metric == "error_rate":
            return f"Taxa de erro em {value:.1f}% (threshold: {rule.threshold}%)"
        else:
            return f"Valor {value} {rule.operator} {rule.threshold}"
    
    async def _send_alert_notification(self, alert: Alert):
        """Envia notificação do alerta"""
        try:
            # Cria mensagem de notificação
            notification = NotificationMessage(
                title=f"🚨 Alerta: {alert.rule.name}",
                content=alert.message,
                severity=alert.rule.severity.value,
                metadata={
                    "alert_id": alert.id,
                    "metric": alert.rule.metric,
                    "value": alert.value,
                    "threshold": alert.rule.threshold,
                    "operator": alert.rule.operator,
                    "timestamp": alert.timestamp.isoformat()
                }
            )
            
            # Envia notificação
            results = await self.notification_manager.send_notification(notification)
            
            # Log dos resultados
            for channel, success in results.items():
                if success:
                    self.logger.info(f"✅ Notificação enviada via {channel}")
                else:
                    self.logger.error(f"❌ Falha ao enviar notificação via {channel}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação: {e}")
    
    async def _check_resolve_alert(self, rule: AlertRule, current_value: float):
        """Verifica se deve resolver alerta ativo"""
        if not self.auto_resolve_enabled:
            return
        
        # Procura alertas ativos para esta regra
        for alert_id, alert in list(self.active_alerts.items()):
            if (alert.rule.name == rule.name and 
                alert.status == AlertStatus.ACTIVE):
                
                # Verifica se o valor voltou ao normal
                if not rule.evaluate(current_value):
                    await self._resolve_alert(alert_id, "Auto-resolvido")
    
    async def _resolve_alert(self, alert_id: str, resolved_by: str):
        """Resolve um alerta"""
        if alert_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.now()
        
        # Remove dos alertas ativos
        del self.active_alerts[alert_id]
        
        # Log da resolução
        self.logger.info(f"✅ Alerta resolvido: {alert.rule.name} por {resolved_by}")
        
        # Envia notificação de resolução
        await self._send_resolution_notification(alert)
    
    async def _send_resolution_notification(self, alert: Alert):
        """Envia notificação de resolução"""
        try:
            notification = NotificationMessage(
                title=f"✅ Alerta Resolvido: {alert.rule.name}",
                content=f"Alerta foi resolvido por {alert.resolved_by}",
                severity="info",
                metadata={
                    "alert_id": alert.id,
                    "resolved_by": alert.resolved_by,
                    "resolved_at": alert.resolved_at.isoformat(),
                    "duration_minutes": int((alert.resolved_at - alert.timestamp).total_seconds() / 60)
                }
            )
            
            await self.notification_manager.send_notification(notification)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar notificação de resolução: {e}")
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Reconhece um alerta"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()
        
        self.logger.info(f"👁️  Alerta reconhecido: {alert.rule.name} por {acknowledged_by}")
        return True
    
    async def escalate_alert(self, alert_id: str):
        """Escala um alerta"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.escalation_count += 1
        alert.last_escalation = datetime.now()
        
        # Verifica se deve escalar baseado na regra
        if alert.escalation_count >= alert.rule.escalation_threshold:
            alert.status = AlertStatus.ESCALATED
            
            # Executa callbacks de escalação
            for callback in self.escalation_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"❌ Erro no callback de escalação: {e}")
            
            self.logger.warning(f"🚨 ALERTA ESCALADO: {alert.rule.name} (escalação #{alert.escalation_count})")
        
        return True
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Retorna alertas ativos"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.rule.severity == severity]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Retorna histórico de alertas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos alertas"""
        total_alerts = len(self.alert_history)
        active_alerts = len(self.active_alerts)
        
        # Estatísticas por severidade
        severity_stats = {}
        for severity in AlertSeverity:
            count = len([a for a in self.active_alerts.values() if a.rule.severity == severity])
            severity_stats[severity.value] = count
        
        # Estatísticas por status
        status_stats = {}
        for status in AlertStatus:
            count = len([a for a in self.active_alerts.values() if a.status == status])
            status_stats[status.value] = count
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "severity_distribution": severity_stats,
            "status_distribution": status_stats,
            "rules_count": len(self.alert_rules)
        }
    
    def export_alerts(self, filepath: str):
        """Exporta alertas para arquivo JSON"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "active_alerts": [alert.to_dict() for alert in self.active_alerts.values()],
                "recent_history": [alert.to_dict() for alert in self.get_alert_history(24)],
                "stats": self.get_alert_stats()
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"✅ Alertas exportados para: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao exportar alertas: {e}")

# Instância global do gerenciador de alertas
alert_manager = AlertManager()

def get_alert_manager() -> AlertManager:
    """Retorna a instância global do gerenciador de alertas"""
    return alert_manager

# Funções de conveniência
async def add_custom_alert_rule(name: str, metric: str, threshold: float, 
                               operator: str, severity: str, description: str):
    """Adiciona regra de alerta customizada"""
    manager = get_alert_manager()
    
    rule = AlertRule(
        name=name,
        metric=metric,
        threshold=threshold,
        operator=operator,
        severity=AlertSeverity(severity),
        description=description
    )
    
    manager.add_alert_rule(rule)
    return rule

async def trigger_manual_alert(name: str, message: str, severity: str = "warning"):
    """Dispara alerta manual"""
    manager = get_alert_manager()
    
    # Cria regra temporária
    rule = AlertRule(
        name=name,
        metric="manual",
        threshold=0,
        operator="==",
        severity=AlertSeverity(severity),
        description="Alerta manual",
        cooldown_seconds=0
    )
    
    # Cria alerta
    alert = Alert(
        id=f"manual_{int(time.time())}",
        rule=rule,
        value=0,
        message=message,
        timestamp=datetime.now()
    )
    
    # Adiciona aos alertas ativos
    manager.active_alerts[alert.id] = alert
    manager.alert_history.append(alert)
    
    # Envia notificação
    await manager._send_alert_notification(alert)
    
    return alert

if __name__ == "__main__":
    # Demonstração do sistema de alertas
    async def demo_alert_system():
        """Demonstra o sistema de alertas"""
        print("🚨 Demonstração do Sistema de Alertas")
        print("=" * 50)
        
        manager = get_alert_manager()
        
        # Mostra regras configuradas
        print(f"📋 Regras configuradas: {len(manager.alert_rules)}")
        for rule in manager.alert_rules:
            print(f"  • {rule.name}: {rule.metric} {rule.operator} {rule.threshold}")
        
        # Mostra estatísticas
        stats = manager.get_alert_stats()
        print(f"\n📊 Estatísticas:")
        print(f"  • Total de alertas: {stats['total_alerts']}")
        print(f"  • Alertas ativos: {stats['active_alerts']}")
        print(f"  • Regras: {stats['rules_count']}")
        
        # Simula alerta manual
        print(f"\n🔔 Disparando alerta manual...")
        alert = await trigger_manual_alert(
            "Teste Manual",
            "Este é um alerta de teste do sistema",
            "info"
        )
        
        print(f"✅ Alerta criado: {alert.id}")
        
        # Mostra alertas ativos
        active_alerts = manager.get_active_alerts()
        print(f"\n🚨 Alertas ativos: {len(active_alerts)}")
        for alert in active_alerts:
            print(f"  • {alert.rule.name}: {alert.message}")
    
    asyncio.run(demo_alert_system())
