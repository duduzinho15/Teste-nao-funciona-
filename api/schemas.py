"""
SCHEMAS PYDANTIC PARA API FASTAPI
=================================

Modelos Pydantic para validação de requests e formatação de responses.
Garante consistência dos dados que entram e saem da API.

Autor: Sistema de API RESTful
Data: 2025-08-03
Versão: 1.0
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================================================
# SCHEMAS BASE
# ============================================================================

class BaseSchema(BaseModel):
    """Schema base com configurações comuns."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp."""
    created_at: Optional[datetime] = Field(None, description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização")

# ============================================================================
# ENUMS
# ============================================================================

class StatusEnum(str, Enum):
    """Status de entidades."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDO = "concluido"
    ERRO = "erro"

class ContextoEnum(str, Enum):
    """Contexto de competições."""
    MASCULINO = "Masculino"
    FEMININO = "Feminino"
    DESCONHECIDO = "Desconhecido"

# ============================================================================
# SCHEMAS DE COMPETIÇÕES
# ============================================================================

class CompeticaoBase(BaseSchema):
    """Schema base para competições."""
    nome: str = Field(..., description="Nome da competição", min_length=1, max_length=100)
    url: Optional[str] = Field(None, description="URL da competição no FBRef")
    contexto: ContextoEnum = Field(default=ContextoEnum.DESCONHECIDO, description="Contexto da competição")
    ativa: bool = Field(default=True, description="Se a competição está ativa")

class CompeticaoCreate(CompeticaoBase):
    """Schema para criação de competição."""
    pass

class CompeticaoUpdate(BaseSchema):
    """Schema para atualização de competição."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    contexto: Optional[ContextoEnum] = None
    ativa: Optional[bool] = None

class CompeticaoResponse(CompeticaoBase, TimestampMixin):
    """Schema de resposta para competição."""
    id: int = Field(..., description="ID único da competição")
    total_links: Optional[int] = Field(None, description="Total de links para coleta")
    total_partidas: Optional[int] = Field(None, description="Total de partidas")

class CompeticaoList(BaseSchema):
    """Schema para lista de competições."""
    items: List[CompeticaoResponse]
    total: int = Field(..., description="Total de competições")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

# ============================================================================
# SCHEMAS DE CLUBES
# ============================================================================

class ClubeBase(BaseSchema):
    """Schema base para clubes."""
    nome: str = Field(..., description="Nome do clube", min_length=1, max_length=100)
    url_fbref: Optional[str] = Field(None, description="URL do clube no FBRef")
    pais: Optional[str] = Field(None, description="País do clube", max_length=50)

class ClubeCreate(ClubeBase):
    """Schema para criação de clube."""
    pass

class ClubeUpdate(BaseSchema):
    """Schema para atualização de clube."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    url_fbref: Optional[str] = None
    pais: Optional[str] = Field(None, max_length=50)

class ClubeResponse(ClubeBase, TimestampMixin):
    """Schema de resposta para clube."""
    id: int = Field(..., description="ID único do clube")
    total_jogadores: Optional[int] = Field(None, description="Total de jogadores")
    total_partidas: Optional[int] = Field(None, description="Total de partidas")

class ClubeList(BaseSchema):
    """Schema para lista de clubes."""
    items: List[ClubeResponse]
    total: int = Field(..., description="Total de clubes")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

# ============================================================================
# SCHEMAS DE JOGADORES
# ============================================================================

class JogadorBase(BaseSchema):
    """Schema base para jogadores."""
    nome: str = Field(..., description="Nome do jogador", min_length=1, max_length=100)
    url_fbref: Optional[str] = Field(None, description="URL do jogador no FBRef")
    posicao: Optional[str] = Field(None, description="Posição do jogador", max_length=20)
    idade: Optional[int] = Field(None, description="Idade do jogador", ge=15, le=50)
    nacionalidade: Optional[str] = Field(None, description="Nacionalidade", max_length=50)

class JogadorCreate(JogadorBase):
    """Schema para criação de jogador."""
    clube_id: Optional[int] = Field(None, description="ID do clube")

class JogadorUpdate(BaseSchema):
    """Schema para atualização de jogador."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    url_fbref: Optional[str] = None
    posicao: Optional[str] = Field(None, max_length=20)
    idade: Optional[int] = Field(None, ge=15, le=50)
    nacionalidade: Optional[str] = Field(None, max_length=50)
    clube_id: Optional[int] = None

class JogadorResponse(JogadorBase, TimestampMixin):
    """Schema de resposta para jogador."""
    id: int = Field(..., description="ID único do jogador")
    clube_id: Optional[int] = Field(None, description="ID do clube")
    clube_nome: Optional[str] = Field(None, description="Nome do clube")

class JogadorList(BaseSchema):
    """Schema para lista de jogadores."""
    items: List[JogadorResponse]
    total: int = Field(..., description="Total de jogadores")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

# ============================================================================
# SCHEMAS DE PARTIDAS
# ============================================================================

class PartidaBase(BaseSchema):
    """Schema base para partidas."""
    data_partida: Optional[datetime] = Field(None, description="Data e hora da partida")
    clube_casa: Optional[str] = Field(None, description="Clube da casa", max_length=100)
    clube_visitante: Optional[str] = Field(None, description="Clube visitante", max_length=100)
    gols_casa: Optional[int] = Field(None, description="Gols do clube da casa", ge=0)
    gols_visitante: Optional[int] = Field(None, description="Gols do clube visitante", ge=0)
    url_fbref: Optional[str] = Field(None, description="URL da partida no FBRef")

class PartidaResponse(PartidaBase, TimestampMixin):
    """Schema de resposta para partida."""
    id: int = Field(..., description="ID único da partida")
    competicao_id: Optional[int] = Field(None, description="ID da competição")
    competicao_nome: Optional[str] = Field(None, description="Nome da competição")
    resultado: Optional[str] = Field(None, description="Resultado da partida")

class PartidaList(BaseSchema):
    """Schema para lista de partidas."""
    items: List[PartidaResponse]
    total: int = Field(..., description="Total de partidas")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

# ============================================================================
# SCHEMAS DE FILTROS E PARÂMETROS
# ============================================================================

class PaginationParams(BaseSchema):
    """Parâmetros de paginação."""
    page: int = Field(default=1, description="Página (inicia em 1)", ge=1)
    size: int = Field(default=50, description="Itens por página", ge=1, le=100)

class CompeticaoFilter(PaginationParams):
    """Filtros para competições."""
    nome: Optional[str] = Field(None, description="Filtrar por nome (busca parcial)")
    contexto: Optional[ContextoEnum] = Field(None, description="Filtrar por contexto")
    ativa: Optional[bool] = Field(None, description="Filtrar por status ativo")

class ClubeFilter(PaginationParams):
    """Filtros para clubes."""
    nome: Optional[str] = Field(None, description="Filtrar por nome (busca parcial)")
    pais: Optional[str] = Field(None, description="Filtrar por país")

class JogadorFilter(PaginationParams):
    """Filtros para jogadores."""
    nome: Optional[str] = Field(None, description="Filtrar por nome (busca parcial)")
    posicao: Optional[str] = Field(None, description="Filtrar por posição")
    clube_id: Optional[int] = Field(None, description="Filtrar por clube")
    nacionalidade: Optional[str] = Field(None, description="Filtrar por nacionalidade")
    idade_min: Optional[int] = Field(None, description="Idade mínima", ge=15)
    idade_max: Optional[int] = Field(None, description="Idade máxima", le=50)

# ============================================================================
# SCHEMAS DE RESPOSTA GERAL
# ============================================================================

class HealthResponse(BaseSchema):
    """Schema de resposta para health check."""
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    database: str = Field(..., description="Status do banco de dados")
    uptime: Optional[str] = Field(None, description="Tempo de atividade")

class ErrorResponse(BaseSchema):
    """Schema de resposta para erros."""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    detail: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")

class MessageResponse(BaseSchema):
    """Schema de resposta para mensagens gerais."""
    message: str = Field(..., description="Mensagem")
    success: bool = Field(default=True, description="Indica sucesso")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
