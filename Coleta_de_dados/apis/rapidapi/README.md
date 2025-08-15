# 🚀 Módulo RapidAPI - ApostaPro

## 📋 Visão Geral

O módulo RapidAPI integra múltiplas APIs complementares do RapidAPI para fornecer dados adicionais ao sistema ApostaPro. Todas as APIs seguem um padrão consistente de interface e tratamento de erros.

## 🏗️ Arquitetura

```
rapidapi/
├── __init__.py              # Exportações do módulo
├── base_rapidapi.py         # Classe base com funcionalidades comuns
├── today_football_prediction.py  # API de previsões de futebol
├── soccer_football_info.py  # Informações gerais de futebol
├── sportspage_feeds.py      # Feeds esportivos
├── football_prediction.py   # Previsões avançadas
├── pinnacle_odds.py         # Odds da Pinnacle
├── bet365_futebol_virtual.py # Futebol virtual Bet365
├── transfermarkt_db.py      # Base de dados Transfermarkt
├── football_pro.py          # API Football Pro (Sportmonks)
└── README.md               # Esta documentação
```

## 🔧 Funcionalidades Padronizadas

Todas as APIs implementam as seguintes funções:

### 1. `coletar_jogos(**kwargs) -> List[Dict[str, Any]]`
Coleta dados de jogos com informações como:
- Times participantes
- Data e hora
- Liga/competição
- Previsões e odds
- Estatísticas básicas

### 2. `coletar_jogadores(**kwargs) -> List[Dict[str, Any]]`
Coleta informações de jogadores:
- Dados pessoais
- Estatísticas de carreira
- Valor de mercado
- Status atual

### 3. `coletar_ligas(**kwargs) -> List[Dict[str, Any]]`
Coleta dados de ligas e competições:
- Informações básicas
- Times participantes
- Temporada atual
- Status da competição

### 4. `coletar_estatisticas(**kwargs) -> List[Dict[str, Any]]`
Coleta estatísticas detalhadas:
- Estatísticas de times
- Estatísticas de jogos
- Métricas de performance
- Histórico de resultados

### 5. `coletar_odds(**kwargs) -> List[Dict[str, Any]]`
Coleta odds e probabilidades:
- Odds de diferentes casas
- Probabilidades calculadas
- Mercados disponíveis
- Histórico de variações

### 6. `coletar_noticias(**kwargs) -> List[Dict[str, Any]]`
Coleta notícias e informações:
- Notícias de times
- Notícias de ligas
- Transferências
- Lesões e suspensões

## 🚀 Como Usar

### Configuração Básica

```python
from Coleta_de_dados.apis.rapidapi import TodayFootballPredictionAPI

# Inicializar com suas chaves de API
api = TodayFootballPredictionAPI([
    "sua_chave_rapidapi_1",
    "sua_chave_rapidapi_2"  # Para rotação
])

# Coletar jogos de hoje
jogos_hoje = api.coletar_jogos()

# Coletar odds para um jogo específico
odds_jogo = api.coletar_odds(jogo_id="12345")

# Verificar status da API
status = api.get_status()
print(f"Requisições hoje: {status['requisicoes_hoje']}")
```

### Exemplo de Uso Completo

```python
import asyncio
from Coleta_de_dados.apis.rapidapi import TodayFootballPredictionAPI
from Coleta_de_dados.utils.logger_centralizado import log_info, log_performance_decorator

class ColetorRapidAPI:
    def __init__(self):
        self.api = TodayFootballPredictionAPI([
            "chave_1",
            "chave_2"
        ])
    
    @log_performance_decorator("rapidapi")
    def coletar_dados_completos(self, data: str = None):
        """Coleta dados completos de uma data específica."""
        try:
            # Coletar jogos
            jogos = self.api.coletar_jogos(data)
            log_info("rapidapi", "coletar_dados_completos", 
                    f"Coletados {len(jogos)} jogos", {"data": data, "total_jogos": len(jogos)})
            
            # Coletar odds para cada jogo
            odds_todos = []
            for jogo in jogos:
                if "id" in jogo:
                    odds = self.api.coletar_odds(jogo["id"])
                    odds_todos.extend(odds)
            
            log_info("rapidapi", "coletar_dados_completos", 
                    f"Coletadas {len(odds_todos)} odds", {"total_odds": len(odds_todos)})
            
            return {
                "jogos": jogos,
                "odds": odds_todos,
                "total_registros": len(jogos) + len(odds_todos)
            }
            
        except Exception as e:
            log_error("rapidapi", "coletar_dados_completos", 
                     "Erro na coleta completa", {"data": data}, error_details=str(e))
            raise

# Uso
coletor = ColetorRapidAPI()
dados = coletor.coletar_dados_completos("2025-08-14")
```

## 📊 Estrutura de Dados Padronizada

### Jogos
```json
{
    "id": "match_123",
    "data": "2025-08-14",
    "hora": "16:00",
    "liga": "Premier League",
    "pais": "England",
    "time_casa": "Manchester United",
    "time_visitante": "Liverpool",
    "probabilidade_casa": 0.35,
    "probabilidade_empate": 0.28,
    "probabilidade_visitante": 0.37,
    "odds_casa": 2.85,
    "odds_empate": 3.20,
    "odds_visitante": 2.70,
    "previsao_recomendada": "away_win",
    "confianca": 0.75,
    "fonte": "Today Football Prediction",
    "coletado_em": "2025-08-14T10:00:00"
}
```

### Jogadores
```json
{
    "id": "player_456",
    "nome": "Bruno Fernandes",
    "posicao": "Midfielder",
    "idade": 26,
    "altura": 179,
    "peso": 69,
    "nacionalidade": "Portugal",
    "valor_mercado": 80000000,
    "contrato_ate": "2026-06-30",
    "fonte": "Today Football Prediction",
    "coletado_em": "2025-08-14T10:00:00"
}
```

### Odds
```json
{
    "jogo_id": "match_123",
    "casa_aposta": "Bet365",
    "mercado": "1X2",
    "selecao": "away_win",
    "odds": 2.70,
    "probabilidade": 0.37,
    "fonte": "Today Football Prediction",
    "coletado_em": "2025-08-14T10:00:00"
}
```

## ⚠️ Rate Limiting e Tratamento de Erros

### Rate Limiting Automático
- **Limite diário**: Configurável por API
- **Limite por minuto**: Configurável por API
- **Rotação de chaves**: Automática quando múltiplas chaves são fornecidas
- **Retry automático**: Com backoff exponencial

### Tratamento de Erros
```python
try:
    dados = api.coletar_jogos()
except Exception as e:
    if "Rate limit" in str(e):
        print("Rate limit atingido, aguarde...")
    elif "API key" in str(e):
        print("Chave de API inválida")
    else:
        print(f"Erro inesperado: {e}")
```

## 🔑 Configuração de Chaves de API

### 1. Obter Chaves do RapidAPI
1. Acesse [rapidapi.com](https://rapidapi.com)
2. Crie uma conta ou faça login
3. Assine as APIs desejadas
4. Copie suas chaves de API

### 2. Configurar Variáveis de Ambiente
```bash
# .env
RAPIDAPI_KEY_1=sua_chave_1
RAPIDAPI_KEY_2=sua_chave_2
RAPIDAPI_KEY_3=sua_chave_3
```

### 3. Usar no Código
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_keys = [
    os.getenv("RAPIDAPI_KEY_1"),
    os.getenv("RAPIDAPI_KEY_2"),
    os.getenv("RAPIDAPI_KEY_3")
]

api = TodayFootballPredictionAPI(api_keys)
```

## 📈 Monitoramento e Logs

### Logs Estruturados
Todos os módulos usam o sistema de logs centralizado:

```python
from Coleta_de_dados.utils.logger_centralizado import (
    log_info, log_error, log_performance_decorator
)

# Log de informação
log_info("rapidapi", "coletar_jogos", "Iniciando coleta", {"data": "2025-08-14"})

# Log de erro
log_error("rapidapi", "coletar_jogos", "Erro na coleta", {"data": "2025-08-14"}, error_details=str(e))

# Decorator de performance
@log_performance_decorator("rapidapi")
def minha_funcao():
    # código aqui
    pass
```

### Dashboard de Status
```python
# Verificar status de todas as APIs
status_geral = {
    "today_football_prediction": api.get_status(),
    "performance": centralized_logger.get_performance_summary(),
    "alertas": centralized_logger.get_alerts()
}

print(json.dumps(status_geral, indent=2))
```

## 🧪 Testes

### Teste Básico
```python
def test_api_basica():
    """Testa funcionalidades básicas da API."""
    api = TodayFootballPredictionAPI(["chave_teste"])
    
    # Testar coleta de ligas
    ligas = api.coletar_ligas()
    assert isinstance(ligas, list)
    
    # Testar coleta de jogos
    jogos = api.coletar_jogos()
    assert isinstance(jogos, list)
    
    print("✅ Testes básicos passaram!")

if __name__ == "__main__":
    test_api_basica()
```

### Teste de Performance
```python
import time

def test_performance():
    """Testa performance da API."""
    api = TodayFootballPredictionAPI(["chave_teste"])
    
    start_time = time.time()
    jogos = api.coletar_jogos()
    execution_time = time.time() - start_time
    
    print(f"⏱️ Tempo de execução: {execution_time:.2f}s")
    print(f"📊 Jogos coletados: {len(jogos)}")
    
    assert execution_time < 30.0  # Máximo 30 segundos
    print("✅ Teste de performance passou!")

if __name__ == "__main__":
    test_performance()
```

## 🚀 Próximos Passos

### Implementações Pendentes
- [ ] `soccer_football_info.py` - Informações gerais de futebol
- [ ] `sportspage_feeds.py` - Feeds esportivos
- [ ] `football_prediction.py` - Previsões avançadas
- [ ] `pinnacle_odds.py` - Odds da Pinnacle
- [ ] `bet365_futebol_virtual.py` - Futebol virtual Bet365
- [ ] `transfermarkt_db.py` - Base de dados Transfermarkt
- [ ] `football_pro.py` - API Football Pro

### Melhorias Futuras
- [ ] Cache inteligente para reduzir requisições
- [ ] Sistema de fallback entre APIs
- [ ] Validação de dados mais robusta
- [ ] Integração com sistema de alertas
- [ ] Dashboard web para monitoramento

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do sistema
2. Consulte a documentação da API específica
3. Teste com chaves de API válidas
4. Verifique limites de rate limiting

## 📄 Licença

Este módulo é parte do projeto ApostaPro e segue as mesmas diretrizes de licenciamento.

---

**Autor**: Sistema de Coleta de Dados ApostaPro  
**Data**: 2025-08-14  
**Versão**: 1.0
