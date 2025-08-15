# 🚀 Sistema de Machine Learning do ApostaPro

Sistema completo e avançado de Machine Learning para análise esportiva e recomendações de apostas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Componentes Principais](#componentes-principais)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso Rápido](#uso-rápido)
- [API Endpoints](#api-endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Configuração Avançada](#configuração-avançada)
- [Monitoramento e Cache](#monitoramento-e-cache)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O sistema de ML do ApostaPro é uma solução completa que integra:

- **Análise de Sentimento**: Processamento de notícias e posts esportivos
- **Preparação de Dados**: Pipeline automatizado para dados de ML
- **Modelos de ML**: Ensemble de algoritmos para previsões esportivas
- **Sistema de Recomendações**: Geração inteligente de apostas
- **Cache Inteligente**: Otimização de performance
- **API REST**: Interface completa para integração

## 🏗️ Arquitetura do Sistema

```
ml_models/
├── config.py                 # Configuração centralizada
├── cache_manager.py          # Sistema de cache inteligente
├── sentiment_analyzer.py     # Análise de sentimento
├── data_preparation.py       # Pipeline de preparação de dados
├── ml_models.py             # Gerenciador de modelos
├── recommendation_system.py  # Sistema de recomendações
└── __init__.py              # Interface unificada

api/routers/
└── ml_router.py             # Endpoints da API

demo_ml_system.py            # Script de demonstração
requirements_ml.txt          # Dependências específicas
```

## 🔧 Componentes Principais

### 1. Sistema de Configuração (`config.py`)
- Configurações centralizadas para todos os parâmetros de ML
- Suporte a diferentes ambientes (development, production, testing)
- Configuração automática de diretórios e features

### 2. Gerenciador de Cache (`cache_manager.py`)
- Cache inteligente com TTL configurável
- Decorators para cache automático de funções
- Estatísticas de performance e limpeza automática

### 3. Analisador de Sentimento (`sentiment_analyzer.py`)
- Análise híbrida (TextBlob + Léxico esportivo)
- Palavras-chave específicas do futebol
- Processamento em lote e resumos estatísticos

### 4. Pipeline de Dados (`data_preparation.py`)
- Detecção automática de tipos de dados
- Tratamento inteligente de valores ausentes
- Codificação de variáveis categóricas
- Criação de features temporais e de interação
- Seleção de features e PCA

### 5. Gerenciador de Modelos (`ml_models.py`)
- Múltiplos algoritmos (Random Forest, XGBoost, LightGBM, etc.)
- Treinamento de modelos ensemble
- Tuning de hiperparâmetros
- Persistência e carregamento de modelos

### 6. Sistema de Recomendações (`recommendation_system.py`)
- Análise completa de partidas
- Geração de previsões para diferentes tipos de aposta
- Recomendações baseadas em nível de risco
- Cálculo de valores recomendados para apostas

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements_ml.txt
```

### 2. Configuração Inicial

```python
from ml_models.config import get_ml_config, update_ml_config

# Obter configuração atual
config = get_ml_config()

# Atualizar configurações específicas
update_ml_config(
    confidence_threshold=0.8,
    cache_ttl_hours=48
)
```

### 3. Verificar Instalação

```bash
python demo_ml_system.py
```

## ⚡ Uso Rápido

### Análise de Sentimento

```python
from ml_models.sentiment_analyzer import analyze_sentiment

# Análise simples
result = analyze_sentiment("Excelente vitória do time!")
print(f"Sentimento: {result['sentiment_label']}")
print(f"Confiança: {result['confidence']:.2f}")
```

### Sistema de Recomendações

```python
from ml_models.recommendation_system import analyze_match, generate_predictions

# Analisar partida
match_data = {
    "home_team": "Flamengo",
    "away_team": "Palmeiras",
    "home_goals_scored": 2.1,
    "away_goals_scored": 1.8,
    # ... mais dados
}

analysis = analyze_match(match_data)
predictions = generate_predictions(analysis)
```

### Cache Inteligente

```python
from ml_models.cache_manager import cache_result, timed_cache_result

@timed_cache_result(ttl_hours=24)
def minha_funcao_custosa(dados):
    # Resultado será cacheado por 24 horas
    return processar_dados(dados)
```

## 🌐 API Endpoints

### Base URL: `/ml`

#### Análise de Sentimento
- `POST /sentiment/analyze` - Analisa sentimento de um texto
- `POST /sentiment/analyze-batch` - Análise em lote

#### Preparação de Dados
- `POST /data/prepare` - Prepara dados para ML
- `GET /data/preprocessing-models` - Lista modelos de pré-processamento

#### Modelos de ML
- `POST /models/train` - Treina um modelo
- `POST /models/ensemble` - Treina modelo ensemble
- `POST /models/predict` - Faz previsão
- `GET /models/info` - Informações dos modelos

#### Recomendações
- `POST /recommendations/analyze-match` - Analisa partida
- `POST /recommendations/generate-predictions` - Gera previsões
- `POST /recommendations/betting-advice` - Recomendações de apostas

#### Cache e Monitoramento
- `GET /cache/stats` - Estatísticas do cache
- `POST /cache/clear` - Limpa cache
- `GET /health` - Saúde do sistema
- `GET /status` - Status detalhado

#### Testes
- `POST /test/sentiment` - Testa análise de sentimento
- `POST /test/recommendations` - Testa sistema de recomendações

## 📚 Exemplos de Uso

### Exemplo 1: Análise Completa de Partida

```python
from ml_models.recommendation_system import (
    analyze_match, generate_predictions, 
    get_betting_recommendations
)

# Dados da partida
match_data = {
    "match_id": "match_001",
    "home_team": "Time A",
    "away_team": "Time B",
    "home_goals_scored": 2.5,
    "away_goals_scored": 1.8,
    "home_recent_form": ["W", "W", "D", "W", "L"],
    "away_recent_form": ["L", "D", "W", "L", "W"],
    "news_sentiment": "Time da casa em excelente fase..."
}

# Pipeline completo
analysis = analyze_match(match_data)
predictions = generate_predictions(analysis)
recommendations = get_betting_recommendations(predictions, "medium", 5)

# Resultados
for rec in recommendations:
    print(f"Aposta: {rec['bet_type']}")
    print(f"Previsão: {rec['prediction']}")
    print(f"Confiança: {rec['confidence']:.2f}")
    print(f"Valor: R$ {rec['recommended_bet_amount']:.2f}")
    print("---")
```

### Exemplo 2: Pipeline de Dados Personalizado

```python
from ml_models.data_preparation import DataPreparationPipeline

pipeline = DataPreparationPipeline()

# Preparar dados com configurações específicas
prepared_data = pipeline.run_full_pipeline(
    data="meus_dados.csv",
    target_col="resultado",
    date_columns=["data_partida"],
    feature_groups=[["gols_casa", "gols_fora"]],
    apply_pca=True
)

print(f"Dados preparados: {prepared_data.shape}")
```

### Exemplo 3: Treinamento de Modelo

```python
from ml_models.ml_models import train_model, train_ensemble

# Treinar modelo individual
result = train_model(
    model_name="random_forest",
    model_type="result_prediction",
    X_train=X_train,
    y_train=y_train,
    hyperparameter_tuning=True
)

# Treinar ensemble
ensemble_result = train_ensemble(
    model_type="result_prediction",
    X_train=X_train,
    y_train=y_train,
    voting_strategy="soft"
)
```

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

```bash
export ENVIRONMENT=production
export ML_CACHE_TTL_HOURS=48
export ML_CONFIDENCE_THRESHOLD=0.8
```

### Configuração Personalizada

```python
from ml_models.config import update_ml_config

# Atualizar configurações
update_ml_config(
    confidence_threshold=0.85,
    cache_ttl_hours=72,
    enable_caching=True,
    sentiment_model_name="custom-model"
)
```

### Features Personalizadas

```python
from ml_models.config import update_ml_config

# Definir features específicas
custom_features = [
    'home_goals_scored', 'away_goals_scored',
    'home_form', 'away_form',
    'home_xg', 'away_xg',
    'custom_feature_1', 'custom_feature_2'
]

update_ml_config(feature_columns=custom_features)
```

## 📊 Monitoramento e Cache

### Estatísticas do Cache

```python
from ml_models.cache_manager import get_cache_stats

stats = get_cache_stats()
print(f"Hit Rate: {stats['hit_rate']}%")
print(f"Total Requests: {stats['total_requests']}")
print(f"Cache Hits: {stats['hits']}")
print(f"Cache Misses: {stats['misses']}")
```

### Limpeza de Cache

```python
from ml_models.cache_manager import clear_ml_cache, cleanup_expired_cache

# Limpar todo o cache
clear_ml_cache()

# Remover apenas caches expirados
removed_count = cleanup_expired_cache()
print(f"Removidos {removed_count} arquivos expirados")
```

### Monitoramento de Performance

```python
from ml_models.ml_models import get_model_info

# Informações dos modelos
models_info = get_model_info()
print(f"Total de modelos: {models_info['total_models']}")

# Informações específicas
for model_key, info in models_info['models'].items():
    print(f"{model_key}: {info['test_accuracy']}")
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de Importação
```bash
# Verificar se todas as dependências estão instaladas
pip install -r requirements_ml.txt

# Verificar se o Python path está correto
export PYTHONPATH="${PYTHONPATH}:/caminho/para/apostapro"
```

#### 2. Erro de Cache
```python
# Limpar cache corrompido
from ml_models.cache_manager import clear_ml_cache
clear_ml_cache()
```

#### 3. Erro de Modelos
```python
# Verificar se os modelos estão carregados
from ml_models.ml_models import get_model_info
info = get_model_info()
print(info)
```

#### 4. Problemas de Performance
```python
# Desabilitar cache temporariamente
from ml_models.config import update_ml_config
update_ml_config(enable_caching=False)

# Ajustar TTL do cache
update_ml_config(cache_ttl_hours=1)
```

### Logs e Debug

```python
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG)

# Ver logs específicos
logger = logging.getLogger('ml_models')
logger.setLevel(logging.DEBUG)
```

## 📈 Próximos Passos

### Melhorias Planejadas

1. **Deep Learning**: Integração com TensorFlow/PyTorch
2. **AutoML**: Seleção automática de melhores modelos
3. **MLflow**: Tracking de experimentos
4. **Streaming**: Processamento em tempo real
5. **A/B Testing**: Comparação de modelos em produção

### Contribuições

Para contribuir com o sistema:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente e teste suas mudanças
4. Envie um Pull Request

## 📞 Suporte

- **Documentação**: Este README
- **Issues**: GitHub Issues
- **Demonstração**: `python demo_ml_system.py`
- **API Docs**: `/docs` após iniciar a API

## 🏆 Conclusão

O sistema de Machine Learning do ApostaPro representa uma solução completa e profissional para análise esportiva e recomendações de apostas. Com arquitetura modular, cache inteligente e integração completa com a API, oferece uma base sólida para aplicações de ML em produção.

---

**Desenvolvido com ❤️ pela equipe ApostaPro**
