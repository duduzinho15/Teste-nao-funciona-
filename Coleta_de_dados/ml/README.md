# Módulo de Machine Learning - ApostaPro

Este módulo implementa um pipeline completo de Machine Learning para análise de apostas esportivas, incluindo preparação de dados, treinamento de modelos e geração de recomendações.

## 🏗️ Arquitetura

```
Coleta_de_dados/ml/
├── __init__.py                 # Interface do módulo
├── preparacao_dados.py         # Preparação e feature engineering
├── treinamento.py             # Treinamento de modelos ML
├── gerar_recomendacoes.py     # Geração de recomendações
└── README.md                  # Este arquivo
```

## 🚀 Funcionalidades

### 1. Preparação de Dados (`preparacao_dados.py`)

- **Feature Engineering**: Calcula estatísticas de forma dos times, sentimento médio, diferenças de performance
- **Consolidação**: Une dados de partidas, estatísticas e análise de sentimento
- **Limpeza**: Remove valores nulos e normaliza dados

**Features calculadas:**
- Forma dos times (últimos 7 dias)
- Estatísticas de gols marcados/sofridos
- Sentimento médio de notícias e posts
- Diferenças de performance entre times

### 2. Treinamento de Modelos (`treinamento.py`)

- **Múltiplos Algoritmos**: Random Forest, Gradient Boosting, Regressão Logística
- **Grid Search**: Otimização automática de hiperparâmetros
- **Validação Cruzada**: Avaliação robusta dos modelos
- **Persistência**: Salva modelos treinados em formato joblib

**Métricas de Avaliação:**
- Accuracy score
- Classification report
- Matriz de confusão
- Probabilidades por classe

### 3. Geração de Recomendações (`gerar_recomendacoes.py`)

- **Previsões**: Usa modelos treinados para prever resultados
- **Múltiplos Mercados**: Resultado final, ambas marcam, total de gols
- **Probabilidades**: Calcula odds justas baseadas nas previsões
- **Persistência**: Salva recomendações no banco de dados

## 📊 Dados de Entrada

O sistema espera as seguintes tabelas no banco:

- `partidas`: Jogos com resultados conhecidos (para treinamento)
- `clubes`: Informações dos times
- `noticias_clubes`: Notícias com análise de sentimento
- `posts_redes_sociais`: Posts com análise de sentimento

## 🎯 Dados de Saída

- **Modelos treinados**: Arquivos `.joblib` com modelos e metadados
- **Datasets**: Arquivos CSV com features para treinamento
- **Recomendações**: Registros na tabela `recomendacoes_apostas`

## 🛠️ Instalação

```bash
# Instalar dependências
pip install -r requirements_ml.txt

# Ou instalar individualmente
pip install pandas numpy scikit-learn joblib
```

## 📖 Uso

### Execução Completa

```bash
python demo_pipeline_ml.py
```

### Uso Individual dos Módulos

```python
# Preparação de dados
from Coleta_de_dados.ml.preparacao_dados import PreparadorDadosML
preparador = PreparadorDadosML()
df = preparador.preparar_dataset_treinamento()

# Treinamento
from Coleta_de_dados.ml.treinamento import TreinadorModeloML
treinador = TreinadorModeloML()
modelo_info = treinador.treinar_modelos(df)

# Geração de recomendações
from Coleta_de_dados.ml.gerar_recomendacoes import GeradorRecomendacoes
gerador = GeradorRecomendacoes()
recomendacoes = gerador.gerar_recomendacoes_partidas_futuras()
```

## 🔧 Configuração

### Diretórios

- **Modelos**: `ml_models/saved_models/` (criado automaticamente)
- **Datasets**: `ml_models/data/` (criado automaticamente)
- **Banco**: `Banco_de_dados/aposta.db` (padrão)

### Parâmetros Ajustáveis

- **Janela de análise**: 7 dias (configurável)
- **Período de treinamento**: 30-60 dias (configurável)
- **Threshold de probabilidade**: 0.5 para classificação

## 📈 Performance

### Modelos Testados

- **Random Forest**: Geralmente melhor performance para dados tabulares
- **Gradient Boosting**: Boa performance com overfitting controlado
- **Regressão Logística**: Baseline simples e interpretável

### Métricas Esperadas

- **Accuracy**: 60-80% (dependendo da qualidade dos dados)
- **Tempo de treinamento**: 1-5 minutos para datasets pequenos
- **Tempo de inferência**: <1 segundo por partida

## 🚨 Limitações e Considerações

1. **Dados Históricos**: Requer dados suficientes para treinamento
2. **Qualidade dos Dados**: Análise de sentimento depende da qualidade do texto
3. **Overfitting**: Modelos podem se ajustar demais aos dados históricos
4. **Mercado Dinâmico**: Performance pode degradar com mudanças no futebol

## 🔮 Melhorias Futuras

- **Deep Learning**: Redes neurais para capturar padrões complexos
- **Ensemble Methods**: Combinação de múltiplos modelos
- **Feature Selection**: Seleção automática de features mais relevantes
- **Online Learning**: Atualização contínua dos modelos
- **A/B Testing**: Validação de recomendações em produção

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs de execução
2. Confirme se todas as dependências estão instaladas
3. Valide se o banco de dados tem dados suficientes
4. Execute o script de demonstração para diagnóstico

## 📝 Licença

Este módulo faz parte do projeto ApostaPro e segue as mesmas diretrizes de licenciamento.

