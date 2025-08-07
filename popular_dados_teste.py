#!/usr/bin/env python3
"""Script para popular o banco de dados com dados de teste."""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from Coleta_de_dados.database.config import SessionLocal, Base, engine
from Coleta_de_dados.database.models import (
    Competicao, Clube, Partida, EstatisticaPartida, PaisClube
)

def criar_paises(session: Session):
    """Cria países de teste."""
    paises = [
        {"nome": "Brasil", "codigo_iso": "BRA"},
        {"nome": "Espanha", "codigo_iso": "ESP"},
        {"nome": "Inglaterra", "codigo_iso": "ENG"},
    ]
    return [PaisClube(**p) for p in paises]

def criar_clubes(session: Session, paises):
    """Cria clubes de teste."""
    clubes = [
        {"nome": "Flamengo", "pais_id": paises[0].id},
        {"nome": "Palmeiras", "pais_id": paises[0].id},
        {"nome": "Barcelona", "pais_id": paises[1].id},
        {"nome": "Real Madrid", "pais_id": paises[1].id},
        {"nome": "Liverpool", "pais_id": paises[2].id},
        {"nome": "Manchester City", "pais_id": paises[2].id},
    ]
    return [Clube(**c) for c in clubes]

def criar_competicoes():
    """Cria competições de teste."""
    return [
        Competicao(nome="Campeonato Brasileiro", contexto="Masculino", ativa=True),
        Competicao(nome="La Liga", contexto="Masculino", ativa=True),
    ]

def criar_partidas(competicao_id, clubes):
    """Cria partidas de teste."""
    partidas = []
    for i in range(5):
        partida = Partida(
            competicao_id=competicao_id,
            clube_casa_id=random.choice(clubes).id,
            clube_visitante_id=random.choice(clubes).id,
            data_partida=datetime.now().date() - timedelta(days=i),
            rodada=f"{i+1}ª Rodada",
            temporada="2024",
            status="finalizada"
        )
        partidas.append(partida)
    return partidas

def criar_estatisticas(partida):
    """Cria estatísticas avançadas para uma partida."""
    return EstatisticaPartida(
        partida=partida,
        posse_bola_casa=round(random.uniform(40, 70), 1),
        xg_casa=round(random.uniform(0.5, 3.5), 2),
        xg_visitante=round(random.uniform(0.5, 3.5), 2),
        formacao_casa="4-3-3",
        formacao_visitante="4-4-2"
    )

def main():
    """Popula o banco de dados com dados de teste."""
    print("Criando dados de teste...")
    session = SessionLocal()
    
    try:
        # Cria entidades
        paises = criar_paises(session)
        session.add_all(paises)
        
        clubes = criar_clubes(session, paises)
        session.add_all(clubes)
        
        competicoes = criar_competicoes()
        session.add_all(competicoes)
        
        session.commit()
        
        # Cria partidas para a primeira competição
        partidas = criar_partidas(competicoes[0].id, clubes)
        session.add_all(partidas)
        session.commit()
        
        # Cria estatísticas para as partidas
        for partida in partidas:
            estatisticas = criar_estatisticas(partida)
            session.add(estatisticas)
        
        session.commit()
        print("Dados de teste criados com sucesso!")
        
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
