import logging
import time
import random
from datetime import datetime

# Biblioteca de parsing
from bs4 import BeautifulSoup, Comment
# Biblioteca de requisição que personifica navegadores
from curl_cffi.requests import Session, RequestsError

# --- CONFIGURAÇÕES GERAIS ---
BASE_URL = "https://fbref.com"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ARQUIVO_ERRO_LOG = 'erros_coleta.log'

# --- SESSÃO E REQUISIÇÃO (LÓGICA MELHORADA) ---

# Sessão será criada uma vez e reutilizada para todas as requisições
session = None

def setup_session():
    """Inicia a sessão ou a retorna se já existir."""
    global session
    if session is None:
        logging.info("Iniciando sessão de requisições persistente...")
        session = Session()
        session.impersonate = "chrome110" # Personificação é definida para toda a sessão
    return session

def close_session():
    """Fecha a sessão ao final do script."""
    global session
    if session:
        session.close()
        logging.info("Sessão de requisições finalizada.")

def fazer_requisicao(url, retries=3, backoff_factor=5):
    """
    Faz requisições usando uma sessão persistente e com lógica de retentativas.
    """
    sess = setup_session()
    for i in range(retries):
        try:
            # Pausa aleatória entre 2 e 4 segundos para simular comportamento humano
            time.sleep(random.uniform(2, 4))
            response = sess.get(url, timeout=45)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except RequestsError as e:
            logging.warning(f"Falha na requisição para {url} (Tentativa {i+1}/{retries}): {e}")
            if i + 1 == retries:
                logging.error(f"Não foi possível acessar {url} após {retries} tentativas.")
                registrar_erro(url, e)
                return None
            # Pausa exponencial antes de tentar novamente (5s, 10s, 20s...)
            sleep_time = backoff_factor * (2 ** i)
            logging.info(f"Aguardando {sleep_time} segundos antes de tentar novamente...")
            time.sleep(sleep_time)

# --- DEMAIS FUNÇÕES ---

def registrar_erro(url, erro):
    with open(ARQUIVO_ERRO_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] Erro ao processar: {url}\n  Detalhe: {str(erro)}\n\n")

def coletar_competicoes():
    """Coleta os links de todas as tabelas de competição encontradas na página."""
    logging.info("Iniciando busca por competições...")
    url_principal = f"{BASE_URL}/en/comps/"
    soup = fazer_requisicao(url_principal)
    if not soup: return []
    competicoes = []
    todas_as_tabelas = soup.find_all('table')
    if not todas_as_tabelas:
        logging.warning("Nenhuma tabela encontrada na página de competições.")
        return []
    logging.info(f"Encontradas {len(todas_as_tabelas)} tabelas. Extraindo competições...")
    for tabela in todas_as_tabelas:
        if tabela.find('tbody'):
            for linha in tabela.find('tbody').find_all('tr'):
                link_tag = linha.find('th').find('a')
                if link_tag and link_tag.get('href') and ('history' in link_tag.get('href') or 'tournaments' in link_tag.get('href')):
                    competicoes.append({'nome': link_tag.text, 'url': BASE_URL + link_tag.get('href')})
    logging.info(f"SUCESSO! Total de {len(competicoes)} competições encontradas.")
    return competicoes

def coletar_temporadas_de_competicao(url_competicao):
    """
    Coleta os links para todas as temporadas de uma única competição com seletor robusto.
    """
    links_temporadas = []
    soup = fazer_requisicao(url_competicao)
    if not soup: return []

    # Seletor robusto: encontra qualquer link dentro de um cabeçalho de linha (th)
    # de uma tabela que contenha 'history' ou 'results' no seu id.
    seletor_css = "table[id*=history] th a, table[id*=results] th a"
    tags_de_temporada = soup.select(seletor_css)
    
    for tag in tags_de_temporada:
        link = tag.get('href')
        # Validação extra para garantir que é um link de temporada válido
        if link and 'comps' in link and ('-Stats' in link or '-Seasons' in link):
             links_temporadas.append(BASE_URL + link)

    logging.info(f"Encontradas {len(links_temporadas)} temporadas para a competição.")
    return links_temporadas

# --- FLUXO PRINCIPAL ---

def main():
    """Função principal que orquestra todo o processo de coleta."""
    logging.info("🚀 Iniciando coleta completa do FBref...")
    open(ARQUIVO_ERRO_LOG, 'w').close()

    try:
        lista_competicoes = coletar_competicoes()
        if not lista_competicoes:
            logging.warning("Nenhuma competição foi encontrada.")
            return

        for i, comp in enumerate(lista_competicoes):
            logging.info(f"\n--- [{i+1}/{len(lista_competicoes)}] Processando Competição: {comp['nome']} ---")
            links_das_temporadas = coletar_temporadas_de_competicao(comp['url'])

            if not links_das_temporadas:
                continue # Pula para a próxima competição se não encontrar temporadas

            # Aqui você pode adicionar a lógica para processar as temporadas encontradas
            # Ex: processar_pagina_temporada(links_das_temporadas[0], comp['nome'])

        logging.info("\n✅ Coleta de links de temporadas finalizada com sucesso!")

    finally:
        # Garante que a sessão seja fechada mesmo se ocorrer um erro
        close_session()

if __name__ == "__main__":
    main()