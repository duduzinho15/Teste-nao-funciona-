import logging
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup, Comment
from selenium.webdriver.common.by import By

# --- CONFIGURAÇÕES GLOBAIS ---
BASE_URL = "https://fbref.com"
ARQUIVO_ERRO_LOG = 'erros_coleta.log'
driver = None # Variável global para a instância do navegador

# --- FUNÇÕES DE CONTROLE DO NAVEGADOR E REQUISIÇÃO ---

def setup_driver():
    """Inicia e retorna a instância global do navegador Chrome via Selenium."""
    global driver
    if driver is None:
        try:
            logging.info("Iniciando o navegador (WebDriver)...")
            options = webdriver.ChromeOptions()
            # Argumentos para rodar em modo invisível (headless)
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument("--log-level=3") # Suprime logs desnecessários
            
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logging.info("Navegador iniciado com sucesso em modo invisível.")
        except Exception as e:
            logging.error(f"Falha ao iniciar o WebDriver: {e}")
            driver = None
    return driver

def close_driver():
    """Fecha a instância do navegador se ela estiver aberta."""
    global driver
    if driver:
        driver.quit()
        logging.info("Navegador (WebDriver) finalizado.")
        driver = None

def fazer_requisicao(url):
    """Navega até uma URL usando Selenium e retorna o conteúdo da página."""
    driver = setup_driver()
    if not driver: return None
    try:
        time.sleep(3) # Pausa para evitar sobrecarregar o site
        driver.get(url)
        return BeautifulSoup(driver.page_source, 'lxml')
    except WebDriverException as e:
        logging.error(f"O Selenium falhou ao tentar acessar a URL: {url}")
        registrar_erro(url, e)
        return None

def registrar_erro(url, erro):
    """Registra um erro em um arquivo de log para análise posterior."""
    with open(ARQUIVO_ERRO_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] Erro ao processar: {url}\n  Detalhe: {str(erro)}\n\n")

def encontrar_links_temporadas(driver):
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "div#all_comps a[href*='/comps/']")
        if not links:
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/comps/')]")
        return links
    except Exception as e:
        print(f"Erro ao buscar links de temporadas: {e}")
        return []

def extrair_nome_e_genero(href):
    if "/comps/9/" in href:
        return "Serie A", "Masculino"
    elif "/comps/106/" in href:
        return "Serie A", "Feminino"
    elif "/comps/183/" in href:
        return "Bundesliga", "Feminino"
    elif "/comps/20/" in href:
        return "Bundesliga", "Masculino"
    else:
        return "Indefinido", "Desconhecido"        

def extrair_tabelas_da_pagina(soup):
    """Encontra e extrai todas as tabelas, incluindo as escondidas em comentários HTML."""
    if not soup: return []
    all_tables = soup.find_all('table')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'lxml')
        all_tables.extend(comment_soup.find_all('table'))
    return all_tables