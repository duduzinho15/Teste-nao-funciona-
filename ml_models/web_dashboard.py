#!/usr/bin/env python3
"""
Dashboard web interativo para visualização de dados ML e apostas
"""
import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import warnings
warnings.filterwarnings('ignore')

from .config import get_ml_config
from .cache_manager import cache_result, timed_cache_result
from .production_monitoring import get_system_dashboard
from .betting_apis_integration import get_market_analysis

logger = logging.getLogger(__name__)

class WebDashboard:
    """Sistema de dashboard web interativo"""
    
    def __init__(self):
        self.config = get_ml_config()
        
        # Diretórios
        self.dashboard_dir = Path(self.config.monitoring_dir) / "web_dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações do dashboard
        self.dashboard_config = {
            'refresh_interval': 30,  # segundos
            'max_data_points': 1000,
            'chart_colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        }
    
    def generate_system_overview_chart(self) -> str:
        """Gera gráfico de visão geral do sistema"""
        try:
            # Obter dados do sistema
            dashboard_data = get_system_dashboard()
            
            if 'error' in dashboard_data:
                return self._create_error_chart("Erro ao obter dados do sistema")
            
            # Criar gráfico de saúde do sistema
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Uso de CPU', 'Uso de Memória', 'Status dos Modelos', 'Alertas Recentes'),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            # CPU e Memória
            cpu_usage = dashboard_data.get('current_metrics', {}).get('cpu_usage', 0)
            memory_usage = dashboard_data.get('current_metrics', {}).get('memory_usage', 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=cpu_usage,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "CPU (%)"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 80], 'color': "yellow"},
                                    {'range': [80, 100], 'color': "red"}]},
                    delta={'reference': 50}
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=memory_usage,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Memória (%)"},
                    gauge={'axis': {'range': [None, 100]},
                           'bar': {'color': "darkgreen"},
                           'steps': [{'range': [0, 60], 'color': "lightgray"},
                                    {'range': [60, 85], 'color': "yellow"},
                                    {'range': [85, 100], 'color': "red"}]},
                    delta={'reference': 60}
                ),
                row=1, col=2
            )
            
            # Status dos modelos
            models_status = dashboard_data.get('system_health', {}).get('models_status', {})
            model_names = list(models_status.keys())
            model_values = [1 if status == 'healthy' else 0.5 if status == 'warning' else 0 
                           for status in models_status.values()]
            
            fig.add_trace(
                go.Bar(
                    x=model_names,
                    y=model_values,
                    marker_color=['green' if v == 1 else 'orange' if v == 0.5 else 'red' 
                                 for v in model_values],
                    name='Status dos Modelos'
                ),
                row=2, col=1
            )
            
            # Alertas recentes
            recent_alerts = dashboard_data.get('recent_alerts', [])
            if recent_alerts:
                alert_levels = [alert.get('level', 'info') for alert in recent_alerts]
                alert_counts = pd.Series(alert_levels).value_counts()
                
                fig.add_trace(
                    go.Scatter(
                        x=list(alert_counts.index),
                        y=list(alert_counts.values),
                        mode='markers+text',
                        text=list(alert_counts.values),
                        textposition='top center',
                        marker=dict(size=20, color=['red', 'orange', 'blue', 'green']),
                        name='Alertas por Nível'
                    ),
                    row=2, col=2
                )
            
            # Layout
            fig.update_layout(
                title="Visão Geral do Sistema",
                height=600,
                showlegend=False
            )
            
            return plotly.utils.PlotlyJSONEncoder().encode(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de visão geral: {e}")
            return self._create_error_chart(f"Erro: {str(e)}")
    
    def generate_ml_performance_chart(self) -> str:
        """Gera gráfico de performance dos modelos ML"""
        try:
            # Obter dados de performance
            dashboard_data = get_system_dashboard()
            
            if 'error' in dashboard_data:
                return self._create_error_chart("Erro ao obter dados de performance")
            
            model_performance = dashboard_data.get('model_performance', {})
            
            if not model_performance:
                return self._create_error_chart("Nenhum dado de performance disponível")
            
            # Preparar dados para o gráfico
            model_types = []
            accuracy_scores = []
            f1_scores = []
            colors = []
            
            for model_type, perf in model_performance.items():
                if isinstance(perf, dict) and 'error' not in perf:
                    model_types.append(model_type.replace('_', ' ').title())
                    accuracy_scores.append(perf.get('avg_accuracy', 0))
                    f1_scores.append(perf.get('avg_f1_score', 0))
                    colors.append(self.dashboard_config['chart_colors'][len(colors) % len(self.dashboard_config['chart_colors'])])
            
            if not model_types:
                return self._create_error_chart("Nenhum modelo com dados válidos")
            
            # Criar gráfico
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Acurácia dos Modelos', 'F1-Score dos Modelos'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Gráfico de acurácia
            fig.add_trace(
                go.Bar(
                    x=model_types,
                    y=accuracy_scores,
                    marker_color=colors,
                    name='Acurácia',
                    text=[f'{acc:.3f}' for acc in accuracy_scores],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Gráfico de F1-Score
            fig.add_trace(
                go.Bar(
                    x=model_types,
                    y=f1_scores,
                    marker_color=colors,
                    name='F1-Score',
                    text=[f'{f1:.3f}' for f1 in f1_scores],
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            # Layout
            fig.update_layout(
                title="Performance dos Modelos ML",
                height=500,
                showlegend=False
            )
            
            # Eixos Y
            fig.update_yaxes(range=[0, 1], row=1, col=1)
            fig.update_yaxes(range=[0, 1], row=1, col=2)
            
            return plotly.utils.PlotlyJSONEncoder().encode(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de performance ML: {e}")
            return self._create_error_chart(f"Erro: {str(e)}")
    
    def generate_betting_analysis_chart(self) -> str:
        """Gera gráfico de análise de apostas"""
        try:
            # Obter análise de mercado
            market_data = get_market_analysis()
            
            if 'error' in market_data:
                return self._create_error_chart("Erro ao obter dados de mercado")
            
            competition_analysis = market_data.get('competition_analysis', {})
            
            if not competition_analysis:
                return self._create_error_chart("Nenhum dado de competição disponível")
            
            # Preparar dados
            competitions = list(competition_analysis.keys())
            home_win_rates = []
            away_win_rates = []
            draw_rates = []
            avg_goals = []
            
            for comp in competitions:
                comp_data = competition_analysis[comp]
                home_win_rates.append(comp_data.get('home_win_rate', 0))
                away_win_rates.append(comp_data.get('away_win_rate', 0))
                draw_rates.append(comp_data.get('draw_rate', 0))
                avg_goals.append(comp_data.get('avg_goals_per_match', 0))
            
            # Criar gráfico
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Taxa de Vitória por Posição', 'Média de Gols por Competição', 
                               'Distribuição de Resultados', 'Eficiência do Mercado'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "pie"}, {"type": "bar"}]]
            )
            
            # Taxa de vitória
            fig.add_trace(
                go.Bar(
                    x=competitions,
                    y=home_win_rates,
                    name='Vitória em Casa',
                    marker_color='blue'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=competitions,
                    y=away_win_rates,
                    name='Vitória Fora',
                    marker_color='red'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=competitions,
                    y=draw_rates,
                    name='Empates',
                    marker_color='gray'
                ),
                row=1, col=1
            )
            
            # Média de gols
            fig.add_trace(
                go.Bar(
                    x=competitions,
                    y=avg_goals,
                    name='Média de Gols',
                    marker_color='green',
                    text=[f'{g:.1f}' for g in avg_goals],
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            # Distribuição de resultados (exemplo para uma competição)
            if competitions:
                comp_data = competition_analysis[competitions[0]]
                labels = ['Vitória Casa', 'Vitória Fora', 'Empate']
                values = [comp_data.get('home_win_rate', 0), 
                         comp_data.get('away_win_rate', 0), 
                         comp_data.get('draw_rate', 0)]
                
                fig.add_trace(
                    go.Pie(
                        labels=labels,
                        values=values,
                        name='Distribuição',
                        hole=0.3
                    ),
                    row=2, col=1
                )
            
            # Eficiência do mercado
            market_efficiency = []
            for comp in competitions:
                comp_data = competition_analysis[comp]
                efficiency = comp_data.get('market_efficiency', 'Unknown')
                if efficiency == 'Home Bias':
                    market_efficiency.append(1)
                elif efficiency == 'Away Bias':
                    market_efficiency.append(-1)
                else:
                    market_efficiency.append(0)
            
            fig.add_trace(
                go.Bar(
                    x=competitions,
                    y=market_efficiency,
                    name='Eficiência',
                    marker_color=['red' if v == -1 else 'green' if v == 1 else 'gray' for v in market_efficiency],
                    text=['Away Bias' if v == -1 else 'Home Bias' if v == 1 else 'Balanced' for v in market_efficiency],
                    textposition='auto'
                ),
                row=2, col=2
            )
            
            # Layout
            fig.update_layout(
                title="Análise de Mercado de Apostas",
                height=700,
                showlegend=True
            )
            
            return plotly.utils.PlotlyJSONEncoder().encode(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de análise de apostas: {e}")
            return self._create_error_chart(f"Erro: {str(e)}")
    
    def generate_value_betting_chart(self) -> str:
        """Gera gráfico de oportunidades de value betting"""
        try:
            # Obter análise de mercado
            market_data = get_market_analysis()
            
            if 'error' in market_data:
                return self._create_error_chart("Erro ao obter dados de mercado")
            
            opportunities = market_data.get('value_betting_opportunities', [])
            
            if not opportunities:
                return self._create_error_chart("Nenhuma oportunidade de value betting encontrada")
            
            # Preparar dados
            matches = [opp['match'] for opp in opportunities]
            value_scores = [opp['value_score'] for opp in opportunities]
            odds = [opp['odds'] for opp in opportunities]
            bet_types = [opp['bet_type'] for opp in opportunities]
            
            # Criar gráfico
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Score de Valor por Partida', 'Distribuição de Odds', 
                               'Tipos de Aposta', 'Top Oportunidades'),
                specs=[[{"type": "bar"}, {"type": "histogram"}],
                       [{"type": "pie"}, {"type": "scatter"}]]
            )
            
            # Score de valor
            fig.add_trace(
                go.Bar(
                    x=matches,
                    y=value_scores,
                    marker_color='green',
                    name='Score de Valor',
                    text=[f'{score:.3f}' for score in value_scores],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Distribuição de odds
            fig.add_trace(
                go.Histogram(
                    x=odds,
                    nbinsx=10,
                    name='Distribuição de Odds',
                    marker_color='blue'
                ),
                row=1, col=2
            )
            
            # Tipos de aposta
            bet_type_counts = pd.Series(bet_types).value_counts()
            fig.add_trace(
                go.Pie(
                    labels=list(bet_type_counts.index),
                    values=list(bet_type_counts.values),
                    name='Tipos de Aposta',
                    hole=0.3
                ),
                row=2, col=1
            )
            
            # Scatter plot: Score vs Odds
            fig.add_trace(
                go.Scatter(
                    x=odds,
                    y=value_scores,
                    mode='markers+text',
                    text=matches,
                    textposition='top center',
                    marker=dict(size=10, color=value_scores, colorscale='Viridis'),
                    name='Score vs Odds'
                ),
                row=2, col=2
            )
            
            # Layout
            fig.update_layout(
                title="Oportunidades de Value Betting",
                height=700,
                showlegend=True
            )
            
            return plotly.utils.PlotlyJSONEncoder().encode(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de value betting: {e}")
            return self._create_error_chart(f"Erro: {str(e)}")
    
    def generate_trend_analysis_chart(self) -> str:
        """Gera gráfico de análise de tendências"""
        try:
            # Simular dados de tendências (em produção, viriam do sistema de análise)
            trend_data = {
                'dates': pd.date_range(start='2025-01-01', end='2025-01-31', freq='D').strftime('%Y-%m-%d').tolist(),
                'accuracy_trend': np.random.normal(0.75, 0.05, 31).tolist(),
                'prediction_volume': np.random.poisson(50, 31).tolist(),
                'roi_trend': np.random.normal(0.15, 0.08, 31).tolist()
            }
            
            # Criar gráfico
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Tendência de Acurácia', 'Volume de Predições', 
                               'Tendência de ROI', 'Correlação Acurácia-ROI'),
                specs=[[{"type": "scatter"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "scatter"}]]
            )
            
            # Tendência de acurácia
            fig.add_trace(
                go.Scatter(
                    x=trend_data['dates'],
                    y=trend_data['accuracy_trend'],
                    mode='lines+markers',
                    name='Acurácia',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=1
            )
            
            # Volume de predições
            fig.add_trace(
                go.Bar(
                    x=trend_data['dates'],
                    y=trend_data['prediction_volume'],
                    name='Volume',
                    marker_color='green'
                ),
                row=1, col=2
            )
            
            # Tendência de ROI
            fig.add_trace(
                go.Scatter(
                    x=trend_data['dates'],
                    y=trend_data['roi_trend'],
                    mode='lines+markers',
                    name='ROI',
                    line=dict(color='red', width=2)
                ),
                row=2, col=1
            )
            
            # Correlação
            fig.add_trace(
                go.Scatter(
                    x=trend_data['accuracy_trend'],
                    y=trend_data['roi_trend'],
                    mode='markers',
                    name='Correlação',
                    marker=dict(size=8, color='purple')
                ),
                row=2, col=2
            )
            
            # Layout
            fig.update_layout(
                title="Análise de Tendências do Sistema",
                height=700,
                showlegend=True
            )
            
            # Eixos
            fig.update_yaxes(range=[0.6, 0.9], row=1, col=1)
            fig.update_yaxes(range=[0, 100], row=1, col=2)
            fig.update_yaxes(range=[-0.1, 0.4], row=2, col=1)
            
            return plotly.utils.PlotlyJSONEncoder().encode(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de tendências: {e}")
            return self._create_error_chart(f"Erro: {str(e)}")
    
    def _create_error_chart(self, error_message: str) -> str:
        """Cria um gráfico de erro"""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Erro no Gráfico",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return plotly.utils.PlotlyJSONEncoder().encode(fig)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtém todos os dados do dashboard"""
        try:
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'charts': {
                    'system_overview': self.generate_system_overview_chart(),
                    'ml_performance': self.generate_ml_performance_chart(),
                    'betting_analysis': self.generate_betting_analysis_chart(),
                    'value_betting': self.generate_value_betting_chart(),
                    'trend_analysis': self.generate_trend_analysis_chart()
                },
                'metrics': self._get_current_metrics(),
                'alerts': self._get_recent_alerts()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard: {e}")
            return {'error': str(e)}
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Obtém métricas atuais do sistema"""
        try:
            dashboard_data = get_system_dashboard()
            
            if 'error' in dashboard_data:
                return {'error': 'Erro ao obter métricas'}
            
            return {
                'system_health': dashboard_data.get('system_health', {}).get('overall_status', 'unknown'),
                'cpu_usage': dashboard_data.get('current_metrics', {}).get('cpu_usage', 0),
                'memory_usage': dashboard_data.get('current_metrics', {}).get('memory_usage', 0),
                'active_models': len([k for k, v in dashboard_data.get('system_health', {}).get('models_status', {}).items() 
                                    if v == 'healthy']),
                'total_models': len(dashboard_data.get('system_health', {}).get('models_status', {}))
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas atuais: {e}")
            return {'error': str(e)}
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas recentes"""
        try:
            dashboard_data = get_system_dashboard()
            
            if 'error' in dashboard_data:
                return []
            
            alerts = dashboard_data.get('recent_alerts', [])
            return alerts[:5]  # Últimos 5 alertas
            
        except Exception as e:
            logger.error(f"Erro ao obter alertas: {e}")
            return []

# Instância global
web_dashboard = WebDashboard()

# Funções de conveniência
def get_dashboard_data() -> Dict[str, Any]:
    """Obtém dados do dashboard"""
    return web_dashboard.get_dashboard_data()

def generate_system_chart() -> str:
    """Gera gráfico do sistema"""
    return web_dashboard.generate_system_overview_chart()

def generate_ml_chart() -> str:
    """Gera gráfico de ML"""
    return web_dashboard.generate_ml_performance_chart()

def generate_betting_chart() -> str:
    """Gera gráfico de apostas"""
    return web_dashboard.generate_betting_analysis_chart()
