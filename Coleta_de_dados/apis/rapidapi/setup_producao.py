#!/usr/bin/env python3
"""
Script de Configuração Rápida para Sistema de Produção

Este script facilita:
- Criação do arquivo .env
- Configuração de notificações
- Validação de configurações
- Teste de conectividade
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional

def criar_arquivo_env():
    """Cria arquivo .env com configurações padrão"""
    env_content = """# Configuração de Produção - RapidAPI Notifications
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

# Email (SMTP) - Configure com suas credenciais
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
FROM_EMAIL=noreply@apostapro.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT=30

# Slack - Configure com seu webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_CHANNEL=#alerts
SLACK_USERNAME=RapidAPI Bot
SLACK_ICON_EMOJI=:robot_face:

# Discord - Configure com seu webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_USERNAME=RapidAPI Bot
DISCORD_AVATAR_URL=

# Telegram - Configure com seu bot
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
    
    env_path = Path('.env')
    if env_path.exists():
        print("⚠️  Arquivo .env já existe!")
        overwrite = input("Deseja sobrescrever? (y/N): ").lower()
        if overwrite != 'y':
            print("❌ Configuração cancelada")
            return False
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com sucesso!")
    print("📝 Configure suas variáveis e execute novamente para testar")
    return True

def configurar_email():
    """Configura notificações por email"""
    print("\n📧 Configuração de Email:")
    print("-" * 30)
    
    smtp_server = input("Servidor SMTP (ex: smtp.gmail.com): ").strip()
    if not smtp_server:
        return False
    
    smtp_port = input("Porta SMTP (ex: 587): ").strip() or "587"
    username = input("Email: ").strip()
    password = input("Senha/App Password: ").strip()
    from_email = input("Email de origem (ex: noreply@apostapro.com): ").strip()
    
    # Atualiza .env
    atualizar_env({
        'SMTP_SERVER': smtp_server,
        'SMTP_PORT': smtp_port,
        'SMTP_USERNAME': username,
        'SMTP_PASSWORD': password,
        'FROM_EMAIL': from_email
    })
    
    print("✅ Email configurado!")
    return True

def configurar_slack():
    """Configura notificações Slack"""
    print("\n💬 Configuração do Slack:")
    print("-" * 30)
    
    webhook_url = input("Webhook URL: ").strip()
    if not webhook_url:
        return False
    
    channel = input("Canal (ex: #alerts): ").strip() or "#alerts"
    
    # Atualiza .env
    atualizar_env({
        'SLACK_WEBHOOK_URL': webhook_url,
        'SLACK_CHANNEL': channel
    })
    
    print("✅ Slack configurado!")
    return True

def configurar_discord():
    """Configura notificações Discord"""
    print("\n🎮 Configuração do Discord:")
    print("-" * 30)
    
    webhook_url = input("Webhook URL: ").strip()
    if not webhook_url:
        return False
    
    # Atualiza .env
    atualizar_env({
        'DISCORD_WEBHOOK_URL': webhook_url
    })
    
    print("✅ Discord configurado!")
    return True

def configurar_telegram():
    """Configura notificações Telegram"""
    print("\n📱 Configuração do Telegram:")
    print("-" * 30)
    
    bot_token = input("Bot Token: ").strip()
    if not bot_token:
        return False
    
    chat_id = input("Chat ID: ").strip()
    if not chat_id:
        return False
    
    # Atualiza .env
    atualizar_env({
        'TELEGRAM_BOT_TOKEN': bot_token,
        'TELEGRAM_CHAT_ID': chat_id
    })
    
    print("✅ Telegram configurado!")
    return True

def configurar_dashboard():
    """Configura dashboard web"""
    print("\n🌐 Configuração do Dashboard:")
    print("-" * 30)
    
    port = input("Porta (ex: 8080): ").strip() or "8080"
    secret_key = input("Chave secreta (deixe vazio para gerar): ").strip()
    
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"🔑 Chave secreta gerada: {secret_key}")
    
    # Atualiza .env
    atualizar_env({
        'DASHBOARD_PORT': port,
        'DASHBOARD_SECRET_KEY': secret_key
    })
    
    print("✅ Dashboard configurado!")
    return True

def atualizar_env(config: Dict[str, str]):
    """Atualiza arquivo .env com novas configurações"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return
    
    # Lê arquivo atual
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Atualiza linhas
    for key, value in config.items():
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                break
    
    # Escreve arquivo atualizado
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(lines)

def testar_conectividade():
    """Testa conectividade dos serviços configurados"""
    print("\n🧪 Testando Conectividade:")
    print("-" * 30)
    
    try:
        # Carrega configuração
        from .production_config import load_production_config
        config = load_production_config()
        
        # Testa email
        if config.email:
            print("📧 Testando email...")
            try:
                import smtplib
                with smtplib.SMTP(config.email.smtp_server, config.email.smtp_port) as server:
                    if config.email.use_tls:
                        server.starttls()
                    if config.email.username and config.email.password:
                        server.login(config.email.username, config.email.password)
                print("✅ Email: Conexão OK")
            except Exception as e:
                print(f"❌ Email: Erro - {e}")
        
        # Testa Slack
        if config.slack:
            print("💬 Testando Slack...")
            try:
                import aiohttp
                import asyncio
                
                async def test_slack():
                    async with aiohttp.ClientSession() as session:
                        async with session.post(config.slack.webhook_url, json={"text": "Teste de conectividade"}) as response:
                            if response.status == 200:
                                return True
                            return False
                
                result = asyncio.run(test_slack())
                if result:
                    print("✅ Slack: Conexão OK")
                else:
                    print("❌ Slack: Erro na resposta")
            except Exception as e:
                print(f"❌ Slack: Erro - {e}")
        
        # Testa Discord
        if config.discord:
            print("🎮 Testando Discord...")
            try:
                import aiohttp
                import asyncio
                
                async def test_discord():
                    async with aiohttp.ClientSession() as session:
                        async with session.post(config.discord.webhook_url, json={"content": "Teste de conectividade"}) as response:
                            if response.status == 204:
                                return True
                            return False
                
                result = asyncio.run(test_discord())
                if result:
                    print("✅ Discord: Conexão OK")
                else:
                    print("❌ Discord: Erro na resposta")
            except Exception as e:
                print(f"❌ Discord: Erro - {e}")
        
        # Testa Telegram
        if config.telegram:
            print("📱 Testando Telegram...")
            try:
                import aiohttp
                import asyncio
                
                async def test_telegram():
                    url = f"https://api.telegram.org/bot{config.telegram.bot_token}/getMe"
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                return True
                            return False
                
                result = asyncio.run(test_telegram())
                if result:
                    print("✅ Telegram: Conexão OK")
                else:
                    print("❌ Telegram: Erro na resposta")
            except Exception as e:
                print(f"❌ Telegram: Erro - {e}")
        
        print("\n✅ Testes de conectividade concluídos!")
        
    except Exception as e:
        print(f"❌ Erro ao testar conectividade: {e}")

def mostrar_menu():
    """Mostra menu principal"""
    print("\n🚀 Configurador do Sistema de Produção RapidAPI")
    print("=" * 50)
    print("1. Criar arquivo .env")
    print("2. Configurar Email")
    print("3. Configurar Slack")
    print("4. Configurar Discord")
    print("5. Configurar Telegram")
    print("6. Configurar Dashboard")
    print("7. Testar Conectividade")
    print("8. Mostrar Configuração Atual")
    print("9. Sair")
    print("-" * 50)

def mostrar_configuracao():
    """Mostra configuração atual"""
    print("\n📋 Configuração Atual:")
    print("-" * 30)
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado!")
        return
    
    try:
        from .production_config import load_production_config
        config = load_production_config()
        
        print(f"🌍 Ambiente: {config.environment}")
        print(f"📊 Log Level: {config.log_level}")
        print(f"🌐 Dashboard: {config.dashboard.host}:{config.dashboard.port}")
        print(f"🔔 Canais de Notificação: {config.get_notification_channels()}")
        
        if config.email:
            print(f"📧 Email: {config.email.from_email}")
        if config.slack:
            print(f"💬 Slack: {config.slack.channel}")
        if config.discord:
            print(f"🎮 Discord: Configurado")
        if config.telegram:
            print(f"📱 Telegram: Configurado")
            
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")

def main():
    """Função principal"""
    print("🚀 Bem-vindo ao Configurador do Sistema de Produção!")
    
    while True:
        mostrar_menu()
        
        try:
            opcao = input("\nEscolha uma opção (1-9): ").strip()
            
            if opcao == "1":
                criar_arquivo_env()
            elif opcao == "2":
                configurar_email()
            elif opcao == "3":
                configurar_slack()
            elif opcao == "4":
                configurar_discord()
            elif opcao == "5":
                configurar_telegram()
            elif opcao == "6":
                configurar_dashboard()
            elif opcao == "7":
                testar_conectividade()
            elif opcao == "8":
                mostrar_configuracao()
            elif opcao == "9":
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n\n👋 Configuração interrompida pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
