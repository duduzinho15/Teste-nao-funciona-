#!/usr/bin/env python3
"""
Script de teste simples para verificar se a função de requisição está funcionando.
"""

import sys
import os
import logging

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes

def configurar_logging_simples():
    """Configura logging simples para o teste."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def testar_requisicao():
    """Testa a função de coleta de competições."""
    print("=== TESTE DE REQUISIÇÃO SIMPLES ===")
    
    # Configura logging
    configurar_logging_simples()
    logger = logging.getLogger(__name__)
    
    try:
        print("Iniciando teste de coleta de competições...")
        logger.info("Iniciando teste de coleta de competições...")
        
        # Testa a função de coleta de competições
        competicoes = coletar_competicoes()
        
        if competicoes:
            print(f"✅ SUCESSO! Encontradas {len(competicoes)} competições")
            logger.info(f"Teste bem-sucedido: {len(competicoes)} competições encontradas")
            
            # Mostra as primeiras 5 competições como exemplo
            print("\nPrimeiras 5 competições encontradas:")
            for i, comp in enumerate(competicoes[:5]):
                print(f"  {i+1}. {comp['nome']} ({comp['contexto']})")
                
        else:
            print("❌ FALHA! Nenhuma competição encontrada")
            logger.error("Teste falhou: nenhuma competição encontrada")
            return False
            
    except Exception as e:
        print(f"❌ ERRO! {e}")
        logger.error(f"Erro durante o teste: {e}")
        return False
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    sucesso = testar_requisicao()
    sys.exit(0 if sucesso else 1) 