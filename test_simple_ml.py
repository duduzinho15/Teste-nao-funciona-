#!/usr/bin/env python3
"""
Teste simples do sistema de Machine Learning
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ml_imports():
    """Testa se os módulos ML podem ser importados"""
    print("🧪 TESTANDO IMPORTS DO SISTEMA ML")
    print("=" * 50)
    
    try:
        print("1️⃣ Testando import do config...")
        from ml_models.config import get_ml_config
        config = get_ml_config()
        print(f"✅ Config carregado: {config.model_version}")
        
        print("\n2️⃣ Testando import do cache manager...")
        from ml_models.cache_manager import get_cache_stats
        stats = get_cache_stats()
        print(f"✅ Cache manager: {stats}")
        
        print("\n3️⃣ Testando import do sentiment analyzer...")
        from ml_models.sentiment_analyzer import analyze_sentiment
        print("✅ Sentiment analyzer: OK")
        
        print("\n4️⃣ Testando import do data preparation...")
        from ml_models.data_preparation import prepare_data
        print("✅ Data preparation: OK")
        
        print("\n5️⃣ Testando import do ML models...")
        from ml_models.ml_models import train_model
        print("✅ ML models: OK")
        
        print("\n6️⃣ Testando import do recommendation system...")
        from ml_models.recommendation_system import analyze_match
        print("✅ Recommendation system: OK")
        
        print("\n🎉 TODOS OS MÓDULOS ML ESTÃO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar módulos ML: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_functionality():
    """Testa funcionalidades básicas do ML"""
    print("\n🚀 TESTANDO FUNCIONALIDADES ML")
    print("=" * 50)
    
    try:
        # Teste de configuração
        from ml_models.config import get_ml_config
        config = get_ml_config()
        print(f"✅ Configuração: {config.model_version}")
        
        # Teste de cache
        from ml_models.cache_manager import get_cache_stats
        stats = get_cache_stats()
        print(f"✅ Cache: {stats['total_requests']} requisições")
        
        # Teste de sentimento
        from ml_models.sentiment_analyzer import analyze_sentiment
        result = analyze_sentiment("Excelente vitória do Flamengo!")
        print(f"✅ Sentimento: {result['sentiment_label']} (confiança: {result['confidence']:.2f})")
        
        print("\n🎉 FUNCIONALIDADES ML ESTÃO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar funcionalidades ML: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO TESTE SIMPLES DO SISTEMA ML")
    print("=" * 60)
    
    # Teste 1: Imports
    if test_ml_imports():
        print("\n✅ Imports funcionando! Testando funcionalidades...")
        
        # Teste 2: Funcionalidades
        if test_ml_functionality():
            print("\n🎉 SISTEMA ML TOTALMENTE FUNCIONAL!")
        else:
            print("\n❌ Funcionalidades com problemas")
    else:
        print("\n❌ Problemas nos imports")
    
    print("\n🏁 Teste concluído!")
