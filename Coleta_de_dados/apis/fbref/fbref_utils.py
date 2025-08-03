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
import re

# Constantes globais
BASE_URL = "https://fbref.com"
FALLBACK_DIR = "fallback_htmls"
REQUEST_DELAY = 3.0  # Aumentado para 3 segundos para evitar rate limiting
MAX_RETRIES = 5
TIMEOUT = 30
RATE_LIMIT_DELAY = 300  # 5 minutos de espera para rate limiting
MAX_RATE_LIMIT_RETRIES = 2  # Reduzido para 2 tentativas
USE_PROXY_ROTATION = True  # Ativar rotação de proxies

# Thread-local storage para múltiplas instâncias
_thread_local = threading.local()

# Configuração de diretórios
os.makedirs(FALLBACK_DIR, exist_ok=True)

# Configuração de logging
logger = logging.getLogger(__name__)

# Sistemas Anti-429 Globais
_state_machine = None
_proxy_system = None
_header_system = None
_systems_initialized = False

def _initialize_anti_429_systems():
    """Inicializa os sistemas anti-429 globalmente."""
    global _state_machine, _proxy_system, _header_system, _systems_initialized
    
    if _systems_initialized:
        return
    
    try:
        # Importar sistemas anti-429 (lazy loading)
        from .anti_429_state_machine import Anti429StateMachine
        from .proxy_rotation_system import ProxyRotationSystem
        from .browser_emulation_headers import BrowserEmulationHeaders
        
        # Máquina de estados anti-429
        _state_machine = Anti429StateMachine()
        
        # Sistema de rotação de proxies
        _proxy_system = ProxyRotationSystem()
        
        # Sistema de cabeçalhos de emulação
        _header_system = BrowserEmulationHeaders()
        
        _systems_initialized = True
        logger.info("Sistemas anti-429 inicializados com sucesso")
        
    except ImportError as e:
        logger.warning(f"Sistemas anti-429 nao disponiveis: {e}")
        _systems_initialized = False
    except Exception as e:
        logger.error(f"Erro ao inicializar sistemas anti-429: {e}")
        _systems_initialized = False

def get_anti_429_systems():
    """Retorna os sistemas anti-429 inicializados."""
    if not _systems_initialized:
        _initialize_anti_429_systems()
    
    return _state_machine, _proxy_system, _header_system

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
            backoff_factor=2,  # Aumentado para backoff mais agressivo
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers mais realistas para evitar detecção
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
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

def extrair_conteudo_comentarios_html(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Extrai e parseia conteúdo de comentários HTML - tática específica do FBRef.
    
    O FBRef frequentemente oculta tabelas importantes dentro de comentários HTML
    para dificultar o scraping. Esta função encontra esses comentários e os
    converte em elementos HTML parseáveis.
    
    Args:
        soup: Objeto BeautifulSoup da página original
        
    Returns:
        BeautifulSoup: Nova instância com conteúdo dos comentários incluído
    """
    logger.debug("Procurando conteudo em comentarios HTML...")
    
    # Encontrar todos os comentários HTML
    comentarios = soup.find_all(string=lambda text: isinstance(text, Comment))
    
    if not comentarios:
        logger.debug("Nenhum comentario encontrado")
        return soup
    
    logger.debug(f"Encontrados {len(comentarios)} comentarios para analisar")
    
    # Coletar conteúdo dos comentários que contêm HTML
    conteudos_html = []
    
    for i, comentario in enumerate(comentarios):
        conteudo_comentario = str(comentario).strip()
        
        # Verificar se o comentário contém HTML estruturado
        if any(tag in conteudo_comentario.lower() for tag in ['<table', '<div', '<tbody', '<tr', '<td']):
            logger.debug(f"Comentario {i+1}: Encontrado conteudo HTML ({len(conteudo_comentario)} chars)")
            conteudos_html.append(conteudo_comentario)
    
    if not conteudos_html:
        logger.debug("Nenhum conteudo HTML relevante encontrado em comentarios")
        return soup
    
    # Criar novo HTML combinando o original com o conteúdo dos comentários
    html_original = str(soup)
    
    # Adicionar conteúdo dos comentários ao final do body
    if '</body>' in html_original:
        # Inserir antes do fechamento do body
        conteudo_extra = '\n'.join(conteudos_html)
        novo_html = html_original.replace('</body>', f'\n{conteudo_extra}\n</body>')
    else:
        # Se não tem body, adicionar ao final
        conteudo_extra = '\n'.join(conteudos_html)
        novo_html = html_original + '\n' + conteudo_extra
    
    logger.info(f"Conteudo extraido de {len(conteudos_html)} comentarios HTML - reparsing...")
    return BeautifulSoup(novo_html, 'lxml')

def processar_soup_com_comentarios(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Processa um objeto BeautifulSoup aplicando parsing de comentários se necessário.
    
    Args:
        soup: BeautifulSoup original
        
    Returns:
        BeautifulSoup: Processado com conteúdo de comentários se encontrado
    """
    if soup is None:
        return None
        
    # Primeiro tenta encontrar tabelas normalmente
    tabelas_normais = soup.find_all('table')
    
    # Se não encontrou tabelas ou encontrou poucas, tenta extrair de comentários
    if len(tabelas_normais) < 2:  # FBRef geralmente tem múltiplas tabelas por página
        logger.debug("🔄 Poucas tabelas encontradas, tentando extrair de comentários...")
        soup_processado = extrair_conteudo_comentarios_html(soup)
        
        # Verifica se encontrou mais tabelas após processar comentários
        tabelas_processadas = soup_processado.find_all('table')
        if len(tabelas_processadas) > len(tabelas_normais):
            logger.info(f"🎉 Sucesso! Tabelas encontradas: {len(tabelas_normais)} → {len(tabelas_processadas)}")
            return soup_processado
    
    return soup

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
    
    try:
        if use_selenium:
            logger.debug("Usando Selenium para requisição...")
            soup = _fazer_requisicao_selenium(url, driver)
        else:
            logger.debug("Usando requests HTTP para requisição...")
            soup = _fazer_requisicao_http(url)
        
        # Aplica parsing de comentários HTML (tática específica do FBRef)
        if soup is not None:
            soup = processar_soup_com_comentarios(soup)
        
        return soup
        
    except Exception as e:
        logger.error(f"Erro inesperado em fazer_requisicao para {url}: {e}")
        return None

def _fazer_requisicao_http(url: str) -> Optional[BeautifulSoup]:
    """Faz requisição usando requests HTTP com sistema anti-429 avançado."""
    
    # Inicializar sistemas anti-429
    state_machine, proxy_system, header_system = get_anti_429_systems()
    
    # Inicializar sistema anti-bloqueio simplificado (sem travamentos)
    try:
        from .simple_anti_blocking import get_simple_anti_blocking
        simple_anti_blocking = get_simple_anti_blocking()
    except ImportError:
        logger.warning("Sistema anti-bloqueio simplificado não disponível")
        simple_anti_blocking = None
    
    # Manter compatibilidade com sistema avançado (fallback)
    try:
        from .advanced_anti_blocking import get_advanced_anti_blocking, record_fbref_request, should_change_identity
        anti_blocking = get_advanced_anti_blocking()
    except ImportError:
        anti_blocking = None
    
    # Verificar se deve continuar fazendo scraping
    if state_machine and not state_machine.should_continue_scraping():
        logger.error("Máquina de estados indica parada - não fazendo requisição")
        return None
    
    # Verificar se deve trocar identidade antes da requisição
    if anti_blocking and should_change_identity():
        logger.info("Trocando identidade para evitar detecção")
        if state_machine:
            state_machine.request_identity_change()
        if header_system:
            header_system.reset_session()
        if anti_blocking:
            anti_blocking.reset_session()
    
    # Usar sistema anti-bloqueio simplificado (prioridade)
    if simple_anti_blocking:
        logger.debug("Usando sistema anti-bloqueio simplificado")
        response = simple_anti_blocking.make_request(url)
        
        if response and response.status_code == 200:
            # Sucesso com sistema simplificado!
            logger.debug(f"Requisição bem-sucedida (simplificado): {url}")
            
            # Registrar sucesso nos outros sistemas
            if state_machine:
                state_machine.record_success(url)
            if anti_blocking:
                record_fbref_request(url, True, 0.0, 200)
            
            return BeautifulSoup(response.text, 'lxml')
        
        elif response is None:
            # Falha no sistema simplificado - registrar
            if anti_blocking:
                record_fbref_request(url, False, 0.0, None)
            
            logger.debug("Sistema simplificado falhou - usando fallback")
            return None  # Usar fallback
    
    # Fallback para sistema avançado se simplificado não disponível
    elif state_machine:
        # Delay da máquina de estados (limitado)
        wait_time = state_machine.get_wait_time()
        if wait_time > 0:
            wait_time = min(wait_time, 8.0)  # Máximo 8 segundos
            logger.debug(f"Aguardando {wait_time:.2f}s (máquina de estados)")
            time.sleep(wait_time)
    
    # Obter proxy se disponível
    current_proxy = None
    proxy_dict = None
    if proxy_system and proxy_system.has_available_proxies():
        current_proxy = proxy_system.get_next_proxy()
        if current_proxy:
            proxy_dict = proxy_system.get_proxy_dict(current_proxy)
            logger.debug(f"Usando proxy: {current_proxy.host}:{current_proxy.port}")
    
    # Gerar cabeçalhos completos
    headers = {}
    if header_system:
        headers = header_system.get_headers_for_fbref(url)
        logger.debug(f"Usando {len(headers)} cabeçalhos de emulação")
    
    # Fazer requisição com todos os sistemas integrados
    start_time = time.time()
    
    try:
        logger.debug(f"Requisição HTTP avançada para: {url}")
        
        # Usar sessão com configurações avançadas
        session = _get_session()
        
        # Aplicar cabeçalhos
        if headers:
            session.headers.update(headers)
        
        # Timeout mais agressivo para evitar travamentos
        timeout_connect = 10  # 10s para conectar
        timeout_read = 20     # 20s para ler resposta
        
        logger.debug(f"Fazendo requisição com timeout ({timeout_connect}s, {timeout_read}s)")
        
        # Fazer requisição
        response = session.get(
            url, 
            proxies=proxy_dict,
            timeout=(timeout_connect, timeout_read),
            allow_redirects=True
        )
        
        response_time = time.time() - start_time
        
        # Processar resposta baseada no código de status
        if response.status_code == 200:
            # Sucesso!
            logger.debug(f"Requisição bem-sucedida: {url} ({len(response.text)} bytes, {response_time:.2f}s)")
            
            # Registrar sucesso nos sistemas
            if state_machine:
                state_machine.record_success(url)
            if current_proxy:
                proxy_system.record_proxy_result(current_proxy, True, response_time)
            if header_system:
                header_system.update_referer(url)
            if anti_blocking:
                record_fbref_request(url, True, response_time, 200)
            
            return BeautifulSoup(response.text, 'lxml')
        
        elif response.status_code == 429:
            # Rate limiting detectado
            retry_after = None
            if 'Retry-After' in response.headers:
                try:
                    retry_after = int(response.headers['Retry-After'])
                except ValueError:
                    pass
            
            logger.warning(f"Rate limit detectado (429) para {url} - Retry-After: {retry_after}")
            
            # Registrar erro nos sistemas
            if state_machine:
                state_machine.record_429_error(url, retry_after)
            if current_proxy:
                proxy_system.record_proxy_result(current_proxy, False)
            if anti_blocking:
                record_fbref_request(url, False, response_time, 429)
            
            # Estratégia agressiva para contornar 429
            if anti_blocking:
                # Analisar se deve tentar estratégia alternativa
                stats = anti_blocking.get_session_statistics()
                if stats['success_rate'] < 0.3:  # Taxa de sucesso muito baixa
                    logger.info("Taxa de sucesso baixa - implementando estratégia agressiva")
                    
                    # Forçar troca de identidade
                    if state_machine:
                        state_machine.request_identity_change()
                    if header_system:
                        header_system.reset_session()
                    anti_blocking.reset_session()
                    
                    # Delay mais longo antes de tentar novamente
                    aggressive_delay = retry_after if retry_after else 60
                    logger.info(f"Aguardando {aggressive_delay}s para estratégia agressiva")
                    time.sleep(aggressive_delay)
                    
                    # Tentar novamente com nova identidade
                    return _fazer_requisicao_http(url)
            
            # Verificar se deve mudar identidade (estratégia padrão)
            if state_machine and state_machine.get_current_state().value == "RECONFIGURING":
                if state_machine.request_identity_change():
                    logger.info("Mudando identidade após rate limiting")
                    if header_system:
                        header_system.reset_session()
                    # Tentar novamente com nova identidade
                    return _fazer_requisicao_http(url)
            
            return None  # Usar fallback
        
        elif response.status_code >= 500:
            # Erro do servidor
            logger.warning(f"Erro do servidor ({response.status_code}) para {url}")
            if state_machine:
                state_machine.record_connection_error(url, f"HTTP_{response.status_code}")
            if current_proxy:
                proxy_system.record_proxy_result(current_proxy, False)
            
            return None  # Usar fallback
        
        else:
            # Outros erros HTTP
            logger.error(f"Erro HTTP {response.status_code} para {url}")
            if current_proxy:
                proxy_system.record_proxy_result(current_proxy, False)
            
            return None
    
    except requests.exceptions.Timeout as e:
        logger.warning(f"Timeout na requisição para {url}: {e}")
        if state_machine:
            state_machine.record_connection_error(url, "timeout")
        if current_proxy:
            proxy_system.record_proxy_result(current_proxy, False)
        if anti_blocking:
            record_fbref_request(url, False, response_time, None)
        return None
    
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"Erro de conexão para {url}: {e}")
        if state_machine:
            state_machine.record_connection_error(url, "connection_error")
        if current_proxy:
            proxy_system.record_proxy_result(current_proxy, False)
        if anti_blocking:
            record_fbref_request(url, False, response_time, None)
        return None
    
    except requests.exceptions.ProxyError as e:
        logger.warning(f"Erro de proxy para {url}: {e}")
        if current_proxy:
            proxy_system.record_proxy_result(current_proxy, False)
        if anti_blocking:
            record_fbref_request(url, False, response_time, None)
        # Tentar sem proxy
        return _fazer_requisicao_http_sem_proxy(url)
    
    except Exception as e:
        logger.error(f"Erro inesperado na requisição para {url}: {e}")
        if current_proxy:
            proxy_system.record_proxy_result(current_proxy, False)
        if anti_blocking:
            record_fbref_request(url, False, response_time, None)
        return None

def _fazer_requisicao_http_sem_proxy(url: str) -> Optional[BeautifulSoup]:
    """Fallback para requisição sem proxy quando proxy falha."""
    try:
        logger.debug(f"Tentativa sem proxy para: {url}")
        
        # Usar sessão simples sem proxy
        session = _get_session()
        
        # Cabeçalhos básicos
        _, _, header_system = get_anti_429_systems()
        if header_system:
            headers = header_system.get_headers_for_fbref(url)
            session.headers.update(headers)
        
        response = session.get(url, timeout=(15, 30))
        
        if response.status_code == 200:
            logger.debug(f"Sucesso sem proxy: {url}")
            return BeautifulSoup(response.text, 'lxml')
        else:
            logger.warning(f"Falha sem proxy ({response.status_code}): {url}")
            return None
            
    except Exception as e:
        logger.error(f"Erro na requisição sem proxy para {url}: {e}")
        return None

def _fazer_requisicao_selenium(url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[BeautifulSoup]:
    """Faz requisição usando Selenium (fallback)."""
    driver_criado = False
    
    try:
        logger.debug(f"Iniciando requisição Selenium para: {url}")
        
        if not driver:
            logger.debug("Criando nova instância do driver Selenium...")
            driver = iniciar_driver()
            driver_criado = True
            
        if not driver:
            logger.error("Falha ao inicializar o driver Selenium")
            return None
            
        logger.debug(f"Navegando para: {url}")
        driver.get(url)
        
        # Aguarda o carregamento da página com timeout mais específico
        logger.debug("Aguardando carregamento da página...")
        WebDriverWait(driver, 10).until(  # Reduzido de 20 para 10 segundos
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Aguarda um pouco mais para garantir que o conteúdo foi carregado
        time.sleep(1)  # Reduzido de 2 para 1 segundo
        
        page_source = driver.page_source
        logger.debug(f"Requisição Selenium bem-sucedida para: {url} (tamanho: {len(page_source)} bytes)")
        return BeautifulSoup(page_source, 'lxml')
        
    except TimeoutException as e:
        logger.warning(f"Timeout na requisição Selenium para {url}: {e}")
        _salvar_html_fallback(url, driver)
        return None
    except WebDriverException as e:
        logger.error(f"Erro do WebDriver para {url}: {e}")
        _salvar_html_fallback(url, driver)
        return None
    except Exception as e:
        logger.error(f"Erro inesperado na requisição Selenium para {url}: {e}")
        _salvar_html_fallback(url, driver)
        return None
        
    finally:
        if driver_criado and driver:
            logger.debug("Fechando driver Selenium criado...")
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