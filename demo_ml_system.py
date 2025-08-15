#!/usr/bin/env python3
"""
Demonstração completa do sistema de Machine Learning do ApostaPro
"""

import logging
import json
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal de demonstração"""
    print("🚀 APOSTAPRO - SISTEMA DE MACHINE LEARNING")
    print("=" * 50)
    
    try:
        # 1. Testar sistema de configuração
        print("\n1️⃣ Testando sistema de configuração...")
        from ml_models.config import get_ml_config, update_ml_config
        
        config = get_ml_config()
        print(f"✅ Configuração carregada: {config.model_version}")
        print(f"   - Threshold de confiança: {config.confidence_threshold}")
        print(f"   - Cache habilitado: {config.enable_caching}")
        
        # 2. Testar sistema de cache
        print("\n2️⃣ Testando sistema de cache...")
        from ml_models.cache_manager import get_cache_stats, clear_ml_cache
        
        cache_stats = get_cache_stats()
        print(f"✅ Cache funcionando: {cache_stats['total_requests']} requisições")
        print(f"   - Hit rate: {cache_stats['hit_rate']}%")
        
        # 3. Testar análise de sentimento
        print("\n3️⃣ Testando análise de sentimento...")
        from ml_models.sentiment_analyzer import analyze_sentiment, analyze_sentiments_batch
        
        test_texts = [
            "Excelente vitória do Flamengo! Gol espetacular do Gabigol!",
            "Derrota amarga para o Palmeiras. O time jogou muito mal.",
            "Empate justo entre Corinthians e São Paulo. Bom jogo das duas equipes.",
            "Vasco vence e se aproxima da liderança. Momentos de alegria para a torcida!",
            "Atlético-MG perde em casa. Preocupação com a defesa do time."
        ]
        
        print("   Analisando textos de exemplo...")
        for i, text in enumerate(test_texts, 1):
            result = analyze_sentiment(text)
            print(f"   {i}. '{text[:50]}...' → {result['sentiment_label']} (confiança: {result['confidence']:.2f})")
        
        # 4. Testar sistema de recomendações
        print("\n4️⃣ Testando sistema de recomendações...")
        from ml_models.recommendation_system import analyze_match, generate_predictions, get_betting_recommendations
        
        # Dados de exemplo para uma partida
        match_data = {
            "match_id": "demo_001",
            "home_team": "Flamengo",
            "away_team": "Palmeiras",
            "competition": "Brasileirão 2025",
            "match_date": "2025-01-15",
            "home_goals_scored": 2.3,
            "away_goals_scored": 1.8,
            "home_goals_conceded": 1.1,
            "away_goals_conceded": 1.4,
            "home_shots": 12.5,
            "away_shots": 10.2,
            "home_possession": 55.0,
            "away_possession": 45.0,
            "home_recent_form": ["W", "W", "D", "W", "W"],
            "away_recent_form": ["L", "W", "W", "D", "L"],
            "news_sentiment": "Flamengo em excelente fase, expectativa muito positiva para a partida em casa."
        }
        
        print("   Analisando partida de exemplo...")
        analysis = analyze_match(match_data)
        print(f"   ✅ Análise concluída para {analysis['home_team']} vs {analysis['away_team']}")
        
        print("   Gerando previsões...")
        predictions = generate_predictions(analysis)
        print(f"   ✅ Previsões geradas: {len(predictions['predictions'])} tipos de aposta")
        
        print("   Gerando recomendações...")
        recommendations = get_betting_recommendations(predictions, "medium", 3)
        print(f"   ✅ Recomendações geradas: {len(recommendations)} apostas recomendadas")
        
        # Mostrar recomendações
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['bet_type']}: {rec['prediction']} (confiança: {rec['confidence']:.2f})")
            print(f"      Valor recomendado: R$ {rec['recommended_bet_amount']:.2f}")
        
        # 5. Testar sistema de dados
        print("\n5️⃣ Testando sistema de preparação de dados...")
        from ml_models.data_preparation import DataPreparationPipeline
        
        data_pipeline = DataPreparationPipeline()
        print(f"✅ Pipeline de dados inicializado")
        print(f"   - Diretório de modelos: {data_pipeline.models_dir}")
        
        # 6. Testar sistema de modelos
        print("\n6️⃣ Testando sistema de modelos...")
        from ml_models.ml_models import MLModelManager
        
        ml_manager = MLModelManager()
        print(f"✅ Gerenciador de modelos inicializado")
        print(f"   - Modelos disponíveis: {len(ml_manager.base_models)} tipos")
        
        # 7. Gerar relatório final
        print("\n7️⃣ Gerando relatório final...")
        generate_final_report(analysis, predictions, recommendations)
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("O sistema de Machine Learning está funcionando perfeitamente!")
        
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"\n❌ Erro na demonstração: {e}")
        print("Verifique se todas as dependências estão instaladas corretamente.")

def generate_final_report(analysis, predictions, recommendations):
    """Gera um relatório final da demonstração"""
    report = {
        "demonstracao": {
            "data": datetime.now().isoformat(),
            "versao": "1.0.0",
            "status": "sucesso"
        },
        "analise_partida": {
            "home_team": analysis['home_team'],
            "away_team": analysis['away_team'],
            "competition": analysis['competition'],
            "features_extraidas": len(analysis['features'].get('numeric', {}))
        },
        "previsoes": {
            "total_tipos": len(predictions['predictions']),
            "tipos_disponiveis": list(predictions['predictions'].keys())
        },
        "recomendacoes": {
            "total": len(recommendations),
            "por_tipo": {}
        }
    }
    
    # Contar recomendações por tipo
    for rec in recommendations:
        bet_type = rec['bet_type']
        if bet_type not in report['recomendacoes']['por_tipo']:
            report['recomendacoes']['por_tipo'][bet_type] = 0
        report['recomendacoes']['por_tipo'][bet_type] += 1
    
    # Salvar relatório
    report_file = Path("demo_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"   📊 Relatório salvo em: {report_file}")
    
    # Mostrar resumo
    print(f"\n📈 RESUMO DA DEMONSTRAÇÃO:")
    print(f"   - Partida analisada: {analysis['home_team']} vs {analysis['away_team']}")
    print(f"   - Features extraídas: {report['analise_partida']['features_extraidas']}")
    print(f"   - Tipos de previsão: {report['previsoes']['total_tipos']}")
    print(f"   - Recomendações geradas: {report['recomendacoes']['total']}")

def test_individual_components():
    """Testa componentes individuais do sistema"""
    print("\n🔧 TESTANDO COMPONENTES INDIVIDUAIS...")
    
    try:
        # Testar configuração
        from ml_models.config import get_ml_config
        config = get_ml_config()
        print("✅ Configuração: OK")
        
        # Testar cache
        from ml_models.cache_manager import get_cache_stats
        stats = get_cache_stats()
        print("✅ Cache Manager: OK")
        
        # Testar sentimento
        from ml_models.sentiment_analyzer import analyze_sentiment
        result = analyze_sentiment("Teste")
        print("✅ Sentiment Analyzer: OK")
        
        # Testar pipeline de dados
        from ml_models.data_preparation import DataPreparationPipeline
        pipeline = DataPreparationPipeline()
        print("✅ Data Pipeline: OK")
        
        # Testar modelos
        from ml_models.ml_models import MLModelManager
        manager = MLModelManager()
        print("✅ ML Models: OK")
        
        # Testar recomendações
        from ml_models.recommendation_system import BettingRecommendationSystem
        rec_system = BettingRecommendationSystem()
        print("✅ Recommendation System: OK")
        
        print("\n🎯 TODOS OS COMPONENTES ESTÃO FUNCIONANDO!")
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes: {e}")

if __name__ == "__main__":
    print("Iniciando demonstração do sistema de ML...")
    
    # Testar componentes individuais primeiro
    test_individual_components()
    
    # Executar demonstração completa
    main()
    
    print("\n🏁 Demonstração finalizada!")
    print("Para mais informações, consulte a documentação da API em /ml/status")
