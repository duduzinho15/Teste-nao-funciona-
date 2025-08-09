#!/usr/bin/env python3
"""
Teste End-to-End da Coleta e Validação Final da API

Este script executa um teste completo do fluxo de coleta de estatísticas avançadas:
1. Processa partidas pendentes usando o coletor FBRef
2. Verifica se os dados foram salvos corretamente no banco
3. Inicia a API e testa o endpoint de partidas
4. Valida a resposta da API

Uso:
    python teste_final_integracao.py [--limite N] [--db-password SENHA] [--no-headless]

Argumentos:
    --limite N         Limitar o número de partidas a processar (padrão: 1)
    --db-password SENHA Senha do banco de dados (opcional, tenta usar .env)
    --no-headless      Executar o navegador em modo visível (para depuração)
"""

import argparse
import os
import sys
import time
import requests
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_integracao.log')
    ]
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações padrão
DEFAULT_DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "apostapro"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}

API_URL = "http://localhost:8000"

# Configurações do Selenium
SELENIUM_HEADLESS = True

class TesteIntegracao:
    def __init__(self, db_config: Dict[str, str], headless: bool = True):
        self.api_process = None
        self.partida_teste = None
        self.db_config = db_config
        self.headless = headless
        
        # Configura variáveis de ambiente para o Selenium
        if not self.headless:
            os.environ["HEADLESS_MODE"] = "false"

    def conectar_banco(self) -> Optional[psycopg2.extensions.connection]:
        """Estabelece conexão com o banco de dados"""
        try:
            # Remove senha vazia para evitar erro de autenticação
            db_config = {k: v for k, v in self.db_config.items() if v is not None and v != ""}
            
            # Log das configurações de conexão (sem a senha por segurança)
            db_config_log = db_config.copy()
            if 'password' in db_config_log:
                db_config_log['password'] = '***'  # Não logar a senha real
            logger.info(f"🔌 Tentando conectar ao banco com configuração: {db_config_log}")
            
            # Tenta conectar com timeout de 5 segundos
            conn = psycopg2.connect(
                host=db_config.get('host'),
                database=db_config.get('database'),
                user=db_config.get('user'),
                password=db_config.get('password'),
                port=db_config.get('port', '5432'),
                connect_timeout=5
            )
            
            # Testa a conexão
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                logger.info(f"✅ Conexão com o banco de dados estabelecida com sucesso!")
                logger.debug(f"Versão do PostgreSQL: {db_version[0]}")
                
            return conn
            
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro operacional ao conectar ao banco: {e}")
            logger.error(f"Verifique se o PostgreSQL está rodando e acessível em {self.db_config.get('host')}:{self.db_config.get('port', '5432')}")
            logger.error(f"Detalhes da conexão: host={self.db_config.get('host')} dbname={self.db_config.get('database')} user={self.db_config.get('user')}")
            return None
            
        except psycopg2.Error as e:
            logger.error(f"❌ Erro do PostgreSQL ao conectar ao banco: {e}")
            logger.error(f"PG Code: {e.pgcode}, PG Error: {e.pgerror}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao conectar ao banco: {e}", exc_info=True)
            return None

    def obter_partida_para_teste(self) -> Optional[Dict[str, Any]]:
        """Obtém uma partida com URL do FBRef para teste"""
        conn = self.conectar_banco()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.url_fbref, c1.nome as time_casa, c2.nome as time_visitante,
                           comp.nome as competicao, p.data_partida
                    FROM partidas p
                    JOIN clubes c1 ON p.clube_casa_id = c1.id
                    JOIN clubes c2 ON p.clube_visitante_id = c2.id
                    JOIN competicoes comp ON p.competicao_id = comp.id
                    WHERE p.url_fbref IS NOT NULL
                    LIMIT 1;
                """)
                
                colunas = [desc[0] for desc in cur.description]
                resultado = cur.fetchone()
                
                if not resultado:
                    logger.error("❌ Nenhuma partida com URL do FBRef encontrada para teste")
                    return None
                
                partida = dict(zip(colunas, resultado))
                logger.info(f"🔍 Partida selecionada para teste: {partida['time_casa']} x {partida['time_visitante']}")
                return partida
                
        except Exception as e:
            logger.error(f"❌ Erro ao buscar partida para teste: {e}")
            return None
        finally:
            conn.close()

    def executar_coleta(self, limite: int = 1) -> bool:
        """
        Executa a coleta de estatísticas avançadas
        
        Args:
            limite: Número máximo de partidas para processar
            
        Returns:
            bool: True se a coleta foi bem-sucedida, False caso contrário
        """
        logger.info(f"🚀 Iniciando coleta de estatísticas avançadas (limite: {limite})...")
        
        try:
            # Adiciona os diretórios necessários ao path para importações
            projeto_root = Path(__file__).parent.absolute()
            sys.path.insert(0, str(projeto_root))
            sys.path.insert(0, str(projeto_root / "Coleta_de_dados"))
            sys.path.insert(0, str(projeto_root / "Coleta_de_dados" / "apis"))
            sys.path.insert(0, str(projeto_root / "Coleta_de_dados" / "apis" / "fbref"))
            
            # Log dos paths para debug
            logger.info(f"📁 Caminhos de importação adicionados:")
            for i, path in enumerate(sys.path[:5], 1):
                logger.info(f"   {i}. {path}")
            
            # Configura o ambiente para o coletor
            os.environ["ENVIRONMENT"] = "test"
            
            # Tenta importar o módulo de coleta
            try:
                logger.info("🔍 Tentando importar FBRefCollectorORM...")
                from Coleta_de_dados.apis.fbref.fbref_integrado import FBRefCollectorORM
                logger.info("✅ Módulo FBRefCollectorORM importado com sucesso via caminho completo")
            except ImportError as e:
                logger.error(f"❌ Erro ao importar módulo de coleta (caminho completo): {e}")
                # Tenta caminho alternativo
                try:
                    logger.info("🔄 Tentando caminho de importação alternativo...")
                    from fbref_integrado import FBRefCollectorORM
                    logger.info("✅ Módulo FBRefCollectorORM importado com sucesso via caminho alternativo")
                except ImportError as e2:
                    logger.error(f"❌ Erro ao importar módulo de coleta (caminho alternativo): {e2}")
                    # Mostra o conteúdo do diretório para debug
                    fbref_dir = projeto_root / "Coleta_de_dados" / "apis" / "fbref"
                    if fbref_dir.exists():
                        logger.info(f"📂 Conteúdo do diretório {fbref_dir}:")
                        for f in fbref_dir.glob("*.py"):
                            logger.info(f"   - {f.name}")
                    else:
                        logger.error(f"❌ Diretório não encontrado: {fbref_dir}")
                    return False
            
            try:
                # Cria e executa o coletor
                logger.info("🚀 Inicializando FBRefCollectorORM...")
                coletor = FBRefCollectorORM()
                
                # Executa a coleta para o número especificado de partidas
                logger.info(f"🔍 Iniciando coleta para até {limite} partida(s)...")
                resultado = coletor.processar_partidas_pendentes_com_stats_avancadas(limite=limite)
                
                if resultado and resultado.get("partidas_processadas", 0) > 0:
                    logger.info(f"✅ Coleta concluída com sucesso: {resultado}")
                    return True
                else:
                    logger.warning(f"⚠️ Nenhuma partida foi processada. Resultado: {resultado}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Erro durante a execução da coleta: {e}", exc_info=True)
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro inesperado durante a coleta: {e}", exc_info=True)
            return False

    def verificar_dados_banco(self, partida_id: int) -> bool:
        """Verifica se os dados avançados foram salvos no banco"""
        logger.info("🔍 Verificando dados no banco...")
        
        conn = self.conectar_banco()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cur:
                # Verifica estatísticas da partida
                cur.execute("""
                    SELECT xg_casa, xg_visitante, formacao_casa, formacao_visitante
                    FROM estatisticas_partidas
                    WHERE partida_id = %s;
                """, (partida_id,))
                
                stats = cur.fetchone()
                if not stats:
                    logger.error("❌ Nenhum dado de estatística encontrado para a partida")
                    return False
                
                # Verifica se os campos obrigatórios foram preenchidos
                xg_casa, xg_visitante, formacao_casa, formacao_visitante = stats
                
                if xg_casa is None or xg_visitante is None:
                    logger.error("❌ Valores de xG não foram preenchidos")
                    return False
                    
                if not formacao_casa or not formacao_visitante:
                    logger.error("❌ Formações das equipes não foram preenchidas")
                    return False
                
                logger.info(f"✅ Dados encontrados no banco:")
                logger.info(f"   - xG Casa: {xg_casa}")
                logger.info(f"   - xG Visitante: {xg_visitante}")
                logger.info(f"   - Formação Casa: {formacao_casa}")
                logger.info(f"   - Formação Visitante: {formacao_visitante}")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar dados no banco: {e}")
            return False
        finally:
            conn.close()

    def iniciar_api(self):
        """Inicia o servidor da API em um processo separado"""
        logger.info("🚀 Iniciando servidor da API...")
        
        try:
            self.api_process = subprocess.Popen(
                [sys.executable, "start_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguarda a API iniciar
            time.sleep(5)
            logger.info("✅ Servidor da API iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar a API: {e}")
            return False

    def testar_endpoint_partida(self, partida_id: int) -> bool:
        """Testa o endpoint de detalhes da partida"""
        logger.info(f"🔍 Testando endpoint da API para partida ID: {partida_id}...")
        
        try:
            response = requests.get(f"{API_URL}/partidas/{partida_id}")
            response.raise_for_status()
            
            data = response.json()
            
            # Verifica se os campos de estatísticas avançadas estão presentes
            if "estatisticas_avancadas" not in data:
                logger.error("❌ Campo 'estatisticas_avancadas' não encontrado na resposta")
                return False
                
            stats = data["estatisticas_avancadas"]
            campos_obrigatorios = [
                "xg_casa", "xg_visitante", 
                "formacao_casa", "formacao_visitante"
            ]
            
            for campo in campos_obrigatorios:
                if campo not in stats:
                    logger.error(f"❌ Campo obrigatório faltando: {campo}")
                    return False
            
            logger.info("✅ Resposta da API válida. Campos encontrados:")
            for campo, valor in stats.items():
                logger.info(f"   - {campo}: {valor}")
                
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro na requisição HTTP: {e}")
            return False
        except ValueError as e:
            logger.error(f"❌ Erro ao decodificar JSON da resposta: {e}")
            return False

    def encerrar_api(self):
        """Encerra o processo da API"""
        if self.api_process:
            logger.info("🛑 Encerrando servidor da API...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
            logger.info("✅ Servidor da API encerrado")

    def executar_teste(self, limite_partidas: int = 1) -> bool:
        """
        Executa o teste end-to-end completo
        
        Args:
            limite_partidas: Número máximo de partidas para processar
            
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO TESTE DE INTEGRAÇÃO END-TO-END")
        logger.info("=" * 60)
        
        # Verifica a conexão com o banco de dados primeiro
        conn = self.conectar_banco()
        if not conn:
            logger.error("❌ Falha na conexão com o banco de dados. Verifique as credenciais.")
            return False
        conn.close()
        
        # 1. Obtém uma partida para teste
        self.partida_teste = self.obter_partida_para_teste()
        if not self.partida_teste:
            logger.error("❌ Não foi possível obter uma partida para teste")
            logger.info("⚠️ Tentando inserir uma partida de teste...")
            
            if not self.criar_partida_teste():
                return False
                
            # Tenta novamente obter uma partida
            self.partida_teste = self.obter_partida_para_teste()
            if not self.partida_teste:
                logger.error("❌ Falha ao criar partida de teste")
                return False
        
        # 2. Executa a coleta de estatísticas avançadas
        if not self.executar_coleta(limite=limite_partidas):
            logger.error("❌ Falha na coleta de estatísticas")
            return False
        
        # 3. Verifica se os dados foram salvos no banco
        if not self.verificar_dados_banco(self.partida_teste['id']):
            logger.error("❌ Dados não foram salvos corretamente no banco")
            return False
        
        # 4. Inicia a API
        if not self.iniciar_api():
            logger.error("❌ Falha ao iniciar a API")
            return False
        
        try:
            # 5. Testa o endpoint da API
            if not self.testar_endpoint_partida(self.partida_teste['id']):
                logger.error("❌ Falha no teste do endpoint da API")
                return False
            
            # Se chegou até aqui, todos os testes passaram
            logger.info("\n" + "=" * 60)
            logger.info("✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
            logger.info("=" * 60)
            return True
            
        finally:
            # 6. Encerra a API
            self.encerrar_api()

def parse_args() -> argparse.Namespace:
    """Analisa os argumentos de linha de comando"""
    parser = argparse.ArgumentParser(description='Executa teste de integração end-to-end')
    parser.add_argument('--limite', type=int, default=1,
                       help='Número máximo de partidas para processar')
    parser.add_argument('--db-password', type=str, default=None,
                       help='Senha do banco de dados')
    parser.add_argument('--no-headless', action='store_true',
                       help='Executar navegador em modo visível')
    return parser.parse_args()

if __name__ == "__main__":
    # Configura o logger para mostrar cores no terminal
    logging.addLevelName(logging.INFO, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
    
    # Analisa argumentos
    args = parse_args()
    
    # Configura o banco de dados
    db_config = DEFAULT_DB_CONFIG.copy()
    if args.db_password:
        db_config["password"] = args.db_password
    
    # Executa o teste
    teste = TesteIntegracao(db_config=db_config, headless=not args.no_headless)
    sucesso = teste.executar_teste(limite_partidas=args.limite)
    
    # Encerra com código de saída apropriado
    sys.exit(0 if sucesso else 1)
