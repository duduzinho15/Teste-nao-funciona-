#!/usr/bin/env python3
"""
Dashboard web avançado com visualizações interativas para o sistema ML
"""
import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import warnings
warnings.filterwarnings('ignore')

try:
    import dash
    from dash import dcc, html, Input, Output, callback_context
    from dash.exceptions import PreventUpdate
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("⚠️ Dash não disponível. Instale com: pip install dash")

try:
    from .config import get_ml_config
    from .cache_manager import cache_result, timed_cache_result
    from .production_monitoring import get_system_dashboard
    from .betting_apis_integration import get_market_analysis
except ImportError:
    # Fallback para execução direta
    def get_ml_config():
        class Config:
            monitoring_dir = "monitoring"
        return Config()
    
    def cache_result(func):
        return func
    
    def timed_cache_result(seconds):
        def decorator(func):
            return func
        return decorator
    
    def get_system_dashboard():
        return {
            'current_metrics': {'cpu_usage': 45, 'memory_usage': 60},
            'system_health': {'models_status': {'model1': 'healthy', 'model2': 'healthy'}},
            'recent_alerts': []
        }
    
    def get_market_analysis():
        return {}

logger = logging.getLogger(__name__)

class AdvancedWebDashboard:
    """Dashboard web avançado com visualizações interativas"""
    
    def __init__(self):
        self.config = get_ml_config()
        
        # Diretórios
        self.dashboard_dir = Path(self.config.monitoring_dir) / "advanced_web_dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações do dashboard
        self.dashboard_config = {
            'refresh_interval': 30,  # segundos
            'max_data_points': 1000,
            'chart_colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            'theme': 'plotly_white'
        }
        
        # Dados do dashboard
        self.dashboard_data = {}
        self.last_update = None
        
        # Inicializar Dash se disponível
        if DASH_AVAILABLE:
            self.app = dash.Dash(__name__, title='ApostaPro ML Dashboard')
            self.setup_dash_callbacks()
        else:
            self.app = None
    
    def setup_dash_callbacks(self):
        """Configura callbacks do Dash"""
        if not self.app:
            return
        
        @self.app.callback(
            Output('system-overview', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_system_overview(n):
            return self.generate_system_overview_chart()
        
        @self.app.callback(
            Output('performance-chart', 'figure'),
            [Input('interval-component', 'n_intervals'),
             Input('performance-metric-dropdown', 'value')]
        )
        def update_performance_chart(n, metric):
            return self.generate_performance_chart(metric)
        
        @self.app.callback(
            Output('betting-analysis', 'figure'),
            [Input('interval-component', 'n_intervals'),
             Input('competition-dropdown', 'value'),
             Input('betting-type-dropdown', 'value')]
        )
        def update_betting_analysis(n, competition, betting_type):
            return self.generate_betting_analysis_chart(competition, betting_type)
        
        @self.app.callback(
            Output('model-performance', 'figure'),
            [Input('interval-component', 'n_intervals'),
             Input('model-dropdown', 'value')]
        )
        def update_model_performance(n, model):
            return self.generate_model_performance_chart(model)
    
    def generate_system_overview_chart(self) -> go.Figure:
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
                    marker_color=['green' if v == 1 else 'orange' if v == 0.5 else 'red' for v in model_values],
                    name='Status dos Modelos'
                ),
                row=2, col=1
            )
            
            # Alertas recentes
            alerts = dashboard_data.get('recent_alerts', [])
            if alerts:
                alert_times = [alert.get('timestamp', '') for alert in alerts[:10]]
                alert_severities = [alert.get('severity', 'info') for alert in alerts[:10]]
                
                colors = {'critical': 'red', 'warning': 'orange', 'info': 'blue'}
                alert_colors = [colors.get(severity, 'gray') for severity in alert_severities]
                
                fig.add_trace(
                    go.Scatter(
                        x=alert_times,
                        y=list(range(len(alert_times))),
                        mode='markers',
                        marker=dict(color=alert_colors, size=10),
                        name='Alertas',
                        text=[f"{alert.get('message', '')} - {alert.get('severity', '')}" for alert in alerts[:10]]
                    ),
                    row=2, col=2
                )
            
            fig.update_layout(
                title="Visão Geral do Sistema",
                height=600,
                showlegend=False,
                template=self.dashboard_config['theme']
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de visão geral: {e}")
            return self._create_error_chart(f"Erro: {e}")
    
    def generate_performance_chart(self, metric: str = 'accuracy') -> go.Figure:
        """Gera gráfico de performance dos modelos"""
        try:
            # Simular dados de performance (substituir por dados reais)
            dates = pd.date_range(start='2025-01-01', end='2025-08-13', freq='D')
            
            if metric == 'accuracy':
                values = np.random.normal(0.75, 0.05, len(dates))
                title = "Acurácia dos Modelos ao Longo do Tempo"
                y_label = "Acurácia"
            elif metric == 'precision':
                values = np.random.normal(0.70, 0.08, len(dates))
                title = "Precisão dos Modelos ao Longo do Tempo"
                y_label = "Precisão"
            elif metric == 'recall':
                values = np.random.normal(0.72, 0.06, len(dates))
                title = "Recall dos Modelos ao Longo do Tempo"
                y_label = "Recall"
            else:
                values = np.random.normal(0.73, 0.07, len(dates))
                title = "F1-Score dos Modelos ao Longo do Tempo"
                y_label = "F1-Score"
            
            # Suavizar dados
            values = pd.Series(values).rolling(window=7).mean().fillna(method='bfill')
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    name=metric.title(),
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=4)
                )
            )
            
            # Adicionar linha de tendência
            z = np.polyfit(range(len(dates)), values, 1)
            p = np.poly1d(z)
            trend_line = p(range(len(dates)))
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=trend_line,
                    mode='lines',
                    name='Tendência',
                    line=dict(color='red', width=2, dash='dash')
                )
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Data",
                yaxis_title=y_label,
                height=400,
                template=self.dashboard_config['theme'],
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de performance: {e}")
            return self._create_error_chart(f"Erro: {e}")
    
    def generate_betting_analysis_chart(self, competition: str = 'all', betting_type: str = 'all') -> go.Figure:
        """Gera gráfico de análise de apostas"""
        try:
            # Simular dados de apostas (substituir por dados reais das APIs)
            competitions = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Brasileirão']
            betting_types = ['Match Winner', 'Over/Under', 'Both Teams Score', 'Double Chance']
            
            if competition == 'all':
                comp_data = competitions
            else:
                comp_data = [competition]
            
            if betting_type == 'all':
                bet_data = betting_types
            else:
                bet_data = [betting_type]
            
            # Gerar dados simulados
            data = []
            for comp in comp_data:
                for bet in bet_data:
                    for _ in range(10):
                        data.append({
                            'competition': comp,
                            'betting_type': bet,
                            'odds': np.random.uniform(1.5, 5.0),
                            'success_rate': np.random.uniform(0.3, 0.8),
                            'volume': np.random.uniform(100, 10000)
                        })
            
            df = pd.DataFrame(data)
            
            # Criar gráfico de dispersão
            fig = px.scatter(
                df,
                x='odds',
                y='success_rate',
                size='volume',
                color='competition',
                hover_data=['betting_type', 'volume'],
                title=f"Análise de Apostas - {competition} - {betting_type}",
                labels={
                    'odds': 'Odds',
                    'success_rate': 'Taxa de Sucesso',
                    'volume': 'Volume de Apostas',
                    'competition': 'Competição'
                }
            )
            
            fig.update_layout(
                height=500,
                template=self.dashboard_config['theme'],
                xaxis=dict(range=[1, 6]),
                yaxis=dict(range=[0, 1])
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de análise de apostas: {e}")
            return self._create_error_chart(f"Erro: {e}")
    
    def generate_model_performance_chart(self, model: str = 'all') -> go.Figure:
        """Gera gráfico de performance específico de um modelo"""
        try:
            # Simular dados de diferentes modelos
            models = ['Both Teams Score', 'Over/Under 2.5', 'Match Winner', 'Correct Score']
            
            if model == 'all':
                model_data = models
            else:
                model_data = [model]
            
            # Gerar dados simulados
            data = []
            for mod in model_data:
                for month in range(1, 9):
                    data.append({
                        'model': mod,
                        'month': month,
                        'accuracy': np.random.normal(0.75, 0.05),
                        'profit_loss': np.random.normal(0.05, 0.15),
                        'total_bets': np.random.randint(50, 200)
                    })
            
            df = pd.DataFrame(data)
            
            # Criar subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Acurácia Mensal', 'Lucro/Prejuízo Mensal'),
                vertical_spacing=0.1
            )
            
            for mod in model_data:
                mod_df = df[df['model'] == mod]
                
                fig.add_trace(
                    go.Scatter(
                        x=mod_df['month'],
                        y=mod_df['accuracy'],
                        mode='lines+markers',
                        name=f'{mod} - Acurácia',
                        line=dict(width=2)
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=mod_df['month'],
                        y=mod_df['profit_loss'],
                        name=f'{mod} - P&L',
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            fig.update_layout(
                title=f"Performance do Modelo: {model}",
                height=600,
                template=self.dashboard_config['theme'],
                showlegend=True
            )
            
            fig.update_xaxes(title_text="Mês", row=1, col=1)
            fig.update_xaxes(title_text="Mês", row=2, col=1)
            fig.update_yaxes(title_text="Acurácia", row=1, col=1)
            fig.update_yaxes(title_text="Lucro/Prejuízo (%)", row=2, col=1)
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de performance do modelo: {e}")
            return self._create_error_chart(f"Erro: {e}")
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """Cria gráfico de erro"""
        fig = go.Figure()
        fig.add_annotation(
            text=error_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="Erro no Dashboard",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def create_dash_layout(self):
        """Cria layout do dashboard Dash"""
        if not self.app:
            return None
        
        return html.Div([
            html.H1("🎯 ApostaPro ML Dashboard", 
                    style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
            
            # Controles
            html.Div([
                html.Div([
                    html.Label("Métrica de Performance:"),
                    dcc.Dropdown(
                        id='performance-metric-dropdown',
                        options=[
                            {'label': 'Acurácia', 'value': 'accuracy'},
                            {'label': 'Precisão', 'value': 'precision'},
                            {'label': 'Recall', 'value': 'recall'},
                            {'label': 'F1-Score', 'value': 'f1_score'}
                        ],
                        value='accuracy',
                        style={'width': '100%'}
                    )
                ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),
                
                html.Div([
                    html.Label("Competição:"),
                    dcc.Dropdown(
                        id='competition-dropdown',
                        options=[
                            {'label': 'Todas', 'value': 'all'},
                            {'label': 'Premier League', 'value': 'Premier League'},
                            {'label': 'La Liga', 'value': 'La Liga'},
                            {'label': 'Bundesliga', 'value': 'Bundesliga'},
                            {'label': 'Serie A', 'value': 'Serie A'},
                            {'label': 'Brasileirão', 'value': 'Brasileirão'}
                        ],
                        value='all',
                        style={'width': '100%'}
                    )
                ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),
                
                html.Div([
                    html.Label("Tipo de Aposta:"),
                    dcc.Dropdown(
                        id='betting-type-dropdown',
                        options=[
                            {'label': 'Todos', 'value': 'all'},
                            {'label': 'Match Winner', 'value': 'Match Winner'},
                            {'label': 'Over/Under', 'value': 'Over/Under'},
                            {'label': 'Both Teams Score', 'value': 'Both Teams Score'},
                            {'label': 'Double Chance', 'value': 'Double Chance'}
                        ],
                        value='all',
                        style={'width': '100%'}
                    )
                ], style={'width': '25%', 'display': 'inline-block', 'marginRight': 20}),
                
                html.Div([
                    html.Label("Modelo:"),
                    dcc.Dropdown(
                        id='model-dropdown',
                        options=[
                            {'label': 'Todos', 'value': 'all'},
                            {'label': 'Both Teams Score', 'value': 'Both Teams Score'},
                            {'label': 'Over/Under 2.5', 'value': 'Over/Under 2.5'},
                            {'label': 'Match Winner', 'value': 'Match Winner'},
                            {'label': 'Correct Score', 'value': 'Correct Score'}
                        ],
                        value='all',
                        style={'width': '100%'}
                    )
                ], style={'width': '25%', 'display': 'inline-block'})
            ], style={'marginBottom': 30}),
            
            # Gráficos
            html.Div([
                html.Div([
                    dcc.Graph(id='system-overview', style={'height': 600})
                ], style={'width': '100%', 'marginBottom': 30}),
                
                html.Div([
                    html.Div([
                        dcc.Graph(id='performance-chart', style={'height': 400})
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        dcc.Graph(id='betting-analysis', style={'height': 400})
                    ], style={'width': '50%', 'display': 'inline-block'})
                ], style={'marginBottom': 30}),
                
                html.Div([
                    dcc.Graph(id='model-performance', style={'height': 600})
                ], style={'width': '100%'})
            ]),
            
            # Componente de atualização automática
            dcc.Interval(
                id='interval-component',
                interval=self.dashboard_config['refresh_interval'] * 1000,  # em milissegundos
                n_intervals=0
            )
        ])
    
    def start_web_server(self, host: str = '0.0.0.0', port: int = 8050, debug: bool = False):
        """Inicia servidor web do dashboard"""
        if not self.app:
            logger.error("Dash não está disponível")
            return
        
        try:
            self.app.layout = self.create_dash_layout()
            logger.info(f"🌐 Iniciando servidor web em http://{host}:{port}")
            self.app.run_server(host=host, port=port, debug=debug)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor web: {e}")
    
    def generate_static_dashboard(self) -> str:
        """Gera dashboard estático em HTML"""
        try:
            # Gerar todos os gráficos
            system_chart = self.generate_system_overview_chart()
            performance_chart = self.generate_performance_chart()
            betting_chart = self.generate_betting_analysis_chart()
            model_chart = self.generate_model_performance_chart()
            
            # Converter para HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ApostaPro ML Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                    .chart-container {{ margin-bottom: 30px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .chart-title {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #34495e; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎯 ApostaPro ML Dashboard</h1>
                    <p>Dashboard de Machine Learning para Análise de Apostas</p>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Visão Geral do Sistema</div>
                    <div id="system-overview"></div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Performance dos Modelos</div>
                    <div id="performance-chart"></div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Análise de Apostas</div>
                    <div id="betting-analysis"></div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Performance Específica dos Modelos</div>
                    <div id="model-performance"></div>
                </div>
                
                <script>
                    {plotly.utils.PlotlyJSONEncoder().encode(system_chart)}
                    {plotly.utils.PlotlyJSONEncoder().encode(performance_chart)}
                    {plotly.utils.PlotlyJSONEncoder().encode(betting_chart)}
                    {plotly.utils.PlotlyJSONEncoder().encode(model_chart)}
                    
                    Plotly.newPlot('system-overview', system_chart.data, system_chart.layout);
                    Plotly.newPlot('performance-chart', performance_chart.data, performance_chart.layout);
                    Plotly.newPlot('betting-analysis', betting_chart.data, betting_chart.layout);
                    Plotly.newPlot('model-performance', model_chart.data, model_chart.layout);
                </script>
            </body>
            </html>
            """
            
            # Salvar arquivo HTML
            html_file = self.dashboard_dir / "dashboard.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Dashboard estático gerado: {html_file}")
            return str(html_file)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar dashboard estático: {e}")
            return ""

# Função de conveniência
def create_advanced_dashboard() -> AdvancedWebDashboard:
    """Cria e retorna instância do dashboard avançado"""
    return AdvancedWebDashboard()

if __name__ == "__main__":
    # Criar dashboard
    dashboard = AdvancedWebDashboard()
    
    # Gerar dashboard estático
    html_file = dashboard.generate_static_dashboard()
    print(f"✅ Dashboard estático gerado: {html_file}")
    
    # Tentar iniciar servidor web se Dash estiver disponível
    if DASH_AVAILABLE:
        print("🚀 Iniciando servidor web...")
        dashboard.start_web_server(debug=True)
    else:
        print("⚠️ Dash não disponível. Dashboard estático gerado.")
