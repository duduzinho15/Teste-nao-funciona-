# thesportsdb_api.py - versão expandida com coleta de esportes, ligas, jogos, estatísticas e atletas
from Coleta_de_dados.apis.statsbomb_api import executar_coleta_statsbomb
from utils.log_utils import registrar_log, registrar_erro
import requests
import sqlite3
import time

DB_PATH = 'Banco_de_dados/aposta.db'
API_KEY = '123'
BASE_URL = 'https://www.thesportsdb.com/api/v1/json/{}/'.format(API_KEY)

# === Funções utilitárias ===
def salvar_jogo(liga, data, time_casa, time_fora, estatisticas):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO thesportsdb (liga, data, time_casa, time_fora, estatisticas)
        VALUES (?, ?, ?, ?, ?)
    ''', (liga, data, time_casa, time_fora, estatisticas))
    conn.commit()
    conn.close()

def buscar(endpoint):
    try:
        r = requests.get(BASE_URL + endpoint)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"❌ Erro {r.status_code} ao buscar {endpoint}")
    except Exception as e:
        print(f"⚠️ Erro ao buscar {endpoint}: {e}")
    return {}

def obter_ligas():
    esportes = buscar('all_sports.php').get('sports', [])
    ligas = []
    for esporte in esportes:
        nome = esporte['strSport']
        ligas_json = buscar(f'search_all_leagues.php?s={nome}')
        for liga in ligas_json.get('countrys', []):
            ligas.append((liga['idLeague'], liga['strLeague'], nome))
    return ligas

def obter_eventos_liga(id_liga):
    eventos = buscar(f'eventsseason.php?id={id_liga}&s=2024-2025')
    return eventos.get('events', [])

def obter_estatisticas_evento(id_evento):
    estat = buscar(f'lookupeventstats.php?id={id_evento}')
    return estat.get('eventstats', [])

def obter_jogadores_time(id_time):
    dados = buscar(f'lookup_all_players.php?id={id_time}')
    return dados.get('player', [])

def salvar_jogador(j):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO jogadores (id_jogador, nome, posicao, id_time, esporte)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        j['idPlayer'],
        j['strPlayer'],
        j.get('strPosition', 'N/A'),
        j['idTeam'],
        j['strSport']
    ))
    conn.commit()
    conn.close()

def executar_coleta_thesportsdb():
    print("\n🌐 Iniciando coleta do TheSportsDB (ligas, eventos, atletas)...")
    ligas = obter_ligas()
    print(f"🔍 {len(ligas)} ligas encontradas")

    for id_liga, nome_liga, esporte in ligas:
        print(f"\n⚽ Liga: {nome_liga} ({esporte})")
        eventos = obter_eventos_liga(id_liga)
        for e in eventos:
            if not e.get('idEvent'):
                continue
            estatisticas = obter_estatisticas_evento(e['idEvent'])
            stats_json = str(estatisticas) if estatisticas else None
            salvar_jogo(nome_liga, e['dateEvent'], e['strHomeTeam'], e['strAwayTeam'], stats_json)

            # Coletar jogadores dos dois times
            for id_time in [e.get('idHomeTeam'), e.get('idAwayTeam')]:
                if id_time:
                    jogadores = obter_jogadores_time(id_time)
                    for jogador in jogadores:
                        salvar_jogador(jogador)
            time.sleep(1)

    print("✅ Coleta do TheSportsDB finalizada.")

if __name__ == "__main__":
    try:
        registrar_log("thesportsdb_api", "Iniciando coleta da StatsBomb")
        executar_coleta_thesportsdb()
        registrar_log("thesportsdb_api.", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("thesportsdb_api.", f"Erro durante execução: {e}")