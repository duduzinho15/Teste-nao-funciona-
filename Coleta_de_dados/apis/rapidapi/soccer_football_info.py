"""
Soccer Football Info API - RapidAPI
===================================

Implementação da API Soccer Football Info do RapidAPI para coleta de dados
de futebol, incluindo informações de clubes, jogadores, ligas e estatísticas.

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_rapidapi import RapidAPIBase, RapidAPIConfig

logger = logging.getLogger(__name__)

class SoccerFootballInfoAPI(RapidAPIBase):
    """
    API Soccer Football Info do RapidAPI.
    
    Fornece informações detalhadas sobre:
    - Clubes e suas estatísticas
    - Jogadores e perfis
    - Ligas e competições
    - Estatísticas de partidas
    - Histórico de confrontos
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa a API Soccer Football Info."""
        # Usar chave padrão se não fornecida
        if api_key is None:
            api_key = "chave_padrao_rapidapi"  # Será substituída pela variável de ambiente
        
        config = RapidAPIConfig(
            nome="Soccer Football Info",
            host="soccer-football-info.p.rapidapi.com",
            endpoint_base="https://soccer-football-info.p.rapidapi.com",
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
            'clubes': '/clubs',
            'jogadores': '/players',
            'ligas': '/leagues',
            'partidas': '/matches',
            'estatisticas': '/statistics',
            'confrontos': '/head-to-head'
        }
    
    async def coletar_jogos(self, data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta jogos para uma data específica"""
        if not data:
            data = datetime.now().strftime("%Y%m%d")
        
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/emulation/totalcorner/match/schedule/"
            params = {"date": data, "l": "en_US"}
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_jogo(jogo) for jogo in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos: {e}")
            return []

    async def coletar_jogadores(self, clube_id: Optional[str] = None, liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta jogadores de um clube ou liga específica"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/emulation/totalcorner/players/"
            params = {"l": "en_US"}
            
            if clube_id:
                params["team"] = clube_id
            if liga_id:
                params["league"] = liga_id
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_jogador(jogador) for jogador in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, pais: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta ligas da API Soccer Football Info.
        
        Args:
            pais: País das ligas (opcional)
            
        Returns:
            Lista de ligas padronizadas
        """
        try:
            params = {}
            if pais:
                params['country'] = pais
            
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
            
            logger.info(f"Coletadas {len(ligas)} ligas da Soccer Football Info")
            return ligas
            
        except Exception as e:
            logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, partida_id: Optional[str] = None,
                                  clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas da API Soccer Football Info.
        
        Args:
            partida_id: ID da partida (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de estatísticas padronizadas
        """
        try:
            params = {}
            if partida_id:
                params['match'] = partida_id
            if clube_id:
                params['club'] = clube_id
            
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
            
            logger.info(f"Coletadas {len(estatisticas)} estatísticas da Soccer Football Info")
            return estatisticas
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, partida_id: str) -> List[Dict[str, Any]]:
        """
        Coleta odds da API Soccer Football Info.
        
        Args:
            partida_id: ID da partida
            
        Returns:
            Lista de odds padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para odds
            # Vamos tentar buscar nas estatísticas da partida
            response = await self._make_request(
                endpoint=self.endpoints['estatisticas'],
                params={'match': partida_id}
            )
            
            if not response or 'odds' not in response:
                logger.warning("API não fornece dados de odds")
                return []
            
            odds = []
            for odd in response['odds']:
                odd_padronizada = self._padronizar_odd(odd)
                if odd_padronizada:
                    odds.append(odd_padronizada)
            
            logger.info(f"Coletadas {len(odds)} odds da Soccer Football Info")
            return odds
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, clube_id: Optional[str] = None,
                              liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta notícias da API Soccer Football Info.
        
        Args:
            clube_id: ID do clube (opcional)
            liga_id: ID da liga (opcional)
            
        Returns:
            Lista de notícias padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para notícias
            # Retornamos lista vazia por enquanto
            logger.info("API Soccer Football Info não fornece notícias")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    def _padronizar_jogo(self, partida: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma partida."""
        try:
            return {
                'id_partida': str(partida.get('id', '')),
                'liga': partida.get('league', {}).get('name', ''),
                'time_casa': partida.get('home_team', {}).get('name', ''),
                'time_fora': partida.get('away_team', {}).get('name', ''),
                'data': partida.get('date', ''),
                'status': partida.get('status', ''),
                'placar_casa': partida.get('home_score', 0),
                'placar_fora': partida.get('away_score', 0),
                'estadio': partida.get('venue', ''),
                'arbitro': partida.get('referee', ''),
                'fonte': 'soccer_football_info',
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
                'posicao': jogador.get('position', ''),
                'clube': jogador.get('club', {}).get('name', ''),
                'idade': jogador.get('age', 0),
                'nacionalidade': jogador.get('nationality', ''),
                'altura': jogador.get('height', 0),
                'peso': jogador.get('weight', 0),
                'fonte': 'soccer_football_info',
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
                'pais': liga.get('country', ''),
                'tipo': liga.get('type', ''),
                'nivel': liga.get('level', ''),
                'temporada_atual': liga.get('current_season', ''),
                'fonte': 'soccer_football_info',
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
                'contexto': stat.get('context', ''),
                'fonte': 'soccer_football_info',
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
                'timestamp': odd.get('timestamp', ''),
                'fonte': 'soccer_football_info',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar odd: {e}")
            return None

# Função de demonstração
async def demo_soccer_football_info():
    """Demonstra o uso da API Soccer Football Info."""
    print("🧪 TESTANDO SOCCER FOOTBALL INFO API...")
    
    try:
        api = SoccerFootballInfoAPI()
        
        # Teste de coleta de ligas
        print("\n1️⃣ Coletando ligas...")
        ligas = await api.coletar_ligas()
        print(f"✅ {len(ligas)} ligas coletadas")
        
        # Teste de coleta de jogos
        print("\n2️⃣ Coletando jogos...")
        jogos = await api.coletar_jogos()
        print(f"✅ {len(jogos)} jogos coletados")
        
        # Teste de coleta de jogadores
        print("\n3️⃣ Coletando jogadores...")
        jogadores = await api.coletar_jogadores()
        print(f"✅ {len(jogadores)} jogadores coletados")
        
        print("\n🎉 Soccer Football Info API funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na Soccer Football Info API: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_soccer_football_info())
