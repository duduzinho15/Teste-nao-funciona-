#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API TODAY FOOTBALL PREDICTION - RAPIDAPI
========================================

Implementação da API Today Football Prediction do RapidAPI.
Fornece previsões, odds e análises para jogos de futebol.

Endpoint: https://today-football-prediction.p.rapidapi.com
Documentação: https://rapidapi.com/letscrape-6bRBa3QguO5/api/today-football-prediction

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .base_rapidapi import RapidAPIBase, RapidAPIConfig

logger = logging.getLogger(__name__)

class TodayFootballPredictionAPI(RapidAPIBase):
    """
    API para previsões de futebol do dia.
    
    Funcionalidades:
    - Previsões de jogos
    - Odds e probabilidades
    - Estatísticas de confrontos
    - Análise de forma das equipes
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa a API Today Football Prediction.
        
        Args:
            api_key: Chave de API do RapidAPI (opcional)
        """
        # Usar chave padrão se não fornecida
        if api_key is None:
            api_key = "chave_padrao_rapidapi"  # Será substituída pela variável de ambiente
        
        config = RapidAPIConfig(
            nome="Today Football Prediction",
            host="today-football-prediction.p.rapidapi.com",
            endpoint_base="https://today-football-prediction.p.rapidapi.com",
            chaves=[api_key],
            limite_requisicoes_dia=100,  # Limite gratuito
            limite_requisicoes_minuto=10,
            timeout=30,
            retry_attempts=3,
            retry_delay=2
        )
        super().__init__(config)
    
    async def coletar_jogos(self, data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Coleta previsões de jogos para uma data específica"""
        if not data:
            data = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/predictions"
            params = {"date": data}
            
            response = await self._make_request(url, params=params)
            
            if response and "data" in response:
                jogos_padronizados = []
                for jogo in response["data"]:
                    jogo_padronizado = self._padronizar_jogo(jogo)
                    if jogo_padronizado:
                        jogos_padronizados.append(jogo_padronizado)
                return jogos_padronizados
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos: {e}")
            return []
    
    async def coletar_jogadores(self, time_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta informações de jogadores de um time específico.
        
        Args:
            time_id: ID do time
            
        Returns:
            Lista de jogadores
        """
        try:
            if not time_id:
                self.logger.warning("time_id é obrigatório para coletar jogadores")
                return []
            
            endpoint = f"/api/v1/team/{time_id}/players"
            response = await self._make_request(endpoint)
            
            jogadores = []
            if response and "data" in response and "players" in response["data"]:
                for jogador in response["data"]["players"]:
                    jogador_padronizado = self._padronizar_jogador(jogador)
                    if jogador_padronizado:
                        jogadores.append(jogador_padronizado)
            
            self.logger.info(f"✅ {len(jogadores)} jogadores coletados para time {time_id}")
            return jogadores
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogadores: {e}")
            return []
    
    async def coletar_ligas(self) -> List[Dict[str, Any]]:
        """Coleta lista de ligas disponíveis"""
        try:
            # Endpoint correto baseado no playground
            url = f"https://{self.config.host}/leagues/"
            
            response = await self._make_request(url)
            
            if response and "data" in response:
                ligas_padronizadas = []
                for liga in response["data"]:
                    liga_padronizada = self._padronizar_liga(liga)
                    if liga_padronizada:
                        ligas_padronizadas.append(liga_padronizada)
                return ligas_padronizadas
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar ligas: {e}")
            return []
    
    async def coletar_estatisticas(self, time_id: Optional[str] = None, jogo_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas de times ou jogos específicos.
        
        Args:
            time_id: ID do time
            jogo_id: ID do jogo
            
        Returns:
            Lista de estatísticas
        """
        try:
            if time_id:
                endpoint = f"/api/v1/team/{time_id}/stats"
                response = await self._make_request(endpoint)
                if response:
                    return self._padronizar_estatisticas_time(response, time_id)
                return []
            
            elif jogo_id:
                endpoint = f"/api/v1/match/{jogo_id}/stats"
                response = await self._make_request(endpoint)
                if response:
                    return self._padronizar_estatisticas_jogo(response, jogo_id)
                return []
            
            else:
                self.logger.warning("time_id ou jogo_id é obrigatório")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas: {e}")
            return []
    
    async def coletar_odds(self, jogo_id: Optional[str] = None, data: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta odds e probabilidades para jogos.
        
        Args:
            jogo_id: ID do jogo específico
            data: Data para filtrar jogos
            
        Returns:
            Lista de odds
        """
        try:
            if jogo_id:
                endpoint = f"/api/v1/match/{jogo_id}/odds"
                response = await self._make_request(endpoint)
                if response:
                    return self._padronizar_odds_jogo(response, jogo_id)
                return []
            
            elif data:
                # Coletar odds para todos os jogos de uma data
                jogos = await self.coletar_jogos(data)
                odds_todos = []
                
                for jogo in jogos:
                    if "id" in jogo:
                        odds_jogo = await self.coletar_odds(jogo["id"])
                        odds_todos.extend(odds_jogo)
                
                return odds_todos
            
            else:
                self.logger.warning("jogo_id ou data é obrigatório")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar odds: {e}")
            return []
    
    async def coletar_noticias(self, time_id: Optional[str] = None, liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta notícias relacionadas a times ou ligas.
        
        Args:
            time_id: ID do time
            liga_id: ID da liga
            
        Returns:
            Lista de notícias
        """
        try:
            if time_id:
                endpoint = f"/api/v1/team/{time_id}/news"
            elif liga_id:
                endpoint = f"/api/v1/league/{liga_id}/news"
            else:
                self.logger.warning("time_id ou liga_id é obrigatório")
                return []
            
            response = await self._make_request(endpoint)
            if response:
                return self._padronizar_noticias(response)
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar notícias: {e}")
            return []
    
    # ============================================================================
    # FUNÇÕES AUXILIARES PARA PADRONIZAÇÃO DE DADOS
    # ============================================================================
    
    def _padronizar_jogo(self, predicao: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza os dados de um jogo."""
        try:
            return {
                "id": predicao.get("match_id"),
                "data": predicao.get("date"),
                "hora": predicao.get("time"),
                "liga": predicao.get("league"),
                "pais": predicao.get("country"),
                "time_casa": predicao.get("home_team"),
                "time_visitante": predicao.get("away_team"),
                "probabilidade_casa": predicao.get("home_win_probability"),
                "probabilidade_empate": predicao.get("draw_probability"),
                "probabilidade_visitante": predicao.get("away_win_probability"),
                "odds_casa": predicao.get("home_odds"),
                "odds_empate": predicao.get("draw_odds"),
                "odds_visitante": predicao.get("away_odds"),
                "previsao_recomendada": predicao.get("recommended_bet"),
                "confianca": predicao.get("confidence"),
                "fonte": "Today Football Prediction",
                "coletado_em": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar jogo: {e}")
            return None
    
    def _padronizar_jogador(self, jogador: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza os dados de um jogador."""
        try:
            return {
                "id": jogador.get("player_id"),
                "nome": jogador.get("name"),
                "posicao": jogador.get("position"),
                "idade": jogador.get("age"),
                "altura": jogador.get("height"),
                "peso": jogador.get("weight"),
                "nacionalidade": jogador.get("nationality"),
                "valor_mercado": jogador.get("market_value"),
                "contrato_ate": jogador.get("contract_until"),
                "fonte": "Today Football Prediction",
                "coletado_em": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar jogador: {e}")
            return None
    
    def _padronizar_liga(self, liga: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza os dados de uma liga."""
        try:
            return {
                "id": liga.get("league_id"),
                "nome": liga.get("name"),
                "pais": liga.get("country"),
                "tipo": liga.get("type"),
                "temporada": liga.get("season"),
                "ativo": liga.get("active", True),
                "fonte": "Today Football Prediction",
                "coletado_em": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar liga: {e}")
            return None
    
    def _padronizar_estatisticas_time(self, response: Dict[str, Any], time_id: str) -> List[Dict[str, Any]]:
        """Padroniza estatísticas de um time."""
        try:
            stats = []
            if "data" in response and "stats" in response["data"]:
                for stat in response["data"]["stats"]:
                    stats.append({
                        "time_id": time_id,
                        "temporada": stat.get("season"),
                        "jogos": stat.get("matches_played"),
                        "vitorias": stat.get("wins"),
                        "empates": stat.get("draws"),
                        "derrotas": stat.get("losses"),
                        "gols_marcados": stat.get("goals_for"),
                        "gols_sofridos": stat.get("goals_against"),
                        "pontos": stat.get("points"),
                        "posicao": stat.get("position"),
                        "fonte": "Today Football Prediction",
                        "coletado_em": datetime.now().isoformat()
                    })
            return stats
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar estatísticas do time: {e}")
            return []
    
    def _padronizar_estatisticas_jogo(self, response: Dict[str, Any], jogo_id: str) -> List[Dict[str, Any]]:
        """Padroniza estatísticas de um jogo."""
        try:
            stats = []
            if "data" in response and "stats" in response["data"]:
                for stat in response["data"]["stats"]:
                    stats.append({
                        "jogo_id": jogo_id,
                        "time": stat.get("team"),
                        "posse_bola": stat.get("possession"),
                        "finalizacoes": stat.get("shots"),
                        "finalizacoes_no_gol": stat.get("shots_on_target"),
                        "escanteios": stat.get("corners"),
                        "faltas": stat.get("fouls"),
                        "cartoes_amarelos": stat.get("yellow_cards"),
                        "cartoes_vermelhos": stat.get("red_cards"),
                        "fonte": "Today Football Prediction",
                        "coletado_em": datetime.now().isoformat()
                    })
            return stats
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar estatísticas do jogo: {e}")
            return []
    
    def _padronizar_odds_jogo(self, response: Dict[str, Any], jogo_id: str) -> List[Dict[str, Any]]:
        """Padroniza odds de um jogo."""
        try:
            odds = []
            if "data" in response and "odds" in response["data"]:
                for odd in response["data"]["odds"]:
                    odds.append({
                        "jogo_id": jogo_id,
                        "casa_aposta": odd.get("bookmaker"),
                        "mercado": odd.get("market"),
                        "selecao": odd.get("selection"),
                        "odds": odd.get("odds"),
                        "probabilidade": odd.get("probability"),
                        "fonte": "Today Football Prediction",
                        "coletado_em": datetime.now().isoformat()
                    })
            return odds
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar odds: {e}")
            return []
    
    def _padronizar_noticias(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Padroniza notícias."""
        try:
            noticias = []
            if "data" in response and "news" in response["data"]:
                for noticia in response["data"]["news"]:
                    noticias.append({
                        "id": noticia.get("news_id"),
                        "titulo": noticia.get("title"),
                        "resumo": noticia.get("summary"),
                        "conteudo": noticia.get("content"),
                        "url": noticia.get("url"),
                        "imagem": noticia.get("image"),
                        "data_publicacao": noticia.get("published_at"),
                        "autor": noticia.get("author"),
                        "fonte": "Today Football Prediction",
                        "coletado_em": datetime.now().isoformat()
                    })
            return noticias
        except Exception as e:
            self.logger.warning(f"Erro ao padronizar notícias: {e}")
            return []
