#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO - NOTÍCIAS VIA API
==================================

Script para testar o fluxo completo de coleta e exposição de notícias de clubes:
1. Coleta notícias de um clube
2. Verifica se os dados foram salvos no banco de dados
3. Inicia a API localmente
4. Testa o endpoint da API para validar os dados
5. Gera relatório de teste
"""

import os
import sys
import time
import logging
import traceback
import subprocess
from typing import Dict, List, Optional, Any
import requests
from requests.exceptions import RequestException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_integracao_noticias.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class TesteIntegracaoNoticias:
    """Classe para testar a integração de notícias com a API."""
    
    # Inicialização dos atributos como variáveis de classe
    logger = logging.getLogger(__name__)
    test_results = {}
    api_process = None
    api_url = "http://localhost:8000"
    api_key = "apostapro-api-key-change-in-production"  # Chave padrão de desenvolvimento
    engine = None
    Session = None
    
    @classmethod
    def setup_class(cls):
        """Configuração da classe de teste."""
        # Configurar logger para arquivo
        cls.logger = logging.getLogger('test_news_api')
        cls.logger.setLevel(logging.INFO)
        
        # Criar handler para arquivo se não existir
        if not any(isinstance(h, logging.FileHandler) for h in cls.logger.handlers):
            file_handler = logging.FileHandler('test_news_integration.log', mode='w')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            cls.logger.addHandler(file_handler)
        
        # Configurar handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        cls.logger.addHandler(console_handler)
        
        cls.test_results = {}
        cls.api_process = None
        cls.api_url = "http://localhost:8000"
        cls.api_key = "apostapro-api-key-change-in-production"
        cls.logger.info("🔧 Configuração da classe de teste concluída")
    
    @classmethod
    def setup_database(cls) -> bool:
        """Configura a conexão com o banco de dados."""
        try:
            cls.logger.info("🔍 Configurando conexão com o banco de dados...")
            
            # Configuração do banco de dados (ajuste conforme necessário)
            db_url = os.getenv('DATABASE_URL', 'postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db')
            cls.logger.info(f"Conectando ao banco de dados: {db_url}")
            
            # Criar engine com configurações básicas
            cls.engine = create_engine(db_url, pool_pre_ping=True)
            cls.Session = sessionmaker(bind=cls.engine)
            
            # Testar conexão
            with cls.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            cls.logger.info("✅ Conexão com o banco de dados bem-sucedida")
            return True
            
        except Exception as e:
            cls.logger.error(f"❌ Falha na conexão com o banco de dados: {e}")
            cls.logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def obter_clube_teste(cls) -> Optional[Dict]:
        """Obtém um clube para teste."""
        try:
            session = cls.Session()
            
            # Buscar um clube que tenha notícias
            query = text("""
                SELECT c.id, c.nome, COUNT(n.id) as total_noticias
                FROM clubes c
                LEFT JOIN noticias_clubes n ON c.id = n.clube_id
                GROUP BY c.id, c.nome
                ORDER BY total_noticias DESC
                LIMIT 1
            """)
            
            result = session.execute(query).fetchone()
            
            if not result:
                # Se não houver notícias, buscar qualquer clube
                query = text("SELECT id, nome FROM clubes LIMIT 1")
                result = session.execute(query).fetchone()
                
                if not result:
                    self.logger.warning("Nenhum clube encontrado no banco de dados")
                    return None
                
                clube = {
                    'id': result[0],
                    'nome': result[1],
                    'total_noticias': 0
                }
            else:
                clube = {
                    'id': result[0],
                    'nome': result[1],
                    'total_noticias': result[2] or 0
                }
            
            session.close()
            return clube
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar clube para teste: {e}")
            self.logger.error(traceback.format_exc())
            return None
    
    def criar_noticia_teste(self, clube_id: int) -> Dict:
        """Cria uma notícia de teste para o clube especificado."""
        try:
            session = self.Session()
            
            # Gerar dados de teste
            titulo = f"Notícia de teste para clube ID {clube_id}"
            url_noticia = f"https://exemplo.com/noticia/teste-{clube_id}-{int(time.time())}"
            fonte = "Teste Automatizado"
            data_publicacao = datetime.now()
            
            # Inserir notícia de teste
            query = text("""
                INSERT INTO noticias_clubes 
                (clube_id, titulo, url_noticia, fonte, data_publicacao, resumo, conteudo_completo, autor, imagem_destaque)
                VALUES 
                (:clube_id, :titulo, :url_noticia, :fonte, :data_publicacao, :resumo, :conteudo_completo, :autor, :imagem_destaque)
                RETURNING id
            """)
            
            result = session.execute(
                query,
                {
                    'clube_id': clube_id,
                    'titulo': titulo,
                    'url_noticia': url_noticia,
                    'fonte': fonte,
                    'data_publicacao': data_publicacao,
                    'resumo': "Este é um resumo de teste para a notícia de teste.",
                    'conteudo_completo': "Este é o conteúdo completo da notícia de teste. " * 10,
                    'autor': "Sistema de Teste",
                    'imagem_destaque': f"https://exemplo.com/imagens/teste-{clube_id}.jpg"
                }
            )
            
            noticia_id = result.fetchone()[0]
            session.commit()
            
            noticia = {
                'id': noticia_id,
                'clube_id': clube_id,
                'titulo': titulo,
                'url_noticia': url_noticia,
                'fonte': fonte,
                'data_publicacao': data_publicacao.isoformat()
            }
            
            self.logger.info(f"✅ Notícia de teste criada com sucesso: ID {noticia_id}")
            return noticia
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"❌ Erro ao criar notícia de teste: {e}")
            return None
            
        finally:
            session.close()
    
    @classmethod
    def start_api(cls) -> bool:
        """Inicia a API em um processo separado."""
        try:
            cls.logger.info("🚀 Iniciando a API...")
            
            # Comando para iniciar a API (ajuste conforme necessário)
            cmd = ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
            cls.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Dar um tempo para a API iniciar
            time.sleep(5)
            
            # Verificar se a API está respondendo
            try:
                response = requests.get(f"{cls.api_url}/health", timeout=10)
                if response.status_code == 200:
                    cls.logger.info("✅ API iniciada com sucesso")
                    return True
                else:
                    cls.logger.error(f"❌ Falha ao iniciar a API: {response.text}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                cls.logger.error(f"❌ Erro ao conectar à API: {e}")
                return False
                
        except Exception as e:
            cls.logger.error(f"❌ Erro ao iniciar a API: {e}")
            cls.logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def stop_api(cls):
        """Para o processo da API."""
        if cls.api_process:
            cls.logger.info("🛑 Parando a API...")
            cls.api_process.terminate()
            try:
                cls.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.api_process.kill()
            cls.logger.info("✅ API parada")
    
    @classmethod
    def _testar_endpoint_noticias_clube(cls, clube_id: int) -> bool:
        """Testa o endpoint de notícias por clube."""
        try:
            cls.logger.info(f"🧪 Testando endpoint de notícias para o clube ID: {clube_id}")
            
            headers = {
                "X-API-Key": cls.api_key,
                "Content-Type": "application/json"
            }
            
            # Testar parâmetros de paginação
            for page in [1, 2]:
                for per_page in [5, 10]:
                    url = f"{cls.api_url}/api/v1/clubs/{clube_id}/news?page={page}&per_page={per_page}"
                    response = requests.get(url, headers=headers)
                    
                    # Verificar status code
                    if response.status_code != 200:
                        cls.logger.error(f"❌ Erro no endpoint de notícias. Status: {response.status_code}")
                        cls.logger.error(f"Resposta: {response.text}")
                        return False
                    
                    # Verificar schema da resposta
                    try:
                        data = response.json()
                        
                        # Verificar estrutura básica
                        if not all(key in data for key in ["items", "total", "page", "per_page"]):
                            cls.logger.error("❌ Estrutura da resposta inválida")
                            return False
                            
                        # Verificar itens
                        for item in data["items"]:
                            if not all(key in item for key in ["id", "titulo", "conteudo", "data_publicacao", "fonte"]):
                                cls.logger.error("❌ Item de notícia inválido")
                                return False
                                
                        cls.logger.info(f"✅ Teste de paginação (página {page}, {per_page} itens) passou")
                        
                    except ValueError as e:
                        cls.logger.error(f"❌ Resposta não é um JSON válido: {e}")
                        return False
            
            cls.logger.info("✅ Todos os testes de paginação passaram")
            return True
            
        except Exception as e:
            cls.logger.error(f"❌ Erro ao testar endpoint de notícias: {e}")
            cls.logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def _testar_endpoint_noticias_invalido(cls) -> bool:
        """Testa o endpoint de notícias com parâmetros inválidos."""
        try:
            cls.logger.info("🧪 Testando endpoint de notícias com parâmetros inválidos")
            
            headers = {
                "X-API-Key": cls.api_key,
                "Content-Type": "application/json"
            }
            
            # Testar com ID de clube inválido
            response = requests.get(f"{cls.api_url}/api/v1/clubs/999999/news", headers=headers)
            if response.status_code != 404:
                cls.logger.error(f"❌ Status code inesperado para clube inexistente: {response.status_code}")
                return False
                
            # Testar com parâmetros de paginação inválidos
            for test_url in [
                f"{cls.api_url}/api/v1/clubs/1/news?page=0",
                f"{cls.api_url}/api/v1/clubs/1/news?per_page=0",
                f"{cls.api_url}/api/v1/clubs/1/news?page=abc",
                f"{cls.api_url}/api/v1/clubs/1/news?per_page=abc"
            ]:
                response = requests.get(test_url, headers=headers)
                if response.status_code != 422:  # 422 Unprocessable Entity para validação falha
                    cls.logger.error(f"❌ Status code inesperado para parâmetros inválidos em {test_url}: {response.status_code}")
                    return False
            
            cls.logger.info("✅ Testes com parâmetros inválidos passaram")
            return True
            
        except Exception as e:
            cls.logger.error(f"❌ Erro ao testar endpoint com parâmetros inválidos: {e}")
            cls.logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def _testar_endpoint_noticia_especifica(cls, noticia_id: int) -> bool:
        """Testa o endpoint de uma notícia específica."""
        try:
            cls.logger.info(f"🔍 Testando endpoint /api/v1/news/{noticia_id}...")
            
            headers = {
                "X-API-Key": cls.api_key
            }
            
            response = requests.get(
                f"{cls.api_url}/api/v1/news/{noticia_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                cls.logger.error(f"❌ Falha ao buscar notícia. Status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Validar estrutura da resposta
            required_fields = ["id", "clube_id", "titulo", "url_noticia", "fonte", "data_publicacao"]
            for field in required_fields:
                if field not in data:
                    cls.logger.error(f"❌ Campo obrigatório ausente na resposta: {field}")
                    return False
            
            cls.logger.info(f"✅ Notícia encontrada: {data['titulo']}")
            return True
            
        except Exception as e:
            cls.logger.error(f"❌ Erro ao testar endpoint de notícia específica: {e}")
            cls.logger.error(traceback.format_exc())
            return False
    
    @classmethod
    def test_news_endpoints(cls):
        """Testa todos os endpoints de notícias."""
        cls.test_results = {}
        sucesso_geral = True
        
        # 1. Configurar banco de dados
        if not cls.setup_database():
            cls.logger.error("❌ Falha ao configurar o banco de dados")
            return False
            
        # 2. Iniciar a API
        if not cls.start_api():
            cls.logger.error("❌ Falha ao iniciar a API")
            return False
            
        try:
            # 3. Testar endpoints
            cls.logger.info("\n🔍 Iniciando testes de integração...")
            
            # Testar endpoint de notícias inválidas
            cls.logger.info("\n🧪 Testando endpoint com parâmetros inválidos...")
            if cls._testar_endpoint_noticias_invalido():
                cls.test_results["test_invalid_params"] = "✅ Passou"
            else:
                cls.test_results["test_invalid_params"] = "❌ Falhou"
                sucesso_geral = False
            
            # Testar endpoint de notícias por clube (usando um ID de clube conhecido)
            clube_id = 1  # Ajuste para um ID de clube válido no seu banco de dados
            cls.logger.info(f"\n🧪 Testando endpoint de notícias para o clube ID: {clube_id}...")
            if cls._testar_endpoint_noticias_clube(clube_id):
                cls.test_results["test_club_news"] = "✅ Passou"
            else:
                cls.test_results["test_club_news"] = "❌ Falhou"
                sucesso_geral = False
            
            # Se o teste de notícias por clube passou, testar notícia específica
            if sucesso_geral and hasattr(cls, 'ultima_noticia_id'):
                cls.logger.info(f"\n🧪 Testando endpoint de notícia específica ID: {cls.ultima_noticia_id}...")
                if cls._testar_endpoint_noticia_especifica(cls.ultima_noticia_id):
                    cls.test_results["test_single_news"] = "✅ Passou"
                else:
                    cls.test_results["test_single_news"] = "❌ Falhou"
                    sucesso_geral = False
            
            # Exibir resultados
            cls.logger.info("\n📊 Resultados dos testes:")
            for teste, resultado in cls.test_results.items():
                cls.logger.info(f"{teste}: {resultado}")
            
            return sucesso_geral
            
        except Exception as e:
            cls.logger.error(f"❌ Erro durante a execução dos testes: {e}")
            cls.logger.error(traceback.format_exc())
            return False
            
        finally:
            # 4. Parar a API
            cls.stop_api()
            cls.logger.info("\n🏁 Testes concluídos")
        """Executa todos os testes de integração."""
        cls.test_results = {}
        sucesso_geral = True
        
        # 1. Configurar banco de dados
        self.test_results['setup_database'] = self.setup_database()
        if not self.test_results['setup_database']:
            self.logger.error("❌ Falha na configuração do banco de dados. Abortando teste.")
            return False
        
        # 2. Obter ou criar um clube para teste
        clube = self.obter_clube_teste()
        if not clube:
            self.logger.error("❌ Não foi possível obter um clube para teste.")
            return False
        
        self.logger.info(f"🏆 Clube selecionado para teste: {clube['nome']} (ID: {clube['id']})")
        
        # 3. Se não houver notícias, criar uma
        if clube['total_noticias'] == 0:
            self.logger.info("ℹ️  Nenhuma notícia encontrada para o clube. Criando notícia de teste...")
            noticia = self.criar_noticia_teste(clube['id'])
            if not noticia:
                self.logger.error("❌ Falha ao criar notícia de teste.")
                return False
        
        # 4. Iniciar a API
        self.test_results['iniciar_api'] = self.iniciar_api()
        if not self.test_results['iniciar_api']:
            self.logger.error("❌ Falha ao iniciar a API. Abortando teste.")
            self.parar_api()
            return False
        
        # 5. Testar endpoints
        try:
            # Testar endpoint de notícias por clube
            self.test_results['testar_endpoint_noticias'] = self.testar_endpoint_noticias_clube(clube['id'])
            
            # Se todos os testes passaram
            sucesso_geral = all(self.test_results.values())
            
            if sucesso_geral:
                self.logger.info("✅✅✅ TODOS OS TESTES PASSARAM COM SUCESSO! ✅✅✅")
            else:
                self.logger.error("❌❌❌ ALGUNS TESTES FALHARAM. VERIFIQUE OS LOGS. ❌❌❌")
                
                # Log detalhado dos resultados
                self.logger.info("\n📊 RESUMO DOS TESTES:")
                for teste, resultado in self.test_results.items():
                    status = "✅ PASSOU" if resultado else "❌ FALHOU"
                    self.logger.info(f"{status} - {teste}")
            
            return sucesso_geral
            
        except Exception as e:
            self.logger.error(f"❌❌❌ ERRO INESPERADO DURANTE OS TESTES: {e}")
            self.logger.error(traceback.format_exc())
            return False
            
        finally:
            # 6. Parar a API
            self.parar_api()

def main() -> int:
    """Função principal."""
    logger.info("🚀 INICIANDO TESTE DE INTEGRAÇÃO - NOTÍCIAS VIA API")
    logger.info("=" * 60)
    
    teste = TesteIntegracaoNoticias()
    sucesso = teste.executar_teste_completo()
    
    logger.info("=" * 60)
    logger.info("✅ TESTE CONCLUÍDO" if sucesso else "❌ TESTE FALHOU")
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n❌ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERRO NÃO TRATADO: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
