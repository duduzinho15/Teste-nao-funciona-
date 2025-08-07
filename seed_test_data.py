#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
"""
import psycopg2
from psycopg2 import sql
import logging
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "database": "apostapro",
    "user": "postgres",
    "password": "Canjica@@2025"  # Substitua pela senha correta se necessário
}

def connect_db():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conexão com o banco de dados estabelecida")
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def seed_data():
    """Popula o banco de dados com dados de teste"""
    conn = connect_db()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            logger.info("\n🔧 Iniciando a inserção de dados de teste...")
            
            # Inserir países
            logger.info("\n🌎 Inserindo países...")
            paises = [
                ("Brasil", "BRA", "América do Sul"),
                ("Argentina", "ARG", "América do Sul"),
                ("Espanha", "ESP", "Europa"),
                ("Inglaterra", "ENG", "Europa"),
                ("Itália", "ITA", "Europa"),
            ]
            
            for pais in paises:
                cur.execute(
                    """
                    INSERT INTO paises_clubes (nome, codigo_iso, continente)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (nome) DO NOTHING
                    RETURNING id;
                    """,
                    pais
                )
            
            # Obter IDs dos países
            cur.execute("SELECT id, nome FROM paises_clubes")
            paises_dict = {nome: id for id, nome in cur.fetchall()}
            
            # Inserir competições
            logger.info("\n🏆 Inserindo competições...")
            competicoes = [
                ("Campeonato Brasileiro Série A", "https://fbref.com/en/comps/24/Serie-A", "Brasil", "Brasil", "Liga Nacional"),
                ("Copa Libertadores", "https://fbref.com/en/comps/8/history/Copa-Libertadores", "América do Sul", "CONMEBOL", "Copa Internacional"),
                ("La Liga", "https://fbref.com/en/comps/12/La-Liga", "Espanha", "Espanha", "Liga Nacional"),
                ("Premier League", "https://fbref.com/en/comps/9/Premier-League", "Inglaterra", "Inglaterra", "Liga Nacional"),
                ("Serie A", "https://fbref.com/en/comps/11/Serie-A", "Itália", "Itália", "Liga Nacional"),
            ]
            
            for competicao in competicoes:
                cur.execute(
                    """
                    INSERT INTO competicoes (nome, url, pais, contexto, tipo)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (nome) DO NOTHING
                    RETURNING id;
                    """,
                    competicao
                )
            
            # Obter IDs das competições
            cur.execute("SELECT id, nome FROM competicoes")
            competicoes_dict = {nome: id for id, nome in cur.fetchall()}
            
            # Inserir clubes
            logger.info("\n⚽ Inserindo clubes...")
            clubes = [
                ("Flamengo", paises_dict["Brasil"]),
                ("Palmeiras", paises_dict["Brasil"]),
                ("River Plate", paises_dict["Argentina"]),
                ("Barcelona", paises_dict["Espanha"]),
                ("Real Madrid", paises_dict["Espanha"]),
                ("Manchester City", paises_dict["Inglaterra"]),
                ("Liverpool", paises_dict["Inglaterra"]),
                ("Juventus", paises_dict["Itália"]),
                ("Internazionale", paises_dict["Itália"]),
            ]
            
            for clube in clubes:
                cur.execute(
                    """
                    INSERT INTO clubes (nome, pais_id)
                    VALUES (%s, %s)
                    ON CONFLICT (nome) DO NOTHING
                    RETURNING id;
                    """,
                    clube
                )
            
            # Obter IDs dos clubes
            cur.execute("SELECT id, nome FROM clubes")
            clubes_dict = {nome: id for id, nome in cur.fetchall()}
            
            # Inserir partidas
            logger.info("\n📅 Inserindo partidas...")
            hoje = datetime.now().date()
            partidas = [
                (competicoes_dict["Campeonato Brasileiro Série A"], 
                 clubes_dict["Flamengo"], 
                 clubes_dict["Palmeiras"], 
                 hoje + timedelta(days=7), 
                 "1ª Rodada", 
                 "2024", 
                 None, 
                 None, 
                 "https://fbref.com/en/matches/12345678/Flamengo-Palmeiras-August-12-2024-Serie-A", 
                 "agendada"),
                (competicoes_dict["Copa Libertadores"], 
                 clubes_dict["Flamengo"], 
                 clubes_dict["River Plate"], 
                 hoje + timedelta(days=14), 
                 "Quartas de Final", 
                 "2024", 
                 None, 
                 None, 
                 "https://fbref.com/en/matches/12345679/Flamengo-River-Plate-August-19-2024-Copa-Libertadores", 
                 "agendada"),
                (competicoes_dict["La Liga"], 
                 clubes_dict["Barcelona"], 
                 clubes_dict["Real Madrid"], 
                 hoje + timedelta(days=21), 
                 "10ª Rodada", 
                 "2024/2025", 
                 None, 
                 None, 
                 "https://fbref.com/en/matches/12345680/Barcelona-Real-Madrid-August-26-2024-La-Liga", 
                 "agendada"),
            ]
            
            partidas_ids = []
            for partida in partidas:
                cur.execute(
                    """
                    INSERT INTO partidas 
                    (competicao_id, clube_casa_id, clube_visitante_id, data_partida, 
                     rodada, temporada, gols_casa, gols_visitante, url_fbref, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    partida
                )
                partida_id = cur.fetchone()[0]
                partidas_ids.append(partida_id)
            
            # Inserir estatísticas de partidas (inicialmente vazias)
            logger.info("\n📊 Inserindo estatísticas de partidas...")
            for partida_id in partidas_ids:
                cur.execute(
                    """
                    INSERT INTO estatisticas_partidas 
                    (partida_id, xg_casa, xg_visitante, formacao_casa, formacao_visitante)
                    VALUES (%s, NULL, NULL, NULL, NULL);
                    """,
                    (partida_id,)
                )
            
            # Commit das alterações
            conn.commit()
            logger.info("\n✅ Dados de teste inseridos com sucesso!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados de teste: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("🚀 Iniciando o processo de seed do banco de dados...")
    if seed_data():
        logger.info("✨ Processo de seed concluído com sucesso!")
    else:
        logger.error("❌ Falha no processo de seed do banco de dados")
