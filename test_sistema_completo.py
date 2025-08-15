#!/usr/bin/env python3
"""
Script de Teste Completo do Sistema ApostaPro
"""

import asyncio
import sys
import traceback

def test_ml_system():
    """Testa o sistema de Machine Learning"""
    print("🔍 Testando Sistema de Machine Learning...")
    try:
        from ml_models import test_ml_system, get_ml_system_info
        
        # Teste básico
        result = test_ml_system()
        print(f"✅ Teste ML: {result['message']}")
        
        # Informações do sistema
        info = get_ml_system_info()
        print(f"📊 Versão: {info['version']}")
        print(f"📊 Componentes: {len(info['components'])} módulos")
        
        # Teste de análise de sentimento
        from ml_models import analyze_sentiment
        sentiment_result = analyze_sentiment("Excelente vitória do time!")
        print(f"📊 Análise de Sentimento: {sentiment_result['sentiment_label']}")
        
        # Teste de cache
        from ml_models import get_cache_stats
        cache_stats = get_cache_stats()
        print(f"📊 Cache: {cache_stats['hits']} hits, {cache_stats['misses']} misses")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Sistema ML: {e}")
        traceback.print_exc()
        return False

def test_rapidapi_system():
    """Testa o sistema de APIs RapidAPI"""
    print("\n🔍 Testando Sistema de APIs RapidAPI...")
    try:
        # Teste de importação
        from Coleta_de_dados.apis.rapidapi.base_rapidapi import RapidAPIBase
        print("✅ RapidAPIBase importado")
        
        from Coleta_de_dados.apis.rapidapi.performance_monitor import get_performance_monitor
        print("✅ Performance Monitor importado")
        
        from Coleta_de_dados.apis.rapidapi.fallback_manager import get_fallback_manager
        print("✅ Fallback Manager importado")
        
        from Coleta_de_dados.apis.rapidapi.notification_system import get_notification_manager
        print("✅ Notification System importado")
        
        from Coleta_de_dados.apis.rapidapi.web_dashboard import RapidAPIDashboard
        print("✅ Web Dashboard importado")
        
        # Teste de configuração do dashboard
        from Coleta_de_dados.apis.rapidapi.web_dashboard import DashboardConfig
        config = DashboardConfig()
        print(f"📊 Dashboard configurado para porta {config.port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Sistema RapidAPI: {e}")
        traceback.print_exc()
        return False

def test_api_classes():
    """Testa as classes de API específicas"""
    print("\n🔍 Testando Classes de API...")
    try:
        # Teste Today Football Prediction
        from Coleta_de_dados.apis.rapidapi.today_football_prediction import TodayFootballPredictionAPI
        print("✅ TodayFootballPredictionAPI importada")
        
        # Teste Soccer Football Info
        from Coleta_de_dados.apis.rapidapi.soccer_football_info import SoccerFootballInfoAPI
        print("✅ SoccerFootballInfoAPI importada")
        
        # Teste Sportspage Feeds
        from Coleta_de_dados.apis.rapidapi.sportspage_feeds import SportspageFeedsAPI
        print("✅ SportspageFeedsAPI importada")
        
        # Teste Football Prediction
        from Coleta_de_dados.apis.rapidapi.football_prediction import FootballPredictionAPI
        print("✅ FootballPredictionAPI importada")
        
        # Teste Pinnacle Odds
        from Coleta_de_dados.apis.rapidapi.pinnacle_odds import PinnacleOddsAPI
        print("✅ PinnacleOddsAPI importada")
        
        # Teste Football Pro
        from Coleta_de_dados.apis.rapidapi.football_pro import FootballProAPI
        print("✅ FootballProAPI importada")
        
        # Teste SportAPI7
        from Coleta_de_dados.apis.rapidapi.sportapi7 import SportAPI7
        print("✅ SportAPI7 importada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas Classes de API: {e}")
        traceback.print_exc()
        return False

def test_ml_modules():
    """Testa os módulos específicos de ML"""
    print("\n🔍 Testando Módulos de ML...")
    try:
        # Teste Sentiment Analyzer
        from ml_models.sentiment_analyzer import SentimentAnalyzer
        print("✅ SentimentAnalyzer importado")
        
        # Teste Data Preparation
        from ml_models.data_preparation import DataPreparationPipeline
        print("✅ DataPreparationPipeline importado")
        
        # Teste ML Models
        from ml_models.ml_models import MLModelManager
        print("✅ MLModelManager importado")
        
        # Teste Recommendation System
        from ml_models.recommendation_system import BettingRecommendationSystem
        print("✅ BettingRecommendationSystem importado")
        
        # Teste Data Collector
        from ml_models.data_collector import HistoricalDataCollector
        print("✅ HistoricalDataCollector importado")
        
        # Teste Model Trainer
        from ml_models.model_trainer import ModelTrainer
        print("✅ ModelTrainer importado")
        
        # Teste Database Integration
        from ml_models.database_integration import DatabaseIntegration
        print("✅ DatabaseIntegration importado")
        
        # Teste Cache Manager
        from ml_models.cache_manager import cache_result, timed_cache_result
        print("✅ Cache Manager importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos Módulos de ML: {e}")
        traceback.print_exc()
        return False

def test_demo_files():
    """Testa os arquivos de demonstração"""
    print("\n🔍 Testando Arquivos de Demonstração...")
    try:
        # Teste demo_ml_system
        import ast
        with open('demo_ml_system.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_ml_system.py sintaticamente válido")
        
        # Teste demo_advanced_features
        with open('demo_advanced_features.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_advanced_features.py sintaticamente válido")
        
        # Teste demo_web_dashboard
        with open('demo_web_dashboard.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_web_dashboard.py sintaticamente válido")
        
        # Teste demo_kubernetes_orchestration
        with open('demo_kubernetes_orchestration.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_kubernetes_orchestration.py sintaticamente válido")
        
        # Teste demo_automation_pipeline
        with open('demo_automation_pipeline.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_automation_pipeline.py sintaticamente válido")
        
        # Teste demo_betting_apis
        with open('demo_betting_apis.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_betting_apis.py sintaticamente válido")
        
        # Teste demo_training_ml
        with open('demo_training_ml.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_training_ml.py sintaticamente válido")
        
        # Teste demo_pipeline_ml
        with open('demo_pipeline_ml.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ demo_pipeline_ml.py sintaticamente válido")
        
        # Teste executar_workflow_ml
        with open('executar_workflow_ml.py', 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ executar_workflow_ml.py sintaticamente válido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos Arquivos de Demonstração: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA APOSTAPRO")
    print("=" * 60)
    
    results = []
    
    # Teste Sistema ML
    results.append(("Sistema ML", test_ml_system()))
    
    # Teste Sistema RapidAPI
    results.append(("Sistema RapidAPI", test_rapidapi_system()))
    
    # Teste Classes de API
    results.append(("Classes de API", test_api_classes()))
    
    # Teste Módulos de ML
    results.append(("Módulos de ML", test_ml_modules()))
    
    # Teste Arquivos de Demonstração
    results.append(("Arquivos de Demonstração", test_demo_files()))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if failed_tests == 0:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente.")
        return True
    else:
        print(f"⚠️  {failed_tests} teste(s) falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
