import requests
import sqlite3
import pandas as pd  # FALTAVA ISSO

# Time: Chelsea → ID = 44
TEAM_ID = 44
URL = f"https://api.sofascore.com/api/v1/team/{TEAM_ID}/events/last/0"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
data = response.json()

jogos = []
for e in data.get("events", []):
    try:
        timestamp = e.get("startTimestamp")
        if timestamp is None:
            continue

        data_jogo = pd.to_datetime(timestamp, unit="s").isoformat()

        casa = e["homeTeam"]["name"]
        fora = e["awayTeam"]["name"]
        pc = e["homeScore"]["current"]
        pf = e["awayScore"]["current"]

        if pc is not None and pf is not None:
            jogos.append((data_jogo, casa, fora, pc, pf))
    except Exception as err:
        print("Erro ao processar jogo:", err)
        continue

# Salvar no banco
conn = sqlite3.connect("aposta.db")
cursor = conn.cursor()

inseridos = 0
for jogo in jogos:
    try:
        cursor.execute("""
            INSERT INTO jogos_historicos (liga, data, time_casa, time_fora, placar_casa, placar_fora)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("sofascore", *jogo))
        inseridos += 1
    except:
        continue

conn.commit()
conn.close()

print(f"✅ {inseridos} jogos históricos salvos no banco!")
