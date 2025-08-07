#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e ajustar a codificação do banco de dados PostgreSQL.

Este script verifica a codificação atual do banco de dados e, se necessário,
o recria com a codificação UTF-8 e o collation pt_BR.UTF-8.
"""
try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    print("Erro: O pacote psycopg2-binary não está instalado.")
    print("Por favor, instale-o com: pip install psycopg2-binary")
    sys.exit(1)
    
import logging
import sys
import os
from typing import Dict, Optional, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ajustar_encoding.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configurações de conexão
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",  # Conecta ao banco padrão inicialmente
    "user": "postgres",
    "password": "@Eduardo123",
    "port": "5432"
}

def conectar_banco(config: Dict, autocommit: bool = False) -> Optional[psycopg2.extensions.connection]:
    """Estabelece conexão com o banco de dados."""
    # Cria uma cópia do dicionário de configuração para não modificar o original
    conn_config = config.copy()
    
    # Remove a senha do log por segurança
    log_config = conn_config.copy()
    if 'password' in log_config:
        log_config['password'] = '***'
    
    logger.debug(f"Tentando conectar com: {log_config}")
    
    try:
        # Tenta conectar com encoding explícito
        conn = psycopg2.connect(
            host=conn_config.get('host'),
            database=conn_config.get('database'),
            user=conn_config.get('user'),
            password=conn_config.get('password'),
            port=conn_config.get('port'),
            client_encoding='UTF8',  # Força o encoding UTF-8
            connect_timeout=5  # Timeout de 5 segundos
        )
        
        if autocommit:
            conn.autocommit = True
            
        logger.debug("Conexão estabelecida com sucesso!")
        return conn
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Erro de conexão: {str(e).strip()}")
        if "password authentication failed" in str(e).lower():
            logger.error("Falha na autenticação. Verifique o usuário e senha.")
        elif "could not connect to server" in str(e).lower():
            logger.error("Não foi possível conectar ao servidor PostgreSQL.")
            logger.error("Verifique se o serviço PostgreSQL está em execução.")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao conectar: {str(e).strip()}")
        return None

def verificar_encoding_banco(conn: psycopg2.extensions.connection, dbname: str) -> Tuple[bool, str]:
    """Verifica a codificação de um banco de dados específico."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT datname, pg_encoding_to_char(encoding) "
                "FROM pg_database WHERE datname = %s",
                (dbname,)
            )
            result = cur.fetchone()
            
            if not result:
                logger.warning(f"Banco de dados '{dbname}' não encontrado.")
                return False, ""
                
            db_name, encoding = result
            logger.info(f"Banco de dados: {db_name}, Codificação: {encoding}")
            return True, encoding
            
    except Exception as e:
        logger.error(f"Erro ao verificar encoding do banco {dbname}: {e}")
        return False, ""

def verificar_collation(conn: psycopg2.extensions.connection) -> None:
    """Verifica os collations disponíveis no servidor PostgreSQL."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT collname, collcollate, collctype FROM pg_collation "
                       "WHERE collname LIKE '%portuguese%' OR collname LIKE '%pt_%'")
            logger.info("Collations disponíveis no servidor:")
            for row in cur.fetchall():
                logger.info(f"- {row[0]} (collate: {row[1]}, ctype: {row[2]})")
    except Exception as e:
        logger.error(f"Erro ao verificar collations: {e}")

def criar_banco_utf8(conn: psycopg2.extensions.connection, dbname: str) -> bool:
    """Cria um novo banco de dados com codificação UTF-8."""
    try:
        with conn.cursor() as cur:
            # Verifica se o banco já existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            if cur.fetchone():
                logger.warning(f"O banco de dados '{dbname}' já existe.")
                return False
                
            # Tenta criar com collation pt_BR.UTF-8
            try:
                cur.execute(
                    f"CREATE DATABASE {dbname} "
                    "ENCODING 'UTF8' "
                    "LC_COLLATE 'pt_BR.UTF-8' "
                    "LC_CTYPE 'pt_BR.UTF-8' "
                    "TEMPLATE template0;"
                )
                logger.info(f"✅ Banco de dados '{dbname}' criado com sucesso com codificação UTF-8.")
                return True
                
            except psycopg2.Error as e:
                logger.warning(f"Não foi possível criar com collation pt_BR.UTF-8: {e}")
                logger.info("Tentando criar com collation padrão...")
                
                # Tenta criar com collation padrão
                try:
                    cur.execute(
                        f"CREATE DATABASE {dbname} "
                        "ENCODING 'UTF8' "
                        "TEMPLATE template0;"
                    )
                    logger.info(f"✅ Banco de dados '{dbname}' criado com sucesso com codificação UTF-8 (collation padrão).")
                    return True
                    
                except psycopg2.Error as e2:
                    logger.error(f"Falha ao criar banco de dados: {e2}")
                    return False
                    
    except Exception as e:
        logger.error(f"Erro ao criar banco de dados: {e}")
        return False

def verificar_servico_postgres() -> bool:
    """Verifica se o serviço do PostgreSQL está em execução."""
    try:
        # Tenta conectar ao banco de dados 'postgres' que sempre deve existir
        test_config = {
            'host': 'localhost',
            'database': 'postgres',
            'user': 'postgres',
            'password': '@Eduardo123',
            'port': '5432'
        }
        
        conn = conectar_banco(test_config)
        if conn:
            conn.close()
            return True
            
        # Se chegou aqui, a conexão falhou
        logger.warning("""
⚠️  Não foi possível conectar ao servidor PostgreSQL. Verifique:
1. Se o serviço PostgreSQL está em execução
2. Se as credenciais estão corretas
3. Se o servidor está configurado para aceitar conexões

No Windows, você pode verificar o serviço com:
> Get-Service -Name postgresql-*

E iniciá-lo com (como administrador):
> Start-Service -Name postgresql-*
""")
        return False
        
    except Exception as e:
        logger.error(f"Erro ao verificar serviço PostgreSQL: {e}")
        return False

def main():
    """Função principal do script."""
    # Configura o encoding da saída do console para UTF-8
    if sys.platform == 'win32':
        import io, sys
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    logger.info("=" * 60)
    logger.info("VERIFICAÇÃO E AJUSTE DE CODIFICAÇÃO DO BANCO DE DADOS")
    logger.info("=" * 60)
    
    # Verifica se o serviço PostgreSQL está rodando
    if not verificar_servico_postgres():
        return 1
    
    # Conecta ao banco postgres (banco padrão)
    conn = conectar_banco(DB_CONFIG, autocommit=True)
    if not conn:
        logger.error("Não foi possível conectar ao servidor PostgreSQL.")
        return 1
    
    try:
        # Verifica collations disponíveis
        verificar_collation(conn)
        
        # Pede o nome do banco de dados
        dbname = input("Digite o nome do banco de dados (padrão: apostapro): ").strip()
        if not dbname:
            dbname = "apostapro"
            
        logger.info(f"Verificando banco de dados: {dbname}")
        existe, encoding = verificar_encoding_banco(conn, dbname)
        
        if existe:
            if encoding.upper() in ('UTF8', 'UTF-8'):
                logger.info("✅ O banco de dados já está configurado com codificação UTF-8.")
                return 0
            else:
                logger.warning(f"⚠️  O banco de dados está configurado com codificação {encoding}.")
                logger.info("Para alterar para UTF-8, será necessário recriar o banco de dados.")
                
                # Pergunta ao usuário se deseja recriar o banco
                resposta = input("Deseja recriar o banco de dados com codificação UTF-8? (s/N): ").strip().lower()
                if resposta == 's':
                    # Fecha a conexão atual para poder dropar o banco
                    conn.close()
                    
                    # Reconecta ao banco postgres
                    conn = conectar_banco(DB_CONFIG, autocommit=True)
                    
                    # Remove o banco existente
                    try:
                        with conn.cursor() as cur:
                            logger.info(f"Removendo banco de dados '{dbname}'...")
                            # Desconecta todos os usuários do banco
                            cur.execute("""
                                SELECT pg_terminate_backend(pg_stat_activity.pid)
                                FROM pg_stat_activity
                                WHERE pg_stat_activity.datname = %s
                                AND pid <> pg_backend_pid();
                            """, (dbname,))
                            
                            # Remove o banco
                            cur.execute(f"DROP DATABASE IF EXISTS {dbname}")
                            logger.info(f"Banco de dados '{dbname}' removido com sucesso.")
                            
                    except Exception as e:
                        logger.error(f"Erro ao remover banco de dados: {e}")
                        return 1
                    
                    # Cria o novo banco com UTF-8
                    if criar_banco_utf8(conn, dbname):
                        logger.info("✅ Banco de dados recriado com sucesso com codificação UTF-8.")
                        logger.info("\nPróximos passos:")
                        logger.info("1. Recrie as tabelas e objetos do banco de dados")
                        logger.info("2. Importe os dados novamente usando a codificação correta")
                        return 0
                    else:
                        logger.error("❌ Falha ao recriar o banco de dados.")
                        return 1
                else:
                    logger.info("Operação cancelada pelo usuário.")
                    return 1
        else:
            logger.info(f"O banco de dados '{dbname}' não existe.")
            resposta = input(f"Deseja criar o banco de dados '{dbname}' com codificação UTF-8? (s/N): ").strip().lower()
            if resposta == 's':
                if criar_banco_utf8(conn, dbname):
                    logger.info("✅ Banco de dados criado com sucesso com codificação UTF-8.")
                    return 0
                else:
                    logger.error("❌ Falha ao criar o banco de dados.")
                    return 1
            else:
                logger.info("Operação cancelada pelo usuário.")
                return 1
                
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        return 1
    finally:
        if conn and not conn.closed:
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
