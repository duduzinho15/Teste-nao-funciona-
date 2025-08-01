# apis/football_data_org.py
from utils.log_utils import registrar_log, registrar_erro
import requests
import sqlite3
import time

API_TOKEN = 'd3842c0c58f441389d260bd92c4dafd1'  # Substitua pela sua chave
BASE_URL = 'https://api.football-data.org/v4'

HEADERS = {'X-Auth-Token': API_TOKEN}
DB_PATH = 'Banco_de_dados/aposta.db'

def salvar_jogo(liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM football_data_temp
        WHERE liga=? AND data=? AND time_casa=? AND time_fora=?
    ''', (liga, data, time_casa, time_fora))
    
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO football_data_temp (
                liga, data, time_casa, time_fora,
                placar_casa, placar_fora, estatisticas
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas))
        conn.commit()
    
    conn.close()

def obter_competicoes():
    url = f"{BASE_URL}/competitions"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        time.sleep(6)  # respeita o limite após sucesso
        return r.json().get("competitions", [])
    print("Erro ao buscar competições:", r.status_code)
    time.sleep(6)
    return []

def obter_partidas(competition_code, temporada='2023'):
    url = f"{BASE_URL}/competitions/{competition_code}/matches?season={temporada}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        time.sleep(6)  # respeita o limite após sucesso
        return r.json().get("matches", [])
    print(f"Erro ao buscar jogos da {competition_code}:", r.status_code)
    time.sleep(6)
    return []

def executar_coleta_football_data():
    print("⚽ Iniciando coleta da Football-Data.org...")
    ligas = obter_competicoes()

    for liga in ligas:
        code = liga.get('code')
        nome = liga.get('name')
        if liga['currentSeason'] is None:
            print(f"⏭️ Pulando {nome} ({code}) pois não há temporada atual disponível.")
            continue

        if not code:
            continue

        print(f"🔍 Coletando jogos da {nome} ({code})")
        partidas = obter_partidas(code)

        count = 0
        for p in partidas:
            time_casa = p['homeTeam']['name']
            time_fora = p['awayTeam']['name']
            placar_casa = p['score']['fullTime']['home']
            placar_fora = p['score']['fullTime']['away']
            data = p['utcDate'][:10]

            salvar_jogo(nome, data, time_casa, time_fora, placar_casa, placar_fora)
            count += 1

        print(f"✅ {count} jogos salvos para {nome}")

    print("✅ Coleta finalizada com sucesso!")

if __name__ == "__main__":
    try:
        registrar_log("football_data_org", "Iniciando coleta da Football Data")
        executar_coleta_football_data()
        registrar_log("football_data_org", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("football_data_org", f"Erro durante execução: {e}")
