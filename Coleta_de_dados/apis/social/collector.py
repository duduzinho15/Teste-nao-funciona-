"""
Módulo para coleta de dados de redes sociais dos clubes.

Este módulo fornece funcionalidades para coletar e armazenar dados de redes sociais
dos clubes de futebol, como posts, curtidas, comentários e compartilhamentos.
"""
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
import re
import time
import requests
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importações locais
from Coleta_de_dados.database.models import Clube, PostRedeSocial
from Coleta_de_dados.database.config import SessionLocal

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações de headers para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}

class SocialMediaCollector:
    """
    Coletor de dados de redes sociais para clubes de futebol.
    
    Esta classe é responsável por coletar, processar e armazenar dados de redes sociais
    dos clubes, como posts, engajamento e métricas de interação.
    """
    
    def __init__(self, db_session: Optional[Session] = None, headless: bool = True):
        """
        Inicializa o coletor de redes sociais.
        
        Args:
            db_session: Sessão do banco de dados. Se não fornecida, uma nova será criada.
            headless: Se True, executa o navegador em modo headless (sem interface gráfica).
        """
        self.session = db_session if db_session else SessionLocal()
        self.db = self.session  # For backward compatibility
        self.logger = logging.getLogger(f"{__name__}.SocialMediaCollector")
        self.headless = headless
        self.driver = self._init_webdriver()
        self.wait_timeout = 30  # segundos
        self.scroll_pause_time = 2  # segundos
        self.max_scroll_attempts = 5  # número máximo de tentativas de rolagem
    
    def _init_webdriver(self):
        """Inicializa e retorna uma instância do WebDriver do Selenium."""
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Configura o User-Agent para parecer um navegador real
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            
            # Inicializa o WebDriver
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Configurações adicionais para evitar detecção
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar o WebDriver: {e}")
            raise
            
    def _extrair_metricas_tweet(self, soup) -> Dict[str, int]:
        """
        Extrai as métricas de um tweet a partir do HTML.
        
        Args:
            soup: Objeto BeautifulSoup com o conteúdo do tweet
            
        Returns:
            Dict com as métricas extraídas (replies, retweets, likes, views)
        """
        metrics = {
            'replies': 0,
            'retweets': 0,
            'likes': 0,
            'views': 0
        }
        
        try:
            # Tenta encontrar o grupo de métricas
            metric_groups = soup.find_all('div', {'role': 'group'})
            if not metric_groups:
                return metrics
                
            # Para cada grupo de métricas
            for group in metric_groups:
                # Itera sobre os spans de métricas
                for span in group.find_all('span', recursive=False):
                    # Verifica se é um span de métrica
                    metric_type = span.get('data-testid', '')
                    if not metric_type:
                        continue
                        
                    # Encontra o span com o valor numérico
                    value_span = span.find('span')
                    if not value_span:
                        continue
                        
                    # Obtém o texto do valor
                    value_text = ''
                    if hasattr(value_span, 'get_text'):
                        value_text = value_span.get_text(strip=True)
                    elif hasattr(value_span, 'text'):
                        value_text = value_span.text.strip()
                    
                    if not value_text:
                        continue
                    
                    # Converte o texto para número
                    try:
                        if 'K' in value_text:
                            value = int(float(value_text.replace('K', '').replace(',', '.')) * 1000)
                        elif 'M' in value_text:
                            value = int(float(value_text.replace('M', '').replace(',', '.')) * 1000000)
                        else:
                            value = int(value_text.replace(',', '').replace('.', ''))
                    except (ValueError, AttributeError):
                        continue
                    
                    # Atribui o valor à métrica correta
                    if 'reply' in metric_type:
                        metrics['replies'] = value
                    elif 'retweet' in metric_type:
                        metrics['retweets'] = value
                    elif 'like' in metric_type:
                        metrics['likes'] = value
                    elif 'view' in metric_type:
                        metrics['views'] = value
                    
        except Exception as e:
            self.logger.error(f"Erro ao extrair métricas do tweet: {e}")
            self.logger.exception(e)
            
        return metrics
    
    def _rolar_pagina_para_baixo(self, scroll_pause_time: float = 2, max_attempts: int = 5) -> None:
        """
        Rola a página para baixo para carregar mais tweets.
        
        Args:
            scroll_pause_time: Tempo de espera entre as rolagens
            max_attempts: Número máximo de tentativas de rolagem
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        attempts = 0
        
        while attempts < max_attempts:
            # Rola até o final da página
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Aguarda o carregamento da página
            time.sleep(scroll_pause_time)
            
            # Calcula a nova altura da página
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Se a altura não mudou, para de rolar
            if new_height == last_height:
                break
                
            last_height = new_height
            attempts += 1
    
    def _extrair_url_midia(self, soup) -> Optional[str]:
        """
        Extrai a URL da mídia (imagem/vídeo) de um tweet.
        
        Args:
            soup: Objeto BeautifulSoup com o conteúdo do tweet
            
        Returns:
            URL da mídia ou None se não encontrada
        """
        try:
            # Tenta encontrar uma imagem
            img = soup.find('img')
            if img and 'src' in img.attrs:
                url = img['src']
                # Remove parâmetros da URL, se houver
                return url.split('?')[0]
                
            # Tenta encontrar um vídeo (se necessário no futuro)
            # video = soup.find('video')
            # if video and video.find('source'):
            #     return video.find('source')['src']
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair URL de mídia: {e}")
            
        return None
    
    def __del__(self):
        """Garante que os recursos sejam liberados quando o coletor for destruído."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Erro ao encerrar o WebDriver: {e}")
    
    def coletar_posts_recentes(self, clube_id: int, limite: int = 5) -> int:
        """
        Coleta posts recentes de redes sociais para um clube.
        
        Esta função coleta posts reais do Twitter/X para o clube especificado.
        
        Args:
            clube_id: ID do clube para o qual coletar os posts
            limite: Número máximo de posts a serem coletados (padrão: 5)
            
        Returns:
            int: Número de posts coletados e salvos
        """
        try:
            # Verifica se o clube existe e tem URL de rede social configurada
            clube = self.db.query(Clube).filter(Clube.id == clube_id).first()
            if not clube:
                self.logger.error(f"Clube com ID {clube_id} não encontrado.")
                return 0
                
            # Obtém a URL do perfil do clube no Twitter/X
            # Em produção, isso deve ser uma coluna específica na tabela de clubes
            perfil_url = f"https://x.com/{clube.nome.lower().replace(' ', '')}"
            
            # Coleta os posts da rede social
            self.logger.info(f"Iniciando coleta de posts para {clube.nome} ({perfil_url})")
            posts = self._coletar_posts_twitter(perfil_url, limite)
            
            if not posts:
                self.logger.warning(f"Nenhum post encontrado para {clube.nome}")
                return 0
            
            # Processa e salva os posts no banco de dados
            posts_salvos = 0
            for post in posts:
                if self._salvar_post(clube_id, post):
                    posts_salvos += 1
            
            self.db.commit()
            self.logger.info(f"Coleta concluída para {clube.nome}. {posts_salvos} novos posts salvos.")
            self.logger.info(f"{posts_salvos} posts salvos para {clube.nome}.")
            return posts_salvos
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao coletar posts: {str(e)}", exc_info=True)
            return 0
    
    def _coletar_posts_twitter(self, perfil_url: str, limite: int) -> List[Dict]:
        """
        Coleta posts de um perfil do Twitter/X usando Selenium.
        
        Args:
            perfil_url: URL do perfil do Twitter/X
            limite: Número máximo de posts a serem coletados
            
        Returns:
            List[Dict]: Lista de posts coletados
        """
        try:
            self.logger.info(f"Acessando perfil: {perfil_url}")
            
            # Acessa a página do perfil
            self.driver.get(perfil_url)
            
            # Aguarda o carregamento da página
            try:
                WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except TimeoutException:
                self.logger.warning("Tempo limite excedido ao carregar a página do perfil")
                return []
            
            # Rola a página para carregar mais posts (infinite scroll)
            self._rolar_pagina_para_baixo(limite)
            
            # Aguarda um pouco para garantir que os posts sejam carregados
            time.sleep(2)
            
            # Obtém o HTML da página
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Encontra todos os posts
            articles = soup.find_all('article')
            self.logger.info(f"Encontrados {len(articles)} artigos na página")
            
            posts = []
            for i, article in enumerate(articles[:limite]):
                try:
                    post = self._extrair_dados_post(article, perfil_url)
                    if post:
                        posts.append(post)
                except Exception as e:
                    self.logger.error(f"Erro ao processar artigo {i+1}: {e}")
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar posts do Twitter/X: {e}")
            self.logger.error(f"{e}")
            return []
    
    def _extrair_dados_post(self, article, perfil_url: str) -> dict:
        """Extrai os dados de um post do Twitter/X."""
        try:
            # Extrai o ID do post
            post_id = article.get('data-testid', '').replace('tweet-', '') or article.get('data-tweet-id', '')
            if not post_id:
                return {}
            
            # Extrai o texto do post
            texto_element = article.find('div', {'data-testid': 'tweetText'})
            texto = texto_element.get_text(strip=True) if texto_element else ""
            
            # Extrai a data de publicação
            time_element = article.find('time')
            data_publicacao = None
            if time_element and time_element.get('datetime'):
                try:
                    data_publicacao = time_element['datetime'].replace('Z', '+00:00')
                except (ValueError, TypeError):
                    pass
            
            # Extrai métricas de engajamento
            engajamento = self._extrair_metricas_engajamento(article)
            
            # Extrai mídias (imagens, vídeos, etc.)
            midias = self._extrair_midias(article)
            
            # Constrói a URL completa do post
            url_post = f"{perfil_url}/status/{post_id}" if not perfil_url.endswith('/') else f"{perfil_url}status/{post_id}"
            
            # Prepara o dicionário de retorno com as chaves esperadas por _salvar_post
            post_data = {
                'post_id': post_id,  # Chave alterada de 'id' para 'post_id'
                'conteudo': texto,   # Chave alterada de 'texto' para 'conteudo'
                'data_postagem': data_publicacao,  # Chave alterada de 'data_publicacao' para 'data_postagem'
                'url_post': url_post,  # Chave alterada de 'url' para 'url_post'
                'curtidas': engajamento.get('curtidas', 0),
                'compartilhamentos': engajamento.get('compartilhamentos', 0),
                'comentarios': engajamento.get('comentarios', 0),
                'visualizacoes': engajamento.get('visualizacoes', 0)
            }
            
            # Adiciona a URL da primeira mídia, se existir
            if midias and len(midias) > 0:
                post_data['midia_url'] = midias[0].get('url', '')
                
            return post_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados do post: {e}")
            return {}
    
    def _extrair_metricas_engajamento(self, article) -> dict:
        """Extrai as métricas de engajamento de um post."""
        metrics = {
            'curtidas': 0,
            'compartilhamentos': 0,
            'comentarios': 0,
            'visualizacoes': 0
        }
        
        try:
            # Encontra o container de engajamento
            engagement = article.find('div', {'role': 'group'})
            if not engagement:
                return metrics
            
            # Extrai cada métrica
            for item in engagement.find_all('div', {'role': 'button'}):
                text = item.get_text(strip=True) or ''
                value = 0
                
                # Extrai o valor numérico do texto
                if 'K' in text:
                    value = int(float(text.replace('K', '').replace(',', '.')) * 1000)
                elif 'M' in text:
                    value = int(float(text.replace('M', '').replace(',', '.')) * 1000000)
                else:
                    # Remove caracteres não numéricos
                    value = int(''.join(filter(str.isdigit, text)) or '0')
                
                # Determina o tipo de métrica baseado no texto ou atributos
                if 'Reply' in item.get('aria-label', ''):
                    metrics['comentarios'] = value
                elif 'Repost' in item.get('aria-label', ''):
                    metrics['compartilhamentos'] = value
                elif 'Like' in item.get('aria-label', ''):
                    metrics['curtidas'] = value
                elif 'View' in item.get('aria-label', ''):
                    metrics['visualizacoes'] = value
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair métricas de engajamento: {e}")
        
        return metrics
    
    def _extrair_midias(self, article) -> list:
        """Extrai informações sobre as mídias de um post."""
        midias = []
        
        try:
            # Encontra todas as imagens no post
            for img in article.find_all('img'):
                src = img.get('src', '')
                if src and ('profile_images' not in src) and ('emoji' not in src):
                    midias.append({
                        'tipo': 'imagem',
                        'url': src if src.startswith('http') else f"https://x.com{src}",
                        'alt': img.get('alt', '')
                    })
            
            # Encontra vídeos (implementação simplificada)
            for video in article.find_all('video'):
                src = video.get('src', '')
                if src:
                    midias.append({
                        'tipo': 'video',
                        'url': src if src.startswith('http') else f"https://x.com{src}"
                    })
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair mídias: {e}")
        
        return midias  # Retorna a lista, mesmo que vazia
    
    def _salvar_post(self, clube_id: int, post_data: Dict[str, any]) -> bool:
        """
        Salva um post no banco de dados, verificando duplicatas.
        
        Args:
            clube_id: ID do clube dono do post
            post_data: Dicionário com os dados do post
            
        Returns:
            bool: True se o post foi salvo, False caso contrário
        """
        try:
            from Coleta_de_dados.database.models import PostRedeSocial
            
            # Verifica se o post já existe no banco de dados
            existing_post = self.db.query(PostRedeSocial).filter(
                PostRedeSocial.post_id == post_data['post_id'],
                PostRedeSocial.clube_id == clube_id,
                PostRedeSocial.rede_social == 'Twitter'
            ).first()
            
            if existing_post:
                self.logger.debug(f"Post {post_data['post_id']} já existe no banco de dados.")
                return False
            
            # Cria um novo post usando o modelo ORM
            novo_post = PostRedeSocial(
                clube_id=clube_id,
                rede_social='Twitter',
                post_id=post_data['post_id'],
                conteudo=post_data['conteudo'],
                data_postagem=post_data['data_postagem'],
                curtidas=post_data.get('curtidas', 0),
                comentarios=post_data.get('comentarios', 0),
                compartilhamentos=post_data.get('compartilhamentos', 0),
                url_post=post_data['url_post'],
                midia_url=post_data.get('midia_url')
            )
            
            # Adiciona e faz commit da transação
            self.db.add(novo_post)
            self.db.commit()
            
            self.logger.debug(f"Post {post_data['post_id']} salvo com sucesso.")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar post {post_data.get('post_id', '')}: {str(e)}", exc_info=True)
            return False
    
    def obter_posts_por_clube(self, clube_id: int, limite: int = 10) -> List[Dict]:
        """
        Obtém os posts de redes sociais de um clube específico.
        
        Args:
            clube_id: ID do clube
            limite: Número máximo de posts a retornar
            
        Returns:
            List[Dict]: Lista de dicionários com os dados dos posts
        """
        try:
            from Coleta_de_dados.database.models import PostRedeSocial
            
            posts = self.db.query(PostRedeSocial)\
                .filter(PostRedeSocial.clube_id == clube_id)\
                .order_by(PostRedeSocial.data_postagem.desc())\
                .limit(limite)\
                .all()
            
            return [{
                'id': post.id,
                'rede_social': post.rede_social,
                'conteudo': post.conteudo,
                'data_postagem': post.data_postagem.isoformat() if post.data_postagem else None,
                'curtidas': post.curtidas,
                'comentarios': post.comentarios,
                'compartilhamentos': post.compartilhamentos,
                'url_post': post.url_post,
                'midia_url': post.midia_url
            } for post in posts]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter posts para o clube ID {clube_id}: {e}", exc_info=True)
            return []

def coletar_dados_para_todos_clubes(limite_por_clube: int = 3) -> Dict:
    """
    Função de conveniência para coletar dados para todos os clubes ativos.
    
    Args:
        limite_por_clube: Número máximo de posts a coletar por clube
        
    Returns:
        Dict: Estatísticas da coleta
    """
    db = SessionLocal()
    try:
        # Obtém todos os clubes
        clubes = db.query(Clube).all()
        
        if not clubes:
            return {
                'status': 'erro',
                'mensagem': 'Nenhum clube encontrado.',
                'clubes_processados': 0,
                'total_posts': 0
            }
        
        # Inicializa o coletor
        coletor = SocialMediaCollector(db)
        
        # Coleta dados para cada clube
        total_posts = 0
        for clube in clubes:
            try:
                posts = coletor.coletar_posts_recentes(clube.id, limite_por_clube)
                total_posts += posts
                logger.info(f"Coletados {posts} posts para o clube {clube.nome}.")
                
                # Adiciona um atraso entre as requisições para evitar bloqueios
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Erro ao coletar dados para o clube {clube.nome}: {str(e)}", exc_info=True)
                continue
        
        return {
            'status': 'sucesso',
            'mensagem': f'Coleta concluída para {len(clubes)} clubes.',
            'clubes_processados': len(clubes),
            'total_posts': total_posts
        }
        
    except Exception as e:
        logger.error(f"Erro na coleta de dados: {str(e)}", exc_info=True)
        return {
            'status': 'erro',
            'mensagem': str(e),
            'clubes_processados': 0,
            'total_posts': 0
        }
    finally:
        db.close()


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    # Configura o logging para exibir no console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    db = SessionLocal()
    try:
        # Verifica se foi passado um ID de clube como argumento
        if len(sys.argv) > 1:
            try:
                clube_id = int(sys.argv[1])
                limite = int(sys.argv[2]) if len(sys.argv) > 2 else 5
                
                # Cria uma instância do coletor
                coletor = SocialMediaCollector(db)
                
                # Coleta dados para o clube específico
                num_posts = coletor.coletar_posts_recentes(clube_id, limite=limite)
                print(f"✅ Coletados {num_posts} posts para o clube com ID {clube_id}.")
                
            except ValueError:
                print("❌ Erro: O ID do clube deve ser um número inteiro.")
                sys.exit(1)
            
            # Exibe os posts coletados
            posts = coletor.obter_posts_por_clube(clube_id, limite=limite)
            if posts:
                print(f"\n📝 Últimos {len(posts)} posts coletados:")
                for i, post in enumerate(posts, 1):
                    print(f"\n--- Post {i} ---")
                    print(f"📅 {post.get('data_postagem', 'Data não disponível')}")
                    print(f"{post.get('conteudo', '')}")
                    print(f"❤️ {post.get('curtidas', 0)} | 💬 {post.get('comentarios', 0)} | 🔄 {post.get('compartilhamentos', 0)}")
                    if post.get('midia_url'):
                        print(f"📎 Mídia: {post.get('midia_url')}")
            else:
                print("❌ Nenhum post encontrado para este clube.")
        else:
            # Se não foi passado um ID de clube, coleta para todos os clubes
            print("🔍 Coletando posts para todos os clubes ativos...")
            resultado = coletar_dados_para_todos_clubes(limite_por_clube=3)
            print(f"✅ {resultado['mensagem']}")
            print(f"📊 Total de posts coletados: {resultado['total_posts']}")
            
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        db.close()
