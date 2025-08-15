"""
SCRAPER BASE COM PLAYWRIGHT
============================

Classe base para todos os scrapers usando Playwright da Microsoft.
Oferece funcionalidades avançadas como auto-wait, screenshots, interceptação de requisições,
e suporte a múltiplos navegadores.

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from datetime import datetime
import json

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response, Request
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class PlaywrightBaseScraper:
    """
    Classe base para scrapers usando Playwright.
    
    Funcionalidades:
    - Auto-wait inteligente para elementos
    - Screenshots automáticos para debug
    - Interceptação de requisições
    - Suporte a múltiplos navegadores
    - Modo headless configurável
    - Retry automático em falhas
    - Logging detalhado
    """
    
    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        viewport: Dict[str, int] = None,
        user_agent: str = None,
        timeout: int = 30000,
        screenshot_dir: str = "screenshots",
        enable_video: bool = False,
        enable_har: bool = False
    ):
        """
        Inicializa o scraper base.
        
        Args:
            headless: Executar em modo headless
            browser_type: Tipo de navegador (chromium, firefox, webkit)
            viewport: Tamanho da janela (ex: {"width": 1920, "height": 1080})
            user_agent: User agent personalizado
            timeout: Timeout para operações (ms)
            screenshot_dir: Diretório para screenshots
            enable_video: Gravar vídeo das sessões
            enable_har: Salvar arquivo HAR (HTTP Archive)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.user_agent = user_agent
        self.timeout = timeout
        self.screenshot_dir = Path(screenshot_dir)
        self.enable_video = enable_video
        self.enable_har = enable_har
        
        # Criar diretório de screenshots
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Atributos do Playwright
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Configurações de retry
        self.max_retries = 3
        self.retry_delay = 2
        
        # Interceptação de requisições
        self.intercepted_requests = []
        self.intercepted_responses = []
        
        logger.info(f"🎭 PlaywrightBaseScraper inicializado: {browser_type}, headless={headless}")
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.stop()
    
    async def start(self):
        """Inicia o Playwright e navegador."""
        try:
            logger.info("🚀 Iniciando Playwright...")
            
            self.playwright = await async_playwright().start()
            
            # Selecionar navegador
            if self.browser_type == "chromium":
                browser_launcher = self.playwright.chromium
            elif self.browser_type == "firefox":
                browser_launcher = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"Tipo de navegador inválido: {self.browser_type}")
            
            # Configurações do navegador
            browser_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
            
            # Lançar navegador
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=browser_args
            )
            
            # Configurações do contexto
            context_options = {
                "viewport": self.viewport,
                "user_agent": self.user_agent,
                "ignore_https_errors": True,
                "java_script_enabled": True
            }
            
            # Adicionar gravação de vídeo se habilitado
            if self.enable_video:
                video_path = self.screenshot_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                context_options["record_video_dir"] = str(self.screenshot_dir)
                context_options["record_video_size"] = self.viewport
            
            # Adicionar HAR se habilitado
            if self.enable_har:
                har_path = self.screenshot_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.har"
                context_options["record_har_path"] = str(har_path)
            
            # Criar contexto
            self.context = await self.browser.new_context(**context_options)
            
            # Configurar interceptação de requisições
            await self._setup_request_interception()
            
            # Criar página
            self.page = await self.context.new_page()
            
            # Configurar timeouts
            self.page.set_default_timeout(self.timeout)
            self.page.set_default_navigation_timeout(self.timeout)
            
            # Configurar handlers de erro
            self.page.on("pageerror", self._handle_page_error)
            self.page.on("requestfailed", self._handle_request_failed)
            
            logger.info(f"✅ Playwright iniciado com sucesso: {self.browser_type}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar Playwright: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Para o Playwright e fecha navegador."""
        try:
            if self.page:
                await self.page.close()
                logger.info("📄 Página fechada")
            
            if self.context:
                await self.context.close()
                logger.info("🔒 Contexto fechado")
            
            if self.browser:
                await self.browser.close()
                logger.info("🌐 Navegador fechado")
            
            if self.playwright:
                await self.playwright.stop()
                logger.info("🛑 Playwright parado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao parar Playwright: {e}")
    
    async def _setup_request_interception(self):
        """Configura interceptação de requisições."""
        if not self.context:
            return
        
        await self.context.route("**/*", self._handle_route)
        logger.info("🔍 Interceptação de requisições configurada")
    
    async def _handle_route(self, route):
        """Intercepta e processa requisições."""
        request = route.request
        
        # Registrar requisição
        request_info = {
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "timestamp": datetime.now().isoformat()
        }
        self.intercepted_requests.append(request_info)
        
        # Continuar com a requisição
        await route.continue_()
    
    async def _handle_page_error(self, error):
        """Handler para erros de página."""
        logger.error(f"❌ Erro de página: {error}")
    
    async def _handle_request_failed(self, request):
        """Handler para requisições que falharam."""
        logger.warning(f"⚠️ Requisição falhou: {request.url} - {request.failure}")
    
    async def navigate_to(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navega para uma URL com retry automático.
        
        Args:
            url: URL para navegar
            wait_until: Condição de espera (load, domcontentloaded, networkidle)
        
        Returns:
            True se navegação bem-sucedida
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🌐 Navegando para: {url} (tentativa {attempt + 1})")
                
                response = await self.page.goto(url, wait_until=wait_until)
                
                if response and response.ok:
                    logger.info(f"✅ Navegação bem-sucedida: {response.status}")
                    return True
                else:
                    logger.warning(f"⚠️ Navegação falhou: {response.status if response else 'Sem resposta'}")
                    
            except PlaywrightTimeoutError:
                logger.warning(f"⏰ Timeout na navegação (tentativa {attempt + 1})")
            except Exception as e:
                logger.error(f"❌ Erro na navegação (tentativa {attempt + 1}): {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay)
        
        logger.error(f"❌ Falha na navegação após {self.max_retries} tentativas")
        return False
    
    async def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """
        Aguarda elemento aparecer na página.
        
        Args:
            selector: Seletor CSS ou XPath
            timeout: Timeout personalizado (ms)
        
        Returns:
            True se elemento encontrado
        """
        try:
            timeout = timeout or self.timeout
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.info(f"✅ Elemento encontrado: {selector}")
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"⏰ Timeout aguardando elemento: {selector}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro aguardando elemento {selector}: {e}")
            return False
    
    async def click_element(self, selector: str, force: bool = False) -> bool:
        """
        Clica em um elemento.
        
        Args:
            selector: Seletor CSS ou XPath
            force: Forçar clique mesmo se elemento não visível
        
        Returns:
            True se clique bem-sucedido
        """
        try:
            await self.page.click(selector, force=force)
            logger.info(f"🖱️ Clique realizado: {selector}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao clicar em {selector}: {e}")
            return False
    
    async def fill_input(self, selector: str, value: str) -> bool:
        """
        Preenche campo de input.
        
        Args:
            selector: Seletor CSS ou XPath
            value: Valor para preencher
        
        Returns:
            True se preenchimento bem-sucedido
        """
        try:
            await self.page.fill(selector, value)
            logger.info(f"✏️ Campo preenchido: {selector} = {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao preencher campo {selector}: {e}")
            return False
    
    async def get_text(self, selector: str) -> Optional[str]:
        """
        Obtém texto de um elemento.
        
        Args:
            selector: Seletor CSS ou XPath
        
        Returns:
            Texto do elemento ou None
        """
        try:
            text = await self.page.text_content(selector)
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"❌ Erro ao obter texto de {selector}: {e}")
            return None
    
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Obtém atributo de um elemento.
        
        Args:
            selector: Seletor CSS ou XPath
            attribute: Nome do atributo
        
        Returns:
            Valor do atributo ou None
        """
        try:
            value = await self.page.get_attribute(selector, attribute)
            return value
        except Exception as e:
            logger.error(f"❌ Erro ao obter atributo {attribute} de {selector}: {e}")
            return None
    
    async def take_screenshot(self, filename: str = None) -> Optional[str]:
        """
        Tira screenshot da página atual.
        
        Args:
            filename: Nome do arquivo (opcional)
        
        Returns:
            Caminho do arquivo salvo ou None
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = self.screenshot_dir / filename
            await self.page.screenshot(path=str(filepath))
            
            logger.info(f"📸 Screenshot salvo: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao tirar screenshot: {e}")
            return None
    
    async def get_page_content(self) -> str:
        """
        Obtém conteúdo HTML da página atual.
        
        Returns:
            HTML da página
        """
        try:
            content = await self.page.content()
            logger.info("📄 Conteúdo da página obtido")
            return content
        except Exception as e:
            logger.error(f"❌ Erro ao obter conteúdo da página: {e}")
            return ""
    
    async def evaluate_javascript(self, script: str) -> Any:
        """
        Executa JavaScript na página.
        
        Args:
            script: Código JavaScript para executar
        
        Returns:
            Resultado da execução
        """
        try:
            result = await self.page.evaluate(script)
            logger.info("⚡ JavaScript executado com sucesso")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao executar JavaScript: {e}")
            return None
    
    async def wait_for_load_state(self, state: str = "networkidle") -> bool:
        """
        Aguarda estado específico da página.
        
        Args:
            state: Estado para aguardar (load, domcontentloaded, networkidle)
        
        Returns:
            True se estado alcançado
        """
        try:
            await self.page.wait_for_load_state(state)
            logger.info(f"✅ Estado da página: {state}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro aguardando estado {state}: {e}")
            return False
    
    def get_intercepted_data(self) -> Dict[str, List]:
        """Retorna dados interceptados das requisições."""
        return {
            "requests": self.intercepted_requests,
            "responses": self.intercepted_responses
        }
    
    async def clear_intercepted_data(self):
        """Limpa dados interceptados."""
        self.intercepted_requests.clear()
        self.intercepted_responses.clear()
        logger.info("🧹 Dados interceptados limpos")
    
    async def scroll_to_bottom(self, delay: float = 0.5):
        """
        Rola a página até o final.
        
        Args:
            delay: Delay entre rolagens (segundos)
        """
        try:
            await self.page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight);
            """)
            await asyncio.sleep(delay)
            logger.info("📜 Página rolada até o final")
        except Exception as e:
            logger.error(f"❌ Erro ao rolar página: {e}")
    
    async def wait_for_network_idle(self, timeout: int = None):
        """
        Aguarda rede ficar ociosa.
        
        Args:
            timeout: Timeout personalizado (ms)
        """
        try:
            timeout = timeout or self.timeout
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.info("🌐 Rede ociosa")
        except Exception as e:
            logger.error(f"❌ Erro aguardando rede ociosa: {e}")

# Função de conveniência para uso síncrono
def run_async(coro):
    """Executa corotina de forma síncrona."""
    return asyncio.run(coro)
