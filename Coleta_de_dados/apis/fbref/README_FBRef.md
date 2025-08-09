# 🏈 Sistema FBRef - ApostaPro

Este módulo contém o sistema completo de coleta de dados do FBRef para o projeto ApostaPro.

## 📋 Visão Geral

O sistema FBRef é responsável por coletar dados completos de:
- **Competições e Temporadas**: Todas as ligas, copas e torneios disponíveis
- **Partidas**: Dados de jogos com links para match reports
- **Estatísticas Detalhadas**: Métricas completas de times e jogadores por partida
- **Clubes**: Informações de clubes de todos os países (masculino e feminino)
- **Jogadores**: Dados de jogadores com estatísticas por tipo de competição

## 🏗️ Arquitetura

### Módulos Principais

1. **`fbref_integrado.py`** - Descoberta de competições e temporadas
2. **`coletar_dados_partidas.py`** - Coleta de dados de partidas
3. **`coletar_estatisticas_detalhadas.py`** - Estatísticas detalhadas de partidas
4. **`verificar_extracao.py`** - Verificação da completude da extração
5. **`coletar_clubes.py`** - Coleta de dados de clubes
6. **`coletar_jogadores.py`** - Coleta de dados de jogadores
7. **`orquestrador_coleta.py`** - Orquestração completa da pipeline

### Estrutura do Banco de Dados

#### Tabelas Principais (Competições)
- `competicoes` - Lista de competições
- `links_para_coleta` - Links de temporadas para coleta
- `partidas` - Dados básicos de partidas
- `estatisticas_time_partida` - Estatísticas de times por partida
- `estatisticas_jogador_partida` - Estatísticas de jogadores por partida

#### Tabelas de Clubes
- `paises_clubes` - Países com clubes
- `clubes` - Informações de clubes
- `estatisticas_clube` - Estatísticas de clubes
- `records_vs_opponents` - Records contra adversários

#### Tabelas de Jogadores
- `paises_jogadores` - Países com jogadores
- `jogadores` - Informações de jogadores
- `estatisticas_jogador_geral` - Estatísticas gerais
- `estatisticas_jogador_competicao` - Estatísticas por tipo de competição

## 🚀 Como Usar

### 1. Execução Completa da Pipeline

```bash
# Executa toda a pipeline FBRef
python run.py
```

### 2. Execução Individual de Módulos

```bash
# Descoberta de competições e temporadas
python -m Coleta_de_dados.apis.fbref.fbref_integrado

# Verificação da completude
python -m Coleta_de_dados.apis.fbref.verificar_extracao

# Coleta de partidas
python -m Coleta_de_dados.apis.fbref.coletar_dados_partidas

# Coleta de estatísticas detalhadas
python -m Coleta_de_dados.apis.fbref.coletar_estatisticas_detalhadas

# Coleta de clubes
python -m Coleta_de_dados.apis.fbref.coletar_clubes

# Coleta de jogadores
python -m Coleta_de_dados.apis.fbref.coletar_jogadores
```

### 3. Usando o Orquestrador

```python
from Coleta_de_dados.apis.fbref.orquestrador_coleta import OrquestradorColeta

# Execução completa
orquestrador = OrquestradorColeta()
orquestrador.executar_pipeline_completa()

# Execução de etapa específica
orquestrador.executar_etapa_individual("descoberta_links")

# Listar etapas disponíveis
orquestrador.listar_etapas()
```

### 4. Testando o Sistema

```bash
# Executa todos os testes
python teste_sistema_fbref.py
```

## 📊 Fluxo de Dados

### Etapa 1: Descoberta de Links
1. Acessa `/en/comps/` para obter lista de competições
2. Para cada competição, extrai links de temporadas
3. Salva no banco: `competicoes` e `links_para_coleta`

### Etapa 2: Verificação de Completude
1. Verifica se todas as temporadas foram extraídas
2. Compara com o site para identificar faltantes
3. Gera relatório de status

### Etapa 3: Coleta de Partidas
1. Para cada temporada, encontra link "Scores & Fixtures"
2. Extrai dados de partidas da tabela
3. Identifica links de "Match Report" ou links de score
4. Salva no banco: `partidas`

### Etapa 4: Estatísticas Detalhadas
1. Para cada partida, acessa o match report
2. Extrai estatísticas de times e jogadores
3. Salva no banco: `estatisticas_time_partida` e `estatisticas_jogador_partida`

### Etapa 5: Coleta de Clubes
1. Acessa `/en/squads/` para obter países
2. Para cada país, extrai lista de clubes
3. Identifica gênero (M/F) e links de records
4. Salva no banco: `paises_clubes` e `clubes`

### Etapa 6: Coleta de Jogadores
1. Para cada país, acessa página de jogadores
2. Extrai lista de jogadores
3. Constrói URLs para diferentes tipos de estatísticas
4. Salva no banco: `paises_jogadores` e `jogadores`

## 🔧 Configurações

### Timeouts
- **Descoberta de Links**: 30 minutos
- **Coleta de Partidas**: 1 hora
- **Estatísticas Detalhadas**: 2 horas
- **Coleta de Clubes**: 1 hora
- **Coleta de Jogadores**: 1 hora

### Logging
O sistema usa logging detalhado com:
- Logs de progresso
- Relatórios de estatísticas
- Tratamento de erros
- Checkpoints automáticos

## 📈 Monitoramento

### Verificação de Status
```python
from Coleta_de_dados.apis.fbref.verificar_extracao import VerificadorExtracao

verificador = VerificadorExtracao()
stats = verificador.executar_verificacao_completa()
```

### Relatórios Disponíveis
- Status de competições (completa/incompleta)
- Contagem de temporadas extraídas
- Estatísticas de partidas coletadas
- Progresso de clubes e jogadores

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Timeout de Requisições**
   - Aumentar timeouts no orquestrador
   - Verificar conectividade com FBRef

2. **Estrutura HTML Alterada**
   - Verificar seletores CSS nos módulos
   - Atualizar lógica de extração

3. **Banco de Dados Bloqueado**
   - Verificar se não há outras instâncias rodando
   - Usar `PRAGMA journal_mode=WAL`

### Logs de Debug
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 📝 Notas Importantes

1. **Respeito ao Site**: O sistema inclui delays entre requisições para não sobrecarregar o FBRef
2. **Robustez**: Múltiplas estratégias de extração para lidar com diferentes layouts
3. **Checkpoints**: Sistema salva progresso automaticamente
4. **Tratamento de Erros**: Continua execução mesmo com falhas pontuais

## 🔄 Atualizações

Para atualizar dados:
1. Execute a verificação para identificar faltantes
2. Use o orquestrador para executar etapas específicas
3. Monitore logs para garantir sucesso

## 📞 Suporte

Em caso de problemas:
1. Execute `teste_sistema_fbref.py` para diagnóstico
2. Verifique logs em `logs/`
3. Consulte relatórios de verificação
4. Verifique conectividade com FBRef 