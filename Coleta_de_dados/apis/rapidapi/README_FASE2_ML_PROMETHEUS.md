# 🚀 FASE 2: Machine Learning + Prometheus/Grafana

## 📋 Visão Geral

A **FASE 2** implementa um sistema avançado de Machine Learning para análise preditiva e integração completa com Prometheus e Grafana para monitoramento empresarial.

### 🎯 Objetivos da FASE 2

- **Análise Preditiva de Falhas** usando modelos de ML
- **Detecção Automática de Anomalias** em tempo real
- **Otimização Automática de Thresholds** baseada em padrões históricos
- **Métricas Prometheus** para monitoramento empresarial
- **Dashboards Grafana** automáticos e personalizados
- **Auto-tuning** do sistema baseado em ML

## 🏗️ Arquitetura da FASE 2

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE 2 - ML + PROMETHEUS                │
├─────────────────────────────────────────────────────────────┤
│  🤖 ML Analytics  │  📊 Prometheus Exporter               │
│  • Anomaly Detection │  • Custom Metrics                  │
│  • Performance Prediction │  • Real-time Export           │
│  • Pattern Analysis │  • Historical Data                  │
├─────────────────────────────────────────────────────────────┤
│  🎨 Grafana Integration │  🔧 Auto-optimization           │
│  • Dashboard Templates │  • Threshold Optimization        │
│  • ML Insights │  • Performance Tuning                    │
│  • Real-time Monitoring │  • Predictive Maintenance       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Arquivos

```
Coleta_de_dados/apis/rapidapi/
├── README_FASE2_ML_PROMETHEUS.md    # Esta documentação
├── demo_fase2_ml_prometheus.py      # Demonstração completa
├── ml_analytics.py                   # Sistema de Machine Learning
├── prometheus_integration.py         # Integração Prometheus/Grafana
├── requirements_fase2.txt            # Dependências da FASE 2
└── models/                           # Modelos ML salvos
    ├── anomaly_detector_metadata.json
    ├── anomaly_detector_model.pkl
    ├── performance_predictor_metadata.json
    ├── performance_predictor_model.pkl
    ├── pattern_clusterer_metadata.json
    └── pattern_clusterer_model.pkl
```

## 🚀 Início Rápido

### 1. Instalação das Dependências

```bash
# Instala dependências da FASE 2
pip install -r requirements_fase2.txt

# Ou instalação individual
pip install scikit-learn numpy pandas joblib prometheus-client
```

### 2. Executar Demonstração Completa

```bash
# Demonstração completa da FASE 2
python demo_fase2_ml_prometheus.py
```

### 3. Acessar Sistemas

- **Dashboard Principal**: http://localhost:8080
- **Prometheus Metrics**: http://localhost:9090/metrics
- **Grafana**: http://localhost:3000 (se configurado)

## 🤖 Sistema de Machine Learning

### Modelos Implementados

#### 1. **Anomaly Detector** (`anomaly_detector`)
- **Tipo**: Isolation Forest
- **Propósito**: Detecta anomalias em métricas de performance
- **Features**: Taxa de sucesso, tempo de resposta, taxa de erro, requisições/min
- **Output**: Score de anomalia (0-1) + classificação binária

#### 2. **Performance Predictor** (`performance_predictor`)
- **Tipo**: Random Forest Regressor
- **Propósito**: Prediz performance futura das APIs
- **Features**: Hora, dia da semana, performance anterior
- **Output**: Taxa de sucesso predita + nível de confiança

#### 3. **Pattern Clusterer** (`pattern_clusterer`)
- **Tipo**: K-Means Clustering
- **Propósito**: Identifica padrões de comportamento das APIs
- **Features**: Taxa de sucesso, tempo de resposta, taxa de erro
- **Output**: Clusters com características descritivas

### Funcionalidades ML

#### **Detecção de Anomalias**
```python
from ml_analytics import detect_api_anomalies

# Detecta anomalias em todas as APIs
anomalies = await detect_api_anomalies()

# Detecta anomalias em API específica
api_anomalies = await detect_api_anomalies("api_football")

for anomaly in anomalies:
    if anomaly.is_anomaly:
        print(f"🚨 Anomalia detectada em {anomaly.api_name}")
        print(f"   Score: {anomaly.anomaly_score:.3f}")
        print(f"   Severidade: {anomaly.severity}")
```

#### **Predição de Performance**
```python
from ml_analytics import predict_api_performance

# Prediz performance para próximas 3 horas
predictions = await predict_api_performance("api_football", hours_ahead=3)

for pred in predictions:
    print(f"🔮 {pred.timestamp.strftime('%H:%M')}: {pred.predicted_value:.1f}%")
    print(f"   Confiança: {pred.confidence:.2f}")
```

#### **Otimização Automática de Thresholds**
```python
from ml_analytics import optimize_system_thresholds

# Otimiza thresholds automaticamente
optimization = await optimize_system_thresholds()

if optimization.get("optimized_thresholds"):
    thresholds = optimization["optimized_thresholds"]
    print(f"⚡ Thresholds otimizados: {thresholds}")
```

### Treinamento Automático

O sistema ML inclui:
- **Coleta automática de dados** a cada 5 minutos
- **Retreinamento automático** a cada 24 horas
- **Validação de modelos** com métricas de performance
- **Persistência de modelos** para reutilização

## 📊 Integração Prometheus

### Métricas Exportadas

#### **Métricas de APIs**
```prometheus
# Taxa de sucesso por API
rapidapi_api_success_rate{api_name="api_football", environment="production"}

# Tempo de resposta por API
rapidapi_api_response_time_seconds{api_name="api_football", environment="production"}

# Total de requisições por API
rapidapi_api_requests_total{api_name="api_football", status="success", environment="production"}
```

#### **Métricas do Sistema**
```prometheus
# Uptime do sistema
rapidapi_system_uptime_seconds{environment="production"}

# Uso de memória
rapidapi_system_memory_bytes{environment="production"}

# Uso de CPU
rapidapi_system_cpu_percent{environment="production"}
```

#### **Métricas de ML**
```prometheus
# Precisão dos modelos ML
rapidapi_ml_model_accuracy{model_name="anomaly_detector", environment="production"}

# Anomalias detectadas
rapidapi_ml_anomalies_total{api_name="api_football", severity="high", environment="production"}
```

#### **Métricas de Alertas**
```prometheus
# Alertas ativos por severidade
rapidapi_alerts_active{severity="critical", environment="production"}
```

### Endpoints Prometheus

- **`/metrics`**: Métricas no formato Prometheus
- **`/metrics/json`**: Métricas em formato JSON
- **`/health`**: Health check do sistema
- **`/status`**: Status detalhado do exportador

## 🎨 Integração Grafana

### Dashboards Automáticos

#### **1. RapidAPI - Visão Geral**
- Taxa de sucesso das APIs
- Tempo de resposta das APIs
- Requisições por minuto
- Status geral do sistema

#### **2. RapidAPI - Alertas e ML**
- Alertas ativos por severidade
- Anomalias detectadas por ML
- Precisão dos modelos ML
- Tendências de performance

### Templates de Dashboard

Os dashboards são criados automaticamente usando templates predefinidos:

```python
from prometheus_integration import create_grafana_dashboards

# Cria todos os dashboards disponíveis
result = await create_grafana_dashboards()

# Cria dashboard específico
result = await grafana_integration.create_dashboard("rapidapi_overview")
```

### Configuração Grafana

```bash
# Variáveis de ambiente para Grafana
GRAFANA_URL=http://localhost:3000
GRAFANA_API_KEY=sua_api_key_aqui
GRAFANA_ORG_ID=1
```

## 🔧 Auto-otimização

### Otimização de Thresholds

O sistema ML analisa padrões históricos e otimiza automaticamente:

- **Thresholds de alerta** baseados em percentis dos dados
- **Ajuste dinâmico** conforme mudanças de comportamento
- **Notificações automáticas** quando thresholds são otimizados

### Manutenção Automática

```python
from ml_analytics import get_ml_analytics

analytics = get_ml_analytics()

# Executa manutenção automática
maintenance = await analytics.auto_maintenance()

if maintenance.get("models_trained"):
    print("✅ Modelos retreinados automaticamente")

if maintenance.get("thresholds_optimized"):
    print("✅ Thresholds reotimizados automaticamente")
```

## 📈 Monitoramento em Tempo Real

### Coleta de Dados

- **Intervalo**: A cada 15 segundos
- **Retenção**: 1 semana de dados históricos
- **Storage**: In-memory com persistência opcional
- **Compressão**: Dados antigos são automaticamente removidos

### Alertas Inteligentes

#### **Alertas Baseados em ML**
```python
# Regra de alerta para anomalias ML
await alert_manager.add_custom_alert_rule(
    name="Anomalia ML Detectada",
    metric="ml_anomaly",
    threshold=0.7,
    operator=">",
    severity="warning",
    description="Alerta baseado em detecção de anomalia por ML"
)
```

#### **Alertas para Degradação Gradual**
```python
# Regra para degradação gradual
await alert_manager.add_custom_alert_rule(
    name="Degradação Gradual de Performance",
    metric="performance_trend",
    threshold=-5.0,
    operator="<",
    severity="warning",
    description="Alerta para degradação gradual de performance"
)
```

## 🛠️ Desenvolvimento e Testes

### Estrutura de Testes

```bash
# Testes unitários para ML
python -m pytest test_ml_analytics.py

# Testes para Prometheus
python -m pytest test_prometheus_integration.py

# Testes de integração
python demo_fase2_ml_prometheus.py
```

### Debug e Logs

```python
# Configuração de logs detalhados
logging.basicConfig(level=logging.DEBUG)

# Logs específicos do ML
ml_logger = logging.getLogger("ml.analytics")
ml_logger.setLevel(logging.DEBUG)

# Logs do Prometheus
prometheus_logger = logging.getLogger("prometheus.exporter")
prometheus_logger.setLevel(logging.DEBUG)
```

## 🚀 Deploy em Produção

### Requisitos de Sistema

- **Python**: 3.8+
- **Memória**: Mínimo 2GB RAM
- **CPU**: 2 cores para ML básico, 4+ para produção
- **Storage**: 10GB para modelos e dados históricos
- **Rede**: Acesso às APIs externas

### Configuração de Produção

#### **1. Variáveis de Ambiente**
```bash
# ML Configuration
ML_TRAINING_INTERVAL_HOURS=24
ML_MIN_TRAINING_SAMPLES=1000
ML_ANOMALY_THRESHOLD=0.7

# Prometheus Configuration
PROMETHEUS_EXPORT_INTERVAL=15
PROMETHEUS_METRICS_RETENTION_HOURS=168

# Grafana Configuration
GRAFANA_URL=https://grafana.seudominio.com
GRAFANA_API_KEY=sua_api_key_producao
```

#### **2. Serviços Systemd (Linux)**
```ini
[Unit]
Description=RapidAPI ML + Prometheus Service
After=network.target

[Service]
Type=simple
User=rapidapi
WorkingDirectory=/opt/rapidapi
ExecStart=/usr/bin/python3 demo_fase2_ml_prometheus.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **3. Docker (Opcional)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_fase2.txt .
RUN pip install -r requirements_fase2.txt

COPY . .
EXPOSE 8080 9090

CMD ["python", "demo_fase2_ml_prometheus.py"]
```

### Monitoramento de Produção

#### **Health Checks**
```bash
# Dashboard principal
curl http://localhost:8080/health

# Prometheus
curl http://localhost:9090/health

# Métricas
curl http://localhost:9090/metrics
```

#### **Logs de Produção**
```bash
# Logs do sistema
tail -f logs/rapidapi.log

# Logs específicos do ML
grep "ml.analytics" logs/rapidapi.log

# Logs do Prometheus
grep "prometheus" logs/rapidapi.log
```

## 🔧 Troubleshooting

### Problemas Comuns

#### **1. Modelos ML não treinam**
```bash
# Verifica dados disponíveis
python -c "from ml_analytics import get_ml_analytics; a = get_ml_analytics(); print(f'Dados: {len(a.historical_data)}')"

# Verifica dependências
pip list | grep scikit-learn
```

#### **2. Prometheus não exporta métricas**
```bash
# Verifica se o servidor está rodando
netstat -tlnp | grep 9090

# Verifica logs
grep "prometheus" logs/rapidapi.log
```

#### **3. Grafana não cria dashboards**
```bash
# Verifica API key
echo $GRAFANA_API_KEY

# Testa conectividade
curl -H "Authorization: Bearer $GRAFANA_API_KEY" $GRAFANA_URL/api/org
```

### Debug Avançado

#### **Verificação de Modelos ML**
```python
from ml_analytics import get_ml_analytics

analytics = get_ml_analytics()

# Status dos modelos
for name, model in analytics.models.items():
    print(f"{name}: {'✅ Treinado' if model.last_trained else '⚠️ Não treinado'}")
    print(f"  Amostras: {model.training_samples}")
    print(f"  Precisão: {model.accuracy:.3f}")
```

#### **Verificação de Métricas Prometheus**
```python
from prometheus_integration import get_prometheus_exporter

exporter = get_prometheus_exporter()

# Lista métricas configuradas
for name, metric in exporter.metrics.items():
    print(f"{name}: {metric.description}")
    print(f"  Tipo: {metric.metric_type}")
    print(f"  Labels: {metric.labels}")
```

## 📚 Recursos Adicionais

### Documentação

- **Scikit-learn**: [Documentação oficial](https://scikit-learn.org/)
- **Prometheus**: [Guia de métricas](https://prometheus.io/docs/concepts/metric_types/)
- **Grafana**: [API de dashboards](https://grafana.com/docs/grafana/latest/http_api/dashboard/)

### Exemplos de Uso

- **`demo_fase2_ml_prometheus.py`**: Demonstração completa
- **`ml_analytics.py`**: Sistema de ML standalone
- **`prometheus_integration.py`**: Integração Prometheus/Grafana

### Suporte

- **Issues**: Reporte problemas no repositório
- **Documentação**: Este README e comentários no código
- **Exemplos**: Scripts de demonstração incluídos

## 🎯 Próximos Passos

### Melhorias Planejadas

1. **Deep Learning**: Modelos mais avançados (LSTM, Transformers)
2. **AutoML**: Seleção automática de algoritmos
3. **MLOps**: Pipeline completo de ML em produção
4. **Alertas Preditivos**: Alertas antes de problemas ocorrerem

### Roadmap

- **FASE 2.1**: Modelos de Deep Learning
- **FASE 2.2**: AutoML e Auto-tuning
- **FASE 2.3**: MLOps e CI/CD para ML
- **FASE 2.4**: Alertas Preditivos Avançados

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 👥 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**🚀 FASE 2 - ML + Prometheus/Grafana - Sistema de Produção Avançado!**
