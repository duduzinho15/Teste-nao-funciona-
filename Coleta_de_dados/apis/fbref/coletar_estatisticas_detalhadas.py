import logging
import sqlite3
import pandas as pd
import os
# Importação corrigida
from .fbref_utils import close_driver, fazer_requisicao

# --- CONFIGURAÇÕES ---
# --- INÍCIO DA CORREÇÃO ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
# --- FIM DA CORREÇÃO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_database_stats():
    """Cria/Altera as tabelas de estatísticas para incluir TODAS as colunas do documento."""
    # --- INÍCIO DA CORREÇÃO ---
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    # --- FIM DA CORREÇÃO ---
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    logging.info("Configurando banco de dados com a estrutura completa de estatísticas...")

    # --- TABELA DE ESTATÍSTICAS DO JOGADOR (EXPANDIDA) ---
    # Adicionamos colunas para cada estatística do seu documento.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas_jogador_partida (
            id INTEGER PRIMARY KEY,
            partida_id INTEGER,
            jogador_nome TEXT,
            time_nome TEXT,
            nacao TEXT,
            posicao TEXT,
            idade TEXT,
            minutos_jogados INTEGER,
            
            -- Padrão
            gols INTEGER,
            assistencias INTEGER,
            gols_penalti INTEGER,
            penaltis_cobrados INTEGER,
            cartoes_amarelos INTEGER,
            cartoes_vermelhos INTEGER,
            xg_jogador REAL,
            npxg_jogador REAL,
            xg_assist_jogador REAL,
            xg_npxg_assist_jogador REAL,

            -- Ações de Criação
            sca INTEGER,
            gca INTEGER,

            -- Passe
            passes_completos INTEGER,
            passes_tentados INTEGER,
            passes_pct REAL,
            passes_distancia_total INTEGER,
            passes_distancia_progressiva INTEGER,
            passes_curtos_completos INTEGER,
            passes_curtos_tentados INTEGER,
            passes_medios_completos INTEGER,
            passes_medios_tentados INTEGER,
            passes_longos_completos INTEGER,
            passes_longos_tentados INTEGER,
            passes_chave INTEGER,
            passes_terco_final INTEGER,
            passes_area_penal INTEGER,
            cruzamentos_area_penal INTEGER,
            
            -- Defesa
            desarmes INTEGER,
            desarmes_vencidos INTEGER,
            bloqueios INTEGER,
            chutes_bloqueados INTEGER,
            passes_bloqueados INTEGER,
            interceptacoes INTEGER,
            erros_defensivos INTEGER,
            disputas_vencidas_pct REAL,

            -- Posse
            toques INTEGER,
            toques_terco_defensivo INTEGER,
            toques_terco_medio INTEGER,
            toques_terco_ofensivo INTEGER,
            toques_area_defensiva INTEGER,
            toques_area_ofensiva INTEGER,
            dribles_tentados INTEGER,
            dribles_completos INTEGER,
            dribles_sucesso_pct REAL,
            conducoes_progressivas INTEGER,
            recepcoes_progressivas INTEGER,

            -- Diversos
            faltas_cometidas INTEGER,
            faltas_sofridas INTEGER,
            recuperacoes INTEGER,
            duelos_aereos_vencidos INTEGER,
            duelos_aereos_perdidos INTEGER,
            duelos_aereos_vencidos_pct REAL,

            UNIQUE(partida_id, jogador_nome),
            FOREIGN KEY (partida_id) REFERENCES partidas (id)
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Estrutura do banco de dados atualizada com sucesso.")

def extrair_stat(linha, stat_name, tipo=float):
    """Função auxiliar para extrair e converter uma estatística de forma segura."""
    try:
        tag = linha.find(['th', 'td'], {'data-stat': stat_name})
        # O valor numérico costuma estar no atributo 'csk' para ordenação
        valor_str = tag.get('csk', tag.text) if tag else '0'
        
        if valor_str is None or valor_str == '':
            return tipo(0)
        
        # Converte para o tipo desejado (int, float, etc.)
        return tipo(valor_str)
    except (ValueError, AttributeError, TypeError):
        return tipo(0) # Retorna 0 se o valor não for um número válido

def processar_match_report(soup, partida_id, cursor):
    """Extrai o conjunto completo de estatísticas de jogadores da página."""
    stats_coletadas = False
    
    # Mapeia o ID da tabela no HTML para o nome do time
    times_mapeados = {}
    for caption in soup.select("table[id*='_summary'] caption"):
        id_base = caption.parent['id'].replace('_summary', '')
        time_nome = caption.text.replace(" Player Stats Table", "")
        times_mapeados[id_base] = time_nome

    for id_base, time_nome in times_mapeados.items():
        # Encontra todas as tabelas de estatísticas para o time atual
        tabela_sum = soup.find('table', id=id_base + '_summary')
        tabela_pass = soup.find('table', id=id_base + '_passing')
        tabela_pass_types = soup.find('table', id=id_base + '_passing_types')
        tabela_def = soup.find('table', id=id_base + '_defense')
        tabela_poss = soup.find('table', id=id_base + '_possession')
        tabela_misc = soup.find('table', id=id_base + '_misc')
        
        # Verifica se todas as tabelas foram encontradas antes de prosseguir
        if not all([tabela_sum, tabela_pass, tabela_pass_types, tabela_def, tabela_poss, tabela_misc]):
            logging.warning(f"  -> Nem todas as tabelas de estatísticas foram encontradas para o time {time_nome}.")
            continue

        # Itera sobre cada jogador (linha) na tabela de resumo
        for i, linha_sum in enumerate(tabela_sum.find('tbody').find_all('tr')):
            try:
                minutos = extrair_stat(linha_sum, 'minutes', int)
                if minutos == 0: continue # Pula jogadores que não entraram em campo

                jogador_nome = extrair_stat(linha_sum, 'player', str)
                
                # Para garantir que temos a linha correspondente em cada tabela
                linha_pass = tabela_pass.select('tbody > tr')[i]
                linha_pass_types = tabela_pass_types.select('tbody > tr')[i]
                linha_def = tabela_def.select('tbody > tr')[i]
                linha_poss = tabela_poss.select('tbody > tr')[i]
                linha_misc = tabela_misc.select('tbody > tr')[i]
                
                # Extração de CADA estatística conforme o documento fbref_stats_complete2.md
                dados_jogador = {
                    'partida_id': partida_id, 'jogador_nome': jogador_nome, 'time_nome': time_nome,
                    'nacao': extrair_stat(linha_sum, 'nationality', str),
                    'posicao': extrair_stat(linha_sum, 'position', str),
                    'idade': extrair_stat(linha_sum, 'age', str),
                    'minutos_jogados': minutos,
                    'gols': extrair_stat(linha_sum, 'goals', int),
                    'assistencias': extrair_stat(linha_sum, 'assists', int),
                    'gols_penalti': extrair_stat(linha_sum, 'pens_made', int),
                    'penaltis_cobrados': extrair_stat(linha_sum, 'pens_att', int),
                    'cartoes_amarelos': extrair_stat(linha_sum, 'cards_yellow', int),
                    'cartoes_vermelhos': extrair_stat(linha_sum, 'cards_red', int),
                    'xg_jogador': extrair_stat(linha_sum, 'xg', float),
                    'npxg_jogador': extrair_stat(linha_sum, 'npxg', float),
                    'xg_assist_jogador': extrair_stat(linha_sum, 'xg_assist', float),
                    'xg_npxg_assist_jogador': extrair_stat(linha_sum, 'npxg_plus_xg_assist', float) - extrair_stat(linha_sum, 'npxg', float), # Cálculo
                    'sca': extrair_stat(linha_sum, 'sca', int),
                    'gca': extrair_stat(linha_sum, 'gca', int),
                    'passes_completos': extrair_stat(linha_pass, 'passes_completed', int),
                    'passes_tentados': extrair_stat(linha_pass, 'passes', int),
                    'passes_pct': extrair_stat(linha_pass, 'passes_pct', float),
                    'passes_distancia_total': extrair_stat(linha_pass, 'passes_total_distance', int),
                    'passes_distancia_progressiva': extrair_stat(linha_pass, 'passes_progressive_distance', int),
                    'passes_curtos_completos': extrair_stat(linha_pass_types, 'passes_completed_short', int),
                    'passes_curtos_tentados': extrair_stat(linha_pass_types, 'passes_short', int),
                    'passes_medios_completos': extrair_stat(linha_pass_types, 'passes_completed_medium', int),
                    'passes_medios_tentados': extrair_stat(linha_pass_types, 'passes_medium', int),
                    'passes_longos_completos': extrair_stat(linha_pass_types, 'passes_completed_long', int),
                    'passes_longos_tentados': extrair_stat(linha_pass_types, 'passes_long', int),
                    'passes_chave': extrair_stat(linha_pass_types, 'assisted_shots', int),
                    'passes_terco_final': extrair_stat(linha_pass_types, 'passes_into_final_third', int),
                    'passes_area_penal': extrair_stat(linha_pass_types, 'passes_into_penalty_area', int),
                    'cruzamentos_area_penal': extrair_stat(linha_pass_types, 'crosses_into_penalty_area', int),
                    'desarmes': extrair_stat(linha_def, 'tackles', int),
                    'desarmes_vencidos': extrair_stat(linha_def, 'tackles_won', int),
                    'bloqueios': extrair_stat(linha_def, 'blocks', int),
                    'chutes_bloqueados': extrair_stat(linha_def, 'blocked_shots', int),
                    'passes_bloqueados': extrair_stat(linha_def, 'blocked_passes', int),
                    'interceptacoes': extrair_stat(linha_def, 'interceptions', int),
                    'erros_defensivos': extrair_stat(linha_def, 'errors', int),
                    'disputas_vencidas_pct': extrair_stat(linha_def, 'tackles_interceptions', float), # Nota: este campo não é um percentual direto, é a soma. Ajustar se necessário.
                    'toques': extrair_stat(linha_poss, 'touches', int),
                    'toques_terco_defensivo': extrair_stat(linha_poss, 'touches_def_3rd', int),
                    'toques_terco_medio': extrair_stat(linha_poss, 'touches_mid_3rd', int),
                    'toques_terco_ofensivo': extrair_stat(linha_poss, 'touches_att_3rd', int),
                    'toques_area_defensiva': extrair_stat(linha_poss, 'touches_def_pen_area', int),
                    'toques_area_ofensiva': extrair_stat(linha_poss, 'touches_att_pen_area', int),
                    'dribles_tentados': extrair_stat(linha_poss, 'dribbles', int),
                    'dribles_completos': extrair_stat(linha_poss, 'dribbles_completed', int),
                    'dribles_sucesso_pct': extrair_stat(linha_poss, 'dribbles_completed_pct', float),
                    'conducoes_progressivas': extrair_stat(linha_poss, 'progressive_carries', int),
                    'recepcoes_progressivas': extrair_stat(linha_poss, 'progressive_passes_received', int),
                    'faltas_cometidas': extrair_stat(linha_misc, 'fouls', int),
                    'faltas_sofridas': extrair_stat(linha_misc, 'fouled', int),
                    'recuperacoes': extrair_stat(linha_misc, 'recoveries', int),
                    'duelos_aereos_vencidos': extrair_stat(linha_misc, 'aerials_won', int),
                    'duelos_aereos_perdidos': extrair_stat(linha_misc, 'aerials_lost', int),
                    'duelos_aereos_vencidos_pct': extrair_stat(linha_misc, 'aerials_won_pct', float)
                }

                # Cria a query de inserção dinamicamente para evitar SQL injection
                colunas = ', '.join(dados_jogador.keys())
                placeholders = ', '.join(['?'] * len(dados_jogador))
                query = f"INSERT OR REPLACE INTO estatisticas_jogador_partida ({colunas}) VALUES ({placeholders})"
                
                cursor.execute(query, tuple(dados_jogador.values()))
                stats_coletadas = True

            except Exception as e:
                logging.warning(f"  -> Erro ao extrair dados completos do jogador: {e}")

    logging.info(f"  -> Coleta de estatísticas de jogadores para '{time_nome}' concluída.")
    return stats_coletadas


def main():
    """Lê a fila de Match Reports e coleta o conjunto completo de estatísticas."""
    logging.info("🚀 Iniciando Script 3: Coleta de Estatísticas COMPLETAS...")
    setup_database_stats()
    conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, url_match_report FROM partidas WHERE status_coleta_detalhada = 'pendente'")
        partidas_a_processar = cursor.fetchall()
        logging.info(f"Encontrados {len(partidas_a_processar)} relatórios de partida pendentes.")
        
        for partida_id, url in partidas_a_processar:
            logging.info(f"\n--- Processando Partida ID {partida_id} ---")
            soup = fazer_requisicao(url)
            if soup:
                status = 'concluido' if processar_match_report(soup, partida_id, cursor) else 'sem_stats'
                cursor.execute("UPDATE partidas SET status_coleta_detalhada = ? WHERE id = ?", (status, partida_id))
                conn.commit()
        logging.info("\n✅ Script 3 (Coleta de Estatísticas Completas) finalizado!")
    finally:
        conn.close(); close_driver()

if __name__ == "__main__":
    main()