#!/usr/bin/env python3
"""
Sistema de coleta de dados históricos para treinamento de modelos ML
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import requests
import json
from pathlib import Path
import time
import random
from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    """Coletor de dados históricos para treinamento de modelos ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.data_dir = Path(self.config.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dados de exemplo para demonstração
        self.sample_matches = self._generate_sample_data()
        
    def _generate_sample_data(self) -> List[Dict]:
        """Gera dados de exemplo para demonstração"""
        teams = [
            "Flamengo", "Palmeiras", "Corinthians", "São Paulo", "Santos",
            "Grêmio", "Internacional", "Atlético-MG", "Cruzeiro", "Vasco",
            "Botafogo", "Fluminense", "Athletico-PR", "Fortaleza", "Ceará"
        ]
        
        matches = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(1000):  # 1000 partidas históricas
            match_date = base_date + timedelta(days=i % 365)
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # Gerar estatísticas realistas
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 4)
            
            # Features para ML
            match_data = {
                'match_id': f'match_{i:04d}',
                'date': match_date.strftime('%Y-%m-%d'),
                'competition': 'Brasileirão',
                'season': '2024',
                'home_team': home_team,
                'away_team': away_team,
                'home_goals': home_goals,
                'away_goals': away_goals,
                'total_goals': home_goals + away_goals,
                'both_teams_score': 1 if home_goals > 0 and away_goals > 0 else 0,
                'result': self._determine_result(home_goals, away_goals),
                
                # Features numéricas
                'home_possession': random.uniform(40, 70),
                'away_possession': 100 - random.uniform(40, 70),
                'home_shots': random.randint(5, 20),
                'away_shots': random.randint(5, 20),
                'home_shots_on_target': random.randint(2, 10),
                'away_shots_on_target': random.randint(2, 10),
                'home_corners': random.randint(3, 12),
                'away_corners': random.randint(3, 12),
                'home_fouls': random.randint(8, 25),
                'away_fouls': random.randint(8, 25),
                'home_yellow_cards': random.randint(0, 5),
                'away_yellow_cards': random.randint(0, 5),
                'home_red_cards': random.randint(0, 2),
                'away_red_cards': random.randint(0, 2),
                
                # Features de forma recente (últimas 5 partidas)
                'home_form_last_5': random.uniform(0.2, 1.0),
                'away_form_last_5': random.uniform(0.2, 1.0),
                
                # Features de força de ataque/defesa
                'home_attacking_strength': random.uniform(0.5, 1.5),
                'away_attacking_strength': random.uniform(0.5, 1.5),
                'home_defensive_strength': random.uniform(0.5, 1.5),
                'away_defensive_strength': random.uniform(0.5, 1.5),
                
                # Features de xG (Expected Goals)
                'home_xg': round(random.uniform(0.5, 3.0), 2),
                'away_xg': round(random.uniform(0.5, 3.0), 2),
                'home_xa': round(random.uniform(0.2, 2.0), 2),
                'away_xa': round(random.uniform(0.2, 2.0), 2),
                
                # Features temporais
                'day_of_week': match_date.weekday(),
                'month': match_date.month,
                'is_weekend': 1 if match_date.weekday() >= 5 else 0,
                
                # Features de contexto
                'home_team_rank': random.randint(1, 20),
                'away_team_rank': random.randint(1, 20),
                'home_team_points': random.randint(0, 80),
                'away_team_points': random.randint(0, 80),
                
                # Features de head-to-head
                'h2h_home_wins': random.randint(0, 10),
                'h2h_away_wins': random.randint(0, 10),
                'h2h_draws': random.randint(0, 5),
                
                # Features de mercado
                'home_odds': round(random.uniform(1.5, 4.0), 2),
                'away_odds': round(random.uniform(1.5, 4.0), 2),
                'draw_odds': round(random.uniform(2.5, 5.0), 2),
                'over_2_5_odds': round(random.uniform(1.8, 3.5), 2),
                'both_teams_score_odds': round(random.uniform(1.6, 3.0), 2),
            }
            
            matches.append(match_data)
        
        return matches
    
    def _determine_result(self, home_goals: int, away_goals: int) -> str:
        """Determina o resultado da partida"""
        if home_goals > away_goals:
            return 'home_win'
        elif away_goals > home_goals:
            return 'away_win'
        else:
            return 'draw'
    
    @timed_cache_result(ttl_hours=24)
    def collect_historical_matches(self, 
                                 start_date: str = None,
                                 end_date: str = None,
                                 competitions: List[str] = None,
                                 min_matches: int = 100) -> pd.DataFrame:
        """
        Coleta dados históricos de partidas
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            competitions: Lista de competições
            min_matches: Número mínimo de partidas
            
        Returns:
            DataFrame com dados históricos
        """
        try:
            logger.info("Iniciando coleta de dados históricos...")
            
            # Para demonstração, usar dados de exemplo
            # Em produção, aqui seria feita a coleta real da API ou banco
            matches_data = self.sample_matches
            
            # Filtrar por data se especificado
            if start_date or end_date:
                matches_data = self._filter_by_date(matches_data, start_date, end_date)
            
            # Filtrar por competição se especificado
            if competitions:
                matches_data = [m for m in matches_data if m['competition'] in competitions]
            
            # Verificar se temos dados suficientes
            if len(matches_data) < min_matches:
                logger.warning(f"Dados insuficientes: {len(matches_data)} < {min_matches}")
                return pd.DataFrame()
            
            # Converter para DataFrame
            df = pd.DataFrame(matches_data)
            
            # Adicionar features derivadas
            df = self._add_derived_features(df)
            
            # Salvar dados coletados
            self._save_collected_data(df)
            
            logger.info(f"Coleta concluída: {len(df)} partidas coletadas")
            return df
            
        except Exception as e:
            logger.error(f"Erro na coleta de dados: {e}")
            return pd.DataFrame()
    
    def _filter_by_date(self, matches: List[Dict], start_date: str, end_date: str) -> List[Dict]:
        """Filtra partidas por período"""
        filtered_matches = []
        
        for match in matches:
            match_date = datetime.strptime(match['date'], '%Y-%m-%d')
            
            if start_date:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                if match_date < start:
                    continue
            
            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                if match_date > end:
                    continue
            
            filtered_matches.append(match)
        
        return filtered_matches
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features derivadas para ML"""
        try:
            # Features de diferença de gols
            df['goal_difference'] = df['home_goals'] - df['away_goals']
            df['total_goals_squared'] = df['total_goals'] ** 2
            
            # Features de eficiência
            df['home_shot_efficiency'] = df['home_shots_on_target'] / (df['home_shots'] + 1)
            df['away_shot_efficiency'] = df['away_shots_on_target'] / (df['away_shots'] + 1)
            
            # Features de pressão
            df['home_pressure'] = df['home_corners'] + df['home_shots']
            df['away_pressure'] = df['away_corners'] + df['away_shots']
            
            # Features de disciplina
            df['home_discipline'] = df['home_yellow_cards'] + (df['home_red_cards'] * 2)
            df['away_discipline'] = df['away_yellow_cards'] + (df['away_red_cards'] * 2)
            
            # Features de ranking relativo
            df['ranking_difference'] = df['away_team_rank'] - df['home_team_rank']
            df['points_difference'] = df['home_team_points'] - df['away_team_points']
            
            # Features de head-to-head
            df['h2h_total_matches'] = df['h2h_home_wins'] + df['h2h_away_wins'] + df['h2h_draws']
            df['h2h_home_advantage'] = (df['h2h_home_wins'] - df['h2h_away_wins']) / (df['h2h_total_matches'] + 1)
            
            # Features de odds (probabilidades implícitas)
            df['home_win_prob'] = 1 / df['home_odds']
            df['away_win_prob'] = 1 / df['away_odds']
            df['draw_prob'] = 1 / df['draw_odds']
            
            # Normalizar probabilidades
            total_prob = df['home_win_prob'] + df['away_win_prob'] + df['draw_prob']
            df['home_win_prob_norm'] = df['home_win_prob'] / total_prob
            df['away_win_prob_norm'] = df['away_win_prob'] / total_prob
            df['draw_prob_norm'] = df['draw_prob'] / total_prob
            
            logger.info("Features derivadas adicionadas com sucesso")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao adicionar features derivadas: {e}")
            return df
    
    def _save_collected_data(self, df: pd.DataFrame) -> None:
        """Salva dados coletados em arquivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"historical_matches_{timestamp}.csv"
            filepath = self.data_dir / filename
            
            df.to_csv(filepath, index=False)
            logger.info(f"Dados salvos em: {filepath}")
            
            # Salvar também o arquivo mais recente
            latest_file = self.data_dir / "latest_historical_matches.csv"
            df.to_csv(latest_file, index=False)
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
    
    def get_training_data(self, target_column: str = 'result') -> tuple:
        """
        Prepara dados para treinamento
        
        Args:
            target_column: Coluna alvo para predição
            
        Returns:
            Tuple (X, y) com features e target
        """
        try:
            # Carregar dados mais recentes
            latest_file = self.data_dir / "latest_historical_matches.csv"
            
            if not latest_file.exists():
                logger.info("Dados não encontrados. Coletando dados históricos...")
                df = self.collect_historical_matches()
            else:
                df = pd.read_csv(latest_file)
            
            if df.empty:
                logger.error("Nenhum dado disponível para treinamento")
                return None, None
            
            # Selecionar features para ML
            feature_columns = [
                'home_goals', 'away_goals', 'total_goals', 'both_teams_score',
                'home_possession', 'away_possession', 'home_shots', 'away_shots',
                'home_shots_on_target', 'away_shots_on_target', 'home_corners', 'away_corners',
                'home_fouls', 'away_fouls', 'home_yellow_cards', 'away_yellow_cards',
                'home_red_cards', 'away_red_cards', 'home_form_last_5', 'away_form_last_5',
                'home_attacking_strength', 'away_attacking_strength',
                'home_defensive_strength', 'away_defensive_strength',
                'home_xg', 'away_xg', 'home_xa', 'away_xa',
                'day_of_week', 'month', 'is_weekend',
                'home_team_rank', 'away_team_rank', 'home_team_points', 'away_team_points',
                'h2h_home_wins', 'h2h_away_wins', 'h2h_draws',
                'home_odds', 'away_odds', 'draw_odds',
                'goal_difference', 'total_goals_squared',
                'home_shot_efficiency', 'away_shot_efficiency',
                'home_pressure', 'away_pressure', 'home_discipline', 'away_discipline',
                'ranking_difference', 'points_difference',
                'h2h_total_matches', 'h2h_home_advantage',
                'home_win_prob_norm', 'away_win_prob_norm', 'draw_prob_norm'
            ]
            
            # Filtrar colunas existentes
            available_features = [col for col in feature_columns if col in df.columns]
            
            # Preparar X (features) e y (target)
            X = df[available_features].copy()
            y = df[target_column].copy()
            
            # Remover linhas com valores NaN
            valid_indices = ~(X.isna().any(axis=1) | y.isna())
            X = X[valid_indices]
            y = y[valid_indices]
            
            logger.info(f"Dados de treinamento preparados: {X.shape[0]} amostras, {X.shape[1]} features")
            return X, y
            
        except Exception as e:
            logger.error(f"Erro ao preparar dados de treinamento: {e}")
            return None, None
    
    def get_feature_importance_data(self) -> Dict[str, List[str]]:
        """Retorna dados para análise de importância de features"""
        return {
            'result_prediction': [
                'home_form_last_5', 'away_form_last_5', 'home_attacking_strength',
                'away_attacking_strength', 'home_defensive_strength', 'away_defensive_strength',
                'home_team_rank', 'away_team_rank', 'h2h_home_advantage', 'home_odds'
            ],
            'total_goals_prediction': [
                'home_attacking_strength', 'away_attacking_strength', 'home_xg', 'away_xg',
                'home_shots', 'away_shots', 'home_pressure', 'away_pressure'
            ],
            'both_teams_score_prediction': [
                'home_attacking_strength', 'away_attacking_strength', 'home_xg', 'away_xg',
                'home_shot_efficiency', 'away_shot_efficiency'
            ]
        }

# Instância global
data_collector = HistoricalDataCollector()

# Funções de conveniência
def collect_historical_data(**kwargs) -> pd.DataFrame:
    """Coleta dados históricos"""
    return data_collector.collect_historical_matches(**kwargs)

def get_training_data(target_column: str = 'result') -> tuple:
    """Prepara dados para treinamento"""
    return data_collector.get_training_data(target_column)

def get_feature_importance_data() -> Dict[str, List[str]]:
    """Retorna dados para análise de importância de features"""
    return data_collector.get_feature_importance_data()
