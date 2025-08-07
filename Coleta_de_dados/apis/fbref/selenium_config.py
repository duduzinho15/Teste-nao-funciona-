"""
CONFIGURAÇÃO DO SELENIUM PARA WEB SCRAPING
========================================

Configurações e utilitários para o Selenium WebDriver, incluindo opções
para navegação headless, gerenciamento de drivers e configurações de espera.

Autor: Sistema de Coleta de Dados
Data: 2025-08-03
Versão: 1.0
"""

import os
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Configuração de logging
logger = logging.getLogger(__name__)

class SeleniumConfig:
    """Configurações e utilitários para o Selenium WebDriver."""
    
    # Configurações padrão
    DEFAULT_OPTIONS = {
        'headless': True,  # Modo headless ativado por padrão
        'window_size': '1920,1080',
        'disable_gpu': True,
        'no_sandbox': True,
        'disable_dev_shm_usage': True,
        'disable_extensions': True,
        'disable_infobars': True,
        'disable_notifications': True,
        'disable_web_security': True,
        'ignore_certificate_errors': True,
        'log_level': '3',  # Nível de log do Chrome (0-3, onde 3 é o mais silencioso)
    }
    
    # Tempos de espera padrão (em segundos)
    DEFAULT_TIMEOUT = 30
    PAGE_LOAD_TIMEOUT = 60
    SCRIPT_TIMEOUT = 30
    
    def __init__(self, **kwargs):
        """Inicializa a configuração do Selenium.
        
        Args:
            **kwargs: Sobrescreve as configurações padrão.
        """
        self.options = self.DEFAULT_OPTIONS.copy()
        self.options.update(kwargs)
        logger.debug("SeleniumConfig inicializado com opções: %s", self.options)
    
    def get_chrome_options(self) -> ChromeOptions:
        """Retorna as opções configuradas para o Chrome."""
        chrome_options = ChromeOptions()
        
        # Configurações básicas
        if self.options.get('headless'):
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument(f'--window-size={self.options["window_size"]}')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument(f'--log-level={self.options["log_level"]}')
        
        # Configurações de desempenho
        prefs = {
            'profile.default_content_setting_values.notifications': 2,  # Desativa notificações
            'profile.managed_default_content_settings.images': 2,  # Desativa imagens
            'profile.managed_default_content_settings.javascript': 1,  # Mantém JavaScript ativado
            'profile.managed_default_content_settings.stylesheets': 2,  # Desativa CSS
            'profile.managed_default_content_settings.cookies': 2,  # Bloqueia cookies
            'profile.managed_default_content_settings.plugins': 2,  # Desativa plugins
            'profile.managed_default_content_settings.popups': 2,  # Bloqueia popups
            'profile.managed_default_content_settings.geolocation': 2,  # Bloqueia geolocalização
            'profile.managed_default_content_settings.media_stream': 2,  # Bloqueia acesso à mídia
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Configurações adicionais
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-blink-features=BlockCredentialedSubresources')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent personalizado
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return chrome_options
    
    def create_driver(self) -> Optional[WebDriver]:
        """Cria e retorna uma instância do WebDriver configurada."""
        try:
            logger.info("Inicializando WebDriver do Chrome...")
            
            # Configurar o serviço do Chrome
            service = ChromeService(ChromeDriverManager().install())
            
            # Criar instância do WebDriver
            driver = webdriver.Chrome(
                service=service,
                options=self.get_chrome_options()
            )
            
            # Configurar timeouts
            driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(self.SCRIPT_TIMEOUT)
            
            # Configurações adicionais
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("WebDriver inicializado com sucesso")
            return driver
            
        except Exception as e:
            logger.error(f"Falha ao inicializar o WebDriver: {str(e)}")
            return None
    
    @staticmethod
    def wait_for_element(driver: WebDriver, by: str, value: str, timeout: int = None) -> Any:
        """Aguarda até que um elemento esteja presente na página."""
        timeout = timeout or SeleniumConfig.DEFAULT_TIMEOUT
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception as e:
            logger.error(f"Elemento não encontrado: {value} - {str(e)}")
            raise
    
    @staticmethod
    def wait_for_elements(driver: WebDriver, by: str, value: str, timeout: int = None) -> list:
        """Aguarda até que elementos estejam presentes na página."""
        timeout = timeout or SeleniumConfig.DEFAULT_TIMEOUT
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except Exception as e:
            logger.error(f"Elementos não encontrados: {value} - {str(e)}")
            return []
    
    @staticmethod
    def wait_for_page_load(driver: WebDriver, timeout: int = None) -> bool:
        """Aguarda até que a página seja completamente carregada."""
        timeout = timeout or SeleniumConfig.PAGE_LOAD_TIMEOUT
        try:
            return WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except Exception as e:
            logger.error(f"Falha ao aguardar carregamento da página: {str(e)}")
            return False

# Instância global de configuração
selenium_config = SeleniumConfig()

def get_selenium_config(**kwargs) -> SeleniumConfig:
    """Retorna uma instância de SeleniumConfig com configurações personalizadas."""
    return SeleniumConfig(**kwargs)

def create_driver(**kwargs) -> Optional[WebDriver]:
    """Cria e retorna uma instância do WebDriver com configuração padrão."""
    config = SeleniumConfig(**kwargs)
    return config.create_driver()

def close_driver(driver: Optional[WebDriver]) -> None:
    """Fecha o WebDriver de forma segura."""
    if driver:
        try:
            driver.quit()
            logger.info("WebDriver fechado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar o WebDriver: {str(e)}")

# Função de contexto para gerenciar o ciclo de vida do driver
from contextlib import contextmanager

@contextmanager
def driver_context(**kwargs):
    """Context manager para gerenciar o ciclo de vida do WebDriver."""
    driver = None
    try:
        driver = create_driver(**kwargs)
        if driver:
            yield driver
    except Exception as e:
        logger.error(f"Erro no contexto do WebDriver: {str(e)}")
        raise
    finally:
        if driver:
            close_driver(driver)

if __name__ == "__main__":
    # Teste da configuração
    logging.basicConfig(level=logging.INFO)
    logger.info("🔧 Testando configuração do Selenium...")
    
    with driver_context(headless=True) as driver:
        if driver:
            driver.get("https://www.google.com")
            logger.info(f"Título da página: {driver.title}")
            logger.info("✅ Teste de configuração do Selenium concluído com sucesso!")
