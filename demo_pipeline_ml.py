"""
Demonstração do Pipeline de Machine Learning Completo
Testa todas as fases: preparação de dados, treinamento e geração de recomendações

Este script é voltado para demonstrações e testes locais. Para executar o
workflow completo em produção, utilize `executar_workflow_ml.py`.
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal de demonstração"""
    print("🚀 INICIANDO DEMONSTRAÇÃO DO PIPELINE ML COMPLETO")
    print("=" * 60)
    
    try:
        # FASE 1: Preparação de Dados
        print("\n📊 FASE 1: PREPARAÇÃO DE DADOS")
        print("-" * 40)
        
        from Coleta_de_dados.ml.preparacao_dados import PreparadorDadosML
        
        preparador = PreparadorDadosML()
        print("🔄 Preparando dataset de treinamento...")
        
        # Usar período menor para demonstração
        data_inicio = datetime.now() - timedelta(days=60)
        df = preparador.preparar_dataset_treinamento(data_inicio, datetime.now())
        
        if df.empty:
            print("❌ Não há dados suficientes para treinamento")
            print("💡 Dica: Execute primeiro o script de inserção de dados de teste")
            return
        
        print(f"✅ Dataset preparado com sucesso!")
        print(f"📊 Registros: {len(df)}")
        print(f"🔢 Features: {len(df.columns)}")
        print(f"🎯 Target 'resultado' distribuído:")
        print(df['resultado'].value_counts())
        
        # Salvar dataset
        filename = preparador.salvar_dataset(df)
        print(f"💾 Dataset salvo em: {filename}")
        
        # FASE 2: Treinamento de Modelos
        print("\n🎯 FASE 2: TREINAMENTO DE MODELOS")
        print("-" * 40)
        
        from Coleta_de_dados.ml.treinamento import TreinadorModeloML
        
        treinador = TreinadorModeloML()
        print("🔄 Iniciando treinamento de modelos...")
        
        modelo_info = treinador.treinar_modelos(df)
        
        if not treinador.best_model:
            print("❌ Falha no treinamento dos modelos")
            return
        
        # Salvar modelo
        caminho_modelo = treinador.salvar_modelo(modelo_info)
        print(f"💾 Modelo salvo em: {caminho_modelo}")
        
        print(f"\n🏆 Melhor modelo: {treinador.best_model_name}")
        print(f"📊 Accuracy: {treinador.best_accuracy:.4f}")
        
        # FASE 3: Geração de Recomendações
        print("\n🎲 FASE 3: GERAÇÃO DE RECOMENDAÇÕES")
        print("-" * 40)
        
        from Coleta_de_dados.ml.gerar_recomendacoes import GeradorRecomendacoes
        
        gerador = GeradorRecomendacoes()
        print("🔄 Carregando modelo treinado...")
        
        if not gerador.carregar_ultimo_modelo():
            print("❌ Falha ao carregar modelo")
            return
        
        print("🔄 Gerando recomendações para partidas futuras...")
        recomendacoes = gerador.gerar_recomendacoes_partidas_futuras(dias_futuros=7)
        
        if recomendacoes:
            print(f"\n✅ Recomendações geradas com sucesso!")
            print(f"📊 Total de partidas processadas: {len(recomendacoes)}")
            
            # Mostrar algumas recomendações
            for rec in recomendacoes[:3]:
                print(f"\n🏆 {rec['time_casa']} vs {rec['time_visitante']}")
                print(f"📅 {rec['data_partida']}")
                for mercado_rec in rec['recomendacoes']:
                    print(f"  {mercado_rec['mercado']}: {mercado_rec['previsao']} "
                          f"(Prob: {mercado_rec['probabilidade']:.2%}, "
                          f"Odd: {mercado_rec['odd_justa']:.2f})")
            
            # Buscar recomendações existentes
            print(f"\n📋 Recomendações existentes no banco:")
            existentes = gerador.obter_recomendacoes_existentes()
            print(f"Total: {len(existentes)} recomendações")
            
        else:
            print("⚠️  Nenhuma recomendação foi gerada (pode não haver partidas futuras)")
        
        # RELATÓRIO FINAL
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"✅ Dataset preparado: {len(df)} registros")
        print(f"✅ Modelo treinado: {treinador.best_model_name} (Accuracy: {treinador.best_accuracy:.4f})")
        print(f"✅ Recomendações geradas: {len(recomendacoes)} partidas processadas")
        print(f"✅ Pipeline ML funcionando perfeitamente!")
        
        print("\n🚀 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("1. Integrar com API FastAPI para expor recomendações")
        print("2. Implementar monitoramento de performance dos modelos")
        print("3. Criar dashboard para visualização das recomendações")
        print("4. Implementar retreinamento automático dos modelos")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se todas as dependências estão instaladas")
        print("   pip install pandas numpy scikit-learn joblib")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        logger.exception("Erro detalhado:")

if __name__ == "__main__":
    main()

