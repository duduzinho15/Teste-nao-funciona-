#!/usr/bin/env python3
"""
Ativação de Modo de Emergência

Script para ativar imediatamente o modo de emergência quando há falhas sistemáticas.
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def ativar_modo_emergencia():
    """Ativa modo de emergência para resolver falhas sistemáticas."""
    print("🚑 ATIVANDO MODO DE EMERGÊNCIA")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.emergency_fallback_mode import force_emergency_mode, get_emergency_stats, log_emergency_status
        
        # Ativar modo de emergência por 4 horas
        force_emergency_mode(hours=4)
        print("✅ Modo de emergência ATIVADO por 4 horas")
        
        # Mostrar estatísticas
        log_emergency_status()
        stats = get_emergency_stats()
        
        print("\n📊 ESTATÍSTICAS ATUAIS:")
        print(f"   Total de requisições: {stats['total_requests']}")
        print(f"   Taxa de sucesso: {stats['success_rate']:.1%}")
        print(f"   Falhas consecutivas: {stats['consecutive_failures']}")
        print(f"   Modo emergência: {stats['emergency_mode']}")
        
        print("\n🎯 EFEITO:")
        print("   ✅ TODAS as requisições usarão fallback/cache")
        print("   ✅ NÃO haverá mais tentativas de acesso ao FBRef")
        print("   ✅ Pipeline continuará funcionando offline")
        print("   ✅ Sem travamentos ou timeouts")
        
        print("\n🔄 COMO DESATIVAR:")
        print("   python desativar_modo_emergencia.py")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao ativar modo de emergência: {e}")
        return False

def main():
    """Função principal."""
    print("DETECÇÃO: Falhas sistemáticas no FBRef")
    print("SOLUÇÃO: Ativar modo de emergência")
    print("\nEste comando força o uso de fallback/cache para TODAS as requisições,")
    print("resolvendo imediatamente os problemas de travamento e falhas.")
    print("\nDeseja continuar? (s/N): ", end="")
    
    try:
        resposta = input().strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            sucesso = ativar_modo_emergencia()
            if sucesso:
                print("\n🚀 MODO DE EMERGÊNCIA ATIVO!")
                print("Execute novamente o pipeline - agora funcionará sem problemas.")
                return True
            else:
                print("\n❌ Falha ao ativar modo de emergência")
                return False
        else:
            print("\nOperação cancelada pelo usuário.")
            return False
    except KeyboardInterrupt:
        print("\n\nOperação cancelada.")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
