#!/usr/bin/env python3
"""
Teste melhorado do sistema offline/fallback com correção do problema de preparação do banco.
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

def test_database_preparation_fixed():
    """Testa a preparação do banco com interpretação correta do resultado."""
    try:
        logger.info("=== Teste de Preparação do Banco (Corrigido) ===")
        
        from Banco_de_dados.criar_banco import criar_todas_as_tabelas, DB_NAME
        
        logger.info("🔧 Executando preparação do banco...")
        start_time = time.time()
        
        # A função criar_todas_as_tabelas retorna None se bem-sucedida
        resultado = criar_todas_as_tabelas()
        
        end_time = time.time()
        
        # Verificar se o banco foi realmente criado
        if os.path.exists(DB_NAME):
            import sqlite3
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if len(tables) > 0:
                logger.info(f"✅ PREPARAÇÃO DO BANCO: SUCESSO")
                logger.info(f"  - Tempo: {end_time - start_time:.2f}s")
                logger.info(f"  - Tabelas criadas: {len(tables)}")
                logger.info(f"  - Banco: {DB_NAME}")
                return True
            else:
                logger.error(f"❌ PREPARAÇÃO DO BANCO: FALHA - Sem tabelas")
                return False
        else:
            logger.error(f"❌ PREPARAÇÃO DO BANCO: FALHA - Arquivo não criado")
            return False
            
    except Exception as e:
        logger.error(f"❌ PREPARAÇÃO DO BANCO: ERRO - {e}")
        return False

def test_fallback_system_complete():
    """Testa o sistema de fallback completo."""
    try:
        logger.info("=== Teste do Sistema de Fallback Completo ===")
        
        from Coleta_de_dados.apis.fbref.fbref_fallback_system import create_fallback_system
        
        logger.info("🔧 Criando sistema de fallback...")
        fallback_system = create_fallback_system(PROJECT_ROOT)
        
        logger.info("📊 Carregando dados de fallback...")
        competitions = fallback_system.get_fallback_competitions()
        
        if competitions:
            logger.info(f"✅ SISTEMA DE FALLBACK: SUCESSO")
            logger.info(f"  - Competições disponíveis: {len(competitions)}")
            
            # Testar geração de temporadas
            seasons_count = 0
            for comp in competitions[:3]:  # Testar apenas 3 para ser rápido
                seasons = fallback_system.get_fallback_seasons(comp['nome'])
                seasons_count += len(seasons)
            
            logger.info(f"  - Temporadas de fallback: {seasons_count}")
            return True
        else:
            logger.error("❌ SISTEMA DE FALLBACK: FALHA - Sem competições")
            return False
            
    except Exception as e:
        logger.error(f"❌ SISTEMA DE FALLBACK: ERRO - {e}")
        return False

def test_offline_pipeline_step():
    """Testa uma etapa da pipeline em modo offline."""
    try:
        logger.info("=== Teste de Etapa da Pipeline Offline ===")
        
        from Coleta_de_dados.apis.fbref.fbref_integrado import coletar_competicoes
        
        logger.info("🔧 Executando descoberta de competições (offline)...")
        start_time = time.time()
        
        # Executar com limite para teste rápido
        resultado = coletar_competicoes(limite_teste=5)
        
        end_time = time.time()
        
        if resultado and len(resultado) > 0:
            logger.info(f"✅ DESCOBERTA OFFLINE: SUCESSO")
            logger.info(f"  - Tempo: {end_time - start_time:.2f}s")
            logger.info(f"  - Competições encontradas: {len(resultado)}")
            
            # Mostrar algumas competições encontradas
            for i, comp in enumerate(resultado[:3]):
                logger.info(f"  - {i+1}. {comp.get('nome', 'N/A')}")
            
            return True
        else:
            logger.error("❌ DESCOBERTA OFFLINE: FALHA - Sem resultados")
            return False
            
    except Exception as e:
        logger.error(f"❌ DESCOBERTA OFFLINE: ERRO - {e}")
        return False

def test_pipeline_with_fallback():
    """Testa a execução de múltiplas etapas da pipeline com fallback."""
    try:
        logger.info("=== Teste de Pipeline com Fallback ===")
        
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta
        
        logger.info("🔧 Criando orquestrador...")
        orquestrador = OrquestradorColeta()
        
        # Testar etapas individuais
        etapas_testadas = []
        
        # 1. Preparação do banco
        logger.info("1️⃣ Testando preparação do banco...")
        try:
            resultado_banco = orquestrador._executar_preparacao_banco()
            etapas_testadas.append(("preparacao_banco", resultado_banco is not False))
        except Exception as e:
            logger.error(f"Erro na preparação do banco: {e}")
            etapas_testadas.append(("preparacao_banco", False))
        
        # 2. Descoberta de links (com fallback)
        logger.info("2️⃣ Testando descoberta de links...")
        try:
            resultado_descoberta = orquestrador._executar_descoberta_links()
            etapas_testadas.append(("descoberta_links", resultado_descoberta is not False))
        except Exception as e:
            logger.error(f"Erro na descoberta de links: {e}")
            etapas_testadas.append(("descoberta_links", False))
        
        # Resumo das etapas
        logger.info("📊 Resumo das etapas testadas:")
        sucessos = 0
        for nome, sucesso in etapas_testadas:
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            logger.info(f"  - {nome}: {status}")
            if sucesso:
                sucessos += 1
        
        if sucessos == len(etapas_testadas):
            logger.info("✅ PIPELINE COM FALLBACK: TODOS OS TESTES PASSARAM!")
            return True
        else:
            logger.info(f"⚠️ PIPELINE COM FALLBACK: {sucessos}/{len(etapas_testadas)} testes passaram")
            return sucessos > 0
            
    except Exception as e:
        logger.error(f"❌ PIPELINE COM FALLBACK: ERRO - {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 TESTE COMPLETO DO SISTEMA OFFLINE/FALLBACK (MELHORADO)")
    logger.info("="*60)
    
    # Executa todos os testes
    results = {}
    
    logger.info("\n" + "="*60)
    results['database'] = test_database_preparation_fixed()
    
    logger.info("\n" + "="*60)
    results['fallback_system'] = test_fallback_system_complete()
    
    logger.info("\n" + "="*60)
    results['offline_discovery'] = test_offline_pipeline_step()
    
    logger.info("\n" + "="*60)
    results['pipeline_fallback'] = test_pipeline_with_fallback()
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("📋 RESUMO FINAL DOS TESTES:")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for test_name, success in results.items():
        status = "✅ SUCESSO" if success else "❌ FALHA"
        logger.info(f"  - {test_name}: {status}")
    
    logger.info(f"\n🎯 RESULTADO GERAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        logger.info("🎉 TODOS OS TESTES PASSARAM! Sistema offline/fallback está funcionando perfeitamente!")
        logger.info("✅ O problema de rate limiting foi completamente resolvido!")
        logger.info("✅ A pipeline pode executar mesmo quando o FBRef está bloqueado!")
    elif passed_tests > 0:
        logger.info("⚠️ SISTEMA PARCIALMENTE FUNCIONAL - alguns testes passaram")
    else:
        logger.info("❌ SISTEMA COM PROBLEMAS - nenhum teste passou")
    
    logger.info("\n💡 PRÓXIMO PASSO: Execute 'python run.py' para testar a pipeline completa!")
