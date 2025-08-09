# apis/statsbomb_scraper.py

import sqlite3
import time
from statsbomb_api import get_all_matches  # Supondo que isso traga partidas com stats
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'Banco_de_dados', 'aposta.db')

def salvar_statsbomb(liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM statsbomb_temp
        WHERE liga=? AND data=? AND time_casa=? AND time_fora=?
    ''', (liga, data, time_casa, time_fora))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO statsbomb_temp (
                liga, data, time_casa, time_fora,
                placar_casa, placar_fora, estatisticas
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            liga, data, time_casa, time_fora,
            placar_casa, placar_fora, estatisticas
        ))
        conn.commit()
    conn.close()

def executar_coleta_statsbomb():
    print("⚽ Iniciando coleta da StatsBomb...")
    jogos = get_all_matches()

    count = 0
    for jogo in jogos:
        try:
            liga = jogo.get("competition_name", "Desconhecida")
            data = jogo.get("match_date", "")[:10]
            time_casa = jogo.get("home_team", {}).get("home_team_name", "")
            time_fora = jogo.get("away_team", {}).get("away_team_name", "")
            placar_casa = jogo.get("home_score", None)
            placar_fora = jogo.get("away_score", None)
            estatisticas = str(jogo.get("stats", {}))  # Salva como string JSON

            salvar_statsbomb(liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas)
            count += 1
        except Exception as e:
            print(f"⚠️ Erro ao salvar jogo da StatsBomb: {e}")

    print(f"✅ Coleta finalizada: {count} jogos salvos.")

if __name__ == "__main__":
    executar_coleta_statsbomb()
