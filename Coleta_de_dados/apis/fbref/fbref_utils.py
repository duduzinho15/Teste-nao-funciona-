import logging
import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup, Comment

BASE_URL = "https://fbref.com"
FALLBACK_DIR = "fallback_htmls"
os.makedirs(FALLBACK_DIR, exist_ok=True)
driver = None
logger = logging.getLogger(__name__)

def setup_driver():
    global driver
    if driver is None:
        try:
            logger.info("Iniciando o navegador (WebDriver)...")
            options = webdriver.ChromeOptions()
            options.add_argument('--headless'); options.add_argument('--disable-gpu'); options.add_argument('--window-size=1920,1080')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument("--log-level=3")
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Navegador iniciado com sucesso em modo invisível.")
        except Exception as e:
            logger.error(f"Falha ao iniciar o WebDriver: {e}"); driver = None
    return driver

def close_driver():
    global driver
    if driver:
        driver.quit()
        logger.info("Navegador (WebDriver) finalizado.")
        driver = None


def fazer_requisicao(url):
    driver = setup_driver()
    if not driver: return None
    try:
        time.sleep(3)
        driver.get(url)
        return BeautifulSoup(driver.page_source, 'lxml')
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado ao processar a URL: {url} - Erro: {e}")
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fallback_{timestamp}_{url.replace('/', '_').replace(':', '')}.html"
            filepath = os.path.join(FALLBACK_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"HTML da página com erro foi salvo em: {filepath}")
        except Exception as save_e:
            logger.error(f"Falha ao salvar o HTML de fallback: {save_e}")
        return None

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
    if not soup: return []
    all_tables = soup.find_all('table')
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'lxml'); all_tables.extend(comment_soup.find_all('table'))
    return all_tables