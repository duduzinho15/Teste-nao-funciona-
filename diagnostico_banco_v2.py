#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar a conexão com o banco de dados PostgreSQL
"""
import sys
import os
import logging
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configurações de conexão
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "@Eduardo123",
    "port": "5432"
}

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        logger.info("Testando conexão com o banco de dados...")
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        conn.set_client_encoding('UTF8')
        logger.info("✅ Conexão bem-sucedida!")
        return conn
    except Exception as e:
        logger.error(f"❌ Falha ao conectar ao banco de dados: {e}")
        return None

def verificar_banco(conn):
    """Verifica se o banco de dados apostapro_db existe"""
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro_db'")
            exists = cur.fetchone()
            if exists:
                logger.info("✅ Banco de dados 'apostapro_db' encontrado")
                return True
            else:
                logger.warning("⚠️ Banco de dados 'apostapro_db' não encontrado")
                return False
    except Exception as e:
        logger.error(f"❌ Erro ao verificar banco de dados: {e}")
        return False

def verificar_tabelas(conn, db_name):
    """Verifica se as tabelas necessárias existem no banco de dados"""
    try:
        # Conecta ao banco específico
        conn_db = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=db_name,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        conn_db.set_client_encoding('UTF8')
        
        with conn_db.cursor() as cur:
            # Verifica tabelas necessárias
            tabelas = ['paises_clubes', 'clubes']
            for tabela in tabelas:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                    """,
                    (tabela,)
                )
                if cur.fetchone()[0]:
                    logger.info(f"✅ Tabela '{tabela}' encontrada")
                else:
                    logger.warning(f"⚠️ Tabela '{tabela}' não encontrada")
        
        conn_db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao verificar tabelas: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🔍 Iniciando diagnóstico do banco de dados...")
    
    # Testa a conexão inicial
    conn = testar_conexao()
    if not conn:
        logger.error("❌ Não foi possível continuar o diagnóstico")
        return
    
    # Verifica se o banco de dados existe
    db_exists = verificar_banco(conn)
    
    if db_exists:
        # Se o banco existe, verifica as tabelas
        verificar_tabelas(conn, 'apostapro_db')
    
    conn.close()
    logger.info("✅ Diagnóstico concluído")

if __name__ == "__main__":
    main()
