import logging
import time
import sys
import os

# Garante que o diretório raiz esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# Importa a função 'main' ou equivalente de cada script
from Banco_de_dados.criar_banco import criar_todas_as_tabelas
from .fbref_integrado import main as descobrir_links
from .coletar_dados_partidas import main as coletar_partidas
from .coletar_estatisticas_detalhadas import main as coletar_estatisticas
from .fbref_criar_tabela_rotulada import main as processar_dados
from .gerar_relatorio_final import main as gerar_relatorio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - ORQUESTRADOR - %(message)s')

def executar_pipeline_completa():
    """Executa todos os scripts da pipeline de dados em sequência."""
    start_time = time.time()
    logging.info("🚀🚀🚀 INICIANDO A PIPELINE COMPLETA DE DADOS DO FBREF 🚀🚀🚀")

    try:
        # --- ETAPA 0: Preparação do Banco de Dados ---
        logging.info("\n--- [ETAPA 0 de 6] Executando: Preparação do Banco de Dados ---")
        criar_todas_as_tabelas()
        logging.info("--- [ETAPA 0 de 6] Finalizada com sucesso! ---")
        
        # --- ETAPA 1: Descoberta de Links ---
        logging.info("\n--- [ETAPA 1 de 6] Executando: Descoberta de Competições e Temporadas ---")
        descobrir_links()
        logging.info("--- [ETAPA 1 de 6] Finalizada com sucesso! ---")

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

    except Exception as e:
        logging.error(f"🚨🚨🚨 ERRO CRÍTICO NA PIPELINE! 🚨🚨🚨", exc_info=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    logging.info(f"\n✅✅✅ PIPELINE COMPLETA FINALIZADA! ✅✅✅")
    logging.info(f"Tempo total de execução: {time.strftime('%H:%M:%S', time.gmtime(total_time))}")

if __name__ == "__main__":
    executar_pipeline_completa()