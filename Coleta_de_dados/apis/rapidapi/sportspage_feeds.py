"""
Sportspage Feeds API - RapidAPI
===============================

Implementação da API Sportspage Feeds do RapidAPI para coleta de feeds
esportivos em tempo real, incluindo notícias, resultados e estatísticas.

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_rapidapi import RapidAPIBase, RapidAPIConfig

logger = logging.getLogger(__name__)

class SportspageFeedsAPI(RapidAPIBase):
    """
    API Sportspage Feeds do RapidAPI.
    
    Fornece feeds esportivos em tempo real:
    - Notícias esportivas
    - Resultados ao vivo
    - Estatísticas atualizadas
    - Feeds de diferentes esportes
    - Dados históricos
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa a API Sportspage Feeds."""
        # Usar chave padrão se não fornecida
        if api_key is None:
            api_key = "chave_padrao_rapidapi"  # Será substituída pela variável de ambiente
        
        config = RapidAPIConfig(
            nome="Sportspage Feeds",
            host="sportspage-feeds.p.rapidapi.com",
            endpoint_base="https://sportspage-feeds.p.rapidapi.com",
            chaves=[api_key],
            limite_requisicoes_dia=100,
            limite_requisicoes_minuto=10,
            timeout=30,
            retry_attempts=3,
            retry_delay=2
        )
        super().__init__(config)
        
        # Endpoints específicos da API
        self.endpoints = {
            'feeds': '/feeds',
            'noticias': '/news',
            'resultados': '/results',
            'estatisticas': '/stats',
            'esportes': '/sports',
            'ligas': '/leagues'
        }
    
    async def coletar_jogos(self, esporte: str = "football") -> List[Dict[str, Any]]:
        """Coleta resultados de jogos para um esporte específico"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/results"
            params = {"sport": esporte}
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_jogo(jogo) for jogo in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, esporte: Optional[str] = None,
                               clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogadores dos feeds do Sportspage.
        
        Args:
            esporte: Nome do esporte (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de jogadores padronizados
        """
        try:
            params = {}
            if esporte:
                params['sport'] = esporte
            if clube_id:
                params['team'] = clube_id
            
            # Buscar nas estatísticas que podem conter dados de jogadores
            response = await self._make_request(
                endpoint=self.endpoints['estatisticas'],
                params=params
            )
            
            if not response or 'players' not in response:
                logger.warning("Resposta da API não contém dados de jogadores")
                return []
            
            jogadores = []
            for jogador in response['players']:
                jogador_padronizado = self._padronizar_jogador(jogador)
                if jogador_padronizado:
                    jogadores.append(jogador_padronizado)
            
            logger.info(f"Coletados {len(jogadores)} jogadores do Sportspage Feeds")
            return jogadores
            
        except Exception as e:
            logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, esporte: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta ligas dos feeds do Sportspage.
        
        Args:
            esporte: Nome do esporte (opcional)
            
        Returns:
            Lista de ligas padronizadas
        """
        try:
            params = {}
            if esporte:
                params['sport'] = esporte
            
            response = await self._make_request(
                endpoint=self.endpoints['ligas'],
                params=params
            )
            
            if not response or 'leagues' not in response:
                logger.warning("Resposta da API não contém dados de ligas")
                return []
            
            ligas = []
            for liga in response['leagues']:
                liga_padronizada = self._padronizar_liga(liga)
                if liga_padronizada:
                    ligas.append(liga_padronizada)
            
            logger.info(f"Coletadas {len(ligas)} ligas do Sportspage Feeds")
            return ligas
            
        except Exception as e:
            logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, esporte: Optional[str] = None,
                                  tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas dos feeds do Sportspage.
        
        Args:
            esporte: Nome do esporte (opcional)
            tipo: Tipo de estatística (opcional)
            
        Returns:
            Lista de estatísticas padronizadas
        """
        try:
            params = {}
            if esporte:
                params['sport'] = esporte
            if tipo:
                params['type'] = tipo
            
            response = await self._make_request(
                endpoint=self.endpoints['estatisticas'],
                params=params
            )
            
            if not response or 'statistics' not in response:
                logger.warning("Resposta da API não contém dados de estatísticas")
                return []
            
            estatisticas = []
            for stat in response['statistics']:
                stat_padronizada = self._padronizar_estatistica(stat)
                if stat_padronizada:
                    estatisticas.append(stat_padronizada)
            
            logger.info(f"Coletadas {len(estatisticas)} estatísticas do Sportspage Feeds")
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, esporte: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta odds dos feeds do Sportspage.
        
        Args:
            esporte: Nome do esporte (opcional)
            
        Returns:
            Lista de odds padronizadas
        """
        try:
            # Buscar nas estatísticas que podem conter odds
            params = {}
            if esporte:
                params['sport'] = esporte
            params['type'] = 'odds'
            
            response = await self._make_request(
                endpoint=self.endpoints['estatisticas'],
                params=params
            )
            
            if not response or 'odds' not in response:
                logger.warning("API não fornece dados de odds")
                return []
            
            odds = []
            for odd in response['odds']:
                odd_padronizada = self._padronizar_odd(odd)
                if odd_padronizada:
                    odds.append(odd_padronizada)
            
            logger.info(f"Coletadas {len(odds)} odds do Sportspage Feeds")
            return odds
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, esporte: str = "football") -> List[Dict[str, Any]]:
        """Coleta notícias esportivas para um esporte específico"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/news"
            params = {"sport": esporte}
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_noticia(noticia) for noticia in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    def _padronizar_jogo(self, jogo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de um jogo."""
        try:
            return {
                'id_partida': str(jogo.get('id', '')),
                'esporte': jogo.get('sport', ''),
                'liga': jogo.get('league', ''),
                'time_casa': jogo.get('home_team', ''),
                'time_fora': jogo.get('away_team', ''),
                'data': jogo.get('date', ''),
                'hora': jogo.get('time', ''),
                'status': jogo.get('status', ''),
                'placar_casa': jogo.get('home_score', 0),
                'placar_fora': jogo.get('away_score', 0),
                'periodo': jogo.get('period', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar jogo: {e}")
            return None
    
    def _padronizar_jogador(self, jogador: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de um jogador."""
        try:
            return {
                'id_jogador': str(jogador.get('id', '')),
                'nome': jogador.get('name', ''),
                'esporte': jogador.get('sport', ''),
                'clube': jogador.get('team', ''),
                'posicao': jogador.get('position', ''),
                'numero': jogador.get('number', 0),
                'nacionalidade': jogador.get('nationality', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar jogador: {e}")
            return None
    
    def _padronizar_liga(self, liga: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma liga."""
        try:
            return {
                'id_liga': str(liga.get('id', '')),
                'nome': liga.get('name', ''),
                'esporte': liga.get('sport', ''),
                'pais': liga.get('country', ''),
                'temporada': liga.get('season', ''),
                'status': liga.get('status', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar liga: {e}")
            return None
    
    def _padronizar_estatistica(self, stat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma estatística."""
        try:
            return {
                'id_estatistica': str(stat.get('id', '')),
                'tipo': stat.get('type', ''),
                'valor': stat.get('value', 0),
                'unidade': stat.get('unit', ''),
                'esporte': stat.get('sport', ''),
                'contexto': stat.get('context', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar estatística: {e}")
            return None
    
    def _padronizar_odd(self, odd: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma odd."""
        try:
            return {
                'id_odd': str(odd.get('id', '')),
                'tipo': odd.get('type', ''),
                'valor': odd.get('value', 0.0),
                'casa_aposta': odd.get('bookmaker', ''),
                'esporte': odd.get('sport', ''),
                'timestamp': odd.get('timestamp', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar odd: {e}")
            return None
    
    def _padronizar_noticia(self, noticia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma notícia."""
        try:
            return {
                'id_noticia': str(noticia.get('id', '')),
                'titulo': noticia.get('title', ''),
                'resumo': noticia.get('summary', ''),
                'conteudo': noticia.get('content', ''),
                'autor': noticia.get('author', ''),
                'data_publicacao': noticia.get('published_date', ''),
                'categoria': noticia.get('category', ''),
                'esporte': noticia.get('sport', ''),
                'url': noticia.get('url', ''),
                'fonte': 'sportspage_feeds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar notícia: {e}")
            return None

# Função de demonstração
async def demo_sportspage_feeds():
    """Demonstra o uso da API Sportspage Feeds."""
    print("🧪 TESTANDO SPORTPAGE FEEDS API...")
    
    try:
        api = SportspageFeedsAPI()
        
        # Teste de coleta de feeds
        print("\n1️⃣ Coletando feeds...")
        feeds = await api.coletar_noticias()
        print(f"✅ {len(feeds)} feeds coletados")
        
        # Teste de coleta de notícias
        print("\n2️⃣ Coletando notícias...")
        noticias = await api.coletar_noticias(esporte="football")
        print(f"✅ {len(noticias)} notícias coletadas")
        
        # Teste de coleta de estatísticas
        print("\n3️⃣ Coletando estatísticas...")
        estatisticas = await api.coletar_estatisticas(esporte="football")
        print(f"✅ {len(estatisticas)} estatísticas coletadas")
        
        print("\n🎉 Sportspage Feeds API funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na Sportspage Feeds API: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_sportspage_feeds())
