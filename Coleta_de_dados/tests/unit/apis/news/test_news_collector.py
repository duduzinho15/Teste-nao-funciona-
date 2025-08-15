"""
Testes para o módulo de coleta de notícias.

Este módulo contém testes unitários e de integração para o NewsCollector.
"""
import pytest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
import json
import os

# Importações locais
from Coleta_de_dados.apis.news.collector import NewsCollector
from Coleta_de_dados.database.models import Clube, NoticiaClube

# Caminho para os dados de teste
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def load_test_data(filename):
    """Carrega dados de teste de um arquivo JSON."""
    filepath = os.path.join(TEST_DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Fixture para o mock do banco de dados
@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session

# Fixture para o NewsCollector
@pytest.fixture
def news_collector(mock_db_session):
    return NewsCollector(db_session=mock_db_session)

# Fixture para um clube de teste
@pytest.fixture
def sample_clube():
    return Clube(
        id=1,
        nome="Flamengo",
        abreviacao="FLA",
        cidade="Rio de Janeiro",
        fundacao=date(1895, 11, 15)
    )

# Fixture para HTML de exemplo do Globo Esporte
@pytest.fixture
def sample_ge_html():
    return """
    <html>
        <body>
            <li class="widget--info">
                <a class="feed-post-link" href="https://ge.globo.com/noticia-exemplo-1">
                    <div class="bstn-hl-title">Flamengo anuncia novo reforço para a temporada</div>
                </a>
                <div class="feed-post-body-resumo">Clube contrata jogador para reforçar o elenco.</div>
                <span class="feed-post-datetime">há 2 horas</span>
                <span class="feed-post-metadata-section">Por João Silva</span>
                <img class="bstn-dyu-picture" src="http://example.com/noticia1.jpg">
            </li>
            <li class="widget--info">
                <a class="feed-post-link" href="https://ge.globo.com/noticia-exemplo-2">
                    <div class="bstn-hl-title">Técnico do Flamengo fala sobre próximos jogos</div>
                </a>
                <div class="feed-post-body-resumo">Treinador comenta preparação para a sequência do campeonato.</div>
                <span class="feed-post-datetime">há 1 dia</span>
                <span class="feed-post-metadata-section">Por Maria Oliveira</span>
                <img class="bstn-dyu-picture" src="http://example.com/noticia2.jpg">
            </li>
        </body>
    </html>
    """

# Testes unitários
class TestNewsCollectorUnit:
    """Testes unitários para a classe NewsCollector."""
    
    def test_parse_data_publicacao_horas(self, news_collector):
        """Testa o parser de data para horas."""
        agora = datetime.now()
        data = news_collector._parse_data_publicacao("há 3 horas")
        assert isinstance(data, datetime)
        # Verifica se a diferença está dentro de uma margem aceitável (3 horas +- 1 minuto)
        diff_segundos = abs((agora - data).total_seconds() - 3 * 3600)
        assert diff_segundos <= 60  # Aceita até 1 minuto de diferença
    
    def test_parse_data_publicacao_dias(self, news_collector):
        """Testa o parser de data para dias."""
        agora = datetime.now()
        data = news_collector._parse_data_publicacao("há 2 dias")
        assert isinstance(data, datetime)
        # Verifica se a diferença está dentro de uma margem aceitável (2 dias +- 1 hora)
        diff_segundos = abs((agora - data).total_seconds() - 2 * 24 * 3600)
        assert diff_segundos <= 3600  # Aceita até 1 hora de diferença
    
    def test_parse_data_publicacao_minutos(self, news_collector):
        """Testa o parser de data para minutos."""
        agora = datetime.now()
        data = news_collector._parse_data_publicacao("há 15 minutos")
        assert isinstance(data, datetime)
        # Verifica se a diferença está dentro de uma margem aceitável (15 minutos +- 10 segundos)
        diff_segundos = abs((agora - data).total_seconds() - 15 * 60)
        assert diff_segundos <= 10  # Aceita até 10 segundos de diferença
    
    def test_parse_data_publicacao_invalida(self, news_collector):
        """Testa o parser de data com formato inválido."""
        agora = datetime.now()
        data = news_collector._parse_data_publicacao("data inválida")
        # Deve retornar a data atual
        assert isinstance(data, datetime)
        assert (agora - data).total_seconds() < 1  # Menos de 1 segundo de diferença
    
    def test_parse_noticia_element(self, news_collector, sample_ge_html):
        """Testa o parser de elemento de notícia."""
        soup = BeautifulSoup(sample_ge_html, 'html.parser')
        elemento = soup.find('li', class_='widget--info')
        
        noticia = news_collector._parse_noticia_element(elemento)
        
        assert noticia is not None
        assert noticia['titulo'] == "Flamengo anuncia novo reforço para a temporada"
        assert noticia['url_noticia'] == "https://ge.globo.com/noticia-exemplo-1"
        assert noticia['fonte'] == "Globo Esporte"
        assert noticia['resumo'] == "Clube contrata jogador para reforçar o elenco."
        assert noticia['autor'] == "Por João Silva"  # O código adiciona 'Por ' antes do nome do autor
        assert noticia['imagem_destaque'] == "http://example.com/noticia1.jpg"
        assert isinstance(noticia['data_publicacao'], datetime)
    
    def test_parse_noticia_element_sem_campos_opcionais(self, news_collector):
        """Testa o parser com elementos opcionais ausentes."""
        html = """
        <li class="widget--info">
            <a class="feed-post-link" href="https://ge.globo.com/noticia-exemplo">
                <div class="bstn-hl-title">Título da notícia</div>
            </a>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        elemento = soup.find('li', class_='widget--info')
        
        noticia = news_collector._parse_noticia_element(elemento)
        
        assert noticia is not None
        assert noticia['titulo'] == "Título da notícia"
        assert noticia['url_noticia'] == "https://ge.globo.com/noticia-exemplo"
        assert noticia['fonte'] == "Globo Esporte"
        assert noticia['resumo'] == ""  # Campo opcional vazio
        assert noticia['autor'] == "Redação GE"  # Valor padrão quando não há autor
        assert noticia['imagem_destaque'] == ""  # Campo opcional vazio
        assert isinstance(noticia['data_publicacao'], datetime)

# Testes de integração
class TestNewsCollectorIntegration:
    """Testes de integração para a classe NewsCollector."""
    
    @patch('requests.get')
    def test_coletar_noticias_globo_esporte(self, mock_get, news_collector, sample_clube, sample_ge_html):
        """Testa a coleta de notícias do Globo Esporte."""
        # Configura o mock para retornar o HTML de exemplo
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_ge_html
        mock_get.return_value = mock_response
        
        # Executa o método de coleta
        noticias = news_collector._coletar_noticias_globo_esporte(sample_clube, limite=2)
        
        # Verifica os resultados
        assert len(noticias) == 2
        assert noticias[0]['titulo'] == "Flamengo anuncia novo reforço para a temporada"
        assert noticias[1]['titulo'] == "Técnico do Flamengo fala sobre próximos jogos"
        
        # Verifica se a URL de busca foi chamada corretamente
        expected_url = "https://ge.globo.com/busca/?q=Flamengo&order=recent&species=notícias"
        mock_get.assert_called_once_with(
            expected_url,
            headers=news_collector.HEADERS,
            timeout=10
        )
    
    @patch('requests.get')
    def test_obter_conteudo_completo(self, mock_get, news_collector):
        """Testa a obtenção do conteúdo completo de uma notícia."""
        # HTML de exemplo com conteúdo completo
        conteudo_html = """
        <html>
            <body>
                <article>
                    <p class="content-text__container">Primeiro parágrafo.</p>
                    <p class="content-text__container">Segundo parágrafo.</p>
                    <p class="content-text__container">Terceiro parágrafo.</p>
                </article>
            </body>
        </html>
        """
        
        # Configura o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = conteudo_html
        mock_get.return_value = mock_response
        
        # Executa o método
        url = "https://ge.globo.com/noticia-exemplo"
        conteudo = news_collector._obter_conteudo_completo(url)
        
        # Verifica o resultado
        assert "Primeiro parágrafo." in conteudo
        assert "Segundo parágrafo." in conteudo
        assert "Terceiro parágrafo." in conteudo
        
        # Verifica se a URL foi chamada corretamente
        mock_get.assert_called_once_with(
            url,
            headers=news_collector.HEADERS,
            timeout=10
        )
    
    @patch('Coleta_de_dados.apis.news.collector.NewsCollector._coletar_noticias_globo_esporte')
    @patch('Coleta_de_dados.apis.news.collector.NewsCollector._obter_conteudo_completo')
    def test_coletar_noticias_reais(self, mock_obter_conteudo, mock_coletar_ge, news_collector, sample_clube):
        """Testa o fluxo completo de coleta de notícias reais."""
        # Configura os mocks
        noticias_ge = [
            {
                'titulo': 'Flamengo anuncia reforço',
                'url_noticia': 'https://ge.globo.com/noticia1',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now(),
                'resumo': 'Clube contrata jogador',
                'autor': 'Repórter 1',
                'imagem_destaque': 'http://example.com/img1.jpg'
            },
            {
                'titulo': 'Técnico do Flamengo fala',
                'url_noticia': 'https://ge.globo.com/noticia2',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now() - timedelta(days=1),
                'resumo': 'Treinador comenta jogos',
                'autor': 'Repórter 2',
                'imagem_destaque': 'http://example.com/img2.jpg'
            }
        ]
        
        conteudo_completo = "Conteúdo completo da notícia com vários detalhes importantes."
        
        mock_coletar_ge.return_value = noticias_ge
        mock_obter_conteudo.return_value = conteudo_completo
        
        # Executa o método
        noticias = news_collector._coletar_noticias_reais(sample_clube, limite=2)
        
        # Verifica os resultados
        assert len(noticias) == 2
        assert noticias[0]['titulo'] == 'Flamengo anuncia reforço'
        assert noticias[1]['titulo'] == 'Técnico do Flamengo fala'
        assert noticias[0]['conteudo_completo'] == conteudo_completo
        assert noticias[1]['conteudo_completo'] == conteudo_completo
        
        # Verifica se os métodos foram chamados corretamente
        mock_coletar_ge.assert_called_once_with(sample_clube, 2)
        assert mock_obter_conteudo.call_count == 2  # Deve ser chamado para cada notícia

# Teste de integração com o banco de dados
class TestNewsCollectorDatabaseIntegration:
    """Testes de integração com o banco de dados."""
    
    def test_salvar_noticias(self, news_collector, mock_db_session):
        """Testa o salvamento de notícias no banco de dados."""
        # Configura o mock para simular que não existem notícias duplicadas
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Dados de exemplo
        clube_id = 1
        noticias = [
            {
                'titulo': 'Flamengo anuncia reforço',
                'url_noticia': 'https://ge.globo.com/noticia1',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now(),
                'resumo': 'Clube contrata jogador',
                'conteudo_completo': 'Conteúdo completo',
                'autor': 'Repórter 1',
                'imagem_destaque': 'http://example.com/img1.jpg'
            },
            {
                'titulo': 'Técnico do Flamengo fala',
                'url_noticia': 'https://ge.globo.com/noticia2',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now() - timedelta(days=1),
                'resumo': 'Treinador comenta jogos',
                'conteudo_completo': 'Conteúdo completo 2',
                'autor': 'Repórter 2',
                'imagem_destaque': 'http://example.com/img2.jpg'
            }
        ]
        
        # Executa o método
        qtd_salvas = news_collector._salvar_noticias(clube_id, noticias)
        
        # Verifica os resultados
        assert qtd_salvas == 2
        assert mock_db_session.add.call_count == 2
        mock_db_session.commit.assert_called_once()
        
        # Verifica se os parâmetros estão corretos
        args, _ = mock_db_session.add.call_args_list[0]
        noticia_salva = args[0]
        
        assert isinstance(noticia_salva, NoticiaClube)
        assert noticia_salva.clube_id == clube_id
        assert noticia_salva.titulo == 'Flamengo anuncia reforço'
        assert noticia_salva.url_noticia == 'https://ge.globo.com/noticia1'
    
    def test_salvar_noticias_com_duplicadas(self, news_collector, mock_db_session):
        """Testa o salvamento de notícias com URLs duplicadas."""
        # Configura o mock para simular que a segunda notícia já existe
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            None,  # Primeira notícia não existe
            MagicMock()  # Segunda notícia já existe
        ]
        
        # Dados de exemplo
        clube_id = 1
        noticias = [
            {
                'titulo': 'Notícia Nova',
                'url_noticia': 'https://ge.globo.com/nova',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now(),
                'resumo': 'Resumo',
                'conteudo_completo': 'Conteúdo',
                'autor': 'Repórter',
                'imagem_destaque': 'http://example.com/img.jpg'
            },
            {
                'titulo': 'Notícia Existente',
                'url_noticia': 'https://ge.globo.com/existente',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now(),
                'resumo': 'Já existe',
                'conteudo_completo': 'Conteúdo existente',
                'autor': 'Repórter',
                'imagem_destaque': 'http://example.com/existente.jpg'
            }
        ]
        
        # Executa o método
        qtd_salvas = news_collector._salvar_noticias(clube_id, noticias)
        
        # Verifica os resultados - apenas uma notícia deve ser salva
        assert qtd_salvas == 1
        mock_db_session.add.assert_called_once()  # Apenas uma chamada para adicionar
        mock_db_session.commit.assert_called_once()

# Teste de fluxo completo
class TestNewsCollectorFullFlow:
    """Testes de fluxo completo do NewsCollector."""
    
    @patch('Coleta_de_dados.apis.news.collector.NewsCollector._coletar_noticias_reais')
    @patch('Coleta_de_dados.apis.news.collector.NewsCollector._salvar_noticias')
    def test_coletar_noticias_clube(self, mock_salvar, mock_coletar, news_collector, mock_db_session, sample_clube):
        """Testa o fluxo completo de coleta de notícias para um clube."""
        # Configura o mock do banco para retornar o clube
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_clube
        
        # Configura o mock de coleta
        noticias_coletadas = [
            {
                'titulo': 'Flamengo anuncia reforço',
                'url_noticia': 'https://ge.globo.com/noticia1',
                'fonte': 'Globo Esporte',
                'data_publicacao': datetime.now(),
                'resumo': 'Clube contrata jogador',
                'conteudo_completo': 'Conteúdo completo',
                'autor': 'Repórter 1',
                'imagem_destaque': 'http://example.com/img1.jpg'
            }
        ]
        mock_coletar.return_value = noticias_coletadas
        
        # Configura o mock de salvamento
        mock_salvar.return_value = 1
        
        # Executa o método principal
        resultado = news_collector.coletar_noticias_clube(clube_id=1, limite=5)
        
        # Verifica os resultados
        assert resultado['status'] == 'sucesso'
        assert resultado['clube_id'] == 1
        assert resultado['clube_nome'] == 'Flamengo'
        assert resultado['noticias_coletadas'] == 1
        
        # Verifica se os métodos foram chamados corretamente
        mock_coletar.assert_called_once_with(sample_clube, 5)
        mock_salvar.assert_called_once_with(1, noticias_coletadas)
    
    def test_coletar_noticias_clube_nao_encontrado(self, news_collector, mock_db_session):
        """Testa o tratamento de erro quando o clube não é encontrado."""
        # Configura o mock para retornar None (clube não encontrado)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Executa o método e verifica o erro
        resultado = news_collector.coletar_noticias_clube(clube_id=999, limite=5)
        
        assert resultado['status'] == 'erro'
        assert 'não encontrado' in resultado['mensagem'].lower()
        assert resultado['noticias_coletadas'] == 0
        
        # Verifica se o commit não foi chamado (já que não houve alterações)
        mock_db_session.commit.assert_not_called()
