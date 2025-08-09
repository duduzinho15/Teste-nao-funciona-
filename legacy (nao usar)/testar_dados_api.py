import requests

API_KEY = "661d6760f1814f9188b3f55c7dacacc4"
headers = {"X-Auth-Token": API_KEY}
liga = "PL"  # Premier League
url = f"https://api.football-data.org/v4/matches?status=FINISHED&competitions={liga}"

response = requests.get(url, headers=headers)
print("Status:", response.status_code)

dados = response.json()
partidas = dados.get("matches", [])
print("Partidas recebidas:", len(partidas))

# Mostrar os 3 primeiros resultados com placar
for jogo in partidas[:3]:
    print(jogo["utcDate"], jogo["homeTeam"]["name"], "x", jogo["awayTeam"]["name"])
    print("Placar:", jogo.get("score", {}).get("fullTime"))
