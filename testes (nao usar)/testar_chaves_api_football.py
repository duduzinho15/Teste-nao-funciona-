import requests

API_KEYS = [
    "661d6760f1814f9188b3f55c7dacacc4",
    "fd97b749495f4eac95e057a3c84d84f4",
    "d3842c0c58f441389d260bd92c4dafd1",
    "d13f9335ee2019746a58ce8fbc01ad8c",
    "e6342bbfd30862bc0e5354c88fccbfa8",
    "c456fb130d420ae44a1b0a7b2014291c",
    "fbcbbea822268cd7571d0a7f4c01a042"
]

def testar_chaves():
    print("🔎 Testando chaves da API-Football...\n")
    for i, key in enumerate(API_KEYS, 1):
        url = "https://v3.football.api-sports.io/status"
        headers = {"x-apisports-key": key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(f"✅ Chave {i} FUNCIONA ✅")
        elif response.status_code == 401:
            print(f"❌ Chave {i} inválida ou bloqueada (401)")
        elif response.status_code == 403:
            print(f"❌ Chave {i} proibida (403) – pode estar bloqueada")
        else:
            print(f"⚠️ Chave {i} retornou código {response.status_code}")

testar_chaves()
