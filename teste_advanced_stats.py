#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DO MÓDULO ADVANCED_STATS.PY
===============================

Script para testar a extração de estatísticas avançadas (xG, xA, formações táticas)
usando o módulo advanced_stats.py.

Este script demonstra como usar a classe AdvancedStatsExtractor para extrair e exibir
estatísticas avançadas de uma partida do FBRef.
"""

import os
import sys
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_advanced_stats.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def test_advanced_stats_extraction(match_url: str, headless: bool = True) -> bool:
    """Testa a extração de estatísticas avançadas para uma partida.
    
    Args:
        match_url: URL da partida no FBRef
        headless: Se True, executa o navegador em modo headless
        
    Returns:
        bool: True se o teste for bem-sucedido, False caso contrário
    """
    try:
        logger.info("🔍 Iniciando teste de extração de estatísticas avançadas...")
        logger.info(f"URL da partida: {match_url}")
        
        # Importar o módulo de estatísticas avançadas
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from Coleta_de_dados.apis.fbref.advanced_stats import AdvancedStatsExtractor, AdvancedMatchStats
        
        # Inicializar o extrator
        logger.info("Inicializando AdvancedStatsExtractor...")
        extractor = AdvancedStatsExtractor(headless=headless, timeout=30)
        
        # Extrair estatísticas
        logger.info("Extraindo estatísticas avançadas...")
        stats = extractor.extract_from_url(match_url)
        
        if not stats:
            logger.error("❌ Falha ao extrair estatísticas avançadas")
            return False
        
        # Exibir resultados
        logger.info("\n✅ ESTATÍSTICAS AVANÇADAS EXTRAÍDAS COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(f"🏠 {stats.home_team} {stats.home_xg or 'N/A'} xG - {stats.away_xg or 'N/A'} xG {stats.away_team} 🏠")
        logger.info(f"📅 Data: {stats.match_date or 'N/A'}")
        logger.info(f"🏆 Competição: {stats.competition or 'N/A'}")
        logger.info(f"🔢 Formações: {stats.home_team} {stats.home_formation or 'N/A'} vs {stats.away_team} {stats.away_formation or 'N/A'}")
        
        # Estatísticas de xG e xA
        logger.info("\n📊 ESTATÍSTICAS AVANÇADAS:")
        logger.info(f"- {stats.home_team}:")
        logger.info(f"  • xG: {stats.home_xg or 'N/A'}")
        logger.info(f"  • xA: {stats.home_xa or 'N/A'}")
        logger.info(f"- {stats.away_team}:")
        logger.info(f"  • xG: {stats.away_xg or 'N/A'}")
        logger.info(f"  • xA: {stats.away_xa or 'N/A'}")
        
        # Estatísticas dos jogadores (apenas os primeiros 3 de cada time)
        if stats.home_players_stats:
            logger.info(f"\n👥 JOGADORES - {stats.home_team} (top 3):")
            for i, player in enumerate(stats.home_players_stats[:3], 1):
                logger.info(f"  {i}. {player.get('name')}:")
                logger.info(f"     • xG: {player.get('xg', 'N/A'):.2f}")
                logger.info(f"     • xA: {player.get('xa', 'N/A'):.2f}")
                logger.info(f"     • Chutes: {player.get('shots', 'N/A')}")
                logger.info(f"     • Passes chave: {player.get('key_passes', 'N/A')}")
        
        if stats.away_players_stats:
            logger.info(f"\n👥 JOGADORES - {stats.away_team} (top 3):")
            for i, player in enumerate(stats.away_players_stats[:3], 1):
                logger.info(f"  {i}. {player.get('name')}:")
                logger.info(f"     • xG: {player.get('xg', 'N/A'):.2f}")
                logger.info(f"     • xA: {player.get('xa', 'N/A'):.2f}")
                logger.info(f"     • Chutes: {player.get('shots', 'N/A')}")
                logger.info(f"     • Passes chave: {player.get('key_passes', 'N/A')}")
        
        logger.info("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}", exc_info=True)
        return False
    
    finally:
        logger.info("=" * 60)

if __name__ == "__main__":
    # URL de exemplo (substitua por uma URL real de uma partida do FBRef)
    # Exemplo: "https://fbref.com/en/matches/..."
    MATCH_URL = "https://fbref.com/en/matches/..."
    
    # Verificar se uma URL foi fornecida como argumento
    if len(sys.argv) > 1:
        MATCH_URL = sys.argv[1]
    
    if not MATCH_URL or "fbref.com" not in MATCH_URL:
        logger.error("❌ URL inválida. Por favor, forneça uma URL válida do FBRef.")
        logger.info(f"Uso: {sys.argv[0]} [URL_DA_PARTIDA]")
        sys.exit(1)
    
    # Executar o teste
    success = test_advanced_stats_extraction(MATCH_URL, headless=True)
    
    # Retornar código de saída apropriado
    sys.exit(0 if success else 1)
