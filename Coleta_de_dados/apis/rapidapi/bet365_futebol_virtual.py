"""
Bet365 Futebol Virtual API - Coleta de dados de futebol virtual e odds
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .base_rapidapi import RapidAPIBase, RapidAPIConfig


class Bet365FutebolVirtualAPI(RapidAPIBase):
    """
    API para coleta de dados de futebol virtual da Bet365 via RapidAPI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Usar chave padrão se não fornecida
        if api_key is None:
            api_key = "chave_padrao_rapidapi"  # Será substituída pela variável de ambiente
        
        config = RapidAPIConfig(
            nome="Bet365 Futebol Virtual",
            host="bet36528.p.rapidapi.com",
            endpoint_base="https://bet36528.p.rapidapi.com",
            chaves=[api_key],
            limite_requisicoes_dia=100,
            limite_requisicoes_minuto=10,
            timeout=30,
            retry_attempts=3,
            retry_delay=2
        )
        super().__init__(config)
    
    async def coletar_jogos(self, 
                           esporte: Optional[str] = None, 
                           liga_id: Optional[str] = None, 
                           data: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogos de futebol virtual disponíveis
        
        Args:
            esporte: Esporte (padrão: 'football')
            liga_id: ID da liga virtual
            data: Data para filtrar jogos
            
        Returns:
            Lista de jogos virtuais
        """
        try:
            params = {
                "sport": esporte or "football",
                "league": liga_id or "virtual",
                "date": data or datetime.now().strftime("%Y-%m-%d")
            }
            
            response = await self._make_request(
                "/odds_bet365",
                params=params
            )
            
            if response and "data" in response:
                jogos = []
                for jogo in response.get("data", []):
                    jogo_padronizado = self._padronizar_jogo_virtual(jogo)
                    if jogo_padronizado:
                        jogos.append(jogo_padronizado)
                
                self.logger.info(f"Coletados {len(jogos)} jogos virtuais")
                return jogos
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar jogos virtuais: {e}")
            return []
    
    async def coletar_jogadores(self, 
                               esporte: Optional[str] = None, 
                               clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta jogadores virtuais (não aplicável para futebol virtual)
        
        Returns:
            Lista vazia (futebol virtual não tem jogadores reais)
        """
        # Futebol virtual não tem jogadores reais
        return []
    
    async def coletar_ligas(self, 
                           esporte: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta ligas virtuais disponíveis
        
        Args:
            esporte: Esporte (padrão: 'football')
            
        Returns:
            Lista de ligas virtuais
        """
        try:
            params = {
                "sport": esporte or "football",
                "type": "virtual"
            }
            
            response = await self._make_request(
                "/odds_bet365",
                params=params
            )
            
            if response and "leagues" in response:
                ligas = []
                for liga in response["leagues"]:
                    liga_padronizada = self._padronizar_liga_virtual(liga)
                    if liga_padronizada:
                        ligas.append(liga_padronizada)
                
                self.logger.info(f"Coletadas {len(ligas)} ligas virtuais")
                return ligas
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar ligas virtuais: {e}")
            return []
    
    async def coletar_estatisticas(self, 
                                  partida_id: Optional[str] = None, 
                                  clube_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta estatísticas de partidas virtuais
        
        Args:
            partida_id: ID da partida virtual
            clube_id: ID do clube virtual
            
        Returns:
            Lista de estatísticas
        """
        try:
            params = {}
            if partida_id:
                params["match_id"] = partida_id
            if clube_id:
                params["team_id"] = clube_id
            
            response = await self._make_request(
                "virtual_statistics",
                params=params
            )
            
            if response and "statistics" in response:
                stats = []
                for stat in response["statistics"]:
                    stat_padronizada = self._padronizar_estatistica_virtual(stat)
                    if stat_padronizada:
                        stats.append(stat_padronizada)
                
                self.logger.info(f"Coletadas {len(stats)} estatísticas virtuais")
                return stats
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar estatísticas virtuais: {e}")
            return []
    
    async def coletar_odds(self, 
                          partida_id: str) -> List[Dict[str, Any]]:
        """
        Coleta odds de partidas virtuais
        
        Args:
            partida_id: ID da partida virtual
            
        Returns:
            Lista de odds
        """
        try:
            params = {"match_id": partida_id}
            
            response = await self._make_request(
                "virtual_odds",
                params=params
            )
            
            if response and "odds" in response:
                odds = []
                for odd in response["odds"]:
                    odd_padronizada = self._padronizar_odd_virtual(odd)
                    if odd_padronizada:
                        odds.append(odd_padronizada)
                
                self.logger.info(f"Coletadas {len(odds)} odds virtuais")
                return odds
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar odds virtuais: {e}")
            return []
    
    async def coletar_noticias(self, 
                              clube_id: Optional[str] = None, 
                              liga_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta notícias relacionadas ao futebol virtual (não aplicável)
        
        Returns:
            Lista vazia (futebol virtual não tem notícias)
        """
        # Futebol virtual não tem notícias
        return []
    
    async def coletar_resultados_virtuais(self, 
                                        data: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Coleta resultados de partidas virtuais
        
        Args:
            data: Data para filtrar resultados
            
        Returns:
            Lista de resultados virtuais
        """
        try:
            params = {
                "date": data or datetime.now().strftime("%Y-%m-%d")
            }
            
            response = await self._make_request(
                "virtual_results",
                params=params
            )
            
            if response and "results" in response:
                resultados = []
                for resultado in response["results"]:
                    resultado_padronizado = self._padronizar_resultado_virtual(resultado)
                    if resultado_padronizado:
                        resultados.append(resultado_padronizado)
                
                self.logger.info(f"Coletados {len(resultados)} resultados virtuais")
                return resultados
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar resultados virtuais: {e}")
            return []
    
    async def coletar_proximos_jogos_virtuais(self, 
                                             horas: int = 24) -> List[Dict[str, Any]]:
        """
        Coleta próximos jogos virtuais nas próximas horas
        
        Args:
            horas: Número de horas para frente
            
        Returns:
            Lista de próximos jogos virtuais
        """
        try:
            data_futura = datetime.now() + timedelta(hours=horas)
            params = {
                "date": data_futura.strftime("%Y-%m-%d"),
                "type": "upcoming"
            }
            
            response = await self._make_request(
                "virtual_matches",
                params=params
            )
            
            if response and "matches" in response:
                jogos = []
                for jogo in response["matches"]:
                    jogo_padronizado = self._padronizar_jogo_virtual(jogo)
                    if jogo_padronizado:
                        jogos.append(jogo_padronizado)
                
                self.logger.info(f"Coletados {len(jogos)} próximos jogos virtuais")
                return jogos
            
            return []
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar próximos jogos virtuais: {e}")
            return []
    
    def _padronizar_jogo_virtual(self, jogo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de jogo virtual"""
        try:
            return {
                "id": jogo.get("match_id"),
                "tipo": "virtual",
                "esporte": "football",
                "liga": jogo.get("league", {}).get("name"),
                "liga_id": jogo.get("league", {}).get("id"),
                "casa": jogo.get("home_team", {}).get("name"),
                "casa_id": jogo.get("home_team", {}).get("id"),
                "visitante": jogo.get("away_team", {}).get("name"),
                "visitante_id": jogo.get("away_team", {}).get("id"),
                "data_inicio": jogo.get("start_time"),
                "status": jogo.get("status"),
                "resultado_casa": jogo.get("home_score"),
                "resultado_visitante": jogo.get("away_score"),
                "periodo": jogo.get("period"),
                "tempo_restante": jogo.get("time_remaining"),
                "fonte": "bet365_virtual",
                "timestamp_coleta": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao padronizar jogo virtual: {e}")
            return None
    
    def _padronizar_liga_virtual(self, liga: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de liga virtual"""
        try:
            return {
                "id": liga.get("id"),
                "nome": liga.get("name"),
                "pais": liga.get("country"),
                "tipo": "virtual",
                "esporte": "football",
                "nivel": liga.get("level"),
                "status": liga.get("status"),
                "fonte": "bet365_virtual",
                "timestamp_coleta": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao padronizar liga virtual: {e}")
            return None
    
    def _padronizar_estatistica_virtual(self, stat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de estatística virtual"""
        try:
            return {
                "id": stat.get("stat_id"),
                "partida_id": stat.get("match_id"),
                "tipo": stat.get("type"),
                "valor": stat.get("value"),
                "equipe": stat.get("team"),
                "periodo": stat.get("period"),
                "fonte": "bet365_virtual",
                "timestamp_coleta": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao padronizar estatística virtual: {e}")
            return None
    
    def _padronizar_odd_virtual(self, odd: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de odd virtual"""
        try:
            return {
                "id": odd.get("odd_id"),
                "partida_id": odd.get("match_id"),
                "tipo": odd.get("type"),
                "selecao": odd.get("selection"),
                "odd": odd.get("odds"),
                "probabilidade": odd.get("probability"),
                "status": odd.get("status"),
                "fonte": "bet365_virtual",
                "timestamp_coleta": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao padronizar odd virtual: {e}")
            return None
    
    def _padronizar_resultado_virtual(self, resultado: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Padroniza dados de resultado virtual"""
        try:
            return {
                "id": resultado.get("result_id"),
                "partida_id": resultado.get("match_id"),
                "resultado_final": resultado.get("final_score"),
                "resultado_casa": resultado.get("home_score"),
                "resultado_visitante": resultado.get("away_score"),
                "vencedor": resultado.get("winner"),
                "status": resultado.get("status"),
                "data_fim": resultado.get("end_time"),
                "fonte": "bet365_virtual",
                "timestamp_coleta": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erro ao padronizar resultado virtual: {e}")
            return None


async def demo_bet365_futebol_virtual():
    """Demonstração da API Bet365 Futebol Virtual"""
    print("=== Demo Bet365 Futebol Virtual API ===")
    
    # Inicializar API
    api = Bet365FutebolVirtualAPI()
    
    try:
        # Coletar ligas virtuais
        print("\n1. Coletando ligas virtuais...")
        ligas = await api.coletar_ligas()
        print(f"Ligas encontradas: {len(ligas)}")
        for liga in ligas[:3]:  # Mostrar apenas 3
            print(f"  - {liga['nome']} ({liga['pais']})")
        
        # Coletar jogos virtuais
        print("\n2. Coletando jogos virtuais...")
        jogos = await api.coletar_jogos()
        print(f"Jogos encontrados: {len(jogos)}")
        for jogo in jogos[:3]:  # Mostrar apenas 3
            print(f"  - {jogo['casa']} vs {jogo['visitante']} ({jogo['status']})")
        
        # Coletar próximos jogos
        print("\n3. Coletando próximos jogos virtuais...")
        proximos = await api.coletar_proximos_jogos_virtuais(horas=12)
        print(f"Próximos jogos: {len(proximos)}")
        for jogo in proximos[:3]:  # Mostrar apenas 3
            print(f"  - {jogo['casa']} vs {jogo['visitante']} em {jogo['data_inicio']}")
        
        # Coletar resultados
        print("\n4. Coletando resultados virtuais...")
        resultados = await api.coletar_resultados_virtuais()
        print(f"Resultados encontrados: {len(resultados)}")
        for resultado in resultados[:3]:  # Mostrar apenas 3
            print(f"  - {resultado['resultado_final']} - {resultado['status']}")
        
        # Se houver jogos, tentar coletar odds
        if jogos:
            print("\n5. Coletando odds para primeiro jogo...")
            primeiro_jogo = jogos[0]
            odds = await api.coletar_odds(primeiro_jogo['id'])
            print(f"Odds encontradas: {len(odds)}")
            for odd in odds[:3]:  # Mostrar apenas 3
                print(f"  - {odd['tipo']}: {odd['odd']} ({odd['probabilidade']}%)")
        
        print("\n✅ Demo Bet365 Futebol Virtual concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_bet365_futebol_virtual())
