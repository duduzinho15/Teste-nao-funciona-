#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para popular a tabela estatisticas_partidas com dados de teste.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Configuração da conexão com o banco de dados
    db_url = "postgresql://apostapro_user:apostapro_pass@localhost:5432/apostapro_db"
    engine = create_engine(db_url)
    
    # Criar uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar se já existem estatísticas de teste
        result = session.execute(
            text("SELECT COUNT(*) FROM estatisticas_partidas")
        ).scalar()
        
        if result > 0:
            print("Já existem registros na tabela 'estatisticas_partidas'.")
            print("Para evitar duplicação, o script não será executado.")
            return
        
        # Obter uma partida existente para associar as estatísticas
        partida = session.execute(
            text("SELECT id FROM partidas LIMIT 1")
        ).fetchone()
        
        if not partida:
            print("Nenhuma partida encontrada no banco de dados.")
            print("Por favor, importe as partidas antes de executar este script.")
            return
        
        partida_id = partida[0]
        now = datetime.now()
        
        # Inserir estatísticas de teste
        insert_query = """
        INSERT INTO estatisticas_partidas (
            partida_id, 
            posse_bola_casa, posse_bola_visitante,
            chutes_casa, chutes_visitante,
            chutes_no_gol_casa, chutes_no_gol_visitante,
            cartoes_amarelos_casa, cartoes_amarelos_visitante,
            cartoes_vermelhos_casa, cartoes_vermelhos_visitante,
            faltas_casa, faltas_visitante,
            escanteios_casa, escanteios_visitante,
            xg_casa, xg_visitante,
            xa_casa, xa_visitante,
            formacao_casa, formacao_visitante,
            created_at, updated_at
        ) VALUES (
            :partida_id,
            55.5, 44.5,  # posse_bola
            15, 10,       # chutes
            5, 3,         # chutes_no_gol
            2, 3,         # cartoes_amarelos
            0, 1,         # cartoes_vermelhos
            12, 14,       # faltas
            7, 4,         # escanteios
            1.8, 1.2,     # xg
            1.5, 1.0,     # xa
            '4-4-2', '4-3-3',  # formacoes
            :now, :now    # timestamps
        )
        """
        
        session.execute(
            text(insert_query),
            {"partida_id": partida_id, "now": now}
        )
        
        # Commit das alterações
        session.commit()
        print("Dados de teste inseridos com sucesso na tabela 'estatisticas_partidas'!")
        print(f"Partida ID: {partida_id} atualizada com estatísticas de teste.")
    
    except Exception as e:
        print(f"Erro ao inserir dados de teste: {e}")
        session.rollback()
    
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
