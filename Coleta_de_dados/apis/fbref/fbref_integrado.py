import logging
import sqlite3
import os
import time
from bs4 import BeautifulSoup # Importar BeautifulSoup
from .fbref_utils import fechar_driver, fazer_requisicao, extrair_tabelas_da_pagina, BASE_URL
from .fbref_fallback_system import create_fallback_system

# --- CONFIGURAÇÕES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logger = logging.getLogger(__name__)

# Sistema de fallback global
fallback_system = create_fallback_system(PROJECT_ROOT)

def coletar_competicoes():
    """
    Coleta competições com sistema de fallback robusto para lidar com rate limiting.
    """
    logger.info("Buscando lista de competições com sistema de fallback...")
    
    # Primeiro, verifica se há cache válido
    cached_competitions = fallback_system.get_cached_competitions()
    if cached_competitions:
        logger.info(f"Usando competições do cache: {len(cached_competitions)} competições")
        return cached_competitions
    
    # Verifica se o site está acessível rapidamente
    if not fallback_system.is_site_accessible():
        logger.warning("Site FBRef parece inacessível. Usando dados de fallback.")
        fallback_competitions = fallback_system.load_fallback_data()
        return fallback_competitions
    
    # Tenta fazer a requisição com timeout curto
    competicoes = []
    try:
        logger.info("Tentando requisição ao site FBRef...")
        
        # Timeout mais curto para evitar travamento
        start_time = time.time()
        soup = fazer_requisicao(f"{BASE_URL}/en/comps/")
        request_time = time.time() - start_time
        
        logger.info(f"Requisição completada em {request_time:.2f} segundos")
        
        if not soup:
            logger.warning("Requisição retornou None. Usando fallback.")
            return fallback_system.load_fallback_data()
        
        # Processa as tabelas normalmente
        tabelas_competicoes = soup.select("table.stats_table")
        if not tabelas_competicoes:
            logger.warning("Nenhuma tabela encontrada. Usando fallback.")
            return fallback_system.load_fallback_data()

        logger.debug(f"Encontradas {len(tabelas_competicoes)} tabelas de competições")
        
        for i, tabela in enumerate(tabelas_competicoes):
            logger.debug(f"Processando tabela {i+1}/{len(tabelas_competicoes)}")
            tbody = tabela.find('tbody')
            if not tbody:
                continue
                
            linhas = tbody.find_all('tr')
            
            for linha in linhas:
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
                    logger.debug(f"Erro ao processar linha: {e}")
                    continue

        # Remove duplicatas e ordena
        competicoes_unicas = []
        urls_vistas = set()
        
        for comp in competicoes:
            if comp['url'] not in urls_vistas:
                competicoes_unicas.append(comp)
                urls_vistas.add(comp['url'])
        
        competicoes_unicas.sort(key=lambda x: x['nome'])
        
        if competicoes_unicas:
            logger.info(f"Sucesso! Encontradas {len(competicoes_unicas)} competições únicas")
            # Salva no cache para uso futuro
            fallback_system.save_competitions_cache(competicoes_unicas)
            return competicoes_unicas
        else:
            logger.warning("Nenhuma competição válida encontrada. Usando fallback.")
            return fallback_system.load_fallback_data()
            
    except Exception as e:
        logger.error(f"Erro ao coletar competições: {e}")
        logger.info("Usando dados de fallback devido ao erro.")
        return fallback_system.load_fallback_data()

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
    """Lógica de extração com sistema de fallback para temporadas."""
    logger.info(f"Coletando temporadas de: {url_competicao}")
    
    try:
        # Verifica se o site está acessível rapidamente
        if not fallback_system.is_site_accessible():
            logger.warning(f"Site inacessível. Usando temporadas de fallback para: {url_competicao}")
            fallback_seasons = fallback_system.get_fallback_seasons(url_competicao)
            if fallback_seasons:
                links = [season['url'] for season in fallback_seasons]
                logger.info(f"  -> {len(links)} temporadas de fallback geradas")
                return links, "FALLBACK_TEMPORADAS"
            else:
                return [], "sem_fallback_disponivel"
        
        # Tenta fazer a requisição com timeout curto
        start_time = time.time()
        soup = fazer_requisicao(url_competicao)
        request_time = time.time() - start_time
        
        if not soup or request_time > 30:  # Se demorou mais de 30 segundos ou falhou
            logger.warning(f"Requisição falhou ou demorou muito ({request_time:.1f}s). Usando fallback.")
            fallback_seasons = fallback_system.get_fallback_seasons(url_competicao)
            if fallback_seasons:
                links = [season['url'] for season in fallback_seasons]
                logger.info(f"  -> {len(links)} temporadas de fallback geradas")
                return links, "FALLBACK_TEMPORADAS"
            else:
                return [], "erro_requisicao"

        links, tipo = [], "NENHUM DADO ENCONTRADO"

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
        
        # Se nenhum método funcionou, usa fallback
        logger.warning("Nenhum método de extração funcionou. Tentando fallback.")
        fallback_seasons = fallback_system.get_fallback_seasons(url_competicao)
        if fallback_seasons:
            links = [season['url'] for season in fallback_seasons]
            logger.info(f"  -> {len(links)} temporadas de fallback geradas")
            return links, "FALLBACK_TEMPORADAS"
        
        return [], "sem_dados_encontrados"
        
    except Exception as e:
        logger.error(f"Erro ao processar temporadas de {url_competicao}: {e}")
        logger.info("Tentando fallback devido ao erro...")
        
        try:
            fallback_seasons = fallback_system.get_fallback_seasons(url_competicao)
            if fallback_seasons:
                links = [season['url'] for season in fallback_seasons]
                logger.info(f"  -> {len(links)} temporadas de fallback geradas")
                return links, "FALLBACK_TEMPORADAS"
        except Exception as fallback_error:
            logger.error(f"Erro no fallback: {fallback_error}")
        
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

def main(modo_teste=False):
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
        
        # Modo teste: processa apenas as primeiras 5 competições
        if modo_teste:
            lista_competicoes = lista_competicoes[:5]
            logger.info(f"MODO TESTE ATIVADO: Processando apenas as primeiras {len(lista_competicoes)} competições")
        
        total_links = 0
        competicoes_processadas = 0
        competicoes_com_erro = 0
        
        # Processa em lotes menores para melhor controle
        lote_size = 5 if modo_teste else 10
        total_competicoes = len(lista_competicoes)
        
        logger.info(f"Processando {total_competicoes} competições em lotes de {lote_size}")
        
        for lote_inicio in range(0, total_competicoes, lote_size):
            lote_fim = min(lote_inicio + lote_size, total_competicoes)
            lote_competicoes = lista_competicoes[lote_inicio:lote_fim]
            
            logger.info(f"\n=== PROCESSANDO LOTE {lote_inicio//lote_size + 1}/{(total_competicoes + lote_size - 1)//lote_size} ===")
            logger.info(f"Competições {lote_inicio + 1} a {lote_fim} de {total_competicoes}")
            
            for i, comp in enumerate(lote_competicoes):
                indice_global = lote_inicio + i + 1
                logger.info(f"\n--- Processando Competição {indice_global}/{total_competicoes}: {comp['nome']} ({comp['contexto']}) ---")
                
                try:
                    # Salva competição e obtém ID
                    competicao_id = salvar_competicao_no_banco(conn, comp)
                    if not competicao_id:
                        logger.error(f"Falha ao salvar competição: {comp['nome']}")
                        competicoes_com_erro += 1
                        continue
                    
                    # Coleta links de temporadas com timeout individual
                    links, tipo = coletar_temporadas_de_competicao(comp['url'])
                    logger.info(f"  -> Encontrados {len(links)} links do tipo {tipo}.")
                    
                    # Salva links no banco
                    salvar_links_no_banco(conn, competicao_id, links, tipo)
                    
                    total_links += len(links)
                    competicoes_processadas += 1
                    
                    # Commit a cada competição para não perder dados
                    conn.commit()
                    
                except Exception as e:
                    logger.error(f"Erro ao processar competição {comp['nome']}: {e}")
                    competicoes_com_erro += 1
                    continue
            
            # Log de progresso do lote
            logger.info(f"\n✅ Lote {lote_inicio//lote_size + 1} concluído:")
            logger.info(f"  -> {competicoes_processadas} competições processadas até agora")
            logger.info(f"  -> {competicoes_com_erro} competições com erro")
            logger.info(f"  -> {total_links} links coletados até agora")
        
        logger.info(f"\n✅ Script 1 (Descoberta) finalizado com sucesso!")
        logger.info(f"  -> {competicoes_processadas} competições processadas com sucesso")
        logger.info(f"  -> {competicoes_com_erro} competições com erro")
        logger.info(f"  -> {total_links} links de temporadas coletados")
        
        return {
            "competicoes_encontradas": len(lista_competicoes),
            "competicoes_processadas": competicoes_processadas,
            "competicoes_com_erro": competicoes_com_erro,
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