#!/usr/bin/env python3
"""
Player Market Data API - RapidAPI
Coleta dados de mercado de jogadores e transferências
"""

import asyncio
from typing import List, Dict, Any, Optional
from .base_rapidapi import RapidAPIBase, RapidAPIConfig


class PlayerMarketDataAPI(RapidAPIBase):
    """API para dados de mercado de jogadores via RapidAPI"""
    
    def __init__(self, api_key: Optional[str] = None):
        config = RapidAPIConfig(
            nome="Player Market Data API",
            host="transfermarkt.p.rapidapi.com",
            endpoint_base="/",
            chaves=[api_key] if api_key else [],
            limite_requisicoes_dia=1000,
            limite_requisicoes_minuto=60,
            timeout=30,
            retry_attempts=3,
            retry_delay=1
        )
        super().__init__(config)
    
    async def coletar_jogos(self, **kwargs) -> List[Dict[str, Any]]:
        """Esta API não fornece dados de jogos"""
        return []
    
    async def coletar_jogadores(self, clube_id: Optional[str] = None, liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta dados de jogadores com valores de mercado"""
        try:
            endpoint = "/players"
            params = {}
            if clube_id:
                params["club_id"] = clube_id
            if liga_id:
                params["league_id"] = liga_id
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_jogador(player) for player in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, pais: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta ligas disponíveis"""
        try:
            endpoint = "/leagues"
            params = {}
            if pais:
                params["country"] = pais
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_liga(league) for league in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, jogador_id: Optional[str] = None, clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta estatísticas de jogadores"""
        try:
            endpoint = "/player/stats"
            params = {}
            if jogador_id:
                params["player_id"] = jogador_id
            if clube_id:
                params["club_id"] = clube_id
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_estatistica(stat) for stat in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, **kwargs) -> List[Dict[str, Any]]:
        """Esta API não fornece dados de odds"""
        return []
    
    async def coletar_noticias(self, **kwargs) -> List[Dict[str, Any]]:
        """Esta API não fornece notícias"""
        return []
    
    async def coletar_valores_mercado(self, jogador_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta valores de mercado de jogadores"""
        try:
            endpoint = "/player/market-value"
            params = {}
            if jogador_id:
                params["player_id"] = jogador_id
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_valor_mercado(value) for value in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar valores de mercado: {e}")
            return []
    
    async def coletar_transferencias(self, clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta dados de transferências"""
        try:
            endpoint = "/transfers"
            params = {}
            if clube_id:
                params["club_id"] = clube_id
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_transferencia(transfer) for transfer in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar transferências: {e}")
            return []
    
    # Métodos de padronização
    def _padronizar_jogador(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de jogador"""
        return {
            "id": player.get("id", ""),
            "nome": player.get("name", ""),
            "posicao": player.get("position", ""),
            "clube": player.get("club", ""),
            "liga": player.get("league", ""),
            "idade": player.get("age", 0),
            "nacionalidade": player.get("nationality", ""),
            "valor_mercado": player.get("market_value", ""),
            "fonte": "Player Market Data API"
        }
    
    def _padronizar_liga(self, league: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de liga"""
        return {
            "id": league.get("id", ""),
            "nome": league.get("name", ""),
            "pais": league.get("country", ""),
            "nivel": league.get("level", ""),
            "temporada": league.get("season", ""),
            "fonte": "Player Market Data API"
        }
    
    def _padronizar_estatistica(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de estatística"""
        return {
            "id": stat.get("id", ""),
            "tipo": stat.get("type", ""),
            "valor": stat.get("value", 0),
            "unidade": stat.get("unit", ""),
            "contexto": stat.get("context", ""),
            "fonte": "Player Market Data API"
        }
    
    def _padronizar_valor_mercado(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de valor de mercado"""
        return {
            "id": value.get("id", ""),
            "jogador_id": value.get("player_id", ""),
            "valor": value.get("value", ""),
            "moeda": value.get("currency", ""),
            "data_atualizacao": value.get("updated_at", ""),
            "tendencia": value.get("trend", ""),
            "fonte": "Player Market Data API"
        }
    
    def _padronizar_transferencia(self, transfer: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de transferência"""
        return {
            "id": transfer.get("id", ""),
            "jogador": transfer.get("player", ""),
            "clube_origem": transfer.get("from_club", ""),
            "clube_destino": transfer.get("to_club", ""),
            "valor": transfer.get("fee", ""),
            "data": transfer.get("date", ""),
            "tipo": transfer.get("type", ""),
            "fonte": "Player Market Data API"
        }


async def demo_player_market_data():
    """Demonstração da API Player Market Data"""
    print("🔄 Testando Player Market Data API...")
    
    api = PlayerMarketDataAPI()
    
    # Teste de jogadores
    jogadores = await api.coletar_jogadores()
    print(f"  ✅ Jogadores coletados: {len(jogadores)}")
    
    # Teste de valores de mercado
    valores = await api.coletar_valores_mercado()
    print(f"  ✅ Valores de mercado coletados: {len(valores)}")
    
    return len(jogadores) > 0 or len(valores) > 0


if __name__ == "__main__":
    asyncio.run(demo_player_market_data())
