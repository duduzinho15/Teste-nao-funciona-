#!/usr/bin/env python3
"""
Funcionalidades avançadas para expansão do sistema ML
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
import optuna
import warnings
warnings.filterwarnings('ignore')

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .database_integration import DatabaseIntegration

logger = logging.getLogger(__name__)

class AdvancedFeatures:
    """Funcionalidades avançadas para o sistema ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.db_integration = DatabaseIntegration()
        self.results_dir = Path(self.config.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações para análise avançada
        self.trend_analysis_config = {
            'window_sizes': [5, 10, 20],
            'min_trend_strength': 0.6,
            'confidence_threshold': 0.7
        }
        
        self.backtesting_config = {
            'initial_bankroll': 10000.0,
            'bet_size_percentage': 0.05,
            'min_odds': 1.5,
            'max_odds': 5.0,
            'stop_loss': 0.3,
            'take_profit': 0.5
        }
    
    def analyze_trends(self, 
                      team_name: str = None,
                      competition: str = None,
                      days_back: int = 90) -> Dict[str, Any]:
        """
        Analisa tendências de equipes e competições
        
        Args:
            team_name: Nome da equipe específica
            competition: Nome da competição
            days_back: Número de dias para análise
            
        Returns:
            Dicionário com análise de tendências
        """
        try:
            logger.info(f"Analisando tendências para {team_name or 'todas as equipes'}")
            
            # Obter dados históricos
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            matches_data = self.db_integration.get_matches_data(
                start_date=start_date,
                end_date=end_date,
                competition=competition,
                limit=1000
            )
            
            if matches_data.empty:
                return {'error': 'Nenhum dado disponível para análise'}
            
            # Análise de tendências
            trends = {}
            
            if team_name:
                # Análise específica da equipe
                trends = self._analyze_team_trends(matches_data, team_name)
            else:
                # Análise geral da competição
                trends = self._analyze_competition_trends(matches_data)
            
            # Salvar resultados
            self._save_trend_analysis(trends, team_name, competition)
            
            return trends
            
        except Exception as e:
            logger.error(f"Erro na análise de tendências: {e}")
            return {'error': str(e)}
    
    def _analyze_team_trends(self, matches_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """Analisa tendências de uma equipe específica"""
        # Filtrar partidas da equipe
        team_matches = matches_data[
            (matches_data['home_team'] == team_name) | 
            (matches_data['away_team'] == team_name)
        ].copy()
        
        if team_matches.empty:
            return {'error': f'Nenhuma partida encontrada para {team_name}'}
        
        # Ordenar por data
        team_matches = team_matches.sort_values('date')
        
        # Calcular métricas de tendência
        trends = {
            'team_name': team_name,
            'total_matches': len(team_matches),
            'period': f"{team_matches['date'].min()} a {team_matches['date'].max()}",
            'trends': {}
        }
        
        # Tendência de resultados
        trends['trends']['results'] = self._calculate_result_trends(team_matches, team_name)
        
        # Tendência de gols
        trends['trends']['goals'] = self._calculate_goals_trends(team_matches, team_name)
        
        # Tendência de performance
        trends['trends']['performance'] = self._calculate_performance_trends(team_matches, team_name)
        
        # Tendência de mercado
        trends['trends']['market'] = self._calculate_market_trends(team_matches, team_name)
        
        return trends
    
    def _analyze_competition_trends(self, matches_data: pd.DataFrame) -> Dict[str, Any]:
        """Analisa tendências gerais da competição"""
        trends = {
            'competition': matches_data['competition'].iloc[0] if not matches_data.empty else 'Unknown',
            'total_matches': len(matches_data),
            'period': f"{matches_data['date'].min()} a {matches_data['date'].max()}",
            'trends': {}
        }
        
        # Tendências de gols
        trends['trends']['goals'] = {
            'avg_total_goals': matches_data['total_goals'].mean(),
            'goals_trend': self._calculate_rolling_trend(matches_data, 'total_goals'),
            'both_teams_score_rate': matches_data['both_teams_score'].mean(),
            'high_scoring_matches': (matches_data['total_goals'] > 2.5).mean()
        }
        
        # Tendências de resultados
        home_wins = (matches_data['home_goals'] > matches_data['away_goals']).mean()
        away_wins = (matches_data['away_goals'] > matches_data['home_goals']).mean()
        draws = (matches_data['home_goals'] == matches_data['away_goals']).mean()
        
        trends['trends']['results'] = {
            'home_win_rate': home_wins,
            'away_win_rate': away_wins,
            'draw_rate': draws,
            'home_advantage_strength': home_wins - away_wins
        }
        
        # Tendências de mercado
        if 'home_odds' in matches_data.columns:
            trends['trends']['market'] = {
                'avg_home_odds': matches_data['home_odds'].mean(),
                'avg_away_odds': matches_data['away_odds'].mean(),
                'avg_draw_odds': matches_data['draw_odds'].mean(),
                'value_betting_opportunities': self._identify_value_betting(matches_data)
            }
        
        return trends
    
    def _calculate_result_trends(self, matches_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """Calcula tendências de resultados para uma equipe"""
        results = []
        
        for _, match in matches_data.iterrows():
            if match['home_team'] == team_name:
                if match['home_goals'] > match['away_goals']:
                    results.append('W')
                elif match['home_goals'] < match['away_goals']:
                    results.append('L')
                else:
                    results.append('D')
            else:
                if match['away_goals'] > match['home_goals']:
                    results.append('W')
                elif match['away_goals'] < match['home_goals']:
                    results.append('L')
                else:
                    results.append('D')
        
        # Calcular tendências
        if len(results) >= 5:
            recent_results = results[-5:]
            win_rate_recent = recent_results.count('W') / len(recent_results)
            
            # Detectar padrões
            patterns = {
                'current_form': 'Good' if win_rate_recent >= 0.6 else 'Poor' if win_rate_recent <= 0.2 else 'Average',
                'win_rate_recent': win_rate_recent,
                'last_5_results': recent_results,
                'trend_direction': 'Up' if win_rate_recent >= 0.6 else 'Down' if win_rate_recent <= 0.2 else 'Stable'
            }
        else:
            patterns = {'error': 'Dados insuficientes para análise de tendência'}
        
        return patterns
    
    def _calculate_goals_trends(self, matches_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """Calcula tendências de gols para uma equipe"""
        goals_scored = []
        goals_conceded = []
        
        for _, match in matches_data.iterrows():
            if match['home_team'] == team_name:
                goals_scored.append(match['home_goals'])
                goals_conceded.append(match['away_goals'])
            else:
                goals_scored.append(match['away_goals'])
                goals_conceded.append(match['home_goals'])
        
        # Calcular métricas
        avg_scored = np.mean(goals_scored)
        avg_conceded = np.mean(goals_conceded)
        
        # Tendência recente
        if len(goals_scored) >= 5:
            recent_scored = goals_scored[-5:]
            recent_conceded = goals_conceded[-5:]
            
            scored_trend = 'Up' if np.mean(recent_scored) > avg_scored else 'Down'
            conceded_trend = 'Up' if np.mean(recent_conceded) > avg_conceded else 'Down'
        else:
            scored_trend = 'Unknown'
            conceded_trend = 'Unknown'
        
        return {
            'avg_goals_scored': round(avg_scored, 2),
            'avg_goals_conceded': round(avg_conceded, 2),
            'scored_trend': scored_trend,
            'conceded_trend': conceded_trend,
            'goal_difference': round(avg_scored - avg_conceded, 2)
        }
    
    def _calculate_performance_trends(self, matches_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """Calcula tendências de performance para uma equipe"""
        performance_metrics = []
        
        for _, match in matches_data.iterrows():
            if match['home_team'] == team_name:
                possession = match.get('home_possession', 50)
                shots = match.get('home_shots', 10)
                shots_on_target = match.get('home_shots_on_target', 5)
                xg = match.get('home_xg', 1.0)
            else:
                possession = match.get('away_possession', 50)
                shots = match.get('away_shots', 10)
                shots_on_target = match.get('away_shots_on_target', 5)
                xg = match.get('away_xg', 1.0)
            
            # Calcular eficiência
            shot_efficiency = shots_on_target / shots if shots > 0 else 0
            xg_efficiency = xg / shots if shots > 0 else 0
            
            performance_metrics.append({
                'possession': possession,
                'shot_efficiency': shot_efficiency,
                'xg_efficiency': xg_efficiency
            })
        
        # Calcular tendências
        if performance_metrics:
            avg_possession = np.mean([m['possession'] for m in performance_metrics])
            avg_shot_efficiency = np.mean([m['shot_efficiency'] for m in performance_metrics])
            avg_xg_efficiency = np.mean([m['xg_efficiency'] for m in performance_metrics])
            
            return {
                'avg_possession': round(avg_possession, 1),
                'avg_shot_efficiency': round(avg_shot_efficiency, 3),
                'avg_xg_efficiency': round(avg_xg_efficiency, 3),
                'possession_trend': 'High' if avg_possession > 55 else 'Low' if avg_possession < 45 else 'Average',
                'efficiency_trend': 'Good' if avg_shot_efficiency > 0.4 else 'Poor' if avg_shot_efficiency < 0.2 else 'Average'
            }
        
        return {'error': 'Dados de performance insuficientes'}
    
    def _calculate_market_trends(self, matches_data: pd.DataFrame, team_name: str) -> Dict[str, Any]:
        """Calcula tendências de mercado para uma equipe"""
        if 'home_odds' not in matches_data.columns:
            return {'error': 'Dados de odds não disponíveis'}
        
        odds_data = []
        
        for _, match in matches_data.iterrows():
            if match['home_team'] == team_name:
                odds_data.append({
                    'odds': match['home_odds'],
                    'implied_prob': 1 / match['home_odds'],
                    'position': 'home'
                })
            else:
                odds_data.append({
                    'odds': match['away_odds'],
                    'implied_prob': 1 / match['away_odds'],
                    'position': 'away'
                })
        
        if odds_data:
            avg_odds = np.mean([d['odds'] for d in odds_data])
            avg_prob = np.mean([d['implied_prob'] for d in odds_data])
            
            # Detectar valor de mercado
            market_value = 'Overvalued' if avg_prob < 0.3 else 'Undervalued' if avg_prob > 0.4 else 'Fair'
            
            return {
                'avg_odds': round(avg_odds, 2),
                'avg_implied_probability': round(avg_prob, 3),
                'market_value': market_value,
                'betting_opportunity': 'Yes' if market_value == 'Undervalued' else 'No'
            }
        
        return {'error': 'Dados de odds insuficientes'}
    
    def _calculate_rolling_trend(self, data: pd.DataFrame, column: str, window: int = 10) -> str:
        """Calcula tendência usando média móvel"""
        if len(data) < window:
            return 'Unknown'
        
        rolling_mean = data[column].rolling(window=window).mean()
        
        if len(rolling_mean.dropna()) < 2:
            return 'Unknown'
        
        recent_trend = rolling_mean.iloc[-1] - rolling_mean.iloc[-2]
        
        if recent_trend > 0.1:
            return 'Up'
        elif recent_trend < -0.1:
            return 'Down'
        else:
            return 'Stable'
    
    def _identify_value_betting(self, matches_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identifica oportunidades de value betting"""
        opportunities = []
        
        for _, match in matches_data.iterrows():
            # Calcular probabilidades implícitas
            home_prob = 1 / match['home_odds']
            away_prob = 1 / match['away_odds']
            draw_prob = 1 / match['draw_odds']
            
            total_prob = home_prob + away_prob + draw_prob
            
            # Normalizar
            home_prob_norm = home_prob / total_prob
            away_prob_norm = away_prob / total_prob
            draw_prob_norm = draw_prob / total_prob
            
            # Identificar value bets (probabilidade real > probabilidade implícita)
            if home_prob_norm > 0.4 and match['home_odds'] > 2.0:
                opportunities.append({
                    'match': f"{match['home_team']} vs {match['away_team']}",
                    'bet_type': 'Home Win',
                    'odds': match['home_odds'],
                    'value_score': round(home_prob_norm - (1/match['home_odds']), 3)
                })
            
            if away_prob_norm > 0.35 and match['away_odds'] > 2.5:
                opportunities.append({
                    'match': f"{match['home_team']} vs {match['away_team']}",
                    'bet_type': 'Away Win',
                    'odds': match['away_odds'],
                    'value_score': round(away_prob_norm - (1/match['away_odds']), 3)
                })
        
        # Ordenar por score de valor
        opportunities.sort(key=lambda x: x['value_score'], reverse=True)
        return opportunities[:5]  # Top 5 oportunidades
    
    def run_backtesting(self, 
                       strategy_name: str,
                       start_date: str = None,
                       end_date: str = None,
                       competition: str = None) -> Dict[str, Any]:
        """
        Executa backtesting de uma estratégia de apostas
        
        Args:
            strategy_name: Nome da estratégia
            start_date: Data inicial
            end_date: Data final
            competition: Competição
            
        Returns:
            Resultados do backtesting
        """
        try:
            logger.info(f"Iniciando backtesting da estratégia: {strategy_name}")
            
            # Obter dados históricos
            if not start_date:
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            matches_data = self.db_integration.get_matches_data(
                start_date=start_date,
                end_date=end_date,
                competition=competition,
                limit=1000
            )
            
            if matches_data.empty:
                return {'error': 'Nenhum dado disponível para backtesting'}
            
            # Executar estratégia
            if strategy_name == 'value_betting':
                results = self._run_value_betting_strategy(matches_data)
            elif strategy_name == 'trend_following':
                results = self._run_trend_following_strategy(matches_data)
            elif strategy_name == 'ml_predictions':
                results = self._run_ml_predictions_strategy(matches_data)
            else:
                return {'error': f'Estratégia {strategy_name} não implementada'}
            
            # Salvar resultados
            self._save_backtesting_results(results, strategy_name)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro no backtesting: {e}")
            return {'error': str(e)}
    
    def _run_value_betting_strategy(self, matches_data: pd.DataFrame) -> Dict[str, Any]:
        """Executa estratégia de value betting"""
        bankroll = self.backtesting_config['initial_bankroll']
        bet_size = self.backtesting_config['bet_size_percentage']
        bets = []
        current_bankroll = bankroll
        
        for _, match in matches_data.iterrows():
            # Identificar value bets
            opportunities = self._identify_value_betting(pd.DataFrame([match]))
            
            for opp in opportunities:
                if current_bankroll <= bankroll * (1 - self.backtesting_config['stop_loss']):
                    break  # Stop loss atingido
                
                bet_amount = current_bankroll * bet_size
                odds = opp['odds']
                
                # Simular resultado da aposta
                if self._simulate_bet_result(opp['bet_type'], match):
                    # Vitória
                    profit = bet_amount * (odds - 1)
                    current_bankroll += profit
                    result = 'W'
                else:
                    # Derrota
                    current_bankroll -= bet_amount
                    profit = -bet_amount
                    result = 'L'
                
                bets.append({
                    'match': opp['match'],
                    'bet_type': opp['bet_type'],
                    'odds': odds,
                    'bet_amount': bet_amount,
                    'profit': profit,
                    'result': result,
                    'bankroll': current_bankroll
                })
        
        # Calcular métricas
        total_bets = len(bets)
        winning_bets = len([b for b in bets if b['result'] == 'W'])
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        total_profit = current_bankroll - bankroll
        roi = (total_profit / bankroll) * 100 if bankroll > 0 else 0
        
        return {
            'strategy': 'value_betting',
            'initial_bankroll': bankroll,
            'final_bankroll': current_bankroll,
            'total_profit': total_profit,
            'roi': roi,
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'win_rate': win_rate,
            'bets': bets
        }
    
    def _run_trend_following_strategy(self, matches_data: pd.DataFrame) -> Dict[str, Any]:
        """Executa estratégia de seguir tendências"""
        bankroll = self.backtesting_config['initial_bankroll']
        bet_size = self.backtesting_config['bet_size_percentage']
        bets = []
        current_bankroll = bankroll
        
        # Calcular tendências para cada equipe
        team_trends = {}
        for _, match in matches_data.iterrows():
            for team in [match['home_team'], match['away_team']]:
                if team not in team_trends:
                    team_trends[team] = self._calculate_team_trend_simple(matches_data, team)
        
        for _, match in matches_data.iterrows():
            home_trend = team_trends.get(match['home_team'], 'Unknown')
            away_trend = team_trends.get(match['away_team'], 'Unknown')
            
            # Apostar na equipe com tendência melhor
            if home_trend == 'Good' and away_trend != 'Good':
                bet_type = 'Home Win'
                odds = match['home_odds']
            elif away_trend == 'Good' and home_trend != 'Good':
                bet_type = 'Away Win'
                odds = match['away_odds']
            else:
                continue  # Não apostar se ambas têm tendências similares
            
            if current_bankroll <= bankroll * (1 - self.backtesting_config['stop_loss']):
                break
            
            bet_amount = current_bankroll * bet_size
            
            # Simular resultado
            if self._simulate_bet_result(bet_type, match):
                profit = bet_amount * (odds - 1)
                current_bankroll += profit
                result = 'W'
            else:
                profit = -bet_amount
                current_bankroll -= bet_amount
                result = 'L'
            
            bets.append({
                'match': f"{match['home_team']} vs {match['away_team']}",
                'bet_type': bet_type,
                'odds': odds,
                'bet_amount': bet_amount,
                'profit': profit,
                'result': result,
                'bankroll': current_bankroll
            })
        
        # Calcular métricas
        total_bets = len(bets)
        winning_bets = len([b for b in bets if b['result'] == 'W'])
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        total_profit = current_bankroll - bankroll
        roi = (total_profit / bankroll) * 100 if bankroll > 0 else 0
        
        return {
            'strategy': 'trend_following',
            'initial_bankroll': bankroll,
            'final_bankroll': current_bankroll,
            'total_profit': total_profit,
            'roi': roi,
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'win_rate': win_rate,
            'bets': bets
        }
    
    def _run_ml_predictions_strategy(self, matches_data: pd.DataFrame) -> Dict[str, Any]:
        """Executa estratégia baseada em predições ML"""
        # Esta estratégia seria implementada quando os modelos ML estiverem disponíveis
        return {
            'strategy': 'ml_predictions',
            'error': 'Estratégia ML não implementada ainda',
            'note': 'Implementar quando modelos estiverem treinados'
        }
    
    def _calculate_team_trend_simple(self, matches_data: pd.DataFrame, team_name: str) -> str:
        """Calcula tendência simples de uma equipe"""
        team_matches = matches_data[
            (matches_data['home_team'] == team_name) | 
            (matches_data['away_team'] == team_name)
        ].tail(5)  # Últimas 5 partidas
        
        if len(team_matches) < 3:
            return 'Unknown'
        
        wins = 0
        for _, match in team_matches.iterrows():
            if match['home_team'] == team_name:
                if match['home_goals'] > match['away_goals']:
                    wins += 1
            else:
                if match['away_goals'] > match['home_goals']:
                    wins += 1
        
        win_rate = wins / len(team_matches)
        
        if win_rate >= 0.6:
            return 'Good'
        elif win_rate <= 0.2:
            return 'Poor'
        else:
            return 'Average'
    
    def _simulate_bet_result(self, bet_type: str, match: pd.Series) -> bool:
        """Simula resultado de uma aposta"""
        if bet_type == 'Home Win':
            return match['home_goals'] > match['away_goals']
        elif bet_type == 'Away Win':
            return match['away_goals'] > match['home_goals']
        elif bet_type == 'Draw':
            return match['home_goals'] == match['away_goals']
        elif bet_type == 'Over 2.5':
            return match['total_goals'] > 2.5
        elif bet_type == 'Both Teams Score':
            return match['both_teams_score'] == 1
        else:
            return False
    
    def optimize_hyperparameters(self, 
                               model_type: str,
                               optimization_method: str = 'optuna',
                               n_trials: int = 100) -> Dict[str, Any]:
        """
        Otimiza hiperparâmetros de um modelo
        
        Args:
            model_type: Tipo do modelo
            optimization_method: Método de otimização
            n_trials: Número de tentativas
            
        Returns:
            Resultados da otimização
        """
        try:
            logger.info(f"Otimizando hiperparâmetros para {model_type}")
            
            # Obter dados de treinamento
            from .data_collector import get_training_data
            
            X, y = get_training_data(target_column=model_type)
            if X is None or y is None:
                return {'error': 'Dados de treinamento não disponíveis'}
            
            # Preparar dados
            from .data_preparation import DataPreparationPipeline
            data_pipeline = DataPreparationPipeline()
            X_processed = data_pipeline.run_full_pipeline(X, model_type)
            
            # Dividir dados
            from sklearn.model_selection import train_test_split
            X_train, X_val, y_train, y_val = train_test_split(
                X_processed, y, test_size=0.2, random_state=42
            )
            
            if optimization_method == 'optuna':
                best_params = self._optimize_with_optuna(
                    model_type, X_train, X_val, y_train, y_val, n_trials
                )
            else:
                best_params = self._optimize_with_grid_search(
                    model_type, X_train, X_val, y_train, y_val
                )
            
            # Salvar resultados da otimização
            self._save_optimization_results(best_params, model_type)
            
            return {
                'model_type': model_type,
                'optimization_method': optimization_method,
                'best_parameters': best_params,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização: {e}")
            return {'error': str(e)}
    
    def _optimize_with_optuna(self, 
                             model_type: str,
                             X_train: pd.DataFrame,
                             X_val: pd.DataFrame,
                             y_train: pd.Series,
                             y_val: pd.Series,
                             n_trials: int) -> Dict[str, Any]:
        """Otimiza usando Optuna"""
        def objective(trial):
            # Definir espaço de busca
            if 'xgboost' in model_type:
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_uniform('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.6, 1.0)
                }
                
                model = xgb.XGBClassifier(**params, random_state=42)
            elif 'lightgbm' in model_type:
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_loguniform('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_uniform('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.6, 1.0)
                }
                
                model = lgb.LGBMClassifier(**params, random_state=42)
            else:
                # Random Forest como padrão
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 20),
                    'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                    'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10)
                }
                
                model = RandomForestClassifier(**params, random_state=42)
            
            # Treinar e avaliar
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            
            # Métrica de avaliação
            if len(np.unique(y_val)) > 2:
                score = f1_score(y_val, y_pred, average='macro')
            else:
                score = f1_score(y_val, y_pred)
            
            return score
        
        # Executar otimização
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': n_trials
        }
    
    def _optimize_with_grid_search(self, 
                                  model_type: str,
                                  X_train: pd.DataFrame,
                                  X_val: pd.DataFrame,
                                  y_train: pd.Series,
                                  y_val: pd.Series) -> Dict[str, Any]:
        """Otimiza usando Grid Search"""
        # Definir grid de parâmetros
        if 'xgboost' in model_type:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.1, 0.2]
            }
            model = xgb.XGBClassifier(random_state=42)
        elif 'lightgbm' in model_type:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.1, 0.2]
            }
            model = lgb.LGBMClassifier(random_state=42)
        else:
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5, 10]
            }
            model = RandomForestClassifier(random_state=42)
        
        # Grid search
        grid_search = GridSearchCV(
            model, param_grid, cv=3, scoring='f1_macro', n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
    
    def _save_trend_analysis(self, trends: Dict[str, Any], team_name: str = None, competition: str = None):
        """Salva análise de tendências"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"trend_analysis_{timestamp}.json"
            
            if team_name:
                filename = f"trend_analysis_{team_name}_{timestamp}.json"
            elif competition:
                filename = f"trend_analysis_{competition}_{timestamp}.json"
            
            filepath = self.results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(trends, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Análise de tendências salva em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise de tendências: {e}")
    
    def _save_backtesting_results(self, results: Dict[str, Any], strategy_name: str):
        """Salva resultados do backtesting"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backtesting_{strategy_name}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Resultados do backtesting salvos em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados do backtesting: {e}")
    
    def _save_optimization_results(self, results: Dict[str, Any], model_type: str):
        """Salva resultados da otimização"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"optimization_{model_type}_{timestamp}.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Resultados da otimização salvos em: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados da otimização: {e}")

# Instância global
advanced_features = AdvancedFeatures()

# Funções de conveniência
def analyze_trends(**kwargs) -> Dict[str, Any]:
    """Analisa tendências"""
    return advanced_features.analyze_trends(**kwargs)

def run_backtesting(**kwargs) -> Dict[str, Any]:
    """Executa backtesting"""
    return advanced_features.run_backtesting(**kwargs)

def optimize_hyperparameters(**kwargs) -> Dict[str, Any]:
    """Otimiza hiperparâmetros"""
    return advanced_features.optimize_hyperparameters(**kwargs)
