#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o sistema funciona com apenas 5 competições.
"""

import sys
import os
import logging
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Coleta_de_dados.apis.fbref.fbref_integrado import main

def configurar_logging_simples():
    """Configura logging simples para o teste."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def testar_modo_rapido():
    """Testa o modo rápido com apenas 5 competições."""
    print("=== TESTE RÁPIDO (5 COMPETIÇÕES) ===")
    
    # Configura logging
    configurar_logging_simples()
    logger = logging.getLogger(__name__)
    
    try:
        print("Iniciando teste rápido...")
        logger.info("Iniciando teste rápido...")
        
        # Executa o modo teste
        resultado = main(modo_teste=True)
        
        if resultado and resultado.get("competicoes_processadas", 0) > 0:
            print(f"✅ SUCESSO! {resultado['competicoes_processadas']} competições processadas")
            print(f"   -> {resultado['links_coletados']} links coletados")
            print(f"   -> {resultado.get('competicoes_com_erro', 0)} competições com erro")
            logger.info(f"Teste bem-sucedido: {resultado}")
            return True
        else:
            print("❌ FALHA! Nenhuma competição foi processada")
            logger.error("Teste falhou: nenhuma competição processada")
            return False
            
    except Exception as e:
        print(f"❌ ERRO! {e}")
        logger.error(f"Erro durante o teste: {e}")
        return False
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    sucesso = testar_modo_rapido()
    sys.exit(0 if sucesso else 1) 