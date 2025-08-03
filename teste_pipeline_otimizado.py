#!/usr/bin/env python3
"""
Script de teste otimizado para verificar se o pipeline funciona com as melhorias.
"""

import sys
import os
import logging
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta

def configurar_logging_simples():
    """Configura logging simples para o teste."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def testar_pipeline_otimizada():
    """Testa o pipeline otimizado."""
    print("=== TESTE DO PIPELINE OTIMIZADO ===")
    
    # Configura logging
    configurar_logging_simples()
    logger = logging.getLogger(__name__)
    
    try:
        print("Iniciando teste do pipeline otimizado...")
        logger.info("Iniciando teste do pipeline otimizado...")
        
        # Cria o orquestrador
        orquestrador = OrquestradorColeta()
        
        # Executa apenas a etapa de descoberta de links (que estava causando timeout)
        print("Executando etapa 'descoberta_links'...")
        sucesso = orquestrador.executar_etapa_individual("descoberta_links")
        
        if sucesso:
            print("✅ SUCESSO! Etapa 'descoberta_links' executada com sucesso")
            logger.info("Teste bem-sucedido: etapa 'descoberta_links' executada")
            return True
        else:
            print("❌ FALHA! Etapa 'descoberta_links' falhou")
            logger.error("Teste falhou: etapa 'descoberta_links' falhou")
            return False
            
    except Exception as e:
        print(f"❌ ERRO! {e}")
        logger.error(f"Erro durante o teste: {e}")
        return False
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

if __name__ == "__main__":
    sucesso = testar_pipeline_otimizada()
    sys.exit(0 if sucesso else 1) 