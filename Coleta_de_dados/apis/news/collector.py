"""
Módulo para coleta de notícias sobre clubes de futebol.

Este módulo fornece funcionalidades para coletar e armazenar notícias
sobre os clubes de futebol de várias fontes na internet.
"""
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
import re
import time
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

# Importações locais
from Coleta_de_dados.database.models import Clube, NoticiaClube
from Coleta_de_dados.database.config import SessionLocal

# Configuração de headers para parecer um navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
}

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsCollector:
    """
    Coletor de notícias sobre clubes de futebol.
    
    Esta classe é responsável por coletar, processar e armazenar notícias
    sobre os clubes de futebol de várias fontes na internet.
    """
    
    # Configurações de busca
    BASE_URL = "https://ge.globo.com/busca/"
    SITE_URL = "https://ge.globo.com"
    
    # Headers para simular um navegador
    HEADERS = HEADERS
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Inicializa o coletor de notícias.
        
        Args:
            db_session: Sessão do banco de dados. Se não fornecida, uma nova será criada.
        """
        self.db = db_session if db_session else SessionLocal()
        self.logger = logging.getLogger(f"{__name__}.NewsCollector")
    
    def __del__(self):
        """Garante que a sessão seja fechada quando o coletor for destruído."""
        if hasattr(self, 'db') and self.db:
            self.db.close()
    
    def coletar_noticias_clube(self, clube_id: int, limite: int = 10) -> Dict:
        """
        Coleta notícias recentes sobre um clube específico.
        
        Args:
            clube_id: ID do clube para o qual coletar notícias
            limite: Número máximo de notícias a coletar
            
        Returns:
            Dict: Estatísticas da coleta
        """
        try:
            self.logger.info(f"Iniciando coleta de notícias para o clube ID: {clube_id}")
            
            # Verifica se o clube existe
            clube = self.db.query(Clube).filter(Clube.id == clube_id).first()
            if not clube:
                self.logger.error(f"Clube com ID {clube_id} não encontrado.")
                return {
                    'status': 'erro',
                    'mensagem': f'Clube com ID {clube_id} não encontrado',
                    'clube_id': clube_id,
                    'noticias_coletadas': 0
                }
            
            # Coleta notícias reais
            noticias_coletadas = self._coletar_noticias_reais(clube, limite)
            
            # Salva as notícias no banco de dados
            noticias_salvas = self._salvar_noticias(clube_id, noticias_coletadas)
            
            self.logger.info(f"Coleta concluída para o clube {clube.nome}. {noticias_salvas} notícias salvas.")
            
            return {
                'status': 'sucesso',
                'clube_id': clube_id,
                'clube_nome': clube.nome,
                'noticias_coletadas': noticias_salvas,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar notícias para o clube {clube_id}: {str(e)}", exc_info=True)
            return {
                'status': 'erro',
                'mensagem': str(e),
                'clube_id': clube_id,
                'noticias_coletadas': 0
            }
    
    def _parse_noticia_element(self, elemento: Any) -> Optional[Dict[str, Any]]:
        """
        Extrai os dados de uma notícia a partir de um elemento HTML.
        
        Args:
            elemento: Elemento BeautifulSoup contendo os dados da notícia
            
        Returns:
            Dicionário com os dados da notícia ou None se inválido
        """
        try:
            # Extrai o título e URL
            link = elemento.find('a', class_='feed-post-link')
            if not link:
                return None
                
            titulo = link.get_text(strip=True)
            url = link['href']
            
            # Extrai a data de publicação
            data_element = elemento.find('span', class_='feed-post-datetime')
            data_publicacao = self._parse_data_publicacao(
                data_element.get_text(strip=True) if data_element else ''
            )
            
            # Extrai o resumo
            resumo_element = elemento.find('div', class_='feed-post-body-resumo')
            resumo = resumo_element.get_text(strip=True) if resumo_element else ''
            
            # Extrai a imagem de destaque
            imagem_element = elemento.find('img', class_='bstn-dyu-picture')
            imagem_destaque = imagem_element['src'] if imagem_element and 'src' in imagem_element.attrs else ''
            
            # Extrai o autor (se disponível)
            autor_element = elemento.find('span', class_='feed-post-metadata-section')
            autor = autor_element.get_text(strip=True) if autor_element else 'Redação GE'
            
            return {
                'titulo': titulo,
                'url_noticia': url,
                'fonte': 'Globo Esporte',
                'data_publicacao': data_publicacao,
                'resumo': resumo,
                'imagem_destaque': imagem_destaque,
                'autor': autor
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar elemento de notícia: {str(e)}", exc_info=True)
            return None
    
    def _parse_data_publicacao(self, texto_data: str) -> datetime:
        """
        Converte o texto da data de publicação para um objeto datetime.
        
        Args:
            texto_data: Texto com a data (ex: 'há 2 horas', 'há 1 dia')
            
        Returns:
            Objeto datetime com a data de publicação
        """
        agora = datetime.now()
        
        if 'hora' in texto_data.lower():
            horas = int(re.search(r'\d+', texto_data).group())
            return agora - timedelta(hours=horas)
        elif 'dia' in texto_data.lower():
            dias = int(re.search(r'\d+', texto_data).group())
            return agora - timedelta(days=dias)
        elif 'minuto' in texto_data.lower():
            minutos = int(re.search(r'\d+', texto_data).group())
            return agora - timedelta(minutes=minutos)
            
        return agora
    
    def _coletar_noticias_globo_esporte(self, clube: Clube, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Coleta notícias reais do Globo Esporte para um clube específico.
        
        Args:
            clube: Objeto Clube para o qual coletar notícias
            limite: Número máximo de notícias a retornar
            
        Returns:
            Lista de dicionários contendo as notícias coletadas
        """
        noticias = []
        
        try:
            # Formata o termo de busca (nome do clube)
            termo_busca = quote_plus(clube.nome)
            url_busca = f"{self.BASE_URL}?q={termo_busca}&order=recent&species=notícias"
            
            self.logger.info(f"Buscando notícias para {clube.nome} em: {url_busca}")
            
            # Faz a requisição HTTP
            response = requests.get(url_busca, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            
            # Faz o parsing do HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Encontra os elementos das notícias
            noticias_elements = soup.find_all('li', class_='widget--info')
            
            # Processa cada notícia encontrada
            for element in noticias_elements[:limite]:
                noticia = self._parse_noticia_element(element)
                if noticia:
                    noticias.append(noticia)
            
            # Se não encontrou notícias suficientes, tenta buscar mais páginas
            if len(noticias) < limite:
                self.logger.info(f"Apenas {len(noticias)} notícias encontradas na primeira página. Buscando mais páginas...")
                # Implementar lógica de paginação se necessário
                
        except requests.RequestException as e:
            self.logger.error(f"Erro ao buscar notícias para {clube.nome}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar notícias para {clube.nome}: {str(e)}", exc_info=True)
        
        return noticias
    
    def _obter_conteudo_completo(self, url: str) -> str:
        """
        Obtém o conteúdo completo de uma notícia a partir da URL.
        
        Args:
            url: URL da notícia
            
        Returns:
            String com o conteúdo completo da notícia
        """
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Encontra o conteúdo principal da notícia
            conteudo_elements = soup.find_all('p', class_='content-text__container')
            
            # Junta todos os parágrafos em um único texto
            conteudo = '\n\n'.join([p.get_text(strip=True) for p in conteudo_elements])
            
            return conteudo
            
        except Exception as e:
            self.logger.error(f"Erro ao obter conteúdo da notícia {url}: {str(e)}")
            return ""
    
    def _coletar_noticias_reais(self, clube: Clube, limite: int) -> List[Dict[str, Any]]:
        """
        Coleta notícias reais para um clube de fontes online.
        
        Args:
            clube: Objeto Clube para o qual coletar notícias
            limite: Número máximo de notícias a retornar
            
        Returns:
            Lista de dicionários contendo as notícias coletadas
        """
        # Coleta notícias do Globo Esporte
        noticias = self._coletar_noticias_globo_esporte(clube, limite)
        
        # Para cada notícia, busca o conteúdo completo
        for noticia in noticias:
            if not noticia.get('conteudo_completo'):
                noticia['conteudo_completo'] = self._obter_conteudo_completo(noticia['url_noticia'])
                # Respeita o rate limit do site
                time.sleep(1)
        
        return noticias
    
    def _salvar_noticias(self, clube_id: int, noticias: List[Dict]) -> int:
        """
        Salva as notícias no banco de dados, evitando duplicatas.
        
        Args:
            clube_id: ID do clube dono das notícias
            noticias: Lista de dicionários contendo as notícias
            
        Returns:
            int: Número de notícias salvas
        """
        contador = 0
        
        for noticia in noticias:
            try:
                # Verifica se a notícia já existe pela URL
                existe = self.db.query(NoticiaClube).filter(
                    NoticiaClube.url_noticia == noticia['url_noticia']
                ).first()
                
                if not existe:
                    # Cria um novo registro de notícia
                    nova_noticia = NoticiaClube(
                        clube_id=clube_id,
                        titulo=noticia['titulo'],
                        url_noticia=noticia['url_noticia'],
                        fonte=noticia['fonte'],
                        data_publicacao=noticia['data_publicacao'],
                        resumo=noticia.get('resumo'),
                        conteudo_completo=noticia.get('conteudo_completo'),
                        autor=noticia.get('autor'),
                        imagem_destaque=noticia.get('imagem_destaque')
                    )
                    
                    self.db.add(nova_noticia)
                    contador += 1
                
            except Exception as e:
                self.logger.error(
                    f"Erro ao salvar notícia '{noticia.get('titulo')}': {str(e)}", 
                    exc_info=True
                )
        
        try:
            self.db.commit()
            return contador
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erro ao fazer commit das notícias: {str(e)}", exc_info=True)
            return 0
    
    def coletar_para_todos_clubes(self, limite_por_clube: int = 5) -> Dict:
        """
        Coleta notícias para todos os clubes ativos no banco de dados.
        
        Args:
            limite_por_clube: Número máximo de notícias a coletar por clube
            
        Returns:
            Dict: Estatísticas da coleta
        """
        self.logger.info(f"Iniciando coleta de notícias para todos os clubes ativos")
        
        try:
            # Busca todos os clubes ativos
            clubes = self.db.query(Clube).filter(Clube.ativo == True).all()
            
            if not clubes:
                self.logger.warning("Nenhum clube ativo encontrado no banco de dados.")
                return {
                    'status': 'aviso',
                    'mensagem': 'Nenhum clube ativo encontrado',
                    'total_noticias_coletadas': 0,
                    'clubes_processados': 0
                }
            
            # Coleta notícias para cada clube
            total_noticias = 0
            for clube in clubes:
                resultado = self.coletar_noticias_clube(clube.id, limite_por_clube)
                if resultado['status'] == 'sucesso':
                    total_noticias += resultado['noticias_coletadas']
            
            self.logger.info(
                f"Coleta concluída para {len(clubes)} clubes. "
                f"Total de notícias coletadas: {total_noticias}"
            )
            
            return {
                'status': 'sucesso',
                'total_clubes': len(clubes),
                'total_noticias_coletadas': total_noticias,
                'limite_por_clube': limite_por_clube,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro durante a coleta de notícias: {str(e)}", exc_info=True)
            return {
                'status': 'erro',
                'mensagem': str(e),
                'total_noticias_coletadas': 0,
                'clubes_processados': 0
            }

def coletar_noticias_para_todos_clubes(limite_por_clube: int = 5) -> Dict:
    """
    Função de conveniência para coletar notícias para todos os clubes ativos.
    
    Args:
        limite_por_clube: Número máximo de notícias a coletar por clube
        
    Returns:
        Dict: Estatísticas da coleta
    """
    collector = NewsCollector()
    try:
        return collector.coletar_para_todos_clubes(limite_por_clube)
    except Exception as e:
        logging.error(f"Erro inesperado ao coletar notícias: {str(e)}", exc_info=True)
        return {
            'status': 'erro',
            'mensagem': f"Erro inesperado: {str(e)}",
            'total_noticias_coletadas': 0,
            'clubes_processados': 0
        }
    finally:
        # O coletor fecha a sessão no destruidor
        pass

if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    # Configura logging para o console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    # Cria um coletor e coleta notícias para todos os clubes
    resultado = coletar_noticias_para_todos_clubes(limite_por_clube=3)
    
    # Exibe o resultado
    print("\n" + "="*80)
    print("RESULTADO DA COLETA DE NOTÍCIAS".center(80))
    print("="*80)
    print(f"Status: {resultado['status'].upper()}")
    print(f"Clubes processados: {resultado.get('total_clubes', 0)}")
    print(f"Notícias coletadas: {resultado.get('total_noticias_coletadas', 0)}")
    
    if 'mensagem' in resultado:
        print(f"Mensagem: {resultado['mensagem']}")
    
    print("="*80)
