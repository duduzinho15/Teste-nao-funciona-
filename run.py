import sys
import os

# --- INÍCIO DA CORREÇÃO ---
# Adiciona o diretório raiz do projeto ao caminho de busca do Python.
# Isso garante que os módulos em pastas como 'Coleta_de_dados' possam ser encontrados.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)
# --- FIM DA CORREÇÃO ---

# Agora que o Python sabe onde procurar, esta importação funcionará.
from Coleta_de_dados.apis.fbref.orquestrador_coleta import executar_pipeline_completa

if __name__ == "__main__":
    # Chama a função principal da nossa pipeline
    executar_pipeline_completa()