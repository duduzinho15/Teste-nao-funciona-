#!/usr/bin/env python3
"""
Script para verificar a conexão com o banco de dados e listar tabelas.
"""
import os
import logging
from sqlalchemy import create_engine, inspect

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Lista de senhas para tentar
    passwords = ["Canjica@@2025", "@Eduardo123", "apostapro_pass", "postgres"]
    
    # Tenta conectar com cada senha
    for password in passwords:
        try:
            DATABASE_URL = f'postgresql://postgres:{password}@localhost:5432/postgres'
    
            logger.info(f"Tentando conectar com a senha: {'*' * len(password)}")
            # Tenta conectar ao banco de dados
            engine = create_engine(DATABASE_URL)
            # Testa a conexão
            with engine.connect() as test_conn:
                test_conn.execute(text("SELECT 1"))
        with engine.connect() as conn:
            logger.info("Conexão com o banco de dados estabelecida com sucesso!")
            
            # Lista todos os bancos de dados
            logger.info("Listando bancos de dados disponíveis:")
            result = conn.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            for row in result:
                print(f"- {row[0]}")
            
            # Verifica se o banco apostapro existe
            result = conn.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro'")
            if result.scalar() == 1:
                logger.info("\nO banco de dados 'apostapro' existe.")
                
                # Lista as tabelas no banco apostapro
                logger.info("\nListando tabelas no banco 'apostapro':")
                conn.execute("SET search_path TO public;")
                result = conn.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE';
                """)
                
                tables = [row[0] for row in result]
                if tables:
                    for table in tables:
                        print(f"- {table}")
                else:
                    logger.warning("Nenhuma tabela encontrada no banco 'apostapro'.")
            else:
                logger.warning("O banco de dados 'apostapro' não existe.")
                
            # Se chegou aqui, a conexão foi bem-sucedida
            logger.info(f"Conexão bem-sucedida com a senha: {'*' * len(password)}")
            break
        except Exception as e:
            logger.warning(f"Falha ao conectar com a senha: {'*' * len(password)} - {str(e).split('(')[0]}")
            continue
    else:
        logger.error("Todas as tentativas de conexão falharam")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("Verificando banco de dados...")
    if main():
        logger.info("Verificação concluída com sucesso!")
    else:
        logger.error("Falha ao verificar o banco de dados.")
