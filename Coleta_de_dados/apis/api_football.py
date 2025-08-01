# api_football.py - versão expandida com múltiplas chaves, ligas priorizadas e coleta de odds/estatísticas
from utils.log_utils import registrar_log, registrar_erro
import requests
import sqlite3
import time
import random
from datetime import datetime

# Chaves da API-Football (ordem de prioridade)
API_KEYS = [
    "d13f9335ee2019746a58ce8fbc01ad8c",  # ✅ PRIORIDADE 1
    "e6342bbfd30862bc0e5354c88fccbfa8",
    "c456fb130d420ae44a1b0a7b2014291c",
    "fbcbbea822268cd7571d0a7f4c01a042",
    "661d6760f1814f9188b3f55c7dacacc4",
    "fd97b749495f4eac95e057a3c84d84f4",
    "d3842c0c58f441389d260bd92c4dafd1"
]

# IDs das ligas priorizadas por região (até 700 ligas no total, 100 por chave)
LIGAS_PRIORITARIAS = [
    71, 72, 73, 74, 75, 76, 77, 78, 128, 129, 130, 131, 132, 133, 134, 135, 136,
    137, 138, 139, 140, 141, 142, 143, 144, 145,
    266, 267, 268, 269, 270, 271, 272,
    210, 211, 212, 213, 214, 215,
    253, 262,
    39, 78, 61, 88, 94, 140, 135, 203, 199, 253, 265, 268, 289, 293, 294, 295,
    296, 297, 298, 299, 300, 306, 308, 309, 310,
    2, 3, 6, 7, 8, 9, 10, 15, 16, 17, 18, 19, 20, 21, 27, 28,
    301, 302, 303, 304, 305, 307, 312, 313, 314, 315,
    12,
] + list(range(4000, 4600))

TEMP_DB = "Banco_de_dados/aposta.db"


def usar_chave(index):
    return API_KEYS[index % len(API_KEYS)]

def salvar_no_banco(jogo, tabela):
    conn = sqlite3.connect(TEMP_DB)
    cursor = conn.cursor()
    colunas = ', '.join(jogo.keys())
    valores = tuple(jogo.values())
    placeholders = ', '.join('?' * len(jogo))
    cursor.execute(f"INSERT OR IGNORE INTO {tabela} ({colunas}) VALUES ({placeholders})", valores)
    conn.commit()
    conn.close()

def obter_estatisticas_odds(fixture_id, headers):
    estatisticas, odds = {}, {}
    try:
        stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
        odds_url = f"https://v3.football.api-sports.io/odds?fixture={fixture_id}"

        stats_resp = requests.get(stats_url, headers=headers)
        odds_resp = requests.get(odds_url, headers=headers)

        if stats_resp.status_code == 200:
            estatisticas = stats_resp.json()
        if odds_resp.status_code == 200:
            odds = odds_resp.json()

    except Exception as e:
        print(f"⚠️ Erro ao coletar stats/odds do jogo {fixture_id}: {e}")
    return estatisticas, odds

def coletar_ligas():
    print("\n🔄 Iniciando coleta expandida da API-Football...")
    for idx, key in enumerate(API_KEYS):
        headers = {"x-apisports-key": key}
        ligas_atuais = LIGAS_PRIORITARIAS[idx*100:(idx+1)*100]
        print(f"\n🔑 Usando chave {idx+1} para {len(ligas_atuais)} ligas")

        for id_liga in ligas_atuais:
            try:
                print(f"📥 Coletando liga ID {id_liga}...")
                params = {"league": id_liga, "season": 2024}
                r = requests.get("https://v3.football.api-sports.io/fixtures", params=params, headers=headers)

                if r.status_code == 200:
                    dados = r.json()
                    for item in dados.get("response", []):
                        fixture_id = item['fixture']['id']
                        estatisticas, odds = obter_estatisticas_odds(fixture_id, headers)
                        jogo = {
                            "id_jogo": fixture_id,
                            "liga": item['league']['name'],
                            "time_casa": item['teams']['home']['name'],
                            "time_fora": item['teams']['away']['name'],
                            "data": item['fixture']['date'],
                            "status": item['fixture']['status']['short'],
                            "odds": str(odds),
                            "estatisticas": str(estatisticas)
                        }
                        tabela = 'jogos_futuros' if jogo['status'] in ['NS', 'TBD'] else 'jogos_historicos'
                        salvar_no_banco(jogo, tabela)
                        print(f"✅ Inserido jogo {jogo['id_jogo']} ({jogo['liga']})")
                    time.sleep(1)
                else:
                    print(f"❌ Erro ao coletar liga {id_liga}: {r.status_code}")
            except Exception as e:
                print(f"❌ Erro inesperado para liga {id_liga}: {str(e)}")

    print("\n✅ Coleta expandida da API-Football finalizada.")

if __name__ == "__main__":
    try:
        registrar_log("api_football", "Iniciando coleta da StatsBomb")
        coletar_ligas()
        registrar_log("api_football", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("api_football", f"Erro durante execução: {e}")
