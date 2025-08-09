from apis import sofascore_scraper, thesportsdb_api
from apis.api_football import coletar_ligas
from apis.football_data_org import executar_coleta_football_data
from apis.statsbomb_api import executar_coleta_statsbomb
from utils.log_utils import registrar_log, registrar_erro
from Coleta_de_dados.apis.fbref import fbref_integrado
import sqlite3
import os
import sys

# Adicionar caminho para importar o criar_banco e processar_temporarios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Banco_de_dados')))
from Banco_de_dados.criar_banco import criar_tabelas

# Processamento final dos dados temporários
from processar_temporarios import (
    processar_sofascore,
    processar_thesportsdb,
    processar_apifootball,
    processar_estatisticas_avancadas,
    processar_football_data
)

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'Banco_de_dados', 'aposta.db')

def resumir_tabela(tabela):
    try:
        with sqlite3.connect(get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            return cursor.fetchone()[0]
    except Exception as e:
        registrar_erro("resumir_tabela", f"Erro ao consultar tabela {tabela}", e)
        return None

def executar_coleta_com_resumo(nome_coleta, funcao_coleta):
    print(f"\nIniciando coleta do {nome_coleta}...")
    tabela_nome = f'{nome_coleta.lower()}_temp' if 'SofaScore' in nome_coleta else nome_coleta.lower()
    contador_anterior = resumir_tabela(tabela_nome)

    try:
        funcao_coleta()
        print(f"{nome_coleta}: coleta concluída.")
        contador_atual = resumir_tabela(tabela_nome)
        if contador_atual is not None and contador_anterior is not None:
            print(f"{nome_coleta}: {contador_atual - contador_anterior} novos registros inseridos (total: {contador_atual})")
        else:
            print(f"{nome_coleta}: não foi possível verificar novos registros")
    except Exception as e:
        print(f"Erro em {nome_coleta.lower()}: {e}")
        registrar_erro(nome_coleta, "Erro durante execução da coleta", e)

def executar_coletas():
    criar_tabelas()

    # Coleta bruta nas fontes primárias
    executar_coleta_com_resumo("SofaScore", sofascore_scraper.executar_coleta_sofascore)
    executar_coleta_com_resumo("TheSportsDB", thesportsdb_api.executar_coleta_thesportsdb)

    print("\nIniciando coleta da API-Football expandida...")
    try:
        coletar_ligas()
    except Exception as e:
        registrar_erro("api_football", "Erro durante coleta das ligas", e)

    print("\nIniciando coleta da Football-Data.org...")
    executar_coleta_com_resumo("football_data", executar_coleta_football_data)

    print("\nIniciando coleta da StatsBomb...")
    executar_coleta_com_resumo("statsbomb", executar_coleta_statsbomb)

    # Processamento e deduplicação dos dados temporários
    print("\n🔄 Processando dados temporários...")
    try:
        registrar_log("coletar_tudo", "🔄 Iniciando processamento dos dados temporários...")
        processar_sofascore()
        processar_thesportsdb()
        processar_apifootball()
        processar_estatisticas_avancadas()
        processar_football_data()
        registrar_log("coletar_tudo", "✅ Processamento dos dados temporários finalizado com sucesso.")
    except Exception as e:
        registrar_erro("processar_temporarios", "Erro durante processamento dos dados", e)

    # Resumo final
    print("\n\n=== RESUMO GERAL ===")
    tabelas = [
        'ligas', 'times', 'jogadores',
        'jogos_historicos', 'jogos_futuros',
        'estatisticas', 'estatisticas_partidas', 'estatisticas_jogadores',
        'estatisticas_times', 'estatisticas_historicas',
        'sofascore_temp', 'thesportsdb', 'apifootball', 'football_data_temp'
    ]
    for tabela in tabelas:
        contador = resumir_tabela(tabela)
        if contador is not None:
            print(f"{tabela}: {contador} registros")

if __name__ == "__main__":
    try:
        registrar_log("coletar_tudo", "🚀 Início do processo de coleta geral")
        executar_coletas()
        registrar_log("coletar_tudo", "✅ Fim do processo de coleta geral")
    except Exception as e:
        registrar_erro("coletar_tudo", f"❌ Erro fatal no processo geral: {e}")
