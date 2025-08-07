import requests
import sqlite3
import json
import time
from utils.log_utils import registrar_log, registrar_erro

DB_PATH = 'Banco_de_dados/aposta.db'
BASE_URL = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data'

def salvar_jogo(liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas=None):
    try:
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
            ''', (liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas))
            conn.commit()
        conn.close()
    except Exception as e:
        registrar_erro("statsbomb_api", f"Erro ao salvar jogo: {e}")

def executar_coleta_statsbomb():
    print("📊 Iniciando coleta da StatsBomb (open data)...")
    try:
        response = requests.get(f"{BASE_URL}/competitions.json")
        response.raise_for_status()
        competicoes = response.json()
    except Exception as e:
        registrar_erro("statsbomb_api", f"Erro ao obter competições: {e}")
        return

    for comp in competicoes:
        comp_id = comp.get("competition_id")
        temporada_id = comp.get("season_id")
        nome_liga = comp.get("competition_name")
        temporada_nome = comp.get("season_name")
        print(f"🔍 Coletando jogos de {nome_liga} ({temporada_nome})")

        try:
            res_partidas = requests.get(f"{BASE_URL}/matches/{comp_id}/{temporada_id}.json")
            res_partidas.raise_for_status()
            partidas = res_partidas.json()
        except Exception as e:
            registrar_erro("statsbomb_api", f"Erro partidas {nome_liga} {temporada_nome}: {e}")
            continue

        for p in partidas:
            try:
                data = p['match_date']
                time_casa = p['home_team']['home_team_name']
                time_fora = p['away_team']['away_team_name']
                placar_casa = p['home_score']
                placar_fora = p['away_score']
                match_id = p['match_id']

                estatisticas = None
                try:
                    res_eventos = requests.get(f"{BASE_URL}/events/{match_id}.json")
                    if res_eventos.status_code == 200:
                        estatisticas = json.dumps(res_eventos.json())
                        time.sleep(0.5)
                except Exception as e:
                    registrar_erro("statsbomb_api", f"Erro eventos jogo {match_id}: {e}")

                salvar_jogo(nome_liga, data, time_casa, time_fora, placar_casa, placar_fora, estatisticas)
            except Exception as e:
                registrar_erro("statsbomb_api", f"Erro processando partida: {e}")

    print("✅ Coleta da StatsBomb finalizada!")

if __name__ == "__main__":
    try:
        registrar_log("statsbomb_api", "Iniciando coleta da StatsBomb")
        executar_coleta_statsbomb()
        registrar_log("statsbomb_api", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("statsbomb_api", f"Erro durante execução: {e}")
