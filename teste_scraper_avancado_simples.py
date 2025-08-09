#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE SIMPLIFICADO DO ADVANCED MATCH SCRAPER
===========================================

Script para testar o AdvancedMatchScraper com uma URL de exemplo do FBRef.
Este script não requer banco de dados e pode ser executado isoladamente.
"""

import asyncio
import aiohttp
import logging
import sys
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_scraper_avancado.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AdvancedMatchScraper:
    """Versão simplificada do AdvancedMatchScraper para testes."""
    
    def __init__(self, session):
        """Inicializa o scraper com uma sessão HTTP."""
        self.session = session
        self.base_url = "https://fbref.com"
    
    async def get_match_report_page(self, match_url: str) -> Optional[BeautifulSoup]:
        """Obtém a página de relatório da partida."""
        try:
            # Garante que temos a URL completa
            if not match_url.startswith('http'):
                match_url = f"{self.base_url}{match_url}"
                
            # Adiciona sufixo para a página de relatório se necessário
            if '/match/' in match_url and not match_url.endswith('/matchreport'):
                match_url = match_url.replace('/match/', '/matchreport/')
            
            logger.info(f"Obtendo página: {match_url}")
            
            # Fazer a requisição HTTP
            async with self.session.get(match_url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
            # Parse do HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Erro ao obter a página da partida: {e}")
            return None
    
    async def get_advanced_match_stats(self, match_url: str) -> Dict[str, Any]:
        """Extrai estatísticas avançadas da partida."""
        logger.info(f"Iniciando extração de estatísticas avançadas para: {match_url}")
        
        # Obter a página do relatório
        soup = await self.get_match_report_page(match_url)
        if not soup:
            logger.error("Falha ao obter a página do relatório")
            return {}
        
        # Inicializar dicionário de resultados
        stats = {
            'formacoes': {},
            'expected_goals': {},
            'jogadores': {}
        }
        
        try:
            # Extrair formações táticas
            logger.info("Extraindo formações táticas...")
            stats['formacoes'] = self._extrair_formacoes(soup)
            
            # Extrair expected goals (xG)
            logger.info("Extraindo expected goals (xG)...")
            stats['expected_goals'] = self._extrair_expected_goals(soup)
            
            # Extrair estatísticas de jogadores
            logger.info("Extraindo estatísticas de jogadores...")
            stats['jogadores'] = self._extrair_estatisticas_jogadores(soup)
            
            logger.info("Extração de estatísticas avançadas concluída com sucesso!")
            return stats
            
        except Exception as e:
            logger.error(f"Erro durante a extração de estatísticas: {e}", exc_info=True)
            return {}
    
    def _extrair_formacoes(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extrai as formações táticas dos times."""
        formacoes = {}
        
        try:
            # Encontrar os elementos que contêm as formações
            # (Ajuste os seletores conforme a estrutura real da página)
            formacao_elements = soup.select('.scorebox_meta')
            
            if len(formacao_elements) >= 2:
                # Extrair a formação do time da casa (primeiro elemento)
                formacoes['casa'] = self._extrair_formacao_do_elemento(formacao_elements[0])
                
                # Extrair a formação do time visitante (segundo elemento)
                formacoes['visitante'] = self._extrair_formacao_do_elemento(formacao_elements[1])
            
            return formacoes
            
        except Exception as e:
            logger.error(f"Erro ao extrair formações: {e}")
            return {}
    
    def _extrair_formacao_do_elemento(self, element) -> str:
        """Extrai a formação de um elemento específico."""
        try:
            # Tentar encontrar a formação no elemento
            # (Ajuste o seletor conforme a estrutura real da página)
            formacao_element = element.select_one('.scorebox_meta div')
            if formacao_element:
                return formacao_element.get_text(strip=True)
            return "N/A"
        except:
            return "N/A"
    
    def _extrair_expected_goals(self, soup: BeautifulSoup) -> Dict[str, float]:
        """Extrai os valores de expected goals (xG) da partida."""
        xg = {'casa': None, 'visitante': None}
        
        try:
            # Encontrar a tabela de estatísticas esperadas
            # (Ajuste os seletores conforme a estrutura real da página)
            xg_table = soup.select_one('#team_stats_extra')
            
            if xg_table:
                # Extrair os valores de xG
                # (Ajuste a lógica conforme a estrutura real da tabela)
                xg_values = xg_table.select('.score')
                if len(xg_values) >= 2:
                    xg['casa'] = float(xg_values[0].get_text(strip=True))
                    xg['visitante'] = float(xg_values[1].get_text(strip=True))
            
            return xg
            
        except Exception as e:
            logger.error(f"Erro ao extrair expected goals: {e}")
            return xg
    
    def _extrair_estatisticas_jogadores(self, soup: BeautifulSoup) -> Dict[str, list]:
        """Extrai estatísticas avançadas dos jogadores."""
        estatisticas = {'casa': [], 'visitante': []}
        
        try:
            # Encontrar as tabelas de estatísticas dos jogadores
            # (Ajuste os seletores conforme a estrutura real da página)
            tabelas = soup.select('.table_container')
            
            # Processar cada tabela de estatísticas
            for tabela in tabelas:
                # Verificar se é a tabela do time da casa ou visitante
                # (Ajuste a lógica conforme a estrutura real da página)
                if 'home' in tabela.get('id', ''):
                    time = 'casa'
                elif 'away' in tabela.get('id', ''):
                    time = 'visitante'
                else:
                    continue
                
                # Extrair estatísticas dos jogadores
                linhas = tabela.select('tbody tr')
                for linha in linhas:
                    jogador = {}
                    
                    # Extrair nome do jogador
                    nome_element = linha.select_one('th[data-stat="player"] a')
                    if nome_element:
                        jogador['nome'] = nome_element.get_text(strip=True)
                    
                    # Extrair estatísticas avançadas (xA, etc.)
                    # (Ajuste os seletores conforme a estrutura real da tabela)
                    xa_element = linha.select_one('td[data-stat="xg_assist"]')
                    if xa_element:
                        try:
                            jogador['xa'] = float(xa_element.get_text(strip=True))
                        except (ValueError, AttributeError):
                            jogador['xa'] = 0.0
                    
                    # Adicionar jogador à lista do time
                    if 'nome' in jogador:
                        estatisticas[time].append(jogador)
            
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao extrair estatísticas de jogadores: {e}")
            return estatisticas

async def testar_scraper(url_partida: str):
    """Função para testar o scraper com uma URL de partida."""
    logger.info(f"🔍 Iniciando teste com URL: {url_partida}")
    
    async with aiohttp.ClientSession() as session:
        # Inicializar o scraper
        scraper = AdvancedMatchScraper(session)
        
        # Obter estatísticas avançadas
        stats = await scraper.get_advanced_match_stats(url_partida)
        
        # Exibir resultados
        if not stats:
            logger.error("❌ Nenhuma estatística foi retornada")
            return False
        
        logger.info("\n📊 ESTATÍSTICAS AVANÇADAS COLETADAS:")
        logger.info("=" * 50)
        
        # Formações táticas
        if 'formacoes' in stats and stats['formacoes']:
            logger.info("FORMACOES TATICAS:")
            for time, formacao in stats['formacoes'].items():
                logger.info(f"- {time.capitalize()}: {formacao if formacao else 'N/A'}")
        
        # Expected goals (xG)
        if 'expected_goals' in stats and any(stats['expected_goals'].values()):
            logger.info("\n⚽ EXPECTED GOALS (xG):")
            for time, xg in stats['expected_goals'].items():
                if xg is not None:
                    logger.info(f"- {time.capitalize()}: {xg:.2f}")
        
        # Estatísticas de jogadores (amostra)
        if 'jogadores' in stats and any(stats['jogadores'].values()):
            logger.info("\n👥 ESTATÍSTICAS DE JOGADORES (amostra):")
            for time, jogadores in stats['jogadores'].items():
                if jogadores:
                    logger.info(f"\n{time.upper()} (mostrando 3 primeiros):")
                    for jogador in jogadores[:3]:
                        xa = jogador.get('xa', 'N/A')
                        if isinstance(xa, float):
                            xa = f"{xa:.2f}"
                        logger.info(f"- {jogador.get('nome', 'N/A')} (xA: {xa})")
        
        logger.info("\n✅ Teste concluído com sucesso!")
        return True

async def main():
    """Função principal assíncrona."""
    # URL de exemplo - substitua por uma URL real do FBRef
    url_teste = "https://fbref.com/en/matches/..."  # Substitua pela URL real
    
    if not url_teste or 'fbref.com' not in url_teste:
        logger.error("❌ URL de teste inválida. Por favor, forneça uma URL válida do FBRef.")
        return 1
    
    # Executar teste
    sucesso = await testar_scraper(url_teste)
    return 0 if sucesso else 1

if __name__ == "__main__":
    import os
    import sys
    
    # Verificar se foi fornecida uma URL como argumento
    if len(sys.argv) > 1 and 'fbref.com' in sys.argv[1]:
        url = sys.argv[1]
    else:
        # Usar URL de exemplo (substitua por uma URL real)
        url = "https://fbref.com/en/matches/..."
    
    # Executar o teste
    sys.exit(asyncio.run(main()))
