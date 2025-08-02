import requests
import sqlite3
import time

API_KEYS = [
    "661d6760f1814f9188b3f55c7dacacc4",
    "fd97b749495f4eac95e057a3c84d84f4",
    "d3842c0c58f441389d260bd92c4dafd1"  # opcional
]

ligas = ["PL", "FL1", "PD", "BL1", "SA", "BSA", "CL", "PPL", "DED", "ELC"]

# Conectar ao banco
conn = sqlite3.connect("aposta.db")
cursor = conn.cursor()

total_inseridos = 0
chave_index = 0

def get_headers():
    return {"X-Auth-Token": API_KEYS[chave_index]}

for liga in ligas:
    url = f"https://api.football-data.org/v4/matches?status=SCHEDULED&competitions={liga}"

    while True:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            partidas = response.json().get("matches", [])
            for jogo in partidas:
                cursor.execute("""
                    INSERT INTO jogos_futuros (liga, data, time_casa, time_fora)
                    VALUES (?, ?, ?, ?)
                """, (
                    liga,
                    jogo["utcDate"],
                    jogo["homeTeam"]["name"],
                    jogo["awayTeam"]["name"]
                ))
                total_inseridos += 1
            print(f"✅ Liga {liga} coletada com sucesso.")
            break

        elif response.status_code == 429:
            print(f"⚠️ Limite atingido com a chave {API_KEYS[chave_index][:6]}... Trocando.")
            chave_index += 1
            if chave_index >= len(API_KEYS):
                print("❌ Todas as chaves atingiram o limite. Encerrando.")
                conn.commit()
                conn.close()
                exit()
            time.sleep(1)  # Espera antes de usar a próxima
        else:
            print(f"❌ Erro inesperado na liga {liga}: {response.status_code}")
            break  # pula essa liga

conn.commit()
conn.close()
print(f"✅ Coleta finalizada. {total_inseridos} jogos futuros salvos em 'aposta.db'.")
