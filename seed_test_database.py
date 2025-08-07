#!/usr/bin/env python3
"""Seed Test Database

Script para popular o banco de dados com dados de teste mínimos.
"""
import sys
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importa configurações e modelos
try:
    from Coleta_de_dados.database.config import DATABASE_URL, Base, SessionLocal
    from Coleta_de_dados.database.models import (
        Competicao, Clube, Partida, EstatisticaPartida, PaisClube
    )
    logger.info("Módulos importados com sucesso")
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

def limpar_tabelas(session):
    """Limpa as tabelas necessárias."""
    logger.info("Limpando tabelas...")
    try:
        session.execute(text('TRUNCATE TABLE estatisticas_partidas CASCADE;'))
        session.execute(text('TRUNCATE TABLE partidas CASCADE;'))
        session.execute(text('TRUNCATE TABLE clubes CASCADE;'))
        session.execute(text('TRUNCATE TABLE paises_clubes CASCADE;'))
        session.execute(text('TRUNCATE TABLE competicoes CASCADE;'))
        session.commit()
        logger.info("Tabelas limpas com sucesso")
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao limpar tabelas: {e}")
        return False

def criar_dados_teste():
    """Cria dados de teste no banco de dados."""
    session = SessionLocal()
    
    try:
        # Limpa as tabelas
        if not limpar_tabelas(session):
            return False
        
        # Cria países
        brasil = PaisClube(nome="Brasil", codigo_iso="BRA")
        espanha = PaisClube(nome="Espanha", codigo_iso="ESP")
        session.add_all([brasil, espanha])
        session.commit()
        
        # Cria clubes
        flamengo = Clube(nome="Flamengo", pais_id=brasil.id)
        palmeiras = Clube(nome="Palmeiras", pais_id=brasil.id)
        barcelona = Clube(nome="Barcelona", pais_id=espanha.id)
        realmadrid = Clube(nome="Real Madrid", pais_id=espanha.id)
        session.add_all([flamengo, palmeiras, barcelona, realmadrid])
        session.commit()
        
        # Cria competição
        brasileirao = Competicao(
            nome="Campeonato Brasileiro Série A",
            url="https://fbref.com/pt-br/comps/24/Serie-A",
            contexto="Masculino",
            pais="Brasil",
            tipo="Liga",
            ativa=True
        )
        session.add(brasileirao)
        session.commit()
        
        # Cria partidas com estatísticas
        for i in range(3):
            partida = Partida(
                competicao_id=brasileirao.id,
                clube_casa_id=flamengo.id if i % 2 == 0 else palmeiras.id,
                clube_visitante_id=barcelona.id if i % 2 == 0 else realmadrid.id,
                data_partida=datetime.now().date() - timedelta(days=i),
                rodada=f"{i+1}ª Rodada",
                temporada="2024",
                gols_casa=random.randint(0, 3),
                gols_visitante=random.randint(0, 3),
                url_fbref=f"https://fbref.com/pt-br/partidas/teste{i}",
                status="finalizada"
            )
            session.add(partida)
            session.flush()  # Obtém o ID da partida
            
            # Cria estatísticas vazias para a partida
            estatisticas = EstatisticaPartida(partida_id=partida.id)
            session.add(estatisticas)
        
        session.commit()
        logger.info("Dados de teste criados com sucesso!")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar dados de teste: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("Iniciando seed do banco de dados...")
    if criar_dados_teste():
        logger.info("Seed concluído com sucesso!")
    else:
        logger.error("Falha ao executar o seed do banco de dados")
