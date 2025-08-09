#!/usr/bin/env python3
"""
Sistema de Cabeçalhos HTTP Completos para Emulação Perfeita de Navegador.

Baseado no documento "Erro 429 Scraping FBREF.md" - Tabela 1: Cabeçalhos Essenciais.
"""

import logging
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class BrowserProfile:
    """Perfil completo de um navegador para emulação."""
    name: str
    user_agent: str
    accept: str
    accept_language: str
    accept_encoding: str
    sec_fetch_site: str
    sec_fetch_mode: str
    sec_fetch_dest: str
    sec_fetch_user: Optional[str] = None
    upgrade_insecure_requests: str = "1"
    dnt: str = "1"  # Do Not Track

class BrowserEmulationHeaders:
    """
    Sistema de cabeçalhos HTTP completos para emulação perfeita de navegador.
    
    Implementa todas as recomendações do documento "Erro 429 Scraping FBREF.md":
    - User-Agent realístico e atualizado
    - Accept headers completos
    - Accept-Language para localização
    - Accept-Encoding para compressão
    - Sec-Fetch-* headers para segurança
    - Referer para simular navegação natural
    - Connection keep-alive
    """
    
    def __init__(self):
        self.browser_profiles = self._initialize_browser_profiles()
        self.current_profile: Optional[BrowserProfile] = None
        self.current_referer: Optional[str] = None
        
        logger.info("Sistema de emulacao de cabecalhos HTTP inicializado")
    
    def _initialize_browser_profiles(self) -> List[BrowserProfile]:
        """Inicializa perfis de navegadores atualizados (2024/2025)."""
        return [
            # Chrome Windows
            BrowserProfile(
                name="Chrome_Windows_Latest",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                accept_language="pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                accept_encoding="gzip, deflate, br",
                sec_fetch_site="same-origin",
                sec_fetch_mode="navigate",
                sec_fetch_dest="document",
                sec_fetch_user="?1"
            ),
            
            # Chrome macOS
            BrowserProfile(
                name="Chrome_macOS_Latest",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                accept_language="en-US,en;q=0.9,pt;q=0.8",
                accept_encoding="gzip, deflate, br",
                sec_fetch_site="same-origin",
                sec_fetch_mode="navigate", 
                sec_fetch_dest="document",
                sec_fetch_user="?1"
            ),
            
            # Firefox Windows
            BrowserProfile(
                name="Firefox_Windows_Latest",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                accept_language="pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                accept_encoding="gzip, deflate, br",
                sec_fetch_site="same-origin",
                sec_fetch_mode="navigate",
                sec_fetch_dest="document",
                sec_fetch_user="?1"
            ),
            
            # Safari macOS
            BrowserProfile(
                name="Safari_macOS_Latest",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                accept_language="en-US,en;q=0.9",
                accept_encoding="gzip, deflate, br",
                sec_fetch_site="same-origin",
                sec_fetch_mode="navigate",
                sec_fetch_dest="document",
                sec_fetch_user="?1"
            ),
            
            # Edge Windows
            BrowserProfile(
                name="Edge_Windows_Latest",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
                accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                accept_language="pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                accept_encoding="gzip, deflate, br",
                sec_fetch_site="same-origin",
                sec_fetch_mode="navigate",
                sec_fetch_dest="document",
                sec_fetch_user="?1"
            )
        ]
    
    def select_random_profile(self) -> BrowserProfile:
        """Seleciona um perfil de navegador aleatório."""
        profile = random.choice(self.browser_profiles)
        self.current_profile = profile
        
        logger.debug(f"Perfil selecionado: {profile.name}")
        return profile
    
    def get_current_profile(self) -> Optional[BrowserProfile]:
        """Retorna o perfil atual."""
        return self.current_profile
    
    def generate_headers(self, url: str, referer: Optional[str] = None, 
                        is_ajax: bool = False) -> Dict[str, str]:
        """
        Gera cabeçalhos HTTP completos para uma requisição.
        
        Args:
            url: URL de destino
            referer: URL de referência (página anterior)
            is_ajax: Se é uma requisição AJAX
            
        Returns:
            Dict com cabeçalhos HTTP completos
        """
        if not self.current_profile:
            self.select_random_profile()
        
        profile = self.current_profile
        
        # Cabeçalhos base obrigatórios
        headers = {
            "User-Agent": profile.user_agent,
            "Accept": profile.accept,
            "Accept-Language": profile.accept_language,
            "Accept-Encoding": profile.accept_encoding,
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": profile.upgrade_insecure_requests,
            "DNT": profile.dnt,
        }
        
        # Cabeçalhos Sec-Fetch-* (importantes para anti-bot)
        if not is_ajax:
            headers.update({
                "Sec-Fetch-Site": profile.sec_fetch_site,
                "Sec-Fetch-Mode": profile.sec_fetch_mode,
                "Sec-Fetch-Dest": profile.sec_fetch_dest,
            })
            
            if profile.sec_fetch_user:
                headers["Sec-Fetch-User"] = profile.sec_fetch_user
        else:
            # Para requisições AJAX
            headers.update({
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "X-Requested-With": "XMLHttpRequest"
            })
        
        # Referer (simula navegação natural)
        if referer:
            headers["Referer"] = referer
            self.current_referer = referer
        elif self.current_referer:
            headers["Referer"] = self.current_referer
        
        # Cache-Control para parecer mais natural
        headers["Cache-Control"] = "max-age=0"
        
        # Sec-CH-UA headers (Chrome/Edge)
        if "Chrome" in profile.user_agent or "Edg" in profile.user_agent:
            headers.update({
                'Sec-CH-UA': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"' if "Windows" in profile.user_agent else '"macOS"'
            })
        
        logger.debug(f"Cabecalhos gerados para {url} ({len(headers)} cabecalhos)")
        return headers
    
    def update_referer(self, url: str):
        """Atualiza o referer para a próxima requisição."""
        self.current_referer = url
        logger.debug(f"Referer atualizado: {url}")
    
    def get_headers_for_fbref(self, url: str, referer: Optional[str] = None) -> Dict[str, str]:
        """
        Gera cabeçalhos específicos otimizados para FBRef.
        
        Args:
            url: URL do FBRef
            referer: Página anterior (para simular navegação)
            
        Returns:
            Dict com cabeçalhos otimizados para FBRef
        """
        headers = self.generate_headers(url, referer)
        
        # Otimizações específicas para FBRef
        if "fbref.com" in url:
            # Accept mais específico para páginas de estatísticas
            if any(keyword in url for keyword in ['/stats/', '/squads/', '/players/']):
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            
            # Priorizar inglês para FBRef (site em inglês)
            if "pt-BR" in headers["Accept-Language"]:
                headers["Accept-Language"] = "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7"
            
            # Sec-Fetch-Site baseado na navegação
            if referer and "fbref.com" in referer:
                headers["Sec-Fetch-Site"] = "same-origin"
            else:
                headers["Sec-Fetch-Site"] = "none"  # Navegação direta
        
        return headers
    
    def simulate_natural_browsing_headers(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Simula navegação natural gerando cabeçalhos sequenciais.
        
        Args:
            urls: Lista de URLs em sequência de navegação
            
        Returns:
            Lista de cabeçalhos para cada URL
        """
        headers_sequence = []
        previous_url = None
        
        for i, url in enumerate(urls):
            # Primeira requisição não tem referer
            referer = previous_url if i > 0 else None
            
            # Ocasionalmente muda o perfil do navegador (simula usuário diferente)
            if i > 0 and random.random() < 0.1:  # 10% chance
                self.select_random_profile()
                logger.debug("Mudanca de perfil de navegador para simular usuario diferente")
            
            headers = self.get_headers_for_fbref(url, referer)
            headers_sequence.append(headers)
            
            previous_url = url
        
        logger.info(f"Sequencia de navegacao simulada para {len(urls)} URLs")
        return headers_sequence
    
    def get_profile_stats(self) -> Dict:
        """Retorna estatísticas dos perfis disponíveis."""
        return {
            'total_profiles': len(self.browser_profiles),
            'current_profile': self.current_profile.name if self.current_profile else None,
            'current_referer': self.current_referer,
            'available_profiles': [p.name for p in self.browser_profiles]
        }
    
    def reset_session(self):
        """Reset da sessão (novo perfil, limpa referer)."""
        self.select_random_profile()
        self.current_referer = None
        logger.info("Sessao de cabecalhos resetada")

# Headers de exemplo para diferentes tipos de requisição
EXAMPLE_HEADERS = {
    "fbref_main_page": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
}
