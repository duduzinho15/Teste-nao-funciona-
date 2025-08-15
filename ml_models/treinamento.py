#!/usr/bin/env python3
"""
Módulo de treinamento de modelos de Machine Learning para previsão de apostas esportivas.
Inclui treinamento de modelos para diferentes tipos de apostas: 1X2, Over/Under, Ambos Marcam.
"""

import pandas as pd
import numpy as np
import logging
import pickle
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TreinadorModelosML:
    """Treinador de modelos de Machine Learning para apostas esportivas."""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Inicializa o treinador de modelos.
        
        Args:
            dataset_path: Caminho para o dataset de treinamento
        """
        self.dataset_path = dataset_path or 'dataset_treinamento_ml.csv'
        self.dataset = None
        self.modelos = {}
        self.scalers = {}
        self.label_encoders = {}
        self.metricas = {}
        
        # Configurações dos modelos
        self.configuracoes_modelos = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'gradient_boosting': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            },
            'xgboost': {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            },
            'logistic_regression': {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        }
        
        logger.info("🤖 Treinador de modelos ML inicializado")
    
    def carregar_dataset(self) -> bool:
        """
        Carrega o dataset de treinamento.
        
        Returns:
            True se o dataset foi carregado com sucesso
        """
        try:
            if not os.path.exists(self.dataset_path):
                logger.error(f"❌ Dataset não encontrado: {self.dataset_path}")
                return False
            
            self.dataset = pd.read_csv(self.dataset_path)
            logger.info(f"✅ Dataset carregado: {self.dataset.shape}")
            logger.info(f"📊 Colunas: {list(self.dataset.columns)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dataset: {e}")
            return False
    
    def preparar_dados_treinamento(self) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """
        Prepara os dados para treinamento dos modelos.
        
        Returns:
            Tuple com features e targets para cada tipo de aposta
        """
        try:
            if self.dataset is None:
                logger.error("❌ Dataset não carregado")
                return pd.DataFrame(), {}
            
            logger.info("🔧 Preparando dados para treinamento...")
            
            # Remove colunas não úteis para ML
            colunas_remover = ['partida_id', 'data_partida', 'clube_casa_id', 'clube_visitante_id', 'competicao_id']
            colunas_features = [col for col in self.dataset.columns if col not in colunas_remover and not col.startswith('target_')]
            
            # Features para treinamento
            X = self.dataset[colunas_features].copy()
            
            # Targets para cada tipo de aposta
            targets = {
                'resultado_1x2': self.dataset['target_resultado'],
                'over_under_2_5': self.dataset['target_total_gols'].apply(lambda x: 'over' if x > 2.5 else 'under'),
                'ambos_marcam': self.dataset['target_ambos_marcam']
            }
            
            # Remove linhas com valores nulos
            X = X.dropna()
            for target_name, target_values in targets.items():
                targets[target_name] = target_values[X.index]
            
            # Remove linhas com valores infinitos
            X = X.replace([np.inf, -np.inf], np.nan).dropna()
            for target_name, target_values in targets.items():
                targets[target_name] = target_values[X.index]
            
            logger.info(f"✅ Dados preparados: {X.shape[0]} amostras, {X.shape[1]} features")
            
            return X, targets
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar dados: {e}")
            return pd.DataFrame(), {}
    
    def treinar_modelo_resultado_1x2(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Treina modelo para prever resultado da partida (1X2).
        
        Args:
            X: Features para treinamento
            y: Target (resultado da partida)
            
        Returns:
            Dicionário com informações do modelo treinado
        """
        try:
            logger.info("🏆 Treinando modelo para resultado 1X2...")
            
            # Codifica o target
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            self.label_encoders['resultado_1x2'] = le
            
            # Divide dados em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Escala as features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers['resultado_1x2'] = scaler
            
            # Lista de modelos para testar
            modelos = {
                'Random Forest': RandomForestClassifier(random_state=42, n_jobs=-1),
                'Gradient Boosting': GradientBoostingClassifier(random_state=42),
                'XGBoost': xgb.XGBClassifier(random_state=42, n_jobs=-1),
                'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            melhor_modelo = None
            melhor_score = 0
            resultados_modelos = {}
            
            # Testa cada modelo
            for nome, modelo in modelos.items():
                logger.info(f"🔍 Testando {nome}...")
                
                # Treina o modelo
                modelo.fit(X_train_scaled, y_train)
                
                # Faz predições
                y_pred = modelo.predict(X_test_scaled)
                y_pred_proba = modelo.predict_proba(X_test_scaled)
                
                # Calcula métricas
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                
                resultados_modelos[nome] = {
                    'modelo': modelo,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'roc_auc': roc_auc
                }
                
                logger.info(f"   📊 {nome}: Accuracy={accuracy:.4f}, F1={f1:.4f}, ROC AUC={roc_auc:.4f}")
                
                # Atualiza melhor modelo
                if f1 > melhor_score:
                    melhor_score = f1
                    melhor_modelo = nome
            
            # Seleciona o melhor modelo
            modelo_final = resultados_modelos[melhor_modelo]['modelo']
            self.modelos['resultado_1x2'] = modelo_final
            
            # Salva métricas
            self.metricas['resultado_1x2'] = resultados_modelos[melhor_modelo]
            
            logger.info(f"🏆 Melhor modelo para resultado 1X2: {melhor_modelo}")
            logger.info(f"📊 Métricas finais: F1={melhor_score:.4f}")
            
            return {
                'melhor_modelo': melhor_modelo,
                'metricas': resultados_modelos[melhor_modelo],
                'todos_modelos': resultados_modelos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo resultado 1X2: {e}")
            return {}
    
    def treinar_modelo_over_under(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Treina modelo para prever Over/Under 2.5 gols.
        
        Args:
            X: Features para treinamento
            y: Target (over/under)
            
        Returns:
            Dicionário com informações do modelo treinado
        """
        try:
            logger.info("⚽ Treinando modelo para Over/Under 2.5...")
            
            # Codifica o target
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            self.label_encoders['over_under_2_5'] = le
            
            # Divide dados em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
            )
            
            # Escala as features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers['over_under_2_5'] = scaler
            
            # Lista de modelos para testar
            modelos = {
                'Random Forest': RandomForestClassifier(random_state=42, n_jobs=-1),
                'Gradient Boosting': GradientBoostingClassifier(random_state=42),
                'XGBoost': xgb.XGBClassifier(random_state=42, n_jobs=-1),
                'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            melhor_modelo = None
            melhor_score = 0
            resultados_modelos = {}
            
            # Testa cada modelo
            for nome, modelo in modelos.items():
                logger.info(f"🔍 Testando {nome}...")
                
                # Treina o modelo
                modelo.fit(X_train_scaled, y_train)
                
                # Faz predições
                y_pred = modelo.predict(X_test_scaled)
                y_pred_proba = modelo.predict_proba(X_test_scaled)
                
                # Calcula métricas
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
                
                resultados_modelos[nome] = {
                    'modelo': modelo,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'roc_auc': roc_auc
                }
                
                logger.info(f"   📊 {nome}: Accuracy={accuracy:.4f}, F1={f1:.4f}, ROC AUC={roc_auc:.4f}")
                
                # Atualiza melhor modelo
                if f1 > melhor_score:
                    melhor_score = f1
                    melhor_modelo = nome
            
            # Seleciona o melhor modelo
            modelo_final = resultados_modelos[melhor_modelo]['modelo']
            self.modelos['over_under_2_5'] = modelo_final
            
            # Salva métricas
            self.metricas['over_under_2_5'] = resultados_modelos[melhor_modelo]
            
            logger.info(f"⚽ Melhor modelo para Over/Under: {melhor_modelo}")
            logger.info(f"📊 Métricas finais: F1={melhor_score:.4f}")
            
            return {
                'melhor_modelo': melhor_modelo,
                'metricas': resultados_modelos[melhor_modelo],
                'todos_modelos': resultados_modelos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo Over/Under: {e}")
            return {}
    
    def treinar_modelo_ambos_marcam(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Treina modelo para prever se ambos os times marcam.
        
        Args:
            X: Features para treinamento
            y: Target (ambos marcam: 0 ou 1)
            
        Returns:
            Dicionário com informações do modelo treinado
        """
        try:
            logger.info("🎯 Treinando modelo para Ambos Marcam...")
            
            # Divide dados em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Escala as features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers['ambos_marcam'] = scaler
            
            # Lista de modelos para testar
            modelos = {
                'Random Forest': RandomForestClassifier(random_state=42, n_jobs=-1),
                'Gradient Boosting': GradientBoostingClassifier(random_state=42),
                'XGBoost': xgb.XGBClassifier(random_state=42, n_jobs=-1),
                'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
            }
            
            melhor_modelo = None
            melhor_score = 0
            resultados_modelos = {}
            
            # Testa cada modelo
            for nome, modelo in modelos.items():
                logger.info(f"🔍 Testando {nome}...")
                
                # Treina o modelo
                modelo.fit(X_train_scaled, y_train)
                
                # Faz predições
                y_pred = modelo.predict(X_test_scaled)
                y_pred_proba = modelo.predict_proba(X_test_scaled)
                
                # Calcula métricas
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                roc_auc = roc_auc_score(y_test, y_pred_proba[:, 1])  # Probabilidade da classe positiva
                
                resultados_modelos[nome] = {
                    'modelo': modelo,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'roc_auc': roc_auc
                }
                
                logger.info(f"   📊 {nome}: Accuracy={accuracy:.4f}, F1={f1:.4f}, ROC AUC={roc_auc:.4f}")
                
                # Atualiza melhor modelo
                if f1 > melhor_score:
                    melhor_score = f1
                    melhor_modelo = nome
            
            # Seleciona o melhor modelo
            modelo_final = resultados_modelos[melhor_modelo]['modelo']
            self.modelos['ambos_marcam'] = modelo_final
            
            # Salva métricas
            self.metricas['ambos_marcam'] = resultados_modelos[melhor_modelo]
            
            logger.info(f"🎯 Melhor modelo para Ambos Marcam: {melhor_modelo}")
            logger.info(f"📊 Métricas finais: F1={melhor_score:.4f}")
            
            return {
                'melhor_modelo': melhor_modelo,
                'metricas': resultados_modelos[melhor_modelo],
                'todos_modelos': resultados_modelos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo Ambos Marcam: {e}")
            return {}
    
    def treinar_todos_modelos(self) -> Dict[str, Any]:
        """
        Treina todos os modelos para os diferentes tipos de apostas.
        
        Returns:
            Dicionário com resultados de todos os treinamentos
        """
        try:
            logger.info("🚀 Iniciando treinamento de todos os modelos...")
            
            # Carrega dataset se necessário
            if self.dataset is None:
                if not self.carregar_dataset():
                    return {}
            
            # Prepara dados
            X, targets = self.preparar_dados_treinamento()
            if X.empty:
                return {}
            
            resultados = {}
            
            # Treina modelo para resultado 1X2
            if 'target_resultado' in targets:
                resultados['resultado_1x2'] = self.treinar_modelo_resultado_1x2(X, targets['target_resultado'])
            
            # Treina modelo para Over/Under
            if 'over_under_2_5' in targets:
                resultados['over_under_2_5'] = self.treinar_modelo_over_under(X, targets['over_under_2_5'])
            
            # Treina modelo para Ambos Marcam
            if 'ambos_marcam' in targets:
                resultados['ambos_marcam'] = self.treinar_modelo_ambos_marcam(X, targets['ambos_marcam'])
            
            logger.info("✅ Treinamento de todos os modelos concluído!")
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento geral: {e}")
            return {}
    
    def salvar_modelos(self, diretorio: str = 'modelos_treinados') -> bool:
        """
        Salva todos os modelos treinados em arquivos.
        
        Args:
            diretorio: Diretório para salvar os modelos
            
        Returns:
            True se todos os modelos foram salvos com sucesso
        """
        try:
            # Cria diretório se não existir
            os.makedirs(diretorio, exist_ok=True)
            
            # Salva modelos
            for nome_tipo, modelo in self.modelos.items():
                caminho_modelo = os.path.join(diretorio, f'{nome_tipo}_modelo.pkl')
                with open(caminho_modelo, 'wb') as f:
                    pickle.dump(modelo, f)
                logger.info(f"💾 Modelo {nome_tipo} salvo em: {caminho_modelo}")
            
            # Salva scalers
            for nome_tipo, scaler in self.scalers.items():
                caminho_scaler = os.path.join(diretorio, f'{nome_tipo}_scaler.pkl')
                with open(caminho_scaler, 'wb') as f:
                    pickle.dump(scaler, f)
                logger.info(f"💾 Scaler {nome_tipo} salvo em: {caminho_scaler}")
            
            # Salva label encoders
            for nome_tipo, le in self.label_encoders.items():
                caminho_le = os.path.join(diretorio, f'{nome_tipo}_label_encoder.pkl')
                with open(caminho_le, 'wb') as f:
                    pickle.dump(le, f)
                logger.info(f"💾 Label Encoder {nome_tipo} salvo em: {caminho_le}")
            
            # Salva métricas
            caminho_metricas = os.path.join(diretorio, 'metricas_treinamento.json')
            metricas_para_salvar = {}
            for nome_tipo, metricas in self.metricas.items():
                metricas_para_salvar[nome_tipo] = {
                    'accuracy': float(metricas['accuracy']),
                    'precision': float(metricas['precision']),
                    'recall': float(metricas['recall']),
                    'f1': float(metricas['f1']),
                    'roc_auc': float(metricas['roc_auc'])
                }
            
            import json
            with open(caminho_metricas, 'w') as f:
                json.dump(metricas_para_salvar, f, indent=2)
            logger.info(f"💾 Métricas salvas em: {caminho_metricas}")
            
            logger.info("✅ Todos os modelos e componentes salvos com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelos: {e}")
            return False
    
    def carregar_modelos(self, diretorio: str = 'modelos_treinados') -> bool:
        """
        Carrega modelos salvos anteriormente.
        
        Args:
            diretorio: Diretório onde os modelos estão salvos
            
        Returns:
            True se todos os modelos foram carregados com sucesso
        """
        try:
            if not os.path.exists(diretorio):
                logger.error(f"❌ Diretório não encontrado: {diretorio}")
                return False
            
            # Carrega modelos
            tipos_modelos = ['resultado_1x2', 'over_under_2_5', 'ambos_marcam']
            
            for tipo in tipos_modelos:
                caminho_modelo = os.path.join(diretorio, f'{tipo}_modelo.pkl')
                caminho_scaler = os.path.join(diretorio, f'{tipo}_scaler.pkl')
                caminho_le = os.path.join(diretorio, f'{tipo}_label_encoder.pkl')
                
                if all(os.path.exists(p) for p in [caminho_modelo, caminho_scaler, caminho_le]):
                    # Carrega modelo
                    with open(caminho_modelo, 'rb') as f:
                        self.modelos[tipo] = pickle.load(f)
                    
                    # Carrega scaler
                    with open(caminho_scaler, 'rb') as f:
                        self.scalers[tipo] = pickle.load(f)
                    
                    # Carrega label encoder
                    with open(caminho_le, 'rb') as f:
                        self.label_encoders[tipo] = pickle.load(f)
                    
                    logger.info(f"✅ Modelo {tipo} carregado com sucesso")
                else:
                    logger.warning(f"⚠️ Arquivos do modelo {tipo} não encontrados")
            
            # Carrega métricas
            caminho_metricas = os.path.join(diretorio, 'metricas_treinamento.json')
            if os.path.exists(caminho_metricas):
                import json
                with open(caminho_metricas, 'r') as f:
                    self.metricas = json.load(f)
                logger.info("✅ Métricas carregadas com sucesso")
            
            return len(self.modelos) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelos: {e}")
            return False
    
    def fazer_predicao(self, features: pd.DataFrame, tipo_aposta: str) -> Dict[str, Any]:
        """
        Faz predição usando um modelo treinado.
        
        Args:
            features: Features da partida
            tipo_aposta: Tipo de aposta ('resultado_1x2', 'over_under_2_5', 'ambos_marcam')
            
        Returns:
            Dicionário com predição e probabilidades
        """
        try:
            if tipo_aposta not in self.modelos:
                logger.error(f"❌ Modelo para {tipo_aposta} não encontrado")
                return {}
            
            # Escala as features
            features_scaled = self.scalers[tipo_aposta].transform(features)
            
            # Faz predição
            modelo = self.modelos[tipo_aposta]
            predicao = modelo.predict(features_scaled)
            probabilidades = modelo.predict_proba(features_scaled)
            
            # Decodifica predição se necessário
            if tipo_aposta in self.label_encoders:
                predicao_decodificada = self.label_encoders[tipo_aposta].inverse_transform(predicao)
            else:
                predicao_decodificada = predicao
            
            resultado = {
                'predicao': predicao_decodificada[0] if len(predicao_decodificada) == 1 else predicao_decodificada,
                'probabilidades': probabilidades[0] if len(probabilidades) == 1 else probabilidades,
                'confianca': float(np.max(probabilidades))
            }
            
            logger.info(f"🎯 Predição para {tipo_aposta}: {resultado['predicao']} (confiança: {resultado['confianca']:.2f})")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer predição: {e}")
            return {}


def executar_treinamento_modelos():
    """Função principal para executar o treinamento de modelos."""
    try:
        logger.info("🚀 Iniciando treinamento de modelos de ML...")
        
        # Cria treinador
        treinador = TreinadorModelosML()
        
        # Treina todos os modelos
        resultados = treinador.treinar_todos_modelos()
        
        if resultados:
            logger.info("✅ Treinamento concluído com sucesso!")
            
            # Salva modelos
            if treinador.salvar_modelos():
                logger.info("💾 Modelos salvos com sucesso!")
            else:
                logger.error("❌ Erro ao salvar modelos")
            
            # Mostra resumo das métricas
            logger.info("📊 Resumo das métricas:")
            for tipo, metricas in treinador.metricas.items():
                logger.info(f"   {tipo}: F1={metricas['f1']:.4f}, ROC AUC={metricas['roc_auc']:.4f}")
            
            return resultados
        else:
            logger.error("❌ Falha no treinamento dos modelos")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro fatal no treinamento: {e}")
        raise


if __name__ == "__main__":
    executar_treinamento_modelos()
