"""
Script simples para popular o banco de dados com dados mínimos para teste.
"""
import psycopg2
from datetime import datetime, timedelta
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
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
    """Executa uma consulta SQL e retorna o resultado"""
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao executar consulta: {e}")
        logger.error(f"Consulta: {query}")
        if params:
            logger.error(f"Parâmetros: {params}")
        return None

def insert_paises(conn):
    """Insere países na tabela paises_clubes"""
    logger.info("\n🌎 Inserindo países...")
    paises = [
        (1, 'Brasil', 'BRA', 'América do Sul'),
        (2, 'Espanha', 'ESP', 'Europa'),
        (3, 'Inglaterra', 'ENG', 'Europa'),
        (4, 'Itália', 'ITA', 'Europa'),
        (5, 'Alemanha', 'GER', 'Europa')
    ]
    
    for pais in paises:
        query = """
        INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        if not execute_query(conn, query, pais):
            return False
    
    logger.info("✅ Países inseridos com sucesso!")
    return True

def insert_competicoes(conn):
    """Insere competições na tabela competicoes"""
    logger.info("\n🏆 Inserindo competições...")
    competicoes = [
        (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A', True, 'https://example.com/brasileirao'),
        (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A', True, 'https://example.com/laliga'),
        (3, 'Premier League', 'EPL', 'Liga', 'Inglaterra', 'A', True, 'https://example.com/premierleague'),
        (4, 'Copa do Brasil', 'CdB', 'Copa', 'Brasil', 'A', True, 'https://example.com/copadobrasil'),
        (5, 'Champions League', 'UCL', 'Internacional', 'Europa', 'A', True, 'https://example.com/ucl')
    ]
    
    for competicao in competicoes:
        query = """
        INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel, ativo, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        if not execute_query(conn, query, competicao):
            return False
    
    logger.info("✅ Competições inseridas com sucesso!")
    return True

def insert_clubes(conn):
    """Insere clubes na tabela clubes"""
    logger.info("\n⚽ Inserindo clubes...")
    clubes = [
        (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15', True, 'https://example.com/flamengo.png'),
        (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29', True, 'https://example.com/barcelona.png'),
        (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06', True, 'https://example.com/realmadrid.png'),
        (4, 'Liverpool', 'LIV', 3, 'Liverpool', '1892-06-03', True, 'https://example.com/liverpool.png'),
        (5, 'Juventus', 'JUV', 4, 'Turim', '1897-11-01', True, 'https://example.com/juventus.png'),
        (6, 'Bayern de Munique', 'BAY', 5, 'Munique', '1900-02-27', True, 'https://example.com/bayern.png')
    ]
    
    for clube in clubes:
        query = """
        INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao, ativo, url_escudo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        if not execute_query(conn, query, clube):
            return False
    
    logger.info("✅ Clubes inseridos com sucesso!")
    return True

def create_table_estadios(conn):
    """Cria a tabela estadios se não existir"""
    logger.info("\n🏟️  Verificando tabela 'estadios'...")
    
    # Verifica se a tabela já existe
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'estadios'
    );
    """
    
    result = execute_query(conn, query)
    if not result:
        return False
    
    if not result[0][0]:
        logger.info("Criando tabela 'estadios'...")
        create_table_query = """
        CREATE TABLE estadios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            apelido VARCHAR(100),
            cidade VARCHAR(100),
            capacidade INTEGER,
            inauguracao DATE,
            gramado VARCHAR(50),
            clube_id INTEGER REFERENCES clubes(id) ON DELETE SET NULL,
            pais_id INTEGER REFERENCES paises_clubes(id) ON DELETE SET NULL,
            ativo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        if not execute_query(conn, create_table_query):
            return False
        logger.info("✅ Tabela 'estadios' criada com sucesso!")
    else:
        logger.info("ℹ️  Tabela 'estadios' já existe.")
    
    return True

def insert_estadios(conn):
    """Insere estádios na tabela estadios"""
    logger.info("\n🏟️  Inserindo estádios...")
    estadios = [
        (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 'Natural', 1, 1, True),
        (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 'Híbrido', 2, 2, True),
        (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 'Híbrido', 3, 2, True),
        (4, 'Anfield', 'Anfield', 'Liverpool', 53394, '1884-01-01', 'Híbrido', 4, 3, True),
        (5, 'Allianz Arena', 'Allianz', 'Munique', 75024, '2005-05-30', 'Sintético', 6, 5, True)
    ]
    
    for estadio in estadios:
        query = """
        INSERT INTO estadios (id, nome, apelido, cidade, capacidade, inauguracao, gramado, clube_id, pais_id, ativo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        if not execute_query(conn, query, estadio):
            return False
    
    logger.info("✅ Estádios inseridos com sucesso!")
    return True

def insert_partidas(conn):
    """Insere partidas na tabela partidas"""
    logger.info("\n📅 Inserindo partidas...")
    
    # Obtém a data atual
    hoje = datetime.now().date()
    
    # Partidas de exemplo
    partidas = [
        # ID, competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, temporada, gols_casa, gols_visitante, status, estadio_id, url_fbref
        (1, 1, 1, 2, hoje - timedelta(days=7), '1ª Rodada', '2024', 2, 1, 'Finalizada', 1, 'https://example.com/partida1'),
        (2, 2, 3, 4, hoje - timedelta(days=5), 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 3, 'https://example.com/partida2'),
        (3, 1, 1, 4, hoje + timedelta(days=3), '2ª Rodada', '2024', None, None, 'Agendada', 1, 'https://example.com/partida3'),
        (4, 2, 5, 3, hoje + timedelta(days=5), 'Jogo 11', '2023/2024', None, None, 'Agendada', 5, 'https://example.com/partida4')
    ]
    
    for partida in partidas:
        query = """
        INSERT INTO partidas (
            id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, 
            rodada, temporada, gols_casa, gols_visitante, status, estadio_id, url_fbref
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        if not execute_query(conn, query, partida):
            return False
    
    logger.info("✅ Partidas inseridas com sucesso!")
    return True

def insert_estatisticas_partidas(conn):
    """Insere estatísticas para as partidas finalizadas"""
    logger.info("\n📊 Inserindo estatísticas de partidas...")
    
    # Estatísticas para as partidas finalizadas (IDs 1 e 2)
    estatisticas = [
        # partida_id, posse_bola_casa, posse_bola_visitante, finalizacoes_totais_casa, finalizacoes_totais_visitante,
        # finalizacoes_no_alvo_casa, finalizacoes_no_alvo_visitante, defesas_casa, defesas_visitante,
        # escanteios_casa, escanteios_visitante, faltas_casa, faltas_visitante, impedimentos_casa,
        # impedimentos_visitante, tiro_meta_casa, tiro_meta_visitante, defesas_do_goleiro_casa,
        # defesas_do_goleiro_visitante, cartoes_amarelos_casa, cartoes_amarelos_visitante,
        # cartoes_vermelhos_casa, cartoes_vermelhos_visitante
        (1, 55, 45, 15, 10, 7, 4, 3, 5, 6, 4, 12, 14, 2, 1, 4, 5, 4, 3, 2, 1, 0, 0),
        (2, 48, 52, 12, 14, 5, 6, 5, 4, 5, 7, 10, 12, 1, 3, 6, 4, 6, 5, 3, 4, 0, 1)
    ]
    
    for estatistica in estatisticas:
        query = """
        INSERT INTO estatisticas_partidas (
            partida_id, posse_bola_casa, posse_bola_visitante, finalizacoes_totais_casa, 
            finalizacoes_totais_visitante, finalizacoes_no_alvo_casa, finalizacoes_no_alvo_visitante,
            defesas_casa, defesas_visitante, escanteios_casa, escanteios_visitante,
            faltas_casa, faltas_visitante, impedimentos_casa, impedimentos_visitante,
            tiro_meta_casa, tiro_meta_visitante, defesas_do_goleiro_casa,
            defesas_do_goleiro_visitante, cartoes_amarelos_casa, cartoes_amarelos_visitante,
            cartoes_vermelhos_casa, cartoes_vermelhos_visitante
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (partida_id) DO NOTHING;
        """
        if not execute_query(conn, query, estatistica):
            return False
    
    logger.info("✅ Estatísticas de partidas inseridas com sucesso!")
    return True

def main():
    """Função principal para popular o banco de dados"""
    logger.info("🚀 Iniciando o processo de seed do banco de dados...")
    
    # Conecta ao banco de dados
    conn = connect_db()
    if not conn:
        return False
    
    try:
        # Executa as funções de inserção em sequência
        if not insert_paises(conn):
            return False
        
        if not insert_competicoes(conn):
            return False
        
        if not insert_clubes(conn):
            return False
        
        if not create_table_estadios(conn):
            return False
        
        if not insert_estadios(conn):
            return False
        
        if not insert_partidas(conn):
            return False
        
        if not insert_estatisticas_partidas(conn):
            return False
        
        logger.info("\n✨ Processo de seed concluído com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o processo de seed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if main():
        logger.info("✅ Banco de dados populado com sucesso!")
    else:
        logger.error("❌ Falha ao popular o banco de dados")
