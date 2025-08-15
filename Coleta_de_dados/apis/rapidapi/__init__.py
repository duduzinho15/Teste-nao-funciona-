#!/usr/bin/env python3
"""
Sistema Completo RapidAPI para ApostaPro

Este módulo implementa um sistema completo de integração com APIs RapidAPI,
incluindo cache inteligente, fallback automático, monitoramento de performance,
sistema de notificações, dashboard web e sistema de alertas para produção.

Funcionalidades Principais:
- Cache inteligente com TTL e estatísticas
- Sistema de fallback automático entre APIs
- Monitoramento de performance em tempo real
- Sistema de notificações multi-canal
- Dashboard web para monitoramento
- Sistema de alertas automáticos para produção
- Configuração robusta para múltiplos ambientes

APIs Disponíveis:
- Today Football Prediction
- Soccer Football Info
- Sportspage Feeds
- Football Prediction
- Pinnacle Odds
- Football Pro
- SportAPI7

Módulos de Produção:
- Configuração multi-ambiente
- Dashboard otimizado para produção
- Sistema de alertas automáticos
- Rate limiting e segurança
- Logs estruturados
"""

# APIs RapidAPI
from .today_football_prediction import TodayFootballPredictionAPI
from .soccer_football_info import SoccerFootballInfoAPI
from .sportspage_feeds import SportspageFeedsAPI
from .football_prediction import FootballPredictionAPI
from .pinnacle_odds import PinnacleOddsAPI
from .football_pro import FootballProAPI
from .sportapi7 import SportAPI7

# Sistema de cache
from .base_rapidapi import (
    RapidAPIBase,
    RapidAPICache,
    CacheEntry
)

# Sistema de fallback
from .fallback_manager import (
    APIFallbackManager,
    APIFallbackConfig,
    APIStatus,
    get_fallback_manager
)

# Monitor de performance
from .performance_monitor import (
    PerformanceMonitor,
    PerformanceMetrics,
    AlertThreshold,
    monitor_performance,
    get_performance_monitor
)

# Sistema de notificações
from .notification_system import (
    NotificationManager,
    NotificationMessage,
    NotificationConfig,
    EmailNotifier,
    SlackNotifier,
    DiscordNotifier,
    TelegramNotifier,
    get_notification_manager,
    setup_email_notifications,
    setup_slack_notifications,
    setup_discord_notifications,
    setup_telegram_notifications
)

# Dashboard web
from .web_dashboard import (
    RapidAPIDashboard,
    DashboardConfig,
    start_dashboard
)

# Módulos de produção
try:
    from .production_config import (
        ProductionConfig,
        EmailConfig,
        SlackConfig,
        DiscordConfig,
        TelegramConfig,
        DashboardConfig as ProdDashboardConfig,
        AlertConfig,
        load_production_config,
        create_env_template
    )
except ImportError:
    # Fallback para quando os módulos de produção não estiverem disponíveis
    ProductionConfig = None
    EmailConfig = None
    SlackConfig = None
    DiscordConfig = None
    TelegramConfig = None
    ProdDashboardConfig = None
    AlertConfig = None
    load_production_config = lambda: {}
    create_env_template = lambda: {}

try:
    from .dashboard_producao import (
        ProductionDashboard,
        RateLimiter,
        start_production_dashboard
    )
except ImportError:
    # Fallback para quando os módulos de produção não estiverem disponíveis
    ProductionDashboard = None
    RateLimiter = None
    start_production_dashboard = lambda: None

try:
    from .alert_system import (
        AlertManager,
        AlertRule,
        Alert,
        AlertSeverity,
        AlertStatus,
        get_alert_manager,
        add_custom_alert_rule,
        trigger_manual_alert
    )
except ImportError:
    # Fallback para quando os módulos de produção não estiverem disponíveis
    AlertManager = None
    AlertRule = None
    Alert = None
    AlertSeverity = None
    AlertStatus = None
    get_alert_manager = lambda: None
    add_custom_alert_rule = lambda: None
    trigger_manual_alert = lambda: None

__all__ = [
    # APIs RapidAPI
    "TodayFootballPredictionAPI",
    "SoccerFootballInfoAPI",
    "SportspageFeedsAPI",
    "FootballPredictionAPI",
    "PinnacleOddsAPI",
    "FootballProAPI",
    "SportAPI7",
    
    # Sistema de cache
    "RapidAPIBase",
    "RapidAPICache",
    "CacheEntry",
    
    # Sistema de fallback
    "APIFallbackManager",
    "APIFallbackConfig",
    "APIStatus",
    "get_fallback_manager",
    
    # Monitor de performance
    "PerformanceMonitor",
    "PerformanceMetrics",
    "AlertThreshold",
    "monitor_performance",
    "get_performance_monitor",
    
    # Sistema de notificações
    "NotificationManager",
    "NotificationMessage",
    "NotificationConfig",
    "EmailNotifier",
    "SlackNotifier",
    "DiscordNotifier",
    "TelegramNotifier",
    "get_notification_manager",
    "setup_email_notifications",
    "setup_slack_notifications",
    "setup_discord_notifications",
    "setup_telegram_notifications",
    
    # Dashboard web
    "RapidAPIDashboard",
    "DashboardConfig",
    "start_dashboard",
    
    # Módulos de produção
    "ProductionConfig",
    "EmailConfig",
    "SlackConfig",
    "DiscordConfig",
    "TelegramConfig",
    "ProdDashboardConfig",
    "AlertConfig",
    "load_production_config",
    "create_env_template",
    
    "ProductionDashboard",
    "RateLimiter",
    "start_production_dashboard",
    
    "AlertManager",
    "AlertRule",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "get_alert_manager",
    "add_custom_alert_rule",
    "trigger_manual_alert"
]

__version__ = "2.0.0"
__author__ = "ApostaPro Team"
__description__ = "Sistema Completo RapidAPI com Funcionalidades de Produção"
