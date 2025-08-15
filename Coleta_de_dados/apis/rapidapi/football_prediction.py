#!/usr/bin/env python3
"""
Football Prediction API - RapidAPI
Coleta previsões e probabilidades de futebol
"""

import asyncio
from typing import List, Dict, Any, Optional
from .base_rapidapi import RapidAPIBase, RapidAPIConfig
from datetime import datetime


class FootballPredictionAPI(RapidAPIBase):
    """API para previsões de futebol via RapidAPI"""
    
    def __init__(self, api_key: Optional[str] = None):
        config = RapidAPIConfig(
            nome="Football Prediction API",
            host="football-prediction.p.rapidapi.com",
            endpoint_base="/api/v2",
            chaves=[api_key] if api_key else [],
            limite_requisicoes_dia=1000,
            limite_requisicoes_minuto=60,
            timeout=30,
            retry_attempts=3,
            retry_delay=1
        )
        super().__init__(config)
    
    async def coletar_jogos(self, data: Optional[str] = None, federacao: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta previsões de jogos para uma data específica"""
        if not data:
            data = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/api/v2/predictions"
            params = {"iso_date": data, "market": "classic"}
            
            if federacao:
                params["federation"] = federacao
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_jogo(jogo) for jogo in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, clube_id: Optional[str] = None, liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta estatísticas de jogadores para previsões"""
        try:
            # Endpoint para estatísticas de jogadores
            endpoint = "/players/stats"
            params = {}
            if clube_id:
                params["team_id"] = clube_id
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
        """Coleta ligas disponíveis para previsões"""
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
        """Coleta estatísticas para previsões"""
        try:
            endpoint = "/stats"
            params = {}
            if jogador_id:
                params["player_id"] = jogador_id
            if clube_id:
                params["team_id"] = clube_id
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_estatistica(stat) for stat in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, jogo_id: str) -> List[Dict[str, Any]]:
        """Coleta probabilidades para um jogo específico"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/api/v2/probabilities"
            params = {"match": jogo_id}
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_odds(odds) for odds in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta notícias relacionadas a previsões"""
        try:
            endpoint = "/news"
            params = {
                "category": kwargs.get("category", "predictions"),
                "limit": kwargs.get("limit", 10)
            }
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_noticia(news) for news in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    # Métodos de padronização
    def _padronizar_jogo(self, pred: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de previsão de jogo"""
        return {
            "id": pred.get("id", ""),
            "data": pred.get("date", ""),
            "time_casa": pred.get("home_team", ""),
            "time_visitante": pred.get("away_team", ""),
            "liga": pred.get("league", ""),
            "previsao": pred.get("prediction", ""),
            "probabilidade": pred.get("probability", 0.0),
            "confianca": pred.get("confidence", 0.0),
            "fonte": "Football Prediction API"
        }
    
    def _padronizar_jogador(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de jogador"""
        return {
            "id": player.get("id", ""),
            "nome": player.get("name", ""),
            "posicao": player.get("position", ""),
            "clube": player.get("team", ""),
            "liga": player.get("league", ""),
            "estatisticas": player.get("stats", {}),
            "fonte": "Football Prediction API"
        }
    
    def _padronizar_liga(self, league: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de liga"""
        return {
            "id": league.get("id", ""),
            "nome": league.get("name", ""),
            "pais": league.get("country", ""),
            "nivel": league.get("level", ""),
            "temporada": league.get("season", ""),
            "fonte": "Football Prediction API"
        }
    
    def _padronizar_estatistica(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de estatística"""
        return {
            "id": stat.get("id", ""),
            "tipo": stat.get("type", ""),
            "valor": stat.get("value", 0),
            "unidade": stat.get("unit", ""),
            "contexto": stat.get("context", ""),
            "fonte": "Football Prediction API"
        }
    
    def _padronizar_odds(self, odd: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de odds"""
        return {
            "id": odd.get("id", ""),
            "tipo": odd.get("type", ""),
            "valor": odd.get("value", 0.0),
            "probabilidade": odd.get("probability", 0.0),
            "confianca": odd.get("confidence", 0.0),
            "fonte": "Football Prediction API"
        }
    
    def _padronizar_noticia(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de notícia"""
        return {
            "id": news.get("id", ""),
            "titulo": news.get("title", ""),
            "resumo": news.get("summary", ""),
            "conteudo": news.get("content", ""),
            "data": news.get("date", ""),
            "autor": news.get("author", ""),
            "fonte": "Football Prediction API"
        }


async def demo_football_prediction():
    """Demonstração da API Football Prediction"""
    print("🔄 Testando Football Prediction API...")
    
    api = FootballPredictionAPI()
    
    # Teste de previsões
    previsoes = await api.coletar_jogos(date="2025-08-14")
    print(f"  ✅ Previsões coletadas: {len(previsoes)}")
    
    # Teste de odds
    odds = await api.coletar_odds(match_id="test_match_id")
    print(f"  ✅ Odds coletadas: {len(odds)}")
    
    return len(previsoes) > 0 or len(odds) > 0


if __name__ == "__main__":
    asyncio.run(demo_football_prediction())
