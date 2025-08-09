#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DIRETO DO ADVANCED MATCH SCRAPER
===================================

Script para testar diretamente o AdvancedMatchScraper com uma URL de exemplo.
"""

import logging
import asyncio
import sys
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_avancado_direto.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Importar o módulo AdvancedMatchScraper
sys.path.append('.')
from Coleta_de_dados.apis.fbref.scraper_estatisticas_avancadas import AdvancedMatchScraper

async def testar_scraper_avancado(url_partida: str):
    """Testa o AdvancedMatchScraper com uma URL de partida."""
    logger.info(f"🔍 Iniciando teste com URL: {url_partida}")
    
    try:
        # Criar uma sessão HTTP
        async with aiohttp.ClientSession() as session:
            # Inicializar o scraper
            scraper = AdvancedMatchScraper(session)
            
            # Obter a página do relatório da partida
            logger.info("Obtendo página do relatório da partida...")
            soup = await scraper.get_match_report_page(url_partida)
            
            if not soup:
                logger.error("❌ Falha ao obter a página do relatório")
                return False
            
            # Extrair estatísticas avançadas
            logger.info("Extraindo estatísticas avançadas...")
            stats = await scraper.get_advanced_match_stats(url_partida)
            
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
                logger.info("\n👥 ESTATÍSTICAS DE JOGADORES (amostra):")
                for time, jogadores in stats['jogadores'].items():
                    logger.info(f"\n{time.upper()} (mostrando 3 primeiros):")
                    for jogador in jogadores[:3]:
                        logger.info(f"- {jogador.get('nome', 'N/A')} (xA: {jogador.get('xa', 'N/A')})")
            
            logger.info("\n✅ Teste concluído com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}", exc_info=True)
        return False

async def main():
    """Função principal assíncrona."""
    # URL de exemplo - substitua por uma URL real do FBRef
    url_teste = "https://fbref.com/en/matches/..."  # Substitua pela URL real
    
    if not url_teste or 'fbref.com' not in url_teste:
        logger.error("❌ URL de teste inválida. Por favor, forneça uma URL válida do FBRef.")
        return 1
    
    # Executar teste
    sucesso = await testar_scraper_avancado(url_teste)
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
