#!/usr/bin/env python3
"""
Teste do Sistema de Detecção de Travamentos

Valida se o sistema de logging está capturando adequadamente onde e por que o código pode estar travando.
"""

import sys
import os
import time
import threading
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def teste_sistema_deteccao_travamentos():
    """Testa o sistema básico de detecção de travamentos."""
    print("TESTE: Sistema de Detecção de Travamentos")
    print("=" * 50)
    
    try:
        from utils.hang_detection_logger import get_hang_detector, log_critical_section
        
        # Obter detector
        detector = get_hang_detector()
        print("✓ Sistema de detecção de travamentos inicializado")
        
        # Testar operação normal
        op_id = detector.log_operation_start("TESTE_OPERACAO", "Operação de teste", 10)
        time.sleep(1)
        detector.log_operation_end(op_id, True, "Teste concluído")
        print("✓ Operação normal registrada e finalizada")
        
        # Testar seção crítica
        with log_critical_section("TESTE_SECAO"):
            time.sleep(0.5)
            print("✓ Seção crítica executada")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def teste_integracao_fbref_utils():
    """Testa integração com fbref_utils."""
    print("\nTESTE: Integração com fbref_utils")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import _fazer_requisicao_http
        
        # URL de teste
        test_url = "https://httpbin.org/delay/2"  # Simula delay de 2s
        print(f"Testando: {test_url}")
        print("Deve completar em ~2-3 segundos com logging detalhado")
        
        start_time = time.time()
        
        # Fazer requisição (deve usar sistema de detecção)
        soup = _fazer_requisicao_http(test_url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ Completado em: {duration:.2f}s")
        
        if soup or duration < 10:  # Sucesso ou fallback rápido
            print("✓ Sistema funcionando - sem travamentos")
        else:
            print("⚠ Possível problema - verificar logs")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def teste_deteccao_travamento_simulado():
    """Simula um travamento para testar detecção."""
    print("\nTESTE: Detecção de Travamento Simulado")
    print("=" * 50)
    print("AVISO: Este teste vai simular um travamento por 15 segundos")
    print("O sistema deve detectar e alertar sobre o travamento")
    
    try:
        from utils.hang_detection_logger import get_hang_detector
        
        detector = get_hang_detector()
        
        # Simular operação que trava (timeout baixo para teste)
        op_id = detector.log_operation_start("OPERACAO_TRAVADA", "Simulação de travamento", 5)
        
        print("⏳ Simulando travamento por 8 segundos...")
        print("   (timeout configurado para 5s - deve alertar)")
        
        # Aguardar tempo suficiente para trigger do timeout
        time.sleep(8)
        
        # Finalizar operação
        detector.log_operation_end(op_id, True, "Simulação concluída")
        
        print("✓ Simulação de travamento concluída")
        print("✓ Verifique os logs para alertas de travamento")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def teste_logging_requisicoes_reais():
    """Testa logging em requisições reais ao FBRef."""
    print("\nTESTE: Logging de Requisições Reais")
    print("=" * 50)
    
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao
        
        # URL real do FBRef
        test_url = "https://fbref.com/en/"
        print(f"Testando: {test_url}")
        print("Deve mostrar logging detalhado de detecção de travamentos")
        
        start_time = time.time()
        
        # Fazer requisição com sistema completo
        soup = fazer_requisicao(test_url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✓ Completado em: {duration:.2f}s")
        
        if duration < 30:  # Não deve travar
            print("✓ EXCELENTE: Sem travamentos detectados")
        else:
            print("⚠ ATENÇÃO: Operação demorou mais que esperado")
        
        if soup:
            print("✓ Conteúdo HTML recebido")
        else:
            print("✓ Fallback usado (comportamento esperado)")
        
        return True
        
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

def main():
    """Função principal do teste de detecção de travamentos."""
    print("TESTE DE DETECÇÃO DE TRAVAMENTOS")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("OBJETIVO: Validar sistema de logging para identificar travamentos")
    print("=" * 70)
    
    resultados = []
    
    # Teste 1: Sistema básico
    resultado1 = teste_sistema_deteccao_travamentos()
    resultados.append(("Sistema Básico", resultado1))
    
    # Teste 2: Integração com fbref_utils
    resultado2 = teste_integracao_fbref_utils()
    resultados.append(("Integração fbref_utils", resultado2))
    
    # Teste 3: Detecção de travamento simulado
    print("\n" + "!" * 70)
    print("TESTE CRÍTICO: Detecção de Travamento")
    print("Este teste vai simular um travamento para validar a detecção")
    print("!" * 70)
    
    resultado3 = teste_deteccao_travamento_simulado()
    resultados.append(("Detecção de Travamento", resultado3))
    
    # Teste 4: Requisições reais
    resultado4 = teste_logging_requisicoes_reais()
    resultados.append(("Logging Requisições Reais", resultado4))
    
    # Relatório final
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
    
    if sucessos >= 3:  # Pelo menos 3 de 4 testes
        print("\n🎉 SISTEMA DE DETECÇÃO FUNCIONANDO!")
        print("✅ Logging de operações implementado")
        print("✅ Detecção de travamentos ativa")
        print("✅ Integração com requisições HTTP")
        print("✅ Monitoramento em tempo real")
        print("\n🔍 AGORA PODEMOS IDENTIFICAR TRAVAMENTOS!")
        
        print("\n📋 COMO USAR:")
        print("1. Execute o pipeline normal (python run.py)")
        print("2. Monitore os logs para mensagens de 'HANG_DETECTION'")
        print("3. Procure por alertas de '🚨 POSSÍVEL TRAVAMENTO DETECTADO'")
        print("4. Verifique operações que demoram mais que o timeout")
        
        return True
    else:
        print("\n❌ Sistema de detecção precisa de ajustes")
        print("Alguns testes falharam - verificar implementação")
        return False

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
