#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DE INTEGRAÇÃO - ESTATÍSTICAS AVANÇADAS VIA API
==================================================

Script para testar o fluxo completo de coleta e exposição de estatísticas avançadas:
1. Coleta estatísticas avançadas de uma partida
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
from typing import Dict, List, Optional, Tuple, Any
import requests
from requests.exceptions import RequestException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_integracao_estatisticas_avancadas.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class TesteIntegracaoEstatisticasAvancadas:
    """Classe para testar a integração de estatísticas avançadas com a API."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        self.api_process = None
        self.api_url = "http://localhost:8000"
        
    def setup_database(self) -> bool:
        """Configura a conexão com o banco de dados."""
        try:
            self.logger.info("🔍 Configurando conexão com o banco de dados...")
            
            # Configuração do banco de dados (ajuste conforme necessário)
            db_url = os.getenv('DATABASE_URL', 'postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db')
            self.logger.info(f"Conectando ao banco de dados: {db_url}")
            
            # Criar engine com configurações básicas
            self.engine = create_engine(db_url, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine)
            
            # Testar conexão
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.logger.info("✅ Conexão com o banco de dados bem-sucedida")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Falha na conexão com o banco de dados: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def obter_partida_teste(self) -> Optional[Dict]:
        """Obtém uma partida para teste com estatísticas avançadas."""
        try:
            session = self.Session()
            
            # Buscar partida com estatísticas avançadas
            query = text("""
                SELECT p.id, p.url_fbref, 
                       ep.xg_casa, ep.xg_visitante, 
                       ep.formacao_casa, ep.formacao_visitante
                FROM partidas p
                JOIN estatisticas_partidas ep ON p.id = ep.partida_id
                WHERE ep.xg_casa IS NOT NULL 
                AND ep.xg_visitante IS NOT NULL
                AND ep.formacao_casa IS NOT NULL
                AND ep.formacao_visitante IS NOT NULL
                LIMIT 1
            """)
            result = session.execute(query).fetchone()
            
            if not result:
                self.logger.warning("Nenhuma partida com estatísticas avançadas encontrada")
                return None
                
            partida = {
                'id': result[0],
                'url': result[1],
                'xg_casa': float(result[2]) if result[2] is not None else None,
                'xg_visitante': float(result[3]) if result[3] is not None else None,
                'formacao_casa': result[4],
                'formacao_visitante': result[5]
            }
            
            self.logger.info(f"Partida de teste selecionada: ID {partida['id']}")
            return partida
            
        except Exception as e:
            self.logger.error(f"Erro ao obter partida para teste: {e}")
            self.logger.error(traceback.format_exc())
            return None
            
        finally:
            if 'session' in locals():
                session.close()
    
    def iniciar_api(self) -> bool:
        """Inicia a API localmente em um processo separado."""
        try:
            self.logger.info("🚀 Iniciando API localmente...")
            
            # Comando para iniciar a API
            cmd = [sys.executable, "start_api.py"]
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Dar um tempo para a API iniciar
            time.sleep(5)
            
            # Verificar se a API está respondendo
            try:
                response = requests.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    self.logger.info("✅ API iniciada com sucesso")
                    return True
            except RequestException:
                pass
                
            self.logger.error("❌ Falha ao iniciar a API")
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar a API: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def parar_api(self) -> None:
        """Para o processo da API."""
        if self.api_process:
            self.logger.info("🛑 Parando API...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
            self.api_process = None
    
    def testar_endpoint_partida(self, partida_id: int) -> Tuple[bool, Dict]:
        """Testa o endpoint de partida para validar as estatísticas avançadas."""
        try:
            url = f"{self.api_url}/api/partidas/{partida_id}"
            self.logger.info(f"🔍 Testando endpoint: {url}")
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar se o campo estatisticas_avancadas existe
            if 'estatisticas_avancadas' not in data:
                self.logger.error("❌ Campo 'estatisticas_avancadas' não encontrado na resposta")
                return False, {}
                
            estatisticas = data['estatisticas_avancadas']
            
            # Verificar campos obrigatórios
            campos_obrigatorios = [
                'xg_casa', 'xg_visitante',
                'formacao_casa', 'formacao_visitante'
            ]
            
            faltando = [campo for campo in campos_obrigatorios if campo not in estatisticas]
            if faltando:
                self.logger.error(f"❌ Campos obrigatórios faltando: {', '.join(faltando)}")
                return False, estatisticas
                
            self.logger.info("✅ Formato da resposta válido")
            return True, estatisticas
            
        except RequestException as e:
            self.logger.error(f"❌ Erro na requisição HTTP: {e}")
            return False, {}
        except Exception as e:
            self.logger.error(f"❌ Erro ao testar endpoint: {e}")
            self.logger.error(traceback.format_exc())
            return False, {}
    
    def validar_dados(self, estatisticas_api: Dict, partida: Dict) -> bool:
        """Valida se os dados da API correspondem aos dados do banco."""
        try:
            self.logger.info("🔍 Validando dados da API...")
            
            # Mapear campos para validação
            campos_validacao = [
                ('xg_casa', 'xg_casa'),
                ('xg_visitante', 'xg_visitante'),
                ('formacao_casa', 'formacao_casa'),
                ('formacao_visitante', 'formacao_visitante')
            ]
            
            validacao_ok = True
            
            for campo_api, campo_banco in campos_validacao:
                valor_api = estatisticas_api.get(campo_api)
                valor_banco = partida.get(campo_banco)
                
                # Converter para o mesmo tipo para comparação
                if isinstance(valor_banco, float):
                    valor_api = float(valor_api) if valor_api is not None else None
                
                if valor_api != valor_banco:
                    self.logger.warning(
                        f"⚠️ Valor diferente para {campo_api}: "
                        f"API={valor_api} | BANCO={valor_banco}"
                    )
                    validacao_ok = False
                else:
                    self.logger.info(f"✅ {campo_api}: {valor_api}")
            
            return validacao_ok
            
        except Exception as e:
            self.logger.error(f"❌ Erro na validação dos dados: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def executar_testes(self) -> bool:
        """Executa todos os testes de integração."""
        self.logger.info("="*50)
        self.logger.info("🚀 INÍCIO DOS TESTES DE INTEGRAÇÃO")
        self.logger.info("="*50)
        
        try:
            # Configurar banco de dados
            if not self.setup_database():
                self.logger.error("❌ Teste abortado: falha na configuração do banco de dados")
                return False
            
            # Obter partida para teste
            partida = self.obter_partida_teste()
            if not partida:
                self.logger.error("❌ Nenhuma partida com estatísticas avançadas disponível para teste")
                return False
            
            # Iniciar API
            if not self.iniciar_api():
                self.logger.error("❌ Teste abortado: falha ao iniciar a API")
                return False
            
            try:
                # Testar endpoint da partida
                sucesso, estatisticas_api = self.testar_endpoint_partida(partida['id'])
                
                if not sucesso:
                    self.logger.error("❌ Falha ao testar endpoint da partida")
                    return False
                
                # Validar dados
                if not self.validar_dados(estatisticas_api, partida):
                    self.logger.error("❌ Falha na validação dos dados")
                    return False
                
                self.logger.info("✅ Todos os testes passaram com sucesso!")
                return True
                
            finally:
                # Garantir que a API seja parada
                self.parar_api()
                
        except Exception as e:
            self.logger.error(f"❌ Erro durante a execução dos testes: {e}")
            self.logger.error(traceback.format_exc())
            return False
        
        finally:
            self.logger.info("="*50)
            self.logger.info("🏁 FIM DOS TESTES DE INTEGRAÇÃO")
            self.logger.info("="*50)

def main() -> int:
    """Função principal."""
    tester = TesteIntegracaoEstatisticasAvancadas()
    return 0 if tester.executar_testes() else 1

if __name__ == "__main__":
    sys.exit(main())
