#!/usr/bin/env python3
"""
Script para verificar a existência e acessibilidade do banco de dados
"""
import psycopg2
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
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
        logger.info(f"✅ Conexão bem-sucedida com o banco '{dbname}'")
        return conn
    except Exception as e:
        logger.warning(f"❌ Falha na conexão com '{dbname}': {str(e).split('(')[0]}")
        return None

def check_tables(conn):
    """Verifica as tabelas no banco de dados"""
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            # Verifica tabelas existentes
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            if tables:
                logger.info("\n📋 Tabelas encontradas:")
                for table in tables:
                    logger.info(f"- {table}")
                    
                    # Conta registros em cada tabela
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM \"{table}\"")
                        count = cur.fetchone()[0]
                        logger.info(f"  • Registros: {count}")
                    except Exception as e:
                        logger.warning(f"  • Erro ao contar registros: {str(e).split('(')[0]}")
            else:
                logger.warning("ℹ️ Nenhuma tabela encontrada no banco de dados.")
                
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabelas: {str(e).split('(')[0]}")
    finally:
        conn.close()

def main():
    # Configurações
    configs = [
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "Canjica@@2025"},
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "@Eduardo123"},
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "apostapro_pass"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "Canjica@@2025"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "postgres"}
    ]
    
    logger.info("🔍 Iniciando verificação do banco de dados...\n")
    
    for cfg in configs:
        logger.info(f"🔗 Tentando conectar: postgresql://{cfg['user']}:******@{cfg['host']}/{cfg['dbname']}")
        conn = test_connection(**cfg)
        if conn:
            check_tables(conn)
            break
    else:
        logger.error("❌ Todas as tentativas de conexão falharam.")

if __name__ == "__main__":
    main()
