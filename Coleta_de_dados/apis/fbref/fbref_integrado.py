import logging
import sqlite3
import os
from bs4 import BeautifulSoup # Importar BeautifulSoup
from .fbref_utils import close_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL

# --- CONFIGURAÇÕES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logger = logging.getLogger(__name__)

def coletar_competicoes():
    """
    Coleta competições extraindo o gênero diretamente da tabela para máxima precisão.
    """
    logger.info("Buscando lista de competições com extração de gênero direta...")
    soup = fazer_requisicao(f"{BASE_URL}/en/comps/")
    if not soup: return []
    
    competicoes = []
    
    # Encontra todas as tabelas de competições na página
    tabelas_competicoes = soup.select("table.stats_table")
    if not tabelas_competicoes:
        logger.error("Nenhuma tabela de competições encontrada na página principal.")
        return []

    for tabela in tabelas_competicoes:
        if tabela.find('tbody'):
            for linha in tabela.find('tbody').find_all('tr'):
                th_cell = linha.find('th', {'data-stat': 'league_name'})
                gender_cell = linha.find('td', {'data-stat': 'gender'})
                
                if th_cell and th_cell.find('a'):
                    link_tag = th_cell.find('a')
                    nome = link_tag.text.strip()
                    url = link_tag.get('href')
                    
                    contexto = "Desconhecido"
                    if gender_cell:
                        if gender_cell.text.strip() == 'M':
                            contexto = "Masculino"
                        elif gender_cell.text.strip() == 'F':
                            contexto = "Feminino"

                    # Resolve a ambiguidade da Serie A
                    if nome == "Serie A" and contexto == "Feminino":
                        nome = "Serie A (W)"
                    
                    if url and ('history' in url or 'tournaments' in url):
                        if not url.startswith('http'):
                            url = BASE_URL + url
                        
                        competicoes.append({'nome': nome, 'contexto': contexto, 'url': url})

    competicoes_unicas = sorted(list({v['url']:v for v in competicoes}.values()), key=lambda x: x['nome'])
    logger.info(f"Encontradas {len(competicoes_unicas)} competições únicas com contexto.")
    return competicoes_unicas

def extrair_links_de_torneios_da_tabela(soup):
    """
    NOVO MÉTODO: Extrai links de temporadas de páginas de torneios que usam uma tabela de histórico.
    Este método foi criado para lidar com o layout de páginas como Copa do Mundo, Olimpíadas, etc.
    """
    links = []
    # A tabela de histórico geralmente é a primeira (ou única) tabela na página de torneios.
    tabela_historico = soup.find('table') 
    
    if tabela_historico and tabela_historico.find('tbody'):
        for linha in tabela_historico.find('tbody').find_all('tr'):
            # O link da temporada/ano está no primeiro cabeçalho (th) de cada linha.
            header = linha.find('th')
            if header and header.find('a'):
                link_relativo = header.find('a')['href']
                links.append(BASE_URL + link_relativo)
    
    return links

def coletar_temporadas_de_competicao(url_competicao):
    """Lógica de extração em múltiplos estágios, aprimorada com base nos HTMLs fornecidos."""
    soup = fazer_requisicao(url_competicao)
    if not soup: return [], "desconhecido"

    links, tipo = [], "NENHUM DADO ENCONTRADO"

    # --- MÉTODO 1: TABELA DE TEMPORADAS (Padrão para Ligas) ---
    tabela_seasons = soup.find('table', id='seasons')
    if tabela_seasons:
        for tag in tabela_seasons.select('th[data-stat="year_id"] a'):
            if tag.get('href'): links.append(BASE_URL + tag['href'])
        if links:
            logger.info(f"  -> {len(links)} links encontrados pelo MÉTODO DE TABELA DE TEMPORADAS.")
            return sorted(list(set(links)), reverse=True), "TEMPORADAS"

    # --- MÉTODO 2: CABEÇALHOS H2 (Padrão para Qualificatórias) ---
    content_div = soup.find('div', id='content')
    if content_div:
        for header in content_div.find_all('h2'):
            link_tag = header.find('a')
            if link_tag and link_tag.get('href') and '/comps/' in link_tag['href']:
                links.append(BASE_URL + link_tag['href'])
    if links:
        logger.info(f"  -> {len(links)} links encontrados pelo MÉTODO DE CABEÇALHOS H2.")
        return sorted(list(set(links)), reverse=True), "TORNEIOS"
    
    # --- MÉTODO 3: TABELA DE HISTÓRICO DE TORNEIOS (Solução para Copas, Olimpíadas, etc.) ---
    links = extrair_links_de_torneios_da_tabela(soup)
    if links:
        logger.info(f"  -> {len(links)} links encontrados pelo NOVO MÉTODO DE TABELA DE HISTÓRICO.")
        return sorted(list(set(links)), reverse=True), "TORNEIOS"
        
    logger.warning("  -> AVISO: Nenhum método de extração encontrou links de temporada válidos.")
    return links, tipo

def main():
    """Orquestra a coleta de links e salva na fila de trabalho do banco de dados."""
    logger.info("🚀 Iniciando Script 1: Descoberta de Links...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        lista_competicoes = coletar_competicoes()
        if not lista_competicoes: 
            logger.warning("Nenhuma competição foi encontrada.")
            return
            
        for i, comp in enumerate(lista_competicoes):
            logger.info(f"\n--- Processando Competição {i+1}/{len(lista_competicoes)}: {comp['nome']} ({comp['contexto']}) ---")
            
            cursor.execute("INSERT OR IGNORE INTO competicoes (nome, contexto, url_historico) VALUES (?, ?, ?)", 
                           (comp['nome'], comp['contexto'], comp['url']))
            cursor.execute("SELECT id FROM competicoes WHERE url_historico = ?", (comp['url'],)); competicao_id = cursor.fetchone()[0]
            
            links, tipo = coletar_temporadas_de_competicao(comp['url'])
            logger.info(f"  -> Encontrados {len(links)} links do tipo {tipo}.")
            
            for link in links:
                cursor.execute("INSERT OR IGNORE INTO links_para_coleta (competicao_id, url, tipo_dado) VALUES (?, ?, ?)",
                               (competicao_id, link, tipo))
            conn.commit()
            
        logger.info("\n✅ Script 1 (Descoberta) finalizado com sucesso!")
    finally:
        conn.close()
        close_driver()

if __name__ == "__main__":
    main()