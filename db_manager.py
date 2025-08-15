"""
Script para gerenciar o banco de dados do ApostaPro.
Permite criar, recriar e popular o banco de dados com dados iniciais.
"""
import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'apostapro_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

class DatabaseManager:
    """Classe para gerenciar operações no banco de dados."""
    
    def __init__(self):
        self.conn = None
        self.admin_conn = None
    
    def connect_as_admin(self):
        """Conecta ao PostgreSQL como superusuário."""
        try:
            # Usa as credenciais do usuário postgres para operações administrativas
            admin_config = {
                'dbname': 'postgres',  # Conecta ao banco padrão
                'user': 'postgres',    # Usuário admin
                'password': os.getenv('DB_ROOT_PASSWORD', 'postgres'),
                'host': DB_CONFIG['host'],
                'port': DB_CONFIG['port']
            }
            self.admin_conn = psycopg2.connect(**admin_config)
            self.admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("✅ Conectado ao PostgreSQL como administrador")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao conectar como administrador: {e}")
            return False
    
    def connect(self):
        """Conecta ao banco de dados."""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = True
            logger.info(f"✅ Conectado ao banco de dados {DB_CONFIG['dbname']}")
            return True
        except Exception as e:
            logger.error(f"❌ Falha ao conectar ao banco de dados: {e}")
            return False
    
    def close(self):
        """Fecha as conexões com o banco de dados."""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com o banco de dados fechada")
        if self.admin_conn:
            self.admin_conn.close()
            logger.info("Conexão de administração fechada")
    
    def drop_database(self):
        """Remove o banco de dados se ele existir."""
        if not self.admin_conn:
            if not self.connect_as_admin():
                return False
        
        try:
            with self.admin_conn.cursor() as cur:
                # Encerra todas as conexões ativas
                logger.info("Encerrando conexões ativas...")
                cur.execute("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid();
                """, (DB_CONFIG['dbname'],))
                
                # Remove o banco de dados
                logger.info(f"Removendo banco de dados {DB_CONFIG['dbname']}...")
                cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
                    sql.Identifier(DB_CONFIG['dbname']))
                )
                logger.info("✅ Banco de dados removido com sucesso")
                return True
        except Exception as e:
            logger.error(f"❌ Falha ao remover banco de dados: {e}")
            return False
    
    def create_database(self):
        """Cria um novo banco de dados com codificação UTF-8."""
        if not self.admin_conn:
            if not self.connect_as_admin():
                return False
        
        try:
            with self.admin_conn.cursor() as cur:
                logger.info(f"Criando banco de dados {DB_CONFIG['dbname']}...")
                # Usando psycopg2.sql para evitar injeção SQL
                query = sql.SQL("""
                    CREATE DATABASE {dbname}
                    WITH 
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'pt_BR.UTF-8'
                    LC_CTYPE = 'pt_BR.UTF-8'
                    TEMPLATE = template0;
                """).format(
                    dbname=sql.Identifier(DB_CONFIG['dbname'])
                )
                cur.execute(query)
                
                # Cria o usuário se não existir
                cur.execute("""
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
                    sql.Identifier(DB_CONFIG['user']),  # Nome do usuário
                ), (DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['password']))
                
                # Concede privilégios
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                    sql.Identifier(DB_CONFIG['dbname']),
                    sql.Identifier(DB_CONFIG['user'])
                ))
                
                logger.info("✅ Banco de dados criado com sucesso")
                return True
        except Exception as e:
            logger.error(f"❌ Falha ao criar banco de dados: {e}")
            return False
    
    def run_sql_file(self, file_path):
        """Executa um arquivo SQL."""
        if not self.conn:
            if not self.connect():
                return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_commands = f.read()
            
            with self.conn.cursor() as cur:
                logger.info(f"Executando arquivo SQL: {file_path}")
                cur.execute(sql_commands)
                self.conn.commit()
                logger.info("✅ Arquivo SQL executado com sucesso")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao executar arquivo SQL: {e}")
            return False
    
    def run_alembic_migrations(self):
        """Executa as migrações do Alembic."""
        try:
            logger.info("Executando migrações do Alembic...")
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                logger.info("✅ Migrações do Alembic aplicadas com sucesso")
                logger.debug(f"Saída: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Falha ao executar migrações do Alembic: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao executar migrações do Alembic: {e}")
            return False

def main():
    """Função principal."""
    db_manager = DatabaseManager()
    
    try:
        # 1. Remover banco de dados existente
        logger.info("\n🚀 Iniciando processo de reset do banco de dados...")
        if not db_manager.drop_database():
            logger.error("❌ Não foi possível remover o banco de dados existente")
            return 1
        
        # 2. Criar novo banco de dados
        if not db_manager.create_database():
            logger.error("❌ Não foi possível criar o banco de dados")
            return 1
        
        # 3. Executar migrações do Alembic
        if not db_manager.run_alembic_migrations():
            logger.error("❌ Não foi possível executar as migrações do Alembic")
            return 1
        
        # 4. Executar script SQL de configuração
        script_path = os.path.join(os.path.dirname(__file__), 'setup_db.sql')
        if os.path.exists(script_path):
            if not db_manager.run_sql_file(script_path):
                logger.error("❌ Não foi possível executar o script de configuração")
                return 1
        else:
            logger.warning(f"⚠️  Arquivo {script_path} não encontrado. Pulando execução do script SQL.")
        
        logger.info("\n✨ Processo concluído com sucesso!")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        db_manager.close()

if __name__ == "__main__":
    sys.exit(main())
