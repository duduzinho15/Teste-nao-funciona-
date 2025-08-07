import requests
import pandas as pd

API_KEY = "sua_chave_aqui"
headers = {"X-Auth-Token": API_KEY}

ligas = ["PL", "FL1", "PD", "BL1", "SA", "BSA", "CL", "PPL", "DED", "ELC"]

historico = []

for liga in ligas:
    url = f"https://api.football-data.org/v4/matches?status=FINISHED&competitions={liga}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        partidas = response.json().get("matches", [])
        for jogo in partidas:
            historico.append({
                "liga": liga,
                "data": jogo["utcDate"],
                "time_casa": jogo["homeTeam"]["name"],
                "time_fora": jogo["awayTeam"]["name"],
                "placar_casa": jogo["score"]["fullTime"]["home"],
                "placar_fora": jogo["score"]["fullTime"]["away"]
            })
    else:
        print(f"Erro na liga {liga}: {response.status_code}")

if historico:
    df = pd.DataFrame(historico)
    df.to_excel("historico_partidas.xlsx", index=False)
    print("✅ Planilha 'historico_partidas.xlsx' criada com sucesso!")
else:
    print("⚠️ Nenhum dado histórico encontrado.")
