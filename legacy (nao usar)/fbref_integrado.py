# Coleta_de_dados/apis/fbref_integrado.py
from utils.log_utils import registrar_log, registrar_erro
import requests
import sqlite3
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from Coleta_de_dados.apis.fbref.fbref_utils import obter_temporadas_disponiveis, obter_partidas_por_temporada, identificar_tipo_tabela
from Coleta_de_dados.apis.fbref_scraper import coletar_tabelas_fbref
from Coleta_de_dados.apis.fbref_parser import rotular_tabelas_partida


DB_PATH = os.path.join(os.path.dirname(__file__), '../../Banco_de_dados/aposta.db')

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def salvar_tabela_temporaria(partida_url, tabela_index, tabela_html):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT OR IGNORE INTO fbref_com_temp (partida_url, tabela_index, estatisticas_json, coletado_em)
            VALUES (?, ?, ?, ?)
        ''', (partida_url, tabela_index, tabela_html, datetime.now().isoformat()))


def rotular_e_salvar(partida_url, tabela_index, html):
    try:
        dfs = pd.read_html(html)
        for df in dfs:
            tipo, nome = identificar_tipo_tabela(df)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    INSERT OR IGNORE INTO fbref_com_rotulada (partida_url, tabela_index, tipo_tabela, tabela_nome, estatisticas_json, processado_em)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    partida_url, tabela_index, tipo, nome,
                    df.to_json(orient='split'),
                    datetime.now().isoformat()
                ))
    except Exception as e:
        print(f"⚠️ Erro ao rotular tabela {tabela_index} da partida {partida_url}: {e}")


def coletar_partidas_da_temporada(competicao, temporada):
    print(f"\n🚀 Iniciando coleta do FBref para: {competicao} {temporada}\n")

    partidas = obter_partidas_por_temporada(competicao, temporada)
    print(f"🔗 {len(partidas)} links de partidas encontrados na temporada.")

    for i, partida_url in enumerate(partidas):
        print(f"\n📥 Coletando dados da partida {i+1}: {partida_url}")
        try:
            r = requests.get(partida_url, headers=HEADERS)
            soup = BeautifulSoup(r.text, 'html.parser')
            tabelas = soup.find_all('table')

            if not tabelas:
                print("⚠️ Nenhuma tabela encontrada na partida.")
                continue

            for idx, tabela in enumerate(tabelas):
                html_tabela = str(tabela)
                salvar_tabela_temporaria(partida_url, idx, html_tabela)
                rotular_e_salvar(partida_url, idx, html_tabela)

            print(f"✅ {len(tabelas)} tabelas salvas e processadas.")

        except Exception as e:
            print(f"❌ Erro na partida {partida_url}: {e}")

    print("\n✅ Coleta e processamento da temporada concluídos.\n")


def executar_coleta_fbref():
    print("\nIniciando coleta do FBref (modo produção)...")
    try:
        nome_competicao = "Premier League"
        temporada = "2022-2023"
        modo_teste = False
        executar_fluxo_completo(nome_competicao, temporada, modo_teste=modo_teste)
        print("✅ FBref: coleta completa finalizada.")
    except Exception as e:
        from utils.log_utils import registrar_erro
        registrar_erro("fbref", "Erro durante execução da coleta", e)

if __name__ == "__main__":
    try:
        registrar_log("fbref_integrado", "Iniciando coleta da StatsBomb")
        executar_coleta_fbref()
        registrar_log("fbref_integrado", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("fbref_integrado", f"Erro durante execução: {e}")