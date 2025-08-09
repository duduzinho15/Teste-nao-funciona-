# 🚀 ApostaPro: Plataforma de Análise Esportiva com IA

![Status do Projeto](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Linguagem](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

O ApostaPro é uma plataforma completa de engenharia de dados e machine learning projetada para coletar, processar e analisar uma vasta gama de informações esportivas. O objetivo final é construir um modelo de IA preditivo que forneça recomendações de apostas baseadas em análises estatísticas profundas e dados qualitativos.

## 🎯 Conceito Central

O projeto funciona como um pipeline de dados automatizado que se conecta a múltiplas fontes para construir um data lakehouse robusto. A arquitetura segue o fluxo:

**Coleta de Dados Multifonte ➔ Armazenamento e Processamento ➔ Modelo de IA ➔ API Backend ➔ Interface do Usuário**



<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/31cbae6b-ca8e-4112-8a92-069df5298b79" />



## 📊 Principais Funcionalidades

* **Coleta de Dados Multifonte:** Extração de dados de diversas fontes, incluindo:
    * **Sites de Estatísticas:** FBref, SofaScore e outros.
    * **Redes Sociais e Notícias:** Twitter/X, Reddit, portais de notícias para análise de sentimento e informações em tempo real.
* **Análise Estatística Profunda:** Coleta e processamento de métricas detalhadas de equipes e jogadores, como:
    * **Performance:** Resultados, gols, xG (Expected Goals), xA (Expected Assists).
    * **Dados Táticos:** Formações mais utilizadas, mudanças de escalação.
    * **Condições Externas:** Lesões, suspensões, moral da equipe e até condições climáticas.
* **Modelo Preditivo:** Um módulo de IA que utiliza os dados coletados para prever resultados de partidas e identificar oportunidades de aposta.
* **API e Interface:** Um backend em Flask serve os dados e as previsões para uma interface de usuário, permitindo a consulta e visualização das análises.

## 🛠️ Tecnologias Utilizadas

* **Linguagem Principal:** Python
* **Coleta de Dados:** Requests, BeautifulSoup, Selenium, Scrapy (planejado)
* **Banco de Dados:** SQLite (inicial), com planos de migração para uma solução mais robusta.
* **Análise de Dados:** Pandas, NumPy
* **Machine Learning:** Scikit-learn, TensorFlow/PyTorch (planejado)
* **Backend:** Flask
* **Agendamento de Tarefas:** `schedule` (ou cronjobs no servidor)

## 📂 Estrutura do Projeto

A estrutura de pastas foi organizada de forma modular para separar as responsabilidades de cada componente do sistema.

```
ApostaPro/
├── run.py                    # Ponto de entrada principal da aplicação (backend)
├── .gitignore
├── requirements.txt
│
├── Banco_de_dados/
│   ├── criar_banco.py        # Script para inicializar o schema do banco
│   └── verificar_dados.py    # Utilitários para inspecionar o banco
│
├── Coleta_de_dados/
│   ├── coletar_tudo.py       # Script mestre para orquestrar toda a coleta
│   ├── agendador.py          # Gerencia a execução periódica dos scrapers
│   ├── apis/                 # Módulos específicos para cada fonte de dados
│   │   ├── fbref_scraper.py
│   │   ├── sofascore_scraper.py
│   │   └── ...
│   └── logs/                 # Arquivos de log para coleta e erros
│
├── IA/
│   └── modelo_ia_apostapro.py  # Treinamento e uso do modelo de machine learning
│
├── interface/
│   └── interface.py          # Código para a interface gráfica (se aplicável)
│
├── backend/
│   └── backend_rest.py       # API Flask para servir os dados e previsões
│
└── legacy/
    └── ...                     # Scripts antigos, testes e experimentos
```

## 🚀 Como Começar

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/duduzinho15/ApostaPro.git](https://github.com/duduzinho15/ApostaPro.git)
    cd ApostaPro
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Crie o banco de dados:**
    ```bash
    python Banco_de_dados/criar_banco.py
    ```

5.  **Execute a aplicação:**
    ```bash
    python run.py
    ```

## 📝 Testes

O projeto inclui uma suíte abrangente de testes automatizados para garantir a qualidade e robustez do código. Aqui está como executar e entender os testes do módulo SocialMediaCollector.

### Testes do SocialMediaCollector

O módulo `SocialMediaCollector` é responsável por coletar posts de redes sociais (atualmente Twitter/X) de perfis públicos de clubes e atletas. Os testes estão localizados em:

```
Coleta_de_dados/apis/social/test_social_media_collector.py
```

#### Como Executar os Testes

Para executar todos os testes do SocialMediaCollector:

```bash
# Navegue até o diretório raiz do projeto
cd /caminho/para/ApostaPro

# Execute os testes com pytest
pytest Coleta_de_dados/apis/social/test_social_media_collector.py -v
```

Para executar testes específicos:

```bash
# Apenas testes unitários
pytest Coleta_de_dados/apis/social/test_social_media_collector.py::TestSocialMediaCollector -v

# Apenas testes de integração
pytest Coleta_de_dados/apis/social/test_social_media_collector.py::TestSocialMediaIntegration -v
```

#### Cobertura de Testes

Para verificar a cobertura de testes:

```bash
pytest --cov=Coleta_de_dados.apis.social Coleta_de_dados/apis/social/test_social_media_collector.py -v
```

#### O que é Testado

1. **Testes Unitários**
   - Parsing de HTML de posts do Twitter/X
   - Extração de dados como ID, conteúdo, data, curtidas e comentários
   - Verificação de duplicidade de posts
   - Formatação dos dados para o banco de dados

2. **Testes de Integração**
   - Fluxo completo de coleta de posts
   - Persistência no banco de dados
   - Exposição dos dados via API
   - Tratamento de erros e casos extremos

#### Mocking e Dados de Teste

Os testes utilizam mocks para simular requisições HTTP e respostas da API do Twitter/X, garantindo testes rápidos e confiáveis sem depender de conexões externas.

---

## 📈 Status Atual do Projeto

O projeto está em fase ativa de desenvolvimento. O foco atual está na **correção e robustecimento do módulo de coleta de dados do FBref**, que é a principal fonte de dados estatísticos no momento. As próximas etapas envolverão a implementação dos scrapers para outras fontes e o desenvolvimento inicial do modelo preditivo.

---
Feito com ❤️ por [duduzinho15](https://github.com/duduzinho15)
