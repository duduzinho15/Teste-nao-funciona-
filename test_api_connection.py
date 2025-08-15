"""
Script para testar a conexão com a API após a correção da codificação do banco de dados.
"""
import os
import sys
import requests
from dotenv import load_dotenv
import json

def test_health_check(base_url):
    """Testa o endpoint de health check da API."""
    print(f"\n🔍 Testando health check em {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao acessar o health check: {e}")
        return False

def test_database_connection(base_url):
    """Testa a conexão com o banco de dados através da API."""
    print(f"\n🔍 Testando conexão com o banco de dados em {base_url}/health/db")
    try:
        response = requests.get(f"{base_url}/health/db", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao testar conexão com o banco de dados: {e}")
        return False

def test_list_tables(base_url):
    """Lista as tabelas disponíveis através da API."""
    print(f"\n📋 Listando tabelas disponíveis em {base_url}/tables")
    try:
        response = requests.get(f"{base_url}/tables", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tables = response.json()
            print("   Tabelas encontradas:")
            for table in tables:
                print(f"   - {table}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return False

def test_sample_data(base_url):
    """Testa a recuperação de dados de exemplo de cada tabela."""
    endpoints = [
        "clubes",
        "competicoes",
        "estadios",
        "paises_clubes",
        "partidas"
    ]
    
    all_success = True
    
    for endpoint in endpoints:
        print(f"\n📊 Testando endpoint /{endpoint}")
        try:
            response = requests.get(f"{base_url}/{endpoint}?limit=3", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total de registros: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"   Amostra: {json.dumps(data[:1] if isinstance(data, list) else data, ensure_ascii=False, indent=2)}")
            else:
                print(f"   Erro: {response.text}")
                all_success = False
                
        except Exception as e:
            print(f"❌ Erro ao acessar /{endpoint}: {e}")
            all_success = False
    
    return all_success

def main():
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Configura a URL base da API
    api_host = os.getenv("API_HOST", "http://localhost")
    api_port = os.getenv("API_PORT", "8000")
    base_url = f"{api_host}:{api_port}"
    
    print("""
    🚀 TESTE DE CONEXÃO COM A API
    ===========================
    Este script irá testar a conexão com a API e verificar se os endpoints
    estão respondendo corretamente após a correção da codificação do banco de dados.
    """)
    
    print(f"\n🔗 Conectando à API em: {base_url}")
    
    # Executa os testes
    tests = [
        ("Health Check", test_health_check, base_url),
        ("Conexão com o Banco de Dados", test_database_connection, base_url),
        ("Listar Tabelas", test_list_tables, base_url),
        ("Dados de Exemplo", test_sample_data, base_url)
    ]
    
    results = []
    
    for name, test_func, *args in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {name.upper()}")
        print(f"{'='*50}")
        success = test_func(*args)
        results.append((name, success))
    
    # Exibe o resumo
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    all_passed = True
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Todos os testes foram concluídos com sucesso!")
        print("   O banco de dados está funcionando corretamente com a codificação UTF-8.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as mensagens de erro acima.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
