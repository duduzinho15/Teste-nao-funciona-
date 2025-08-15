#!/usr/bin/env python3
"""
Script para testar os endpoints da API relacionados a posts de redes sociais

Este script testa os seguintes endpoints da API:
- GET /api/v1/social/posts/clube/{clube_id} - Listar posts por clube
- GET /api/v1/social/posts/{post_id} - Obter detalhes de um post
- POST /api/v1/social/coletar/clube/{clube_id} - Coletar posts para um clube
- POST /api/v1/social/coletar/todos - Coletar posts para todos os clubes
- GET /api/v1/social/estatisticas/{clube_id} - Obter estatísticas de engajamento
"""
import requests
import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configurações da API
BASE_URL = "http://localhost:8000"  # URL base da API
API_KEY = "apostapro-api-key-change-in-production"  # Chave de API padrão do ambiente de desenvolvimento

# Cabeçalhos para as requisições
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-Key": API_KEY
}

# Configuração de timeout para as requisições
REQUEST_TIMEOUT = 30  # segundos

# Classe para exceções personalizadas
class APITestError(Exception):
    """Exceção personalizada para erros de teste de API"""
    pass

# Função auxiliar para fazer requisições HTTP
def make_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """
    Função auxiliar para fazer requisições HTTP com tratamento de erros.
    
    Args:
        method: Método HTTP (GET, POST, etc.)
        endpoint: Endpoint da API (ex: '/api/v1/social/posts')
        **kwargs: Argumentos adicionais para requests.request()
        
    Returns:
        Response: Objeto de resposta da requisição
        
    Raises:
        APITestError: Se ocorrer um erro na requisição
    """
    url = f"{BASE_URL}{endpoint}"
    
    # Adiciona cabeçalhos padrão se não fornecidos
    if 'headers' not in kwargs:
        kwargs['headers'] = HEADERS
    else:
        # Garante que os cabeçalhos padrão sejam mesclados com os fornecidos
        for key, value in HEADERS.items():
            if key not in kwargs['headers']:
                kwargs['headers'][key] = value
    
    # Adiciona timeout se não fornecido
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 30  # 30 segundos de timeout padrão
    
    try:
        logger.debug(f"Enviando requisição {method.upper()} para {url}")
        logger.debug(f"Cabeçalhos: {kwargs.get('headers', {})}")
        
        start_time = time.time()
        response = requests.request(method, url, **kwargs)
        elapsed_time = (time.time() - start_time) * 1000  # em milissegundos
        
        # Tenta fazer o parse do JSON, se possível
        try:
            if response.text:
                logger.debug(f"Corpo da resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            logger.debug(f"Resposta não é JSON: {response.text[:500]}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erro na requisição para {url}: {str(e)}"
        logger.error(error_msg)
        raise APITestError(error_msg) from e

def test_health_check() -> bool:
    """Testa o endpoint de health check"""
    logger.info("🔍 Testando health check...")
    try:
        response = make_request("GET", "/api/v1/health")
        
        if response.status_code == 200:
            logger.info(f"✅ Health check bem-sucedido! Status: {response.status_code}")
            logger.info(f"Versão da API: {response.json().get('version', 'N/A')}")
            logger.info(f"Status do banco: {response.json().get('database', 'N/A')}")
            return True
        else:
            logger.error(f"❌ Falha no health check. Status: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
            
    except APITestError as e:
        logger.error(f"❌ Erro ao testar health check: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao testar health check: {str(e)}", exc_info=True)
        return False

def test_listar_posts_por_clube(clube_id: int = 1) -> List[Dict[str, Any]]:
    """
    Testa a listagem de posts de um clube específico
    
    Args:
        clube_id: ID do clube para listar os posts
        
    Returns:
        Lista de posts do clube
    """
    logger.info(f"📋 Testando listagem de posts para o clube ID {clube_id}...")
    
    try:
        # Parâmetros de consulta
        params = {
            "page": 1,
            "size": 5,
            "rede_social": "twitter",  # Filtro opcional
            "data_inicio": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "data_fim": datetime.now().strftime('%Y-%m-%d')
        }
        
        logger.debug(f"Parâmetros da consulta: {params}")
        
        # Faz a requisição usando a função auxiliar
        response = make_request(
            "GET", 
            f"/api/v1/social/posts/clube/{clube_id}",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Listagem de posts bem-sucedida! Total: {data.get('total', 0)} posts")
            logger.info(f"📊 Página {data.get('page', 1)} de {data.get('pages', 1)} (tamanho: {data.get('size', 0)})")
            
            items = data.get('items', [])
            if items:
                logger.info("📄 Exemplo de posts encontrados:")
                for i, post in enumerate(items[:3], 1):
                    logger.info(
                        f"   {i}. ID: {post.get('id', 'N/A')} | "
                        f"Rede: {post.get('rede_social', 'N/A')} | "
                        f"Curtidas: {post.get('curtidas', 0)} | "
                        f"Data: {post.get('data_postagem', 'N/A')}"
                    )
            else:
                logger.warning("⚠️  Nenhum post encontrado para este clube")
            
            return items
        else:
            error_msg = f"❌ Erro ao listar posts. Status: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'Detalhe não disponível')
                error_msg += f" | Detalhe: {error_detail}"
            except:
                error_msg += f" | Resposta: {response.text[:200]}"
            
            logger.error(error_msg)
            return []
            
    except APITestError as e:
        logger.error(f"❌ Erro na requisição de listagem de posts: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao listar posts: {str(e)}", exc_info=True)
        return []

def test_obter_post_por_id(post_id: int) -> Optional[Dict[str, Any]]:
    """
    Testa a busca por um post específico pelo ID
    
    Args:
        post_id: ID do post a ser buscado
        
    Returns:
        Dicionário com os dados do post se encontrado, None caso contrário
    """
    logger.info(f"🔍 Testando busca pelo post ID {post_id}...")
    
    try:
        # Faz a requisição usando a função auxiliar
        response = make_request(
            "GET",
            f"/api/v1/social/posts/{post_id}"
        )
        
        if response.status_code == 200:
            post = response.json()
            logger.info("✅ Post encontrado com sucesso!")
            
            # Loga os detalhes do post de forma estruturada
            logger.info("📝 Detalhes do post:")
            logger.info(f"   ID: {post.get('id', 'N/A')}")
            logger.info(f"   Rede Social: {post.get('rede_social', 'N/A')}")
            logger.info(f"   Clube ID: {post.get('clube_id', 'N/A')}")
            logger.info(f"   Post ID Original: {post.get('post_id', 'N/A')}")
            logger.info(f"   Data de Postagem: {post.get('data_postagem', 'N/A')}")
            logger.info(f"   Curtidas: {post.get('curtidas', 0)}")
            logger.info(f"   Comentários: {post.get('comentarios', 0)}")
            logger.info(f"   Compartilhamentos: {post.get('compartilhamentos', 0)}")
            
            # Loga uma prévia do conteúdo (limitando o tamanho)
            conteudo = post.get('conteudo', '')
            if conteudo:
                preview = (conteudo[:100] + '...') if len(conteudo) > 100 else conteudo
                logger.info(f"   Conteúdo: {preview}")
            
            # Loga a URL do post se existir
            if 'url_post' in post and post['url_post']:
                logger.info(f"   URL: {post['url_post']}")
            
            return post
            
        elif response.status_code == 404:
            logger.warning(f"⚠️  Post com ID {post_id} não encontrado")
            return None
            
        else:
            error_msg = f"❌ Erro ao buscar post. Status: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'Detalhe não disponível')
                error_msg += f" | Detalhe: {error_detail}"
            except:
                error_msg += f" | Resposta: {response.text[:200]}"
            
            logger.error(error_msg)
            return None
            
    except APITestError as e:
        logger.error(f"❌ Erro na requisição de busca de post: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao buscar post: {str(e)}", exc_info=True)
        return None

def test_coletar_posts_clube(clube_id: int = 1, limite: int = 3) -> bool:
    """
    Testa a coleta de posts para um clube específico
    
    Args:
        clube_id: ID do clube para coletar posts
        limite: Número máximo de posts a serem coletados
        
    Returns:
        True se a coleta for bem-sucedida, False caso contrário
    """
    logger.info(f"🔄 Testando coleta de até {limite} posts para o clube ID {clube_id}...")
    
    try:
        # Parâmetros da requisição
        params = {"limite": limite}
        
        # Faz a requisição usando a função auxiliar
        response = make_request(
            "POST",
            f"/api/v1/social/coletar/clube/{clube_id}",
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica se a resposta tem a estrutura esperada
            if 'message' in result and 'data' in result and 'posts_coletados' in result['data']:
                logger.info(f"✅ {result['message']}")
                logger.info(f"   Posts coletados: {result['data']['posts_coletados']}")
                
                # Loga detalhes adicionais se disponíveis
                if 'detalhes' in result['data'] and result['data']['detalhes']:
                    logger.info("   Detalhes adicionais:")
                    for key, value in result['data']['detalhes'].items():
                        logger.info(f"      - {key}: {value}")
                
                return True
            else:
                logger.warning("⚠️  Resposta da API em formato inesperado")
                logger.debug(f"Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False
                
        elif response.status_code == 404:
            logger.error(f"❌ Clube com ID {clube_id} não encontrado")
            return False
            
        else:
            error_msg = f"❌ Erro ao coletar posts. Status: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'Detalhe não disponível')
                error_msg += f" | Detalhe: {error_detail}"
            except:
                error_msg += f" | Resposta: {response.text[:200]}"
            
            logger.error(error_msg)
            return False
            
    except APITestError as e:
        logger.error(f"❌ Erro na requisição de coleta de posts: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao coletar posts: {str(e)}", exc_info=True)
        return False

def test_coletar_posts_todos_clubes(limite_por_clube: int = 2) -> bool:
    """
    Testa a coleta de posts para todos os clubes
    
    Args:
        limite_por_clube: Número máximo de posts a serem coletados por clube
        
    Returns:
        True se a coleta for bem-sucedida para pelo menos um clube, False caso contrário
    """
    logger.info(f"🔄 Testando coleta de até {limite_por_clube} posts para todos os clubes...")
    
    try:
        # Parâmetros da requisição
        params = {"limite_por_clube": limite_por_clube}
        
        # Faz a requisição usando a função auxiliar
        response = make_request(
            "POST",
            "/api/v1/social/coletar/todos",
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica se a resposta tem a estrutura esperada
            if 'message' in result and 'data' in result and 'resultados' in result['data']:
                logger.info(f"✅ {result['message']}")
                
                resultados = result['data']['resultados']
                total_posts = sum(res.get('posts_coletados', 0) for res in resultados)
                total_clubes = len(resultados)
                
                logger.info(f"📊 Resumo da coleta:")
                logger.info(f"   - Total de clubes processados: {total_clubes}")
                logger.info(f"   - Total de posts coletados: {total_posts}")
                
                # Loga os resultados por clube
                if resultados:
                    logger.info("📋 Detalhes por clube:")
                    for i, res in enumerate(resultados, 1):
                        clube_nome = res.get('clube_nome', f'Clube {i}')
                        posts_coletados = res.get('posts_coletados', 0)
                        status = "✅" if res.get('sucesso', False) else "❌"
                        
                        logger.info(f"   {status} {clube_nome}: {posts_coletados} posts")
                        
                        # Loga detalhes adicionais se disponíveis
                        if 'detalhes' in res and res['detalhes']:
                            for key, value in res['detalhes'].items():
                                logger.info(f"      - {key}: {value}")
                
                # Retorna True se pelo menos um post foi coletado
                return total_posts > 0
            else:
                logger.warning("⚠️  Resposta da API em formato inesperado")
                logger.debug(f"Resposta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return False
                
        else:
            error_msg = f"❌ Erro ao coletar posts. Status: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'Detalhe não disponível')
                error_msg += f" | Detalhe: {error_detail}"
            except:
                error_msg += f" | Resposta: {response.text[:200]}"
            
            logger.error(error_msg)
            return False
            
    except APITestError as e:
        logger.error(f"❌ Erro na requisição de coleta de posts: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao coletar posts: {str(e)}", exc_info=True)
        return False

def test_obter_estatisticas_engajamento(clube_id: int = 1, periodo_dias: int = 30) -> Optional[Dict[str, Any]]:
    """
    Testa a obtenção de estatísticas de engajamento para um clube
    
    Args:
        clube_id: ID do clube para obter estatísticas
        periodo_dias: Número de dias para o período de análise
        
    Returns:
        Dicionário com as estatísticas de engajamento se bem-sucedido, None caso contrário
    """
    logger.info(f"📊 Testando obtenção de estatísticas para o clube ID {clube_id} (últimos {periodo_dias} dias)...")
    
    try:
        # Parâmetros da requisição
        params = {"periodo_dias": periodo_dias}
        
        # Faz a requisição usando a função auxiliar
        response = make_request(
            "GET",
            f"/api/v1/social/estatisticas/{clube_id}",
            params=params
        )
        
        if response.status_code == 200:
            stats = response.json()
            
            # Verifica se a resposta tem a estrutura esperada
            if 'clube_id' in stats and 'periodo' in stats and 'estatisticas' in stats:
                logger.info("✅ Estatísticas obtidas com sucesso!")
                
                # Loga um resumo das estatísticas
                logger.info("📊 Resumo das estatísticas:")
                logger.info(f"   - Clube ID: {stats.get('clube_id', 'N/A')}")
                logger.info(f"   - Período: {stats.get('periodo', {}).get('inicio', 'N/A')} a {stats.get('periodo', {}).get('fim', 'N/A')}")
                
                estatisticas = stats.get('estatisticas', {})
                
                # Loga métricas básicas
                if 'metricas_basicas' in estatisticas:
                    metricas = estatisticas['metricas_basicas']
                    logger.info("   📈 Métricas Básicas:")
                    for key, value in metricas.items():
                        logger.info(f"      - {key.replace('_', ' ').title()}: {value}")
                
                # Loga métricas por rede social
                if 'por_rede_social' in estatisticas and estatisticas['por_rede_social']:
                    logger.info("   📱 Métricas por Rede Social:")
                    for rede, dados in estatisticas['por_rede_social'].items():
                        logger.info(f"      - {rede.upper()}:")
                        for key, value in dados.items():
                            logger.info(f"         • {key.replace('_', ' ').title()}: {value}")
                
                # Loga métricas ao longo do tempo se disponíveis
                if 'evolucao_no_tempo' in estatisticas and estatisticas['evolucao_no_tempo']:
                    logger.info(f"   📅 Evolução no tempo: {len(estatisticas['evolucao_no_tempo'])} períodos")
                
                return stats
            else:
                logger.warning("⚠️  Resposta da API em formato inesperado")
                logger.debug(f"Resposta completa: {json.dumps(stats, indent=2, ensure_ascii=False)}")
                return None
                
        elif response.status_code == 404:
            logger.error(f"❌ Clube com ID {clube_id} não encontrado")
            return None
            
        else:
            error_msg = f"❌ Erro ao obter estatísticas. Status: {response.status_code}"
            try:
                error_detail = response.json().get('detail', 'Detalhe não disponível')
                error_msg += f" | Detalhe: {error_detail}"
            except:
                error_msg += f" | Resposta: {response.text[:200]}"
            
            logger.error(error_msg)
            return None
            
    except APITestError as e:
        logger.error(f"❌ Erro na requisição de estatísticas: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao obter estatísticas: {str(e)}", exc_info=True)
        return None

def main():
    """
    Função principal para executar os testes da API de Redes Sociais
    """
    # Configura o nível de log para DEBUG durante os testes
    logger.setLevel(logging.DEBUG)
    
    logger.info("🚀 Iniciando testes da API de Redes Sociais")
    logger.info("=" * 60)
    
    # 1. Testa o health check
    logger.info("\n" + "🔍 FASE 1: Verificando saúde da API".ljust(70, '='))
    if not test_health_check():
        logger.error("❌ Health check falhou. Verifique se a API está rodando corretamente.")
        return 1
    
    # ID do clube de teste (pode ser ajustado via argumento de linha de comando)
    clube_teste_id = 1
    
    # 2. Testa a coleta de posts para um clube específico
    logger.info("\n" + "🔄 FASE 2: Testando coleta de posts para um clube".ljust(70, '='))
    coleta_ok = test_coletar_posts_clube(clube_teste_id, limite=3)
    
    # Aguarda um pouco para a coleta ser concluída
    if coleta_ok:
        logger.info("⏳ Aguardando processamento da coleta...")
        time.sleep(2)
    
    # 3. Testa a listagem de posts do clube
    logger.info("\n" + "📋 FASE 3: Testando listagem de posts por clube".ljust(70, '='))
    posts = test_listar_posts_por_clube(clube_teste_id)
    
    # 4. Se houver posts, testa a busca por um post específico
    if posts:
        logger.info("\n" + "🔍 FASE 4: Testando busca detalhada de um post".ljust(70, '='))
        post_id_teste = posts[0].get('id') if posts else None
        if post_id_teste:
            test_obter_post_por_id(post_id_teste)
    else:
        logger.warning("⚠️  Nenhum post encontrado para teste. Pulando teste de busca detalhada.")
    
    # 5. Testa a coleta de posts para todos os clubes (opcional - pode ser descomentado)
    # logger.info("\n" + "🔄 FASE 5: Testando coleta de posts para todos os clubes".ljust(70, '='))
    # test_coletar_posts_todos_clubes(limite_por_clube=2)
    
    # 6. Testa a obtenção de estatísticas de engajamento
    logger.info("\n" + "📊 FASE 5: Testando obtenção de estatísticas de engajamento".ljust(70, '='))
    test_obter_estatisticas_engajamento(clube_teste_id)
    
    logger.info("\n" + "✅ Testes concluídos com sucesso!" + " " * 30)
    return 0

if __name__ == "__main__":
    main()
