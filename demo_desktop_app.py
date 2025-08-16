#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEMO APOSTAPRO DESKTOP APP
==========================

Script de demonstração para testar a nova interface desktop.
Executa a aplicação ApostaPro com Flet.

Autor: Sistema ApostaPro
Data: 2025-01-14
"""

import subprocess
import sys
import os
from pathlib import Path

def check_flet_installation():
    """Verifica se o Flet está instalado"""
    try:
        import flet
        print("✅ Flet está instalado!")
        return True
    except ImportError:
        print("❌ Flet não está instalado!")
        return False

def install_flet():
    """Instala o Flet se necessário"""
    print("📦 Instalando Flet...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flet==0.21.0"])
        print("✅ Flet instalado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar Flet!")
        return False

def run_desktop_app():
    """Executa a aplicação desktop"""
    print("🚀 Iniciando aplicação ApostaPro Desktop...")
    
    app_file = Path("apostapro_desktop.py")
    if not app_file.exists():
        print("❌ Arquivo apostapro_desktop.py não encontrado!")
        return False
    
    try:
        # Executa a aplicação
        subprocess.run([sys.executable, "apostapro_desktop.py"])
        return True
    except KeyboardInterrupt:
        print("\n🛑 Aplicação interrompida pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        return False

def main():
    """Função principal"""
    print("🎮 APOSTAPRO DESKTOP APP - DEMO")
    print("=" * 50)
    
    # Verifica instalação do Flet
    if not check_flet_installation():
        print("\n🔧 Instalando dependências...")
        if not install_flet():
            print("❌ Não foi possível instalar o Flet!")
            return
    
    print("\n📱 Características da nova interface:")
    print("   • Design moderno e minimalista")
    print("   • Modos claro e escuro")
    print("   • Interface responsiva")
    print("   • Controles intuitivos")
    print("   • Sistema de logs em tempo real")
    print("   • Configurações avançadas")
    print("   • Estatísticas visuais")
    
    print("\n🎯 Funcionalidades:")
    print("   • Iniciar/Parar sistema")
    print("   • Monitoramento em tempo real")
    print("   • Configurações do sistema")
    print("   • Visualização de logs")
    print("   • Métricas de performance")
    print("   • Troca de temas")
    
    print("\n🚀 Iniciando aplicação...")
    print("   • Use os botões para controlar o sistema")
    print("   • Configure suas preferências")
    print("   • Monitore os logs em tempo real")
    print("   • Teste a troca de temas")
    
    # Executa a aplicação
    success = run_desktop_app()
    
    if success:
        print("\n✅ Demo concluído com sucesso!")
    else:
        print("\n❌ Demo falhou!")

if __name__ == "__main__":
    main()
