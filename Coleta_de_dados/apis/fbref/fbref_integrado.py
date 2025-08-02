import logging
import sqlite3
import os
from .fbref_utils import close_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL

# --- CONFIGURAÇÕES GERAIS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

def coletar_competicoes():
    """
    Coleta competições de forma robusta, usando os cabeçalhos H2 como âncora para
    determinar o contexto (Masculino/Feminino) e resolver ambiguidades.
    """
    logging.info("Buscando lista de competições com reconhecimento de contexto aprimorado...")
    url_principal = f"{BASE_URL}/en/comps/"
    soup = fazer_requisicao(url_principal)
    if not soup: return []
    
    competicoes = []
    # A âncora principal para a busca é a div de conteúdo principal
    content_div = soup.find('div', id='content')
    if not content_div:
        logging.error("Div de conteúdo principal ('#content') não encontrada. Não é possível continuar.")
        return []

    # Encontra todos os cabeçalhos de seção (H2)
    for header in content_div.find_all('h2'):
        contexto = "Desconhecido"
        header_text = header.get_text().lower()
        if "men's" in header_text:
            contexto = "Masculino"
        elif "women's" in header_text:
            contexto = "Feminino"

        # Encontra a próxima tabela de dados que segue o cabeçalho
        tabela = header.find_next('table')
        if tabela and tabela.find('tbody'):
            for linha in tabela.find_all('tr'):
                th_cell = linha.find('th')
                if th_cell:
                    link_tag = th_cell.find('a')
                    if link_tag and link_tag.get('href') and ('history' in link_tag.get('href') or 'tournaments' in link_tag.get('href')):
                        nome = link_tag.text.strip()
                        # Lógica aprimorada para resolver ambiguidade da Serie A
                        if nome == "Serie A" and contexto == "Feminino":
                            nome = "Serie A (W)"
                        
                        competicoes.append({
                            'nome': nome,
                            'contexto': contexto,
                            'url': BASE_URL + link_tag.get('href')
                        })

    competicoes_unicas = sorted(list({v['url']:v for v in competicoes}.values()), key=lambda x: x['nome'])
    logging.info(f"Encontradas {len(competicoes_unicas)} competições únicas com contexto.")
    return competicoes_unicas

def coletar_temporadas_de_competicao(url_competicao):
    """Lógica de extração em múltiplos estágios, aprimorada com base nos HTMLs fornecidos."""
    soup = fazer_requisicao(url_competicao)
    if not soup: return [], "desconhecido"

    links = []; tipo = "NENHUM DADO ENCONTRADO"
    # Estágio 1: Busca por tabela de histórico padrão
    for tabela in extrair_tabelas_da_pagina(soup):
        if len(tabela.select('th a[href*="/comps/"]')) > 3:
            for tag in tabela.select('th a[href*="/comps/"]'):
                if tag.get('href') and ('-Stats' in tag['href'] or '-Seasons' in tag['href']):
                    links.append(BASE_URL + tag['href']); tipo = "TEMPORADAS"
    if links:
        logging.info(f"  -> {len(set(links))} links encontrados pelo MÉTODO PADRÃO."); return sorted(list(set(links)), reverse=True), tipo

    # Estágio 2: Busca por links em listas (Qualificatórias e Torneios)
    content_div = soup.find('div', id='content')
    if content_div:
        for tag in content_div.select('ul li a[href*="/comps/"], p > a[href*="/comps/"]'):
             if tag.get('href') and 'Stats' in tag['href']:
                links.append(BASE_URL + tag['href']); tipo = "TORNEIOS"
    if links:
        logging.info(f"  -> {len(set(links))} links encontrados pelo MÉTODO DE LISTAS."); return sorted(list(set(links)), reverse=True), tipo
        
    # Estágio 3: Busca por links de "Match Report"
    for tag in soup.find_all('a', string='Match Report'):
        if tag.get('href') and '/matches/' in tag['href']:
            links.append(BASE_URL + tag['href']); tipo = "PARTIDAS"
    if links:
        logging.info(f"  -> {len(set(links))} links encontrados pelo MÉTODO DE PARTIDAS."); return sorted(list(set(links)), reverse=True), tipo

    logging.warning("  -> AVISO: Nenhum método de extração encontrou links válidos.")
    return links, tipo

def main():
    """Orquestra a coleta de links e salva na fila de trabalho do banco de dados."""
    logging.info("🚀 Iniciando Script 1: Descoberta de Links...")
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        lista_competicoes = coletar_competicoes()
        if not lista_competicoes:
            logging.warning("Nenhuma competição foi encontrada na página principal. A Etapa 1 não produziu dados.")
            return
            
        for i, comp in enumerate(lista_competicoes):
            logging.info(f"\n--- Processando Competição {i+1}/{len(lista_competicoes)}: {comp['nome']} ({comp['contexto']}) ---")
            
            cursor.execute("INSERT OR IGNORE INTO competicoes (nome, contexto, url_historico) VALUES (?, ?, ?)", 
                           (comp['nome'], comp['contexto'], comp['url']))
            cursor.execute("SELECT id FROM competicoes WHERE url_historico = ?", (comp['url'],)); competicao_id = cursor.fetchone()[0]
            
            links, tipo = coletar_temporadas_de_competicao(comp['url'])
            logging.info(f"  -> Encontrados {len(links)} links do tipo {tipo}.")
            
            for link in links:
                cursor.execute("INSERT OR IGNORE INTO links_para_coleta (competicao_id, url, tipo_dado) VALUES (?, ?, ?)",
                               (competicao_id, link, tipo))
            conn.commit()
            
        logging.info("\n✅ Script 1 (Descoberta) finalizado com sucesso!")
    finally:
        conn.close(); close_driver()

if __name__ == "__main__":
    main()