"""
Testes para o módulo de coleta de redes sociais.

Este módulo contém testes unitários e de integração para o SocialMediaCollector.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Importações locais
from Coleta_de_dados.apis.social.collector import SocialMediaCollector
from Coleta_de_dados.database.models import Clube
from Coleta_de_dados.database.config import SessionLocal, Base, engine

# Configuração do pytest
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_session():
    """Cria uma sessão de banco de dados em memória para testes."""
    # Cria todas as tabelas no banco de dados de teste
    Base.metadata.create_all(engine)
    
    db = SessionLocal()
    
    # Adiciona um clube de teste
    clube = Clube(
        id=1,
        nome="Flamengo",
        nome_completo="Clube de Regatas do Flamengo",
        ativo=True
    )
    db.add(clube)
    db.commit()
    
    yield db
    
    # Limpa o banco de dados após os testes
    db.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def mock_requests():
    """Cria um mock para o módulo requests."""
    with patch('Coleta_de_dados.apis.social.collector.requests') as mock:
        yield mock

@pytest.fixture
def mock_soup():
    """Cria um mock para o BeautifulSoup."""
    with patch('Coleta_de_dados.apis.social.collector.BeautifulSoup') as mock:
        yield mock

def test_social_media_collector_init():
    """Testa a inicialização do SocialMediaCollector."""
    collector = SocialMediaCollector()
    assert collector is not None
    assert hasattr(collector, 'db')
    assert hasattr(collector, 'logger')
    assert hasattr(collector, 'session')

def test_coletar_posts_recentes_clube_nao_encontrado(db_session, caplog):
    """Testa o comportamento quando o clube não é encontrado."""
    collector = SocialMediaCollector(db_session)
    resultado = collector.coletar_posts_recentes(999)  # ID que não existe
    
    assert resultado == 0
    assert "Clube com ID 999 não encontrado" in caplog.text

def test_coletar_posts_recentes_sucesso(db_session, mock_requests, caplog):
    """Testa a coleta de posts com sucesso."""
    # Configura o mock da requisição
    mock_response = Mock()
    mock_response.status_code = 200
    
    # HTML de exemplo que será retornado pelo mock
    html_content = """
    <html>
        <body>
            <article data-testid="tweet" data-tweet-id="12345">
                <div data-testid="tweetText">Teste de post do Flamengo! 🔴⚫ #Fla</div>
                <time datetime="2023-08-07T15:30:00.000Z">3:30 PM · 7 de ago. de 2023</time>
                <div role="group">
                    <span data-testid="reply">
                        <span>245</span>
                    </span>
                    <span data-testid="retweet">
                        <span>1,2K</span>
                    </span>
                    <span data-testid="like">
                        <span>5,3K</span>
                    </span>
                    <span data-testid="view">
                        <span>10,5K</span>
                    </span>
                </div>
                <img src="https://pbs.twimg.com/media/ABC123.jpg" />
            </article>
        </body>
    </html>
    """
    mock_response.text = html_content
    
    # Configura o mock da sessão de requests
    mock_session = Mock()
    mock_session.get.return_value = mock_response
    mock_requests.Session.return_value = mock_session
    
    # Cria o coletor e executa o teste
    collector = SocialMediaCollector(db_session)
    
    # Mock do time.sleep para evitar atrasos nos testes
    with patch('time.sleep'):
        # Executa o teste
        resultado = collector.coletar_posts_recentes(1)  # ID do Flamengo
    
    # Verifica o resultado
    assert resultado == 1
    assert "1 posts salvos para Flamengo" in caplog.text
    
    # Verifica se o post foi salvo no banco de dados
    from sqlalchemy import text
    cursor = db_session.execute(text("SELECT * FROM posts_redes_sociais WHERE clube_id = :clube_id"), {"clube_id": 1})
    posts = cursor.fetchall()
    assert len(posts) == 1, f"Nenhum post encontrado no banco de dados. Esperado 1, encontrado {len(posts)}"
    
    post = posts[0]
    assert post[3] == "Teste de post do Flamengo! 🔴⚫ #Fla"  # conteúdo
    assert post[6] == 1200  # curtidas (1.2K)
    assert post[7] == 245   # comentários
    assert post[8] == 5300  # compartilhamentos (5.3K)

def test_extrair_metricas_tweet():
    """Testa a extração de métricas de um tweet."""
    # Cria um mock do BeautifulSoup
    soup_mock = MagicMock()
    
    # Configura os elementos de métricas
    group_mock = MagicMock()
    
    # Cria spans simulados para as métricas
    reply_span = MagicMock()
    reply_span.get.return_value = 'reply'
    reply_span.get_text.return_value = '245'
    
    retweet_span = MagicMock()
    retweet_span.get.return_value = 'retweet'
    retweet_span.get_text.return_value = '1.2K'
    
    like_span = MagicMock()
    like_span.get.return_value = 'like'
    like_span.get_text.return_value = '5.3K'
    
    view_span = MagicMock()
    view_span.get.return_value = 'view'
    view_span.get_text.return_value = '10.5K'
    
    # Configura o mock para retornar os spans corretos
    group_mock.find_all.return_value = [reply_span, retweet_span, like_span, view_span]
    soup_mock.find_all.return_value = [group_mock]
    
    # Cria o coletor e executa o teste
    collector = SocialMediaCollector()
    metrics = collector._extrair_metricas_tweet(soup_mock)
    
    # Verifica as métricas extraídas
    assert metrics['replies'] == 245
    assert metrics['retweets'] == 1200
    assert metrics['likes'] == 5300
    assert metrics['views'] == 10500

def test_extrair_url_midia():
    """Testa a extração de URL de mídia de um tweet."""
    # Cria um mock do BeautifulSoup
    soup_mock = MagicMock()
    
    # Configura o mock para retornar uma imagem
    img_mock = MagicMock()
    img_mock.get.return_value = "https://pbs.twimg.com/media/ABC123.jpg?format=jpg&name=medium"
    soup_mock.find.return_value = img_mock
    
    # Cria o coletor e executa o teste
    collector = SocialMediaCollector()
    url = collector._extrair_url_midia(soup_mock)
    
    # Verifica se a URL foi extraída corretamente
    assert url == "https://pbs.twimg.com/media/ABC123.jpg"

def test_salvar_post_duplicado(db_session):
    """Testa o comportamento ao tentar salvar um post duplicado."""
    # Insere um post de teste
    db_session.execute(
        """
        INSERT INTO posts_redes_sociais 
        (clube_id, rede_social, post_id, conteudo, data_postagem, 
         curtidas, comentarios, compartilhamentos, url_post)
        VALUES 
        (1, 'Twitter', '12345', 'Post de teste', '2023-08-07 15:30:00',
         100, 10, 50, 'https://twitter.com/user/status/12345')
        """
    )
    db_session.commit()
    
    # Cria o coletor e tenta salvar o mesmo post novamente
    collector = SocialMediaCollector(db_session)
    resultado = collector._salvar_post(
        1,  # clube_id
        {
            'post_id': '12345',
            'conteudo': 'Post de teste atualizado',
            'data_postagem': datetime.now(),
            'curtidas': 200,
            'comentarios': 20,
            'compartilhamentos': 100,
            'url_post': 'https://twitter.com/user/status/12345',
            'midia_url': None
        }
    )
    
    # Verifica que o post não foi salvo novamente (é duplicado)
    assert resultado is False
    
    # Verifica se o post original não foi alterado
    from sqlalchemy import text
    cursor = db_session.execute(
        text("SELECT conteudo, curtidas FROM posts_redes_sociais WHERE post_id = :post_id"),
        {"post_id": '12345'}
    )
    post = cursor.fetchone()
    assert post is not None, "Nenhum post encontrado com o ID especificado"
    assert post[0] == 'Post de teste', f"Conteúdo inesperado: {post[0]}"  # Conteúdo não foi atualizado
    assert post[1] == 100, f"Número de curtidas inesperado: {post[1]}"  # Curtidas não foram atualizadas

def test_coletar_dados_para_todos_clubes(db_session, monkeypatch):
    """Testa a função de conveniência para coletar dados de todos os clubes."""
    # Adiciona um segundo clube para teste
    clube2 = Clube(
        id=2,
        nome="Vasco",
        nome_completo="Club de Regatas Vasco da Gama",
        ativo=True
    )
    db_session.add(clube2)
    db_session.commit()
    
    # Mock da função coletar_posts_recentes para retornar 2 posts para cada clube
    def mock_coletar_posts_recentes(self, clube_id, limite=5):
        return 2  # Retorna 2 posts para cada clube
    
    # Aplica o mock
    monkeypatch.setattr(
        'Coleta_de_dados.apis.social.collector.SocialMediaCollector.coletar_posts_recentes',
        mock_coletar_posts_recentes
    )
    
    # Importa a função diretamente para evitar problemas com o monkeypatch
    from Coleta_de_dados.apis.social.collector import coletar_dados_para_todos_clubes
    
    # Executa a função de teste
    resultado = coletar_dados_para_todos_clubes(limite_por_clube=5)
    
    # Verifica o resultado
    assert resultado['status'] == 'sucesso'
    assert resultado['clubes_processados'] == 2  # Flamengo e Vasco
    assert resultado['total_posts'] == 4  # 2 posts por clube
    assert "Coleta concluída para 2 clubes" in resultado['mensagem']
