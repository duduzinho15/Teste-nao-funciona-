"""
Script para testar os endpoints da API ApostaPro.
"""
import sys
import requests
import json
from pathlib import Path
from urllib.parse import urljoin

# Configuração
BASE_URL = "http://localhost:8000"  # Porta padrão da API
API_KEY = "change-this-in-production"  # Chave de API do arquivo .env

def print_header(text):
    """Imprime um cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"{text}")
    print("=" * 80)

def test_health_check():
    """Testa o endpoint de health check."""
    print_header("🩺 TESTANDO HEALTH CHECK")
    url = urljoin(BASE_URL, "/api/v1/health")
    
    try:
        response = requests.get(url)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print("Resposta:", json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return False

def test_protected_endpoint(endpoint, method="GET", data=None):
    """Testa um endpoint protegido por API key."""
    url = urljoin(BASE_URL, endpoint)
    headers = {"X-API-Key": API_KEY}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"❌ Método {method} não suportado")
            return False
            
        print(f"\n🔍 {method.upper()} {url}")
        print(f"Status Code: {response.status_code}")
        
        try:
            print("Resposta:", json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print("Resposta:", response.text)
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return False

def main():
    """Função principal."""
    print_header("🔍 TESTANDO ENDPOINTS DA API APOSTAPRO")
    
    # Testa o health check
    if not test_health_check():
        print("\n❌ Falha no teste de health check. Verifique se o servidor está rodando.")
        return
    
    # Lista de endpoints para testar
    endpoints = [
        ("/api/v1/competitions", "GET"),
        ("/api/v1/clubs", "GET"),
        ("/api/v1/players", "GET"),
        ("/api/v1/matches", "GET"),
        ("/api/v1/news", "GET"),
        ("/api/v1/social", "GET"),
    ]
    
    # Testa cada endpoint
    results = []
    for endpoint, method in endpoints:
        success = test_protected_endpoint(endpoint, method)
        results.append((endpoint, method, success))
    
    # Exibe resumo
    print_header("📊 RESUMO DOS TESTES")
    for endpoint, method, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {method} {endpoint}")
    
    # Verifica se todos os testes passaram
    all_passed = all(success for _, _, success in results)
    if all_passed:
        print("\n🎉 Todos os testes passaram com sucesso!")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima para mais detalhes.")

if __name__ == "__main__":
    # Adiciona o diretório raiz ao path do Python
    project_root = str(Path(__file__).parent.absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Tenta obter a chave da API do arquivo .env
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        API_KEY = os.getenv("API_KEY", API_KEY)
    except ImportError:
        print("⚠️  python-dotenv não encontrado. Usando chave padrão.")
    
    main()
    input("\nPressione Enter para sair...")
