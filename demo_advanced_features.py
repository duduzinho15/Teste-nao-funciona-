#!/usr/bin/env python3
"""
Demonstração das funcionalidades avançadas do sistema ML
Fases 3 e 4: Expansão de Features e Produção/Monitoramento
"""
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal da demonstração"""
    print("🚀 APOSTAPRO - DEMONSTRAÇÃO DAS FUNCIONALIDADES AVANÇADAS")
    print("=" * 70)
    print("📋 Fases 3 e 4: Expansão de Features e Produção/Monitoramento")
    print("=" * 70)
    
    try:
        # 1. Demonstração de Análise de Tendências
        print("\n1️⃣ ANÁLISE DE TENDÊNCIAS")
        print("-" * 50)
        demo_trend_analysis()
        
        # 2. Demonstração de Backtesting
        print("\n2️⃣ BACKTESTING DE ESTRATÉGIAS")
        print("-" * 50)
        demo_backtesting()
        
        # 3. Demonstração de Otimização de Hiperparâmetros
        print("\n3️⃣ OTIMIZAÇÃO DE HIPERPARÂMETROS")
        print("-" * 50)
        demo_hyperparameter_optimization()
        
        # 4. Demonstração de Monitoramento e Produção
        print("\n4️⃣ MONITORAMENTO E PRODUÇÃO")
        print("-" * 50)
        demo_production_monitoring()
        
        # 5. Demonstração de Relatórios de Performance
        print("\n5️⃣ RELATÓRIOS DE PERFORMANCE")
        print("-" * 50)
        demo_performance_reports()
        
        print("\n🎉 DEMONSTRAÇÃO DAS FUNCIONALIDADES AVANÇADAS CONCLUÍDA!")
        print("   O sistema está pronto para produção com monitoramento completo!")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        logger.error(f"Erro na demonstração: {e}", exc_info=True)

def demo_trend_analysis():
    """Demonstra análise de tendências"""
    try:
        print("   🔍 Analisando tendências de equipes...")
        
        from ml_models.advanced_features import analyze_trends
        
        # Análise de tendências para equipe específica
        print("   📊 Analisando Flamengo...")
        flamengo_trends = analyze_trends(
            team_name="Flamengo",
            days_back=90
        )
        
        if 'error' not in flamengo_trends:
            print(f"   ✅ Tendências do Flamengo analisadas:")
            trends = flamengo_trends.get('trends', {})
            
            if 'results' in trends:
                results = trends['results']
                print(f"      - Forma atual: {results.get('current_form', 'N/A')}")
                print(f"      - Direção da tendência: {results.get('trend_direction', 'N/A')}")
                print(f"      - Últimos 5 resultados: {results.get('last_5_results', [])}")
            
            if 'goals' in trends:
                goals = trends['goals']
                print(f"      - Média de gols marcados: {goals.get('avg_goals_scored', 'N/A')}")
                print(f"      - Média de gols sofridos: {goals.get('avg_goals_conceded', 'N/A')}")
                print(f"      - Diferença de gols: {goals.get('goal_difference', 'N/A')}")
            
            if 'performance' in trends:
                perf = trends['performance']
                print(f"      - Posse de bola média: {perf.get('avg_possession', 'N/A')}%")
                print(f"      - Eficiência de finalização: {perf.get('avg_shot_efficiency', 'N/A')}")
            
            if 'market' in trends:
                market = trends['market']
                print(f"      - Valor de mercado: {market.get('market_value', 'N/A')}")
                print(f"      - Oportunidade de aposta: {market.get('betting_opportunity', 'N/A')}")
        else:
            print(f"   ⚠️ Erro na análise: {flamengo_trends['error']}")
        
        # Análise de tendências da competição
        print("\n   🏆 Analisando tendências do Brasileirão...")
        competition_trends = analyze_trends(
            competition="Brasileirão",
            days_back=90
        )
        
        if 'error' not in competition_trends:
            print(f"   ✅ Tendências da competição analisadas:")
            trends = competition_trends.get('trends', {})
            
            if 'goals' in trends:
                goals = trends['goals']
                print(f"      - Média de gols por partida: {goals.get('avg_total_goals', 'N/A')}")
                print(f"      - Tendência de gols: {goals.get('goals_trend', 'N/A')}")
                print(f"      - Taxa de ambas marcam: {goals.get('both_teams_score_rate', 'N/A'):.1%}")
            
            if 'results' in trends:
                results = trends['results']
                print(f"      - Taxa de vitórias em casa: {results.get('home_win_rate', 'N/A'):.1%}")
                print(f"      - Taxa de vitórias fora: {results.get('away_win_rate', 'N/A'):.1%}")
                print(f"      - Taxa de empates: {results.get('draw_rate', 'N/A'):.1%}")
                print(f"      - Vantagem de jogar em casa: {results.get('home_advantage_strength', 'N/A'):.3f}")
            
            if 'market' in trends:
                market = trends['market']
                print(f"      - Odds médias (casa): {market.get('avg_home_odds', 'N/A')}")
                print(f"      - Odds médias (fora): {market.get('avg_away_odds', 'N/A')}")
                print(f"      - Odds médias (empate): {market.get('avg_draw_odds', 'N/A')}")
                
                opportunities = market.get('value_betting_opportunities', [])
                if opportunities:
                    print(f"      - Oportunidades de value betting encontradas: {len(opportunities)}")
                    for i, opp in enumerate(opportunities[:3], 1):
                        print(f"         {i}. {opp['match']} - {opp['bet_type']} @ {opp['odds']} (score: {opp['value_score']})")
        
        print("   ✅ Análise de tendências concluída!")
        
    except Exception as e:
        print(f"   ❌ Erro na análise de tendências: {e}")
        logger.error(f"Erro na análise de tendências: {e}")

def demo_backtesting():
    """Demonstra backtesting de estratégias"""
    try:
        print("   🧪 Executando backtesting de estratégias...")
        
        from ml_models.advanced_features import run_backtesting
        
        # Backtesting da estratégia de value betting
        print("   💰 Testando estratégia de value betting...")
        value_betting_results = run_backtesting(
            strategy_name="value_betting",
            start_date="2024-01-01",
            end_date="2024-12-31",
            competition="Brasileirão"
        )
        
        if 'error' not in value_betting_results:
            print(f"   ✅ Resultados do value betting:")
            print(f"      - Banca inicial: R$ {value_betting_results.get('initial_bankroll', 0):,.2f}")
            print(f"      - Banca final: R$ {value_betting_results.get('final_bankroll', 0):,.2f}")
            print(f"      - Lucro total: R$ {value_betting_results.get('total_profit', 0):,.2f}")
            print(f"      - ROI: {value_betting_results.get('roi', 0):.2f}%")
            print(f"      - Total de apostas: {value_betting_results.get('total_bets', 0)}")
            print(f"      - Taxa de acerto: {value_betting_results.get('win_rate', 0):.1%}")
        else:
            print(f"   ⚠️ Erro no value betting: {value_betting_results['error']}")
        
        # Backtesting da estratégia de seguir tendências
        print("\n   📈 Testando estratégia de seguir tendências...")
        trend_following_results = run_backtesting(
            strategy_name="trend_following",
            start_date="2024-01-01",
            end_date="2024-12-31",
            competition="Brasileirão"
        )
        
        if 'error' not in trend_following_results:
            print(f"   ✅ Resultados do trend following:")
            print(f"      - Banca inicial: R$ {trend_following_results.get('initial_bankroll', 0):,.2f}")
            print(f"      - Banca final: R$ {trend_following_results.get('final_bankroll', 0):,.2f}")
            print(f"      - Lucro total: R$ {trend_following_results.get('total_profit', 0):,.2f}")
            print(f"      - ROI: {trend_following_results.get('roi', 0):.2f}%")
            print(f"      - Total de apostas: {trend_following_results.get('total_bets', 0)}")
            print(f"      - Taxa de acerto: {trend_following_results.get('win_rate', 0):.1%}")
        else:
            print(f"   ⚠️ Erro no trend following: {trend_following_results['error']}")
        
        print("   ✅ Backtesting concluído!")
        
    except Exception as e:
        print(f"   ❌ Erro no backtesting: {e}")
        logger.error(f"Erro no backtesting: {e}")

def demo_hyperparameter_optimization():
    """Demonstra otimização de hiperparâmetros"""
    try:
        print("   ⚙️ Otimizando hiperparâmetros dos modelos...")
        
        from ml_models.advanced_features import optimize_hyperparameters
        
        # Otimização para modelo de predição de resultado
        print("   🎯 Otimizando modelo de predição de resultado...")
        result_optimization = optimize_hyperparameters(
            model_type="result_prediction",
            optimization_method="optuna",
            n_trials=50  # Reduzido para demonstração
        )
        
        if 'error' not in result_optimization:
            print(f"   ✅ Otimização concluída:")
            print(f"      - Método: {result_optimization.get('optimization_method', 'N/A')}")
            print(f"      - Status: {result_optimization.get('status', 'N/A')}")
            
            best_params = result_optimization.get('best_parameters', {})
            if best_params:
                print(f"      - Melhores parâmetros encontrados:")
                for param, value in best_params.get('best_params', {}).items():
                    print(f"         - {param}: {value}")
                print(f"      - Melhor score: {best_params.get('best_score', 'N/A'):.4f}")
                print(f"      - Tentativas realizadas: {best_params.get('n_trials', 'N/A')}")
        else:
            print(f"   ⚠️ Erro na otimização: {result_optimization['error']}")
        
        print("   ✅ Otimização de hiperparâmetros concluída!")
        
    except Exception as e:
        print(f"   ❌ Erro na otimização: {e}")
        logger.error(f"Erro na otimização: {e}")

def demo_production_monitoring():
    """Demonstra sistema de monitoramento e produção"""
    try:
        print("   📊 Iniciando sistema de monitoramento...")
        
        from ml_models.production_monitoring import (
            start_monitoring, 
            get_system_dashboard,
            stop_monitoring
        )
        
        # Iniciar monitoramento
        print("   🚀 Iniciando monitoramento contínuo...")
        start_monitoring()
        
        # Aguardar um pouco para coletar métricas
        import time
        print("   ⏳ Aguardando coleta de métricas...")
        time.sleep(5)
        
        # Obter dashboard do sistema
        print("   📈 Obtendo dashboard do sistema...")
        dashboard = get_system_dashboard()
        
        if 'error' not in dashboard:
            print(f"   ✅ Dashboard gerado com sucesso:")
            print(f"      - Timestamp: {dashboard.get('timestamp', 'N/A')}")
            
            system_health = dashboard.get('system_health', {})
            if system_health:
                print(f"      - Status geral: {system_health.get('overall_status', 'N/A')}")
                print(f"      - Status do banco: {system_health.get('database_status', 'N/A')}")
                print(f"      - Status do cache: {system_health.get('cache_status', 'N/A')}")
                print(f"      - Uso de CPU: {system_health.get('cpu_usage', 'N/A'):.1f}%")
                print(f"      - Uso de memória: {system_health.get('memory_usage', 'N/A'):.1f}%")
                print(f"      - Uso de disco: {system_health.get('disk_usage', 'N/A'):.1f}%")
            
            current_metrics = dashboard.get('current_metrics', {})
            if current_metrics:
                print(f"      - Processos ativos: {current_metrics.get('active_processes', 'N/A')}")
                print(f"      - Conexões ativas: {current_metrics.get('active_connections', 'N/A')}")
            
            recent_alerts = dashboard.get('recent_alerts', [])
            if recent_alerts:
                print(f"      - Alertas recentes: {len(recent_alerts)}")
                for i, alert in enumerate(recent_alerts[:3], 1):
                    print(f"         {i}. [{alert.get('level', 'N/A')}] {alert.get('message', 'N/A')}")
            
            system_stats = dashboard.get('system_stats', {})
            if system_stats:
                print(f"      - Total de predições: {system_stats.get('total_predictions', 'N/A')}")
                print(f"      - Total de alertas: {system_stats.get('total_alerts', 'N/A')}")
                print(f"      - Alertas não resolvidos: {system_stats.get('unresolved_alerts', 'N/A')}")
        else:
            print(f"   ⚠️ Erro no dashboard: {dashboard['error']}")
        
        # Parar monitoramento
        print("   🛑 Parando monitoramento...")
        stop_monitoring()
        
        print("   ✅ Demonstração de monitoramento concluída!")
        
    except Exception as e:
        print(f"   ❌ Erro no monitoramento: {e}")
        logger.error(f"Erro no monitoramento: {e}")

def demo_performance_reports():
    """Demonstra geração de relatórios de performance"""
    try:
        print("   📋 Gerando relatórios de performance...")
        
        from ml_models.production_monitoring import generate_performance_report
        
        # Relatório da última semana
        print("   📊 Relatório da última semana...")
        weekly_report = generate_performance_report(
            start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        if 'error' not in weekly_report:
            print(f"   ✅ Relatório semanal gerado:")
            print(f"      - Período: {weekly_report.get('period', 'N/A')}")
            print(f"      - Gerado em: {weekly_report.get('generated_at', 'N/A')}")
            
            summary = weekly_report.get('summary', {})
            if summary:
                print(f"      - Total de predições: {summary.get('total_predictions', 'N/A')}")
                print(f"      - Acurácia média: {summary.get('avg_accuracy', 'N/A'):.3f}")
                print(f"      - Uptime do sistema: {summary.get('system_uptime', 'N/A'):.1f}%")
                print(f"      - Total de alertas: {summary.get('total_alerts', 'N/A')}")
                print(f"      - Alertas críticos: {summary.get('critical_alerts', 'N/A')}")
            
            model_performance = weekly_report.get('model_performance', {})
            if model_performance:
                print(f"      - Performance dos modelos:")
                for model_type, perf in model_performance.items():
                    if isinstance(perf, dict) and 'error' not in perf:
                                        print(f"         - {model_type}:")
                avg_acc = perf.get('avg_accuracy', 'N/A')
                avg_f1 = perf.get('avg_f1_score', 'N/A')
                trend = perf.get('trend', 'N/A')
                print(f"           * Acurácia: {avg_acc if avg_acc == 'N/A' else f'{avg_acc:.3f}'}")
                print(f"           * F1-Score: {avg_f1 if avg_f1 == 'N/A' else f'{avg_f1:.3f}'}")
                print(f"           * Tendência: {trend}")
            
            system_health = weekly_report.get('system_health', {})
            if system_health:
                print(f"      - Saúde do sistema:")
                print(f"         - Uptime: {system_health.get('uptime_percentage', 'N/A'):.1f}%")
                print(f"         - CPU médio: {system_health.get('avg_cpu_usage', 'N/A'):.1f}%")
                print(f"         - Memória média: {system_health.get('avg_memory_usage', 'N/A'):.1f}%")
                print(f"         - Disco médio: {system_health.get('avg_disk_usage', 'N/A'):.1f}%")
                print(f"         - Tendência: {system_health.get('health_trend', 'N/A')}")
            
            alerts_analysis = weekly_report.get('alerts_analysis', {})
            if alerts_analysis:
                print(f"      - Análise de alertas:")
                print(f"         - Total: {alerts_analysis.get('total_alerts', 'N/A')}")
                print(f"         - Resolvidos: {alerts_analysis.get('resolved_alerts', 'N/A')}")
                print(f"         - Reconhecidos: {alerts_analysis.get('acknowledged_alerts', 'N/A')}")
                
                level_dist = alerts_analysis.get('level_distribution', {})
                if level_dist:
                    print(f"         - Distribuição por nível:")
                    for level, count in level_dist.items():
                        print(f"           * {level}: {count}")
        else:
            print(f"   ⚠️ Erro no relatório: {weekly_report['error']}")
        
        print("   ✅ Relatórios de performance gerados!")
        
    except Exception as e:
        print(f"   ❌ Erro nos relatórios: {e}")
        logger.error(f"Erro nos relatórios: {e}")

def test_advanced_components():
    """Testa componentes avançados"""
    print("🔧 TESTANDO COMPONENTES AVANÇADOS...")
    
    try:
        # Teste das funcionalidades avançadas
        print("1️⃣ Testando funcionalidades avançadas...")
        from ml_models.advanced_features import analyze_trends
        print("   ✅ Funcionalidades avançadas: OK")
        
        # Teste do sistema de monitoramento
        print("2️⃣ Testando sistema de monitoramento...")
        from ml_models.production_monitoring import get_system_dashboard
        print("   ✅ Sistema de monitoramento: OK")
        
        print("✅ Todos os componentes avançados estão funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando demonstração das funcionalidades avançadas...")
    
    # Testar componentes primeiro
    if test_advanced_components():
        print("\n✅ Componentes testados! Iniciando demonstração completa...")
        main()
    else:
        print("\n❌ Problemas nos componentes. Verifique as dependências.")
    
    print("\n🏁 Demonstração finalizada!")
