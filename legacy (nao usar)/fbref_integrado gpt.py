import os
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys

# Corrigir importação dos utilitários
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from utils.log_utils import registrar_log, registrar_erro
from Coleta_de_dados.apis.fbref.fbref_utils import (
    obter_competicoes_disponiveis,
    obter_temporadas_disponiveis,
    obter_partidas_por_temporada,
    coletar_tabelas_partida
)

DB_PATH = os.path.join("Banco_de_dados", "aposta.db")

def coletar_dados_completos():
    print("\n🚀 Iniciando coleta completa do FBref...\n")

    # 1. Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Obter todas as competições (masculinas e femininas)
    competicoes = obter_competicoes_disponiveis()
    print(f"\n🔍 {len(competicoes)} competições encontradas.")

    for comp in competicoes:
        nome_competicao = comp["nome"]
        url_competicao = comp["url"]

        print(f"\n🏆 Competição: {nome_competicao}\n🔗 URL: {url_competicao}")

        # 3. Obter temporadas disponíveis para a competição
        temporadas = obter_temporadas_disponiveis(url_competicao)
        print(f"📅 {len(temporadas)} temporadas disponíveis.")

        for temp in temporadas:
            nome_temporada = temp["nome"]
            url_temporada = temp["url"]

            print(f"\n📆 Temporada: {nome_temporada}\n🔗 URL: {url_temporada}")
            partidas = obter_partidas_por_temporada(nome_competicao, nome_temporada)

            for i, link_partida in enumerate(partidas):
                print(f"\n📥 Coletando partida {i+1}/{len(partidas)}: {link_partida}")
                try:
                    tabelas = coletar_tabelas_partida(link_partida)

                    for idx, tabela in enumerate(tabelas):
                        tipo = tabela["tipo"]
                        titulo = tabela["titulo"]
                        print(f"🔍 Tabela {idx+1}: {titulo} ➤ Tipo: {tipo}")

                        cursor.execute('''
                            INSERT OR IGNORE INTO fbref_com_temp (
                                partida_url, tabela_index, estatisticas_json, coletado_em,
                                tipo_tabela, url_partida, titulo_tabela, html_tabela, data_coleta
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            link_partida,
                            idx,
                            str(tabela["dados"]),
                            datetime.now().isoformat(),
                            tipo,
                            link_partida,
                            titulo,
                            tabela["html"],
                            datetime.now().strftime("%Y-%m-%d")
                        ))
                        conn.commit()

                except Exception as e:
                    print(f"❌ Erro ao coletar dados da partida: {e}")
                time.sleep(1)

    conn.close()
    print("\n✅ Coleta completa finalizada com sucesso!\n")

if __name__ == "__main__":
    try:
        registrar_log("fbref_integrado", "Iniciando coleta do FBref")
        coletar_dados_completos()
        registrar_log("fbref_integrado", "Coleta finalizada com sucesso")
    except Exception as e:
        registrar_erro("fbref_integrado", f"Erro durante execução: {e}")
