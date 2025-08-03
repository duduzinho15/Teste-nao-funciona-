#!/usr/bin/env python3
"""
Script de teste super rápido para verificar se o sistema funciona com apenas 2 competições.
"""

import sys
import os
import logging
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes, coletar_temporadas_de_competicao

def configurar_logging_simples():
    """Configura logging simples para o teste."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def testar_super_rapido():
    """Testa apenas 2 competições para verificar se funciona."""
    print("=== TESTE SUPER RÁPIDO (2 COMPETIÇÕES) ===")
    
    # Configura logging
    configurar_logging_simples()
    logger = logging.getLogger(__name__)
    
    try:
        print("Iniciando teste super rápido...")
        logger.info("Iniciando teste super rápido...")
        
        # Coleta apenas as primeiras 2 competições
        competicoes = coletar_competicoes()
        if not competicoes:
            print("❌ FALHA! Nenhuma competição encontrada")
            return False
        
        competicoes_teste = competicoes[:2]
        print(f"Testando com {len(competicoes_teste)} competições:")
        
        for i, comp in enumerate(competicoes_teste):
            print(f"  {i+1}. {comp['nome']} ({comp['contexto']})")
        
        # Testa apenas a primeira competição
        comp = competicoes_teste[0]
        print(f"\nTestando coleta de temporadas para: {comp['nome']}")
        
        links, tipo = coletar_temporadas_de_competicao(comp['url'])
        
        if links:
            print(f"✅ SUCESSO! {len(links)} links encontrados do tipo {tipo}")
            logger.info(f"Teste bem-sucedido: {len(links)} links encontrados")
            return True
        else:
            print(f"❌ FALHA! Nenhum link encontrado para {comp['nome']}")
            logger.error("Teste falhou: nenhum link encontrado")
            return False
            
    except Exception as e:
        print(f"❌ ERRO! {e}")
        logger.error(f"Erro durante o teste: {e}")
        return False
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    sucesso = testar_super_rapido()
    sys.exit(0 if sucesso else 1) 