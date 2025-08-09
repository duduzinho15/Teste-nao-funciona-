"""
Testes de Integração para Análise de Sentimento

Este módulo contém testes de integração para os endpoints de análise de sentimento da API.
Os testes verificam o funcionamento correto da análise de sentimento em diferentes cenários.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime, timedelta

# Importa a aplicação FastAPI
from api.main import create_app
from api.database import get_db
from Coleta_de_dados.database.models import NoticiaClube, Clube, Base
from Coleta_de_dados.database import db_manager

# Configuração do cliente de teste
app = create_app()
client = TestClient(app)

# Dados de teste
TEST_API_KEY = os.getenv("API_KEY", "test-api-key")
TEST_HEADERS = {
    "X-API-Key": TEST_API_KEY,
    "Content-Type": "application/json"
}

# Dados de exemplo para teste
TEST_NEWS_DATA = {
    "titulo": "Time vence partida emocionante por 3x2 no último minuto",
    "conteudo_completo": """
    Em uma partida emocionante, o time demonstrou grande espírito de equipe e garra para virar o placar 
    nos minutos finais. O técnico foi muito elogiado por suas substituições precisas que mudaram o rumo do jogo. 
    Os torcedores saíram satisfeitos com a atuação da equipe, que mostrou evolução tática e emocional.
    """,
    "data_publicacao": "2025-08-10T15:30:00",
    "fonte": "Teste Automatizado",
    "url": "http://exemplo.com/noticia/123",
    "url_imagem": "http://exemplo.com/imagens/noticia123.jpg",
    "autor": "Sistema de Teste",
    "resumo": "Time vira no final e emociona torcida em jogo histórico",
    "clube_id": 1,
    "categoria": "futebol",
    "tags": "futebol,campeonato,vitória,time"
}

# Fixture para o banco de dados de teste
@pytest.fixture(scope="module")
def test_db():
    """Configura um banco de dados de teste em memória."""
    # Configuração do banco de dados em memória para testes
    db_manager.engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(bind=db_manager.engine)
    
    # Cria uma sessão de teste
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
    
    # Cria dados iniciais
    db = TestingSessionLocal()
    
    # Adiciona um clube de teste
    test_club = Clube(
        id=1,
        nome="Clube de Teste",
        nome_comum="Teste FC",
        sigla="TST",
        pais="Brasil",
        tipo="Clube",
        fundacao=1950,
        estadio="Estádio de Teste",
        capacidade=50000,
        cidade="Cidade de Teste",
        uf="TS",
        escudo_url="http://exemplo.com/escudo.png",
        site="http://testefc.com.br",
        twitter="@testefc",
        facebook="testefc",
        instagram="testefc",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(test_club)
    db.commit()
    
    # Adiciona algumas notícias de teste
    test_news = [
        NoticiaClube(
            titulo="Time vence partida emocionante",
            conteudo_completo="O time jogou muito bem e garantiu uma vitória importante no campeonato.",
            data_publicacao=datetime.utcnow() - timedelta(days=1),
            fonte="Teste Automatizado",
            url=f"http://exemplo.com/noticia/{i+1}",
            clube_id=1,
            sentimento_geral=0.8 if i % 2 == 0 else -0.3,
            polaridade="positivo" if i % 2 == 0 else "negativo",
            confianca_sentimento=0.9,
            modelo_analise="test_model_v1",
            analisado_em=datetime.utcnow() - timedelta(hours=i)
        )
        for i in range(5)
    ]
    
    db.add_all(test_news)
    db.commit()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=db_manager.engine)

# Fixture para o cliente de teste com banco de dados configurado
@pytest.fixture(scope="module")
def test_client(test_db):
    """Cria um cliente de teste com banco de dados configurado."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()

def test_analisar_texto_sentimento(test_client):
    """Testa a análise de sentimento de um texto."""
    # Dados de teste
    test_text = {
        "texto": "O time jogou muito bem e garantiu uma vitória importante no campeonato.",
        "titulo": "Vitória importante no campeonato"
    }
    
    # Faz a requisição para o endpoint
    response = test_client.post(
        "/api/v1/analise/sentimento",
        json=test_text,
        headers=TEST_HEADERS
    )
    
    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    
    # Verifica se os campos esperados estão presentes
    assert "sentimento_geral" in data
    assert "confianca" in data
    assert "polaridade" in data
    assert "palavras_chave" in data
    assert "topicos" in data
    assert "modelo" in data
    
    # Verifica se a pontuação de sentimento está dentro do intervalo esperado
    assert -1.0 <= data["sentimento_geral"] <= 1.0
    assert 0.0 <= data["confianca"] <= 1.0
    assert data["polaridade"] in ["positivo", "negativo", "neutro"]

def test_analisar_noticia_por_id(test_client, test_db):
    """Testa a análise de sentimento de uma notícia por ID."""
    # Primeiro, cria uma notícia de teste
    nova_noticia = NoticiaClube(
        titulo="Time empata em jogo difícil",
        conteudo_completo="O time não conseguiu vencer e ficou no empate em jogo difícil fora de casa.",
        data_publicacao=datetime.utcnow(),
        fonte="Teste Automatizado",
        url="http://exemplo.com/noticia/teste-empate",
        clube_id=1
    )
    
    test_db.add(nova_noticia)
    test_db.commit()
    test_db.refresh(nova_noticia)
    
    # Agora, testa a análise de sentimento
    response = test_client.post(
        f"/api/v1/analise/noticias/{nova_noticia.id}",
        headers=TEST_HEADERS
    )
    
    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    
    # Verifica se os campos de sentimento foram preenchidos
    assert data["sentimento_geral"] is not None
    assert data["confianca_sentimento"] is not None
    assert data["polaridade"] is not None
    assert data["modelo_analise"] is not None
    assert data["analisado_em"] is not None

def test_analisar_lote_noticias(test_client, test_db):
    """Testa a análise de sentimento em lote de notícias."""
    # Dados de teste para análise em lote
    lote_noticias = {
        "noticias": [
            {
                "id": 1,  # ID de notícia existente
                "titulo": "Time vence jogo importante",
                "conteudo_completo": "O time mostrou grande atuação e venceu por 2x0 em casa."
            },
            {
                "id": 2,  # Novo ID
                "titulo": "Derrota fora de casa",
                "conteudo_completo": "O time perdeu por 3x1 em jogo fora de casa."
            }
        ]
    }
    
    # Faz a requisição para o endpoint de análise em lote
    response = test_client.post(
        "/api/v1/analise/noticias/lote",
        json=lote_noticias,
        headers=TEST_HEADERS
    )
    
    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    
    # Verifica se retornou resultados para as notícias
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Verifica se cada resultado contém os campos esperados
    for resultado in data:
        assert "noticia_id" in resultado
        assert "sentimento_geral" in resultado
        assert "confianca" in resultado
        assert "polaridade" in resultado
        assert "topicos" in resultado
        assert "palavras_chave" in resultado
        assert "modelo" in resultado

def test_obter_estatisticas_analise(test_client):
    """Testa a obtenção de estatísticas de análise de sentimento."""
    # Faz a requisição para o endpoint de estatísticas
    response = test_client.get(
        "/api/v1/analise/estatisticas?dias=30",
        headers=TEST_HEADERS
    )
    
    # Verifica a resposta
    assert response.status_code == 200
    data = response.json()
    
    # Verifica se os campos esperados estão presentes
    assert "total_noticias" in data
    assert "total_analisadas" in data
    assert "porcentagem_analisada" in data
    assert "media_sentimento" in data
    assert "confianca_media" in data
    assert "distribuicao_polaridades" in data
    assert "ultimas_analises" in data
    
    # Verifica se a porcentagem de análise está entre 0 e 100
    assert 0 <= data["porcentagem_analisada"] <= 100
    
    # Verifica se a média de sentimento está entre -1 e 1
    assert -1.0 <= data["media_sentimento"] <= 1.0
    
    # Verifica se a confiança média está entre 0 e 1
    assert 0.0 <= data["confianca_media"] <= 1.0

def test_analisar_noticia_inexistente(test_client):
    """Testa a tentativa de analisar uma notícia que não existe."""
    # Tenta analisar uma notícia com ID inexistente
    response = test_client.post(
        "/api/v1/analise/noticias/999999",
        headers=TEST_HEADERS
    )
    
    # Verifica se retornou erro 404
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "não encontrada" in data["detail"].lower()

def test_analisar_lote_sem_noticias(test_client):
    """Testa a tentativa de analisar um lote vazio de notícias."""
    # Tenta analisar um lote vazio
    response = test_client.post(
        "/api/v1/analise/noticias/lote",
        json={"noticias": []},
        headers=TEST_HEADERS
    )
    
    # Verifica se retornou erro 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "nenhuma notícia" in data["detail"].lower()
