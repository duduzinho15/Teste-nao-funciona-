#!/usr/bin/env python3
"""
Database Seeder
--------------

Script minimalista para popular o banco de dados com dados de teste.
"""
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do banco
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/apostapro')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def limpar_tabelas():
    """Limpa as tabelas necessárias."""
    logger.info("Limpando tabelas...")
    session = Session()
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
    finally:
        session.close()

def criar_dados_teste():
    """Cria dados de teste no banco de dados."""
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String, ForeignKey
    
    Base = declarative_base()
    
    # Modelos simplificados
    class PaisClube(Base):
        __tablename__ = 'paises_clubes'
        id = Column(Integer, primary_key=True)
        nome = Column(String(100), unique=True)
    
    class Clube(Base):
        __tablename__ = 'clubes'
        id = Column(Integer, primary_key=True)
        nome = Column(String(255))
        pais_id = Column(Integer, ForeignKey('paises_clubes.id'))
    
    class Competicao(Base):
        __tablename__ = 'competicoes'
        id = Column(Integer, primary_key=True)
        nome = Column(String(255))
        url = Column(String(500))
    
    class Partida(Base):
        __tablename__ = 'partidas'
        id = Column(Integer, primary_key=True)
        competicao_id = Column(Integer, ForeignKey('competicoes.id'))
        clube_casa_id = Column(Integer, ForeignKey('clubes.id'))
        clube_visitante_id = Column(Integer, ForeignKey('clubes.id'))
        url_fbref = Column(String(500))
    
    class EstatisticaPartida(Base):
        __tablename__ = 'estatisticas_partidas'
        id = Column(Integer, primary_key=True)
        partida_id = Column(Integer, ForeignKey('partidas.id'))
    
    # Cria sessão
    session = Session()
    
    try:
        # Limpa as tabelas
        if not limpar_tabelas():
            return False
        
        # Cria países
        logger.info("Criando países...")
        brasil = PaisClube(nome="Brasil")
        espanha = PaisClube(nome="Espanha")
        session.add_all([brasil, espanha])
        session.flush()
        
        # Cria clubes
        logger.info("Criando clubes...")
        flamengo = Clube(nome="Flamengo", pais_id=brasil.id)
        barcelona = Clube(nome="Barcelona", pais_id=espanha.id)
        session.add_all([flamengo, barcelona])
        session.flush()
        
        # Cria competição
        logger.info("Criando competição...")
        brasileirao = Competicao(
            nome="Campeonato Brasileiro Série A",
            url="https://fbref.com/pt-br/comps/24/Serie-A"
        )
        session.add(brasileirao)
        session.flush()
        
        # Cria partida
        logger.info("Criando partida de teste...")
        partida = Partida(
            competicao_id=brasileirao.id,
            clube_casa_id=flamengo.id,
            clube_visitante_id=barcelona.id,
            url_fbref="https://fbref.com/pt-br/partidas/teste123"
        )
        session.add(partida)
        session.flush()
        
        # Cria estatísticas vazias
        estatisticas = EstatisticaPartida(partida_id=partida.id)
        session.add(estatisticas)
        
        # Confirma as alterações
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
