import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import traceback

# Configurações globais
LOG_DIR = "logs"
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Garante que o diretório de logs existe
Path(LOG_DIR).mkdir(exist_ok=True)

def setup_logging(
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    log_filename: Optional[str] = None
) -> str:
    """
    Configura o sistema de logging para todo o projeto.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Se deve exibir logs no console
        file_output: Se deve salvar logs em arquivo
        log_filename: Nome específico do arquivo de log (opcional)
        
    Returns:
        str: Caminho do arquivo de log criado
    """
    # Converte string para nível de logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Cria nome do arquivo de log se não fornecido
    if not log_filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"pipeline_run_{timestamp}.log"
    
    log_filepath = os.path.join(LOG_DIR, log_filename)
    
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura formatador
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Lista de handlers
    handlers = []
    
    # Handler para arquivo
    if file_output:
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)
    
    # Handler para console
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        handlers.append(console_handler)
    
    # Configura logging básico
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        force=True  # Força reconfiguração
    )
    
    # Log inicial
    logger = logging.getLogger("utils.log_utils")
    logger.info(f"Sistema de log configurado. A saída será salva em: {log_filepath}")
    
    return log_filepath

def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado para um módulo específico.
    
    Args:
        name: Nome do módulo/classe
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)

def registrar_log(modulo: str, mensagem: str, nivel: str = "INFO") -> None:
    """
    Registra uma mensagem de log de forma padronizada.
    
    Args:
        modulo: Nome do módulo que está logando
        mensagem: Mensagem a ser registrada
        nivel: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger(modulo)
    numeric_level = getattr(logging, nivel.upper(), logging.INFO)
    logger.log(numeric_level, mensagem)

def registrar_erro(modulo: str, mensagem: str, excecao: Optional[Exception] = None) -> None:
    """
    Registra um erro de forma padronizada.
    
    Args:
        modulo: Nome do módulo onde ocorreu o erro
        mensagem: Descrição do erro
        excecao: Exceção capturada (opcional)
    """
    logger = get_logger(modulo)
    
    if excecao:
        logger.error(f"{mensagem}: {str(excecao)}")
        logger.debug(f"Traceback completo:\n{traceback.format_exc()}")
    else:
        logger.error(mensagem)

def registrar_inicio_etapa(modulo: str, etapa: str, detalhes: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra o início de uma etapa do pipeline.
    
    Args:
        modulo: Nome do módulo
        etapa: Nome da etapa
        detalhes: Informações adicionais da etapa
    """
    logger = get_logger(modulo)
    mensagem = f"🚀 Iniciando etapa: {etapa}"
    
    if detalhes:
        mensagem += f" | Detalhes: {json.dumps(detalhes, ensure_ascii=False)}"
    
    logger.info(mensagem)

def registrar_fim_etapa(modulo: str, etapa: str, sucesso: bool = True, 
                       estatisticas: Optional[Dict[str, Any]] = None) -> None:
    """
    Registra o fim de uma etapa do pipeline.
    
    Args:
        modulo: Nome do módulo
        etapa: Nome da etapa
        sucesso: Se a etapa foi bem-sucedida
        estatisticas: Estatísticas da execução
    """
    logger = get_logger(modulo)
    
    if sucesso:
        mensagem = f"✅ Etapa finalizada com sucesso: {etapa}"
    else:
        mensagem = f"❌ Etapa finalizada com erro: {etapa}"
    
    if estatisticas:
        mensagem += f" | Estatísticas: {json.dumps(estatisticas, ensure_ascii=False)}"
    
    logger.info(mensagem)

def registrar_progresso(modulo: str, atual: int, total: int, item_atual: str = "") -> None:
    """
    Registra progresso de uma operação.
    
    Args:
        modulo: Nome do módulo
        atual: Número atual de itens processados
        total: Total de itens a processar
        item_atual: Descrição do item atual sendo processado
    """
    logger = get_logger(modulo)
    percentual = (atual / total * 100) if total > 0 else 0
    
    mensagem = f"📈 Progresso: {atual}/{total} ({percentual:.1f}%)"
    
    if item_atual:
        mensagem += f" | Processando: {item_atual}"
    
    logger.info(mensagem)

def criar_arquivo_erro_detalhado(erro: Exception, contexto: Dict[str, Any]) -> str:
    """
    Cria um arquivo detalhado com informações do erro para debug.
    
    Args:
        erro: Exceção capturada
        contexto: Informações contextuais do erro
        
    Returns:
        str: Caminho do arquivo criado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    erro_filename = f"erro_detalhado_{timestamp}.json"
    erro_filepath = os.path.join(LOG_DIR, erro_filename)
    
    erro_info = {
        "timestamp": datetime.now().isoformat(),
        "tipo_erro": type(erro).__name__,
        "mensagem_erro": str(erro),
        "traceback": traceback.format_exc(),
        "contexto": contexto
    }
    
    try:
        with open(erro_filepath, 'w', encoding='utf-8') as f:
            json.dump(erro_info, f, indent=2, ensure_ascii=False, default=str)
        
        logger = get_logger("utils.log_utils")
        logger.error(f"Arquivo de erro detalhado criado: {erro_filepath}")
        
        return erro_filepath
        
    except Exception as e:
        logger = get_logger("utils.log_utils")
        logger.error(f"Falha ao criar arquivo de erro detalhado: {e}")
        return ""

def configurar_logger_modulo(nome_modulo: str, nivel: str = "INFO") -> logging.Logger:
    """
    Configura um logger específico para um módulo.
    
    Args:
        nome_modulo: Nome do módulo
        nivel: Nível de log específico para este módulo
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(nome_modulo)
    logger.setLevel(getattr(logging, nivel.upper(), logging.INFO))
    
    return logger

def listar_logs_disponiveis() -> list[str]:
    """
    Lista todos os arquivos de log disponíveis.
    
    Returns:
        list[str]: Lista de arquivos de log
    """
    try:
        log_path = Path(LOG_DIR)
        return [f.name for f in log_path.glob("*.log")]
    except Exception:
        return []

def limpar_logs_antigos(dias: int = 7) -> None:
    """
    Remove logs antigos para evitar acúmulo de arquivos.
    
    Args:
        dias: Número de dias para manter os logs
    """
    try:
        from datetime import timedelta
        
        log_path = Path(LOG_DIR)
        limite_data = datetime.now() - timedelta(days=dias)
        
        logs_removidos = 0
        for arquivo in log_path.glob("*.log"):
            if arquivo.stat().st_mtime < limite_data.timestamp():
                arquivo.unlink()
                logs_removidos += 1
        
        if logs_removidos > 0:
            logger = get_logger("utils.log_utils")
            logger.info(f"Removidos {logs_removidos} arquivos de log antigos")
            
    except Exception as e:
        logger = get_logger("utils.log_utils")
        logger.warning(f"Erro ao limpar logs antigos: {e}")

class LogContextManager:
    """Context manager para logging de operações com tempo de execução."""
    
    def __init__(self, modulo: str, operacao: str, nivel: str = "INFO"):
        self.logger = get_logger(modulo)
        self.operacao = operacao
        self.nivel = getattr(logging, nivel.upper(), logging.INFO)
        self.inicio = None
    
    def __enter__(self):
        self.inicio = datetime.now()
        self.logger.log(self.nivel, f"🔄 Iniciando: {self.operacao}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duracao = datetime.now() - self.inicio
        
        if exc_type is None:
            self.logger.log(self.nivel, f"✅ Concluído: {self.operacao} (duração: {duracao})")
        else:
            self.logger.error(f"❌ Falhou: {self.operacao} (duração: {duracao})")
            self.logger.error(f"Erro: {exc_val}")
        
        return False  # Não suprimir exceções

# Configuração inicial automática quando o módulo é importado
if not logging.getLogger().handlers:
    setup_logging()