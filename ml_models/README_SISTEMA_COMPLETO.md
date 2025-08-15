# 🎯 Sistema Completo de Machine Learning do ApostaPro

## 📋 Visão Geral

Este sistema integra todas as funcionalidades avançadas de Machine Learning para análise de apostas esportivas:

- **📊 Integração com APIs de Casas de Apostas**: Coleta dados em tempo real
- **🖥️ Dashboard Web Interativo**: Visualizações avançadas com Plotly e Dash
- **⚙️ Pipeline de Automação CI/CD**: Automação completa de treinamento e deploy
- **☸️ Orquestração Kubernetes**: Escalabilidade e monitoramento distribuído

## 🚀 Instalação e Configuração

### Pré-requisitos

```bash
# Python 3.9+
python --version

# Dependências principais
pip install -r requirements_ml.txt

# Dependências opcionais para dashboard
pip install dash plotly

# Kubernetes (opcional)
kubectl version --client
```

### Variáveis de Ambiente

Crie um arquivo `.env` com suas chaves de API:

```bash
# APIs de Apostas
FOOTBALL_DATA_API_KEY=sua_chave_aqui
API_FOOTBALL_KEY=sua_chave_aqui
ODDS_API_KEY=sua_chave_aqui
BETFAIR_API_KEY=sua_chave_aqui
PINNACLE_API_KEY=sua_chave_aqui
WILLIAM_HILL_API_KEY=sua_chave_aqui

# Notificações
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
NOTIFICATION_EMAILS=email1@exemplo.com,email2@exemplo.com

# Slack
SLACK_WEBHOOK_URL=sua_webhook_aqui
SLACK_CHANNEL=#ml-pipeline

# Redis (opcional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 🎮 Como Usar

### 1. Execução Rápida

```bash
# Executar sistema completo
cd ml_models
python run_complete_ml_system.py
```

### 2. Execução por Componentes

```bash
# Apenas configuração das APIs
python betting_apis_config.py

# Apenas dashboard web
python advanced_web_dashboard.py

# Apenas pipeline CI/CD
python ci_cd_pipeline_config.py

# Apenas Kubernetes
python kubernetes_monitoring_config.py
```

### 3. Execução do Pipeline Principal

```bash
# Pipeline integrado
python execute_ml_pipeline.py
```

## 📊 Funcionalidades Principais

### 🔌 Integração com APIs de Apostas

- **APIs Suportadas**:
  - Football Data Org
  - API Football
  - The Odds API
  - Betfair
  - Pinnacle Sports
  - William Hill

- **Dados Coletados**:
  - Odds em tempo real
  - Resultados históricos
  - Análise de mercado
  - Validação de qualidade

### 🖥️ Dashboard Web

- **Gráficos Interativos**:
  - Visão geral do sistema
  - Performance dos modelos
  - Análise de apostas
  - Métricas específicas por modelo

- **Funcionalidades**:
  - Atualização automática
  - Filtros por competição/tipo de aposta
  - Exportação de dados
  - Responsivo para mobile

### ⚙️ Pipeline de Automação

- **Pipelines Disponíveis**:
  - `ml_training`: Treinamento automático diário
  - `data_validation`: Validação a cada 6 horas
  - `performance_monitoring`: Monitoramento a cada 15 minutos
  - `model_deployment`: Deploy manual com validação

- **Integrações**:
  - GitHub Actions
  - Docker Compose
  - Kubernetes Manifests

### ☸️ Orquestração Kubernetes

- **Componentes**:
  - ML API (3 réplicas, auto-scaling)
  - ML Training (2 réplicas, auto-scaling)
  - ML Inference (5 réplicas, auto-scaling)

- **Monitoramento**:
  - Prometheus para métricas
  - Grafana para visualização
  - AlertManager para alertas
  - Node Exporter para métricas do sistema

## 📁 Estrutura de Arquivos

```
ml_models/
├── configs/                          # Configurações salvas
├── execute_ml_pipeline.py           # Pipeline principal
├── run_complete_ml_system.py        # Sistema completo
├── betting_apis_config.py           # Configuração das APIs
├── advanced_web_dashboard.py        # Dashboard avançado
├── ci_cd_pipeline_config.py         # Configuração CI/CD
├── kubernetes_monitoring_config.py  # Configuração Kubernetes
├── betting_apis_integration.py      # Integração com APIs
├── automation_pipeline.py           # Pipeline de automação
├── kubernetes_orchestration.py      # Orquestração K8s
├── production_monitoring.py         # Monitoramento
└── README_SISTEMA_COMPLETO.md       # Este arquivo
```

## 🔧 Configuração Avançada

### Personalizar APIs

Edite `betting_apis_config.py`:

```python
# Adicionar nova API
self.apis['nova_api'] = APIConfig(
    name='Nova API',
    base_url='https://api.nova.com',
    api_key=self._get_env_var('NOVA_API_KEY'),
    rate_limit=100
)

# Configurar competições
self.competitions['nova_liga'] = {
    'id': 'NL',
    'name': 'Nova Liga',
    'country': 'Brasil',
    'priority': 'high',
    'apis': ['nova_api', 'odds_api']
}
```

### Personalizar Pipelines

Edite `ci_cd_pipeline_config.py`:

```python
# Adicionar novo pipeline
self.pipelines['custom_pipeline'] = PipelineConfig(
    name='custom_pipeline',
    version='1.0.0',
    description='Pipeline personalizado',
    trigger_type='webhook',
    stages=[
        PipelineStage(
            name='custom_step',
            description='Passo personalizado',
            commands=['python custom_script.py'],
            timeout_minutes=30
        )
    ]
)
```

### Personalizar Kubernetes

Edite `kubernetes_monitoring_config.py`:

```python
# Adicionar novo deployment
self.deployments['custom_service'] = KubernetesDeployment(
    name='custom-service',
    image='apostapro/custom-service',
    image_tag='latest',
    replicas=2,
    cpu_request='250m',
    memory_request='512Mi',
    # ... outras configurações
)
```

## 📊 Monitoramento e Logs

### Logs do Sistema

- **Arquivo principal**: `complete_ml_system.log`
- **Dashboard**: `http://localhost:8050`
- **Métricas**: `http://localhost:9090` (Prometheus)
- **Grafana**: `http://localhost:3000`

### Verificar Status

```python
from run_complete_ml_system import CompleteMLSystem

system = CompleteMLSystem()
status = system.get_system_status()
print(f"Status: {status}")

# Gerar relatório
report = system.generate_system_report()
print(f"Relatório: {report}")
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de importação**:
   ```bash
   # Verificar se está no diretório correto
   cd ml_models
   python -c "import betting_apis_integration"
   ```

2. **APIs não funcionando**:
   ```bash
   # Verificar variáveis de ambiente
   echo $FOOTBALL_DATA_API_KEY
   
   # Testar API individualmente
   python -c "from betting_apis_config import betting_apis_config; print(betting_apis_config.get_enabled_apis())"
   ```

3. **Dashboard não carrega**:
   ```bash
   # Verificar se Dash está instalado
   pip install dash plotly
   
   # Verificar porta disponível
   netstat -an | grep 8050
   ```

4. **Kubernetes não funciona**:
   ```bash
   # Verificar se kubectl está disponível
   kubectl version --client
   
   # Verificar contexto
   kubectl config current-context
   ```

### Logs de Debug

```python
# Ativar logging detalhado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar status detalhado
system = CompleteMLSystem()
system.run_complete_system()
```

## 🔄 Atualizações e Manutenção

### Atualizar Configurações

```bash
# Recarregar configurações
python betting_apis_config.py
python ci_cd_pipeline_config.py
python kubernetes_monitoring_config.py
```

### Backup e Restore

```bash
# Backup das configurações
cp -r configs/ configs_backup_$(date +%Y%m%d_%H%M%S)

# Restore
cp -r configs_backup_20250813_143022/* configs/
```

## 📈 Próximos Passos

### Melhorias Planejadas

1. **Machine Learning Avançado**:
   - Deep Learning com PyTorch/TensorFlow
   - Ensemble methods
   - AutoML para seleção de modelos

2. **Infraestrutura**:
   - Multi-cloud deployment
   - Service mesh (Istio)
   - GitOps com ArgoCD

3. **Monitoramento**:
   - APM (Application Performance Monitoring)
   - Distributed tracing
   - ML model drift detection

4. **Segurança**:
   - Vault para secrets
   - Network policies
   - RBAC avançado

### Contribuições

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Submeta um Pull Request

## 📞 Suporte

- **Documentação**: Este README
- **Issues**: GitHub Issues
- **Logs**: Arquivos `.log` gerados pelo sistema
- **Configurações**: Arquivos em `configs/`

## 📄 Licença

Este projeto é parte do sistema ApostaPro e está sob licença proprietária.

---

**🎯 ApostaPro ML System** - Transformando dados em insights para apostas esportivas inteligentes!
