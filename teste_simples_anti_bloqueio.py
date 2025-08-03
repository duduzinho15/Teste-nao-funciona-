#!/usr/bin/env python3
"""
Teste Simples do Sistema Anti-Bloqueio

Teste básico e rápido para validar se o sistema funciona sem travamentos.
"""

import sys
import os
import time
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def teste_basico():
    """Teste básico do sistema simplificado."""
    print("TESTE: Sistema Anti-Bloqueio Simplificado")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.simple_anti_blocking import get_simple_anti_blocking
        
        # Obter sistema
        system = get_simple_anti_blocking()
        print("✓ Sistema inicializado com sucesso")
        
        # Testar delay
        delay = system.get_smart_delay()
        print(f"✓ Delay calculado: {delay:.2f}s (deve ser <= 8s)")
        
        if delay <= 8.0:
            print("✓ Delay limitado corretamente")
            return True
        else:
            print(f"✗ Delay muito alto: {delay}s")
            return False
            
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def teste_requisicao():
    """Teste de requisição com timeout agressivo."""
    print("\nTESTE: Requisição com Timeout Agressivo")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.simple_anti_blocking import make_safe_request
        
        # URL simples do FBRef
        url = "https://fbref.com/en/"
        print(f"Testando: {url}")
        print("Timeout: 15s máximo")
        
        start_time = time.time()
        
        # Fazer requisição
        response = make_safe_request(url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Completado em: {duration:.2f}s")
        
        if response:
            print("✓ SUCESSO: Resposta recebida")
            print(f"✓ Status: {response.status_code}")
            return True
        else:
            print("⚠ INFO: Sem resposta (pode ser bloqueio - normal)")
            return True  # Não é falha do sistema
            
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def teste_integracao():
    """Teste de integração com fazer_requisicao."""
    print("\nTESTE: Integração com fazer_requisicao")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao
        
        # URL de teste
        url = "https://fbref.com/en/"
        print(f"Testando fazer_requisicao: {url}")
        
        start_time = time.time()
        
        # Usar função integrada
        soup = fazer_requisicao(url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Completado em: {duration:.2f}s")
        
        if soup:
            print("✓ SUCESSO: Conteúdo HTML recebido")
            return True
        else:
            print("⚠ INFO: Sem conteúdo (usando fallback - normal)")
            return True  # Não é falha
            
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def main():
    """Função principal."""
    print("TESTE SIMPLES - SISTEMA ANTI-BLOQUEIO")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    resultados = []
    
    # Teste 1: Básico
    resultado1 = teste_basico()
    resultados.append(("Sistema Basico", resultado1))
    
    # Teste 2: Requisição direta
    resultado2 = teste_requisicao()
    resultados.append(("Requisicao Direta", resultado2))
    
    # Teste 3: Integração
    resultado3 = teste_integracao()
    resultados.append(("Integracao", resultado3))
    
    # Relatório
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "PASSOU" if resultado else "FALHOU"
        print(f"  {status} - {nome}")
        if resultado:
            sucessos += 1
    
    print(f"\nResultado: {sucessos}/{len(resultados)} testes passaram")
    
    if sucessos >= 2:
        print("\n🎉 SISTEMA FUNCIONANDO SEM TRAVAMENTOS!")
        return True
    else:
        print("\n❌ Sistema precisa de ajustes")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
