"""
Script para inserir dados mínimos nas tabelas necessárias para testar o endpoint /matches.
Versão simplificada para evitar timeouts.
"""
import psycopg2
import logging
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "database": "apostapro_db",
    "user": "apostapro_user",
    "password": "senha_segura_123",
    "port": "5432"
}

def connect_db():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        logger.info("✅ Conexão com o banco de dados estabelecida")
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def execute_query(conn, query, params=None):
    """Executa uma consulta SQL"""
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao executar consulta: {e}")
        logger.error(f"Consulta: {query}")
        if params:
            logger.error(f"Parâmetros: {params}")
        return False

def insert_minimal_data():
    """Insere dados mínimos nas tabelas necessárias"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        # 1. Inserir países
        logger.info("\n🌎 Inserindo países...")
        paises = [
            (1, 'Brasil', 'BRA', 'América do Sul'),
            (2, 'Espanha', 'ESP', 'Europa'),
            (3, 'Inglaterra', 'ENG', 'Europa')
        ]
        
        for pais in paises:
            query = """
            INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            if not execute_query(conn, query, pais):
                logger.error(f"Falha ao inserir país: {pais}")
        
        # 2. Inserir competições
        logger.info("\n🏆 Inserindo competições...")
        competicoes = [
            (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
            (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A')
        ]
        
        for competicao in competicoes:
            query = """
            INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            if not execute_query(conn, query, competicao):
                logger.error(f"Falha ao inserir competição: {competicao}")
        
        # 3. Inserir clubes
        logger.info("\n⚽ Inserindo clubes...")
        clubes = [
            (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
            (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
            (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06')
        ]
        
        for clube in clubes:
            query = """
            INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            if not execute_query(conn, query, clube):
                logger.error(f"Falha ao inserir clube: {clube}")
        
        # 4. Inserir estádios
        logger.info("\n🏟️  Inserindo estádios...")
        estadios = [
            (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 1, 1),
            (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 2, 2),
            (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 3, 2)
        ]
        
        for estadio in estadios:
            query = """
            INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, clube_id, pais_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            if not execute_query(conn, query, estadio):
                logger.error(f"Falha ao inserir estádio: {estadio}")
        
        # 5. Inserir partidas
        logger.info("\n📅 Inserindo partidas...")
        hoje = datetime.now().date()
        partidas = [
            (1, 1, 1, 2, hoje - timedelta(days=7), '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
            (2, 2, 2, 3, hoje - timedelta(days=5), 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2)
        ]
        
        for partida in partidas:
            query = """
            INSERT INTO partidas (
                id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, 
                rodada, temporada, gols_casa, gols_visitante, status, estadio_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            if not execute_query(conn, query, partida):
                logger.error(f"Falha ao inserir partida: {partida}")
        
        logger.info("\n✨ Dados mínimos inseridos com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o processo de inserção: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🚀 Iniciando a inserção de dados mínimos...")
    if insert_minimal_data():
        logger.info("✅ Processo concluído com sucesso!")
    else:
        logger.error("❌ Ocorreram erros durante o processo.")
