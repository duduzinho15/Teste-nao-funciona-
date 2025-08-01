# sofascore_scraper.py - versão expandida
from utils.log_utils import registrar_log, registrar_erro
import requests
import sqlite3
import time
from datetime import datetime

BASE_URL = "https://api.sofascore.com/api/v1"
DB_PATH = "Banco_de_dados/aposta.db"

ESPORTES = ["football", "basketball", "tennis", "mma"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def salvar_jogo(jogo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sofascore_temp (liga, data, time_casa, time_fora, estatisticas)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        jogo["liga"], jogo["data"], jogo["time_casa"], jogo["time_fora"], str(jogo["estatisticas"])
    ))
    conn.commit()
    conn.close()

def coletar_jogos_sofascore():
    print("\n🔄 Iniciando coleta SofaScore expandida...")
    for esporte in ESPORTES:
        try:
            print(f"\n➡️ Coletando esporte: {esporte}")
            r = requests.get(f"{BASE_URL}/sport/{esporte}/unique-tournament", headers=HEADERS)
            if r.status_code != 200:
                print(f"⚠️ Erro ao obter torneios para {esporte}")
                continue

            torneios = r.json().get("uniqueTournaments", [])
            for torneio in torneios:
                id_torneio = torneio["id"]
                nome_torneio = torneio["name"]
                try:
                    r2 = requests.get(f"{BASE_URL}/unique-tournament/{id_torneio}/matches/last/0", headers=HEADERS)
                    if r2.status_code != 200:
                        continue
                    partidas = r2.json().get("events", [])

                    for partida in partidas:
                        try:
                            id_partida = partida["id"]
                            liga = nome_torneio
                            data = datetime.utcfromtimestamp(partida["startTimestamp"]).isoformat()
                            time_casa = partida["homeTeam"]["name"]
                            time_fora = partida["awayTeam"]["name"]
                            estatisticas = {}

                            # Estatísticas por partida
                            stats_url = f"{BASE_URL}/event/{id_partida}/statistics"
                            stats_resp = requests.get(stats_url, headers=HEADERS)
                            if stats_resp.status_code == 200:
                                estatisticas = stats_resp.json()

                            jogo = {
                                "liga": liga,
                                "data": data,
                                "time_casa": time_casa,
                                "time_fora": time_fora,
                                "estatisticas": estatisticas
                            }

                            salvar_jogo(jogo)
                            print(f"✅ Coletado: {liga} - {time_casa} x {time_fora}")
                            time.sleep(0.3)

                        except Exception as e:
                            print(f"Erro em partida do torneio {nome_torneio}: {e}")
                except:
                    continue
        except Exception as e:
            print(f"Erro ao coletar dados do esporte {esporte}: {e}")
    print("\n✅ Coleta SofaScore concluída.")

def executar_coleta_sofascore():
    coletar_jogos_sofascore()

if __name__ == "__main__":
    try:
        registrar_log("sofascore_scraper", "Iniciando coleta da SofaScore")
        executar_coleta_sofascore()
        registrar_log("sofascore_scraper", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("sofascore_scraper", f"Erro durante execução: {e}")