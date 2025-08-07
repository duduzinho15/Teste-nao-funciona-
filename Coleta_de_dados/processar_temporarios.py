# processar_temporarios.py
import sqlite3
import os
import json
from utils.log_utils import registrar_log, registrar_erro

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'Banco_de_dados', 'aposta.db')

def processar_sofascore():
    registrar_log("processar_temporarios", "Iniciando processamento de sofascore_temp")
    print("🔄 Processando dados do sofascore_temp...")
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sofascore_temp")
            registros = cursor.fetchall()

            novos = 0
            for r in registros:
                try:
                    cursor.execute('''
                        INSERT INTO jogos_historicos (
                            liga, data, time_casa, time_fora,
                            placar_casa, placar_fora, estatisticas, fonte
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r[1], r[2], r[3], r[4],
                        None, None, r[5], 'SofaScore'
                    ))
                    novos += 1
                except Exception as e:
                    registrar_erro("processar_sofascore", f"Erro ao inserir jogo: {e}")
            print(f"✅ {novos} registros do SofaScore transferidos.")
    except Exception as e:
        registrar_erro("processar_sofascore", f"Erro geral: {e}")

def processar_thesportsdb():
    registrar_log("processar_temporarios", "Iniciando processamento de thesportsdb")
    print("🔄 Processando dados do thesportsdb...")
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM thesportsdb")
            registros = cursor.fetchall()

            novos = 0
            for r in registros:
                try:
                    cursor.execute('''
                        INSERT INTO jogos_historicos (
                            liga, data, time_casa, time_fora,
                            placar_casa, placar_fora, estatisticas, fonte
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r[1], r[2], r[3], r[4],
                        None, None, r[5], 'TheSportsDB'
                    ))
                    novos += 1
                except Exception as e:
                    registrar_erro("processar_thesportsdb", f"Erro ao inserir jogo: {e}")
            print(f"✅ {novos} registros do TheSportsDB transferidos.")
    except Exception as e:
        registrar_erro("processar_thesportsdb", f"Erro geral: {e}")

def processar_apifootball():
    registrar_log("processar_temporarios", "Iniciando processamento da tabela apifootball")
    print("🔄 Processando dados da tabela apifootball...")
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM apifootball")
            registros = cursor.fetchall()

            novos = 0
            for r in registros:
                try:
                    cursor.execute('''
                        INSERT INTO jogos_historicos (
                            liga, data, time_casa, time_fora,
                            placar_casa, placar_fora, estatisticas, odds, fonte
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r[1], r[2], r[3], r[4],
                        r[5], r[6], r[7], r[8], 'API-Football'
                    ))
                    novos += 1
                except Exception as e:
                    registrar_erro("processar_apifootball", f"Erro ao inserir jogo: {e}")
            print(f"✅ {novos} registros da API-Football transferidos.")
    except Exception as e:
        registrar_erro("processar_apifootball", f"Erro geral: {e}")

def processar_football_data():
    registrar_log("processar_temporarios", "Iniciando processamento do football_data_temp")
    print("🔄 Processando dados do football_data_temp...")
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM football_data_temp")
            registros = cursor.fetchall()

            novos = 0
            for r in registros:
                try:
                    cursor.execute('''
                        INSERT INTO jogos_historicos (
                            liga, data, time_casa, time_fora,
                            placar_casa, placar_fora, estatisticas, fonte
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r[1], r[2], r[3], r[4],
                        r[5], r[6], r[7], 'Football-Data.org'
                    ))
                    novos += 1
                except Exception as e:
                    registrar_erro("processar_football_data", f"Erro ao inserir jogo: {e}")
            print(f"✅ {novos} registros do Football-Data.org transferidos.")
    except Exception as e:
        registrar_erro("processar_football_data", f"Erro geral: {e}")

def processar_statsbomb():
    registrar_log("processar_temporarios", "Iniciando processamento do statsbomb_temp")
    print("🔄 Processando dados do statsbomb_temp...")
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM statsbomb_temp")
            registros = cursor.fetchall()

            novos = 0
            for r in registros:
                try:
                    cursor.execute('''
                        INSERT INTO jogos_historicos (
                            liga, data, time_casa, time_fora,
                            placar_casa, placar_fora, estatisticas, fonte
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        r[1], r[2], r[3], r[4],
                        r[5], r[6], r[7], 'StatsBomb'
                    ))
                    novos += 1
                except Exception as e:
                    registrar_erro("processar_statsbomb", f"Erro ao inserir jogo: {e}")
            print(f"✅ {novos} registros da StatsBomb transferidos.")
    except Exception as e:
        registrar_erro("processar_statsbomb", f"Erro geral: {e}")

def processar_estatisticas_avancadas():
    registrar_log("processar_temporarios", "Iniciando processamento de estatísticas avançadas")
    print("🔄 Processando estatísticas avançadas...")

    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()

            # === Consolidar estatísticas de jogadores ===
            cursor.execute("SELECT * FROM estatisticas_jogadores")
            jogadores = cursor.fetchall()
            inseridos_jog = 0

            for j in jogadores:
                try:
                    cursor.execute('''
                        INSERT INTO estatisticas_historicas (entidade, nome, tipo, estatisticas)
                        VALUES (?, ?, ?, ?)
                    ''', ("jogador", j[2], j[6], j[8]))
                    inseridos_jog += 1
                except Exception as e:
                    registrar_erro("estatisticas_jogadores", f"⚠️ Erro estatísticas jogador: {e}")

            # === Consolidar estatísticas de times ===
            cursor.execute("SELECT * FROM estatisticas_times")
            times = cursor.fetchall()
            inseridos_time = 0

            for t in times:
                try:
                    cursor.execute('''
                        INSERT INTO estatisticas_historicas (entidade, nome, tipo, estatisticas)
                        VALUES (?, ?, ?, ?)
                    ''', ("time", t[2], t[5], t[6]))
                    inseridos_time += 1
                except Exception as e:
                    registrar_erro("estatisticas_times", f"⚠️ Erro estatísticas time: {e}")

            conn.commit()
            print(f"✅ {inseridos_jog} estatísticas de jogadores e {inseridos_time} de times transferidas para estatisticas_historicas.")
    except Exception as e:
        registrar_erro("processar_estatisticas_avancadas", f"Erro geral: {e}")

    # Processar StatsBomb ao final
    processar_statsbomb()


if __name__ == "__main__":
    processar_sofascore()
    processar_thesportsdb()
    processar_apifootball()
    processar_estatisticas_avancadas()
    processar_football_data()
