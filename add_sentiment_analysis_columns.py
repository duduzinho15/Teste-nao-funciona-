import psycopg2
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Parâmetros de conexão
params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'apostapro_user'),
    'password': os.getenv('DB_PASSWORD', 'senha_segura_123')
}

def add_sentiment_analysis_columns():
    """Adiciona as colunas de análise de sentimento à tabela noticias_clubes."""
    try:
        # Conecta ao banco de dados
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cur = conn.cursor()
        
        # SQL para adicionar as colunas
        sql_commands = [
            # Adiciona colunas de análise de sentimento
            # Adiciona colunas de análise de sentimento com comentários separados
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS sentimento_geral FLOAT;
            COMMENT ON COLUMN noticias_clubes.sentimento_geral IS 'Pontuação de sentimento entre -1 (negativo) e 1 (positivo)';
            """,
            
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS confianca_sentimento FLOAT;
            COMMENT ON COLUMN noticias_clubes.confianca_sentimento IS 'Nível de confiança da análise de sentimento (0 a 1)';
            """,
            
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS polaridade VARCHAR(20);
            COMMENT ON COLUMN noticias_clubes.polaridade IS 'Classificação geral do sentimento (positivo, negativo, neutro)';
            """,
            
            # Adiciona colunas para tópicos e palavras-chave
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS topicos VARCHAR(255);
            COMMENT ON COLUMN noticias_clubes.topicos IS 'Tópicos principais identificados na notícia (separados por vírgula)';
            """,
            
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS palavras_chave VARCHAR(500);
            COMMENT ON COLUMN noticias_clubes.palavras_chave IS 'Palavras-chave extraídas do conteúdo (separadas por vírgula)';
            """,
            
            # Adiciona metadados da análise
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS analisado_em TIMESTAMP;
            COMMENT ON COLUMN noticias_clubes.analisado_em IS 'Data e hora em que a análise de sentimento foi realizada';
            """,
            
            """
            ALTER TABLE noticias_clubes 
            ADD COLUMN IF NOT EXISTS modelo_analise VARCHAR(100);
            COMMENT ON COLUMN noticias_clubes.modelo_analise IS 'Nome/versão do modelo de análise de sentimento utilizado';
            """,
            
            # Cria índices para melhorar consultas
            """
            CREATE INDEX IF NOT EXISTS idx_noticias_sentimento 
            ON noticias_clubes(sentimento_geral)
            """,
            
            """
            CREATE INDEX IF NOT EXISTS idx_noticias_polaridade 
            ON noticias_clubes(polaridade)
            """
        ]
        
        # Executa cada comando SQL
        for i, sql in enumerate(sql_commands, 1):
            print(f"Executando comando {i}/{len(sql_commands)}...")
            try:
                cur.execute(sql)
                print(f"  ✅ Comando {i} executado com sucesso")
            except Exception as e:
                print(f"  ⚠️ Erro ao executar comando {i}: {e}")
        
        print("\n✅ Todas as alterações foram aplicadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()
            print("Conexão com o banco de dados encerrada.")

if __name__ == "__main__":
    print("=== Adicionando colunas de análise de sentimento à tabela noticias_clubes ===\n")
    add_sentiment_analysis_columns()
