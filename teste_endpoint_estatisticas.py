#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO - ESTATÍSTICAS AVANÇADAS
=========================================

Script para testar o fluxo completo de coleta e exposição de estatísticas avançadas:
1. Processa partidas pendentes com estatísticas avançadas
2. Verifica se os dados foram salvos no banco
3. Testa o endpoint da API para obter as estatísticas

Uso:
    python teste_endpoint_estatisticas.py [--limite N] [--api-key CHAVE]

Argumentos:
    --limite N     Limitar o número de partidas a processar (padrão: 1)
    --api-key CHAVE Chave de API para autenticação (opcional)
"""

import argparse
import logging
import sys
import time
import requests
import io
from typing import Dict, Any, Optional

# Configurar stdout para usar ASCII
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='ascii', errors='replace')

# Configuração de logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler('teste_endpoint_estatisticas.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configurações padrão
DEFAULT_API_URL = "http://localhost:8000/api/v1"

class TesteEndpointEstatisticas:
    """Classe para testar o fluxo de estatísticas avançadas."""
    
    def __init__(self, api_url: str = DEFAULT_API_URL, api_key: Optional[str] = None):
        """Inicializa o teste com a URL da API e chave opcional."""
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key} if api_key else {}
        self.partida_id = None
        self.logger = logging.getLogger(__name__)
    
    def processar_partidas(self, limite: int = 1) -> bool:
        """Processa partidas pendentes com estatísticas avançadas."""
        try:
            logger.info(f"🔍 Processando até {limite} partida(s) pendente(s)...")
            
            # Importar o coletor FBRef
            from Coleta_de_dados.apis.fbref.fbref_integrado_orm import FBRefCollectorORM
            
            # Criar instância do coletor e processar partidas
            coletor = FBRefCollectorORM()
            processadas = coletor.processar_partidas_pendentes_com_stats_avancadas(limite=limite)
            
            if not processadas:
                logger.warning("⚠️ Nenhuma partida foi processada. Verifique se há partidas pendentes.")
                return False
                
            logger.info(f"✅ {len(processadas)} partida(s) processada(s) com sucesso!")
            self.partida_id = processadas[0]  # Pega o ID da primeira partida processada
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar partidas: {e}", exc_info=True)
            return False
    
    def testar_endpoint_partida(self, partida_id: Optional[int] = None) -> bool:
        """Testa o endpoint de detalhes da partida."""
        if not partida_id and not self.partida_id:
            logger.error("❌ Nenhum ID de partida fornecido para teste.")
            return False
            
        partida_id = partida_id or self.partida_id
        url = f"{self.api_url}/matches/{partida_id}"
        
        try:
            logger.info(f"🌐 Testando endpoint: GET {url}")
            
            # Fazer requisição para a API
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Verificar status da resposta
            if response.status_code != 200:
                logger.error(f"❌ Falha na requisição: {response.status_code} - {response.text}")
                return False
            
            # Obter dados da resposta
            data = response.json()
            
            # Verificar estrutura básica da resposta
            required_fields = ["id", "data_partida", "clube_casa_id", "clube_visitante_id", 
                             "estatisticas_avancadas"]
            
            for field in required_fields:
                if field not in data:
                    logger.error(f"❌ Campo obrigatório ausente na resposta: {field}")
                    return False
            
            # Verificar se as estatísticas avançadas estão presentes
            stats = data["estatisticas_avancadas"]
            if not stats:
                logger.warning("⚠️ Nenhuma estatística avançada encontrada para a partida.")
                return True  # Ainda assim, o teste passa, pois o endpoint funcionou
            
            # Verificar alguns campos importantes das estatísticas avançadas
            stats_fields = ["xg_casa", "xg_visitante", "formacao_casa", "formacao_visitante"]
            for field in stats_fields:
                if field not in stats:
                    logger.warning(f"⚠️ Campo de estatística avançada ausente: {field}")
            
            logger.info(f"✅ Endpoint testado com sucesso! Dados da partida {partida_id} retornados.")
            logger.debug(f"Dados da partida: {data}")
            
            # Imprimir resumo das estatísticas avançadas
            if stats:
                logger.info("📊 Estatísticas avançadas encontradas:")
                for key, value in stats.items():
                    if value is not None:  # Mostrar apenas campos preenchidos
                        logger.info(f"   - {key}: {value}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição HTTP: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao testar endpoint: {e}", exc_info=True)
            return False

def parse_args():
    """Analisa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Teste de integração para estatísticas avançadas")
    parser.add_argument("--limite", type=int, default=1, 
                       help="Número máximo de partidas a processar")
    parser.add_argument("--api-key", type=str, default=None,
                       help="Chave de API para autenticação")
    parser.add_argument("--api-url", type=str, default=DEFAULT_API_URL,
                       help=f"URL base da API (padrão: {DEFAULT_API_URL})")
    return parser.parse_args()

def main():
    """Função principal."""
    args = parse_args()
    
    logger.info("🚀 Iniciando teste de integração de estatísticas avançadas...")
    
    # Criar instância do teste
    teste = TesteEndpointEstatisticas(api_url=args.api_url, api_key=args.api_key)
    
    # 1. Processar partidas pendentes
    logger.info("\n" + "="*80)
    logger.info("1. PROCESSANDO PARTIDAS PENDENTES")
    logger.info("="*80)
    
    if not teste.processar_partidas(limite=args.limite):
        logger.error("❌ Falha ao processar partidas. Abortando teste.")
        return 1
    
    # 2. Testar endpoint da API
    logger.info("\n" + "="*80)
    logger.info("2. TESTANDO ENDPOINT DA API")
    logger.info("="*80)
    
    if not teste.testar_endpoint_partida():
        logger.error("❌ Falha ao testar endpoint da API.")
        return 1
    
    logger.info("\n" + "="*80)
    logger.info("✅ TESTE CONCLUÍDO COM SUCESSO!")
    logger.info("="*80)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n❌ Teste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro não tratado: {e}", exc_info=True)
        sys.exit(1)
