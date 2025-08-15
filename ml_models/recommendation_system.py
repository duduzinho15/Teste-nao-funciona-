#!/usr/bin/env python3
"""
Sistema avançado de recomendações de apostas integrado com Machine Learning
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime, timedelta
import warnings
from pathlib import Path
import json

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .ml_models import MLModelManager
from .sentiment_analyzer import SentimentAnalyzer

# Configurar logging
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class BettingRecommendationSystem:
    """Sistema de recomendações de apostas baseado em ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.ml_manager = MLModelManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Configurações de risco
        self.risk_levels = {
            'low': {'confidence_threshold': 0.8, 'max_bet_amount': 100},
            'medium': {'confidence_threshold': 0.7, 'max_bet_amount': 200},
            'high': {'confidence_threshold': 0.6, 'max_bet_amount': 500}
        }
        
        # Tipos de apostas suportados
        self.bet_types = {
            'match_result': ['home_win', 'draw', 'away_win'],
            'total_goals': ['over_0.5', 'over_1.5', 'over_2.5', 'under_2.5', 'under_1.5'],
            'both_teams_score': ['yes', 'no'],
            'double_chance': ['home_or_draw', 'away_or_draw', 'home_or_away'],
            'correct_score': ['1-0', '2-0', '2-1', '1-1', '0-0', '0-1', '1-2', '0-2']
        }
    
    def analyze_match_data(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados de uma partida para gerar recomendações"""
        try:
            analysis = {
                'match_id': match_data.get('match_id'),
                'home_team': match_data.get('home_team'),
                'away_team': match_data.get('away_team'),
                'competition': match_data.get('competition'),
                'match_date': match_data.get('match_date'),
                'analysis_timestamp': datetime.now().isoformat(),
                'features': {},
                'predictions': {},
                'recommendations': {}
            }
            
            # Extrair features numéricas
            numeric_features = self._extract_numeric_features(match_data)
            analysis['features']['numeric'] = numeric_features
            
            # Extrair features categóricas
            categorical_features = self._extract_categorical_features(match_data)
            analysis['features']['categorical'] = categorical_features
            
            # Análise de sentimento se disponível
            if 'news_sentiment' in match_data:
                sentiment_analysis = self.sentiment_analyzer.analyze_sentiment_hybrid(
                    match_data['news_sentiment']
                )
                analysis['features']['sentiment'] = sentiment_analysis
            
            # Análise de forma recente
            form_analysis = self._analyze_recent_form(match_data)
            analysis['features']['form'] = form_analysis
            
            # Análise de head-to-head
            h2h_analysis = self._analyze_head_to_head(match_data)
            analysis['features']['head_to_head'] = h2h_analysis
            
            logger.info(f"Análise de dados concluída para partida {match_data.get('match_id')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise de dados da partida: {e}")
            raise
    
    def _extract_numeric_features(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Extrai features numéricas da partida"""
        features = {}
        
        # Estatísticas básicas
        basic_stats = [
            'home_goals_scored', 'away_goals_scored',
            'home_goals_conceded', 'away_goals_conceded',
            'home_shots', 'away_shots',
            'home_shots_on_target', 'away_shots_on_target',
            'home_possession', 'away_possession'
        ]
        
        for stat in basic_stats:
            if stat in match_data:
                features[stat] = float(match_data[stat])
        
        # Estatísticas avançadas (se disponíveis)
        advanced_stats = [
            'home_xg', 'away_xg', 'home_xa', 'away_xa',
            'home_attacking_strength', 'away_attacking_strength',
            'home_defensive_strength', 'away_defensive_strength'
        ]
        
        for stat in advanced_stats:
            if stat in match_data:
                features[stat] = float(match_data[stat])
        
        # Calcular features derivadas
        if 'home_goals_scored' in features and 'away_goals_conceded' in features:
            features['home_attack_vs_away_defense'] = features['home_goals_scored'] / max(features['away_goals_conceded'], 0.1)
        
        if 'away_goals_scored' in features and 'home_goals_conceded' in features:
            features['away_attack_vs_home_defense'] = features['away_goals_scored'] / max(features['home_goals_conceded'], 0.1)
        
        return features
    
    def _extract_categorical_features(self, match_data: Dict[str, Any]) -> Dict[str, str]:
        """Extrai features categóricas da partida"""
        features = {}
        
        categorical_vars = [
            'home_formation', 'away_formation',
            'home_manager', 'away_manager',
            'stadium', 'weather_conditions',
            'referee', 'competition_type'
        ]
        
        for var in categorical_vars:
            if var in match_data:
                features[var] = str(match_data[var])
        
        return features
    
    def _analyze_recent_form(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a forma recente das equipes"""
        form_analysis = {}
        
        # Forma dos últimos 5 jogos
        for team_type in ['home', 'away']:
            team_form_key = f'{team_type}_recent_form'
            if team_form_key in match_data:
                recent_results = match_data[team_form_key]
                if isinstance(recent_results, list) and len(recent_results) >= 5:
                    # Calcular pontos (3 para vitória, 1 para empate, 0 para derrota)
                    points = 0
                    for result in recent_results[-5:]:
                        if result == 'W':
                            points += 3
                        elif result == 'D':
                            points += 1
                    
                    form_analysis[f'{team_type}_form_points'] = points
                    form_analysis[f'{team_type}_form_percentage'] = (points / 15) * 100
                    
                    # Tendência (últimos 3 jogos vs anteriores)
                    if len(recent_results) >= 3:
                        recent_trend = recent_results[-3:]
                        previous_trend = recent_results[-5:-2]
                        
                        recent_points = sum([3 if r == 'W' else 1 if r == 'D' else 0 for r in recent_trend])
                        previous_points = sum([3 if r == 'W' else 1 if r == 'D' else 0 for r in previous_trend])
                        
                        form_analysis[f'{team_type}_form_trend'] = 'improving' if recent_points > previous_points else 'declining' if recent_points < previous_points else 'stable'
        
        return form_analysis
    
    def _analyze_head_to_head(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa histórico de confrontos diretos"""
        h2h_analysis = {}
        
        if 'head_to_head' in match_data:
            h2h_data = match_data['head_to_head']
            
            if isinstance(h2h_data, list) and len(h2h_data) > 0:
                # Estatísticas dos últimos 10 confrontos
                recent_h2h = h2h_data[-10:] if len(h2h_data) >= 10 else h2h_data
                
                home_wins = sum([1 for match in recent_h2h if match.get('winner') == 'home'])
                away_wins = sum([1 for match in recent_h2h if match.get('winner') == 'away'])
                draws = len(recent_h2h) - home_wins - away_wins
                
                h2h_analysis['total_matches'] = len(recent_h2h)
                h2h_analysis['home_wins'] = home_wins
                h2h_analysis['away_wins'] = away_wins
                h2h_analysis['draws'] = draws
                h2h_analysis['home_win_rate'] = (home_wins / len(recent_h2h)) * 100
                h2h_analysis['away_win_rate'] = (away_wins / len(recent_h2h)) * 100
                h2h_analysis['draw_rate'] = (draws / len(recent_h2h)) * 100
                
                # Média de gols
                if all('home_goals' in match and 'away_goals' in match for match in recent_h2h):
                    total_goals = sum([match['home_goals'] + match['away_goals'] for match in recent_h2h])
                    h2h_analysis['avg_goals_per_match'] = total_goals / len(recent_h2h)
        
        return h2h_analysis
    
    @timed_cache_result(ttl_hours=2)
    def generate_predictions(self, match_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera previsões para diferentes tipos de apostas"""
        try:
            predictions = {
                'match_id': match_analysis['match_id'],
                'timestamp': datetime.now().isoformat(),
                'predictions': {}
            }
            
            # Preparar features para ML
            features_df = self._prepare_features_for_ml(match_analysis)
            
            if features_df is None or features_df.empty:
                logger.warning("Features insuficientes para gerar previsões")
                return predictions
            
            # Previsões para resultado da partida
            try:
                result_prediction = self._predict_match_result(features_df)
                predictions['predictions']['match_result'] = result_prediction
            except Exception as e:
                logger.warning(f"Erro na previsão de resultado: {e}")
            
            # Previsões para total de gols
            try:
                goals_prediction = self._predict_total_goals(features_df)
                predictions['predictions']['total_goals'] = goals_prediction
            except Exception as e:
                logger.warning(f"Erro na previsão de gols: {e}")
            
            # Previsões para ambos marcam
            try:
                bts_prediction = self._predict_both_teams_score(features_df)
                predictions['predictions']['both_teams_score'] = bts_prediction
            except Exception as e:
                logger.warning(f"Erro na previsão de ambos marcam: {e}")
            
            logger.info(f"Previsões geradas para partida {match_analysis['match_id']}")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao gerar previsões: {e}")
            raise
    
    def _prepare_features_for_ml(self, match_analysis: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Prepara features para modelos de ML"""
        try:
            features = {}
            
            # Combinar todas as features
            if 'numeric' in match_analysis['features']:
                features.update(match_analysis['features']['numeric'])
            
            if 'form' in match_analysis['features']:
                features.update(match_analysis['features']['form'])
            
            if 'head_to_head' in match_analysis['features']:
                features.update(match_analysis['features']['head_to_head'])
            
            # Adicionar features de sentimento se disponível
            if 'sentiment' in match_analysis['features']:
                sentiment = match_analysis['features']['sentiment']
                features['sentiment_score'] = sentiment.get('sentiment_score', 0)
                features['sentiment_confidence'] = sentiment.get('confidence', 0)
            
            if not features:
                return None
            
            # Converter para DataFrame
            features_df = pd.DataFrame([features])
            
            # Tratar valores NaN
            features_df = features_df.fillna(0)
            
            return features_df
            
        except Exception as e:
            logger.error(f"Erro ao preparar features: {e}")
            return None
    
    def _predict_match_result(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Previsão para resultado da partida"""
        try:
            # Tentar usar modelo treinado
            model_key = 'result_prediction_ensemble'
            if model_key in self.ml_manager.models:
                prediction = self.ml_manager.make_prediction(model_key, features_df)
                return {
                    'method': 'ml_model',
                    'prediction': prediction['prediction'],
                    'confidence': prediction['confidence'],
                    'probabilities': prediction.get('probabilities', [])
                }
            
            # Fallback para análise estatística
            return self._statistical_result_prediction(features_df)
            
        except Exception as e:
            logger.error(f"Erro na previsão de resultado: {e}")
            return {'method': 'error', 'error': str(e)}
    
    def _predict_total_goals(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Previsão para total de gols"""
        try:
            # Tentar usar modelo treinado
            model_key = 'goals_prediction_ensemble'
            if model_key in self.ml_manager.models:
                prediction = self.ml_manager.make_prediction(model_key, features_df)
                return {
                    'method': 'ml_model',
                    'prediction': prediction['prediction'],
                    'confidence': prediction['confidence'],
                    'probabilities': prediction.get('probabilities', [])
                }
            
            # Fallback para análise estatística
            return self._statistical_goals_prediction(features_df)
            
        except Exception as e:
            logger.error(f"Erro na previsão de gols: {e}")
            return {'method': 'error', 'error': str(e)}
    
    def _predict_both_teams_score(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Previsão para ambos marcam"""
        try:
            # Análise baseada em estatísticas de ataque e defesa
            home_attack = features_df.get('home_goals_scored', [0])[0]
            away_attack = features_df.get('away_goals_scored', [0])[0]
            home_defense = features_df.get('home_goals_conceded', [0])[0]
            away_defense = features_df.get('away_goals_conceded', [0])[0]
            
            # Probabilidade de ambos marcarem
            home_score_prob = min(0.9, max(0.1, home_attack / max(away_defense, 0.1)))
            away_score_prob = min(0.9, max(0.1, away_attack / max(home_defense, 0.1)))
            
            both_score_prob = home_score_prob * away_score_prob
            
            prediction = 'yes' if both_score_prob > 0.5 else 'no'
            confidence = max(both_score_prob, 1 - both_score_prob)
            
            return {
                'method': 'statistical',
                'prediction': prediction,
                'confidence': confidence,
                'home_score_probability': home_score_prob,
                'away_score_probability': away_score_prob,
                'both_score_probability': both_score_prob
            }
            
        except Exception as e:
            logger.error(f"Erro na previsão de ambos marcam: {e}")
            return {'method': 'error', 'error': str(e)}
    
    def _statistical_result_prediction(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Previsão estatística para resultado da partida"""
        try:
            # Calcular força relativa das equipes
            home_strength = (
                features_df.get('home_goals_scored', [0])[0] * 0.4 +
                (15 - features_df.get('home_goals_conceded', [0])[0]) * 0.3 +
                features_df.get('home_form_percentage', [50])[0] * 0.3
            )
            
            away_strength = (
                features_df.get('away_goals_scored', [0])[0] * 0.4 +
                (15 - features_df.get('away_goals_conceded', [0])[0]) * 0.3 +
                features_df.get('away_form_percentage', [50])[0] * 0.3
            )
            
            # Ajustar com head-to-head se disponível
            if 'home_win_rate' in features_df.columns:
                h2h_factor = (features_df['home_win_rate'][0] - 50) / 100
                home_strength += h2h_factor * 10
            
            # Determinar resultado mais provável
            strength_diff = home_strength - away_strength
            
            if strength_diff > 5:
                prediction = 'home_win'
                confidence = min(0.9, 0.5 + abs(strength_diff) / 50)
            elif strength_diff < -5:
                prediction = 'away_win'
                confidence = min(0.9, 0.5 + abs(strength_diff) / 50)
            else:
                prediction = 'draw'
                confidence = 0.6
            
            return {
                'method': 'statistical',
                'prediction': prediction,
                'confidence': confidence,
                'home_strength': home_strength,
                'away_strength': away_strength,
                'strength_difference': strength_diff
            }
            
        except Exception as e:
            logger.error(f"Erro na previsão estatística: {e}")
            return {'method': 'error', 'error': str(e)}
    
    def _statistical_goals_prediction(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Previsão estatística para total de gols"""
        try:
            # Calcular média esperada de gols
            home_goals_for = features_df.get('home_goals_scored', [0])[0]
            away_goals_for = features_df.get('away_goals_scored', [0])[0]
            home_goals_against = features_df.get('home_goals_conceded', [0])[0]
            away_goals_against = features_df.get('away_goals_conceded', [0])[0]
            
            expected_goals = (home_goals_for + away_goals_for) / 2
            
            # Determinar over/under mais provável
            if expected_goals > 2.5:
                prediction = 'over_2.5'
                confidence = min(0.9, (expected_goals - 2.5) / 2)
            elif expected_goals > 1.5:
                prediction = 'over_1.5'
                confidence = min(0.9, (expected_goals - 1.5) / 1)
            else:
                prediction = 'under_1.5'
                confidence = min(0.9, (1.5 - expected_goals) / 1)
            
            return {
                'method': 'statistical',
                'prediction': prediction,
                'confidence': confidence,
                'expected_goals': expected_goals,
                'home_goals_for': home_goals_for,
                'away_goals_for': away_goals_for
            }
            
        except Exception as e:
            logger.error(f"Erro na previsão estatística de gols: {e}")
            return {'method': 'error', 'error': str(e)}
    
    def generate_betting_recommendations(self, predictions: Dict[str, Any], 
                                       risk_level: str = 'medium',
                                       max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Gera recomendações de apostas baseadas nas previsões"""
        try:
            if risk_level not in self.risk_levels:
                risk_level = 'medium'
            
            risk_config = self.risk_levels[risk_level]
            recommendations = []
            
            for bet_type, prediction_data in predictions['predictions'].items():
                if prediction_data.get('method') == 'error':
                    continue
                
                confidence = prediction_data.get('confidence', 0)
                
                # Verificar se atende ao threshold de confiança
                if confidence >= risk_config['confidence_threshold']:
                    recommendation = {
                        'match_id': predictions['match_id'],
                        'bet_type': bet_type,
                        'prediction': prediction_data['prediction'],
                        'confidence': confidence,
                        'method': prediction_data['method'],
                        'risk_level': risk_level,
                        'recommended_bet_amount': self._calculate_bet_amount(confidence, risk_level),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Adicionar informações específicas do tipo de aposta
                    if bet_type == 'match_result':
                        recommendation['odds_estimate'] = self._estimate_odds(confidence)
                        recommendation['value_rating'] = self._calculate_value_rating(prediction_data)
                    
                    recommendations.append(recommendation)
            
            # Ordenar por confiança e limitar número de recomendações
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            recommendations = recommendations[:max_recommendations]
            
            logger.info(f"Geradas {len(recommendations)} recomendações para nível de risco {risk_level}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return []
    
    def _calculate_bet_amount(self, confidence: float, risk_level: str) -> float:
        """Calcula valor recomendado para aposta"""
        risk_config = self.risk_levels[risk_level]
        base_amount = risk_config['max_bet_amount']
        
        # Ajustar baseado na confiança
        confidence_multiplier = confidence ** 2  # Quadrado para dar mais peso à alta confiança
        
        return round(base_amount * confidence_multiplier, 2)
    
    def _estimate_odds(self, confidence: float) -> float:
        """Estima odds baseado na confiança"""
        # Fórmula simples: odds = 1 / (confiança * 0.8)
        # O fator 0.8 representa margem da casa de apostas
        estimated_odds = 1 / (confidence * 0.8)
        return round(estimated_odds, 2)
    
    def _calculate_value_rating(self, prediction_data: Dict[str, Any]) -> str:
        """Calcula rating de valor da aposta"""
        confidence = prediction_data.get('confidence', 0)
        
        if confidence >= 0.8:
            return 'excellent'
        elif confidence >= 0.7:
            return 'good'
        elif confidence >= 0.6:
            return 'fair'
        else:
            return 'poor'
    
    def get_recommendation_summary(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera resumo das recomendações"""
        if not recommendations:
            return {'error': 'Nenhuma recomendação disponível'}
        
        summary = {
            'total_recommendations': len(recommendations),
            'average_confidence': np.mean([r['confidence'] for r in recommendations]),
            'risk_levels': {},
            'bet_types': {},
            'total_recommended_amount': sum([r['recommended_bet_amount'] for r in recommendations]),
            'timestamp': datetime.now().isoformat()
        }
        
        # Distribuição por nível de risco
        for rec in recommendations:
            risk_level = rec['risk_level']
            summary['risk_levels'][risk_level] = summary['risk_levels'].get(risk_level, 0) + 1
        
        # Distribuição por tipo de aposta
        for rec in recommendations:
            bet_type = rec['bet_type']
            summary['bet_types'][bet_type] = summary['bet_types'].get(bet_type, 0) + 1
        
        return summary

# Instância global
recommendation_system = BettingRecommendationSystem()

# Funções de conveniência
def analyze_match(match_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa dados de uma partida"""
    return recommendation_system.analyze_match_data(match_data)

def generate_predictions(match_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Gera previsões para uma partida"""
    return recommendation_system.generate_predictions(match_analysis)

def get_betting_recommendations(predictions: Dict[str, Any], 
                              risk_level: str = 'medium',
                              max_recommendations: int = 5) -> List[Dict[str, Any]]:
    """Gera recomendações de apostas"""
    return recommendation_system.generate_betting_recommendations(
        predictions, risk_level, max_recommendations
    )

def get_recommendation_summary(recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera resumo das recomendações"""
    return recommendation_system.get_recommendation_summary(recommendations)
