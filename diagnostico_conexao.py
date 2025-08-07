#!/usr/bin/env python3
"""
Script de diagnóstico para verificar a conexão com o banco de dados PostgreSQL
"""
import os
import sys
import logging
import psycopg2
from psycopg2 import sql
from pathlib import Path
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def testar_conexao(host, dbname, user, password, port="5432"):
    """Testa a conexão com o banco de dados"""
    logger.info(f"\n🔍 Testando conexão com: postgresql://{user}:***@{host}:{port}/{dbname}")
    
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )
        
        with conn.cursor() as cur:
            # Testa consulta básica
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            logger.info(f"✅ Conexão bem-sucedida!")
            logger.info(f"   - PostgreSQL: {version}")
            
            # Lista bancos de dados
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            dbs = [row[0] for row in cur.fetchall()]
            logger.info(f"\n📊 Bancos de dados encontrados: {', '.join(dbs)}")
            
            if dbname in dbs:
                # Lista tabelas no banco
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                
                tabelas = [row[0] for row in cur.fetchall()]
                logger.info(f"\n📋 Tabelas em '{dbname}':")
                for tabela in tabelas:
                    logger.info(f"   - {tabela}")
                
                # Verifica tabelas necessárias
                tabelas_necessarias = {
                    'partidas': False,
                    'estatisticas_partidas': False,
                    'clubes': False,
                    'competicoes': False,
                    'paises_clubes': False
                }
                
                for tabela in tabelas_necessarias.keys():
                    if tabela in tabelas:
                        tabelas_necessarias[tabela] = True
                
                logger.info("\n🔍 Status das tabelas necessárias:")
                for tabela, encontrada in tabelas_necessarias.items():
                    status = "✅" if encontrada else "❌"
                    logger.info(f"   {status} {tabela}")
                
                # Verifica se há partidas cadastradas
                if 'partidas' in tabelas:
                    cur.execute("SELECT COUNT(*) FROM partidas;")
                    total_partidas = cur.fetchone()[0]
                    logger.info(f"\n📊 Total de partidas cadastradas: {total_partidas}")
                    
                    if total_partidas > 0:
                        cur.execute("""
                            SELECT p.id, c1.nome as time_casa, c2.nome as time_visitante, 
                                   p.url_fbref, p.data_partida
                            FROM partidas p
                            JOIN clubes c1 ON p.clube_casa_id = c1.id
                            JOIN clubes c2 ON p.clube_visitante_id = c2.id
                            LIMIT 5;
                        """)
                        
                        logger.info("\n📅 Últimas partidas cadastradas:")
                        for row in cur.fetchall():
                            logger.info(f"   - {row[1]} x {row[2]} (ID: {row[0]}, Data: {row[4]})")
                            logger.info(f"     URL: {row[3]}")
            else:
                logger.error(f"❌ O banco de dados '{dbname}' não foi encontrado!")
                
        return True
        
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Falha na conexão: {e}")
        
        # Dicas de solução de problemas
        if "connection failed" in str(e).lower():
            logger.info("\n💡 Dicas de solução:")
            logger.info("1. Verifique se o PostgreSQL está em execução")
            logger.info("2. Confirme o host e a porta do banco de dados")
            logger.info("3. Verifique se o usuário e senha estão corretos")
            logger.info("4. Confirme se o banco de dados existe")
            
        return False
    
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    # Carrega variáveis de ambiente do arquivo .env se existir
    load_dotenv()
    
    # Configurações de conexão
    configs = [
        {
            "host": os.getenv("DB_HOST", "localhost"),
            "dbname": os.getenv("DB_NAME", "apostapro"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
            "port": os.getenv("DB_PORT", "5432")
        },
        # Tenta com senhas comuns
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "Canjica@@2025"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "Canjica@@2025"},
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "@Eduardo123"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "@Eduardo123"},
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "apostapro_pass"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "apostapro_pass"},
        {"host": "localhost", "dbname": "apostapro", "user": "postgres", "password": "postgres"},
        {"host": "localhost", "dbname": "postgres", "user": "postgres", "password": "postgres"},
    ]
    
    logger.info("🔍 Iniciando diagnóstico de conexão com o PostgreSQL...")
    
    # Remove duplicatas mantendo a ordem
    seen = set()
    configs_unicas = []
    for cfg in configs:
        key = (cfg['host'], cfg['dbname'], cfg['user'], cfg['password'])
        if key not in seen:
            seen.add(key)
            configs_unicas.append(cfg)
    
    # Testa cada configuração
    for i, cfg in enumerate(configs_unicas, 1):
        logger.info(f"\n🔧 Teste {i}/{len(configs_unicas)}")
        if testar_conexao(**cfg):
            logger.info("\n✅ Diagnóstico concluído com sucesso!")
            return
    
    logger.error("\n❌ Todas as tentativas de conexão falharam. Verifique as configurações do banco de dados.")

if __name__ == "__main__":
    main()
