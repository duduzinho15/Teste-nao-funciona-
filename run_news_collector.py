# run_news_collector.py
import sys
import os

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Agora importar e executar o coletor
from Coleta_de_dados.apis.news.collector import coletar_noticias_para_todos_clubes

if __name__ == "__main__":
    print("🚀 Iniciando coleta de notícias...")
    resultado = coletar_noticias_para_todos_clubes(limite_por_clube=3)
    
    print("\n" + "="*80)
    print("RESULTADO DA COLETA DE NOTÍCIAS".center(80))
    print("="*80)
    print(f"Status: {resultado['status'].upper()}")
    print(f"Clubes processados: {resultado.get('total_clubes', 0)}")
    print(f"Notícias coletadas: {resultado.get('total_noticias_coletadas', 0)}")
    
    if 'mensagem' in resultado:
        print(f"Mensagem: {resultado['mensagem']}")
    
    print("="*80)
