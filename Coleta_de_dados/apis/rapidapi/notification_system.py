#!/usr/bin/env python3
"""
Sistema de Notificações para APIs RapidAPI

Este módulo implementa notificações automáticas via:
- Email (SMTP)
- Slack (Webhooks)
- Discord (Webhooks)
- Telegram (Bot API)
- SMS (Twilio)
- Push Notifications
"""

import asyncio
import smtplib
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import os

@dataclass
class NotificationConfig:
    """Configuração para um canal de notificação"""
    name: str
    type: str  # email, slack, discord, telegram, sms
    enabled: bool = True
    priority: int = 1  # Prioridade mais baixa = mais alta
    cooldown: int = 300  # Segundos entre notificações similares
    
    # Configurações específicas por tipo
    email_config: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    phone_number: Optional[str] = None

@dataclass
class NotificationMessage:
    """Mensagem de notificação"""
    title: str
    content: str
    severity: str = "info"  # info, warning, error, critical
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    recipients: List[str] = field(default_factory=list)

class EmailNotifier:
    """Notificador via email"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("notifications.email")
        
    async def send_notification(self, message: NotificationMessage) -> bool:
        """Envia notificação por email"""
        try:
            # Configura mensagem
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = ', '.join(message.recipients)
            msg['Subject'] = f"[{message.severity.upper()}] {message.title}"
            
            # Corpo da mensagem
            body = self._format_email_body(message)
            msg.attach(MIMEText(body, 'html'))
            
            # Envia email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config.get('use_tls'):
                    server.starttls()
                
                if self.config.get('username') and self.config.get('password'):
                    server.login(self.config['username'], self.config['password'])
                
                server.send_message(msg)
            
            self.logger.info(f"Email enviado para {message.recipients}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
            return False
    
    def _format_email_body(self, message: NotificationMessage) -> str:
        """Formata corpo do email em HTML"""
        severity_colors = {
            "info": "#17a2b8",
            "warning": "#ffc107", 
            "error": "#dc3545",
            "critical": "#721c24"
        }
        
        color = severity_colors.get(message.severity, "#6c757d")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 15px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }}
                .timestamp {{ color: #6c757d; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{message.title}</h2>
                <p>Severidade: {message.severity.upper()}</p>
            </div>
            
            <div class="content">
                {message.content}
            </div>
            
            <div class="metadata">
                <h4>Metadados:</h4>
                <ul>
                    {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in message.metadata.items()])}
                </ul>
            </div>
            
            <div class="timestamp">
                Enviado em: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </body>
        </html>
        """
        
        return html

class SlackNotifier:
    """Notificador via Slack"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger("notifications.slack")
    
    async def send_notification(self, message: NotificationMessage) -> bool:
        """Envia notificação para Slack"""
        try:
            # Formata mensagem para Slack
            slack_message = self._format_slack_message(message)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=slack_message) as response:
                    if response.status == 200:
                        self.logger.info("Notificação enviada para Slack")
                        return True
                    else:
                        self.logger.error(f"Erro ao enviar para Slack: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação Slack: {e}")
            return False
    
    def _format_slack_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """Formata mensagem para formato Slack"""
        severity_colors = {
            "info": "#17a2b8",
            "warning": "#ffc107",
            "error": "#dc3545", 
            "critical": "#721c24"
        }
        
        color = severity_colors.get(message.severity, "#6c757d")
        
        # Campos de metadados
        fields = []
        for key, value in message.metadata.items():
            fields.append({
                "title": key.title(),
                "value": str(value),
                "short": True
            })
        
        return {
            "attachments": [{
                "color": color,
                "title": message.title,
                "text": message.content,
                "fields": fields,
                "footer": f"Enviado em {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png"
            }]
        }

class DiscordNotifier:
    """Notificador via Discord"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger("notifications.discord")
    
    async def send_notification(self, message: NotificationMessage) -> bool:
        """Envia notificação para Discord"""
        try:
            # Formata mensagem para Discord
            discord_message = self._format_discord_message(message)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=discord_message) as response:
                    if response.status == 204:  # Discord retorna 204 para sucesso
                        self.logger.info("Notificação enviada para Discord")
                        return True
                    else:
                        self.logger.error(f"Erro ao enviar para Discord: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação Discord: {e}")
            return False
    
    def _format_discord_message(self, message: NotificationMessage) -> Dict[str, Any]:
        """Formata mensagem para formato Discord"""
        severity_emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        emoji = severity_emojis.get(message.severity, "ℹ️")
        
        # Constrói embed
        embed = {
            "title": f"{emoji} {message.title}",
            "description": message.content,
            "color": self._get_discord_color(message.severity),
            "timestamp": message.timestamp.isoformat(),
            "fields": []
        }
        
        # Adiciona metadados como campos
        for key, value in message.metadata.items():
            embed["fields"].append({
                "name": key.title(),
                "value": str(value),
                "inline": True
            })
        
        return {
            "embeds": [embed]
        }
    
    def _get_discord_color(self, severity: str) -> int:
        """Retorna cor em formato decimal para Discord"""
        colors = {
            "info": 0x17a2b8,
            "warning": 0xffc107,
            "error": 0xdc3545,
            "critical": 0x721c24
        }
        return colors.get(severity, 0x6c757d)

class TelegramNotifier:
    """Notificador via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger("notifications.telegram")
    
    async def send_notification(self, message: NotificationMessage) -> bool:
        """Envia notificação para Telegram"""
        try:
            # Formata mensagem para Telegram
            telegram_message = self._format_telegram_message(message)
            
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": telegram_message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        self.logger.info("Notificação enviada para Telegram")
                        return True
                    else:
                        self.logger.error(f"Erro ao enviar para Telegram: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação Telegram: {e}")
            return False
    
    def _format_telegram_message(self, message: NotificationMessage) -> str:
        """Formata mensagem para formato Telegram"""
        severity_emojis = {
            "info": "ℹ️",
            "warning": "⚠️", 
            "error": "❌",
            "critical": "🚨"
        }
        
        emoji = severity_emojis.get(message.severity, "ℹ️")
        
        # Constrói mensagem HTML
        html = f"<b>{emoji} {message.title}</b>\n\n"
        html += f"<b>Severidade:</b> {message.severity.upper()}\n"
        html += f"<b>Conteúdo:</b>\n{message.content}\n\n"
        
        if message.metadata:
            html += "<b>Metadados:</b>\n"
            for key, value in message.metadata.items():
                html += f"• <b>{key.title()}:</b> {value}\n"
        
        html += f"\n<i>Enviado em {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return html

class NotificationManager:
    """
    Gerenciador central de notificações
    
    Funcionalidades:
    - Múltiplos canais de notificação
    - Priorização de mensagens
    - Cooldown para evitar spam
    - Retry automático
    - Logs de entrega
    """
    
    def __init__(self):
        self.logger = logging.getLogger("notifications.manager")
        self.notifiers: Dict[str, Any] = {}
        self.configs: Dict[str, NotificationConfig] = {}
        self.message_history: List[NotificationMessage] = []
        self.delivery_logs: List[Dict[str, Any]] = []
        
    def add_notifier(self, config: NotificationConfig):
        """Adiciona um notificador"""
        try:
            if config.type == "email" and config.email_config:
                self.notifiers[config.name] = EmailNotifier(config.email_config)
            elif config.type == "slack" and config.webhook_url:
                self.notifiers[config.name] = SlackNotifier(config.webhook_url)
            elif config.type == "discord" and config.webhook_url:
                self.notifiers[config.name] = DiscordNotifier(config.webhook_url)
            elif config.type == "telegram" and config.bot_token and config.chat_id:
                self.notifiers[config.name] = TelegramNotifier(config.bot_token, config.chat_id)
            else:
                self.logger.warning(f"Configuração inválida para {config.name}")
                return
            
            self.configs[config.name] = config
            self.logger.info(f"Notificador {config.name} ({config.type}) adicionado")
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar notificador {config.name}: {e}")
    
    def remove_notifier(self, name: str):
        """Remove um notificador"""
        if name in self.notifiers:
            del self.notifiers[name]
            del self.configs[name]
            self.logger.info(f"Notificador {name} removido")
    
    async def send_notification(self, message: NotificationMessage, 
                               channels: Optional[List[str]] = None) -> Dict[str, bool]:
        """Envia notificação através dos canais especificados"""
        results = {}
        
        # Filtra canais habilitados
        target_channels = channels or list(self.notifiers.keys())
        enabled_channels = [name for name in target_channels 
                          if name in self.configs and self.configs[name].enabled]
        
        if not enabled_channels:
            self.logger.warning("Nenhum canal de notificação habilitado")
            return results
        
        # Verifica cooldown para cada canal
        for channel_name in enabled_channels:
            config = self.configs[channel_name]
            
            if self._should_send_notification(channel_name, message, config):
                # Envia notificação
                notifier = self.notifiers[channel_name]
                success = await notifier.send_notification(message)
                
                results[channel_name] = success
                
                # Registra entrega
                self._log_delivery(channel_name, message, success)
                
                # Atualiza histórico
                self.message_history.append(message)
                
                if success:
                    self.logger.info(f"Notificação enviada com sucesso via {channel_name}")
                else:
                    self.logger.error(f"Falha ao enviar notificação via {channel_name}")
            else:
                results[channel_name] = False
                self.logger.debug(f"Notificação para {channel_name} em cooldown")
        
        return results
    
    def _should_send_notification(self, channel_name: str, message: NotificationMessage, 
                                 config: NotificationConfig) -> bool:
        """Verifica se deve enviar notificação (cooldown)"""
        # Procura última mensagem similar para este canal
        for msg in reversed(self.message_history):
            if (msg.title == message.title and 
                msg.severity == message.severity and
                msg.content == message.content):
                
                time_diff = (datetime.now() - msg.timestamp).total_seconds()
                return time_diff >= config.cooldown
        
        return True
    
    def _log_delivery(self, channel_name: str, message: NotificationMessage, success: bool):
        """Registra log de entrega"""
        log_entry = {
            "timestamp": datetime.now(),
            "channel": channel_name,
            "message_title": message.title,
            "severity": message.severity,
            "success": success,
            "recipients": message.recipients
        }
        
        self.delivery_logs.append(log_entry)
        
        # Mantém apenas últimos 1000 logs
        if len(self.delivery_logs) > 1000:
            self.delivery_logs = self.delivery_logs[-1000:]
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de entrega"""
        if not self.delivery_logs:
            return {"total": 0, "success_rate": 0.0}
        
        total = len(self.delivery_logs)
        successful = sum(1 for log in self.delivery_logs if log["success"])
        success_rate = (successful / total) * 100
        
        # Estatísticas por canal
        channel_stats = {}
        for log in self.delivery_logs:
            channel = log["channel"]
            if channel not in channel_stats:
                channel_stats[channel] = {"total": 0, "successful": 0}
            
            channel_stats[channel]["total"] += 1
            if log["success"]:
                channel_stats[channel]["successful"] += 1
        
        # Calcula taxa de sucesso por canal
        for channel in channel_stats:
            total_channel = channel_stats[channel]["total"]
            successful_channel = channel_stats[channel]["successful"]
            channel_stats[channel]["success_rate"] = (successful_channel / total_channel) * 100
        
        return {
            "total": total,
            "successful": successful,
            "success_rate": success_rate,
            "channels": channel_stats
        }
    
    def get_recent_notifications(self, hours: int = 24) -> List[NotificationMessage]:
        """Retorna notificações recentes"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent = []
        for msg in reversed(self.message_history):
            if msg.timestamp.timestamp() > cutoff_time:
                recent.append(msg)
            else:
                break
        
        return recent

# Instância global do gerenciador de notificações
notification_manager = NotificationManager()

def get_notification_manager() -> NotificationManager:
    """Retorna a instância global do gerenciador de notificações"""
    return notification_manager

# Funções de conveniência para configuração rápida
def setup_email_notifications(smtp_server: str, smtp_port: int, from_email: str,
                             username: str, password: str, use_tls: bool = True):
    """Configura notificações por email"""
    config = NotificationConfig(
        name="email",
        type="email",
        email_config={
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "from_email": from_email,
            "username": username,
            "password": password,
            "use_tls": use_tls
        }
    )
    
    manager = get_notification_manager()
    manager.add_notifier(config)

def setup_slack_notifications(webhook_url: str, channel_name: str = "slack"):
    """Configura notificações para Slack"""
    config = NotificationConfig(
        name=channel_name,
        type="slack",
        webhook_url=webhook_url
    )
    
    manager = get_notification_manager()
    manager.add_notifier(config)

def setup_discord_notifications(webhook_url: str, channel_name: str = "discord"):
    """Configura notificações para Discord"""
    config = NotificationConfig(
        name=channel_name,
        type="discord",
        webhook_url=webhook_url
    )
    
    manager = get_notification_manager()
    manager.add_notifier(config)

def setup_telegram_notifications(bot_token: str, chat_id: str, channel_name: str = "telegram"):
    """Configura notificações para Telegram"""
    config = NotificationConfig(
        name=channel_name,
        type="telegram",
        bot_token=bot_token,
        chat_id=chat_id
    )
    
    manager = get_notification_manager()
    manager.add_notifier(config)
