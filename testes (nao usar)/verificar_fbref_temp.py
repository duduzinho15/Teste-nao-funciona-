import sqlite3
import json
from collections import Counter

DB_PATH = "Banco_de_dados/aposta.db"
TABELA_TEMP = "fbref_com_temp"

def identificar_tipo(colunas):
    """Palpita o tipo da tabela com base nos nomes de colunas"""
    colunas = [c.lower() for c in colunas]
    if "player" in colunas and "minutes" in colunas:
        return "Estatísticas de jogadores"
    if "team" in colunas and "possession" in colunas:
        return "Posse de bola e Time"
    if "shots" in colunas or "sot" in colunas:
        return "Finalizações"
    if "passes" in colunas:
        return "Passes"
    if "tackles" in colunas or "interceptions" in colunas:
        return "Defesa (Desarmes/Interceptações)"
    if "cards" in colunas or "fouls" in colunas:
        return "Cartões e Faltas"
    if "goalkeeper" in colunas or "saves" in colunas:
        return "Goleiros"
    return "Outro"

def verificar_tabelas_fbref():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT partida_url, tabela_index, estatisticas_json FROM {TABELA_TEMP} ORDER BY partida_url, tabela_index")
    resultados = cursor.fetchall()

    if not resultados:
        print("⚠️ Nenhuma tabela encontrada na tabela temporária fbref_com_temp.")
        return

    print(f"🔍 {len(resultados)} tabelas encontradas na fbref_com_temp:\n")

    agrupado = {}
    for url, idx, dados_json in resultados:
        dados = json.loads(dados_json)
        colunas = list(dados[0].keys()) if dados else []
        tipo = identificar_tipo(colunas)
        chave = url
        if chave not in agrupado:
            agrupado[chave] = []
        agrupado[chave].append((idx, len(dados), len(colunas), tipo))

    for url, tabelas in agrupado.items():
        print(f"📎 Partida: {url}")
        for idx, linhas, colunas, tipo in tabelas:
            print(f"   📊 Tabela {idx:<2} | {linhas:>3} linhas x {colunas:>2} colunas → {tipo}")
        print("")

    conn.close()

if __name__ == "__main__":
    print("🧪 Verificando tabelas temporárias do FBref...\n")
    verificar_tabelas_fbref()
