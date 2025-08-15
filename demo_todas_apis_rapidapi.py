"""
Demonstração Completa de Todas as APIs RapidAPI Implementadas
============================================================

Este script demonstra todas as 8 APIs RapidAPI implementadas no sistema:
1. TodayFootballPredictionAPI
2. SoccerFootballInfoAPI  
3. SportspageFeedsAPI
4. FootballPredictionAPI
5. PinnacleOddsAPI
6. TransfermarktDBAPI
7. FootballProAPI
8. Bet365FutebolVirtualAPI

Autor: Sistema de Coleta de Dados
Data: 2025-08-14
Versão: 1.0
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.abspath('.'))

from Coleta_de_dados.apis.rapidapi import (
    TodayFootballPredictionAPI,
    SoccerFootballInfoAPI,
    SportspageFeedsAPI,
    FootballPredictionAPI,
    PinnacleOddsAPI,
    PlayerMarketDataAPI,
    FootballProAPI,
    Bet365FutebolVirtualAPI,
    SportAPI7API
)

from Coleta_de_dados.utils.logger_centralizado import CentralizedLogger


class DemoRapidAPIsCompleto:
    """Classe para demonstrar todas as APIs RapidAPI implementadas"""
    
    def __init__(self):
        self.logger = CentralizedLogger("demo_rapidapi_completo")
        self.resultados = {}
        self.erros = []
        
    async def demo_today_football_prediction(self):
        """Demonstração da API Today Football Prediction"""
        print("\n🔄 Testando Today Football Prediction API...")
        try:
            api = TodayFootballPredictionAPI()
            
            # Testar coleta de jogos
            jogos = api.coletar_jogos()
            print(f"  ✅ Jogos coletados: {len(jogos)}")
            
            # Testar coleta de ligas
            ligas = api.coletar_ligas()
            print(f"  ✅ Ligas coletadas: {len(ligas)}")
            
            self.resultados['today_football_prediction'] = {
                'jogos': len(jogos),
                'ligas': len(ligas),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Today Football Prediction: {e}")
            self.resultados['today_football_prediction'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_soccer_football_info(self):
        """Demonstração da API Soccer Football Info"""
        print("\n🔄 Testando Soccer Football Info API...")
        try:
            api = SoccerFootballInfoAPI()
            
            # Testar coleta de jogos
            jogos = await api.coletar_jogos()
            print(f"  ✅ Jogos coletados: {len(jogos)}")
            
            # Testar coleta de jogadores
            jogadores = await api.coletar_jogadores()
            print(f"  ✅ Jogadores coletados: {len(jogadores)}")
            
            self.resultados['soccer_football_info'] = {
                'jogos': len(jogos),
                'jogadores': len(jogadores),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Soccer Football Info: {e}")
            self.resultados['soccer_football_info'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_sportspage_feeds(self):
        """Demonstração da API Sportspage Feeds"""
        print("\n🔄 Testando Sportspage Feeds API...")
        try:
            api = SportspageFeedsAPI()
            
            # Testar coleta de feeds esportivos
            feeds = await api.coletar_jogos(esporte="football")
            print(f"  ✅ Feeds coletados: {len(feeds)}")
            
            # Testar coleta de notícias
            noticias = await api.coletar_noticias(esporte="football")
            print(f"  ✅ Notícias coletadas: {len(noticias)}")
            
            self.resultados['sportspage_feeds'] = {
                'feeds': len(feeds),
                'noticias': len(noticias),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Sportspage Feeds: {e}")
            self.resultados['sportspage_feeds'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_football_prediction(self):
        """Demonstração da API Football Prediction"""
        print("\n🔄 Testando Football Prediction API...")
        try:
            api = FootballPredictionAPI()
            
            # Testar coleta de previsões
            previsoes = await api.coletar_jogos()
            print(f"  ✅ Previsões coletadas: {len(previsoes)}")
            
            # Testar coleta de odds
            odds = await api.coletar_odds("test_match_id")
            print(f"  ✅ Odds coletadas: {len(odds)}")
            
            self.resultados['football_prediction'] = {
                'previsoes': len(previsoes),
                'odds': len(odds),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Football Prediction: {e}")
            self.resultados['football_prediction'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_pinnacle_odds(self):
        """Demonstração da API Pinnacle Odds"""
        print("\n🔄 Testando Pinnacle Odds API...")
        try:
            api = PinnacleOddsAPI()
            
            # Testar coleta de odds
            odds = await api.coletar_odds()
            print(f"  ✅ Odds coletadas: {len(odds)}")
            
            # Testar coleta de linhas de apostas
            linhas = await api.coletar_linhas_apostas()
            print(f"  ✅ Linhas de apostas coletadas: {len(linhas)}")
            
            self.resultados['pinnacle_odds'] = {
                'odds': len(odds),
                'linhas_apostas': len(linhas),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Pinnacle Odds: {e}")
            self.resultados['pinnacle_odds'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_player_market_data(self):
        """Demonstração da API Player Market Data"""
        print("\n🔄 Testando Player Market Data API...")
        try:
            api = PlayerMarketDataAPI()
            
            # Testar coleta de jogadores
            jogadores = await api.coletar_jogadores()
            print(f"  ✅ Jogadores coletados: {len(jogadores)}")
            
            # Testar coleta de valores de mercado
            valores = await api.coletar_valores_mercado()
            print(f"  ✅ Valores de mercado coletados: {len(valores)}")
            
            self.resultados['player_market_data'] = {
                'jogadores': len(jogadores),
                'valores_mercado': len(valores),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Player Market Data: {e}")
            self.resultados['player_market_data'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_football_pro(self):
        """Demonstração da API Football Pro"""
        print("\n🔄 Testando Football Pro API...")
        try:
            api = FootballProAPI()
            
            # Testar coleta de análises avançadas
            analises = await api.coletar_analises_avancadas()
            print(f"  ✅ Análises avançadas coletadas: {len(analises)}")
            
            # Testar coleta de insights táticos
            insights = await api.coletar_insights_taticos()
            print(f"  ✅ Insights táticos coletados: {len(insights)}")
            
            self.resultados['football_pro'] = {
                'analises_avancadas': len(analises),
                'insights_taticos': len(insights),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Football Pro: {e}")
            self.resultados['football_pro'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_bet365_futebol_virtual(self):
        """Demonstração da API Bet365 Futebol Virtual"""
        print("\n🔄 Testando Bet365 Futebol Virtual API...")
        try:
            api = Bet365FutebolVirtualAPI()
            
            # Testar coleta de jogos virtuais
            jogos = await api.coletar_jogos()
            print(f"  ✅ Jogos virtuais coletados: {len(jogos)}")
            
            # Testar coleta de resultados virtuais
            resultados = await api.coletar_resultados_virtuais()
            print(f"  ✅ Resultados virtuais coletados: {len(resultados)}")
            
            self.resultados['bet365_futebol_virtual'] = {
                'jogos_virtuais': len(jogos),
                'resultados_virtuais': len(resultados),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"Bet365 Futebol Virtual: {e}")
            self.resultados['bet365_futebol_virtual'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def demo_sportapi7(self):
        """Demonstração da API SportAPI7"""
        print("\n🔄 Testando SportAPI7 API...")
        try:
            api = SportAPI7API()
            
            # Testar coleta de ligas
            ligas = await api.coletar_ligas()
            print(f"  ✅ Ligas coletadas: {len(ligas)}")
            
            # Testar coleta de jogadores
            jogadores = await api.coletar_jogadores()
            print(f"  ✅ Jogadores coletados: {len(jogadores)}")
            
            # Testar coleta de dados de time (se houver jogadores)
            if jogadores:
                primeiro_jogador = jogadores[0]
                if primeiro_jogador.get("clube_id"):
                    time_data = await api.coletar_dados_time(primeiro_jogador["clube_id"])
                    if time_data:
                        print(f"  ✅ Dados do time coletados: {time_data['nome']}")
            
            self.resultados['sportapi7'] = {
                'ligas': len(ligas),
                'jogadores': len(jogadores),
                'status': 'sucesso'
            }
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            self.erros.append(f"SportAPI7: {e}")
            self.resultados['sportapi7'] = {
                'status': 'erro',
                'erro': str(e)
            }
    
    async def executar_todos_demos(self):
        """Executa todos os demos das APIs RapidAPI"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DAS APIS RAPIDAPI")
        print("=" * 60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Executar todos os demos
        await asyncio.gather(
            self.demo_today_football_prediction(),
            self.demo_soccer_football_info(),
            self.demo_sportspage_feeds(),
            self.demo_football_prediction(),
            self.demo_pinnacle_odds(),
            self.demo_player_market_data(),
            self.demo_football_pro(),
            self.demo_bet365_futebol_virtual(),
            self.demo_sportapi7()
        )
        
        # Exibir resumo
        self.exibir_resumo()
    
    def exibir_resumo(self):
        """Exibe resumo dos resultados de todos os demos"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS RESULTADOS")
        print("=" * 60)
        
        apis_sucesso = 0
        apis_erro = 0
        
        for nome_api, resultado in self.resultados.items():
            if resultado['status'] == 'sucesso':
                apis_sucesso += 1
                print(f"✅ {nome_api.replace('_', ' ').title()}: SUCESSO")
            else:
                apis_erro += 1
                print(f"❌ {nome_api.replace('_', ' ').title()}: ERRO")
                print(f"   Erro: {resultado.get('erro', 'N/A')}")
        
        print("\n" + "=" * 60)
        print(f"📈 ESTATÍSTICAS FINAIS:")
        print(f"   Total de APIs: {len(self.resultados)}")
        print(f"   APIs com sucesso: {apis_sucesso}")
        print(f"   APIs com erro: {apis_erro}")
        print(f"   Taxa de sucesso: {(apis_sucesso/len(self.resultados)*100):.1f}%")
        
        if self.erros:
            print(f"\n⚠️  ERROS ENCONTRADOS ({len(self.erros)}):")
            for erro in self.erros:
                print(f"   - {erro}")
        
        print("\n" + "=" * 60)
        print("🎯 SISTEMA RAPIDAPI COMPLETO IMPLEMENTADO!")
        print("=" * 60)


async def main():
    """Função principal"""
    demo = DemoRapidAPIsCompleto()
    await demo.executar_todos_demos()


if __name__ == "__main__":
    asyncio.run(main())
