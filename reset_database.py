"""
Script para resetar completamente o banco de dados do ApostaPro.
Este script executa as seguintes etapas:
1. Conecta ao banco de dados como superusuário
2. Encerra todas as conexões ativas
3. Remove o banco de dados existente
4. Cria um novo banco de dados com a codificação correta
5. Executa o script SQL para criar tabelas e inserir dados
6. Verifica se os dados foram inseridos corretamente
"""
import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Configurações do superusuário (para operações administrativas)
ADMIN_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': 'postgres',  # Conecta ao banco padrão
    'user': 'postgres',    # Usuário admin
    'password': os.getenv('DB_ROOT_PASSWORD', 'postgres')
}

class DatabaseManager:
    """Classe para gerenciar operações no banco de dados."""
    
    def __init__(self, config):
        self.config = config
        self.conn = None
    
    def connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info(f"✅ Conectado ao banco de dados {self.config.get('dbname', '')}")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao conectar ao banco de dados: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco de dados fechada")
    
    def execute_query(self, query, params=None):
        """Executa uma consulta SQL e retorna os resultados."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                if cur.description:
                    return cur.fetchall()
                return None
        except Exception as e:
            logger.error(f"❌ Erro ao executar consulta: {e}")
            logger.error(f"Consulta: {query}")
            if params:
                logger.error(f"Parâmetros: {params}")
            raise
    
    def execute_script(self, file_path):
        """Executa um arquivo SQL."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Divide o script em comandos individuais
            commands = sql_script.split(';')
            
            with self.conn.cursor() as cur:
                for command in commands:
                    # Remove espaços em branco e verifica se o comando não está vazio
                    command = command.strip()
                    if not command:
                        continue
                    
                    try:
                        logger.debug(f"Executando comando: {command[:100]}...")
                        cur.execute(command)
                        # Tenta buscar resultados (se for uma consulta SELECT)
                        try:
                            results = cur.fetchall()
                            if results:
                                for row in results:
                                    logger.info(f"Resultado: {row}")
                        except psycopg2.ProgrammingError:
                            # Não há resultados para buscar (não é uma consulta SELECT)
                            pass
                    except Exception as e:
                        logger.error(f"❌ Erro ao executar comando: {e}")
                        logger.error(f"Comando: {command}")
                        # Continua para o próximo comando mesmo em caso de erro
                        continue
            
            logger.info("✅ Script SQL executado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar script SQL: {e}")
            return False

def reset_database():
    """Função principal para resetar o banco de dados."""
    logger.info("🚀 Iniciando processo de reset do banco de dados...")
    
    # 1. Conectar como superusuário para operações administrativas
    admin_db = DatabaseManager(ADMIN_CONFIG)
    if not admin_db.connect():
        logger.error("❌ Não foi possível conectar como superusuário")
        return 1
    
    try:
        # 2. Encerrar todas as conexões ativas
        logger.info("🔌 Encerrando conexões ativas...")
        admin_db.execute_query("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid();
        """, (DB_CONFIG['dbname'],))
        
        # 3. Remover o banco de dados existente
        logger.info(f"🗑️  Removendo banco de dados {DB_CONFIG['dbname']}...")
        admin_db.execute_query(f"DROP DATABASE IF EXISTS {DB_CONFIG['dbname']}")
        
        # 4. Criar um novo banco de dados
        logger.info(f"🆕 Criando novo banco de dados {DB_CONFIG['dbname']}...")
        admin_db.execute_query(f"""
            CREATE DATABASE {dbname}
            WITH 
            ENCODING = 'UTF8'
            LC_COLLATE = 'Portuguese_Brazil.1252'
            LC_CTYPE = 'Portuguese_Brazil.1252'
            TEMPLATE = template0;
        """.format(dbname=DB_CONFIG['dbname']))
        
        # 5. Criar o usuário da aplicação se não existir
        logger.info(f"👤 Criando/configurando usuário {DB_CONFIG['user']}...")
        admin_db.execute_query("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = %s) THEN
                    CREATE USER {} WITH PASSWORD %s;
                ELSE
                    ALTER USER {} WITH PASSWORD %s;
                END IF;
            END
            $$;
        """.format(
            psycopg2.sql.Identifier(DB_CONFIG['user']),
            psycopg2.sql.Identifier(DB_CONFIG['user'])
        ), (DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['password']))
        
        # 6. Conceder privilégios ao usuário
        admin_db.execute_query(f"""
            GRANT ALL PRIVILEGES ON DATABASE {DB_CONFIG['dbname']} TO {DB_CONFIG['user']};
        """)
        
        logger.info("✅ Banco de dados recriado com sucesso")
        
        # 7. Fechar conexão de administração
        admin_db.close()
        
        # 8. Conectar ao novo banco de dados como usuário da aplicação
        app_db = DatabaseManager(DB_CONFIG)
        if not app_db.connect():
            logger.error("❌ Não foi possível conectar ao novo banco de dados")
            return 1
        
        try:
            # 9. Executar o script SQL para criar tabelas e inserir dados
            logger.info("📝 Executando script SQL...")
            script_path = os.path.join(os.path.dirname(__file__), 'manual_db_setup.sql')
            if not os.path.exists(script_path):
                logger.error(f"❌ Arquivo {script_path} não encontrado")
                return 1
            
            if not app_db.execute_script(script_path):
                logger.error("❌ Falha ao executar o script SQL")
                return 1
            
            # 10. Verificar se os dados foram inseridos corretamente
            logger.info("🔍 Verificando dados inseridos...")
            tables = ['paises_clubes', 'clubes', 'competicoes', 'estadios', 'partidas']
            for table in tables:
                try:
                    result = app_db.execute_query(f"SELECT COUNT(*) FROM {table}")
                    if result:
                        logger.info(f"✅ Tabela {table}: {result[0][0]} registros")
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar tabela {table}: {e}")
            
            logger.info("\n✨ Processo de reset do banco de dados concluído com sucesso!")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Erro durante a execução do script SQL: {e}")
            return 1
        finally:
            app_db.close()
            
    except Exception as e:
        logger.error(f"❌ Erro durante o processo de reset do banco de dados: {e}")
        return 1
    finally:
        admin_db.close()

if __name__ == "__main__":
    sys.exit(reset_database())
