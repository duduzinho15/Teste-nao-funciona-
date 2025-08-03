import requests
from bs4 import BeautifulSoup
import sqlite3
import time

def coletar_jogos_sofascore(nome_time, apelido_time):
    url = f"https://www.sofascore.com/team/{apelido_time}/{nome_time}/results"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")

    partidas = []
    for jogo in soup.select("div.event__match"):
        try:
            data = jogo["data-startdate"]
            time_casa = jogo.select_one(".event__participant--home").text
            time_fora = jogo.select_one(".event__participant--away").text
            placar = jogo.select_one(".event__scores").text.strip()
            placar_casa, placar_fora = map(int, placar.split(":"))
            partidas.append((data, time_casa, time_fora, placar_casa, placar_fora))
        except:
            continue

    return partidas

# Exemplo: Chelsea (team ID: 44, nome: chelsea)
jogos = coletar_jogos_sofascore("chelsea", "44")

# Conectar ao banco e salvar
conn = sqlite3.connect("aposta.db")
cursor = conn.cursor()

inseridos = 0
for jogo in jogos:
    data, casa, fora, pc, pf = jogo
    try:
        cursor.execute("""
            INSERT INTO jogos_historicos (liga, data, time_casa, time_fora, placar_casa, placar_fora)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("sofascore", data, casa, fora, pc, pf))
        inseridos += 1
    except:
        continue

conn.commit()
conn.close()

print(f"✅ {inseridos} jogos históricos salvos no banco!")
