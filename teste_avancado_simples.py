#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE SIMPLIFICADO DE COLETA DE ESTATÍSTICAS AVANÇADAS
===================================================

Script mínimo para testar a coleta de estatísticas avançadas (xG, xA, formações táticas)
usando o AdvancedMatchScraper.
"""

import logging
import sys
import os
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_avancado_simples.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def testar_scraper_avancado(url_partida: str):
    """Testa o AdvancedMatchScraper com uma URL de partida."""
    try:
        logger.info(f"🔍 Iniciando teste com URL: {url_partida}")
        
        # Importar o módulo necessário
        from Coleta_de_dados.apis.fbref.advanced_match_scraper import AdvancedMatchScraper
        
        # Inicializar o scraper
        scraper = AdvancedMatchScraper()
        
        # Coletar estatísticas avançadas
        logger.info("Coletando estatísticas avançadas...")
        stats = scraper.get_advanced_match_stats(url_partida)
        
        if not stats:
            logger.error("❌ Nenhuma estatística avançada retornada")
            return False
        
        # Exibir resultados
        logger.info("\n📊 ESTATÍSTICAS AVANÇADAS COLETADAS:")
        logger.info("=" * 50)
        
        # Formações táticas
        if 'formacoes' in stats:
            logger.info("FORMACOES TATICAS:")
            logger.info(f"- Casa: {stats['formacoes'].get('casa', 'N/A')}")
            logger.info(f"- Visitante: {stats['formacoes'].get('visitante', 'N/A')}")
        
        # Estatísticas esperadas (xG, xA)
        if 'expected_goals' in stats:
            logger.info("\n⚽ EXPECTED GOALS (xG):")
            for time, valor in stats['expected_goals'].items():
                logger.info(f"- {time.capitalize()}: {valor}")
        
        # Estatísticas de jogadores
        if 'jogadores' in stats:
            logger.info("\n👥 ESTATÍSTICAS DE JOGADORES:")
            for time, jogadores in stats['jogadores'].items():
                logger.info(f"\n{time.upper()}:")
                for jogador in jogadores[:3]:  # Mostrar apenas os 3 primeiros de cada time
                    logger.info(f"- {jogador.get('nome', 'N/A')} (xA: {jogador.get('xa', 'N/A')})")
        
        logger.info("\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}", exc_info=True)
        return False

def main():
    """Função principal."""
    # URL de exemplo (substitua por uma URL real do FBRef)
    url_teste = "https://fbref.com/en/matches/..."  # Substitua pela URL real
    
    if not url_teste or 'fbref.com' not in url_teste:
        logger.error("❌ URL de teste inválida. Por favor, forneça uma URL válida do FBRef.")
        return 1
    
    # Executar teste
    sucesso = testar_scraper_avancado(url_teste)
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(main())
