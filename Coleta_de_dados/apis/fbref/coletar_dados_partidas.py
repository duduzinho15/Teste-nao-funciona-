import logging
import sqlite3
import os
from .fbref_utils import close_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL

# --- CONFIGURAÇÕES COM CAMINHO ABSOLUTO ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logger = logging.getLogger(__name__)


def processar_pagina_temporada(soup, link_coleta_id, cursor):
    """
    Navega para a página de "Scores & Fixtures" correta e extrai os dados das partidas.
    """
    # --- INÍCIO DA CORREÇÃO ---
    # Seletor específico que busca o link de "Scores & Fixtures" dentro do menu de navegação principal da página.
    # Isso evita capturar links de outras competições na barra lateral.
    inner_nav = soup.find('div', id='inner_nav')
    scores_link_tag = None
    if inner_nav:
        scores_link_tag = inner_nav.find('a', href=lambda href: href and '/schedule/' in href)
    
    if not scores_link_tag or not scores_link_tag.get('href'):
        logger.warning("   -> AVISO: Não foi possível encontrar o link contextual para 'Scores & Fixtures'.")
        # Fallback para o método antigo, caso o novo falhe em algum layout
        scores_link_tag = soup.select_one('a[href*="/schedule/"]')
        if not scores_link_tag:
            return False
    
    url_jogos = BASE_URL + scores_link_tag['href']
    logger.info(f"  -> Navegando para a página de jogos correta: {url_jogos}")
    
    soup_jogos = fazer_requisicao(url_jogos)
    if not soup_jogos: return False

    partidas_encontradas = 0
    tabela_jogos = None

    # Lógica de busca hierárquica pela tabela de jogos
    tabelas_candidatas = soup_jogos.select("table[id*='sched_']")
    if tabelas_candidatas:
        tabela_jogos = tabelas_candidatas[0]
        logger.info("  -> Tabela de jogos encontrada pelo ID.")
    elif not tabela_jogos:
        for tabela in extrair_tabelas_da_pagina(soup_jogos):
            caption = tabela.find('caption')
            if caption and "Scores & Fixtures" in caption.text:
                tabela_jogos = tabela
                logger.info("  -> Tabela de jogos encontrada pelo título.")
                break
    
    if tabela_jogos:
        for linha in tabela_jogos.find('tbody').find_all('tr'):
            if 'thead' in linha.get('class', []): continue
            cols = linha.find_all('td')
            if len(cols) > 8:
                match_report_tag = cols[8].find('a', string='Match Report')
                placar = cols[4].text
                if placar and match_report_tag and match_report_tag.get('href'):
                    data, time_casa, time_visitante = cols[0].text, cols[2].text, cols[6].text
                    url_match_report = BASE_URL + match_report_tag['href']
                    cursor.execute(
                        "INSERT OR IGNORE INTO partidas (link_coleta_id, data, time_casa, placar, time_visitante, url_match_report) VALUES (?, ?, ?, ?, ?, ?)",
                        (link_coleta_id, data, time_casa, placar, time_visitante, url_match_report))
                    partidas_encontradas += 1
    
    if partidas_encontradas > 0:
        logger.info(f"  -> {partidas_encontradas} partidas salvas no banco de dados.")
        return True
    else:
        logger.warning("   -> AVISO: Nenhuma partida com 'Match Report' foi encontrada na página de jogos.")
        return False

def main():
    logger.info("🚀 Iniciando Script 2: Coleta de Dados de Partidas...")
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, url FROM links_para_coleta WHERE status_coleta != 'concluido'")
        links_a_processar = cursor.fetchall()
        logger.info(f"Encontrados {len(links_a_processar)} links pendentes ou a revisar para processar.")
        
        for link_id, url in links_a_processar:
            logger.info(f"\n--- Processando link ID {link_id}: {url} ---")
            soup = fazer_requisicao(url)
            if soup:
                status = 'concluido' if processar_pagina_temporada(soup, link_id, cursor) else 'sem_partidas'
                cursor.execute("UPDATE links_para_coleta SET status_coleta = ? WHERE id = ?", (status, link_id))
                conn.commit()
        logger.info("\n✅ Script 2 (Coleta de Partidas) finalizado!")
    finally:
        conn.close(); close_driver()

if __name__ == "__main__":
    main()