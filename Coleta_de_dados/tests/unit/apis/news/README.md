# Testes do Módulo de Notícias

Este diretório contém testes unitários e de integração para o módulo `Coleta_de_dados.apis.news.collector`.

## Estrutura de Diretórios

```
tests/unit/apis/news/
├── __init__.py
├── test_news_collector.py  # Testes do NewsCollector
└── test_data/              # Dados de teste (se necessário)
```

## Como Executar os Testes

1. Certifique-se de que todas as dependências de desenvolvimento estão instaladas:

```bash
pip install pytest pytest-mock requests beautifulsoup4 lxml
```

2. Execute os testes com o pytest:

```bash
# Executar todos os testes
pytest Coleta_de_dados/tests/unit/apis/news/

# Executar testes específicos (ex: apenas testes unitários)
pytest Coleta_de_dados/tests/unit/apis/news/ -k "TestNewsCollectorUnit"

# Executar com relatório detalhado
pytest Coleta_de_dados/tests/unit/apis/news/ -v
```

## Tipos de Testes

### Testes Unitários
- `TestNewsCollectorUnit`: Testa métodos individuais do `NewsCollector` de forma isolada
  - Testa o parser de datas
  - Testa o parser de elementos HTML de notícias
  - Testa casos de borda e erros

### Testes de Integração
- `TestNewsCollectorIntegration`: Testa a integração entre métodos do `NewsCollector`
  - Testa a coleta de notícias do Globo Esporte (com mock de requisições HTTP)
  - Testa a obtenção de conteúdo completo de notícias
  - Testa o fluxo completo de coleta de notícias

### Testes de Banco de Dados
- `TestNewsCollectorDatabaseIntegration`: Testa a integração com o banco de dados
  - Testa o salvamento de notícias no banco
  - Testa o tratamento de notícias duplicadas

### Testes de Fluxo Completo
- `TestNewsCollectorFullFlow`: Testa o fluxo completo do `NewsCollector`
  - Testa o método principal `coletar_noticias_clube`
  - Testa o tratamento de erros (ex: clube não encontrado)

## Dependências de Teste

- `pytest`: Framework de testes
- `pytest-mock`: Para criar mocks em testes
- `requests`: Para simular requisições HTTP
- `beautifulsoup4` e `lxml`: Para análise de HTML nos testes

## Boas Práticas

1. **Nomes Descritivos**: Use nomes descritivos para classes e métodos de teste
2. **Testes Isolados**: Cada teste deve ser independente e não depender do estado de outros testes
3. **Mocks**: Use mocks para dependências externas (HTTP, banco de dados)
4. **Asserções Específicas**: Use asserções específicas para melhor mensagem de erro
5. **Cobertura**: Almeje alta cobertura de código, mas priorize testes significativos

## Adicionando Novos Testes

1. Crie uma nova classe de teste que herda de `unittest.TestCase`
2. Adicione métodos de teste com nomes que comecem com `test_`
3. Use fixtures do pytest para configurar dados de teste comuns
4. Adicione asserções para verificar o comportamento esperado

## Solução de Problemas

Se os testes falharem:
1. Verifique a mensagem de erro para entender o que deu errado
2. Verifique se todas as dependências estão instaladas corretamente
3. Verifique se o banco de dados de teste está configurado corretamente
4. Execute os testes com a flag `-v` para obter mais detalhes
