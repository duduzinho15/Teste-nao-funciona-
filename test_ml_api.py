#!/usr/bin/env python3
"""
Teste da API com Machine Learning integrado
"""
import requests
import json
from datetime import datetime

def test_ml_endpoints():
    """Testa os endpoints de Machine Learning da API"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 TESTANDO ENDPOINTS DE MACHINE LEARNING")
    print("=" * 50)
    
    # Teste 1: Status da API ML
    try:
        print("1️⃣ Testando /ml/status...")
        response = requests.get(f"{base_url}/ml/status")
        if response.status_code == 200:
            print("✅ Status ML: OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Status ML: Erro {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar status ML: {e}")
    
    # Teste 2: Health da API ML
    try:
        print("\n2️⃣ Testando /ml/health...")
        response = requests.get(f"{base_url}/ml/health")
        if response.status_code == 200:
            print("✅ Health ML: OK")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"❌ Health ML: Erro {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar health ML: {e}")
    
    # Teste 3: Análise de sentimento
    try:
        print("\n3️⃣ Testando /ml/sentiment/analyze...")
        text = "Excelente vitória do Flamengo! Gol espetacular!"
        response = requests.post(
            f"{base_url}/ml/sentiment/analyze",
            params={"text": text, "method": "hybrid"}
        )
        if response.status_code == 200:
            print("✅ Análise de sentimento: OK")
            result = response.json()
            print(f"   Sentimento: {result.get('sentiment', 'N/A')}")
            print(f"   Confiança: {result.get('confidence', 'N/A')}")
        else:
            print(f"❌ Análise de sentimento: Erro {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar análise de sentimento: {e}")
    
    # Teste 4: Cache stats
    try:
        print("\n4️⃣ Testando /ml/cache/stats...")
        response = requests.get(f"{base_url}/ml/cache/stats")
        if response.status_code == 200:
            print("✅ Cache stats: OK")
            stats = response.json()
            print(f"   Total de requisições: {stats.get('total_requests', 'N/A')}")
            print(f"   Hit rate: {stats.get('hit_rate', 'N/A')}%")
        else:
            print(f"❌ Cache stats: Erro {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar cache stats: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO!")

def test_api_startup():
    """Testa se a API pode ser iniciada"""
    print("🚀 TESTANDO INICIALIZAÇÃO DA API")
    print("=" * 50)
    
    try:
        # Importar a aplicação
        from api.main import app
        print("✅ Aplicação importada com sucesso")
        
        # Verificar se o router ML está incluído
        ml_routes = [route for route in app.routes if "ml" in str(route)]
        if ml_routes:
            print(f"✅ Router ML encontrado: {len(ml_routes)} rotas")
            for route in ml_routes[:3]:  # Mostrar apenas as primeiras 3
                print(f"   - {route}")
        else:
            print("❌ Router ML não encontrado")
        
        print("✅ API pode ser inicializada")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar API: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 INICIANDO TESTES DA API COM MACHINE LEARNING")
    print("=" * 60)
    
    # Teste 1: Verificar se a API pode ser iniciada
    if test_api_startup():
        print("\n✅ API está funcionando! Agora teste os endpoints...")
        print("💡 Para testar os endpoints, inicie a API com: python -m api.main")
        print("💡 Ou use: uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ API não pode ser inicializada")
    
    print("\n🏁 Testes concluídos!")
