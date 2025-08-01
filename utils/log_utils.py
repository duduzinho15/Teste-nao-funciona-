# log_utils.py

import os
from datetime import datetime

def get_log_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    return {
        "info": os.path.join(log_dir, 'coleta.log'),
        "erro": os.path.join(log_dir, 'erros.log')
    }

def registrar_log(fonte, mensagem):
    caminhos = get_log_paths()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entrada = f"[{agora}] [{fonte}] {mensagem}\n"
    
    with open(caminhos["info"], 'a', encoding='utf-8') as f:
        f.write(entrada)

def registrar_erro(fonte, mensagem, excecao=None):
    caminhos = get_log_paths()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    erro_msg = f"[{agora}] [{fonte}] ERRO: {mensagem}"
    
    if excecao:
        erro_msg += f" | Exceção: {str(excecao)}"
    erro_msg += "\n"

    with open(caminhos["erro"], 'a', encoding='utf-8') as f:
        f.write(erro_msg)
