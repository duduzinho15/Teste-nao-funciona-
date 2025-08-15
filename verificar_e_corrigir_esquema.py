"""
Script para verificar e corrigir o esquema do banco de dados.

Este script verifica a estrutura da tabela 'clubes' e adiciona uma restrição UNIQUE
à coluna 'nome' se ela ainda não existir.
"""

import sys
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    try:
        # Usando as mesmas configurações do DatabaseManager
        db_url = "postgresql://postgres:postgres@localhost:5432/apostapro_db"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)

def verificar_estrutura_tabela(engine, table_name):
    """Verifica a estrutura de uma tabela."""
    inspector = inspect(engine)
    
    # Verifica se a tabela existe
    if not inspector.has_table(table_name):
        logger.error(f"A tabela '{table_name}' não existe no banco de dados.")
        return False
    
    # Obtém as colunas da tabela
    logger.info(f"\nEstrutura da tabela '{table_name}':")
    columns = inspector.get_columns(table_name)
    for column in columns:
        logger.info(f"  - {column['name']}: {column['type']} (nullable: {column['nullable']})")
    
    # Obtém os índices da tabela
    logger.info(f"\nÍndices da tabela '{table_name}':")
    indexes = inspector.get_indexes(table_name)
    for index in indexes:
        logger.info(f"  - Nome: {index['name']}, Colunas: {index['column_names']}, Único: {index.get('unique', False)}")
    
    # Obtém as restrições UNIQUE da tabela
    logger.info(f"\nRestrições UNIQUE da tabela '{table_name}':")
    try:
        unique_constraints = inspector.get_unique_constraints(table_name)
        for constraint in unique_constraints:
            logger.info(f"  - Nome: {constraint['name']}, Colunas: {constraint['column_names']}")
    except Exception as e:
        logger.warning(f"Não foi possível obter as restrições UNIQUE: {e}")
    
    return True

def adicionar_constraint_unica(engine, table_name, column_name, constraint_name=None):
    """Adiciona uma restrição UNIQUE a uma coluna."""
    if not constraint_name:
        constraint_name = f"uq_{table_name}_{column_name}"
    
    with engine.connect() as conn:
        try:
            # Verifica se a restrição já existe
            result = conn.execute(
                text("""
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = :table_name 
                AND constraint_name = :constraint_name
                AND constraint_type = 'UNIQUE'
                """),
                {'table_name': table_name, 'constraint_name': constraint_name}
            ).scalar()
            
            if result:
                logger.info(f"A restrição UNIQUE '{constraint_name}' já existe na tabela '{table_name}'.")
                return True
            
            # Adiciona a restrição UNIQUE
            logger.info(f"Adicionando restrição UNIQUE '{constraint_name}' à coluna '{column_name}' da tabela '{table_name}'...")
            conn.execute(
                text(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({column_name})")
            )
            conn.commit()
            logger.info(f"Restrição UNIQUE '{constraint_name}' adicionada com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar restrição UNIQUE: {e}")
            conn.rollback()
            return False

def main():
    """Função principal."""
    logger.info("Iniciando verificação do esquema do banco de dados...")
    
    # Conecta ao banco de dados
    engine = get_db_connection()
    
    # Verifica a estrutura da tabela 'clubes'
    if not verificar_estrutura_tabela(engine, 'clubes'):
        logger.error("Não foi possível verificar a estrutura da tabela 'clubes'.")
        sys.exit(1)
    
    # Adiciona a restrição UNIQUE à coluna 'nome' da tabela 'clubes'
    if not adicionar_constraint_unica(engine, 'clubes', 'nome'):
        logger.error("Não foi possível adicionar a restrição UNIQUE à coluna 'nome' da tabela 'clubes'.")
        sys.exit(1)
    
    logger.info("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
