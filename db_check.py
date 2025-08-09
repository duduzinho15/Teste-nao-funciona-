#!/usr/bin/env python3
"""
Script simples para verificar a conexão com o PostgreSQL
"""
import psycopg2
from psycopg2 import sql
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection(host, dbname, user, password):
    """Testa a conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )
        logger.info(f"Conexão bem-sucedida com {dbname} usando a senha: {password[:2]}...")
        
        # Lista as tabelas
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            if tables:
                logger.info("\nTabelas encontradas:")
                for table in tables:
                    print(f"- {table[0]}")
            else:
                logger.warning("Nenhuma tabela encontrada no banco de dados.")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.warning(f"Falha na conexão: {str(e).split('(')[0]}")
        return False

def main():
    # Configurações
    host = "localhost"
    dbname = "postgres"  # Tenta primeiro o banco padrão
    user = "postgres"
    passwords = ["Canjica@@2025", "@Eduardo123", "apostapro_pass", "postgres"]
    
    # Tenta conectar com cada senha
    for password in passwords:
        logger.info(f"\nTentando conectar com a senha: {password[:2]}...")
        if test_connection(host, dbname, user, password):
            # Se conectou, tenta o banco apostapro
            if dbname != "apostapro":
                if test_connection(host, "apostapro", user, password):
                    logger.info("Banco 'apostapro' encontrado e acessível!")
            return
    
    logger.error("Todas as tentativas de conexão falharam.")

if __name__ == "__main__":
    logger.info("Iniciando verificação do banco de dados...")
    main()
