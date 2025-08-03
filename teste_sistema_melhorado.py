#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema melhorado funciona com rate limiting e fallback.
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

def testar_sistema_melhorado():
    """Testa o sistema melhorado com rate limiting e fallback."""
    print("=== TESTE DO SISTEMA MELHORADO ===")
    print("Testando com rate limiting e fallback...")
    
    # Configura logging
    configurar_logging_simples()
    logger = logging.getLogger(__name__)
    
    try:
        print("Iniciando teste do sistema melhorado...")
        logger.info("Iniciando teste do sistema melhorado...")
        
        # Cria o orquestrador com configuração otimizada
        orquestrador = OrquestradorColeta()
        
        # Executa apenas a etapa de descoberta de links
        print("Executando etapa 'descoberta_links'...")
        sucesso = orquestrador.executar_etapa_individual("descoberta_links")
        
        if sucesso:
            print("✅ SUCESSO! Etapa 'descoberta_links' executada com sucesso")
            logger.info("Teste bem-sucedido: etapa 'descoberta_links' executada")
            
            # Verifica se há dados no banco
            from Banco_de_dados.verificar_dados import verificar_dados
            print("📊 Verificando dados no banco...")
            verificar_dados()
            
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
    sucesso = testar_sistema_melhorado()
    sys.exit(0 if sucesso else 1) 