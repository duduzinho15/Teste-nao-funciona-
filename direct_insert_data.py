"""
Script para inserir dados diretamente nas tabelas usando psycopg2.
"""
import psycopg2
import logging
from datetime import datetime, timedelta

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
    "user": "postgres",  # Usuário com privilégios
    "password": "postgres",  # Senha do usuário postgres
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
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao executar consulta: {e}")
        logger.error(f"Consulta: {query}")
        if params:
            logger.error(f"Parâmetros: {params}")
        return False

def table_exists(conn, table_name):
    """Verifica se uma tabela existe"""
    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s
    );
    """
    result = execute_query(conn, query, (table_name,))
    return result[0][0] if result else False

def create_estadios_table(conn):
    """Cria a tabela estadios se não existir"""
    if table_exists(conn, 'estadios'):
        logger.info("✅ Tabela 'estadios' já existe")
        return True
    
    logger.info("🔄 Criando tabela 'estadios'...")
    
    query = """
    CREATE TABLE estadios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        apelido VARCHAR(100),
        cidade VARCHAR(100),
        capacidade INTEGER,
        inauguracao DATE,
        gramado VARCHAR(50),
        clube_id INTEGER,
        pais_id INTEGER,
        ativo BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        FOREIGN KEY (clube_id) REFERENCES clubes(id) ON DELETE SET NULL,
        FOREIGN KEY (pais_id) REFERENCES paises_clubes(id) ON DELETE SET NULL
    );
    """
    
    return execute_query(conn, query)

def insert_initial_data(conn):
    """Insere dados iniciais nas tabelas"""
    logger.info("🔄 Inserindo dados iniciais...")
    
    # 1. Inserir países
    logger.info("🌎 Inserindo países...")
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
        execute_query(conn, query, pais)
    
    # 2. Inserir competições
    logger.info("🏆 Inserindo competições...")
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
        execute_query(conn, query, competicao)
    
    # 3. Inserir clubes
    logger.info("⚽ Inserindo clubes...")
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
        execute_query(conn, query, clube)
    
    # 4. Inserir estádios
    logger.info("🏟️ Inserindo estádios...")
    estadios = [
        (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, '1950-06-16', 'Natural', 1, 1, True),
        (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, '1957-09-24', 'Natural', 2, 2, True),
        (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, '1947-12-14', 'Híbrido', 3, 2, True)
    ]
    
    for estadio in estadios:
        query = """
        INSERT INTO estadios (id, nome, apelido, cidade, capacidade, 
                            inauguracao, gramado, clube_id, pais_id, ativo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        execute_query(conn, query, estadio)
    
    # 5. Inserir partidas
    logger.info("📅 Inserindo partidas...")
    hoje = datetime.now().date()
    partidas = [
        (1, 1, 1, 2, hoje - timedelta(days=7), '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
        (2, 2, 2, 3, hoje - timedelta(days=5), 'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2),
        (3, 1, 1, 3, hoje + timedelta(days=3), '2ª Rodada', '2024', None, None, 'Agendada', 1)
    ]
    
    for partida in partidas:
        query = """
        INSERT INTO partidas (
            id, competicao_id, clube_casa_id, clube_visitante_id, 
            data_partida, rodada, temporada, 
            gols_casa, gols_visitante, status, estadio_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """
        execute_query(conn, query, partida)
    
    logger.info("✅ Dados iniciais inseridos com sucesso!")
    return True

def check_data(conn):
    """Verifica se os dados foram inseridos corretamente"""
    logger.info("\n🔍 Verificando dados inseridos...")
    
    tables = ['paises_clubes', 'clubes', 'competicoes', 'estadios', 'partidas']
    
    for table in tables:
        if not table_exists(conn, table):
            logger.warning(f"⚠️  Tabela '{table}' não existe")
            continue
        
        query = f"SELECT COUNT(*) FROM {table};"
        result = execute_query(conn, query)
        
        if result:
            logger.info(f"📊 Tabela '{table}': {result[0][0]} registros")
        else:
            logger.warning(f"⚠️  Não foi possível contar registros na tabela '{table}'")

def main():
    """Função principal"""
    logger.info("🚀 Iniciando inserção de dados...")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        # Cria a tabela estadios se não existir
        if not create_estadios_table(conn):
            logger.error("❌ Falha ao criar a tabela 'estadios'")
            return
        
        # Insere os dados iniciais
        if not insert_initial_data(conn):
            logger.error("❌ Falha ao inserir dados iniciais")
            return
        
        # Verifica os dados inseridos
        check_data(conn)
        
        logger.info("\n✨ Processo concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante o processo: {e}")
    finally:
        conn.close()
        logger.info("🔒 Conexão com o banco de dados encerrada")

if __name__ == "__main__":
    main()
