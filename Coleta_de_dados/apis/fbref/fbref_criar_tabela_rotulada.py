import sqlite3
import pandas as pd
import logging
import os # Importe a biblioteca OS

# --- CONFIGURAÇÕES COM CAMINHO ABSOLUTO ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logger = logging.getLogger(__name__)

OUTPUT_TABLE_NAME = 'dados_rotulados_partidas'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')

def criar_dataframe_rotulado(dados):
    if not dados:
        return pd.DataFrame()
    tamanhos = [len(v) for v in dados.values()]
    if len(set(tamanhos)) != 1:
        raise ValueError("Columns must be same length as key")
    return pd.DataFrame(dados)

def extrair_placar(placar_str):
    """Extrai gols de casa e visitante de um placar como '3–1'."""
    try:
        gols_casa, gols_visitante = map(int, placar_str.replace('–', '-').strip().split('-'))
        return gols_casa, gols_visitante
    except (ValueError, AttributeError):
        return None, None

def rotular_resultado(gols_casa, gols_visitante):
    """Rotula o resultado da partida: 1 (vitória casa), 0 (empate), 2 (vitória visitante)."""
    if gols_casa is None: return None
    if gols_casa > gols_visitante: return 1
    if gols_casa == gols_visitante: return 0
    return 2

def main():
    """Orquestra o processo de ler dados brutos, processar, rotular e salvar o resultado final."""
    logging.info(f"🚀 Iniciando Script 4: Processamento e Rotulação de Dados...")
    try:
        conn = sqlite3.connect(DB_NAME)

        # Carrega os dados das partidas e as estatísticas agregadas dos times
        query = """
            SELECT
                p.id as partida_id,
                p.placar,
                stats_casa.xg as xg_casa,
                stats_visit.xg as xg_visitante
            FROM partidas p
            JOIN estatisticas_time_partida stats_casa ON p.id = stats_casa.partida_id AND p.time_casa = stats_casa.time_nome
            JOIN estatisticas_time_partida stats_visit ON p.id = stats_visit.partida_id AND p.time_visitante = stats_visit.time_nome
        """

        df = pd.read_sql_query(query, conn)
        logging.info(f"Carregados {len(df)} registros de partidas com estatísticas completas.")

        # 1. Processa o placar para obter gols
        df[['gols_casa', 'gols_visitante']] = df['placar'].apply(lambda x: pd.Series(extrair_placar(x)))

        # 2. Rotula o resultado final da partida
        df['resultado_final'] = df.apply(lambda row: rotular_resultado(row['gols_casa'], row['gols_visitante']), axis=1)

        # 3. Limpa dados inválidos e seleciona colunas finais
        df_final = df.dropna(subset=['resultado_final'])
        df_final = df_final[['partida_id', 'gols_casa', 'gols_visitante', 'xg_casa', 'xg_visitante', 'resultado_final']]

        logging.info(f"Processamento concluído. A tabela final contém {len(df_final)} linhas.")

        # 4. Salva a tabela processada de volta no banco de dados
        df_final.to_sql(OUTPUT_TABLE_NAME, conn, if_exists='replace', index=False)
        logging.info(f"✅ SUCESSO! Tabela '{OUTPUT_TABLE_NAME}' salva no banco de dados.")

    except Exception as e:
        logging.error(f"Ocorreu um erro durante o processamento: {e}")
    finally:
        if 'conn' in locals() and conn: conn.close()

if __name__ == "__main__":
    main()
