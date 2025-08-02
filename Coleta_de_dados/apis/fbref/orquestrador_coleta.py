import logging
import time
import sys
import os

# Garante que o diretório raiz esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# Importações agora funcionam porque o run.py ajustou o path
from Banco_de_dados.criar_banco import criar_todas_as_tabelas
from Coleta_de_dados.apis.fbref.fbref_integrado import main as descobrir_links
from Coleta_de_dados.apis.fbref.coletar_dados_partidas import main as coletar_partidas
from Coleta_de_dados.apis.fbref.coletar_estatisticas_detalhadas import main as coletar_estatisticas
from Coleta_de_dados.apis.fbref.fbref_criar_tabela_rotulada import main as processar_dados
from Coleta_de_dados.apis.fbref.gerar_relatorio_final import main as gerar_relatorio

# Pega o logger já configurado pelo run.py
logger = logging.getLogger(__name__)

def executar_pipeline_completa():
    """Executa todos os scripts da pipeline de dados em sequência."""
    start_time = time.time()
    logger.info("🚀🚀🚀 INICIANDO A PIPELINE COMPLETA DE DADOS DO FBREF 🚀🚀🚀")

    try:
        # Etapa 0: Preparação do Banco de Dados
        logger.info("\n--- [ETAPA 0 de 6] Executando: Preparação do Banco de Dados ---")
        criar_todas_as_tabelas()
        logger.info("--- [ETAPA 0 de 6] Finalizada com sucesso! ---")
        
        # Etapa 1: Descoberta de Links
        logger.info("\n--- [ETAPA 1 de 6] Executando: Descoberta de Competições e Temporadas ---")
        descobrir_links()
        logger.info("--- [ETAPA 1 de 6] Finalizada com sucesso! ---")

        # --- ETAPA 2: Coleta de Dados de Partidas ---
        logging.info("\n--- [ETAPA 2 de 6] Executando: Coleta de Dados de Partidas ---")
        coletar_partidas()
        logging.info("--- [ETAPA 2 de 6] Finalizada com sucesso! ---")

        # --- ETAPA 3: Coleta de Estatísticas Detalhadas ---
        logging.info("\n--- [ETAPA 3 de 6] Executando: Coleta de Estatísticas Detalhadas ---")
        coletar_estatisticas()
        logging.info("--- [ETAPA 3 de 6] Finalizada com sucesso! ---")
        
        # --- ETAPA 4: Processamento e Rotulação dos Dados ---
        logging.info("\n--- [ETAPA 4 de 6] Executando: Processamento e Rotulação dos Dados para IA ---")
        processar_dados()
        logging.info("--- [ETAPA 4 de 6] Finalizada com sucesso! ---")
        
        # --- ETAPA 5: Geração do Relatório Final ---
        logging.info("\n--- [ETAPA 5 de 6] Executando: Geração do Relatório Final de Coleta ---")
        gerar_relatorio()
        logging.info("--- [ETAPA 5 de 6] Finalizada com sucesso! ---")

        # --- ETAPA 6: Finalização da Pipeline ---
        logger.info("\n--- [ETAPA 6 de 6] Finalizando a Pipeline ---")
    except Exception as e:
        logger.critical(f"🚨🚨🚨 ERRO CRÍTICO NA PIPELINE! 🚨🚨🚨", exc_info=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"\n✅✅✅ PIPELINE COMPLETA FINALIZADA! ✅✅✅")
    logger.info(f"Tempo total de execução: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")

if __name__ == "__main__":
    executar_pipeline_completa()