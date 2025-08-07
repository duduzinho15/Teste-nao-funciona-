import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

DB_PATH = "aposta.db"
TABELA_TEMP = "fbref_com_temp"
URL_TESTE = "https://fbref.com/en/matches/2025-07-26"  # Substitua se desejar outro

def criar_tabela_temporaria():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABELA_TEMP} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_url TEXT,
                tabela_index INTEGER,
                estatisticas_json TEXT,
                coletado_em TEXT,
                UNIQUE(partida_url, tabela_index)
            )
        """)
        conn.commit()

def coletar_tabelas_fbref(url):
    print(f"📥 Coletando tabelas da partida: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")

    dados = []
    for idx, table in enumerate(tables):
        table_html = str(table)
        dados.append({
            "tabela_index": idx + 1,
            "html": table_html,
        })
    return dados

def salvar_tabelas_no_banco(url, tabelas):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for tabela in tabelas:
            json_data = json.dumps(tabela)
            try:
                cursor.execute(f"""
                    INSERT INTO {TABELA_TEMP} (partida_url, tabela_index, estatisticas_json, coletado_em)
                    VALUES (?, ?, ?, ?)
                """, (url, tabela["tabela_index"], json_data, datetime.now().isoformat()))
                print(f"✅ Tabela {tabela['tabela_index']} salva.")
            except sqlite3.IntegrityError:
                print(f"🟡 Tabela {tabela['tabela_index']} já existe, pulando...")

        conn.commit()

if __name__ == "__main__":
    print("🚀 Testando coleta FBref com link manual...")
    criar_tabela_temporaria()
    tabelas = coletar_tabelas_fbref(URL_TESTE)
    salvar_tabelas_no_banco(URL_TESTE, tabelas)
