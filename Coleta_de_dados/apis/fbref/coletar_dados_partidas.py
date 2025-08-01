import logging
import sqlite3
import os
from .fbref_utils import close_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL

# --- CONFIGURAÇÕES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def processar_pagina_temporada(soup, link_coleta_id, cursor):
    """
    Extrai os dados de partidas de uma página de temporada/torneio usando uma busca hierárquica.
    """
    tabela_jogos = None
    partidas_encontradas = 0

    # --- INÍCIO DA CORREÇÃO: Lógica de Busca Hierárquica ---

    # Método 1: Tenta encontrar a tabela pelo ID mais comum ("sched_...")
    tabelas_candidatas = soup.select("table[id*='sched_']")
    if tabelas_candidatas:
        tabela_jogos = tabelas_candidatas[0]
        logging.info("  -> Tabela de jogos encontrada pelo ID 'sched_'.")

    # Método 2: Se o primeiro falhar, busca pela tabela com o título "Scores & Fixtures"
    if not tabela_jogos:
        for tabela in extrair_tabelas_da_pagina(soup):
            caption = tabela.find('caption')
            if caption and "Scores & Fixtures" in caption.text:
                tabela_jogos = tabela
                logging.info("  -> Tabela de jogos encontrada pelo título 'Scores & Fixtures'.")
                break
    
    # --- FIM DA CORREÇÃO ---

    if tabela_jogos:
        logging.info("  -> Extraindo partidas da tabela encontrada...")
        for linha in tabela_jogos.find('tbody').find_all('tr'):
            if 'thead' in linha.get('class', []): continue

            cols = linha.find_all('td')
            if len(cols) > 8:
                match_report_tag = cols[8].find('a', string='Match Report')
                if match_report_tag and match_report_tag.get('href'):
                    placar = cols[4].text
                    if placar: # Apenas processa jogos que já ocorreram (têm placar)
                        data = cols[0].text
                        time_casa = cols[2].text
                        time_visitante = cols[6].text
                        url_match_report = BASE_URL + match_report_tag['href']
                        
                        cursor.execute(
                            "INSERT OR IGNORE INTO partidas (link_coleta_id, data, time_casa, placar, time_visitante, url_match_report) VALUES (?, ?, ?, ?, ?, ?)",
                            (link_coleta_id, data, time_casa, placar, time_visitante, url_match_report)
                        )
                        partidas_encontradas += 1
    
    if partidas_encontradas > 0:
        logging.info(f"  -> {partidas_encontradas} partidas salvas no banco de dados.")
        return True
    else:
        logging.warning("   -> AVISO: Nenhuma tabela de jogos válida foi encontrada nesta página.")
        return False

def main():
    """Lê a fila de trabalho e coleta os dados das partidas."""
    logging.info("🚀 Iniciando Script 2: Coleta de Dados de Partidas...")
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, url FROM links_para_coleta WHERE status_coleta != 'concluido'")
        links_a_processar = cursor.fetchall()
        logging.info(f"Encontrados {len(links_a_processar)} links pendentes ou a revisar para processar.")
        
        for link_id, url in links_a_processar:
            logging.info(f"\n--- Processando link ID {link_id}: {url} ---")
            soup = fazer_requisicao(url)
            if soup:
                status = 'concluido' if processar_pagina_temporada(soup, link_id, cursor) else 'sem_partidas'
                cursor.execute("UPDATE links_para_coleta SET status_coleta = ? WHERE id = ?", (status, link_id))
                conn.commit()
        logging.info("\n✅ Script 2 (Coleta de Partidas) finalizado!")
    finally:
        conn.close(); close_driver()

if __name__ == "__main__":
    main()