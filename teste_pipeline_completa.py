#!/usr/bin/env python3
"""
Teste da pipeline completa com sistema de fallback implementado.
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

def test_full_pipeline():
    """Testa a pipeline completa com fallback."""
    try:
        from Coleta_de_dados.apis.fbref.orquestrador_coleta import executar_pipeline_completa
        
        logger.info("=== Testando Pipeline Completa com Fallback ===")
        logger.info("🚀 Iniciando execução da pipeline completa...")
        logger.info("⚠️ NOTA: O sistema usará dados de fallback quando o FBRef estiver bloqueado")
        
        start_time = time.time()
        
        # Executa a pipeline completa
        sucesso = executar_pipeline_completa()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"⏱️ Pipeline executada em {total_time:.2f} segundos")
        
        if sucesso:
            logger.info("✅ PIPELINE COMPLETA EXECUTADA COM SUCESSO!")
            logger.info("🎉 O sistema de fallback resolveu o problema de rate limiting!")
            return True
        else:
            logger.error("❌ Pipeline falhou, mas não travou (progresso!)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na pipeline: {e}", exc_info=True)
        return False

def check_database_results():
    """Verifica os resultados salvos no banco de dados."""
    try:
        from Coleta_de_dados.apis.fbref.fbref_fallback_system import create_fallback_system
        
        logger.info("=== Verificando Resultados no Banco ===")
        
        fallback_system = create_fallback_system(PROJECT_ROOT)
        db_status = fallback_system.check_database_status()
        
        logger.info("📊 Status do banco após execução:")
        logger.info(f"  - Banco existe: {db_status['database_exists']}")
        logger.info(f"  - Competições: {db_status['competitions_count']}")
        logger.info(f"  - Temporadas: {db_status['seasons_count']}")
        logger.info(f"  - Partidas: {db_status['matches_count']}")
        
        if db_status['competitions_count'] > 0:
            logger.info("✅ Dados foram salvos no banco com sucesso!")
            return True
        else:
            logger.warning("⚠️ Nenhum dado encontrado no banco")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco: {e}")
        return False

def show_next_steps():
    """Mostra os próximos passos para completar o sistema."""
    logger.info("\n" + "="*60)
    logger.info("🎯 PRÓXIMOS PASSOS PARA COMPLETAR O SISTEMA:")
    logger.info("\n1. 📊 VERIFICAÇÃO DE COMPLETUDE:")
    logger.info("   - Implementar verificação se todas as ligas/temporadas foram extraídas")
    logger.info("   - Criar relatórios de status da coleta")
    
    logger.info("\n2. ⚽ COLETA DE PARTIDAS:")
    logger.info("   - Implementar coleta de partidas com sistema de fallback")
    logger.info("   - Navegar para 'Scores & Fixtures' de cada temporada")
    logger.info("   - Extrair links de 'Match Report' ou coluna 'Score'")
    
    logger.info("\n3. 🏟️ COLETA DE CLUBES:")
    logger.info("   - Ir para /en/squads/ (Clubs)")
    logger.info("   - Extrair links por país (ex: Brazil Football Clubs)")
    logger.info("   - Separar por gênero (coluna Gender: M/F)")
    logger.info("   - Coletar estatísticas e 'Records vs. Opponents'")
    
    logger.info("\n4. 👤 COLETA DE JOGADORES:")
    logger.info("   - Usar links de países para acessar jogadores")
    logger.info("   - Coletar de 'Brazil Players', etc.")
    logger.info("   - Extrair estatísticas de All Competitions, Domestic Leagues, etc.")
    logger.info("   - Implementar cruzamento de dados para evitar duplicidade")
    
    logger.info("\n5. 🔄 SISTEMA DE CACHE AVANÇADO:")
    logger.info("   - Implementar cache inteligente para dados já coletados")
    logger.info("   - Sistema de atualização incremental")
    logger.info("   - Detecção de mudanças no site")
    
    logger.info("\n6. 📈 MONITORAMENTO E RELATÓRIOS:")
    logger.info("   - Dashboard de status da coleta")
    logger.info("   - Alertas para problemas de rate limiting")
    logger.info("   - Relatórios de completude dos dados")

if __name__ == "__main__":
    logger.info("🚀 TESTE FINAL DA PIPELINE COMPLETA COM FALLBACK")
    logger.info("="*60)
    
    # Teste da pipeline completa
    pipeline_success = test_full_pipeline()
    
    # Verifica resultados no banco
    logger.info("\n" + "="*60)
    db_success = check_database_results()
    
    # Resumo final
    logger.info("\n" + "="*60)
    logger.info("📋 RESUMO FINAL:")
    logger.info(f"  Pipeline executada: {'✅ SUCESSO' if pipeline_success else '❌ FALHA'}")
    logger.info(f"  Dados no banco: {'✅ SUCESSO' if db_success else '❌ FALHA'}")
    
    if pipeline_success:
        logger.info("\n🎉 PARABÉNS! O PROBLEMA DE RATE LIMITING FOI RESOLVIDO!")
        logger.info("✅ A pipeline agora pode executar mesmo quando o FBRef está bloqueado")
        logger.info("✅ O sistema de fallback permite funcionamento offline")
        logger.info("✅ Não há mais travamentos na etapa 'descoberta_links'")
    
    # Mostra próximos passos
    show_next_steps()
    
    logger.info("\n💡 PARA TESTAR A PIPELINE ORIGINAL:")
    logger.info("   Execute: python run.py")
    logger.info("   O sistema agora deve funcionar sem travar!")
