#!/usr/bin/env python3
"""
Teste das melhorias implementadas para lidar com rate limiting do FBRef.
"""
import sys
import os
import logging
import time

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_improved_competition_discovery():
    """Testa a descoberta de competições com as melhorias implementadas."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes
        
        logger.info("=== Testando descoberta de competições com melhorias ===")
        
        start_time = time.time()
        competicoes = coletar_competicoes()
        end_time = time.time()
        
        logger.info(f"Teste concluído em {end_time - start_time:.2f} segundos")
        
        if competicoes:
            logger.info(f"✅ Sucesso! Encontradas {len(competicoes)} competições")
            
            # Mostra algumas competições como exemplo
            for i, comp in enumerate(competicoes[:5]):
                logger.info(f"  {i+1}. {comp['nome']} ({comp['contexto']}) - {comp['url']}")
            
            if len(competicoes) > 5:
                logger.info(f"  ... e mais {len(competicoes) - 5} competições")
            
            return True
        else:
            logger.error("❌ Falha: Nenhuma competição encontrada")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)
        return False

def test_pipeline_step():
    """Testa apenas o primeiro passo da pipeline (descoberta de links)."""
    try:
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        logger.info("=== Testando primeiro passo da pipeline ===")
        
        orquestrador = OrquestradorColeta()
        
        # Executa apenas a etapa de descoberta de links
        sucesso = orquestrador.executar_etapa_individual("descoberta_links")
        
        if sucesso:
            logger.info("✅ Etapa de descoberta de links executada com sucesso!")
            return True
        else:
            logger.error("❌ Falha na etapa de descoberta de links")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste da pipeline: {e}", exc_info=True)
        return False

def test_basic_request():
    """Testa requisição básica com as melhorias."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_utils import fazer_requisicao, BASE_URL
        
        logger.info("=== Testando requisição básica com melhorias ===")
        
        url = f"{BASE_URL}/en/comps/"
        
        start_time = time.time()
        soup = fazer_requisicao(url)
        end_time = time.time()
        
        logger.info(f"Requisição concluída em {end_time - start_time:.2f} segundos")
        
        if soup:
            tables = soup.select("table.stats_table")
            logger.info(f"✅ Sucesso! Encontradas {len(tables)} tabelas de competições")
            return True
        else:
            logger.error("❌ Falha: Requisição retornou None")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na requisição: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando testes das melhorias de rate limiting")
    
    # Teste 1: Requisição básica
    logger.info("\n" + "="*50)
    test1_success = test_basic_request()
    
    # Teste 2: Descoberta de competições
    logger.info("\n" + "="*50)
    test2_success = test_improved_competition_discovery()
    
    # Teste 3: Primeiro passo da pipeline
    logger.info("\n" + "="*50)
    test3_success = test_pipeline_step()
    
    # Resumo
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMO DOS TESTES:")
    logger.info(f"  1. Requisição básica: {'✅ SUCESSO' if test1_success else '❌ FALHA'}")
    logger.info(f"  2. Descoberta de competições: {'✅ SUCESSO' if test2_success else '❌ FALHA'}")
    logger.info(f"  3. Pipeline (descoberta_links): {'✅ SUCESSO' if test3_success else '❌ FALHA'}")
    
    if all([test1_success, test2_success, test3_success]):
        logger.info("🎉 TODOS OS TESTES PASSARAM! As melhorias funcionaram.")
    elif any([test1_success, test2_success, test3_success]):
        logger.info("⚠️ ALGUNS TESTES PASSARAM. Melhorias parcialmente efetivas.")
    else:
        logger.info("❌ TODOS OS TESTES FALHARAM. Necessário investigar mais.")
