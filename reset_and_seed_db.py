"""
Script para recriar o banco de dados e popular com dados iniciais.
"""
import psycopg2
import os
import subprocess
from dotenv import load_dotenv
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Executa um comando no shell e retorna a saída"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar comando: {e}")
        logger.error(f"Saída de erro: {e.stderr}")
        return None

def create_database():
    """Cria o banco de dados se não existir"""
    # Conecta ao banco de dados padrão 'postgres'
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_ROOT_USER', 'postgres'),
        password=os.getenv('DB_ROOT_PASSWORD', 'postgres'),
        dbname='postgres'
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            # Verifica se o banco de dados já existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", 
                       (os.getenv('DB_NAME', 'apostapro_db'),))
            exists = cur.fetchone()
            
            if not exists:
                logger.info("Criando banco de dados...")
                # Constrói a consulta SQL com parâmetros para evitar injeção SQL
                db_name = os.getenv('DB_NAME', 'apostapro_db')
                cur.execute(
                    "CREATE DATABASE %s WITH ENCODING='UTF8' LC_COLLATE='pt_BR.UTF-8' LC_CTYPE='pt_BR.UTF-8' TEMPLATE=template0",
                    (db_name,)
                )
                logger.info("✅ Banco de dados criado com sucesso!")
            else:
                logger.info("ℹ️  O banco de dados já existe.")
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco de dados: {e}")
        return False
    finally:
        conn.close()
    
    return True

def run_migrations():
    """Executa as migrações do Alembic"""
    logger.info("\nExecutando migrações do Alembic...")
    
    # Ativa o ambiente virtual (se estiver usando)
    # activate_cmd = ".venv\\Scripts\\activate" if os.name == 'nt' else "source .venv/bin/activate"
    
    # Executa as migrações
    result = run_command("alembic upgrade head")
    
    if result:
        logger.info("✅ Migrações aplicadas com sucesso!")
        return True
    else:
        logger.error("❌ Falha ao aplicar migrações")
        return False

def insert_test_data():
    """Insere dados de teste no banco de dados"""
    logger.info("\nInserindo dados de teste...")
    
    # Conecta ao banco de dados
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'apostapro_user'),
        password=os.getenv('DB_PASSWORD', 'senha_segura_123'),
        dbname=os.getenv('DB_NAME', 'apostapro_db')
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            # Inserir países
            logger.info("Inserindo países...")
            cur.execute("""
                INSERT INTO paises_clubes (id, nome, codigo_iso, continente)
                VALUES 
                    (1, 'Brasil', 'BRA', 'América do Sul'),
                    (2, 'Espanha', 'ESP', 'Europa'),
                    (3, 'Inglaterra', 'ENG', 'Europa')
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Inserir competições
            logger.info("Inserindo competições...")
            cur.execute("""
                INSERT INTO competicoes (id, nome, nome_curto, tipo, pais, nivel)
                VALUES 
                    (1, 'Campeonato Brasileiro Série A', 'Brasileirão', 'Liga', 'Brasil', 'A'),
                    (2, 'La Liga', 'LaLiga', 'Liga', 'Espanha', 'A')
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Inserir clubes
            logger.info("Inserindo clubes...")
            cur.execute("""
                INSERT INTO clubes (id, nome, abreviacao, pais_id, cidade, fundacao)
                VALUES 
                    (1, 'Flamengo', 'FLA', 1, 'Rio de Janeiro', '1895-11-15'),
                    (2, 'Barcelona', 'BAR', 2, 'Barcelona', '1899-11-29'),
                    (3, 'Real Madrid', 'RMA', 2, 'Madrid', '1902-03-06')
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Verificar se a tabela de estádios existe
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'estadios'
                );
            """)
            
            estadios_table_exists = cur.fetchone()[0]
            
            if not estadios_table_exists:
                logger.info("Criando tabela de estádios...")
                cur.execute("""
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
                """)
            
            # Inserir estádios
            logger.info("Inserindo estádios...")
            cur.execute("""
                INSERT INTO estadios (id, nome, apelido, cidade, capacidade, 
                                   inauguracao, gramado, clube_id, pais_id, ativo)
                VALUES 
                    (1, 'Maracanã', 'Maraca', 'Rio de Janeiro', 78838, 
                     '1950-06-16', 'Natural', 1, 1, TRUE),
                    (2, 'Camp Nou', 'Camp Nou', 'Barcelona', 99354, 
                     '1957-09-24', 'Natural', 2, 2, TRUE),
                    (3, 'Santiago Bernabéu', 'Bernabéu', 'Madrid', 81044, 
                     '1947-12-14', 'Híbrido', 3, 2, TRUE)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Inserir partidas
            logger.info("Inserindo partidas...")
            cur.execute("""
                INSERT INTO partidas (
                    id, competicao_id, clube_casa_id, clube_visitante_id, 
                    data_partida, rodada, temporada, 
                    gols_casa, gols_visitante, status, estadio_id
                )
                VALUES 
                    (1, 1, 1, 2, CURRENT_DATE - INTERVAL '7 days', 
                     '1ª Rodada', '2024', 2, 1, 'Finalizada', 1),
                    (2, 2, 2, 3, CURRENT_DATE - INTERVAL '5 days', 
                     'Jogo 10', '2023/2024', 1, 1, 'Finalizada', 2),
                    (3, 1, 1, 3, CURRENT_DATE + INTERVAL '3 days', 
                     '2ª Rodada', '2024', NULL, NULL, 'Agendada', 1)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            logger.info("✅ Dados de teste inseridos com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados de teste: {e}")
        return False
    finally:
        conn.close()

def main():
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    logger.info("🚀 Iniciando processo de reset do banco de dados...")
    
    # 1. Criar banco de dados se não existir
    if not create_database():
        logger.error("❌ Falha ao criar o banco de dados")
        return
    
    # 2. Executar migrações do Alembic
    if not run_migrations():
        logger.error("❌ Falha ao executar migrações")
        return
    
    # 3. Inserir dados de teste
    if not insert_test_data():
        logger.error("❌ Falha ao inserir dados de teste")
        return
    
    logger.info("\n✨ Processo concluído com sucesso!")
    logger.info("✅ Banco de dados recriado e populado com sucesso!")

if __name__ == "__main__":
    main()
