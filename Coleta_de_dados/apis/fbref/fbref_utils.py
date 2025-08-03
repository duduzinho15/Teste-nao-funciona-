import logging
import time
import datetime
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup, Comment
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, List
import threading
from contextlib import contextmanager

# Constantes globais
BASE_URL = "https://fbref.com"
FALLBACK_DIR = "fallback_htmls"
REQUEST_DELAY = 1.0  # Delay entre requisições para evitar rate limiting
MAX_RETRIES = 3
TIMEOUT = 15

# Thread-local storage para múltiplas instâncias
_thread_local = threading.local()

# Configuração de diretórios
os.makedirs(FALLBACK_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

def configurar_logging():
    """Configura o sistema de log para o projeto."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fbref_scraping.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def _get_session() -> requests.Session:
    """
    Retorna uma sessão HTTP reutilizável com configurações otimizadas.
    Usa thread-local storage para suporte a concorrência.
    """
    if not hasattr(_thread_local, 'session'):
        session = requests.Session()
        
        # Configuração de retry strategy
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers padrão
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        _thread_local.session = session
    
    return _thread_local.session

def iniciar_driver() -> Optional[webdriver.Chrome]:
    """
    Inicializa e retorna uma instância otimizada do WebDriver do Selenium.
    
    Returns:
        webdriver.Chrome or None: Instância do driver ou None em caso de falha.
    """
    logger.info("Iniciando o navegador (WebDriver)...")
    try:
        options = webdriver.ChromeOptions()
        
        # Configurações de performance
        options.add_argument('--headless=new')  # Versão mais recente do headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')  # Não carrega imagens para ser mais rápido
        options.add_argument('--disable-javascript')  # Desabilita JS se não necessário
        options.add_argument('--window-size=1920,1080')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Configurações de log
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Configurações de rede
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Bloqueia imagens
            "profile.default_content_setting_values.notifications": 2,  # Bloqueia notificações
        }
        options.add_experimental_option("prefs", prefs)
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Configurações adicionais
        driver.set_page_load_timeout(TIMEOUT)
        driver.implicitly_wait(10)
        
        logger.info("Navegador iniciado com sucesso em modo otimizado.")
        return driver
        
    except WebDriverException as e:
        logger.error(f"Falha ao iniciar o WebDriver: {e}")
        return None

def fechar_driver(driver: Optional[webdriver.Chrome]) -> None:
    """
    Fecha a instância do WebDriver de forma segura.
    
    Args:
        driver: Instância do WebDriver a ser fechada.
    """
    if driver:
        try:
            driver.quit()
            logger.info("Navegador (WebDriver) finalizado com sucesso.")
        except Exception as e:
            logger.warning(f"Erro ao fechar o driver: {e}")

# Alias para manter compatibilidade com código existente
close_driver = fechar_driver

@contextmanager
def driver_context():
    """
    Context manager para gerenciar automaticamente o ciclo de vida do driver.
    
    Usage:
        with driver_context() as driver:
            if driver:
                # usar o driver
    """
    driver = iniciar_driver()
    try:
        yield driver
    finally:
        fechar_driver(driver)

def fazer_requisicao(url: str, use_selenium: bool = False, driver: Optional[webdriver.Chrome] = None) -> Optional[BeautifulSoup]:
    """
    Faz uma requisição HTTP para a URL e retorna um objeto BeautifulSoup.
    Prioriza requests HTTP, usa Selenium apenas quando necessário.
    
    Args:
        url (str): A URL a ser acessada.
        use_selenium (bool): Se deve usar Selenium ao invés de requests.
        driver (webdriver.Chrome, optional): Instância do driver para reutilizar.
        
    Returns:
        BeautifulSoup or None: O objeto soup da página ou None em caso de falha.
    """
    logger.debug(f"Fazendo requisição para: {url}")
    
    # Controle de rate limiting
    time.sleep(REQUEST_DELAY)
    
    if use_selenium:
        return _fazer_requisicao_selenium(url, driver)
    else:
        return _fazer_requisicao_http(url)

def _fazer_requisicao_http(url: str) -> Optional[BeautifulSoup]:
    """Faz requisição usando requests HTTP (método preferido)."""
    try:
        session = _get_session()
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        logger.debug(f"Requisição HTTP bem-sucedida para: {url}")
        return BeautifulSoup(response.text, 'lxml')
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro na requisição HTTP para {url}: {e}")
        logger.info("Tentando novamente com Selenium...")
        return _fazer_requisicao_selenium(url)

def _fazer_requisicao_selenium(url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[BeautifulSoup]:
    """Faz requisição usando Selenium (fallback)."""
    driver_criado = False
    
    try:
        if not driver:
            driver = iniciar_driver()
            driver_criado = True
            
        if not driver:
            logger.error("Falha ao inicializar o driver Selenium")
            return None
            
        driver.get(url)
        
        # Aguarda o carregamento da página
        WebDriverWait(driver, TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        logger.debug(f"Requisição Selenium bem-sucedida para: {url}")
        return BeautifulSoup(driver.page_source, 'lxml')
        
    except (WebDriverException, TimeoutException) as e:
        logger.error(f"Erro na requisição Selenium para {url}: {e}")
        _salvar_html_fallback(url, driver)
        return None
        
    finally:
        if driver_criado and driver:
            fechar_driver(driver)

def _salvar_html_fallback(url: str, driver: Optional[webdriver.Chrome]) -> None:
    """Salva o HTML da página em caso de erro para debug."""
    try:
        if driver:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fallback_{timestamp}_{url.replace('/', '_').replace(':', '')}.html"
            filepath = os.path.join(FALLBACK_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"HTML de fallback salvo em: {filepath}")
            
    except Exception as e:
        logger.error(f"Falha ao salvar HTML de fallback: {e}")

def encontrar_links_temporadas(driver: webdriver.Chrome) -> List[webdriver.remote.webelement.WebElement]:
    """
    Busca links de temporadas na página usando diferentes estratégias.
    
    Args:
        driver: Instância do WebDriver.
        
    Returns:
        List: Lista de elementos de link encontrados.
    """
    try:
        # Estratégia 1: Seletor CSS específico
        links = driver.find_elements(By.CSS_SELECTOR, "div#all_comps a[href*='/comps/']")
        
        if not links:
            # Estratégia 2: XPath mais geral
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/comps/')]")
            
        if not links:
            # Estratégia 3: Aguardar carregamento dinâmico
            wait = WebDriverWait(driver, 10)
            links = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/comps/']"))
            )
            
        logger.debug(f"Encontrados {len(links)} links de temporadas")
        return links
        
    except (WebDriverException, TimeoutException) as e:
        logger.error(f"Erro ao buscar links de temporadas: {e}")
        return []

def extrair_nome_e_genero(href: str) -> tuple[str, str]:
    """
    Extrai nome da competição e gênero a partir do href.
    
    Args:
        href (str): URL ou parte da URL contendo informações da competição.
        
    Returns:
        tuple: (nome_competicao, genero)
    """
    # Mapeamento expandido de competições
    competicoes_map = {
        "/comps/9/": ("Premier League", "Masculino"),
        "/comps/106/": ("Serie A", "Feminino"),
        "/comps/183/": ("Bundesliga", "Feminino"),
        "/comps/20/": ("Bundesliga", "Masculino"),
        "/comps/11/": ("Serie A", "Masculino"),  # Italiano
        "/comps/12/": ("La Liga", "Masculino"),
        "/comps/13/": ("Ligue 1", "Masculino"),
        # Adicionar mais conforme necessário
    }
    
    for comp_id, (nome, genero) in competicoes_map.items():
        if comp_id in href:
            return nome, genero
            
    logger.warning(f"Competição não mapeada para href: {href}")
    return "Indefinido", "Desconhecido"

def extrair_tabelas_da_pagina(soup: BeautifulSoup) -> List[BeautifulSoup]:
    """
    Extrai todas as tabelas da página, incluindo as em comentários HTML.
    
    Args:
        soup: Objeto BeautifulSoup da página.
        
    Returns:
        List: Lista de objetos BeautifulSoup representando tabelas.
    """
    if not soup:
        return []
        
    tabelas = []
    
    # Tabelas normais
    tabelas.extend(soup.find_all('table'))
    
    # Tabelas em comentários HTML (comum no FBRef)
    comentarios = soup.find_all(string=lambda text: isinstance(text, Comment))
    
    for comentario in comentarios:
        try:
            comment_soup = BeautifulSoup(comentario, 'lxml')
            tabelas.extend(comment_soup.find_all('table'))
        except Exception as e:
            logger.debug(f"Erro ao processar comentário HTML: {e}")
            continue
    
    logger.debug(f"Encontradas {len(tabelas)} tabelas na página")
    return tabelas

def limpar_recursos():
    """
    Limpa recursos globais (sessões HTTP, etc.).
    Deve ser chamado ao final da execução.
    """
    if hasattr(_thread_local, 'session'):
        try:
            _thread_local.session.close()
            logger.info("Sessão HTTP fechada")
        except Exception as e:
            logger.warning(f"Erro ao fechar sessão HTTP: {e}")

def verificar_rate_limit(response: requests.Response) -> bool:
    """
    Verifica se a resposta indica rate limiting.
    
    Args:
        response: Objeto Response do requests.
        
    Returns:
        bool: True se foi detectado rate limiting.
    """
    if response.status_code == 429:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            logger.warning(f"Rate limit detectado. Aguardando {retry_after} segundos...")
            time.sleep(int(retry_after))
        else:
            logger.warning("Rate limit detectado. Aguardando 60 segundos...")
            time.sleep(60)
        return True
    return False

# Configurar logging ao importar o módulo
configurar_logging()