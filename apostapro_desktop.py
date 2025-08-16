#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APOSTAPRO DESKTOP APP - Interface Moderna com Flet
==================================================

Aplicação desktop moderna para o sistema ApostaPro.
Interface clean, minimalista com modos claro/escuro.

Autor: Sistema ApostaPro
Data: 2025-01-14
Versão: 1.0 - Interface Moderna
"""

import flet as ft
import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApostaProDesktopApp:
    """Aplicação desktop moderna para o sistema ApostaPro"""
    
    def __init__(self):
        self.page = None
        self.is_system_running = False
        self.system_thread = None
        self.log_messages = []
        self.max_logs = 1000
        
        # Configurações
        self.config_file = Path("apostapro_config.json")
        self.config = self.load_config()
        
        # Componentes da interface
        self.status_text = None
        self.log_list_view = None
        self.start_button = None
        self.stop_button = None
        self.theme_switch = None
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configurações do arquivo JSON"""
        default_config = {
            "api_key": "",
            "refresh_interval": 30,
            "max_requests_per_minute": 60,
            "enable_notifications": True,
            "log_level": "INFO",
            "theme": "light"
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
        
        return default_config
    
    def save_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """Adiciona mensagem de log à interface"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        self.log_messages.append(log_entry)
        
        # Limita o número de logs
        if len(self.log_messages) > self.max_logs:
            self.log_messages.pop(0)
        
        # Atualiza a interface se estiver disponível
        if self.log_list_view:
            self.log_list_view.controls.clear()
            for log in self.log_messages[-100:]:  # Mostra apenas os últimos 100
                self.log_list_view.controls.append(
                    ft.Text(log, size=12, color=ft.colors.GREY_700)
                )
            self.log_list_view.update()
    
    def start_system(self, e):
        """Inicia o sistema de coleta de dados"""
        if not self.is_system_running:
            self.is_system_running = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.status_text.value = "🟢 SISTEMA ATIVO"
            self.status_text.color = ft.colors.GREEN
            
            # Inicia thread do sistema
            self.system_thread = threading.Thread(target=self.system_worker, daemon=True)
            self.system_thread.start()
            
            self.add_log_message("Sistema iniciado com sucesso", "INFO")
            self.page.update()
    
    def stop_system(self, e):
        """Para o sistema de coleta de dados"""
        if self.is_system_running:
            self.is_system_running = False
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.status_text.value = "🔴 SISTEMA PARADO"
            self.status_text.color = ft.colors.RED
            
            self.add_log_message("Sistema parado pelo usuário", "INFO")
            self.page.update()
    
    def system_worker(self):
        """Worker thread para o sistema de coleta"""
        while self.is_system_running:
            try:
                # Simula coleta de dados
                self.add_log_message("Coletando dados das APIs...", "INFO")
                time.sleep(5)
                
                if self.is_system_running:
                    self.add_log_message("Dados coletados com sucesso", "INFO")
                    time.sleep(self.config["refresh_interval"])
                    
            except Exception as e:
                self.add_log_message(f"Erro no sistema: {e}", "ERROR")
                time.sleep(10)
    
    def toggle_theme(self, e):
        """Alterna entre tema claro e escuro"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_switch.label = "🌙 Modo Escuro"
            self.config["theme"] = "dark"
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_switch.label = "☀️ Modo Claro"
            self.config["theme"] = "light"
        
        self.save_config()
        self.page.update()
    
    def update_config_field(self, field_name: str, value: str):
        """Atualiza campo de configuração"""
        self.config[field_name] = value
        self.save_config()
    
    def main(self, page: ft.Page):
        """Função principal da aplicação"""
        self.page = page
        
        # Configuração da página
        page.title = "ApostaPro - Sistema Inteligente de Apostas"
        page.theme_mode = ft.ThemeMode.LIGHT if self.config["theme"] == "light" else ft.ThemeMode.DARK
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.padding = 20
        page.spacing = 20
        
        # Componentes da interface
        
        # Status do sistema
        self.status_text = ft.Text(
            "🔴 SISTEMA PARADO",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.RED
        )
        
        # Botões de controle
        self.start_button = ft.FilledButton(
            text="🚀 INICIAR SISTEMA",
            on_click=self.start_system,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.GREEN,
                color=ft.colors.WHITE,
                padding=20
            )
        )
        
        self.stop_button = ft.FilledButton(
            text="⏹️ PARAR SISTEMA",
            on_click=self.stop_system,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.RED,
                color=ft.colors.WHITE,
                padding=20
            )
        )
        
        # Switch de tema
        theme_label = "☀️ Modo Claro" if self.config["theme"] == "light" else "🌙 Modo Escuro"
        self.theme_switch = ft.FilledButton(
            text=theme_label,
            on_click=self.toggle_theme,
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
                padding=15
            )
        )
        
        # Painel de controle esquerdo
        control_panel = ft.Container(
            content=ft.Column([
                ft.Text("🎮 CONTROLES", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                ft.SizedBox(height=20),
                self.start_button,
                ft.SizedBox(height=10),
                self.stop_button,
                ft.SizedBox(height=20),
                self.theme_switch,
                ft.SizedBox(height=20),
                
                # Status do sistema
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("📊 STATUS DO SISTEMA", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("APIs: 5/5 Ativas", size=14),
                            ft.Text("Cache: 85% Utilizado", size=14),
                            ft.Text("Última Atualização: --", size=14),
                        ]),
                        padding=15
                    )
                ),
                
                ft.SizedBox(height=20),
                
                # Informações rápidas
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("ℹ️ INFO RÁPIDA", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text("Total de Jogos: 0", size=14),
                            ft.Text("Modelos ML: 3 Ativos", size=14),
                            ft.Text("Taxa de Sucesso: --", size=14),
                        ]),
                        padding=15
                    )
                )
            ]),
            width=300,
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10
        )
        
        # Lista de logs
        self.log_list_view = ft.ListView(
            expand=True,
            auto_scroll=True,
            spacing=5
        )
        
        # Abas principais
        main_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="📋 LOGS",
                    icon=ft.icons.LIST_ALT,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("📋 LOGS DO SISTEMA", size=18, weight=ft.FontWeight.BOLD),
                                ft.FilledButton(
                                    text="🗑️ LIMPAR",
                                    on_click=lambda e: self.clear_logs(),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.GREY,
                                        color=ft.colors.WHITE
                                    )
                                )
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=self.log_list_view,
                                height=400,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=5,
                                padding=10
                            )
                        ]),
                        padding=20
                    )
                ),
                
                ft.Tab(
                    text="⚙️ CONFIGURAÇÕES",
                    icon=ft.icons.SETTINGS,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("⚙️ CONFIGURAÇÕES DO SISTEMA", size=18, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            ft.TextField(
                                label="🔑 Chave da API RapidAPI",
                                value=self.config.get("api_key", ""),
                                on_change=lambda e: self.update_config_field("api_key", e.control.value),
                                password=True,
                                expand=True
                            ),
                            
                            ft.SizedBox(height=15),
                            
                            ft.TextField(
                                label="⏱️ Intervalo de Atualização (segundos)",
                                value=str(self.config.get("refresh_interval", 30)),
                                on_change=lambda e: self.update_config_field("refresh_interval", int(e.control.value) if e.control.value.isdigit() else 30),
                                keyboard_type=ft.KeyboardType.NUMBER,
                                expand=True
                            ),
                            
                            ft.SizedBox(height=15),
                            
                            ft.TextField(
                                label="🚦 Limite de Requisições por Minuto",
                                value=str(self.config.get("max_requests_per_minute", 60)),
                                on_change=lambda e: self.update_config_field("max_requests_per_minute", int(e.control.value) if e.control.value.isdigit() else 60),
                                keyboard_type=ft.KeyboardType.NUMBER,
                                expand=True
                            ),
                            
                            ft.SizedBox(height=15),
                            
                            ft.Row([
                                ft.Text("🔔 Notificações Habilitadas", size=16),
                                ft.Switch(
                                    value=self.config.get("enable_notifications", True),
                                    on_change=lambda e: self.update_config_field("enable_notifications", e.control.value)
                                )
                            ]),
                            
                            ft.SizedBox(height=15),
                            
                            ft.Dropdown(
                                label="📝 Nível de Log",
                                value=self.config.get("log_level", "INFO"),
                                options=[
                                    ft.dropdown.Option("DEBUG"),
                                    ft.dropdown.Option("INFO"),
                                    ft.dropdown.Option("WARNING"),
                                    ft.dropdown.Option("ERROR")
                                ],
                                on_change=lambda e: self.update_config_field("log_level", e.control.value),
                                expand=True
                            ),
                            
                            ft.SizedBox(height=20),
                            
                            ft.Row([
                                ft.FilledButton(
                                    text="💾 SALVAR CONFIGURAÇÕES",
                                    on_click=lambda e: self.save_config_and_notify(),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.GREEN,
                                        color=ft.colors.WHITE
                                    )
                                ),
                                ft.FilledButton(
                                    text="🔄 RESTAURAR PADRÕES",
                                    on_click=lambda e: self.reset_config(),
                                    style=ft.ButtonStyle(
                                        bgcolor=ft.colors.ORANGE,
                                        color=ft.colors.WHITE
                                    )
                                )
                            ])
                        ]),
                        padding=20
                    )
                ),
                
                ft.Tab(
                    text="📊 ESTATÍSTICAS",
                    icon=ft.icons.ANALYTICS,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("📊 ESTATÍSTICAS DO SISTEMA", size=18, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            # Métricas principais
                            ft.Row([
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("🎯 Taxa de Sucesso", size=16),
                                            ft.Text("95.2%", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN)
                                        ]),
                                        padding=20
                                    ),
                                    expand=True
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("⚡ Tempo Médio", size=16),
                                            ft.Text("0.8s", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)
                                        ]),
                                        padding=20
                                    ),
                                    expand=True
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text("📈 Total de Requisições", size=16),
                                            ft.Text("1,247", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.PURPLE)
                                        ]),
                                        padding=20
                                    ),
                                    expand=True
                                )
                            ]),
                            
                            ft.SizedBox(height=20),
                            
                            # Gráfico de performance (simulado)
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("📈 Performance das APIs", size=16, weight=ft.FontWeight.BOLD),
                                        ft.SizedBox(height=10),
                                        ft.Container(
                                            content=ft.Text(
                                                "📊 Gráfico de Performance\n"
                                                "🟢 API 1: 98% Sucesso\n"
                                                "🟡 API 2: 87% Sucesso\n"
                                                "🔴 API 3: 92% Sucesso\n"
                                                "🟢 API 4: 96% Sucesso\n"
                                                "🟡 API 5: 89% Sucesso",
                                                size=14
                                            ),
                                            height=150,
                                            bgcolor=ft.colors.SURFACE_VARIANT,
                                            border_radius=5,
                                            padding=15
                                        )
                                    ]),
                                    padding=20
                                )
                            )
                        ]),
                        padding=20
                    )
                )
            ],
            expand=True
        )
        
        # Painel principal direito
        main_panel = ft.Container(
            content=main_tabs,
            expand=True,
            padding=20
        )
        
        # Layout principal
        page.add(
            ft.Row([
                control_panel,
                ft.VerticalDivider(width=1),
                main_panel
            ], expand=True)
        )
        
        # Adiciona mensagem inicial
        self.add_log_message("Aplicação ApostaPro iniciada com sucesso", "INFO")
        self.add_log_message("Sistema pronto para operação", "INFO")
    
    def clear_logs(self):
        """Limpa todos os logs"""
        self.log_messages.clear()
        if self.log_list_view:
            self.log_list_view.controls.clear()
            self.log_list_view.update()
        self.add_log_message("Logs limpos pelo usuário", "INFO")
    
    def save_config_and_notify(self):
        """Salva configurações e notifica o usuário"""
        self.save_config()
        self.add_log_message("Configurações salvas com sucesso", "INFO")
    
    def reset_config(self):
        """Restaura configurações padrão"""
        self.config = {
            "api_key": "",
            "refresh_interval": 30,
            "max_requests_per_minute": 60,
            "enable_notifications": True,
            "log_level": "INFO",
            "theme": "light"
        }
        self.save_config()
        self.add_log_message("Configurações restauradas para padrão", "INFO")

def main():
    """Função principal para executar a aplicação"""
    app = ApostaProDesktopApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()
