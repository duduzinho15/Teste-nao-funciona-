import logging
import sqlite3
import os
from bs4 import BeautifulSoup # Importar BeautifulSoup
from .fbref_utils import fechar_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL

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
    if not soup: 
        logger.error("Falha ao obter página de competições")
        return []
    
    competicoes = []
    
    # Encontra todas as tabelas de competições na página
    tabelas_competicoes = soup.select("table.stats_table")
    if not tabelas_competicoes:
        logger.error("Nenhuma tabela de competições encontrada na página principal.")
        return []

    for tabela in tabelas_competicoes:
        tbody = tabela.find('tbody')
        if not tbody:
            continue
            
        for linha in tbody.find_all('tr'):
            try:
                th_cell = linha.find('th', {'data-stat': 'league_name'})
                gender_cell = linha.find('td', {'data-stat': 'gender'})
                
                if not (th_cell and th_cell.find('a')):
                    continue
                    
                link_tag = th_cell.find('a')
                nome = link_tag.text.strip()
                url = link_tag.get('href')
                
                if not url:
                    continue
                
                contexto = "Desconhecido"
                if gender_cell:
                    gender_text = gender_cell.text.strip()
                    if gender_text == 'M':
                        contexto = "Masculino"
                    elif gender_text == 'F':
                        contexto = "Feminino"

                # Resolve a ambiguidade da Serie A
                if nome == "Serie A" and contexto == "Feminino":
                    nome = "Serie A (W)"
                
                if 'history' in url or 'tournaments' in url:
                    if not url.startswith('http'):
                        url = BASE_URL + url
                    
                    competicoes.append({
                        'nome': nome, 
                        'contexto': contexto, 
                        'url': url
                    })
                    
            except Exception as e:
                logger.debug(f"Erro ao processar linha da tabela: {e}")
                continue

    # Remove duplicatas baseado na URL
    competicoes_unicas = []
    urls_vistas = set()
    
    for comp in competicoes:
        if comp['url'] not in urls_vistas:
            competicoes_unicas.append(comp)
            urls_vistas.add(comp['url'])
    
    # Ordena por nome
    competicoes_unicas.sort(key=lambda x: x['nome'])
    
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
            try:
                # O link da temporada/ano está no primeiro cabeçalho (th) de cada linha.
                header = linha.find('th')
                if header and header.find('a'):
                    href = header.find('a').get('href')
                    if href:
                        links.append(BASE_URL + href)
            except Exception as e:
                logger.debug(f"Erro ao processar linha de torneio: {e}")
                continue
    
    return links

def coletar_temporadas_de_competicao(url_competicao):
    """Lógica de extração em múltiplos estágios, aprimorada com base nos HTMLs fornecidos."""
    logger.info(f"Coletando temporadas de: {url_competicao}")
    
    soup = fazer_requisicao(url_competicao)
    if not soup: 
        logger.error(f"Falha ao obter conteúdo de: {url_competicao}")
        return [], "erro_requisicao"

    links, tipo = [], "NENHUM DADO ENCONTRADO"

    try:
        # --- MÉTODO 1: TABELA DE TEMPORADAS (Padrão para Ligas) ---
        tabela_seasons = soup.find('table', id='seasons')
        if tabela_seasons:
            for tag in tabela_seasons.select('th[data-stat="year_id"] a'):
                href = tag.get('href')
                if href: 
                    links.append(BASE_URL + href)
            
            if links:
                logger.info(f"  -> {len(links)} links encontrados pelo MÉTODO DE TABELA DE TEMPORADAS.")
                return sorted(list(set(links)), reverse=True), "TEMPORADAS"

        # --- MÉTODO 2: CABEÇALHOS H2 (Padrão para Qualificatórias) ---
        content_div = soup.find('div', id='content')
        if content_div:
            for header in content_div.find_all('h2'):
                link_tag = header.find('a')
                if link_tag and link_tag.get('href') and '/comps/' in link_tag['href']:
                    href = link_tag.get('href')
                    if href:
                        links.append(BASE_URL + href)
        
        if links:
            logger.info(f"  -> {len(links)} links encontrados pelo MÉTODO DE CABEÇALHOS H2.")
            return sorted(list(set(links)), reverse=True), "TORNEIOS"
        
        # --- MÉTODO 3: TABELA DE HISTÓRICO DE TORNEIOS (Solução para Copas, Olimpíadas, etc.) ---
        links = extrair_links_de_torneios_da_tabela(soup)
        if links:
            logger.info(f"  -> {len(links)} links encontrados pelo NOVO MÉTODO DE TABELA DE HISTÓRICO.")
            return sorted(list(set(links)), reverse=True), "TORNEIOS"
        
        logger.warning("  -> AVISO: Nenhum método de extração encontrou links de temporada válidos.")
        return links, "sem_dados_encontrados"
        
    except Exception as e:
        logger.error(f"Erro ao processar temporadas de {url_competicao}: {e}")
        return [], "erro_processamento"

def salvar_competicao_no_banco(conn, competicao):
    """Salva uma competição no banco e retorna o ID."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO competicoes (nome, contexto, url_historico) VALUES (?, ?, ?)", 
            (competicao['nome'], competicao['contexto'], competicao['url'])
        )
        
        cursor.execute("SELECT id FROM competicoes WHERE url_historico = ?", (competicao['url'],))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            logger.error(f"Falha ao obter ID da competição: {competicao['nome']}")
            return None
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar competição {competicao['nome']}: {e}")
        return None

def salvar_links_no_banco(conn, competicao_id, links, tipo):
    """Salva links de temporadas no banco."""
    if not links:
        return
        
    try:
        cursor = conn.cursor()
        links_salvos = 0
        
        for link in links:
            cursor.execute(
                "INSERT OR IGNORE INTO links_para_coleta (competicao_id, url, tipo_dado) VALUES (?, ?, ?)",
                (competicao_id, link, tipo)
            )
            if cursor.rowcount > 0:
                links_salvos += 1
        
        conn.commit()
        
        if links_salvos > 0:
            logger.info(f"  -> {links_salvos} novos links salvos no banco.")
        else:
            logger.info("  -> Nenhum link novo para salvar (todos já existem).")
            
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar links no banco: {e}")

def main():
    """Orquestra a coleta de links e salva na fila de trabalho do banco de dados."""
    logger.info("🚀 Iniciando Script 1: Descoberta de Links...")
    
    # Garantir que o diretório do banco existe
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        
        lista_competicoes = coletar_competicoes()
        if not lista_competicoes: 
            logger.warning("Nenhuma competição foi encontrada.")
            return {"competicoes_encontradas": 0, "links_coletados": 0}
        
        total_links = 0
        competicoes_processadas = 0
        
        for i, comp in enumerate(lista_competicoes):
            logger.info(f"\n--- Processando Competição {i+1}/{len(lista_competicoes)}: {comp['nome']} ({comp['contexto']}) ---")
            
            # Salva competição e obtém ID
            competicao_id = salvar_competicao_no_banco(conn, comp)
            if not competicao_id:
                logger.error(f"Falha ao salvar competição: {comp['nome']}")
                continue
            
            # Coleta links de temporadas
            links, tipo = coletar_temporadas_de_competicao(comp['url'])
            logger.info(f"  -> Encontrados {len(links)} links do tipo {tipo}.")
            
            # Salva links no banco
            salvar_links_no_banco(conn, competicao_id, links, tipo)
            
            total_links += len(links)
            competicoes_processadas += 1
            
        logger.info(f"\n✅ Script 1 (Descoberta) finalizado com sucesso!")
        logger.info(f"  -> {competicoes_processadas} competições processadas")
        logger.info(f"  -> {total_links} links de temporadas coletados")
        
        return {
            "competicoes_encontradas": len(lista_competicoes),
            "competicoes_processadas": competicoes_processadas,
            "links_coletados": total_links
        }
        
    except Exception as e:
        logger.error(f"Erro crítico no script de descoberta: {e}", exc_info=True)
        return None
        
    finally:
        if conn:
            conn.close()
        # Chama fechar_driver para limpar recursos do Selenium se houver
        fechar_driver(None)

if __name__ == "__main__":
    main()