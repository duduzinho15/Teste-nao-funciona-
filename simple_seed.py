#!/usr/bin/env python3
"""
Simple Database Seeder
"""
import os
import logging
from sqlalchemy import create_engine, text

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Configuração do banco
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/apostapro')
    
    try:
        # Cria engine
        engine = create_engine(DATABASE_URL)
        
        # Script SQL para limpar e popular o banco
        sql_script = """
        -- Limpa as tabelas
        TRUNCATE TABLE estatisticas_partidas CASCADE;
        TRUNCATE TABLE partidas CASCADE;
        TRUNCATE TABLE clubes CASCADE;
        TRUNCATE TABLE paises_clubes CASCADE;
        TRUNCATE TABLE competicoes CASCADE;
        
        -- Insere países
        INSERT INTO paises_clubes (nome, codigo_iso, continente) VALUES 
        ('Brasil', 'BRA', 'América do Sul'),
        ('Espanha', 'ESP', 'Europa');
        
        -- Insere clubes
        INSERT INTO clubes (nome, pais_id) VALUES 
        ('Flamengo', 1),
        ('Barcelona', 2);
        
        -- Insere competição
        INSERT INTO competicoes (nome, url, contexto, pais, tipo, ativa) VALUES 
        ('Campeonato Brasileiro Série A', 'https://fbref.com/pt-br/comps/24/Serie-A', 'Masculino', 'Brasil', 'Liga', true);
        
        -- Insere partida
        INSERT INTO partidas (competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, temporada, gols_casa, gols_visitante, url_fbref, status) 
        VALUES (1, 1, 2, CURRENT_DATE, '1ª Rodada', '2024', 2, 1, 'https://fbref.com/pt-br/partidas/teste123', 'finalizada');
        
        -- Insere estatísticas
        INSERT INTO estatisticas_partidas (partida_id) VALUES (1);
        """
        
        # Executa o script SQL
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        
        logger.info("Banco de dados populado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao popular o banco de dados: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando seed do banco de dados...")
    if main():
        logger.info("Seed concluído com sucesso!")
    else:
        logger.error("Falha ao executar o seed do banco de dados")
