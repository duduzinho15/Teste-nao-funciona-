#!/usr/bin/env python3
"""
Demonstração da integração com APIs de casas de apostas
"""
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adicionar diretório pai ao path
sys.path.append(str(Path(__file__).parent))

def main():
    """Função principal da demonstração"""
    print("🎯 APOSTAPRO - Demonstração de Integração com APIs de Casas de Apostas")
    print("=" * 80)
    
    try:
        # Importar módulos
        from ml_models.betting_apis_integration import (
            betting_api_integration,
            get_live_matches,
            get_match_odds,
            get_competition_matches,
            get_match_result,
            get_market_analysis
        )
        
        print("✅ Módulos importados com sucesso")
        
        # Verificar configuração das APIs
        print("\n🔑 Verificando configuração das APIs...")
        api_configs = betting_api_integration.api_configs
        
        for api_name, config in api_configs.items():
            if config['api_key']:
                print(f"   ✅ {api_name}: Configurado")
            else:
                print(f"   ⚠️  {api_name}: Chave não configurada")
        
        # Demonstração com dados simulados (sem chaves de API reais)
        print("\n📊 Demonstração com dados simulados...")
        
        # 1. Simular obtenção de partidas ao vivo
        print("\n1️⃣ Simulando obtenção de partidas ao vivo...")
        live_matches = [
            {
                'match_id': '12345',
                'home_team': 'Manchester City',
                'away_team': 'Liverpool',
                'competition': 'Premier League',
                'match_date': '2025-01-15T20:00:00Z',
                'status': 'live',
                'score': {'home': 1, 'away': 0},
                'api_source': 'football_data_org'
            },
            {
                'match_id': '12346',
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'competition': 'La Liga',
                'match_date': '2025-01-15T21:00:00Z',
                'status': 'live',
                'score': {'home': 0, 'away': 1},
                'api_source': 'api_football'
            }
        ]
        
        print(f"   📍 Partidas ao vivo encontradas: {len(live_matches)}")
        for match in live_matches:
            print(f"      • {match['home_team']} vs {match['away_team']} ({match['competition']})")
        
        # 2. Simular obtenção de odds
        print("\n2️⃣ Simulando obtenção de odds...")
        from ml_models.betting_apis_integration import BettingOdds
        from datetime import datetime
        
        sample_odds = BettingOdds(
            bookmaker='Bet365',
            match_id='12345',
            home_team='Manchester City',
            away_team='Liverpool',
            competition='Premier League',
            match_date='2025-01-15T20:00:00Z',
            home_odds=2.10,
            draw_odds=3.40,
            away_odds=3.20,
            over_25_odds=1.85,
            under_25_odds=1.95,
            both_teams_score_yes=1.75,
            both_teams_score_no=2.05,
            timestamp=datetime.now(),
            last_update=datetime.now()
        )
        
        print(f"   🎲 Odds obtidas para {sample_odds.home_team} vs {sample_odds.away_team}:")
        print(f"      • Casa: {sample_odds.home_odds}")
        print(f"      • Empate: {sample_odds.draw_odds}")
        print(f"      • Fora: {sample_odds.away_odds}")
        print(f"      • Over 2.5: {sample_odds.over_25_odds}")
        print(f"      • Ambas marcam: {sample_odds.both_teams_score_yes}")
        
        # 3. Simular obtenção de resultados
        print("\n3️⃣ Simulando obtenção de resultados...")
        from ml_models.betting_apis_integration import MatchResult
        
        sample_result = MatchResult(
            match_id='12345',
            home_team='Manchester City',
            away_team='Liverpool',
            competition='Premier League',
            match_date='2025-01-15T20:00:00Z',
            home_goals=2,
            away_goals=1,
            total_goals=3,
            both_teams_score=True,
            result='H',
            half_time_score='1-0',
            full_time_score='2-1',
            status='finished',
            timestamp=datetime.now()
        )
        
        print(f"   ⚽ Resultado: {sample_result.home_team} {sample_result.full_time_score} {sample_result.away_team}")
        print(f"      • Resultado: {'Casa' if sample_result.result == 'H' else 'Fora' if sample_result.result == 'A' else 'Empate'}")
        print(f"      • Total de gols: {sample_result.total_goals}")
        print(f"      • Ambas marcaram: {'Sim' if sample_result.both_teams_score else 'Não'}")
        
        # 4. Simular análise de mercado
        print("\n4️⃣ Simulando análise de mercado...")
        
        market_analysis = {
            'total_matches': 50,
            'competition_analysis': {
                'Premier League': {
                    'total_matches': 20,
                    'home_win_rate': 0.45,
                    'away_win_rate': 0.30,
                    'draw_rate': 0.25,
                    'avg_goals_per_match': 2.8,
                    'both_teams_score_rate': 0.65,
                    'market_efficiency': 'Balanced'
                },
                'La Liga': {
                    'total_matches': 30,
                    'home_win_rate': 0.50,
                    'away_win_rate': 0.25,
                    'draw_rate': 0.25,
                    'avg_goals_per_match': 2.5,
                    'both_teams_score_rate': 0.60,
                    'market_efficiency': 'Home Bias'
                }
            },
            'value_betting_opportunities': [
                {
                    'match': 'Arsenal vs Chelsea',
                    'bet_type': 'Home Win',
                    'odds': 2.20,
                    'implied_probability': 0.45,
                    'actual_result': 'Home Win',
                    'value_score': 0.15
                },
                {
                    'match': 'Bayern Munich vs Dortmund',
                    'bet_type': 'Over 2.5',
                    'odds': 1.75,
                    'implied_probability': 0.57,
                    'actual_result': 'Over 2.5',
                    'value_score': 0.12
                }
            ]
        }
        
        print(f"   📈 Análise de mercado:")
        print(f"      • Total de partidas analisadas: {market_analysis['total_matches']}")
        
        for comp_name, comp_data in market_analysis['competition_analysis'].items():
            print(f"      • {comp_name}:")
            print(f"        - Taxa de vitória em casa: {comp_data['home_win_rate']:.1%}")
            print(f"        - Taxa de vitória fora: {comp_data['away_win_rate']:.1%}")
            print(f"        - Média de gols: {comp_data['avg_goals_per_match']:.1f}")
            print(f"        - Eficiência do mercado: {comp_data['market_efficiency']}")
        
        print(f"      • Oportunidades de value betting encontradas: {len(market_analysis['value_betting_opportunities'])}")
        for opp in market_analysis['value_betting_opportunities']:
            print(f"        - {opp['match']}: {opp['bet_type']} @ {opp['odds']} (Score: {opp['value_score']:.3f})")
        
        # 5. Simular salvamento de dados
        print("\n5️⃣ Simulando salvamento de dados...")
        
        # Simular dados para salvar
        odds_data = [sample_odds]
        results_data = [sample_result]
        
        try:
            betting_api_integration.save_data_to_database(odds_data, 'odds')
            betting_api_integration.save_data_to_database(results_data, 'results')
            print("   💾 Dados salvos com sucesso")
        except Exception as e:
            print(f"   ⚠️  Erro ao salvar dados: {e}")
        
        # 6. Demonstração de funcionalidades avançadas
        print("\n6️⃣ Funcionalidades avançadas disponíveis...")
        
        advanced_features = [
            "✅ Integração com múltiplas APIs (Football Data, API Football, Odds API)",
            "✅ Rate limiting automático para respeitar limites das APIs",
            "✅ Cache inteligente para otimizar requisições",
            "✅ Análise de mercado em tempo real",
            "✅ Identificação de oportunidades de value betting",
            "✅ Suporte a múltiplas competições e temporadas",
            "✅ Salvamento automático de dados em CSV",
            "✅ Tratamento de erros e fallbacks"
        ]
        
        for feature in advanced_features:
            print(f"   {feature}")
        
        # 7. Configuração para uso real
        print("\n7️⃣ Configuração para uso real...")
        
        setup_instructions = [
            "📝 Para usar com dados reais, configure as seguintes variáveis de ambiente:",
            "   • FOOTBALL_DATA_API_KEY: Chave da API Football Data (https://www.football-data.org/)",
            "   • API_FOOTBALL_KEY: Chave da API Football (https://www.api-football.com/)",
            "   • ODDS_API_KEY: Chave da Odds API (https://the-odds-api.com/)",
            "",
            "📁 Ou crie um arquivo .env na raiz do projeto com:",
            "   FOOTBALL_DATA_API_KEY=sua_chave_aqui",
            "   API_FOOTBALL_KEY=sua_chave_aqui",
            "   ODDS_API_KEY=sua_chave_aqui"
        ]
        
        for instruction in setup_instructions:
            print(instruction)
        
        print("\n🎉 Demonstração concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("   1. Configure as chaves das APIs para obter dados reais")
        print("   2. Teste a integração com competições específicas")
        print("   3. Implemente alertas para oportunidades de value betting")
        print("   4. Integre com o sistema de ML para predições em tempo real")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
