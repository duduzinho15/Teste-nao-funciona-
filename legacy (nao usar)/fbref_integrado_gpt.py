import requests
import sqlite3
import time
from bs4 import BeautifulSoup, Comment
from datetime import datetime
from tqdm import tqdm

# === CONFIGURACAO DE TESTE ===
COMPETICAO_TESTE = "Premier League"
TEMPORADA_TESTE = "2022-2023"

# === FUNCOES AUXILIARES ===
def limpar_html_oculto(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extrair tabelas ocultas dentro de <!-- ... -->
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        try:
            comment_soup = BeautifulSoup(comment, "html.parser")
            for table in comment_soup.find_all("table"):
                soup.append(table)
        except:
            pass

    return soup

def coletar_links_partidas(competicao, temporada):
    print(f"\n🔗 Buscando partidas de {competicao} - {temporada}...")
    url_base = "https://fbref.com/en/comps/9/{}/schedule/{}-Premier-League-Scores-and-Fixtures".format(
        temporada.replace("-", ""), temporada
    )

    response = requests.get(url_base)
    soup = limpar_html_oculto(response.text)
    links = []
    for a in soup.find_all("a", href=True):
        if "/en/matches/" in a['href']:
            link_completo = "https://fbref.com" + a['href']
            if link_completo not in links:
                links.append(link_completo)

    print(f"🔗 {len(links)} links de partidas encontrados na temporada.")
    return links

def salvar_tabela_temp(partida_url, tabela_index, tabela_html):
    with sqlite3.connect("Banco_de_dados/aposta.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO fbref_com_temp (partida_url, tabela_index, estatisticas_json, coletado_em)
            VALUES (?, ?, ?, ?)
        ''', (partida_url, tabela_index, str(tabela_html), datetime.now().isoformat()))
        conn.commit()

def coletar_dados_partida(url_partida, index):
    print(f"\n📥 Coletando dados da partida {index + 1}: {url_partida}")
    try:
        response = requests.get(url_partida)
        soup = limpar_html_oculto(response.text)
        tabelas = soup.find_all("table")

        if not tabelas:
            print("⚠️ Nenhuma tabela encontrada na partida.")
            return

        for idx, tabela in enumerate(tabelas):
            salvar_tabela_temp(url_partida, idx + 1, str(tabela))
        print(f"✅ {len(tabelas)} tabelas salvas.")
    except Exception as e:
        print(f"❌ Erro ao coletar {url_partida}: {e}")

# === SCRIPT PRINCIPAL ===
def main():
    print(f"\n🚀 Iniciando versão de teste do fbref_integrado.py para: {COMPETICAO_TESTE} {TEMPORADA_TESTE}\n")

    links_partidas = coletar_links_partidas(COMPETICAO_TESTE, TEMPORADA_TESTE)

    for idx, partida_url in enumerate(links_partidas[:5]):  # limitar para 5 no teste
        coletar_dados_partida(partida_url, idx)

    print("\n✅ Coleta e processamento de teste concluídos.")

if __name__ == "__main__":
    main()
