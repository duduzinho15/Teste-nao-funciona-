import sqlite3
import os
import logging

# --- CONFIGURAÇÕES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def criar_todas_as_tabelas():
    """
    Cria ou verifica a existência de TODAS as tabelas necessárias para a pipeline completa.
    """
    logging.info(f"Verificando e configurando a estrutura completa do banco de dados em '{DB_NAME}'...")
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- 1. Tabelas para a Pipeline do FBREF ---
    logging.info("Criando tabelas para o FBRef...")
    
    # Definição ÚNICA e CORRETA da tabela 'competicoes'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS competicoes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            contexto TEXT, -- Coluna para diferenciar (ex: Masculino, Feminino)
            url_historico TEXT UNIQUE
        )
    ''')

    cursor.execute('CREATE TABLE IF NOT EXISTS links_para_coleta (id INTEGER PRIMARY KEY, competicao_id INTEGER, url TEXT NOT NULL UNIQUE, tipo_dado TEXT, status_coleta TEXT DEFAULT "pendente", FOREIGN KEY (competicao_id) REFERENCES competicoes (id))')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY, link_coleta_id INTEGER, data TEXT, time_casa TEXT, placar TEXT,
            time_visitante TEXT, url_match_report TEXT UNIQUE, status_coleta_detalhada TEXT DEFAULT 'pendente',
            FOREIGN KEY (link_coleta_id) REFERENCES links_para_coleta (id))
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas_time_partida (
            id INTEGER PRIMARY KEY, partida_id INTEGER, time_nome TEXT, posse_bola REAL, finalizacoes INTEGER,
            chutes_no_alvo INTEGER, sot_percent REAL, gols_por_chute REAL, gols_por_chute_no_alvo REAL, 
            xg REAL, npxg REAL, xg_assist REAL, g_xg_diff REAL, g_npxg_diff REAL,
            UNIQUE(partida_id, time_nome), FOREIGN KEY (partida_id) REFERENCES partidas (id))
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas_jogador_partida (
            id INTEGER PRIMARY KEY, partida_id INTEGER, jogador_nome TEXT, time_nome TEXT, nacao TEXT, 
            posicao TEXT, idade TEXT, minutos_jogados INTEGER, gols INTEGER, assistencias INTEGER, 
            gols_penalti INTEGER, penaltis_cobrados INTEGER, cartoes_amarelos INTEGER, cartoes_vermelhos INTEGER,
            xg_jogador REAL, npxg_jogador REAL, xg_assist_jogador REAL, xg_npxg_assist_jogador REAL, 
            sca INTEGER, gca INTEGER, passes_completos INTEGER, passes_tentados INTEGER, passes_pct REAL, 
            passes_distancia_total INTEGER, passes_distancia_progressiva INTEGER, passes_curtos_completos INTEGER, 
            passes_curtos_tentados INTEGER, passes_medios_completos INTEGER, passes_medios_tentados INTEGER,
            passes_longos_completos INTEGER, passes_longos_tentados INTEGER, passes_chave INTEGER, 
            passes_terco_final INTEGER, passes_area_penal INTEGER, cruzamentos_area_penal INTEGER, 
            desarmes INTEGER, desarmes_vencidos INTEGER, bloqueios INTEGER, chutes_bloqueados INTEGER,
            passes_bloqueados INTEGER, interceptacoes INTEGER, erros_defensivos INTEGER, 
            disputas_vencidas_pct REAL, toques INTEGER, toques_terco_defensivo INTEGER, 
            toques_terco_medio INTEGER, toques_terco_ofensivo INTEGER, toques_area_defensiva INTEGER,
            toques_area_ofensiva INTEGER, dribles_tentados INTEGER, dribles_completos INTEGER, 
            dribles_sucesso_pct REAL, conducoes_progressivas INTEGER, recepcoes_progressivas INTEGER, 
            faltas_cometidas INTEGER, faltas_sofridas INTEGER, recuperacoes INTEGER,
            duelos_aereos_vencidos INTEGER, duelos_aereos_perdidos INTEGER, duelos_aereos_vencidos_pct REAL,
            UNIQUE(partida_id, jogador_nome), FOREIGN KEY (partida_id) REFERENCES partidas (id)
        )
    ''')

    # --- 2. Tabelas para as outras APIs ---
    logging.info("Criando tabelas para as outras APIs...")
    # (As definições para as outras APIs permanecem as mesmas)
    cursor.execute('CREATE TABLE IF NOT EXISTS ligas_api_football (id INTEGER PRIMARY KEY, liga_id INTEGER UNIQUE, nome TEXT, pais TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS times_api_football (id INTEGER PRIMARY KEY, time_id INTEGER UNIQUE, nome TEXT, fundado INTEGER, estadio TEXT, capacidade_estadio INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS jogadores_api_football (id INTEGER PRIMARY KEY, jogador_id INTEGER UNIQUE, nome TEXT, idade INTEGER, nacionalidade TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS competicoes_football_data (id INTEGER PRIMARY KEY, competicao_id TEXT UNIQUE, nome TEXT, area_nome TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS times_football_data (id INTEGER PRIMARY KEY, time_id INTEGER UNIQUE, nome TEXT, sigla TEXT, endereco TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS partidas_football_data (id INTEGER PRIMARY KEY, partida_id INTEGER UNIQUE, data_utc TEXT, status TEXT, time_casa_id INTEGER, time_visitante_id INTEGER, placar_casa INTEGER, placar_visitante INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS partidas_sofascore (id INTEGER PRIMARY KEY, partida_id INTEGER UNIQUE, data_partida TEXT, time_casa TEXT, time_visitante TEXT, placar_final TEXT, estatisticas_json TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS competicoes_statsbomb (id INTEGER PRIMARY KEY, competicao_id INTEGER UNIQUE, nome_competicao TEXT, nome_temporada TEXT, pais TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS partidas_statsbomb (id INTEGER PRIMARY KEY, partida_id INTEGER UNIQUE, data_partida TEXT, competicao_id INTEGER, time_casa TEXT, time_visitante TEXT, placar_casa INTEGER, placar_visitante INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS eventos_statsbomb (id INTEGER PRIMARY KEY, evento_id TEXT UNIQUE, partida_id INTEGER, tipo_evento TEXT, periodo INTEGER, timestamp TEXT, jogador_id INTEGER, pos_x REAL, pos_y REAL, dados_json TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS ligas_thesportsdb (id INTEGER PRIMARY KEY, liga_id TEXT UNIQUE, nome TEXT, esporte TEXT, liga_alternativa TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS times_thesportsdb (id INTEGER PRIMARY KEY, time_id TEXT UNIQUE, nome TEXT, ano_formado INTEGER, estadio TEXT, website TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS eventos_thesportsdb (id INTEGER PRIMARY KEY, evento_id TEXT UNIQUE, nome_evento TEXT, data_evento TEXT, hora_evento TEXT, id_time_casa TEXT, id_time_visitante TEXT, placar_casa INTEGER, placar_visitante INTEGER)')

    conn.commit()
    conn.close()
    logging.info("Banco de dados pronto com a estrutura completa para TODAS as fontes de dados.")

if __name__ == "__main__":
    criar_todas_as_tabelas()