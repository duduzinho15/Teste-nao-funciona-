#!/usr/bin/env python3
"""
Sistema de integração com banco de dados PostgreSQL para Machine Learning
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result

logger = logging.getLogger(__name__)

class DatabaseIntegration:
    """Integração com banco de dados PostgreSQL para ML"""
    
    def __init__(self):
        self.config = get_ml_config()
        self.connection = None
        self.engine = None
        self.SessionLocal = None
        
        # Configurações de banco
        self.db_config = self._load_database_config()
        
        # Inicializar conexão
        self._initialize_connection()
    
    def _load_database_config(self) -> Dict[str, str]:
        """Carrega configurações do banco de dados"""
        # Tentar carregar de variáveis de ambiente
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'apostapro'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'schema': os.getenv('DB_SCHEMA', 'public')
        }
        
        # Se não houver configurações, usar valores padrão para demonstração
        if not db_config['password']:
            logger.warning("Configurações de banco não encontradas. Usando modo demonstração.")
            db_config['demo_mode'] = True
        else:
            db_config['demo_mode'] = False
        
        return db_config
    
    def _initialize_connection(self):
        """Inicializa conexão com banco de dados"""
        try:
            if not self.db_config.get('demo_mode', False):
                # Conexão real com PostgreSQL
                self.connection = psycopg2.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    database=self.db_config['database'],
                    user=self.db_config['user'],
                    password=self.db_config['password']
                )
                
                # Criar engine SQLAlchemy
                connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
                self.engine = create_engine(connection_string)
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                
                logger.info("Conexão com PostgreSQL estabelecida com sucesso")
                
            else:
                logger.info("Modo demonstração ativado - usando dados simulados")
                
        except Exception as e:
            logger.error(f"Erro ao conectar com banco: {e}")
            logger.info("Continuando em modo demonstração")
            self.db_config['demo_mode'] = True
    
    def test_connection(self) -> bool:
        """Testa conexão com banco de dados"""
        try:
            if self.db_config.get('demo_mode', False):
                return True
            
            if self.connection and not self.connection.closed:
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    @timed_cache_result(ttl_hours=1)
    def get_matches_data(self, 
                        start_date: str = None,
                        end_date: str = None,
                        competition: str = None,
                        limit: int = 1000) -> pd.DataFrame:
        """
        Obtém dados de partidas do banco de dados
        
        Args:
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            competition: Nome da competição
            limit: Limite de registros
            
        Returns:
            DataFrame com dados das partidas
        """
        try:
            if self.db_config.get('demo_mode', False):
                # Retornar dados simulados
                return self._get_demo_matches_data(start_date, end_date, competition, limit)
            
            # Query real para PostgreSQL
            query = """
                SELECT 
                    m.id as match_id,
                    m.date,
                    m.competition,
                    m.season,
                    m.home_team,
                    m.away_team,
                    m.home_goals,
                    m.away_goals,
                    m.total_goals,
                    CASE WHEN m.home_goals > 0 AND m.away_goals > 0 THEN 1 ELSE 0 END as both_teams_score,
                    CASE 
                        WHEN m.home_goals > m.away_goals THEN 'home_win'
                        WHEN m.away_goals > m.home_goals THEN 'away_win'
                        ELSE 'draw'
                    END as result,
                    m.home_possession,
                    m.away_possession,
                    m.home_shots,
                    m.away_shots,
                    m.home_shots_on_target,
                    m.away_shots_on_target,
                    m.home_corners,
                    m.away_corners,
                    m.home_fouls,
                    m.away_fouls,
                    m.home_yellow_cards,
                    m.away_yellow_cards,
                    m.home_red_cards,
                    m.away_red_cards,
                    m.home_form_last_5,
                    m.away_form_last_5,
                    m.home_attacking_strength,
                    m.away_attacking_strength,
                    m.home_defensive_strength,
                    m.away_defensive_strength,
                    m.home_xg,
                    m.away_xg,
                    m.home_xa,
                    m.away_xa,
                    EXTRACT(DOW FROM m.date) as day_of_week,
                    EXTRACT(MONTH FROM m.date) as month,
                    CASE WHEN EXTRACT(DOW FROM m.date) IN (5, 6) THEN 1 ELSE 0 END as is_weekend,
                    m.home_team_rank,
                    m.away_team_rank,
                    m.home_team_points,
                    m.away_team_points,
                    m.h2h_home_wins,
                    m.h2h_away_wins,
                    m.h2h_draws,
                    m.home_odds,
                    m.away_odds,
                    m.draw_odds,
                    m.over_2_5_odds,
                    m.both_teams_score_odds
                FROM matches m
                WHERE 1=1
            """
            
            params = []
            
            if start_date:
                query += " AND m.date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND m.date <= %s"
                params.append(end_date)
            
            if competition:
                query += " AND m.competition = %s"
                params.append(competition)
            
            query += " ORDER BY m.date DESC LIMIT %s"
            params.append(limit)
            
            # Executar query
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
            
            # Converter para DataFrame
            df = pd.DataFrame(results)
            
            if not df.empty:
                # Converter tipos de dados
                df['date'] = pd.to_datetime(df['date'])
                df['day_of_week'] = df['day_of_week'].astype(int)
                df['month'] = df['month'].astype(int)
                
                # Adicionar features derivadas
                df = self._add_derived_features(df)
            
            logger.info(f"Dados obtidos do banco: {len(df)} partidas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do banco: {e}")
            # Fallback para dados simulados
            return self._get_demo_matches_data(start_date, end_date, competition, limit)
    
    def _get_demo_matches_data(self, 
                              start_date: str = None,
                              end_date: str = None,
                              competition: str = None,
                              limit: int = 1000) -> pd.DataFrame:
        """Retorna dados simulados para demonstração"""
        from .data_collector import collect_historical_data
        
        # Usar o coletor de dados existente
        data = collect_historical_data(
            start_date=start_date,
            end_date=end_date,
            competitions=[competition] if competition else None,
            min_matches=min(limit, 100)
        )
        
        return data.head(limit)
    
    @timed_cache_result(ttl_hours=6)
    def get_team_stats(self, team_name: str, last_n_matches: int = 10) -> Dict[str, Any]:
        """
        Obtém estatísticas de uma equipe
        
        Args:
            team_name: Nome da equipe
            last_n_matches: Número de últimas partidas para análise
            
        Returns:
            Dicionário com estatísticas da equipe
        """
        try:
            if self.db_config.get('demo_mode', False):
                return self._get_demo_team_stats(team_name, last_n_matches)
            
            # Query real para estatísticas da equipe
            query = """
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN home_team = %s AND home_goals > away_goals THEN 1
                             WHEN away_team = %s AND away_goals > home_goals THEN 1
                             ELSE 0 END) as wins,
                    SUM(CASE WHEN home_team = %s AND home_goals = away_goals THEN 1
                             WHEN away_team = %s AND away_goals = home_goals THEN 1
                             ELSE 0 END) as draws,
                    SUM(CASE WHEN home_team = %s AND home_goals < away_goals THEN 1
                             WHEN away_team = %s AND away_goals < home_goals THEN 1
                             ELSE 0 END) as losses,
                    AVG(CASE WHEN home_team = %s THEN home_goals
                             WHEN away_team = %s THEN away_goals END) as avg_goals_scored,
                    AVG(CASE WHEN home_team = %s THEN away_goals
                             WHEN away_team = %s THEN home_goals END) as avg_goals_conceded,
                    AVG(CASE WHEN home_team = %s THEN home_possession
                             WHEN away_team = %s THEN away_possession END) as avg_possession,
                    AVG(CASE WHEN home_team = %s THEN home_shots
                             WHEN away_team = %s THEN away_shots END) as avg_shots,
                    AVG(CASE WHEN home_team = %s THEN home_xg
                             WHEN away_team = %s THEN away_xg END) as avg_xg
                FROM matches 
                WHERE (home_team = %s OR away_team = %s)
                AND date >= CURRENT_DATE - INTERVAL '1 year'
                ORDER BY date DESC
                LIMIT %s
            """
            
            params = [team_name] * 12 + [last_n_matches]
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
            
            if result:
                stats = dict(result)
                stats['win_rate'] = stats['wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
                stats['form'] = (stats['wins'] * 3 + stats['draws']) / (stats['total_matches'] * 3)
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas da equipe {team_name}: {e}")
            return self._get_demo_team_stats(team_name, last_n_matches)
    
    def _get_demo_team_stats(self, team_name: str, last_n_matches: int = 10) -> Dict[str, Any]:
        """Retorna estatísticas simuladas para demonstração"""
        import random
        
        # Estatísticas simuladas realistas
        total_matches = random.randint(30, 50)
        wins = random.randint(10, 25)
        draws = random.randint(5, 15)
        losses = total_matches - wins - draws
        
        return {
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / total_matches,
            'form': (wins * 3 + draws) / (total_matches * 3),
            'avg_goals_scored': round(random.uniform(1.2, 2.1), 2),
            'avg_goals_conceded': round(random.uniform(0.8, 1.8), 2),
            'avg_possession': round(random.uniform(45, 65), 1),
            'avg_shots': round(random.uniform(10, 18), 1),
            'avg_xg': round(random.uniform(1.0, 2.5), 2)
        }
    
    @timed_cache_result(ttl_hours=12)
    def get_head_to_head_stats(self, team1: str, team2: str) -> Dict[str, Any]:
        """
        Obtém estatísticas head-to-head entre duas equipes
        
        Args:
            team1: Nome da primeira equipe
            team2: Nome da segunda equipe
            
        Returns:
            Dicionário com estatísticas head-to-head
        """
        try:
            if self.db_config.get('demo_mode', False):
                return self._get_demo_h2h_stats(team1, team2)
            
            # Query real para head-to-head
            query = """
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN home_team = %s AND home_goals > away_goals THEN 1
                             WHEN away_team = %s AND away_goals > home_goals THEN 1
                             ELSE 0 END) as team1_wins,
                    SUM(CASE WHEN home_team = %s AND home_goals = away_goals THEN 1
                             WHEN away_team = %s AND away_goals = home_goals THEN 1
                             ELSE 0 END) as draws,
                    SUM(CASE WHEN home_team = %s AND home_goals < away_goals THEN 1
                             WHEN away_team = %s AND away_goals < home_goals THEN 1
                             ELSE 0 END) as team2_wins,
                    AVG(home_goals + away_goals) as avg_total_goals,
                    AVG(CASE WHEN home_goals > 0 AND away_goals > 0 THEN 1 ELSE 0 END) as both_teams_score_rate
                FROM matches 
                WHERE (home_team = %s AND away_team = %s) 
                   OR (home_team = %s AND away_team = %s)
                AND date >= CURRENT_DATE - INTERVAL '3 years'
            """
            
            params = [team1, team1, team1, team1, team1, team1, team1, team2, team2, team1]
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
            
            if result:
                stats = dict(result)
                stats['team1_win_rate'] = stats['team1_wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
                stats['team2_win_rate'] = stats['team2_wins'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
                stats['draw_rate'] = stats['draws'] / stats['total_matches'] if stats['total_matches'] > 0 else 0
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas H2H entre {team1} e {team2}: {e}")
            return self._get_demo_h2h_stats(team1, team2)
    
    def _get_demo_h2h_stats(self, team1: str, team2: str) -> Dict[str, Any]:
        """Retorna estatísticas H2H simuladas para demonstração"""
        import random
        
        total_matches = random.randint(5, 15)
        team1_wins = random.randint(2, total_matches - 2)
        team2_wins = random.randint(1, total_matches - team1_wins - 1)
        draws = total_matches - team1_wins - team2_wins
        
        return {
            'total_matches': total_matches,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'team1_win_rate': team1_wins / total_matches,
            'team2_win_rate': team2_wins / total_matches,
            'draw_rate': draws / total_matches,
            'avg_total_goals': round(random.uniform(2.0, 3.5), 2),
            'both_teams_score_rate': round(random.uniform(0.4, 0.8), 2)
        }
    
    def save_prediction_result(self, 
                              match_id: str,
                              prediction_type: str,
                              prediction: str,
                              confidence: float,
                              actual_result: str = None,
                              bet_amount: float = None,
                              profit_loss: float = None) -> bool:
        """
        Salva resultado de uma predição para análise posterior
        
        Args:
            match_id: ID da partida
            prediction_type: Tipo de predição
            prediction: Predição feita
            confidence: Confiança da predição
            actual_result: Resultado real (se disponível)
            bet_amount: Valor apostado
            profit_loss: Lucro/prejuízo
            
        Returns:
            True se salvo com sucesso
        """
        try:
            if self.db_config.get('demo_mode', False):
                # Em modo demo, apenas logar
                logger.info(f"Demo: Predição salva - {match_id}, {prediction_type}, {prediction}, confiança: {confidence}")
                return True
            
            # Query para inserir predição
            query = """
                INSERT INTO ml_predictions (
                    match_id, prediction_type, prediction, confidence, 
                    actual_result, bet_amount, profit_loss, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = [
                match_id, prediction_type, prediction, confidence,
                actual_result, bet_amount, profit_loss, datetime.now()
            ]
            
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
            
            logger.info(f"Predição salva com sucesso: {match_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar predição: {e}")
            return False
    
    def get_prediction_accuracy(self, 
                               prediction_type: str = None,
                               days_back: int = 30) -> Dict[str, Any]:
        """
        Obtém precisão das predições salvas
        
        Args:
            prediction_type: Tipo de predição específico
            days_back: Número de dias para trás
            
        Returns:
            Dicionário com métricas de precisão
        """
        try:
            if self.db_config.get('demo_mode', False):
                return self._get_demo_prediction_accuracy(prediction_type, days_back)
            
            # Query para calcular precisão
            query = """
                SELECT 
                    prediction_type,
                    COUNT(*) as total_predictions,
                    SUM(CASE WHEN prediction = actual_result THEN 1 ELSE 0 END) as correct_predictions,
                    AVG(confidence) as avg_confidence,
                    AVG(bet_amount) as avg_bet_amount,
                    SUM(profit_loss) as total_profit_loss
                FROM ml_predictions 
                WHERE actual_result IS NOT NULL
                AND created_at >= CURRENT_DATE - INTERVAL '%s days'
            """
            
            if prediction_type:
                query += " AND prediction_type = %s"
                params = [f"{days_back} days", prediction_type]
            else:
                params = [f"{days_back} days"]
            
            query += " GROUP BY prediction_type"
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
            
            accuracy_stats = {}
            for result in results:
                stats = dict(result)
                stats['accuracy'] = stats['correct_predictions'] / stats['total_predictions']
                accuracy_stats[stats['prediction_type']] = stats
            
            return accuracy_stats
            
        except Exception as e:
            logger.error(f"Erro ao obter precisão das predições: {e}")
            return self._get_demo_prediction_accuracy(prediction_type, days_back)
    
    def _get_demo_prediction_accuracy(self, prediction_type: str = None, days_back: int = 30) -> Dict[str, Any]:
        """Retorna precisão simulada para demonstração"""
        import random
        
        if prediction_type:
            types = [prediction_type]
        else:
            types = ['result_prediction', 'total_goals_prediction', 'both_teams_score_prediction']
        
        accuracy_stats = {}
        for pred_type in types:
            total = random.randint(50, 200)
            correct = random.randint(int(total * 0.6), int(total * 0.8))
            
            accuracy_stats[pred_type] = {
                'prediction_type': pred_type,
                'total_predictions': total,
                'correct_predictions': correct,
                'accuracy': correct / total,
                'avg_confidence': round(random.uniform(0.65, 0.85), 3),
                'avg_bet_amount': round(random.uniform(50, 200), 2),
                'total_profit_loss': round(random.uniform(-500, 1000), 2)
            }
        
        return accuracy_stats
    
    def close_connection(self):
        """Fecha conexão com banco de dados"""
        try:
            if self.connection and not self.connection.closed:
                self.connection.close()
                logger.info("Conexão com banco fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão: {e}")

# Instância global
db_integration = DatabaseIntegration()

# Funções de conveniência
def get_matches_data(**kwargs) -> pd.DataFrame:
    """Obtém dados de partidas do banco"""
    return db_integration.get_matches_data(**kwargs)

def get_team_stats(team_name: str, **kwargs) -> Dict[str, Any]:
    """Obtém estatísticas de uma equipe"""
    return db_integration.get_team_stats(team_name, **kwargs)

def get_head_to_head_stats(team1: str, team2: str) -> Dict[str, Any]:
    """Obtém estatísticas head-to-head"""
    return db_integration.get_head_to_head_stats(team1, team2)

def save_prediction_result(**kwargs) -> bool:
    """Salva resultado de predição"""
    return db_integration.save_prediction_result(**kwargs)

def get_prediction_accuracy(**kwargs) -> Dict[str, Any]:
    """Obtém precisão das predições"""
    return db_integration.get_prediction_accuracy(**kwargs)

def test_database_connection() -> bool:
    """Testa conexão com banco de dados"""
    return db_integration.test_connection()
