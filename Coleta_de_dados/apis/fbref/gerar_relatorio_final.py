import sqlite3
import pandas as pd
import logging
import os # Importe a biblioteca OS

# --- CONFIGURAÇÕES COM CAMINHO ABSOLUTO ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
DB_NAME = os.path.join(PROJECT_ROOT, 'Banco_de_dados', 'aposta.db')
logger = logging.getLogger(__name__)

OUTPUT_CSV_NAME = os.path.join(PROJECT_ROOT, 'relatorio_geral_coleta.csv')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')

def main():
    """
    Gera um relatório CSV consolidado a partir do estado final do banco de dados.
    """
    logging.info("🚀 Iniciando a geração do relatório final de coleta...")
    
    if not os.path.exists(DB_NAME):
        logging.error(f"O arquivo de banco de dados não foi encontrado em: {DB_NAME}")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        
        # Query SQL para agregar os dados de todas as tabelas relevantes
        query = """
        SELECT
            c.nome AS "Nome da Competição",
            COUNT(DISTINCT l.id) AS "Total de Links de Temporada Encontrados",
            
            SUM(CASE WHEN l.status_coleta = 'concluido' THEN 1 ELSE 0 END) AS "Links Processados (Etapa 2)",
            SUM(CASE WHEN l.status_coleta = 'sem_partidas' THEN 1 ELSE 0 END) AS "Links Sem Partidas (Etapa 2)",
            
            COUNT(DISTINCT p.id) AS "Total de Partidas Coletadas (Etapa 2)",
            
            SUM(CASE WHEN p.status_coleta_detalhada = 'concluido' THEN 1 ELSE 0 END) AS "Partidas com Estatísticas (Etapa 3)",
            SUM(CASE WHEN p.status_coleta_detalhada = 'sem_stats' THEN 1 ELSE 0 END) AS "Partidas Sem Estatísticas (Etapa 3)"
            
        FROM competicoes c
        LEFT JOIN links_para_coleta l ON c.id = l.competicao_id
        LEFT JOIN partidas p ON l.id = p.link_coleta_id
        GROUP BY c.nome
        ORDER BY c.nome;
        """
        
        # Executa a query e carrega o resultado em um DataFrame do Pandas
        df_relatorio = pd.read_sql_query(query, conn)
        
        logging.info(f"Dados de {len(df_relatorio)} competições agregados.")

        # Salva o DataFrame em um arquivo CSV
        # O encoding 'utf-8-sig' garante a compatibilidade com acentos no Excel
        df_relatorio.to_csv(OUTPUT_CSV_NAME, index=False, encoding='utf-8-sig')
        
        logging.info(f"✅ SUCESSO! Relatório final salvo em: {OUTPUT_CSV_NAME}")

    except Exception as e:
        logging.error(f"Ocorreu um erro ao gerar o relatório: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()