import os
import sys

# Caminho absoluto até a pasta 'Coleta_de_dados'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Coleta_de_dados')))

from apis import sofascore_scraper

if __name__ == "__main__":
    print("🔎 Iniciando teste de coleta do SofaScore...")
    sofascore_scraper.executar_coleta_sofascore()
    print("✅ Teste finalizado.")
