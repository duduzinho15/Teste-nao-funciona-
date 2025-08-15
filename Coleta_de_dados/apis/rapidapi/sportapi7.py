#!/usr/bin/env python3
"""
SportAPI7 API - RapidAPI
Coleta dados esportivos avançados via RapidAPI
"""

import asyncio
from typing import List, Dict, Any, Optional
from .base_rapidapi import RapidAPIBase, RapidAPIConfig


class SportAPI7(RapidAPIBase):
    """API para dados esportivos avançados via RapidAPI"""
    
    def __init__(self, api_key: Optional[str] = None):
        config = RapidAPIConfig(
            nome="SportAPI7 API",
            host="sportapi7.p.rapidapi.com",
            endpoint_base="/api/v1",
            chaves=[api_key] if api_key else [],
            limite_requisicoes_dia=1000,
            limite_requisicoes_minuto=60,
            timeout=30,
            retry_attempts=3,
            retry_delay=1
        )
        super().__init__(config)
    
    async def coletar_jogos(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados de jogos"""
        try:
            endpoint = "/matches"
            params = {
                "date": kwargs.get("date", "2025-08-14"),
                "sport": kwargs.get("sport", "football"),
                "league": kwargs.get("league", "")
            }
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_jogo(match) for match in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, clube_id: Optional[str] = None, liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta jogadores de um clube ou liga específica"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/api/v1/players"
            params = {}
            
            if clube_id:
                params["team"] = clube_id
            if liga_id:
                params["tournament"] = liga_id
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                return [self._padronizar_jogador(jogador) for jogador in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self, pais: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta ligas disponíveis"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/api/v1/unique-tournaments"
            
            response = await self._make_request(url)
            
            if response and "data" in response:
                ligas = [self._padronizar_liga(liga) for liga in response["data"]]
                if pais:
                    ligas = [liga for liga in ligas if liga.get("pais", "").lower() == pais.lower()]
                return ligas
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, jogador_id: Optional[str] = None, clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta estatísticas de jogadores ou clubes"""
        try:
            if jogador_id:
                endpoint = f"/player/{jogador_id}/stats"
                params = {}
            elif clube_id:
                endpoint = f"/team/{clube_id}/stats"
                params = {}
            else:
                return []
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                if jogador_id:
                    return [self._padronizar_estatistica_jogador(stat) for stat in response["data"]]
                else:
                    return [self._padronizar_estatistica_clube(stat) for stat in response["data"]]
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
    
    async def coletar_ratings_jogador(self, jogador_id: str, liga_id: str, temporada_id: str) -> List[Dict[str, Any]]:
        """Coleta ratings de jogadores"""
        try:
            endpoint = f"/player/{jogador_id}/rating"
            params = {
                "league_id": liga_id,
                "season_id": temporada_id
            }
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_rating_jogador(rating) for rating in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar ratings: {e}")
            return []
    
    async def coletar_dados_time(self, time_id: str) -> Optional[Dict[str, Any]]:
        """Coleta dados completos de um time"""
        try:
            endpoint = f"/team/{time_id}"
            params = {}
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return self._padronizar_time(response["data"])
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do time: {e}")
            return None
    
    async def coletar_estatisticas_avancadas(self, jogador_id: str, liga_id: str, temporada_id: str) -> List[Dict[str, Any]]:
        """Coleta estatísticas avançadas de jogadores"""
        try:
            endpoint = f"/player/{jogador_id}/advanced-stats"
            params = {
                "league_id": liga_id,
                "season_id": temporada_id
            }
            
            response = await self._make_request(endpoint, params)
            if response and "data" in response:
                return [self._padronizar_estatistica_avancada(stat) for stat in response["data"]]
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas avançadas: {e}")
            return []
    
    # Métodos de padronização
    def _padronizar_jogo(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de jogo"""
        return {
            "id": match.get("id", ""),
            "data": match.get("date", ""),
            "time_casa": match.get("home_team", ""),
            "time_visitante": match.get("away_team", ""),
            "liga": match.get("league", ""),
            "status": match.get("status", ""),
            "gols_casa": match.get("home_score", 0),
            "gols_visitante": match.get("away_score", 0),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_jogador(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de jogador"""
        return {
            "id": player.get("id", ""),
            "nome": player.get("name", ""),
            "posicao": player.get("position", ""),
            "clube": player.get("team", ""),
            "liga": player.get("league", ""),
            "idade": player.get("age", 0),
            "nacionalidade": player.get("nationality", ""),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_liga(self, league: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de liga"""
        return {
            "id": league.get("id", ""),
            "nome": league.get("name", ""),
            "pais": league.get("country", ""),
            "nivel": league.get("level", ""),
            "temporada": league.get("season", ""),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_estatistica_jogador(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza estatísticas de jogador"""
        return {
            "id": stat.get("id", ""),
            "jogador_id": stat.get("player_id", ""),
            "temporada": stat.get("season", ""),
            "jogos": stat.get("games", 0),
            "gols": stat.get("goals", 0),
            "assistencias": stat.get("assists", 0),
            "minutos": stat.get("minutes", 0),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_estatistica_clube(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza estatísticas de clube"""
        return {
            "id": stat.get("id", ""),
            "clube_id": stat.get("team_id", ""),
            "temporada": stat.get("season", ""),
            "jogos": stat.get("games", 0),
            "vitorias": stat.get("wins", 0),
            "empates": stat.get("draws", 0),
            "derrotas": stat.get("losses", 0),
            "pontos": stat.get("points", 0),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_rating_jogador(self, rating: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza rating de jogador"""
        return {
            "id": rating.get("id", ""),
            "jogador_id": rating.get("player_id", ""),
            "rating": rating.get("rating", 0.0),
            "posicao": rating.get("position", ""),
            "liga": rating.get("league", ""),
            "temporada": rating.get("season", ""),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_time(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza dados de time"""
        return {
            "id": team.get("id", ""),
            "nome": team.get("name", ""),
            "pais": team.get("country", ""),
            "liga": team.get("league", ""),
            "estadio": team.get("stadium", ""),
            "fundacao": team.get("founded", ""),
            "fonte": "SportAPI7 API"
        }
    
    def _padronizar_estatistica_avancada(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Padroniza estatísticas avançadas"""
        return {
            "id": stat.get("id", ""),
            "jogador_id": stat.get("player_id", ""),
            "tipo": stat.get("type", ""),
            "valor": stat.get("value", 0),
            "unidade": stat.get("unit", ""),
            "contexto": stat.get("context", ""),
            "fonte": "SportAPI7 API"
        }


async def demo_sportapi7():
    """Demonstração da API SportAPI7"""
    print("🔄 Testando SportAPI7 API...")
    
    api = SportAPI7API()
    
    # Teste de ligas
    ligas = await api.coletar_ligas()
    print(f"  ✅ Ligas coletadas: {len(ligas)}")
    
    # Teste de jogadores
    jogadores = await api.coletar_jogadores()
    print(f"  ✅ Jogadores coletados: {len(jogadores)}")
    
    return len(ligas) > 0 or len(jogadores) > 0


if __name__ == "__main__":
    asyncio.run(demo_sportapi7())
