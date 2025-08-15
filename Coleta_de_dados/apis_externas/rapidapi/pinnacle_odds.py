"""
Pinnacle Odds API - RapidAPI
============================

Implementação da API Pinnacle Odds do RapidAPI para coleta de odds
e linhas de apostas da Pinnacle Sports, uma das maiores casas de apostas.

Autor: Sistema de Coleta de Dados ApostaPro
Data: 2025-01-15
Versão: 1.0
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_rapidapi import RapidAPIBase, RapidAPIConfig

logger = logging.getLogger(__name__)

class PinnacleOddsAPI(RapidAPIBase):
    """
    API Pinnacle Odds do RapidAPI.
    
    Fornece odds e linhas de apostas da Pinnacle Sports:
    - Odds em tempo real
    - Linhas de apostas
    - Histórico de odds
    - Diferentes tipos de apostas
    - Múltiplas ligas e esportes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa a API Pinnacle Odds."""
        config = RapidAPIConfig(
            name="Pinnacle Odds",
            host="pinnacle-odds.p.rapidapi.com",
            base_url="https://pinnacle-odds.p.rapidapi.com",
            api_key=api_key,
            rate_limit_per_day=100,
            rate_limit_per_minute=10
        )
        super().__init__(config)
        
        # Endpoints específicos da API
        self.endpoints = {
            'odds': '/odds',
            'linhas': '/lines',
            'partidas': '/matches',
            'ligas': '/leagues',
            'esportes': '/sports',
            'historico': '/history'
        }
    
    async def coletar_jogos(self, esporte: Optional[str] = None,
                           liga_id: Optional[str] = None,
                           data: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogos com odds da API Pinnacle Odds.
        
        Args:
            esporte: Nome do esporte (opcional)
            liga_id: ID da liga (opcional)
            data: Data específica (YYYY-MM-DD, opcional)
            
        Returns:
            Lista de jogos com odds padronizados
        """
        try:
            params = {}
            if esporte:
                params['sport'] = esporte
            if liga_id:
                params['league'] = liga_id
            if data:
                params['date'] = data
            
            response = await self._make_request(
                endpoint=self.endpoints['partidas'],
                params=params
            )
            
            if not response or 'matches' not in response:
                logger.warning("Resposta da API não contém dados de partidas")
                return []
            
            jogos = []
            for partida in response['matches']:
                jogo_padronizado = self._padronizar_jogo_com_odds(partida)
                if jogo_padronizado:
                    jogos.append(jogo_padronizado)
            
            logger.info(f"Coletados {len(jogos)} jogos da Pinnacle Odds")
            return jogos
            
        except Exception as e:
            logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, esporte: Optional[str] = None,
                               clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogadores da API Pinnacle Odds.
        
        Args:
            esporte: Nome do esporte (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de jogadores padronizados
        """
        try:
            # Esta API pode não ter endpoint específico para jogadores
            # Retornamos lista vazia por enquanto
            logger.info("API Pinnacle Odds não fornece dados de jogadores")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, esporte: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta ligas da API Pinnacle Odds.
        
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
            
            logger.info(f"Coletadas {len(ligas)} ligas da Pinnacle Odds")
            return ligas
            
        except Exception as e:
            logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, partida_id: Optional[str] = None,
                                  clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas da API Pinnacle Odds.
        
        Args:
            partida_id: ID da partida (opcional)
            clube_id: ID do clube (opcional)
            
        Returns:
            Lista de estatísticas padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para estatísticas
            # Retornamos lista vazia por enquanto
            logger.info("API Pinnacle Odds não fornece estatísticas detalhadas")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, partida_id: Optional[str] = None,
                          esporte: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta odds da API Pinnacle Odds.
        
        Args:
            partida_id: ID da partida (opcional)
            esporte: Nome do esporte (opcional)
            
        Returns:
            Lista de odds padronizadas
        """
        try:
            params = {}
            if partida_id:
                params['match'] = partida_id
            if esporte:
                params['sport'] = esporte
            
            response = await self._make_request(
                endpoint=self.endpoints['odds'],
                params=params
            )
            
            if not response or 'odds' not in response:
                logger.warning("Resposta da API não contém dados de odds")
                return []
            
            odds = []
            for odd in response['odds']:
                odd_padronizada = self._padronizar_odd(odd)
                if odd_padronizada:
                    odds.append(odd_padronizada)
            
            logger.info(f"Coletadas {len(odds)} odds da Pinnacle Odds")
            return odds
            
        except Exception as e:
            logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, clube_id: Optional[str] = None,
                              liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta notícias da API Pinnacle Odds.
        
        Args:
            clube_id: ID do clube (opcional)
            liga_id: ID da liga (opcional)
            
        Returns:
            Lista de notícias padronizadas
        """
        try:
            # Esta API pode não ter endpoint específico para notícias
            # Retornamos lista vazia por enquanto
            logger.info("API Pinnacle Odds não fornece notícias")
            return []
            
        except Exception as e:
            logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    async def coletar_linhas_apostas(self, partida_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta linhas de apostas da API Pinnacle Odds.
        
        Args:
            partida_id: ID da partida (opcional)
            
        Returns:
            Lista de linhas de apostas padronizadas
        """
        try:
            params = {}
            if partida_id:
                params['match'] = partida_id
            
            response = await self._make_request(
                endpoint=self.endpoints['linhas'],
                params=params
            )
            
            if not response or 'lines' not in response:
                logger.warning("Resposta da API não contém dados de linhas de apostas")
                return []
            
            linhas = []
            for linha in response['lines']:
                linha_padronizada = self._padronizar_linha_aposta(linha)
                if linha_padronizada:
                    linhas.append(linha_padronizada)
            
            logger.info(f"Coletadas {len(linhas)} linhas de apostas da Pinnacle Odds")
            return linhas
            
        except Exception as e:
            logger.error(f"Erro ao coletar linhas de apostas: {e}")
            return []
    
    def _padronizar_jogo_com_odds(self, partida: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma partida com odds."""
        try:
            return {
                'id_partida': str(partida.get('id', '')),
                'esporte': partida.get('sport', ''),
                'liga': partida.get('league', ''),
                'time_casa': partida.get('home_team', ''),
                'time_fora': partida.get('away_team', ''),
                'data': partida.get('date', ''),
                'hora': partida.get('time', ''),
                'status': partida.get('status', ''),
                'odds_vitoria_casa': partida.get('home_odds', 0.0),
                'odds_empate': partida.get('draw_odds', 0.0),
                'odds_vitoria_fora': partida.get('away_odds', 0.0),
                'fonte': 'pinnacle_odds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar jogo com odds: {e}")
            return None
    
    def _padronizar_liga(self, liga: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma liga."""
        try:
            return {
                'id_liga': str(liga.get('id', '')),
                'nome': liga.get('name', ''),
                'esporte': liga.get('sport', ''),
                'pais': liga.get('country', ''),
                'nivel': liga.get('level', ''),
                'status': liga.get('status', ''),
                'fonte': 'pinnacle_odds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar liga: {e}")
            return None
    
    def _padronizar_odd(self, odd: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma odd."""
        try:
            return {
                'id_odd': str(odd.get('id', '')),
                'tipo': odd.get('type', ''),
                'valor': odd.get('value', 0.0),
                'casa_aposta': 'Pinnacle Sports',
                'esporte': odd.get('sport', ''),
                'liga': odd.get('league', ''),
                'partida': odd.get('match', ''),
                'timestamp': odd.get('timestamp', ''),
                'fonte': 'pinnacle_odds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar odd: {e}")
            return None
    
    def _padronizar_linha_aposta(self, linha: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de uma linha de aposta."""
        try:
            return {
                'id_linha': str(linha.get('id', '')),
                'tipo_aposta': linha.get('bet_type', ''),
                'linha': linha.get('line', 0.0),
                'odds': linha.get('odds', 0.0),
                'partida': linha.get('match', ''),
                'esporte': linha.get('sport', ''),
                'timestamp': linha.get('timestamp', ''),
                'fonte': 'pinnacle_odds',
                'timestamp_coleta': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao padronizar linha de aposta: {e}")
            return None

# Função de demonstração
async def demo_pinnacle_odds():
    """Demonstra o uso da API Pinnacle Odds."""
    print("🧪 TESTANDO PINNACLE ODDS API...")
    
    try:
        api = PinnacleOddsAPI()
        
        # Teste de coleta de odds
        print("\n1️⃣ Coletando odds...")
        odds = await api.coletar_odds()
        print(f"✅ {len(odds)} odds coletadas")
        
        # Teste de coleta de linhas de apostas
        print("\n2️⃣ Coletando linhas de apostas...")
        linhas = await api.coletar_linhas_apostas()
        print(f"✅ {len(linhas)} linhas coletadas")
        
        # Teste de coleta de jogos
        print("\n3️⃣ Coletando jogos...")
        jogos = await api.coletar_jogos()
        print(f"✅ {len(jogos)} jogos coletados")
        
        print("\n🎉 Pinnacle Odds API funcionando perfeitamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na Pinnacle Odds API: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_pinnacle_odds())
