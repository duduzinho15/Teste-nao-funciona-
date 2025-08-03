import sqlite3
import pandas as pd
import json
from bs4 import BeautifulSoup
from io import StringIO

DB_PATH = "aposta.db"
TABELA_ORIGEM = "fbref_com_temp"
TABELA_ROTULADA = "fbref_com_rotulada"

def identificar_tipo_tabela(df):
    # 🧠 Regras simples para rótulo
    colunas = df.columns.str.lower().tolist()
    if "player" in colunas and "gls" in colunas:
        return "estatisticas_jogadores"
    elif "team" in colunas and "poss" in colunas:
        return "estatisticas_times"
    elif "passes" in colunas or "pass" in colunas:
        return "passes_completos"
    elif "shots" in colunas:
        return "finalizacoes"
    return "tabela_desconhecida"

def criar_tabela_rotulada():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABELA_ROTULADA} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_url TEXT,
                tabela_index INTEGER,
                tipo_tabela TEXT,
                dados_json TEXT,
                coletado_em TEXT,
                UNIQUE(partida_url, tabela_index)
            )
        """)
        conn.commit()

def rotular_tabelas():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT partida_url, tabela_index, estatisticas_json, coletado_em FROM {TABELA_ORIGEM}")
        rows = cursor.fetchall()

        for partida_url, tabela_index, estatisticas_json, coletado_em in rows:
            try:
                # 🔄 Corrigido: carregar HTML e extrair com read_html
                html = json.loads(estatisticas_json)["html"]
                dfs = pd.read_html(StringIO(html))

                if not dfs:
                    print(f"⚠️ Nenhuma tabela extraída da tabela {tabela_index} da partida {partida_url}")
                    continue

                df = dfs[0]
                tipo = identificar_tipo_tabela(df)
                json_data = df.to_json(orient="records", force_ascii=False)

                cursor.execute(f"""
                    INSERT OR IGNORE INTO {TABELA_ROTULADA} 
                    (partida_url, tabela_index, tipo_tabela, dados_json, coletado_em)
                    VALUES (?, ?, ?, ?, ?)
                """, (partida_url, tabela_index, tipo, json_data, coletado_em))

                print(f"✅ Tabela {tabela_index} rotulada como {tipo}")

            except Exception as e:
                print(f"⚠️ Erro ao processar tabela {tabela_index} da partida {partida_url}: {e}")
        conn.commit()

if __name__ == "__main__":
    print("🔎 Iniciando análise e rotulagem das tabelas brutas do FBref...")
    criar_tabela_rotulada()
    rotular_tabelas()
