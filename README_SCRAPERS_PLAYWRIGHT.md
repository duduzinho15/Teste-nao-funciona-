# 🎭 SCRAPERS COM PLAYWRIGHT - APOSTAPRO

Sistema avançado de web scraping usando **Playwright da Microsoft** para coleta de dados esportivos de múltiplas fontes.

## 🚀 **VANTAGENS DO PLAYWRIGHT**

### ✅ **Performance Superior**
- **Auto-wait inteligente** para elementos
- **Suporte nativo** para múltiplos navegadores (Chromium, Firefox, WebKit)
- **Modo headless otimizado** para produção
- **Interceptação de requisições** para melhor controle

### ✅ **Anti-Detecção Avançado**
- **User agents rotativos** para simular navegadores reais
- **Headers personalizados** para evitar bloqueios
- **Comportamento humano** simulado
- **Rate limiting inteligente** para respeitar limites dos sites

### ✅ **Funcionalidades Avançadas**
- **Screenshots automáticos** para debug
- **Gravação de vídeo** das sessões
- **Arquivos HAR** para análise de rede
- **Retry automático** em falhas
- **Logging detalhado** para monitoramento

## 🏗️ **ARQUITETURA DO SISTEMA**

```
📁 Coleta_de_dados/
├── 📁 apis/
│   ├── 🎭 playwright_base.py          # Classe base para todos os scrapers
│   ├── 🏆 fbref/
│   │   └── playwright_scraper.py      # Scraper do FBRef
│   ├── ⚽ sofascore/
│   │   └── playwright_scraper.py      # Scraper do SofaScore
│   └── ⚙️ scraper_config.py           # Configuração centralizada
├── 🎯 orquestrador_scrapers.py        # Orquestrador principal
└── 📊 demo_playwright_scrapers.py     # Script de demonstração
```

## 🎯 **SCRAPERS IMPLEMENTADOS**

### 🏆 **FBRef Scraper**
- **URLs**: 10+ competições principais (Premier League, La Liga, Champions League, etc.)
- **Dados**: Estatísticas de clubes, partidas, jogadores
- **Rate Limit**: 2 segundos entre requisições
- **Funcionalidades**: Paginação automática, extração de tabelas

### ⚽ **SofaScore Scraper**
- **URLs**: Times principais, torneios, partidas ao vivo
- **Dados**: Resultados em tempo real, estatísticas, odds
- **Rate Limit**: 3 segundos entre requisições (mais conservador)
- **Funcionalidades**: Coleta de partidas ao vivo, histórico de times

### 📊 **FlashScore Scraper** (Configurado)
- **URLs**: 5 ligas principais
- **Dados**: Resultados, estatísticas, odds
- **Rate Limit**: 2.5 segundos entre requisições

### 📈 **WhoScored Scraper** (Configurado)
- **URLs**: 5 regiões principais
- **Dados**: Estatísticas avançadas, análises táticas
- **Rate Limit**: 3 segundos entre requisições

## ⚙️ **CONFIGURAÇÃO**

### 🔧 **Configuração Base**
```python
from Coleta_de_dados.apis.scraper_config import ScraperConfig

# Configuração para desenvolvimento
config = ScraperConfig.get_playwright_config(
    headless=False,      # Mostrar navegador para debug
    timeout=30000,       # 30 segundos
    enable_video=True    # Gravar vídeo para debug
)

# Configuração para produção
config = ScraperConfig.get_playwright_config(
    headless=True,       # Executar em background
    timeout=120000,      # 2 minutos para estabilidade
    enable_video=False   # Não gravar vídeo em produção
)
```

### 🌍 **Configurações por Ambiente**
```python
# Desenvolvimento
config = get_config_for_environment("dev")

# Produção
config = get_config_for_environment("prod")
```

### 📊 **Rate Limiting Configurável**
```python
RATE_LIMITING = {
    "global_delay": 1.0,           # Delay mínimo entre requisições
    "max_requests_per_minute": 30, # Máximo por minuto
    "max_requests_per_hour": 1000, # Máximo por hora
    "backoff_factor": 2.0,         # Fator de backoff exponencial
    "max_retries": 5               # Máximo de tentativas
}
```

## 🚀 **USO BÁSICO**

### 📝 **Exemplo Simples**
```python
from Coleta_de_dados.apis.fbref.playwright_scraper import FBRefPlaywrightScraper

async def coletar_dados():
    async with FBRefPlaywrightScraper(headless=False) as scraper:
        # Coletar competições
        competitions = await scraper.collect_competitions()
        print(f"✅ {len(competitions)} competições encontradas")
        
        # Coletar partidas
        matches = await scraper.collect_matches(competitions[0]['url'])
        print(f"✅ {len(matches)} partidas coletadas")
        
        # Screenshot para debug
        await scraper.take_screenshot("fbref_demo.png")

# Executar
import asyncio
asyncio.run(coletar_dados())
```

### 🎭 **Exemplo com Funcionalidades Avançadas**
```python
from Coleta_de_dados.apis.playwright_base import PlaywrightBaseScraper

async def exemplo_avancado():
    async with PlaywrightBaseScraper(
        headless=False,
        enable_video=True,
        enable_har=True
    ) as scraper:
        
        # Navegar para página
        await scraper.navigate_to("https://example.com")
        
        # Aguardar elemento específico
        await scraper.wait_for_element("h1")
        
        # Executar JavaScript
        title = await scraper.evaluate_javascript("document.title")
        print(f"Título: {title}")
        
        # Screenshot
        await scraper.take_screenshot("exemplo.png")
        
        # Dados interceptados
        intercepted = scraper.get_intercepted_data()
        print(f"Requisições: {len(intercepted['requests'])}")
```

## 🎯 **ORQUESTADOR CENTRALIZADO**

### 🔄 **Execução Coordenada**
```python
from Coleta_de_dados.orquestrador_scrapers import OrquestradorScrapers

async def executar_coleta():
    orchestrator = OrquestradorScrapers(environment="dev")
    
    # Iniciar
    await orchestrator.start()
    
    # Executar ciclo único
    stats = await orchestrator.run_collection_cycle("teste")
    print(f"Dados coletados: {stats['total_data_collected']}")
    
    # Parar
    await orchestrator.stop()

# Executar
asyncio.run(executar_coleta())
```

### ⏰ **Agendamento Automático**
```python
# Executar coleta a cada hora
await orchestrator.run_scheduled_collection(interval_minutes=60)
```

### 📊 **Monitoramento de Saúde**
```python
# Verificar status
health = orchestrator.get_health_status()
print(f"Status: {health['overall_status']}")
print(f"Taxa de sucesso: {health['success_rate']:.2%}")
```

## 🧪 **TESTES E DEMONSTRAÇÃO**

### 🎬 **Script de Demonstração**
```bash
# Executar demonstração completa
python demo_playwright_scrapers.py
```

### 📋 **Testes Disponíveis**
1. **Funcionalidades Base do Playwright**
   - Navegação, screenshots, interceptação
2. **Scraper do FBRef**
   - Coleta de competições e partidas
3. **Scraper do SofaScore**
   - Partidas ao vivo e histórico de times

## 📁 **ESTRUTURA DE ARQUIVOS GERADOS**

### 📸 **Screenshots**
```
screenshots/
├── fbref/
│   ├── fbref_demo.png
│   └── error_competitions.png
├── sofascore/
│   ├── sofascore_demo.png
│   └── error_live_matches.png
└── playwright_features_demo.png
```

### 📊 **Dados Coletados**
```
collected_data/
├── fbref_data_20250814_153000.json
├── sofascore_data_20250814_153000.json
└── ...
```

### 📈 **Estatísticas**
```
stats/
├── cycle_test_cycle_20250814_153000.json
├── orchestrator_final_20250814_153000.json
└── ...
```

### 🎥 **Vídeos (se habilitado)**
```
screenshots/
├── session_20250814_153000.mp4
└── ...
```

### 📋 **Arquivos HAR**
```
screenshots/
├── session_20250814_153000.har
└── ...
```

## 🔧 **INSTALAÇÃO E CONFIGURAÇÃO**

### 📦 **Dependências**
```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install
```

### 🐍 **Verificação da Instalação**
```python
# Testar se Playwright está funcionando
from playwright.async_api import async_playwright

async def test_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        print("✅ Playwright funcionando!")
        await browser.close()

asyncio.run(test_playwright())
```

## 🚨 **TRATAMENTO DE ERROS**

### ⚠️ **Erros Comuns**
- **Timeout**: Aumentar `timeout` na configuração
- **Elemento não encontrado**: Verificar seletores CSS
- **Rate limiting**: Aumentar `rate_limit_delay`
- **Navegador não inicia**: Verificar instalação do Playwright

### 🔄 **Retry Automático**
```python
# Configuração de retry
max_retries = 3
retry_delay = 2

# O sistema tenta automaticamente em caso de falha
```

## 📊 **MONITORAMENTO E LOGS**

### 📝 **Logs Automáticos**
```
logs/
└── scrapers.log
```

### 📊 **Métricas Coletadas**
- Taxa de sucesso por scraper
- Tempo de execução por ciclo
- Quantidade de dados coletados
- Erros e falhas
- Uptime do sistema

## 🚀 **PRÓXIMOS PASSOS**

### 🔮 **Funcionalidades Futuras**
1. **Mais Scrapers**
   - ESPN, Transfermarkt, etc.
2. **Sistema de Proxies**
   - Rotação automática de IPs
3. **Cache Inteligente**
   - Evitar re-coleta de dados
4. **Notificações**
   - Email, Slack, Discord
5. **Dashboard Web**
   - Monitoramento em tempo real

### 🔧 **Otimizações**
1. **Paralelização**
   - Múltiplos scrapers simultâneos
2. **Distribuição**
   - Scrapers em diferentes servidores
3. **Machine Learning**
   - Detecção automática de mudanças nos sites

## 📚 **REFERÊNCIAS**

### 🔗 **Documentação Oficial**
- [Playwright Python](https://playwright.dev/python/)
- [Playwright API Reference](https://playwright.dev/python/docs/api/class-playwright)

### 📖 **Tutoriais e Exemplos**
- [Web Scraping com Playwright](https://playwright.dev/python/docs/web-scraping)
- [Anti-Detection Techniques](https://playwright.dev/python/docs/network)

## 🤝 **CONTRIBUIÇÃO**

### 📝 **Como Contribuir**
1. Fork do repositório
2. Criar branch para feature
3. Implementar funcionalidade
4. Adicionar testes
5. Fazer pull request

### 🐛 **Reportar Bugs**
- Usar issues do GitHub
- Incluir logs de erro
- Descrever passos para reproduzir

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

---

## 🎉 **CONCLUSÃO**

O sistema de scrapers com Playwright oferece uma solução robusta, escalável e profissional para coleta de dados esportivos. Com funcionalidades avançadas de anti-detecção, monitoramento automático e arquitetura modular, está pronto para uso em produção.

**🚀 Playwright é o futuro do web scraping! 🎭**
