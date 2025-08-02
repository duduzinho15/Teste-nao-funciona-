import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configura um sistema de log centralizado que salva todas as mensagens
    em um arquivo e também as exibe no terminal.
    """
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"pipeline_run_{timestamp}.log")

    # Configura o logger principal (root logger).
    # Qualquer script que usar 'import logging' usará esta configuração.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    # Cria um logger específico para este módulo para evitar confusão
    logger = logging.getLogger(__name__)
    logger.info(f"Sistema de log configurado. A saída será salva em: {log_file}")

def registrar_log(nome_logger, mensagem):
    """Registra uma mensagem de informação."""
    logging.getLogger(nome_logger).info(mensagem)

def registrar_erro(nome_logger, mensagem, exc_info=False):
    """Registra uma mensagem de erro."""
    logging.getLogger(nome_logger).error(mensagem, exc_info=exc_info)