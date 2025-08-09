#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a conexão com o banco de dados PostgreSQL
"""
import psycopg2
import os
import sys
import logging
import traceback
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,  # Nível DEBUG para mais informações
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('teste_conexao.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Configurações de conexão
DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",  # Primeiro tenta conectar ao banco padrão
    "user": "postgres",
    "password": "@Eduardo123",
    "port": "5432",
    "client_encoding": "utf-8",  # Força a codificação UTF-8
    "options": "-c client_encoding=utf8"  # Opção adicional para forçar UTF-8
}

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    try:
        logger.info("🔌 Testando conexão com o banco de dados...")
        
        # Log das configurações de conexão (sem a senha por segurança)
        db_config_log = DB_CONFIG.copy()
        if 'password' in db_config_log:
            db_config_log['password'] = '***'  # Não logar a senha real
        logger.debug(f"Configuração de conexão: {db_config_log}")
        
        # Tenta conectar com timeout de 5 segundos
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            logger.info("✅ Conexão com o banco 'postgres' estabelecida com sucesso!")
            
            # Verifica se o banco 'apostapro' existe
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = 'apostapro'")
                if cur.fetchone():
                    logger.info("✅ Banco de dados 'apostapro' encontrado!")
                    
                    # Fecha a conexão atual e tenta conectar ao banco 'apostapro'
                    conn.close()
                    DB_CONFIG["database"] = "apostapro"
                    conn = psycopg2.connect(**DB_CONFIG)
                    logger.info("✅ Conectado ao banco 'apostapro' com sucesso!")
                else:
                    logger.error("❌ Banco de dados 'apostapro' não encontrado!")
                    return False
                    
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
            logger.error("Verifique se o PostgreSQL está rodando e as credenciais estão corretas.")
            return False
        
        # Testa a conexão
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            logger.info(f"✅ Conexão bem-sucedida!")
            logger.info(f"📊 Versão do PostgreSQL: {db_version[0]}")
            
            # Verifica se o banco de dados está acessível
            cur.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
            db_info = cur.fetchone()
            logger.info(f"💾 Banco de dados: {db_info[0]}")
            logger.info(f"👤 Usuário: {db_info[1]}")
            logger.info(f"🌐 Endereço do servidor: {db_info[2]}")
            logger.info(f"🔌 Porta: {db_info[3]}")
            
            # Verifica a codificação do banco de dados
            cur.execute("SHOW SERVER_ENCODING;")
            server_encoding = cur.fetchone()[0]
            logger.info(f"🔤 Codificação do servidor: {server_encoding}")
            
            # Verifica a codificação do cliente
            cur.execute("SHOW CLIENT_ENCODING;")
            client_encoding = cur.fetchone()[0]
            logger.info(f"🔠 Codificação do cliente: {client_encoding}")
            
            # Verifica o locale do banco de dados
            try:
                cur.execute("SHOW LC_COLLATE;")
                lc_collate = cur.fetchone()[0]
                logger.info(f"🔡 Collation do banco: {lc_collate}")
                
                cur.execute("SHOW LC_CTYPE;")
                lc_ctype = cur.fetchone()[0]
                logger.info(f"🔠 CType do banco: {lc_ctype}")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível verificar os parâmetros de locale: {e}")
            
            # Verifica se existem partidas no banco
            cur.execute("SELECT COUNT(*) FROM partidas;")
            total_partidas = cur.fetchone()[0]
            logger.info(f"⚽ Total de partidas no banco: {total_partidas}")
            
            # Verifica se existem estatísticas de partidas
            cur.execute("SELECT COUNT(*) FROM estatisticas_partidas;")
            total_estatisticas = cur.fetchone()[0]
            logger.info(f"📊 Total de estatísticas de partidas: {total_estatisticas}")
            
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Erro operacional ao conectar ao banco: {e}")
        logger.error("Verifique se o PostgreSQL está rodando e acessível")
        logger.error(f"Detalhes do erro: {str(e).encode('utf-8', 'replace').decode('utf-8')}")
        return False
        
    except psycopg2.Error as e:
        logger.error(f"❌ Erro do PostgreSQL: {e}")
        if hasattr(e, 'pgcode'):
            logger.error(f"PG Code: {e.pgcode}")
        if hasattr(e, 'pgerror') and e.pgerror:
            logger.error(f"PG Error: {e.pgerror.encode('utf-8', 'replace').decode('utf-8')}")
        logger.error(f"Tipo de exceção: {type(e).__name__}")
        logger.error(f"Argumentos da exceção: {e.args}")
        return False
        
    except UnicodeDecodeError as ude:
        logger.error(f"❌ Erro de decodificação Unicode: {ude}")
        logger.error(f"Objeto: {ude.object[ude.start:ude.end]}")
        logger.error(f"Posição: {ude.start}-{ude.end}")
        logger.error(f"Causa: {ude.reason}")
        logger.error("Dica: Verifique a codificação do banco de dados e as configurações de locale.")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e).encode('utf-8', 'replace').decode('utf-8')}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Conexão encerrada.")

if __name__ == "__main__":
    testar_conexao()
