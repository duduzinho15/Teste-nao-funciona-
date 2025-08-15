#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
COLETOR DE REDES SOCIAIS COM PLAYWRIGHT
======================================

Módulo para coleta de dados de redes sociais dos clubes usando Playwright.
Substitui o Selenium por Playwright para melhor performance e anti-detecção.

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
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from sqlalchemy.orm import Session

# Importações locais
from ..playwright_base import PlaywrightBaseScraper
from ...database.models import Clube, PostRedeSocial
from ...database.config import SessionLocal

# Configuração de logging
logger = logging.getLogger(__name__)

class SocialMediaPlaywrightCollector(PlaywrightBaseScraper):
    """
    Coletor de dados de redes sociais usando Playwright.
    
    Funcionalidades:
    - Coleta de posts do Twitter/X
    - Coleta de posts do Instagram
    - Coleta de posts do Facebook
    - Análise de engajamento
    - Sistema de anti-detecção avançado
    """
    
    def __init__(self, **kwargs):
        """Inicializa o coletor de redes sociais."""
        super().__init__(**kwargs)
        
        # Configurações específicas para redes sociais
        self.platforms = {
            'twitter': {
                'base_url': 'https://twitter.com',
                'selectors': {
                    'posts': '[data-testid="tweet"]',
                    'text': '[data-testid="tweetText"]',
                    'likes': '[data-testid="like"]',
                    'retweets': '[data-testid="retweet"]',
                    'replies': '[data-testid="reply"]',
                    'timestamp': 'time',
                    'username': '[data-testid="User-Name"]'
                }
            },
            'instagram': {
                'base_url': 'https://www.instagram.com',
                'selectors': {
                    'posts': 'article',
                    'text': 'div[class*="caption"]',
                    'likes': '[class*="like"]',
                    'comments': '[class*="comment"]',
                    'timestamp': 'time',
                    'username': 'a[class*="username"]'
                }
            },
            'facebook': {
                'base_url': 'https://www.facebook.com',
                'selectors': {
                    'posts': '[data-testid="post_message"]',
                    'text': '[data-testid="post_message"]',
                    'likes': '[data-testid="UFI2ReactionsCount/root"]',
                    'comments': '[data-testid="UFI2CommentsCount/root"]',
                    'shares': '[data-testid="UFI2SharesCount/root"]',
                    'timestamp': 'abbr',
                    'username': 'a[data-testid="post_actor_link"]'
                }
            }
        }
        
        # Configurações de coleta
        self.max_posts_per_platform = 50
        self.scroll_pause_time = 2
        self.max_scroll_attempts = 10
        
        logger.info("🎭 SocialMediaPlaywrightCollector inicializado")
    
    async def setup_page(self, page: Page) -> None:
        """Configura a página para coleta de redes sociais."""
        await super().setup_page(page)
        
        # Configurações específicas para redes sociais
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Intercepta requisições para análise
        await page.route("**/*", self._handle_request)
        
        # Configura headers específicos
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    async def _handle_request(self, route) -> None:
        """Intercepta e analisa requisições."""
        request = route.request
        
        # Log de requisições importantes
        if any(platform in request.url for platform in ['twitter.com', 'instagram.com', 'facebook.com']):
            logger.debug(f"Social Media Request: {request.method} {request.url}")
        
        # Continua a requisição
        await route.continue_()
    
    async def collect_twitter_posts(self, club_handle: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta posts do Twitter/X de um clube específico.
        
        Args:
            club_handle: Handle do Twitter do clube (ex: @Flamengo)
            page: Página do Playwright
            
        Returns:
            Lista de posts coletados
        """
        posts = []
        
        try:
            # Remove @ se presente
            clean_handle = club_handle.replace('@', '')
            
            # Navega para o perfil do clube
            profile_url = f"https://twitter.com/{clean_handle}"
            await page.goto(profile_url, wait_until="networkidle")
            
            # Aguarda carregamento dos posts
            await page.wait_for_selector('[data-testid="tweet"]', timeout=15000)
            
            # Coleta posts
            posts_collected = 0
            scroll_attempts = 0
            
            while posts_collected < self.max_posts_per_platform and scroll_attempts < self.max_scroll_attempts:
                # Coleta posts visíveis
                tweet_elements = await page.query_selector_all('[data-testid="tweet"]')
                
                for tweet_elem in tweet_elements[posts_collected:]:
                    if posts_collected >= self.max_posts_per_platform:
                        break
                    
                    tweet_data = await self._extract_twitter_post(tweet_elem)
                    if tweet_data:
                        posts.append(tweet_data)
                        posts_collected += 1
                
                # Rola a página para carregar mais posts
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novos posts
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ Twitter: {len(posts)} posts coletados de @{clean_handle}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar posts do Twitter: {e}")
        
        return posts
    
    async def _extract_twitter_post(self, tweet_elem) -> Optional[Dict[str, Any]]:
        """Extrai dados de um post do Twitter."""
        try:
            # Extrai texto do post
            text_elem = await tweet_elem.query_selector('[data-testid="tweetText"]')
            if not text_elem:
                return None
            
            text = await text_elem.text_content() or ""
            
            # Extrai métricas de engajamento
            likes_elem = await tweet_elem.query_selector('[data-testid="like"]')
            retweets_elem = await tweet_elem.query_selector('[data-testid="retweet"]')
            replies_elem = await tweet_elem.query_selector('[data-testid="reply"]')
            
            likes = await self._extract_metric(likes_elem)
            retweets = await self._extract_metric(retweets_elem)
            replies = await self._extract_metric(replies_elem)
            
            # Extrai timestamp
            time_elem = await tweet_elem.query_selector('time')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else None
            
            # Extrai username
            username_elem = await tweet_elem.query_selector('[data-testid="User-Name"]')
            username = await username_elem.text_content() if username_elem else ""
            
            # Extrai link do post
            post_link = await tweet_elem.query_selector('a[href*="/status/"]')
            post_url = await post_link.get_attribute('href') if post_link else ""
            if post_url:
                post_url = f"https://twitter.com{post_url}"
            
            return {
                "platform": "Twitter",
                "text": text.strip(),
                "username": username.strip(),
                "timestamp": timestamp,
                "likes": likes,
                "retweets": retweets,
                "replies": replies,
                "post_url": post_url,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair post do Twitter: {e}")
            return None
    
    async def _extract_metric(self, element) -> int:
        """Extrai valor numérico de uma métrica."""
        try:
            if element:
                text = await element.text_content() or ""
                # Remove caracteres não numéricos e converte
                number = re.sub(r'[^\d]', '', text)
                return int(number) if number else 0
            return 0
        except:
            return 0
    
    async def collect_instagram_posts(self, club_handle: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta posts do Instagram de um clube específico.
        
        Args:
            club_handle: Handle do Instagram do clube
            page: Página do Playwright
            
        Returns:
            Lista de posts coletados
        """
        posts = []
        
        try:
            # Navega para o perfil do clube
            profile_url = f"https://www.instagram.com/{club_handle}/"
            await page.goto(profile_url, wait_until="networkidle")
            
            # Aguarda carregamento dos posts
            await page.wait_for_selector('article', timeout=15000)
            
            # Coleta posts
            posts_collected = 0
            scroll_attempts = 0
            
            while posts_collected < self.max_posts_per_platform and scroll_attempts < self.max_scroll_attempts:
                # Coleta posts visíveis
                post_elements = await page.query_selector_all('article')
                
                for post_elem in post_elements[posts_collected:]:
                    if posts_collected >= self.max_posts_per_platform:
                        break
                    
                    post_data = await self._extract_instagram_post(post_elem)
                    if post_data:
                        posts.append(post_data)
                        posts_collected += 1
                
                # Rola a página para carregar mais posts
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novos posts
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ Instagram: {len(posts)} posts coletados de @{club_handle}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar posts do Instagram: {e}")
        
        return posts
    
    async def _extract_instagram_post(self, post_elem) -> Optional[Dict[str, Any]]:
        """Extrai dados de um post do Instagram."""
        try:
            # Extrai texto do post
            text_elem = await post_elem.query_selector('div[class*="caption"]')
            text = await text_elem.text_content() if text_elem else ""
            
            # Extrai métricas de engajamento
            likes_elem = await post_elem.query_selector('[class*="like"]')
            comments_elem = await post_elem.query_selector('[class*="comment"]')
            
            likes = await self._extract_metric(likes_elem)
            comments = await self._extract_metric(comments_elem)
            
            # Extrai timestamp
            time_elem = await post_elem.query_selector('time')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else None
            
            # Extrai username
            username_elem = await post_elem.query_selector('a[class*="username"]')
            username = await username_elem.text_content() if username_elem else ""
            
            # Extrai imagem
            img_elem = await post_elem.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else ""
            
            return {
                "platform": "Instagram",
                "text": text.strip(),
                "username": username.strip(),
                "timestamp": timestamp,
                "likes": likes,
                "comments": comments,
                "image_url": image_url,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair post do Instagram: {e}")
            return None
    
    async def collect_facebook_posts(self, club_handle: str, page: Page) -> List[Dict[str, Any]]:
        """
        Coleta posts do Facebook de um clube específico.
        
        Args:
            club_handle: Handle do Facebook do clube
            page: Página do Playwright
            
        Returns:
            Lista de posts coletados
        """
        posts = []
        
        try:
            # Navega para o perfil do clube
            profile_url = f"https://www.facebook.com/{club_handle}/"
            await page.goto(profile_url, wait_until="networkidle")
            
            # Aguarda carregamento dos posts
            await page.wait_for_selector('[data-testid="post_message"]', timeout=15000)
            
            # Coleta posts
            posts_collected = 0
            scroll_attempts = 0
            
            while posts_collected < self.max_posts_per_platform and scroll_attempts < self.max_scroll_attempts:
                # Coleta posts visíveis
                post_elements = await page.query_selector_all('[data-testid="post_message"]')
                
                for post_elem in post_elements[posts_collected:]:
                    if posts_collected >= self.max_posts_per_platform:
                        break
                    
                    post_data = await self._extract_facebook_post(post_elem)
                    if post_data:
                        posts.append(post_data)
                        posts_collected += 1
                
                # Rola a página para carregar mais posts
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.scroll_pause_time * 1000)
                scroll_attempts += 1
                
                # Aguarda carregamento de novos posts
                await page.wait_for_timeout(1000)
            
            logger.info(f"✅ Facebook: {len(posts)} posts coletados de {club_handle}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar posts do Facebook: {e}")
        
        return posts
    
    async def _extract_facebook_post(self, post_elem) -> Optional[Dict[str, Any]]:
        """Extrai dados de um post do Facebook."""
        try:
            # Extrai texto do post
            text = await post_elem.text_content() or ""
            
            # Procura métricas de engajamento no elemento pai
            parent = await post_elem.query_selector('xpath=..')
            if parent:
                likes_elem = await parent.query_selector('[data-testid="UFI2ReactionsCount/root"]')
                comments_elem = await parent.query_selector('[data-testid="UFI2CommentsCount/root"]')
                shares_elem = await parent.query_selector('[data-testid="UFI2SharesCount/root"]')
                
                likes = await self._extract_metric(likes_elem)
                comments = await self._extract_metric(comments_elem)
                shares = await self._extract_metric(shares_elem)
            else:
                likes = comments = shares = 0
            
            # Extrai timestamp
            time_elem = await post_elem.query_selector('xpath=..//abbr')
            timestamp = await time_elem.get_attribute('title') if time_elem else None
            
            # Extrai username
            username_elem = await post_elem.query_selector('xpath=..//a[data-testid="post_actor_link"]')
            username = await username_elem.text_content() if username_elem else ""
            
            return {
                "platform": "Facebook",
                "text": text.strip(),
                "username": username.strip(),
                "timestamp": timestamp,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "collected_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao extrair post do Facebook: {e}")
            return None
    
    async def collect_all_social_media_data(self, club_handles: Dict[str, Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Coleta dados de todas as redes sociais de todos os clubes.
        
        Args:
            club_handles: Dicionário com handles das redes sociais por clube
            
        Returns:
            Dicionário com dados organizados por clube e plataforma
        """
        all_data = {}
        
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
                for club_name, handles in club_handles.items():
                    logger.info(f"🎯 Coletando dados do clube: {club_name}")
                    all_data[club_name] = {}
                    
                    # Coleta do Twitter
                    if 'twitter' in handles:
                        twitter_posts = await self.collect_twitter_posts(handles['twitter'], page)
                        all_data[club_name]['twitter'] = twitter_posts
                        await page.wait_for_timeout(2000)
                    
                    # Coleta do Instagram
                    if 'instagram' in handles:
                        instagram_posts = await self.collect_instagram_posts(handles['instagram'], page)
                        all_data[club_name]['instagram'] = instagram_posts
                        await page.wait_for_timeout(2000)
                    
                    # Coleta do Facebook
                    if 'facebook' in handles:
                        facebook_posts = await self.collect_facebook_posts(handles['facebook'], page)
                        all_data[club_name]['facebook'] = facebook_posts
                        await page.wait_for_timeout(2000)
                    
                    logger.info(f"✅ {club_name}: dados coletados de {len(all_data[club_name])} plataformas")
                    
            except Exception as e:
                logger.error(f"Erro durante coleta de dados: {e}")
            
            finally:
                await browser.close()
        
        return all_data
    
    async def save_to_database(self, data: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> int:
        """
        Salva os dados coletados no banco de dados.
        
        Args:
            data: Dados coletados organizados por clube e plataforma
            
        Returns:
            Número total de registros salvos
        """
        total_saved = 0
        
        try:
            db = SessionLocal()
            
            for club_name, platforms in data.items():
                # Busca o clube no banco
                clube = db.query(Clube).filter(Clube.nome.ilike(f"%{club_name}%")).first()
                if not clube:
                    logger.warning(f"Clube {club_name} não encontrado no banco")
                    continue
                
                for platform, posts in platforms.items():
                    for post in posts:
                        try:
                            # Cria registro do post
                            post_record = PostRedeSocial(
                                clube_id=clube.id,
                                rede_social=platform.capitalize(),
                                post_id=f"{platform}_{hash(post.get('post_url', post.get('text', '')))}",
                                conteudo=post.get('text', '')[:1000],  # Limita tamanho
                                url_post=post.get('post_url', ''),
                                data_postagem=datetime.fromisoformat(post.get('timestamp', post.get('collected_at'))) if post.get('timestamp') else datetime.now(),
                                curtidas=post.get('likes', 0),
                                comentarios=post.get('comments', 0) or post.get('replies', 0),
                                compartilhamentos=post.get('shares', 0) or post.get('retweets', 0),
                                tipo_conteudo='texto',
                                url_imagem=post.get('image_url', ''),
                                data_geracao=datetime.now()
                            )
                            
                            db.add(post_record)
                            total_saved += 1
                            
                        except Exception as e:
                            logger.warning(f"Erro ao salvar post: {e}")
                            continue
            
            db.commit()
            logger.info(f"✅ {total_saved} posts salvos no banco de dados")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            if db:
                db.rollback()
        
        finally:
            if db:
                db.close()
        
        return total_saved

# Função de demonstração
async def demo_social_media_collector():
    """Demonstra o coletor de redes sociais com Playwright."""
    print("🎭 DEMONSTRAÇÃO DO COLETOR DE REDES SOCIAIS COM PLAYWRIGHT")
    print("=" * 70)
    
    try:
        # Configuração do coletor
        config = {
            "headless": False,  # Mostra o navegador para demonstração
            "timeout": 30000,
            "retry_attempts": 3
        }
        
        collector = SocialMediaPlaywrightCollector(**config)
        
        # Handles das redes sociais dos clubes (exemplo)
        club_handles = {
            "Flamengo": {
                "twitter": "@Flamengo",
                "instagram": "flamengo",
                "facebook": "Flamengo"
            },
            "Palmeiras": {
                "twitter": "@Palmeiras",
                "instagram": "palmeiras",
                "facebook": "Palmeiras"
            }
        }
        
        # Coleta dados de todas as redes sociais
        print("🔄 Coletando dados de redes sociais...")
        data = await collector.collect_all_social_media_data(club_handles)
        
        # Mostra resumo dos dados coletados
        print("\n📊 RESUMO DOS DADOS COLETADOS:")
        print("-" * 40)
        for club_name, platforms in data.items():
            print(f"🏆 {club_name}:")
            for platform, posts in platforms.items():
                print(f"   📱 {platform.capitalize()}: {len(posts)} posts")
        
        # Salva no banco de dados
        print("\n💾 Salvando dados no banco...")
        total_saved = await collector.save_to_database(data)
        print(f"✅ Total de posts salvos: {total_saved}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        return False

if __name__ == "__main__":
    # Executa demonstração
    asyncio.run(demo_social_media_collector())
