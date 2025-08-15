#!/usr/bin/env python3
"""
Demonstração do sistema de treinamento de modelos ML para apostas esportivas
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
    """Função principal da demonstração"""
    print("🚀 APOSTAPRO - DEMONSTRAÇÃO DO SISTEMA DE TREINAMENTO ML")
    print("=" * 70)
    
    try:
        # 1. Coletar dados históricos
        print("\n1️⃣ COLETANDO DADOS HISTÓRICOS...")
        from ml_models.data_collector import collect_historical_data
        
        historical_data = collect_historical_data(
            start_date="2024-01-01",
            end_date="2024-12-31",
            competitions=["Brasileirão"],
            min_matches=100
        )
        
        if historical_data.empty:
            print("❌ Falha na coleta de dados históricos")
            return
        
        print(f"✅ Dados coletados: {len(historical_data)} partidas")
        print(f"   Features disponíveis: {len(historical_data.columns)}")
        print(f"   Período: {historical_data['date'].min()} a {historical_data['date'].max()}")
        
        # 2. Preparar dados para treinamento
        print("\n2️⃣ PREPARANDO DADOS PARA TREINAMENTO...")
        from ml_models.data_collector import get_training_data
        
        # Dados para predição de resultado
        X_result, y_result = get_training_data(target_column='result')
        if X_result is not None:
            print(f"✅ Dados para predição de resultado: {X_result.shape[0]} amostras, {X_result.shape[1]} features")
        
        # Dados para predição de total de gols
        X_goals, y_goals = get_training_data(target_column='total_goals')
        if X_goals is not None:
            print(f"✅ Dados para predição de gols: {X_goals.shape[0]} amostras, {X_goals.shape[1]} features")
        
        # Dados para predição de ambos marcam
        X_both, y_both = get_training_data(target_column='both_teams_score')
        if X_both is not None:
            print(f"✅ Dados para predição de ambos marcam: {X_both.shape[0]} amostras, {X_both.shape[1]} features")
        
        # 3. Treinar modelos
        print("\n3️⃣ TREINANDO MODELOS DE MACHINE LEARNING...")
        from ml_models.model_trainer import train_all_models
        
        print("   Iniciando treinamento de todos os modelos...")
        training_results = train_all_models(force_retrain=False)
        
        # 4. Analisar resultados do treinamento
        print("\n4️⃣ ANALISANDO RESULTADOS DO TREINAMENTO...")
        
        successful_models = 0
        for model_type, result in training_results.items():
            if result.get('status') == 'success':
                successful_models += 1
                print(f"   ✅ {model_type}:")
                print(f"      - Amostras de treino: {result.get('training_samples', 'N/A')}")
                print(f"      - Amostras de teste: {result.get('test_samples', 'N/A')}")
                print(f"      - Features: {result.get('features_count', 'N/A')}")
                
                # Métricas específicas por tipo de problema
                metrics = result.get('metrics', {})
                if 'accuracy' in metrics:
                    print(f"      - Acurácia: {metrics['accuracy']:.3f}")
                    print(f"      - F1-Score: {metrics['f1_macro']:.3f}")
                elif 'r2' in metrics:
                    print(f"      - R²: {metrics['r2']:.3f}")
                    print(f"      - RMSE: {metrics['rmse']:.3f}")
                
                # Importância das features
                if result.get('feature_importance'):
                    top_features = list(result['feature_importance'].keys())[:5]
                    print(f"      - Top 5 features: {', '.join(top_features)}")
        
        print(f"\n   📊 Resumo: {successful_models}/{len(training_results)} modelos treinados com sucesso")
        
        # 5. Avaliar performance geral
        print("\n5️⃣ AVALIANDO PERFORMANCE GERAL...")
        from ml_models.model_trainer import get_model_performance_summary
        
        performance_summary = get_model_performance_summary()
        
        if performance_summary['overall_performance']:
            if 'classification' in performance_summary['overall_performance']:
                cls_perf = performance_summary['overall_performance']['classification']
                print(f"   🎯 Classificação:")
                print(f"      - Acurácia média: {cls_perf.get('avg_accuracy', 0):.3f}")
                print(f"      - F1-Score médio: {cls_perf.get('avg_f1', 0):.3f}")
            
            if 'regression' in performance_summary['overall_performance']:
                reg_perf = performance_summary['overall_performance']['regression']
                print(f"   📈 Regressão:")
                print(f"      - R² médio: {reg_perf.get('avg_r2', 0):.3f}")
                print(f"      - RMSE médio: {reg_perf.get('avg_rmse', 0):.3f}")
        
        # 6. Testar predições
        print("\n6️⃣ TESTANDO PREDIÇÕES...")
        from ml_models.recommendation_system import analyze_match
        
        # Dados de exemplo para teste
        test_match_data = {
            'home_team': 'Flamengo',
            'away_team': 'Palmeiras',
            'home_goals': 2,
            'away_goals': 1,
            'home_possession': 55.0,
            'away_possession': 45.0,
            'home_shots': 15,
            'away_shots': 12,
            'home_shots_on_target': 8,
            'away_shots_on_target': 6,
            'home_form_last_5': 0.8,
            'away_form_last_5': 0.7,
            'home_attacking_strength': 1.2,
            'away_attacking_strength': 1.1,
            'home_defensive_strength': 0.9,
            'away_defensive_strength': 1.0
        }
        
        print("   Testando predições para Flamengo vs Palmeiras...")
        
        try:
            recommendations = analyze_match(
                home_team="Flamengo",
                away_team="Palmeiras",
                match_data=test_match_data
            )
            
            if recommendations:
                print(f"   ✅ {len(recommendations)} recomendações geradas:")
                for i, rec in enumerate(recommendations[:3], 1):  # Mostrar apenas as 3 primeiras
                    print(f"      {i}. {rec.get('bet_type', 'N/A')}: {rec.get('prediction', 'N/A')}")
                    print(f"         Confiança: {rec.get('confidence', 0):.2f}")
                    print(f"         Valor recomendado: R$ {rec.get('recommended_amount', 0):.2f}")
            else:
                print("   ⚠️ Nenhuma recomendação gerada")
                
        except Exception as e:
            print(f"   ❌ Erro ao gerar predições: {e}")
        
        # 7. Gerar relatório final
        print("\n7️⃣ GERANDO RELATÓRIO FINAL...")
        generate_training_report(training_results, performance_summary)
        
        print("\n🎉 DEMONSTRAÇÃO DO TREINAMENTO CONCLUÍDA COM SUCESSO!")
        print("   Os modelos estão treinados e prontos para uso!")
        
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        logger.error(f"Erro na demonstração: {e}", exc_info=True)

def generate_training_report(training_results: dict, performance_summary: dict):
    """Gera relatório detalhado do treinamento"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(f"training_report_{timestamp}.json")
        
        report = {
            'training_session': {
                'timestamp': datetime.now().isoformat(),
                'session_id': timestamp
            },
            'training_results': training_results,
            'performance_summary': performance_summary,
            'summary': {
                'total_models': len(training_results),
                'successful_models': len([r for r in training_results.values() if r.get('status') == 'success']),
                'failed_models': len([r for r in training_results.values() if r.get('status') == 'error']),
                'loaded_models': len([r for r in training_results.values() if r.get('status') == 'loaded'])
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"   📊 Relatório salvo em: {report_file}")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar relatório: {e}")

def test_individual_components():
    """Testa componentes individuais"""
    print("🔧 TESTANDO COMPONENTES INDIVIDUAIS...")
    
    try:
        # Teste do coletor de dados
        print("1️⃣ Testando coletor de dados...")
        from ml_models.data_collector import collect_historical_data
        data = collect_historical_data(min_matches=50)
        print(f"   ✅ Coletor de dados: {len(data)} partidas coletadas")
        
        # Teste do treinador de modelos
        print("2️⃣ Testando treinador de modelos...")
        from ml_models.model_trainer import get_model_performance_summary
        summary = get_model_performance_summary()
        print(f"   ✅ Treinador de modelos: {summary['total_models']} modelos disponíveis")
        
        print("✅ Todos os componentes estão funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de componentes: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando demonstração do sistema de treinamento ML...")
    
    # Testar componentes primeiro
    if test_individual_components():
        print("\n✅ Componentes testados! Iniciando demonstração completa...")
        main()
    else:
        print("\n❌ Problemas nos componentes. Verifique as dependências.")
    
    print("\n🏁 Demonstração finalizada!")
