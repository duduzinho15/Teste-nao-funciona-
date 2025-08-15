#!/usr/bin/env python3
"""
Configuração de Produção para Sistema de Notificações RapidAPI

Este módulo implementa:
- Configuração multi-ambiente (dev, staging, produção)
- Configurações seguras para cada canal de notificação
- Validação de configurações
- Fallbacks para configurações ausentes
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import json

# Carrega variáveis de ambiente
load_dotenv()

@dataclass
class EmailConfig:
    """Configuração para notificações por email"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> Optional['EmailConfig']:
        """Cria configuração a partir de variáveis de ambiente"""
        smtp_server = os.getenv('SMTP_SERVER')
        if not smtp_server:
            return None
            
        return cls(
            smtp_server=smtp_server,
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            username=os.getenv('SMTP_USERNAME', ''),
            password=os.getenv('SMTP_PASSWORD', ''),
            from_email=os.getenv('FROM_EMAIL', 'noreply@apostapro.com'),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            use_ssl=os.getenv('SMTP_USE_SSL', 'false').lower() == 'true',
            timeout=int(os.getenv('SMTP_TIMEOUT', '30'))
        )

@dataclass
class SlackConfig:
    """Configuração para notificações Slack"""
    webhook_url: str
    channel: str = "#alerts"
    username: str = "RapidAPI Bot"
    icon_emoji: str = ":robot_face:"
    
    @classmethod
    def from_env(cls) -> Optional['SlackConfig']:
        """Cria configuração a partir de variáveis de ambiente"""
        webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        if not webhook_url:
            return None
            
        return cls(
            webhook_url=webhook_url,
            channel=os.getenv('SLACK_CHANNEL', '#alerts'),
            username=os.getenv('SLACK_USERNAME', 'RapidAPI Bot'),
            icon_emoji=os.getenv('SLACK_ICON_EMOJI', ':robot_face:')
        )

@dataclass
class DiscordConfig:
    """Configuração para notificações Discord"""
    webhook_url: str
    username: str = "RapidAPI Bot"
    avatar_url: str = ""
    
    @classmethod
    def from_env(cls) -> Optional['DiscordConfig']:
        """Cria configuração a partir de variáveis de ambiente"""
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            return None
            
        return cls(
            webhook_url=webhook_url,
            username=os.getenv('DISCORD_USERNAME', 'RapidAPI Bot'),
            avatar_url=os.getenv('DISCORD_AVATAR_URL', '')
        )

@dataclass
class TelegramConfig:
    """Configuração para notificações Telegram"""
    bot_token: str
    chat_id: str
    parse_mode: str = "HTML"
    
    @classmethod
    def from_env(cls) -> Optional['TelegramConfig']:
        """Cria configuração a partir de variáveis de ambiente"""
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return None
            
        return cls(
            bot_token=bot_token,
            chat_id=chat_id,
            parse_mode=os.getenv('TELEGRAM_PARSE_MODE', 'HTML')
        )

@dataclass
class DashboardConfig:
    """Configuração para dashboard web"""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    secret_key: str = ""
    cors_origins: List[str] = field(default_factory=list)
    rate_limit: int = 100  # Requisições por minuto
    max_connections: int = 1000
    
    @classmethod
    def from_env(cls) -> 'DashboardConfig':
        """Cria configuração a partir de variáveis de ambiente"""
        return cls(
            host=os.getenv('DASHBOARD_HOST', '0.0.0.0'),
            port=int(os.getenv('DASHBOARD_PORT', '8080')),
            debug=os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('DASHBOARD_SECRET_KEY', ''),
            cors_origins=os.getenv('DASHBOARD_CORS_ORIGINS', '').split(','),
            rate_limit=int(os.getenv('DASHBOARD_RATE_LIMIT', '100')),
            max_connections=int(os.getenv('DASHBOARD_MAX_CONNECTIONS', '1000'))
        )

@dataclass
class AlertConfig:
    """Configuração para sistema de alertas"""
    # Thresholds de performance
    success_rate_threshold: float = 80.0  # %
    response_time_threshold: float = 2.0  # segundos
    error_rate_threshold: float = 20.0    # %
    
    # Configurações de notificação
    alert_cooldown: int = 300  # segundos
    escalation_threshold: int = 3  # alertas antes de escalar
    critical_recipients: List[str] = field(default_factory=list)
    
    # Configurações de retry
    max_retries: int = 3
    retry_delay: int = 60  # segundos
    exponential_backoff: bool = True
    
    @classmethod
    def from_env(cls) -> 'AlertConfig':
        """Cria configuração a partir de variáveis de ambiente"""
        return cls(
            success_rate_threshold=float(os.getenv('ALERT_SUCCESS_RATE_THRESHOLD', '80.0')),
            response_time_threshold=float(os.getenv('ALERT_RESPONSE_TIME_THRESHOLD', '2.0')),
            error_rate_threshold=float(os.getenv('ALERT_ERROR_RATE_THRESHOLD', '20.0')),
            alert_cooldown=int(os.getenv('ALERT_COOLDOWN', '300')),
            escalation_threshold=int(os.getenv('ALERT_ESCALATION_THRESHOLD', '3')),
            critical_recipients=os.getenv('ALERT_CRITICAL_RECIPIENTS', '').split(','),
            max_retries=int(os.getenv('ALERT_MAX_RETRIES', '3')),
            retry_delay=int(os.getenv('ALERT_RETRY_DELAY', '60')),
            exponential_backoff=os.getenv('ALERT_EXPONENTIAL_BACKOFF', 'true').lower() == 'true'
        )

@dataclass
class ProductionConfig:
    """Configuração principal de produção"""
    environment: str = "development"
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "json"
    
    # Configurações de notificação
    email: Optional[EmailConfig] = None
    slack: Optional[SlackConfig] = None
    discord: Optional[DiscordConfig] = None
    telegram: Optional[TelegramConfig] = None
    
    # Configurações do sistema
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    
    # Configurações de cache
    cache_ttl: int = 3600  # 1 hora
    cache_max_size: int = 10000
    cache_cleanup_interval: int = 300  # 5 minutos
    
    # Configurações de monitoramento
    health_check_interval: int = 60  # segundos
    metrics_retention_hours: int = 24
    
    def __post_init__(self):
        """Valida e configura após inicialização"""
        self._setup_logging()
        self._load_notification_configs()
        self._validate_config()
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        log_level = getattr(logging, self.log_level.upper())
        
        # Configuração básica
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Log para arquivo se especificado
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(log_level)
            
            if self.log_format == "json":
                import json_logging
                formatter = json_logging.JSONRequestLogFormatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
    
    def _load_notification_configs(self):
        """Carrega configurações de notificação do ambiente"""
        self.email = EmailConfig.from_env()
        self.slack = SlackConfig.from_env()
        self.discord = DiscordConfig.from_env()
        self.telegram = TelegramConfig.from_env()
    
    def _validate_config(self):
        """Valida configuração"""
        if not any([self.email, self.slack, self.discord, self.telegram]):
            logging.warning("⚠️  Nenhum canal de notificação configurado!")
        
        if self.environment == "production":
            if not self.dashboard.secret_key:
                logging.warning("⚠️  Chave secreta não configurada para produção!")
            
            if self.dashboard.debug:
                logging.warning("⚠️  Modo debug ativado em produção!")
    
    def get_notification_channels(self) -> List[str]:
        """Retorna lista de canais de notificação disponíveis"""
        channels = []
        if self.email:
            channels.append("email")
        if self.slack:
            channels.append("slack")
        if self.discord:
            channels.append("discord")
        if self.telegram:
            channels.append("telegram")
        return channels
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário"""
        return {
            "environment": self.environment,
            "log_level": self.log_level,
            "notification_channels": self.get_notification_channels(),
            "dashboard": {
                "host": self.dashboard.host,
                "port": self.dashboard.port,
                "debug": self.dashboard.debug
            },
            "alerts": {
                "success_rate_threshold": self.alerts.success_rate_threshold,
                "response_time_threshold": self.alerts.response_time_threshold,
                "error_rate_threshold": self.alerts.error_rate_threshold
            }
        }
    
    def save_to_file(self, filepath: str):
        """Salva configuração em arquivo"""
        config_dict = self.to_dict()
        
        # Remove informações sensíveis
        if "password" in str(config_dict):
            config_dict = self._sanitize_sensitive_data(config_dict)
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        
        logging.info(f"✅ Configuração salva em: {filepath}")
    
    def _sanitize_sensitive_data(self, data: Any) -> Any:
        """Remove dados sensíveis da configuração"""
        if isinstance(data, dict):
            return {k: "***HIDDEN***" if "password" in k.lower() or "token" in k.lower() 
                   else self._sanitize_sensitive_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_sensitive_data(item) for item in data]
        else:
            return data

def load_production_config() -> ProductionConfig:
    """Carrega configuração de produção"""
    environment = os.getenv('ENVIRONMENT', 'development')
    
    config = ProductionConfig(
        environment=environment,
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        log_file=os.getenv('LOG_FILE'),
        log_format=os.getenv('LOG_FORMAT', 'json'),
        cache_ttl=int(os.getenv('CACHE_TTL', '3600')),
        cache_max_size=int(os.getenv('CACHE_MAX_SIZE', '10000')),
        cache_cleanup_interval=int(os.getenv('CACHE_CLEANUP_INTERVAL', '300')),
        health_check_interval=int(os.getenv('HEALTH_CHECK_INTERVAL', '60')),
        metrics_retention_hours=int(os.getenv('METRICS_RETENTION_HOURS', '24'))
    )
    
    return config

def create_env_template():
    """Cria template do arquivo .env"""
    template = """# Configuração de Produção - RapidAPI Notifications
# Copie este arquivo para .env e configure suas variáveis

# Ambiente
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FILE=logs/rapidapi.log
LOG_FORMAT=json

# Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=10000
CACHE_CLEANUP_INTERVAL=300

# Monitoramento
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_HOURS=24

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
FROM_EMAIL=noreply@apostapro.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT=30

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_CHANNEL=#alerts
SLACK_USERNAME=RapidAPI Bot
SLACK_ICON_EMOJI=:robot_face:

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_USERNAME=RapidAPI Bot
DISCORD_AVATAR_URL=

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
TELEGRAM_PARSE_MODE=HTML

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8080
DASHBOARD_DEBUG=false
DASHBOARD_SECRET_KEY=sua_chave_secreta_aqui
DASHBOARD_CORS_ORIGINS=http://localhost:3000,https://seu-dominio.com
DASHBOARD_RATE_LIMIT=100
DASHBOARD_MAX_CONNECTIONS=1000

# Alertas
ALERT_SUCCESS_RATE_THRESHOLD=80.0
ALERT_RESPONSE_TIME_THRESHOLD=2.0
ALERT_ERROR_RATE_THRESHOLD=20.0
ALERT_COOLDOWN=300
ALERT_ESCALATION_THRESHOLD=3
ALERT_CRITICAL_RECIPIENTS=admin@apostapro.com,emergency@apostapro.com
ALERT_MAX_RETRIES=3
ALERT_RETRY_DELAY=60
ALERT_EXPONENTIAL_BACKOFF=true
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("✅ Template .env criado: .env.template")
    print("📝 Configure suas variáveis e renomeie para .env")

if __name__ == "__main__":
    # Cria template do .env
    create_env_template()
    
    # Carrega configuração de exemplo
    config = load_production_config()
    
    print("\n📊 Configuração Carregada:")
    print(f"   Ambiente: {config.environment}")
    print(f"   Canais de Notificação: {config.get_notification_channels()}")
    print(f"   Dashboard: {config.dashboard.host}:{config.dashboard.port}")
    print(f"   Log Level: {config.log_level}")
    
    # Salva configuração sanitizada
    config.save_to_file('config_exemplo.json')
