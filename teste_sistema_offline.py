#!/usr/bin/env python3
"""
Teste do sistema offline/fallback para quando o FBRef está completamente bloqueado.
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

def test_fallback_system():
    """Testa o sistema de fallback diretamente."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_fallback_system import create_fallback_system
        
        logger.info("=== Testando Sistema de Fallback ===")
        
        fallback = create_fallback_system(PROJECT_ROOT)
        
        # Testa carregamento de dados de fallback
        competitions = fallback.load_fallback_data()
        logger.info(f"✅ Dados de fallback carregados: {len(competitions)} competições")
        
        # Mostra algumas competições
        for i, comp in enumerate(competitions[:5]):
            logger.info(f"  {i+1}. {comp['nome']} ({comp['contexto']})")
        
        # Testa status do banco
        db_status = fallback.check_database_status()
        logger.info(f"📊 Status do banco: {db_status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de fallback: {e}", exc_info=True)
        return False

def test_offline_competition_discovery():
    """Testa descoberta de competições em modo offline."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes
        
        logger.info("=== Testando Descoberta Offline de Competições ===")
        
        start_time = time.time()
        competicoes = coletar_competicoes()
        end_time = time.time()
        
        logger.info(f"Descoberta concluída em {end_time - start_time:.2f} segundos")
        
        if competicoes:
            logger.info(f"✅ Sucesso! Encontradas {len(competicoes)} competições")
            
            # Mostra algumas competições como exemplo
            for i, comp in enumerate(competicoes[:5]):
                logger.info(f"  {i+1}. {comp['nome']} ({comp['contexto']})")
            
            return True
        else:
            logger.error("❌ Falha: Nenhuma competição encontrada")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)
        return False

def test_database_preparation():
    """Testa preparação do banco de dados."""
    try:
        from Banco_de_dados.criar_banco import criar_todas_as_tabelas
        
        logger.info("=== Testando Preparação do Banco ===")
        
        start_time = time.time()
        result = criar_todas_as_tabelas()
        end_time = time.time()
        
        logger.info(f"Preparação do banco concluída em {end_time - start_time:.2f} segundos")
        
        if result:
            logger.info("✅ Banco de dados preparado com sucesso")
            return True
        else:
            logger.error("❌ Falha na preparação do banco")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na preparação do banco: {e}", exc_info=True)
        return False

def test_pipeline_with_fallback():
    """Testa pipeline com sistema de fallback."""
    try:
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        logger.info("=== Testando Pipeline com Fallback ===")
        
        orquestrador = OrquestradorColeta()
        
        # Lista etapas disponíveis
        logger.info("Etapas disponíveis:")
        orquestrador.listar_etapas()
        
        # Testa apenas as primeiras etapas
        etapas_teste = ["preparacao_banco", "descoberta_links"]
        
        for etapa in etapas_teste:
            logger.info(f"\n--- Testando etapa: {etapa} ---")
            start_time = time.time()
            
            sucesso = orquestrador.executar_etapa_individual(etapa)
            
            end_time = time.time()
            logger.info(f"Etapa {etapa} concluída em {end_time - start_time:.2f} segundos")
            
            if sucesso:
                logger.info(f"✅ Etapa {etapa} executada com sucesso!")
            else:
                logger.error(f"❌ Falha na etapa {etapa}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste da pipeline: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando testes do sistema offline/fallback")
    
    # Teste 1: Sistema de fallback
    logger.info("\n" + "="*60)
    test1_success = test_fallback_system()
    
    # Teste 2: Preparação do banco
    logger.info("\n" + "="*60)
    test2_success = test_database_preparation()
    
    # Teste 3: Descoberta offline de competições
    logger.info("\n" + "="*60)
    test3_success = test_offline_competition_discovery()
    
    # Teste 4: Pipeline com fallback
    logger.info("\n" + "="*60)
    test4_success = test_pipeline_with_fallback()
    
    # Resumo
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMO DOS TESTES OFFLINE:")
    logger.info(f"  1. Sistema de fallback: {'✅ SUCESSO' if test1_success else '❌ FALHA'}")
    logger.info(f"  2. Preparação do banco: {'✅ SUCESSO' if test2_success else '❌ FALHA'}")
    logger.info(f"  3. Descoberta offline: {'✅ SUCESSO' if test3_success else '❌ FALHA'}")
    logger.info(f"  4. Pipeline com fallback: {'✅ SUCESSO' if test4_success else '❌ FALHA'}")
    
    if all([test1_success, test2_success, test3_success, test4_success]):
        logger.info("🎉 TODOS OS TESTES OFFLINE PASSARAM! Sistema funcionando sem FBRef.")
    elif any([test1_success, test2_success, test3_success, test4_success]):
        logger.info("⚠️ ALGUNS TESTES PASSARAM. Sistema parcialmente funcional.")
    else:
        logger.info("❌ TODOS OS TESTES FALHARAM. Necessário investigar mais.")
    
    logger.info("\n💡 PRÓXIMOS PASSOS:")
    logger.info("  - Se os testes passaram, o sistema pode funcionar offline")
    logger.info("  - Execute 'python run.py' para testar a pipeline completa")
    logger.info("  - O sistema usará dados de fallback quando o FBRef estiver bloqueado")
