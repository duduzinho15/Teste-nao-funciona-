#!/usr/bin/env python3
"""
Script para testar os endpoints da API relacionados à tabela posts_redes_sociais
"""
import requests
import json
import os
from datetime import datetime, timedelta

# Configurações da API
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "sua_chave_api_aqui"  # Substitua pela chave de API correta

# Cabeçalhos para as requisições
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_health_check():
    """Testa o endpoint de health check"""
    print("\n🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao testar health check: {e}")
        return False

def test_create_post():
    """Testa a criação de um novo post"""
    print("\n📝 Testando criação de post...")
    
    # Dados do post de exemplo
    post_data = {
        "clube_id": 1,  # Substitua por um ID de clube válido
        "rede_social": "twitter",
        "post_id": f"tw_{int(datetime.now().timestamp())}",
        "conteudo": "Teste de post via API",
        "data_postagem": (datetime.now() - timedelta(hours=1)).isoformat(),
        "curtidas": 42,
        "comentarios": 7,
        "compartilhamentos": 3,
        "url_post": "https://twitter.com/user/status/123456789",
        "midia_url": "https://pbs.twimg.com/media/example.jpg"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/posts-redes-sociais",
            headers=HEADERS,
            data=json.dumps(post_data)
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("✅ Post criado com sucesso!")
            return response.json()
        else:
            print(f"❌ Erro ao criar post: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao testar criação de post: {e}")
        return None

def test_get_posts():
    """Testa a listagem de posts"""
    print("\n📋 Testando listagem de posts...")
    
    try:
        # Testa filtros opcionais
        params = {
            "skip": 0,
            "limit": 10,
            "clube_id": 1,  # Filtro opcional
            "rede_social": "twitter"  # Filtro opcional
        }
        
        response = requests.get(
            f"{BASE_URL}/posts-redes-sociais",
            headers=HEADERS,
            params=params
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total de posts encontrados: {len(data)}")
        
        if data:
            print("\n📄 Posts encontrados:")
            for i, post in enumerate(data[:3], 1):  # Mostra apenas os 3 primeiros
                print(f"{i}. ID: {post['id']} | Rede: {post['rede_social']} | Curtidas: {post['curtidas']}")
            if len(data) > 3:
                print(f"... e mais {len(data) - 3} posts")
        
        return data
        
    except Exception as e:
        print(f"❌ Erro ao listar posts: {e}")
        return []

def test_get_post(post_id):
    """Testa a busca por um post específico"""
    print(f"\n🔍 Testando busca pelo post ID {post_id}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/posts-redes-sociais/{post_id}",
            headers=HEADERS
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            post = response.json()
            print("✅ Post encontrado:")
            print(json.dumps(post, indent=2, ensure_ascii=False))
            return post
        else:
            print(f"❌ Post não encontrado: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao buscar post: {e}")
        return None

def test_update_post(post_id):
    """Testa a atualização de um post"""
    print(f"\n✏️  Testando atualização do post ID {post_id}...")
    
    update_data = {
        "curtidas": 100,
        "comentarios": 15,
        "compartilhamentos": 8
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/posts-redes-sociais/{post_id}",
            headers=HEADERS,
            data=json.dumps(update_data)
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Post atualizado com sucesso!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return response.json()
        else:
            print(f"❌ Erro ao atualizar post: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao atualizar post: {e}")
        return None

def test_delete_post(post_id):
    """Testa a exclusão de um post"""
    print(f"\n🗑️  Testando exclusão do post ID {post_id}...")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/posts-redes-sociais/{post_id}",
            headers=HEADERS
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Post excluído com sucesso!")
            return True
        else:
            print(f"❌ Erro ao excluir post: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao excluir post: {e}")
        return False

def main():
    print("🚀 Iniciando testes da API de Posts de Redes Sociais")
    print("=" * 60)
    
    # Testa o health check
    if not test_health_check():
        print("\n❌ Health check falhou. Verifique se a API está rodando corretamente.")
        return
    
    # Testa a criação de um post
    created_post = test_create_post()
    
    if created_post:
        post_id = created_post["id"]
        
        # Testa a listagem de posts
        test_get_posts()
        
        # Testa a busca por um post específico
        test_get_post(post_id)
        
        # Testa a atualização do post
        test_update_post(post_id)
        
        # Testa a exclusão do post
        test_delete_post(post_id)
        
        # Verifica se o post foi realmente excluído
        test_get_post(post_id)
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()
