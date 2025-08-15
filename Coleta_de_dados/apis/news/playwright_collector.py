#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
COLETOR DE NOTÍCIAS COM PLAYWRIGHT
==================================

Módulo para coleta de notícias sobre clubes de futebol usando Playwright.
Substitui o requests + BeautifulSoup por Playwright para melhor lidar com
conteúdo JavaScript e sites dinâmicos.

Autor: Sistema de Scraping Avançado
Data: 2025-08-14
Versão: 2.0 (Playwright)
"""

import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse, quote_plus

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from sqlalchemy.orm import Session

# Importações locais
from ..playwright_base import PlaywrightBaseScraper
from ...database.models import Clube, NoticiaClube
from ...database.config import SessionLocal

# Configuração de logging
logger = logging.getLogger(__name__)

class NewsPlaywrightCollector(PlaywrightBaseScraper):
    """
    Coletor de notícias usando Playwright.
    
    Funcionalidades:
    - Coleta de notícias do GE Globo
    - Coleta de notícias do UOL Esporte
    - Coleta de notícias do ESPN Brasil
    - Análise de sentimento das notícias
    - Sistema de anti-detecção avançado
    """
    
    def __init__(self, **kwargs):
        """Inicializa o coletor de notícias."""
        super().__init__(**kwargs)
        
        # Fontes de notícias configuradas
        self.news_sources = {
            'ge_globo': {
                'base_url': 'https://ge.globo.com',
                'search_url': 'https://ge.globo.com/busca/',
                'selectors': {
                    'articles': 'article',
                    'title': 'h3, h2, h1',
                    'summary': '.feed-post-body-resumo, .feed-post-body-chapeu',
                    'link': 'a[href*="/"]',
                    'image': 'img',
                    'timestamp': 'time, .feed-post-datetime',
                    'author': '.feed-post-author, .author'
                }
            },
            'uol_esporte': {
                'base_url': 'https://www.uol.com.br/esporte/',
                'search_url': 'https://www.uol.com.br/esporte/',
                'selectors': {
                    'articles': '.thumbnails-item, .card',
                    'title': 'h3, h2, h1',
                    'summary': '.description, .summary',
                    'link': 'a[href*="/"]',
                    'image': 'img',
                    'timestamp': 'time, .date',
                    'author': '.author, .byline'
                }
            },
            'espn_brasil': {
                'base_url': 'https://www.espn.com.br/',
                'search_url': 'https://www.espn.com.br/',
                'selectors': {
                    'articles': '.contentItem, .story',
                    'title': 'h1, h2, h3',
                    'summary': '.contentItem__subhead, .summary',
                    'link': 'a[href*="/"]',
                    'image': 'img',
                    'timestamp': 'time, .timestamp',
                    'author': '.author, .byline'
                }
            }
        }
        
        # Configurações de coleta
        self.max_news_per_source = 30
        self.max_news_per_club = 20
        self.scroll_pause_time = 2
        self.max_scroll_attempts = 5
        
        logger.info("🎭 NewsPlaywrightCollector inicializado")
    
    async def setup_page(self, page: Page) -> None:
        """Configura a página para coleta de notícias."""
        await super().setup_page(page)
        
        # Configurações específicas para notícias
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Intercepta requisições para análise
        await page.route("**/*", self._handle_request)
        
        # Configura headers específicos para sites de notícias
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
    
    async def _handle_request(self, route) -> None:
        """Intercepta e analisa requisições."""
        request = route.request
        
        # Log de requisições importantes
        if any(source in request.url for source in ['globo.com', 'uol.com.br', 'espn.com.br']):
            logger.debug(f"News Request: {request.method} {request.url}")
        
        # Continua a requisição
        await route.continue_()
    
    async def collect_news_from_ge_globo(self, club_name: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta notícias do GE Globo para um clube específico.
        
        Args:
            club_name: Nome do clube
            page: Página do Playwright
            
        Returns:
            Lista de notícias coletadas
        """
        news = []
        
        try:
            # Constrói URL de busca
            search_query = quote_plus(f"{club_name} futebol")
            search_url = f"{self.news_sources['ge_globo']['search_url']}?q={search_query}"
            
            # Navega para a página de busca
            await page.goto(search_url, wait_until="networkidle")
            
            # Aguarda carregamento dos resultados
            await page.wait_for_selector('article', timeout=15000)
            
            # Coleta notícias
            news_collected = 0
            scroll_attempts = 0
            
            while news_collected < self.max_news_per_club and scroll_attempts < self.max_scroll_attempts:
                # Coleta artigos visíveis
                article_elements = await page.query_selector_all('article')
                
                for article_elem in article_elements[news_collected:]:
                    if news_collected >= self.max_news_per_club:
                        break
                    
                    news_data = await self._extract_ge_globo_news(article_elem, club_name)
                    if news_data:
                        news.append(news_data)
                        news_collected += 1
                
                # Rola a página para carregar mais notícias
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novas notícias
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ GE Globo: {len(news)} notícias coletadas para {club_name}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias do GE Globo: {e}")
        
        return news
    
    async def _extract_ge_globo_news(self, article_elem, club_name: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de uma notícia do GE Globo."""
        try:
            # Extrai título
            title_elem = await article_elem.query_selector('h3, h2, h1')
            if not title_elem:
                return None
            
            title = await title_elem.text_content() or ""
            
            # Extrai resumo
            summary_elem = await article_elem.query_selector('.feed-post-body-resumo, .feed-post-body-chapeu')
            summary = await summary_elem.text_content() if summary_elem else ""
            
            # Extrai link
            link_elem = await article_elem.query_selector('a[href*="/"]')
            if not link_elem:
                return None
            
            link = await link_elem.get_attribute('href') or ""
            if link and not link.startswith('http'):
                link = urljoin(self.news_sources['ge_globo']['base_url'], link)
            
            # Extrai imagem
            img_elem = await article_elem.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            # Extrai timestamp
            time_elem = await article_elem.query_selector('time, .feed-post-datetime')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else None
            
            # Extrai autor
            author_elem = await article_elem.query_selector('.feed-post-author, .author')
            author = await author_elem.text_content() if author_elem else ""
            
            # Verifica se a notícia é relevante para o clube
            if not self._is_relevant_news(title, summary, club_name):
                return None
            
            return {
                "source": "GE Globo",
                "title": title.strip(),
                "summary": summary.strip(),
                "url": link,
                "image_url": image_url,
                "timestamp": timestamp,
                "author": author.strip(),
                "club_name": club_name,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair notícia do GE Globo: {e}")
            return None
    
    async def collect_news_from_uol_esporte(self, club_name: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta notícias do UOL Esporte para um clube específico.
        
        Args:
            club_name: Nome do clube
            page: Página do Playwright
            
        Returns:
            Lista de notícias coletadas
        """
        news = []
        
        try:
            # Constrói URL de busca
            search_query = quote_plus(f"{club_name} futebol")
            search_url = f"{self.news_sources['uol_esporte']['search_url']}?q={search_query}"
            
            # Navega para a página de busca
            await page.goto(search_url, wait_until="networkidle")
            
            # Aguarda carregamento dos resultados
            await page.wait_for_selector('.thumbnails-item, .card', timeout=15000)
            
            # Coleta notícias
            news_collected = 0
            scroll_attempts = 0
            
            while news_collected < self.max_news_per_club and scroll_attempts < self.max_scroll_attempts:
                # Coleta artigos visíveis
                article_elements = await page.query_selector_all('.thumbnails-item, .card')
                
                for article_elem in article_elements[news_collected:]:
                    if news_collected >= self.max_news_per_club:
                        break
                    
                    news_data = await self._extract_uol_esporte_news(article_elem, club_name)
                    if news_data:
                        news.append(news_data)
                        news_collected += 1
                
                # Rola a página para carregar mais notícias
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novas notícias
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ UOL Esporte: {len(news)} notícias coletadas para {club_name}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias do UOL Esporte: {e}")
        
        return news
    
    async def _extract_uol_esporte_news(self, article_elem, club_name: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de uma notícia do UOL Esporte."""
        try:
            # Extrai título
            title_elem = await article_elem.query_selector('h3, h2, h1')
            if not title_elem:
                return None
            
            title = await title_elem.text_content() or ""
            
            # Extrai resumo
            summary_elem = await article_elem.query_selector('.description, .summary')
            summary = await summary_elem.text_content() if summary_elem else ""
            
            # Extrai link
            link_elem = await article_elem.query_selector('a[href*="/"]')
            if not link_elem:
                return None
            
            link = await link_elem.get_attribute('href') or ""
            if link and not link.startswith('http'):
                link = urljoin(self.news_sources['uol_esporte']['base_url'], link)
            
            # Extrai imagem
            img_elem = await article_elem.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            # Extrai timestamp
            time_elem = await article_elem.query_selector('time, .date')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else None
            
            # Extrai autor
            author_elem = await article_elem.query_selector('.author, .byline')
            author = await author_elem.text_content() if author_elem else ""
            
            # Verifica se a notícia é relevante para o clube
            if not self._is_relevant_news(title, summary, club_name):
                return None
            
            return {
                "source": "UOL Esporte",
                "title": title.strip(),
                "summary": summary.strip(),
                "url": link,
                "image_url": image_url,
                "timestamp": timestamp,
                "author": author.strip(),
                "club_name": club_name,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair notícia do UOL Esporte: {e}")
            return None
    
    async def collect_news_from_espn_brasil(self, club_name: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta notícias do ESPN Brasil para um clube específico.
        
        Args:
            club_name: Nome do clube
            page: Página do Playwright
            
        Returns:
            Lista de notícias coletadas
        """
        news = []
        
        try:
            # Constrói URL de busca
            search_query = quote_plus(f"{club_name} futebol")
            search_url = f"{self.news_sources['espn_brasil']['search_url']}?q={search_query}"
            
            # Navega para a página de busca
            await page.goto(search_url, wait_until="networkidle")
            
            # Aguarda carregamento dos resultados
            await page.wait_for_selector('.contentItem, .story', timeout=15000)
            
            # Coleta notícias
            news_collected = 0
            scroll_attempts = 0
            
            while news_collected < self.max_news_per_club and scroll_attempts < self.max_scroll_attempts:
                # Coleta artigos visíveis
                article_elements = await page.query_selector_all('.contentItem, .story')
                
                for article_elem in article_elements[news_collected:]:
                    if news_collected >= self.max_news_per_club:
                        break
                    
                    news_data = await self._extract_espn_brasil_news(article_elem, club_name)
                    if news_data:
                        news.append(news_data)
                        news_collected += 1
                
                # Rola a página para carregar mais notícias
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novas notícias
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ ESPN Brasil: {len(news)} notícias coletadas para {club_name}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias do ESPN Brasil: {e}")
        
        return news
    
    async def _extract_espn_brasil_news(self, article_elem, club_name: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de uma notícia do ESPN Brasil."""
        try:
            # Extrai título
            title_elem = await article_elem.query_selector('h1, h2, h3')
            if not title_elem:
                return None
            
            title = await title_elem.text_content() or ""
            
            # Extrai resumo
            summary_elem = await article_elem.query_selector('.contentItem__subhead, .summary')
            summary = await summary_elem.text_content() if summary_elem else ""
            
            # Extrai link
            link_elem = await article_elem.query_selector('a[href*="/"]')
            if not link_elem:
                return None
            
            link = await link_elem.get_attribute('href') or ""
            if link and not link.startswith('http'):
                link = urljoin(self.news_sources['espn_brasil']['base_url'], link)
            
            # Extrai imagem
            img_elem = await article_elem.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            # Extrai timestamp
            time_elem = await article_elem.query_selector('time, .timestamp')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else None
            
            # Extrai autor
            author_elem = await article_elem.query_selector('.author, .byline')
            author = await author_elem.text_content() if author_elem else ""
            
            # Verifica se a notícia é relevante para o clube
            if not self._is_relevant_news(title, summary, club_name):
                return None
            
            return {
                "source": "ESPN Brasil",
                "title": title.strip(),
                "summary": summary.strip(),
                "url": link,
                "image_url": image_url,
                "timestamp": timestamp,
                "author": author.strip(),
                "club_name": club_name,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair notícia do ESPN Brasil: {e}")
            return None
    
    def _is_relevant_news(self, title: str, summary: str, club_name: str) -> bool:
        """
        Verifica se uma notícia é relevante para o clube.
        
        Args:
            title: Título da notícia
            summary: Resumo da notícia
            club_name: Nome do clube
            
        Returns:
            True se a notícia for relevante
        """
        # Converte para minúsculas para comparação
        title_lower = title.lower()
        summary_lower = summary.lower()
        club_name_lower = club_name.lower()
        
        # Verifica se o nome do clube aparece no título ou resumo
        if club_name_lower in title_lower or club_name_lower in summary_lower:
            return True
        
        # Verifica variações comuns do nome do clube
        club_variations = [
            club_name_lower,
            club_name_lower.replace(' ', ''),
            club_name_lower.split()[0],  # Primeira palavra
            club_name_lower.split()[-1] if len(club_name_lower.split()) > 1 else club_name_lower
        ]
        
        for variation in club_variations:
            if variation in title_lower or variation in summary_lower:
                return True
        
        return False
    
    async def collect_all_news_for_club(self, club_name: str) -> List[Dict[str, Any]]:
        """
        Coleta notícias de todas as fontes para um clube específico.
        
        Args:
            club_name: Nome do clube
            
        Returns:
            Lista de todas as notícias coletadas
        """
        all_news = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=self.browser_args
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=self.user_agent
            )
            
            page = await context.new_page()
            await self.setup_page(page)
            
            try:
                # Coleta do GE Globo
                logger.info(f"🎯 Coletando notícias do GE Globo para {club_name}")
                ge_news = await self.collect_news_from_ge_globo(club_name, page)
                all_news.extend(ge_news)
                await page.wait_for_timeout(2000)
                
                # Coleta do UOL Esporte
                logger.info(f"🎯 Coletando notícias do UOL Esporte para {club_name}")
                uol_news = await self.collect_news_from_uol_esporte(club_name, page)
                all_news.extend(uol_news)
                await page.wait_for_timeout(2000)
                
                # Coleta do ESPN Brasil
                logger.info(f"🎯 Coletando notícias do ESPN Brasil para {club_name}")
                espn_news = await self.collect_news_from_espn_brasil(club_name, page)
                all_news.extend(espn_news)
                
                logger.info(f"✅ {club_name}: {len(all_news)} notícias coletadas no total")
                
            except Exception as e:
                logger.error(f"Erro durante coleta de notícias: {e}")
            
            finally:
                await browser.close()
        
        return all_news
    
    async def save_to_database(self, news_data: List[Dict[str, Any]]) -> int:
        """
        Salva as notícias coletadas no banco de dados.
        
        Args:
            news_data: Lista de notícias coletadas
            
        Returns:
            Número total de notícias salvas
        """
        total_saved = 0
        
        try:
            db = SessionLocal()
            
            for news in news_data:
                try:
                    # Busca o clube no banco
                    clube = db.query(Clube).filter(Clube.nome.ilike(f"%{news['club_name']}%")).first()
                    if not clube:
                        logger.warning(f"Clube {news['club_name']} não encontrado no banco")
                        continue
                    
                    # Cria registro da notícia
                    noticia = NoticiaClube(
                        clube_id=clube.id,
                        titulo=news['title'][:255],  # Limita tamanho
                        url_noticia=news['url'],
                        fonte=news['source'],
                        data_publicacao=datetime.fromisoformat(news['timestamp']) if news.get('timestamp') else datetime.now(),
                        resumo=news['summary'][:500] if news.get('summary') else "",  # Limita tamanho
                        conteudo_completo=news['summary'],  # Por enquanto usa o resumo
                        autor=news['author'][:100] if news.get('author') else "",  # Limita tamanho
                        imagem_destaque=news['image_url'],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    
                    db.add(noticia)
                    total_saved += 1
                    
                except Exception as e:
                    logger.warning(f"Erro ao salvar notícia: {e}")
                    continue
            
            db.commit()
            logger.info(f"✅ {total_saved} notícias salvas no banco de dados")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            if db:
                db.rollback()
        
        finally:
            if db:
                db.close()
        
        return total_saved

# Função de demonstração
async def demo_news_collector():
    """Demonstra o coletor de notícias com Playwright."""
    print("🎭 DEMONSTRAÇÃO DO COLETOR DE NOTÍCIAS COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Configuração do coletor
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        collector = NewsPlaywrightCollector(**config)
        
        # Clubes para coletar notícias
        clubes = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo"]
        
        total_news = 0
        
        for clube in clubes:
            print(f"\n🏆 Coletando notícias para: {clube}")
            
            # Coleta notícias do clube
            news = await collector.collect_all_news_for_club(clube)
            total_news += len(news)
            
            print(f"   📰 {len(news)} notícias coletadas")
        
        print(f"\n📊 TOTAL: {total_news} notícias coletadas")
        
        # Salva no banco de dados
        print("\n💾 Salvando notícias no banco...")
        # Aqui você precisaria implementar a lógica para salvar no banco
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

if __name__ == "__main__":
    # Executa demonstração
    asyncio.run(demo_news_collector())
