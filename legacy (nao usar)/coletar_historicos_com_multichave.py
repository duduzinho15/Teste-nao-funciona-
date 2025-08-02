# coletar_dados.py
import requests
import sqlite3
import time
import json


API_KEYS = [
    "661d6760f1814f9188b3f55c7dacacc4",
    "fd97b749495f4eac95e057a3c84d84f4",
    "d3842c0c58f441389d260bd92c4dafd1"
]

def get_headers():
    if not API_KEYS:
        raise Exception("Todas as API keys foram usadas. Aguarde ou adicione mais chaves.")
    # Rotaciona as chaves, colocando a usada no final da lista
    key = API_KEYS.pop(0)
    API_KEYS.append(key)
    return {"X-Auth-Token": key}

def jogo_existe(cursor, liga, data, time_casa, time_fora):
    cursor.execute("""
        SELECT 1 FROM jogos_historicos WHERE liga=? AND data=? AND time_casa=? AND time_fora=?
    """, (liga, data, time_casa, time_fora))
    return cursor.fetchone() is not None

def coletar_dados():
    ligas = ["PL", "FL1", "PD", "BL1", "SA", "BSA", "CL", "PPL", "DED", "ELC"]
    try:
        with sqlite3.connect("aposta.db") as conn:
            cursor = conn.cursor()

            for liga in ligas:
                print(f"Coletando dados para liga: {liga}")
                page = 1
                total_inseridos = 0
                while True:
                    url = f"https://api.football-data.org/v4/matches?status=FINISHED&competitions={liga}&page={page}"
                    headers = get_headers()
                    try:
                        response = requests.get(url, headers=headers, timeout=20)
                    except requests.RequestException as e:
                        print(f"Erro de rede para {liga} página {page}: {e}")
                        break

                    if response.status_code == 200:
                        dados = response.json()
                        partidas = dados.get("matches", [])
                        if not partidas:
                            print(f"Nenhuma partida encontrada para {liga} na página {page}.")
                            break
                        for jogo in partidas:
                            # Validação de campos
                            data_jogo = jogo.get("utcDate")
                            home = jogo.get("homeTeam", {}).get("name")
                            away = jogo.get("awayTeam", {}).get("name")
                            placar_casa = jogo.get("score", {}).get("fullTime", {}).get("home")
                            placar_fora = jogo.get("score", {}).get("fullTime", {}).get("away")
                            estatisticas = jogo.get("statistics", {})
                            if not (data_jogo and home and away and placar_casa is not None and placar_fora is not None):
                                print(f"Dados incompletos para jogo em {data_jogo} entre {home} x {away}, pulando...")
                                continue
                            if jogo_existe(cursor, liga, data_jogo, home, away):
                                print(f"Jogo já existe no banco: {liga} {data_jogo} {home} x {away}")
                                continue
                            try:
                                cursor.execute('''
                                    INSERT INTO jogos_historicos (liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    liga,
                                    data_jogo,
                                    home,
                                    away,
                                    placar_casa,
                                    placar_fora,
                                    json.dumps(estatisticas)
                                ))
                                total_inseridos += 1
                            except sqlite3.DatabaseError as db_err:
                                print(f"Erro ao inserir jogo: {db_err}")
                        # Paginação: verifica se há próxima página
                        total_count = int(response.headers.get("X-Total-Count", "0"))
                        per_page = int(response.headers.get("X-Per-Page", "0"))
                        if per_page and (page * per_page) < total_count:
                            page += 1
                        else:
                            print(f"Liga {liga}: {total_inseridos} jogos inseridos.")
                            break
                    elif response.status_code == 429:
                        print(f"Limite de requisições atingido para {liga} página {page}. Aguardando 10s...")
                        time.sleep(10)
                    else:
                        print(f"Erro na coleta para {liga} página {page}: {response.status_code}")
                        break
                conn.commit()
    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    coletar_dados()