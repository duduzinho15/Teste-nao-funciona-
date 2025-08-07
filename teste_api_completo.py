"""
TESTE COMPLETO DA API FASTAPI
=============================

Script para testar todos os endpoints da API RESTful do ApostaPro.
Valida autenticação, CRUD operations, filtros e performance.

Uso:
    python teste_api_completo.py

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

import sys
import asyncio
import httpx
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APITester:
    """Classe para testar a API FastAPI."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or "apostapro-api-key-change-in-production"
        self.headers = {"X-API-Key": self.api_key}
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance": {}
        }
    
    async def test_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                          data: Dict = None, description: str = "") -> Dict[str, Any]:
        """
        Testa um endpoint específico.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint a ser testado
            expected_status: Status code esperado
            data: Dados para enviar (POST/PUT)
            description: Descrição do teste
            
        Returns:
            Dict com resultado do teste
        """
        self.results["total_tests"] += 1
        
        url = f"{self.base_url}{endpoint}"
        test_name = f"{method} {endpoint}"
        
        logger.info(f"🧪 Testando: {test_name} - {description}")
        
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # Verificar status code
            if response.status_code == expected_status:
                self.results["passed"] += 1
                status = "✅ PASSOU"
            else:
                self.results["failed"] += 1
                status = "❌ FALHOU"
                self.results["errors"].append({
                    "test": test_name,
                    "expected_status": expected_status,
                    "actual_status": response.status_code,
                    "description": description
                })
            
            # Armazenar performance
            self.results["performance"][test_name] = response_time
            
            result = {
                "test": test_name,
                "description": description,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time_ms": response_time,
                "success": response.status_code == expected_status,
                "response_data": None
            }
            
            # Tentar parsear JSON
            try:
                result["response_data"] = response.json()
            except:
                result["response_data"] = response.text
            
            logger.info(f"   {status} - Status: {response.status_code} - Tempo: {response_time}ms")
            
            return result
            
        except Exception as e:
            self.results["failed"] += 1
            error_msg = f"Erro no teste {test_name}: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            
            self.results["errors"].append({
                "test": test_name,
                "error": str(e),
                "description": description
            })
            
            return {
                "test": test_name,
                "description": description,
                "success": False,
                "error": str(e)
            }
    
    async def test_health_endpoints(self) -> List[Dict]:
        """Testa endpoints de health check."""
        logger.info("\n🏥 TESTANDO ENDPOINTS DE HEALTH")
        logger.info("=" * 40)
        
        tests = []
        
        # Health check básico (sem autenticação)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/", 200,
            description="Health check básico"
        ))
        
        # Health check detalhado
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/detailed", 200,
            description="Health check detalhado"
        ))
        
        # Database health
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/database", 200,
            description="Status do banco de dados"
        ))
        
        # Métricas
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/metrics", 200,
            description="Métricas da API"
        ))
        
        # Ping (sem autenticação)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/ping", 200,
            description="Ping simples"
        ))
        
        # Version (sem autenticação)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/health/version", 200,
            description="Versão da API"
        ))
        
        return tests
    
    async def test_competitions_endpoints(self) -> List[Dict]:
        """Testa endpoints de competições."""
        logger.info("\n🏆 TESTANDO ENDPOINTS DE COMPETIÇÕES")
        logger.info("=" * 40)
        
        tests = []
        
        # Listar competições
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/", 200,
            description="Listar todas as competições"
        ))
        
        # Listar com filtros
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/?page=1&size=10&ativa=true", 200,
            description="Listar competições com filtros"
        ))
        
        # Buscar competição específica (assumindo ID 1 existe)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/1", 200,
            description="Buscar competição por ID"
        ))
        
        # Buscar competição inexistente
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/99999", 404,
            description="Buscar competição inexistente"
        ))
        
        # Estatísticas de competições
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/stats/summary", 200,
            description="Estatísticas de competições"
        ))
        
        # Criar nova competição
        new_competition = {
            "nome": f"Competição Teste API {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "contexto": "Masculino",
            "ativa": True,
            "url": "https://fbref.com/test"
        }
        
        tests.append(await self.test_endpoint(
            "POST", "/api/v1/competitions/", 201,
            data=new_competition,
            description="Criar nova competição"
        ))
        
        return tests
    
    async def test_clubs_endpoints(self) -> List[Dict]:
        """Testa endpoints de clubes."""
        logger.info("\n⚽ TESTANDO ENDPOINTS DE CLUBES")
        logger.info("=" * 40)
        
        tests = []
        
        # Listar clubes
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/clubs/", 200,
            description="Listar todos os clubes"
        ))
        
        # Listar com filtros
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/clubs/?page=1&size=10", 200,
            description="Listar clubes com paginação"
        ))
        
        # Buscar clube específico (assumindo ID 1 existe)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/clubs/1", 200,
            description="Buscar clube por ID"
        ))
        
        # Jogadores do clube
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/clubs/1/players", 200,
            description="Listar jogadores do clube"
        ))
        
        # Estatísticas de clubes
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/clubs/stats/summary", 200,
            description="Estatísticas de clubes"
        ))
        
        # Criar novo clube
        new_club = {
            "nome": f"Clube Teste API {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "pais": "Brasil",
            "url_fbref": "https://fbref.com/test-club"
        }
        
        tests.append(await self.test_endpoint(
            "POST", "/api/v1/clubs/", 201,
            data=new_club,
            description="Criar novo clube"
        ))
        
        return tests
    
    async def test_players_endpoints(self) -> List[Dict]:
        """Testa endpoints de jogadores."""
        logger.info("\n👤 TESTANDO ENDPOINTS DE JOGADORES")
        logger.info("=" * 40)
        
        tests = []
        
        # Listar jogadores
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/", 200,
            description="Listar todos os jogadores"
        ))
        
        # Listar com filtros
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/?page=1&size=10&idade_min=20&idade_max=30", 200,
            description="Listar jogadores com filtros de idade"
        ))
        
        # Buscar jogador específico (assumindo ID 1 existe)
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/1", 200,
            description="Buscar jogador por ID"
        ))
        
        # Buscar por posição
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/search/by-position?posicao=Atacante", 200,
            description="Buscar jogadores por posição"
        ))
        
        # Estatísticas de jogadores
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/stats/summary", 200,
            description="Estatísticas de jogadores"
        ))
        
        # Estatísticas por posição
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/players/stats/positions", 200,
            description="Estatísticas por posição"
        ))
        
        # Criar novo jogador
        new_player = {
            "nome": f"Jogador Teste API {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "posicao": "Atacante",
            "idade": 25,
            "nacionalidade": "Brasil"
        }
        
        tests.append(await self.test_endpoint(
            "POST", "/api/v1/players/", 201,
            data=new_player,
            description="Criar novo jogador"
        ))
        
        return tests
    
    async def test_authentication(self) -> List[Dict]:
        """Testa autenticação da API."""
        logger.info("\n🔐 TESTANDO AUTENTICAÇÃO")
        logger.info("=" * 40)
        
        tests = []
        
        # Teste sem API key
        original_headers = self.headers.copy()
        self.headers = {}
        
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/", 401,
            description="Acesso sem API key (deve falhar)"
        ))
        
        # Teste com API key inválida
        self.headers = {"X-API-Key": "api-key-invalida"}
        
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/", 401,
            description="Acesso com API key inválida (deve falhar)"
        ))
        
        # Restaurar headers válidos
        self.headers = original_headers
        
        tests.append(await self.test_endpoint(
            "GET", "/api/v1/competitions/", 200,
            description="Acesso com API key válida (deve passar)"
        ))
        
        return tests
    
    async def test_root_endpoints(self) -> List[Dict]:
        """Testa endpoints raiz."""
        logger.info("\n🏠 TESTANDO ENDPOINTS RAIZ")
        logger.info("=" * 40)
        
        tests = []
        
        # Endpoint raiz (sem autenticação)
        original_headers = self.headers.copy()
        self.headers = {}
        
        tests.append(await self.test_endpoint(
            "GET", "/", 200,
            description="Endpoint raiz"
        ))
        
        tests.append(await self.test_endpoint(
            "GET", "/api", 200,
            description="Informações da API"
        ))
        
        # Restaurar headers
        self.headers = original_headers
        
        return tests
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes."""
        logger.info("🚀 INICIANDO TESTES COMPLETOS DA API FASTAPI")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Executar todos os grupos de testes
        all_tests = []
        
        all_tests.extend(await self.test_root_endpoints())
        all_tests.extend(await self.test_health_endpoints())
        all_tests.extend(await self.test_authentication())
        all_tests.extend(await self.test_competitions_endpoints())
        all_tests.extend(await self.test_clubs_endpoints())
        all_tests.extend(await self.test_players_endpoints())
        
        total_time = round(time.time() - start_time, 2)
        
        # Gerar relatório final
        logger.info("\n📊 RELATÓRIO FINAL DOS TESTES")
        logger.info("=" * 60)
        logger.info(f"✅ Testes executados: {self.results['total_tests']}")
        logger.info(f"✅ Testes passou: {self.results['passed']}")
        logger.info(f"❌ Testes falharam: {self.results['failed']}")
        logger.info(f"⏱️ Tempo total: {total_time}s")
        
        if self.results['failed'] > 0:
            logger.info(f"\n❌ ERROS ENCONTRADOS ({self.results['failed']}):")
            for error in self.results['errors']:
                logger.error(f"   - {error}")
        
        # Performance
        if self.results['performance']:
            avg_response_time = sum(self.results['performance'].values()) / len(self.results['performance'])
            logger.info(f"\n⚡ PERFORMANCE:")
            logger.info(f"   - Tempo médio de resposta: {avg_response_time:.2f}ms")
            logger.info(f"   - Resposta mais rápida: {min(self.results['performance'].values()):.2f}ms")
            logger.info(f"   - Resposta mais lenta: {max(self.results['performance'].values()):.2f}ms")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        logger.info(f"\n🎯 TAXA DE SUCESSO: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 EXCELENTE! API funcionando perfeitamente!")
        elif success_rate >= 70:
            logger.info("👍 BOM! API funcionando bem com alguns problemas menores")
        else:
            logger.warning("⚠️ ATENÇÃO! API com problemas significativos")
        
        return {
            "summary": self.results,
            "tests": all_tests,
            "total_time": total_time,
            "success_rate": success_rate
        }

async def main():
    """Função principal para executar os testes."""
    # Verificar se a API está rodando
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health/ping")
            if response.status_code != 200:
                logger.error("❌ API não está respondendo. Inicie a API primeiro com: python start_api.py")
                return
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com a API: {e}")
        logger.error("💡 Certifique-se de que a API está rodando: python start_api.py")
        return
    
    # Executar testes
    tester = APITester()
    results = await tester.run_all_tests()
    
    # Salvar relatório
    report_file = f"relatorio_teste_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"\n📄 Relatório salvo em: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
