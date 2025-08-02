import sys
import os
import logging

# Adiciona o diretório raiz do projeto ao caminho de busca do Python.
# Isso garante que importações como 'from Coleta_de_dados...' funcionem.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# Importa e executa a configuração de logging ANTES de qualquer outra coisa.
from utils.log_utils import setup_logging
setup_logging()

# Agora, importa e executa o orquestrador
from Coleta_de_dados.apis.fbref.orquestrador_coleta import executar_pipeline_completa

if __name__ == "__main__":
    try:
        executar_pipeline_completa()
    except Exception:
        logging.getLogger("run_script").critical("A pipeline falhou de forma inesperada.", exc_info=True)