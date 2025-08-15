"""
Módulo de Treinamento de Modelos de Machine Learning
Responsável por treinar modelos de classificação para previsão de resultados de partidas
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
import logging
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TreinadorModeloML:
    def __init__(self, models_dir: str = 'ml_models/saved_models'):
        self.models_dir = models_dir
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.best_model = None
        self.best_model_name = None
        self.best_accuracy = 0.0
        
        # Criar diretório de modelos se não existir
        os.makedirs(models_dir, exist_ok=True)
    
    def _preparar_features_target(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara as features e target para treinamento
        
        Args:
            df: DataFrame com features e target
        
        Returns:
            Tuple com features (X) e target (y) preparados
        """
        # Separar features numéricas (excluir colunas de identificação e target)
        feature_columns = [
            'casa_forma_score', 'casa_vitorias', 'casa_empates', 'casa_derrotas',
            'casa_gols_marcados', 'casa_gols_sofridos', 'casa_sentimento', 'casa_confianca_sentimento',
            'visitante_forma_score', 'visitante_vitorias', 'visitante_empates', 'visitante_derrotas',
            'visitante_gols_marcados', 'visitante_gols_sofridos', 'visitante_sentimento', 'visitante_confianca_sentimento',
            'diferenca_forma', 'diferenca_sentimento'
        ]
        
        # Filtrar apenas colunas que existem no DataFrame
        available_features = [col for col in feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("Nenhuma feature válida encontrada no dataset")
        
        X = df[available_features].values
        y = df['resultado'].values
        
        # Codificar target (casa, visitante, empate)
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Normalizar features
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info(f"Features preparadas: {X_scaled.shape}")
        logger.info(f"Target codificado: {len(np.unique(y_encoded))} classes")
        
        return X_scaled, y_encoded
    
    def _treinar_random_forest(self, X: np.ndarray, y: np.ndarray) -> Tuple[RandomForestClassifier, float]:
        """Treina um modelo Random Forest"""
        logger.info("🌲 Treinando Random Forest...")
        
        # Parâmetros para Grid Search
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X, y)
        
        best_rf = grid_search.best_estimator_
        best_score = grid_search.best_score_
        
        logger.info(f"Random Forest - Melhor score CV: {best_score:.4f}")
        logger.info(f"Random Forest - Melhores parâmetros: {grid_search.best_params_}")
        
        return best_rf, best_score
    
    def _treinar_gradient_boosting(self, X: np.ndarray, y: np.ndarray) -> Tuple[GradientBoostingClassifier, float]:
        """Treina um modelo Gradient Boosting"""
        logger.info("🚀 Treinando Gradient Boosting...")
        
        # Parâmetros para Grid Search
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 0.9, 1.0]
        }
        
        gb = GradientBoostingClassifier(random_state=42)
        grid_search = GridSearchCV(gb, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X, y)
        
        best_gb = grid_search.best_estimator_
        best_score = grid_search.best_score_
        
        logger.info(f"Gradient Boosting - Melhor score CV: {best_score:.4f}")
        logger.info(f"Gradient Boosting - Melhores parâmetros: {grid_search.best_params_}")
        
        return best_gb, best_score
    
    def _treinar_logistic_regression(self, X: np.ndarray, y: np.ndarray) -> Tuple[LogisticRegression, float]:
        """Treina um modelo de Regressão Logística"""
        logger.info("📊 Treinando Regressão Logística...")
        
        # Parâmetros para Grid Search
        param_grid = {
            'C': [0.1, 1.0, 10.0, 100.0],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }
        
        lr = LogisticRegression(random_state=42, max_iter=1000)
        grid_search = GridSearchCV(lr, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X, y)
        
        best_lr = grid_search.best_estimator_
        best_score = grid_search.best_score_
        
        logger.info(f"Regressão Logística - Melhor score CV: {best_score:.4f}")
        logger.info(f"Regressão Logística - Melhores parâmetros: {grid_search.best_params_}")
        
        return best_lr, best_score
    
    def treinar_modelos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Treina múltiplos modelos e seleciona o melhor
        
        Args:
            df: DataFrame com features e target
        
        Returns:
            Dicionário com informações dos modelos treinados
        """
        logger.info("🎯 Iniciando treinamento de modelos...")
        
        # Preparar dados
        X, y = self._preparar_features_target(df)
        
        # Dividir em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Dados divididos: Treino {X_train.shape}, Teste {X_test.shape}")
        
        # Treinar modelos
        modelos_treinados = {}
        
        try:
            # Random Forest
            rf_model, rf_score = self._treinar_random_forest(X_train, y_train)
            rf_accuracy = rf_model.score(X_test, y_test)
            modelos_treinados['random_forest'] = {
                'modelo': rf_model,
                'score_cv': rf_score,
                'accuracy_teste': rf_accuracy
            }
            logger.info(f"Random Forest - Accuracy teste: {rf_accuracy:.4f}")
            
        except Exception as e:
            logger.error(f"Erro ao treinar Random Forest: {e}")
        
        try:
            # Gradient Boosting
            gb_model, gb_score = self._treinar_gradient_boosting(X_train, y_train)
            gb_accuracy = gb_model.score(X_test, y_test)
            modelos_treinados['gradient_boosting'] = {
                'modelo': rf_model,
                'score_cv': gb_score,
                'accuracy_teste': gb_accuracy
            }
            logger.info(f"Gradient Boosting - Accuracy teste: {gb_accuracy:.4f}")
            
        except Exception as e:
            logger.error(f"Erro ao treinar Gradient Boosting: {e}")
        
        try:
            # Regressão Logística
            lr_model, lr_score = self._treinar_logistic_regression(X_train, y_train)
            lr_accuracy = lr_model.score(X_test, y_test)
            modelos_treinados['logistic_regression'] = {
                'modelo': lr_model,
                'score_cv': lr_score,
                'accuracy_teste': lr_accuracy
            }
            logger.info(f"Regressão Logística - Accuracy teste: {lr_accuracy:.4f}")
            
        except Exception as e:
            logger.error(f"Erro ao treinar Regressão Logística: {e}")
        
        # Selecionar melhor modelo
        if modelos_treinados:
            melhor_modelo = max(modelos_treinados.items(), 
                              key=lambda x: x[1]['accuracy_teste'])
            
            self.best_model = melhor_modelo[1]['modelo']
            self.best_model_name = melhor_modelo[0]
            self.best_accuracy = melhor_modelo[1]['accuracy_teste']
            
            logger.info(f"🏆 Melhor modelo: {self.best_model_name} (Accuracy: {self.best_accuracy:.4f})")
            
            # Avaliação detalhada do melhor modelo
            y_pred = self.best_model.predict(X_test)
            y_pred_proba = self.best_model.predict_proba(X_test)
            
            logger.info("\n📈 Relatório de Classificação:")
            logger.info(classification_report(y_test, y_pred, 
                                           target_names=self.label_encoder.classes_))
            
            logger.info("\n🔢 Matriz de Confusão:")
            logger.info(confusion_matrix(y_test, y_pred))
            
            # Calcular probabilidades médias por classe
            probas_por_classe = {}
            for i, classe in enumerate(self.label_encoder.classes_):
                probas_por_classe[classe] = y_pred_proba[:, i].mean()
            
            logger.info("\n📊 Probabilidades médias por classe:")
            for classe, prob in probas_por_classe.items():
                logger.info(f"  {classe}: {prob:.4f}")
        
        return {
            'modelos_treinados': modelos_treinados,
            'melhor_modelo': self.best_model_name,
            'melhor_accuracy': self.best_accuracy,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': [col for col in df.columns if col not in ['partida_id', 'data_partida', 'resultado', 'gols_casa', 'gols_visitante', 'total_gols', 'ambas_marcam']]
        }
    
    def salvar_modelo(self, modelo_info: Dict[str, Any], nome_arquivo: str = None) -> str:
        """
        Salva o melhor modelo treinado
        
        Args:
            modelo_info: Informações do modelo treinado
            nome_arquivo: Nome do arquivo para salvar (opcional)
        
        Returns:
            Caminho do arquivo salvo
        """
        if not self.best_model:
            raise ValueError("Nenhum modelo treinado para salvar")
        
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"modelo_apostas_{self.best_model_name}_{timestamp}.joblib"
        
        caminho_completo = os.path.join(self.models_dir, nome_arquivo)
        
        # Salvar modelo e componentes necessários
        modelo_completo = {
            'modelo': self.best_model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': modelo_info['feature_names'],
            'accuracy': self.best_accuracy,
            'data_treinamento': datetime.now().isoformat(),
            'tipo_modelo': self.best_model_name
        }
        
        joblib.dump(modelo_completo, caminho_completo)
        
        logger.info(f"💾 Modelo salvo em: {caminho_completo}")
        
        # Salvar metadados
        metadados = {
            'nome_modelo': self.best_model_name,
            'accuracy': self.best_accuracy,
            'data_treinamento': datetime.now().isoformat(),
            'feature_names': modelo_info['feature_names'],
            'classes_target': self.label_encoder.classes_.tolist()
        }
        
        metadados_path = caminho_completo.replace('.joblib', '_metadata.json')
        import json
        with open(metadados_path, 'w') as f:
            json.dump(metadados, f, indent=2, default=str)
        
        logger.info(f"📋 Metadados salvos em: {metadados_path}")
        
        return caminho_completo
    
    def carregar_modelo(self, caminho_arquivo: str) -> Dict[str, Any]:
        """
        Carrega um modelo salvo
        
        Args:
            caminho_arquivo: Caminho para o arquivo do modelo
        
        Returns:
            Dicionário com o modelo e componentes
        """
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo de modelo não encontrado: {caminho_arquivo}")
        
        modelo_completo = joblib.load(caminho_arquivo)
        
        self.best_model = modelo_completo['modelo']
        self.best_model_name = modelo_completo['tipo_modelo']
        self.best_accuracy = modelo_completo['accuracy']
        self.scaler = modelo_completo['scaler']
        self.label_encoder = modelo_completo['label_encoder']
        
        logger.info(f"📥 Modelo carregado: {self.best_model_name}")
        logger.info(f"📊 Accuracy: {self.best_accuracy:.4f}")
        
        return modelo_completo

def main():
    """Função principal para demonstração"""
    from preparacao_dados import PreparadorDadosML
    
    print("🎯 Iniciando pipeline de treinamento ML...")
    
    # Preparar dados
    preparador = PreparadorDadosML()
    df = preparador.preparar_dataset_treinamento()
    
    if df.empty:
        print("❌ Não há dados suficientes para treinamento")
        return
    
    print(f"✅ Dataset preparado: {len(df)} registros")
    
    # Treinar modelos
    treinador = TreinadorModeloML()
    modelo_info = treinador.treinar_modelos(df)
    
    if treinador.best_model:
        # Salvar modelo
        caminho_modelo = treinador.salvar_modelo(modelo_info)
        print(f"💾 Modelo salvo em: {caminho_modelo}")
        
        print(f"\n🏆 Melhor modelo: {treinador.best_model_name}")
        print(f"📊 Accuracy: {treinador.best_accuracy:.4f}")
        
    else:
        print("❌ Falha no treinamento dos modelos")

if __name__ == "__main__":
    main()

