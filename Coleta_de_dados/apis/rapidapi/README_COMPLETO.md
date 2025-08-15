# Sistema RapidAPI Completo - ApostaPro

## 📋 Visão Geral

Este módulo implementa **9 APIs RapidAPI** para coleta de dados esportivos complementares ao sistema ApostaPro. Todas as APIs seguem um padrão unificado de interface e funcionalidades.

## 🚀 APIs Implementadas

### 1. **Today Football Prediction API** ✅
- **Arquivo**: `today_football_prediction.py`
- **Host**: `today-football-prediction.p.rapidapi.com`
- **Funcionalidades**: Previsões de futebol, odds, estatísticas
- **Métodos**: `coletar_jogos()`, `coletar_ligas()`, `coletar_odds()`

### 2. **Soccer Football Info API** ✅
- **Arquivo**: `soccer_football_info.py`
- **Host**: `soccer-football-info.p.rapidapi.com`
- **Funcionalidades**: Informações gerais de futebol, jogos, jogadores
- **Métodos**: `coletar_jogos()`, `coletar_jogadores()`, `coletar_ligas()`

### 3. **Sportspage Feeds API** ✅
- **Arquivo**: `sportspage_feeds.py`
- **Host**: `sportspage-feeds.p.rapidapi.com`
- **Funcionalidades**: Feeds esportivos, notícias, atualizações em tempo real
- **Métodos**: `coletar_jogos()`, `coletar_noticias()`, `coletar_ligas()`

### 4. **Football Prediction API** ✅
- **Arquivo**: `football_prediction.py`
- **Host**: `football-prediction.p.rapidapi.com`
- **Funcionalidades**: Previsões avançadas, análises estatísticas
- **Métodos**: `coletar_jogos()`, `coletar_odds()`, `coletar_estatisticas()`

### 5. **Pinnacle Odds API** ✅
- **Arquivo**: `pinnacle_odds.py`
- **Host**: `pinnacle-odds.p.rapidapi.com`
- **Funcionalidades**: Odds de apostas, linhas de apostas
- **Métodos**: `coletar_odds()`, `coletar_linhas_apostas()`, `coletar_jogos()`

### 6. **Player Market Data API** ✅ (Substitui Transfermarkt DB)
- **Arquivo**: `player_market_data.py`
- **Host**: `api-football.p.rapidapi.com`
- **Funcionalidades**: Dados de jogadores, valores de mercado, estatísticas de carreira
- **Métodos**: `coletar_jogadores()`, `coletar_ligas()`, `coletar_estatisticas()`, `coletar_valores_mercado()`, `coletar_transferencias()`

### 7. **Football Pro API** ✅
- **Arquivo**: `football_pro.py`
- **Host**: `football-pro.p.rapidapi.com`
- **Funcionalidades**: Análises avançadas, insights táticos, estatísticas profissionais
- **Métodos**: `coletar_analises_avancadas()`, `coletar_insights_taticos()`, `coletar_estatisticas()`

### 8. **Bet365 Futebol Virtual API** ✅
- **Arquivo**: `bet365_futebol_virtual.py`
- **Host**: `bet36528.p.rapidapi.com`
- **Funcionalidades**: Futebol virtual, odds virtuais, resultados virtuais
- **Métodos**: `coletar_jogos()`, `coletar_resultados_virtuais()`, `coletar_odds()`

### 9. **SportAPI7 API** ✅
- **Arquivo**: `sportapi7.py`
- **Host**: `sportapi7.p.rapidapi.com`
- **Funcionalidades**: Dados esportivos avançados, ratings de jogadores, estatísticas detalhadas
- **Métodos**: `coletar_jogos()`, `coletar_jogadores()`, `coletar_ligas()`, `coletar_estatisticas()`, `coletar_ratings_jogador()`, `coletar_dados_time()`, `coletar_estatisticas_avancadas()`

## 🔑 **APIs Adicionais Disponíveis** ✅
- **Bet365Data**: `bet365data.p.rapidapi.com` - Dados esportivos gerais
- **BetsAPI**: `betsapi.p.rapidapi.com` - API de apostas

## 🏗️ Arquitetura

### Classe Base: `RapidAPIBase`
Todas as APIs herdam desta classe abstrata que fornece:

- **Gerenciamento de API Keys**: Rotação automática de chaves
- **Rate Limiting**: Controle de limites de requisições
- **Retry Mechanism**: Tentativas automáticas em caso de falha
- **Logging Centralizado**: Sistema de logs estruturado
- **Métodos Padrão**: Interface unificada para todas as APIs

### Métodos Padrão Implementados
```python
async def coletar_jogos() -> List[Dict[str, Any]]
async def coletar_jogadores() -> List[Dict[str, Any]]
async def coletar_ligas() -> List[Dict[str, Any]]
async def coletar_estatisticas() -> List[Dict[str, Any]]
async def coletar_odds() -> List[Dict[str, Any]]
async def coletar_noticias() -> List[Dict[str, Any]]
```

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# Chave principal do RapidAPI (JÁ CONFIGURADA)
RAPIDAPI_KEY=76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6

# Chaves específicas (opcional)
RAPIDAPI_TODAY_FOOTBALL_KEY=76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6
RAPIDAPI_SOCCER_FOOTBALL_KEY=76fc2644acmsh7cd74e5849f04a7p18bfc7jsn81c96ac958a6
# ... outras chaves específicas
```

### Configuração no Código
```python
from Coleta_de_dados.apis.rapidapi import TodayFootballPredictionAPI

# Usar chave padrão
api = TodayFootballPredictionAPI()

# Ou especificar chave personalizada
api = TodayFootballPredictionAPI(api_key="chave_personalizada")
```

## 📊 Funcionalidades Específicas

### APIs de Previsão
- **Today Football Prediction**: Previsões diárias
- **Football Prediction**: Análises estatísticas avançadas

### APIs de Dados
- **Soccer Football Info**: Dados gerais de futebol
- **Sportspage Feeds**: Feeds em tempo real
- **Transfermarkt DB**: Dados de mercado e transferências

### APIs de Apostas
- **Pinnacle Odds**: Odds profissionais
- **Bet365 Futebol Virtual**: Futebol virtual

### APIs de Análise
- **Football Pro**: Análises avançadas e insights táticos

## 🚀 Uso

### Importação Básica
```python
from Coleta_de_dados.apis.rapidapi import (
    TodayFootballPredictionAPI,
    SoccerFootballInfoAPI,
    SportspageFeedsAPI,
    FootballPredictionAPI,
    PinnacleOddsAPI,
    TransfermarktDBAPI,
    FootballProAPI,
    Bet365FutebolVirtualAPI
)
```

### Exemplo de Uso
```python
async def exemplo_coleta():
    # Inicializar API
    api = TodayFootballPredictionAPI()
    
    # Coletar dados
    jogos = await api.coletar_jogos()
    ligas = await api.coletar_ligas()
    odds = await api.coletar_odds()
    
    print(f"Coletados: {len(jogos)} jogos, {len(ligas)} ligas, {len(odds)} odds")
```

## 🧪 Testes

### Script de Demonstração Completa
```bash
python demo_todas_apis_rapidapi.py
```

Este script testa todas as 8 APIs implementadas e fornece um relatório completo de funcionamento.

### Testes Individuais
Cada API possui uma função `demo_*()` que pode ser executada individualmente:

```python
# Testar API específica
from Coleta_de_dados.apis.rapidapi.today_football_prediction import demo_today_football_prediction
await demo_today_football_prediction()
```

## 📈 Monitoramento

### Sistema de Logs
- **Logs Estruturados**: Formato JSON para fácil análise
- **Performance Monitoring**: Métricas de tempo de resposta
- **Alertas**: Notificações em caso de falhas
- **Rotação**: Gerenciamento automático de arquivos de log

### Métricas Coletadas
- Tempo de resposta por API
- Taxa de sucesso/erro
- Número de requisições por minuto
- Uso de API keys

## 🔄 Rate Limiting

### Limites Configurados
- **Padrão**: 100 requisições por dia por API
- **Configurável**: Via arquivo de configuração
- **Inteligente**: Pausa automática quando limites são atingidos

### Estratégias de Controle
- **API Key Rotation**: Múltiplas chaves para maior throughput
- **Request Spacing**: Delays inteligentes entre requisições
- **Fallback**: Múltiplas APIs para redundância

## 🛠️ Manutenção

### Atualizações
- **Versões**: Controle de versão para cada API
- **Compatibilidade**: Manutenção de compatibilidade com versões anteriores
- **Documentação**: Atualizações automáticas da documentação

### Troubleshooting
- **Logs Detalhados**: Informações completas para debugging
- **Fallbacks**: Mecanismos de recuperação automática
- **Health Checks**: Verificações de saúde das APIs

## 📚 Documentação Adicional

### Arquivos de Configuração
- `Coleta_de_dados/apis_externas/config.py`: Configuração centralizada
- `Coleta_de_dados/apis/rapidapi/__init__.py`: Exposição das classes

### Exemplos de Uso
- `demo_todas_apis_rapidapi.py`: Demonstração completa
- Funções `demo_*()` em cada arquivo de API

### Logs e Monitoramento
- `Coleta_de_dados/utils/logger_centralizado.py`: Sistema de logs

## 🎯 Próximos Passos

### Implementações Futuras
- **Cache Inteligente**: Sistema de cache para reduzir requisições
- **Orquestração**: Coleta paralela de múltiplas APIs
- **Fallbacks Automáticos**: Troca automática entre APIs em caso de falha
- **Machine Learning**: Análise preditiva de performance das APIs

### Integrações
- **Dashboard Web**: Interface para monitoramento em tempo real
- **Alertas**: Sistema de notificações para problemas
- **Relatórios**: Geração automática de relatórios de performance

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs em `Coleta_de_dados/utils/logs/`
2. Executar script de demonstração para diagnóstico
3. Consultar documentação específica de cada API
4. Verificar configuração em `config.py`

---

**Status**: ✅ **COMPLETO** - Todas as 9 APIs RapidAPI implementadas e testadas
**Versão**: 2.0
**Última Atualização**: 2025-08-14
