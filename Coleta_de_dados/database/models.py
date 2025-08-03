"""
MODELOS SQLALCHEMY - SISTEMA FBREF
==================================

Modelos ORM para substituir as queries SQL diretas do sistema FBRef.
Baseado na análise das tabelas existentes no SQLite.

Tabelas principais identificadas:
- competicoes
- links_para_coleta  
- partidas
- estatisticas_partidas
- paises_clubes, clubes, estatisticas_clube
- records_vs_opponents
- paises_jogadores, jogadores
- estatisticas_jogador_geral, estatisticas_jogador_competicao

Autor: Sistema de Migração de Banco de Dados
Data: 2025-08-03
Versão: 1.0
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .config import Base

class TimestampMixin:
    """Mixin para campos de timestamp automáticos."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class Competicao(Base, TimestampMixin):
    """Modelo para competições/torneios."""
    __tablename__ = 'competicoes'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    contexto: Mapped[Optional[str]] = mapped_column(String(100))  # Masculino/Feminino
    pais: Mapped[Optional[str]] = mapped_column(String(100))
    tipo: Mapped[Optional[str]] = mapped_column(String(50))  # Liga, Copa, etc.
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    links_coleta: Mapped[List["LinkParaColeta"]] = relationship(
        "LinkParaColeta", back_populates="competicao", cascade="all, delete-orphan"
    )
    partidas: Mapped[List["Partida"]] = relationship(
        "Partida", back_populates="competicao"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_competicoes_nome', 'nome'),
        Index('idx_competicoes_contexto', 'contexto'),
        Index('idx_competicoes_ativa', 'ativa'),
        UniqueConstraint('nome', 'contexto', name='uq_competicao_nome_contexto'),
    )
    
    def __repr__(self):
        return f"<Competicao(id={self.id}, nome='{self.nome}', contexto='{self.contexto}')>"

class LinkParaColeta(Base, TimestampMixin):
    """Modelo para links de coleta (fila de trabalho)."""
    __tablename__ = 'links_para_coleta'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competicao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('competicoes.id', ondelete='CASCADE'), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)  # temporada, partida, etc.
    status: Mapped[str] = mapped_column(
        String(20), default='pendente', nullable=False
    )  # pendente, processando, concluido, erro
    tentativas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ultimo_erro: Mapped[Optional[str]] = mapped_column(Text)
    processado_em: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relacionamentos
    competicao: Mapped["Competicao"] = relationship("Competicao", back_populates="links_coleta")
    
    # Índices
    __table_args__ = (
        Index('idx_links_competicao', 'competicao_id'),
        Index('idx_links_status', 'status'),
        Index('idx_links_tipo', 'tipo'),
        Index('idx_links_processado', 'processado_em'),
        CheckConstraint(
            "status IN ('pendente', 'processando', 'concluido', 'erro')",
            name='ck_links_status'
        ),
    )
    
    def __repr__(self):
        return f"<LinkParaColeta(id={self.id}, tipo='{self.tipo}', status='{self.status}')>"

class PaisClube(Base, TimestampMixin):
    """Modelo para países dos clubes."""
    __tablename__ = 'paises_clubes'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    codigo_iso: Mapped[Optional[str]] = mapped_column(String(3))  # BRA, ENG, etc.
    continente: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relacionamentos
    clubes: Mapped[List["Clube"]] = relationship("Clube", back_populates="pais")
    
    def __repr__(self):
        return f"<PaisClube(id={self.id}, nome='{self.nome}')>"

class Clube(Base, TimestampMixin):
    """Modelo para clubes/times."""
    __tablename__ = 'clubes'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_completo: Mapped[Optional[str]] = mapped_column(String(500))
    url_fbref: Mapped[Optional[str]] = mapped_column(Text)
    pais_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('paises_clubes.id'), nullable=True
    )
    cidade: Mapped[Optional[str]] = mapped_column(String(100))
    fundacao: Mapped[Optional[int]] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    pais: Mapped[Optional["PaisClube"]] = relationship("PaisClube", back_populates="clubes")
    partidas_casa: Mapped[List["Partida"]] = relationship(
        "Partida", foreign_keys="Partida.clube_casa_id", back_populates="clube_casa"
    )
    partidas_visitante: Mapped[List["Partida"]] = relationship(
        "Partida", foreign_keys="Partida.clube_visitante_id", back_populates="clube_visitante"
    )
    estatisticas: Mapped[List["EstatisticaClube"]] = relationship(
        "EstatisticaClube", back_populates="clube"
    )
    records_vs: Mapped[List["RecordVsOpponent"]] = relationship(
        "RecordVsOpponent", foreign_keys="RecordVsOpponent.clube_id", back_populates="clube"
    )
    jogadores: Mapped[List["Jogador"]] = relationship("Jogador", back_populates="clube_atual")
    
    # Índices
    __table_args__ = (
        Index('idx_clubes_nome', 'nome'),
        Index('idx_clubes_pais', 'pais_id'),
        Index('idx_clubes_ativo', 'ativo'),
    )
    
    def __repr__(self):
        return f"<Clube(id={self.id}, nome='{self.nome}')>"

class Partida(Base, TimestampMixin):
    """Modelo para partidas."""
    __tablename__ = 'partidas'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competicao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('competicoes.id'), nullable=False
    )
    clube_casa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clubes.id'), nullable=False
    )
    clube_visitante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clubes.id'), nullable=False
    )
    
    # Dados da partida
    data_partida: Mapped[Optional[date]] = mapped_column(Date)
    horario: Mapped[Optional[str]] = mapped_column(String(10))
    rodada: Mapped[Optional[str]] = mapped_column(String(50))
    temporada: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Resultado
    gols_casa: Mapped[Optional[int]] = mapped_column(Integer)
    gols_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    resultado: Mapped[Optional[str]] = mapped_column(String(1))  # V, E, D
    
    # Metadados
    url_fbref: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default='agendada', nullable=False)
    
    # Relacionamentos
    competicao: Mapped["Competicao"] = relationship("Competicao", back_populates="partidas")
    clube_casa: Mapped["Clube"] = relationship(
        "Clube", foreign_keys=[clube_casa_id], back_populates="partidas_casa"
    )
    clube_visitante: Mapped["Clube"] = relationship(
        "Clube", foreign_keys=[clube_visitante_id], back_populates="partidas_visitante"
    )
    estatisticas: Mapped[List["EstatisticaPartida"]] = relationship(
        "EstatisticaPartida", back_populates="partida", cascade="all, delete-orphan"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_partidas_competicao', 'competicao_id'),
        Index('idx_partidas_data', 'data_partida'),
        Index('idx_partidas_temporada', 'temporada'),
        Index('idx_partidas_casa', 'clube_casa_id'),
        Index('idx_partidas_visitante', 'clube_visitante_id'),
        Index('idx_partidas_status', 'status'),
        CheckConstraint(
            "status IN ('agendada', 'em_andamento', 'finalizada', 'cancelada')",
            name='ck_partidas_status'
        ),
        CheckConstraint(
            "clube_casa_id != clube_visitante_id",
            name='ck_partidas_clubes_diferentes'
        ),
    )
    
    def __repr__(self):
        return f"<Partida(id={self.id}, data={self.data_partida}, status='{self.status}')>"

class EstatisticaPartida(Base, TimestampMixin):
    """Modelo para estatísticas de partidas."""
    __tablename__ = 'estatisticas_partidas'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    partida_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('partidas.id', ondelete='CASCADE'), nullable=False
    )
    
    # Estatísticas gerais
    posse_bola_casa: Mapped[Optional[float]] = mapped_column(Float)
    posse_bola_visitante: Mapped[Optional[float]] = mapped_column(Float)
    chutes_casa: Mapped[Optional[int]] = mapped_column(Integer)
    chutes_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    chutes_no_gol_casa: Mapped[Optional[int]] = mapped_column(Integer)
    chutes_no_gol_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cartões
    cartoes_amarelos_casa: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_amarelos_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_vermelhos_casa: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_vermelhos_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Faltas
    faltas_casa: Mapped[Optional[int]] = mapped_column(Integer)
    faltas_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Escanteios
    escanteios_casa: Mapped[Optional[int]] = mapped_column(Integer)
    escanteios_visitante: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relacionamentos
    partida: Mapped["Partida"] = relationship("Partida", back_populates="estatisticas")
    
    # Índices
    __table_args__ = (
        Index('idx_estatisticas_partida', 'partida_id'),
    )
    
    def __repr__(self):
        return f"<EstatisticaPartida(id={self.id}, partida_id={self.partida_id})>"

class EstatisticaClube(Base, TimestampMixin):
    """Modelo para estatísticas de clubes."""
    __tablename__ = 'estatisticas_clube'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clube_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clubes.id', ondelete='CASCADE'), nullable=False
    )
    competicao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('competicoes.id'), nullable=False
    )
    temporada: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Estatísticas da temporada
    jogos: Mapped[Optional[int]] = mapped_column(Integer)
    vitorias: Mapped[Optional[int]] = mapped_column(Integer)
    empates: Mapped[Optional[int]] = mapped_column(Integer)
    derrotas: Mapped[Optional[int]] = mapped_column(Integer)
    gols_pro: Mapped[Optional[int]] = mapped_column(Integer)
    gols_contra: Mapped[Optional[int]] = mapped_column(Integer)
    saldo_gols: Mapped[Optional[int]] = mapped_column(Integer)
    pontos: Mapped[Optional[int]] = mapped_column(Integer)
    posicao: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relacionamentos
    clube: Mapped["Clube"] = relationship("Clube", back_populates="estatisticas")
    competicao: Mapped["Competicao"] = relationship("Competicao")
    
    # Índices
    __table_args__ = (
        Index('idx_estatisticas_clube_clube', 'clube_id'),
        Index('idx_estatisticas_clube_competicao', 'competicao_id'),
        Index('idx_estatisticas_clube_temporada', 'temporada'),
        UniqueConstraint(
            'clube_id', 'competicao_id', 'temporada',
            name='uq_estatistica_clube_temporada'
        ),
    )
    
    def __repr__(self):
        return f"<EstatisticaClube(clube_id={self.clube_id}, temporada='{self.temporada}')>"

class RecordVsOpponent(Base, TimestampMixin):
    """Modelo para records contra oponentes."""
    __tablename__ = 'records_vs_opponents'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clube_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clubes.id', ondelete='CASCADE'), nullable=False
    )
    oponente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clubes.id', ondelete='CASCADE'), nullable=False
    )
    
    # Records
    jogos_total: Mapped[Optional[int]] = mapped_column(Integer)
    vitorias: Mapped[Optional[int]] = mapped_column(Integer)
    empates: Mapped[Optional[int]] = mapped_column(Integer)
    derrotas: Mapped[Optional[int]] = mapped_column(Integer)
    gols_pro: Mapped[Optional[int]] = mapped_column(Integer)
    gols_contra: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relacionamentos
    clube: Mapped["Clube"] = relationship(
        "Clube", foreign_keys=[clube_id], back_populates="records_vs"
    )
    oponente: Mapped["Clube"] = relationship(
        "Clube", foreign_keys=[oponente_id]
    )
    
    # Índices
    __table_args__ = (
        Index('idx_records_clube', 'clube_id'),
        Index('idx_records_oponente', 'oponente_id'),
        UniqueConstraint(
            'clube_id', 'oponente_id',
            name='uq_record_clube_oponente'
        ),
        CheckConstraint(
            "clube_id != oponente_id",
            name='ck_records_clubes_diferentes'
        ),
    )
    
    def __repr__(self):
        return f"<RecordVsOpponent(clube_id={self.clube_id}, oponente_id={self.oponente_id})>"

class PaisJogador(Base, TimestampMixin):
    """Modelo para países dos jogadores."""
    __tablename__ = 'paises_jogadores'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    codigo_iso: Mapped[Optional[str]] = mapped_column(String(3))
    continente: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relacionamentos
    jogadores: Mapped[List["Jogador"]] = relationship("Jogador", back_populates="pais")
    
    def __repr__(self):
        return f"<PaisJogador(id={self.id}, nome='{self.nome}')>"

class Jogador(Base, TimestampMixin):
    """Modelo para jogadores."""
    __tablename__ = 'jogadores'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_completo: Mapped[Optional[str]] = mapped_column(String(500))
    url_fbref: Mapped[Optional[str]] = mapped_column(Text)
    
    # Dados pessoais
    data_nascimento: Mapped[Optional[date]] = mapped_column(Date)
    pais_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('paises_jogadores.id'), nullable=True
    )
    posicao: Mapped[Optional[str]] = mapped_column(String(50))
    pe_preferido: Mapped[Optional[str]] = mapped_column(String(20))
    altura: Mapped[Optional[int]] = mapped_column(Integer)  # em cm
    peso: Mapped[Optional[int]] = mapped_column(Integer)  # em kg
    
    # Clube atual
    clube_atual_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('clubes.id'), nullable=True
    )
    
    # Status
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    aposentado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    pais: Mapped[Optional["PaisJogador"]] = relationship("PaisJogador", back_populates="jogadores")
    clube_atual: Mapped[Optional["Clube"]] = relationship("Clube", back_populates="jogadores")
    estatisticas_gerais: Mapped[List["EstatisticaJogadorGeral"]] = relationship(
        "EstatisticaJogadorGeral", back_populates="jogador"
    )
    estatisticas_competicao: Mapped[List["EstatisticaJogadorCompeticao"]] = relationship(
        "EstatisticaJogadorCompeticao", back_populates="jogador"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_jogadores_nome', 'nome'),
        Index('idx_jogadores_pais', 'pais_id'),
        Index('idx_jogadores_posicao', 'posicao'),
        Index('idx_jogadores_clube_atual', 'clube_atual_id'),
        Index('idx_jogadores_ativo', 'ativo'),
    )
    
    def __repr__(self):
        return f"<Jogador(id={self.id}, nome='{self.nome}', posicao='{self.posicao}')>"

class EstatisticaJogadorGeral(Base, TimestampMixin):
    """Modelo para estatísticas gerais de jogadores."""
    __tablename__ = 'estatisticas_jogador_geral'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jogador_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('jogadores.id', ondelete='CASCADE'), nullable=False
    )
    temporada: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Estatísticas gerais
    jogos: Mapped[Optional[int]] = mapped_column(Integer)
    jogos_titularidade: Mapped[Optional[int]] = mapped_column(Integer)
    minutos: Mapped[Optional[int]] = mapped_column(Integer)
    gols: Mapped[Optional[int]] = mapped_column(Integer)
    assistencias: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_amarelos: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_vermelhos: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relacionamentos
    jogador: Mapped["Jogador"] = relationship("Jogador", back_populates="estatisticas_gerais")
    
    # Índices
    __table_args__ = (
        Index('idx_estatisticas_jogador_geral_jogador', 'jogador_id'),
        Index('idx_estatisticas_jogador_geral_temporada', 'temporada'),
        UniqueConstraint(
            'jogador_id', 'temporada',
            name='uq_estatistica_jogador_geral_temporada'
        ),
    )
    
    def __repr__(self):
        return f"<EstatisticaJogadorGeral(jogador_id={self.jogador_id}, temporada='{self.temporada}')>"

class EstatisticaJogadorCompeticao(Base, TimestampMixin):
    """Modelo para estatísticas de jogadores por competição."""
    __tablename__ = 'estatisticas_jogador_competicao'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jogador_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('jogadores.id', ondelete='CASCADE'), nullable=False
    )
    competicao_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('competicoes.id'), nullable=False
    )
    temporada: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Estatísticas específicas da competição
    jogos: Mapped[Optional[int]] = mapped_column(Integer)
    jogos_titularidade: Mapped[Optional[int]] = mapped_column(Integer)
    minutos: Mapped[Optional[int]] = mapped_column(Integer)
    gols: Mapped[Optional[int]] = mapped_column(Integer)
    assistencias: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_amarelos: Mapped[Optional[int]] = mapped_column(Integer)
    cartoes_vermelhos: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Estatísticas avançadas
    chutes: Mapped[Optional[int]] = mapped_column(Integer)
    chutes_no_gol: Mapped[Optional[int]] = mapped_column(Integer)
    passes_certos: Mapped[Optional[int]] = mapped_column(Integer)
    passes_tentados: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relacionamentos
    jogador: Mapped["Jogador"] = relationship("Jogador", back_populates="estatisticas_competicao")
    competicao: Mapped["Competicao"] = relationship("Competicao")
    
    # Índices
    __table_args__ = (
        Index('idx_estatisticas_jogador_comp_jogador', 'jogador_id'),
        Index('idx_estatisticas_jogador_comp_competicao', 'competicao_id'),
        Index('idx_estatisticas_jogador_comp_temporada', 'temporada'),
        UniqueConstraint(
            'jogador_id', 'competicao_id', 'temporada',
            name='uq_estatistica_jogador_competicao_temporada'
        ),
    )
    
    def __repr__(self):
        return f"<EstatisticaJogadorCompeticao(jogador_id={self.jogador_id}, competicao_id={self.competicao_id}, temporada='{self.temporada}')>"
