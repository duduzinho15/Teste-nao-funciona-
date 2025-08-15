#!/usr/bin/env python3
"""
Sistema avançado de preparação de dados para Machine Learning
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime, timedelta
import warnings
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.decomposition import PCA
import joblib
from pathlib import Path

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

# Configurar logging
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class DataPreparationPipeline:
    """Pipeline completo de preparação de dados para ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.feature_selectors = {}
        self.pca_models = {}
        
        # Criar diretórios necessários
        self.models_dir = Path(self.config.models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def load_and_validate_data(self, data: Union[pd.DataFrame, str, Path]) -> pd.DataFrame:
        """Carrega e valida dados de entrada"""
        try:
            if isinstance(data, str) or isinstance(data, Path):
                # Carregar de arquivo
                if str(data).endswith('.csv'):
                    df = pd.read_csv(data)
                elif str(data).endswith('.parquet'):
                    df = pd.read_parquet(data)
                elif str(data).endswith('.json'):
                    df = pd.read_json(data)
                else:
                    raise ValueError(f"Formato de arquivo não suportado: {data}")
            else:
                df = data.copy()
            
            # Validações básicas
            if df.empty:
                raise ValueError("DataFrame está vazio")
            
            logger.info(f"Dados carregados com sucesso: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            raise
    
    def detect_data_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detecta automaticamente os tipos de dados"""
        data_types = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'text': [],
            'boolean': []
        }
        
        for col in df.columns:
            col_type = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(col_type):
                data_types['numeric'].append(col)
            elif pd.api.types.is_datetime64_dtype(col_type):
                data_types['datetime'].append(col)
            elif pd.api.types.is_bool_dtype(col_type):
                data_types['boolean'].append(col)
            elif df[col].nunique() < df.shape[0] * 0.1:  # Menos de 10% valores únicos
                data_types['categorical'].append(col)
            else:
                data_types['text'].append(col)
        
        logger.info(f"Tipos de dados detectados: {data_types}")
        return data_types
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """Trata valores ausentes de forma inteligente"""
        try:
            df_clean = df.copy()
            missing_info = df_clean.isnull().sum()
            
            if missing_info.sum() == 0:
                logger.info("Nenhum valor ausente encontrado")
                return df_clean
            
            logger.info(f"Valores ausentes encontrados: {missing_info[missing_info > 0]}")
            
            data_types = self.detect_data_types(df_clean)
            
            for col in df_clean.columns:
                if df_clean[col].isnull().sum() > 0:
                    if col in data_types['numeric']:
                        # Para colunas numéricas, usar mediana
                        imputer = SimpleImputer(strategy='median')
                        df_clean[col] = imputer.fit_transform(df_clean[[col]])
                        self.imputers[f"imputer_{col}"] = imputer
                        
                    elif col in data_types['categorical']:
                        # Para colunas categóricas, usar moda
                        imputer = SimpleImputer(strategy='most_frequent')
                        df_clean[col] = imputer.fit_transform(df_clean[[col]])
                        self.imputers[f"imputer_{col}"] = imputer
                        
                    elif col in data_types['datetime']:
                        # Para datas, usar forward fill
                        df_clean[col] = df_clean[col].fillna(method='ffill')
                        
                    else:
                        # Para texto, usar string vazia
                        df_clean[col] = df_clean[col].fillna('')
            
            logger.info("Valores ausentes tratados com sucesso")
            return df_clean
            
        except Exception as e:
            logger.error(f"Erro ao tratar valores ausentes: {e}")
            raise
    
    def encode_categorical_variables(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """Codifica variáveis categóricas"""
        try:
            df_encoded = df.copy()
            data_types = self.detect_data_types(df_encoded)
            
            for col in data_types['categorical']:
                if df_encoded[col].nunique() <= 2:
                    # Para variáveis binárias, usar LabelEncoder
                    encoder = LabelEncoder()
                    df_encoded[col] = encoder.fit_transform(df_encoded[col])
                    self.encoders[f"label_encoder_{col}"] = encoder
                    
                elif df_encoded[col].nunique() <= 10:
                    # Para poucas categorias, usar OneHotEncoder
                    encoder = OneHotEncoder(sparse=False, drop='first')
                    encoded_data = encoder.fit_transform(df_encoded[[col]])
                    encoded_df = pd.DataFrame(
                        encoded_data,
                        columns=[f"{col}_{cat}" for cat in encoder.categories_[0][1:]],
                        index=df_encoded.index
                    )
                    
                    # Remover coluna original e adicionar encoded
                    df_encoded = df_encoded.drop(columns=[col])
                    df_encoded = pd.concat([df_encoded, encoded_df], axis=1)
                    self.encoders[f"onehot_encoder_{col}"] = encoder
                    
                else:
                    # Para muitas categorias, usar LabelEncoder
                    encoder = LabelEncoder()
                    df_encoded[col] = encoder.fit_transform(df_encoded[col])
                    self.encoders[f"label_encoder_{col}"] = encoder
            
            logger.info("Variáveis categóricas codificadas com sucesso")
            return df_encoded
            
        except Exception as e:
            logger.error(f"Erro ao codificar variáveis categóricas: {e}")
            raise
    
    def scale_numeric_features(self, df: pd.DataFrame, strategy: str = 'standard') -> pd.DataFrame:
        """Escala features numéricas"""
        try:
            df_scaled = df.copy()
            data_types = self.detect_data_types(df_scaled)
            
            numeric_cols = data_types['numeric']
            if not numeric_cols:
                logger.info("Nenhuma coluna numérica encontrada para escalar")
                return df_scaled
            
            if strategy == 'standard':
                scaler = StandardScaler()
            elif strategy == 'minmax':
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
            elif strategy == 'robust':
                from sklearn.preprocessing import RobustScaler
                scaler = RobustScaler()
            else:
                scaler = StandardScaler()
            
            df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])
            self.scalers['main_scaler'] = scaler
            
            logger.info(f"Features numéricas escaladas com sucesso usando {strategy}")
            return df_scaled
            
        except Exception as e:
            logger.error(f"Erro ao escalar features: {e}")
            raise
    
    def create_time_features(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Cria features temporais a partir de colunas de data"""
        try:
            df_time = df.copy()
            
            for date_col in date_columns:
                if date_col in df_time.columns:
                    df_time[date_col] = pd.to_datetime(df_time[date_col])
                    
                    # Features básicas de tempo
                    df_time[f"{date_col}_year"] = df_time[date_col].dt.year
                    df_time[f"{date_col}_month"] = df_time[date_col].dt.month
                    df_time[f"{date_col}_day"] = df_time[date_col].dt.day
                    df_time[f"{date_col}_dayofweek"] = df_time[date_col].dt.dayofweek
                    df_time[f"{date_col}_quarter"] = df_time[date_col].dt.quarter
                    
                    # Features sazonais
                    df_time[f"{date_col}_is_weekend"] = df_time[date_col].dt.dayofweek.isin([5, 6]).astype(int)
                    df_time[f"{date_col}_is_month_start"] = df_time[date_col].dt.is_month_start.astype(int)
                    df_time[f"{date_col}_is_month_end"] = df_time[date_col].dt.is_month_end.astype(int)
                    
                    # Remover coluna original de data
                    df_time = df_time.drop(columns=[date_col])
            
            logger.info("Features temporais criadas com sucesso")
            return df_time
            
        except Exception as e:
            logger.error(f"Erro ao criar features temporais: {e}")
            raise
    
    def create_interaction_features(self, df: pd.DataFrame, feature_groups: List[List[str]]) -> pd.DataFrame:
        """Cria features de interação entre grupos de variáveis"""
        try:
            df_interaction = df.copy()
            
            for group in feature_groups:
                if len(group) >= 2:
                    # Criar produto das features do grupo
                    interaction_name = "_x_".join(group)
                    df_interaction[interaction_name] = df_interaction[group].prod(axis=1)
                    
                    # Criar razão entre features (evitando divisão por zero)
                    if len(group) == 2:
                        ratio_name = f"{group[0]}_div_{group[1]}"
                        df_interaction[ratio_name] = np.where(
                            df_interaction[group[1]] != 0,
                            df_interaction[group[0]] / df_interaction[group[1]],
                            0
                        )
            
            logger.info("Features de interação criadas com sucesso")
            return df_interaction
            
        except Exception as e:
            logger.error(f"Erro ao criar features de interação: {e}")
            raise
    
    def select_features(self, df: pd.DataFrame, target_col: str, method: str = 'mutual_info', k: int = 20) -> pd.DataFrame:
        """Seleciona as melhores features"""
        try:
            if target_col not in df.columns:
                raise ValueError(f"Coluna alvo '{target_col}' não encontrada")
            
            # Separar features e target
            X = df.drop(columns=[target_col])
            y = df[target_col]
            
            # Verificar se há dados suficientes
            if X.shape[0] < 10:
                logger.warning("Dados insuficientes para seleção de features")
                return df
            
            if method == 'mutual_info':
                selector = SelectKBest(score_func=mutual_info_classif, k=min(k, X.shape[1]))
            elif method == 'f_classif':
                selector = SelectKBest(score_func=f_classif, k=min(k, X.shape[1]))
            else:
                selector = SelectKBest(score_func=mutual_info_classif, k=min(k, X.shape[1]))
            
            # Aplicar seleção
            X_selected = selector.fit_transform(X, y)
            selected_features = X.columns[selector.get_support()].tolist()
            
            # Criar DataFrame com features selecionadas + target
            df_selected = pd.DataFrame(X_selected, columns=selected_features, index=df.index)
            df_selected[target_col] = y
            
            self.feature_selectors['main_selector'] = selector
            
            logger.info(f"Features selecionadas: {len(selected_features)} de {X.shape[1]}")
            return df_selected
            
        except Exception as e:
            logger.error(f"Erro na seleção de features: {e}")
            return df
    
    def apply_pca(self, df: pd.DataFrame, target_col: str, n_components: float = 0.95) -> pd.DataFrame:
        """Aplica PCA para redução de dimensionalidade"""
        try:
            if target_col not in df.columns:
                raise ValueError(f"Coluna alvo '{target_col}' não encontrada")
            
            X = df.drop(columns=[target_col])
            y = df[target_col]
            
            # Determinar número de componentes
            if isinstance(n_components, float):
                n_components = int(X.shape[1] * n_components)
            
            n_components = min(n_components, X.shape[1])
            
            if n_components >= X.shape[1]:
                logger.info("PCA não aplicado - dados já têm dimensão adequada")
                return df
            
            # Aplicar PCA
            pca = PCA(n_components=n_components, random_state=self.config.random_state)
            X_pca = pca.fit_transform(X)
            
            # Criar DataFrame com componentes PCA
            pca_columns = [f"pca_component_{i+1}" for i in range(n_components)]
            df_pca = pd.DataFrame(X_pca, columns=pca_columns, index=df.index)
            df_pca[target_col] = y
            
            self.pca_models['main_pca'] = pca
            
            # Calcular variância explicada
            explained_variance = pca.explained_variance_ratio_.sum()
            logger.info(f"PCA aplicado: {n_components} componentes explicam {explained_variance:.2%} da variância")
            
            return df_pca
            
        except Exception as e:
            logger.error(f"Erro ao aplicar PCA: {e}")
            return df
    
    def save_preprocessing_models(self, filename: str = None) -> str:
        """Salva todos os modelos de pré-processamento"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"preprocessing_models_{timestamp}.joblib"
            
            filepath = self.models_dir / filename
            
            models_to_save = {
                'scalers': self.scalers,
                'encoders': self.encoders,
                'imputers': self.imputers,
                'feature_selectors': self.feature_selectors,
                'pca_models': self.pca_models,
                'config': self.config,
                'timestamp': datetime.now().isoformat()
            }
            
            joblib.dump(models_to_save, filepath)
            logger.info(f"Modelos de pré-processamento salvos em: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelos: {e}")
            raise
    
    def load_preprocessing_models(self, filepath: str) -> bool:
        """Carrega modelos de pré-processamento salvos"""
        try:
            models = joblib.load(filepath)
            
            self.scalers = models.get('scalers', {})
            self.encoders = models.get('encoders', {})
            self.imputers = models.get('imputers', {})
            self.feature_selectors = models.get('feature_selectors', {})
            self.pca_models = models.get('pca_models', {})
            
            logger.info(f"Modelos de pré-processamento carregados de: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            return False
    
    @timed_cache_result(ttl_hours=24)
    def run_full_pipeline(self, data: Union[pd.DataFrame, str, Path], 
                         target_col: str,
                         date_columns: List[str] = None,
                         feature_groups: List[List[str]] = None,
                         apply_pca: bool = False) -> pd.DataFrame:
        """Executa o pipeline completo de preparação de dados"""
        try:
            logger.info("Iniciando pipeline completo de preparação de dados")
            
            # 1. Carregar e validar dados
            df = self.load_and_validate_data(data)
            
            # 2. Tratar valores ausentes
            df = self.handle_missing_values(df)
            
            # 3. Criar features temporais se especificado
            if date_columns:
                df = self.create_time_features(df, date_columns)
            
            # 4. Codificar variáveis categóricas
            df = self.encode_categorical_variables(df)
            
            # 5. Criar features de interação se especificado
            if feature_groups:
                df = self.create_interaction_features(df, feature_groups)
            
            # 6. Escalar features numéricas
            df = self.scale_numeric_features(df)
            
            # 7. Selecionar features
            df = self.select_features(df, target_col)
            
            # 8. Aplicar PCA se solicitado
            if apply_pca:
                df = self.apply_pca(df, target_col)
            
            # 9. Salvar modelos de pré-processamento
            self.save_preprocessing_models()
            
            logger.info(f"Pipeline completo executado com sucesso. Shape final: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Erro no pipeline completo: {e}")
            raise

# Instância global
data_pipeline = DataPreparationPipeline()

# Funções de conveniência
def prepare_data(data: Union[pd.DataFrame, str, Path], 
                target_col: str,
                **kwargs) -> pd.DataFrame:
    """Prepara dados usando o pipeline completo"""
    return data_pipeline.run_full_pipeline(data, target_col, **kwargs)

def save_preprocessing_models(filename: str = None) -> str:
    """Salva modelos de pré-processamento"""
    return data_pipeline.save_preprocessing_models(filename)

def load_preprocessing_models(filepath: str) -> bool:
    """Carrega modelos de pré-processamento"""
    return data_pipeline.load_preprocessing_models(filepath)
