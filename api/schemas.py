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
# SCHEMAS DE AUTENTICAÇÃO
# ============================================================================

class TokenData(BaseModel):
    """Dados contidos no token JWT."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = []
    exp: Optional[datetime] = None

class UserInDB(BaseModel):
    """Modelo de usuário para autenticação."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str
    scopes: List[str] = []

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

class EstatisticasAvancadas(BaseSchema):
    """Schema para estatísticas avançadas de partidas."""
    xg_casa: Optional[float] = Field(None, description="Expected Goals do time da casa")
    xg_visitante: Optional[float] = Field(None, description="Expected Goals do time visitante")
    xa_casa: Optional[float] = Field(None, description="Expected Assists do time da casa")
    xa_visitante: Optional[float] = Field(None, description="Expected Assists do time visitante")
    formacao_casa: Optional[str] = Field(None, description="Formação tática do time da casa (ex: 4-3-3)")
    formacao_visitante: Optional[str] = Field(None, description="Formação tática do time visitante (ex: 4-3-3)")
    posse_bola_casa: Optional[float] = Field(None, description="Porcentagem de posse de bola do time da casa")
    posse_bola_visitante: Optional[float] = Field(None, description="Porcentagem de posse de bola do time visitante")
    chutes_casa: Optional[int] = Field(None, description="Total de chutes do time da casa")
    chutes_visitante: Optional[int] = Field(None, description="Total de chutes do time visitante")
    chutes_no_gol_casa: Optional[int] = Field(None, description="Chutes no gol do time da casa")
    chutes_no_gol_visitante: Optional[int] = Field(None, description="Chutes no gol do time visitante")


class PartidaResponse(PartidaBase, TimestampMixin):
    """Schema de resposta para partida."""
    id: int = Field(..., description="ID único da partida")
    competicao_id: Optional[int] = Field(None, description="ID da competição")
    competicao_nome: Optional[str] = Field(None, description="Nome da competição")
    resultado: Optional[str] = Field(None, description="Resultado da partida")
    estatisticas_avancadas: Optional[EstatisticasAvancadas] = Field(
        None, 
        description="Estatísticas avançadas da partida (xG, xA, formações, etc.)"
    )

class MatchDetailResponse(PartidaResponse):
    """Schema detalhado para resposta de partida com informações adicionais."""
    data_partida: Optional[datetime] = Field(None, description="Data da partida")
    hora_partida: Optional[str] = Field(None, description="Hora da partida")
    clube_casa_id: Optional[int] = Field(None, description="ID do clube da casa")
    clube_casa_nome: Optional[str] = Field(None, description="Nome do clube da casa")
    clube_visitante_id: Optional[int] = Field(None, description="ID do clube visitante")
    clube_visitante_nome: Optional[str] = Field(None, description="Nome do clube visitante")
    gols_casa: Optional[int] = Field(None, description="Gols do time da casa")
    gols_visitante: Optional[int] = Field(None, description="Gols do time visitante")
    rodada: Optional[str] = Field(None, description="Rodada da competição")
    temporada: Optional[str] = Field(None, description="Temporada da partida")
    status: Optional[str] = Field(None, description="Status da partida")
    
    class Config:
        from_attributes = True

class MatchItem(BaseModel):
    """Item de partida para listagem."""
    id: int = Field(..., description="ID único da partida")
    data_partida: Optional[datetime] = Field(None, description="Data da partida")
    hora_partida: Optional[str] = Field(None, description="Hora da partida")
    competicao_id: Optional[int] = Field(None, description="ID da competição")
    clube_casa_id: Optional[int] = Field(None, description="ID do clube da casa")
    clube_visitante_id: Optional[int] = Field(None, description="ID do clube visitante")
    gols_casa: Optional[int] = Field(None, description="Gols do time da casa")
    gols_visitante: Optional[int] = Field(None, description="Gols do time visitante")
    resultado: Optional[str] = Field(None, description="Resultado da partida")
    rodada: Optional[str] = Field(None, description="Rodada da competição")
    temporada: Optional[str] = Field(None, description="Temporada da partida")
    status: Optional[str] = Field(None, description="Status da partida")

class MatchList(BaseModel):
    """Schema para lista de partidas."""
    items: List[MatchItem] = Field(..., description="Lista de partidas")
    total: int = Field(..., description="Total de partidas")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")
    
    class Config:
        from_attributes = True

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
# SCHEMAS DE ANÁLISE DE SENTIMENTO
# ============================================================================

class SentimentoClubeSchema(BaseModel):
    """Schema para análise de sentimento de notícias de clubes."""
    noticia_id: int = Field(..., description="ID da notícia analisada")
    sentimento_geral: float = Field(
        ..., 
        description="Pontuação de sentimento entre -1 (negativo) e 1 (positivo)",
        ge=-1.0,
        le=1.0
    )
    confianca: float = Field(
        ..., 
        description="Nível de confiança da análise (0 a 1)",
        ge=0.0,
        le=1.0
    )
    polaridade: str = Field(
        ..., 
        description="Classificação do sentimento",
        pattern="^(positivo|negativo|neutro)$"
    )
    palavras_chave: List[str] = Field(
        default_factory=list, 
        description="Palavras-chave extraídas do conteúdo"
    )
    topicos: List[str] = Field(
        default_factory=list, 
        description="Tópicos principais identificados"
    )
    modelo: str = Field(..., description="Nome/versão do modelo utilizado")
    analisado_em: datetime = Field(..., description="Data e hora da análise")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "noticia_id": 123,
                "sentimento_geral": 0.75,
                "confianca": 0.92,
                "polaridade": "positivo",
                "palavras_chave": ["vitória", "gol", "jogador", "técnico", "time"],
                "topicos": ["desempenho", "resultado", "elogios"],
                "modelo": "lexico_basico_v1",
                "analisado_em": "2025-08-10T15:30:00.000Z"
            }
        }


# ============================================================================
# SCHEMAS DE NOTÍCIAS DE CLUBES
# ============================================================================

class NoticiaClubeBase(BaseSchema):
    """Schema base para notícias de clubes."""
    titulo: str = Field(..., description="Título da notícia", max_length=255)
    url_noticia: str = Field(..., description="URL da notícia", max_length=500)
    fonte: str = Field(..., description="Fonte da notícia", max_length=100)
    data_publicacao: datetime = Field(..., description="Data de publicação da notícia")
    resumo: Optional[str] = Field(None, description="Resumo da notícia")
    conteudo_completo: Optional[str] = Field(None, description="Conteúdo completo da notícia")
    autor: Optional[str] = Field(None, description="Autor da notícia", max_length=100)
    imagem_destaque: Optional[str] = Field(None, description="URL da imagem de destaque", max_length=500)


class NoticiaClubeCreate(NoticiaClubeBase):
    """Schema para criação de notícia de clube."""
    clube_id: int = Field(..., description="ID do clube relacionado à notícia")


class NoticiaClubeUpdate(BaseSchema):
    """Schema para atualização de notícia de clube."""
    titulo: Optional[str] = Field(None, description="Título da notícia", max_length=255)
    url_noticia: Optional[str] = Field(None, description="URL da notícia", max_length=500)
    fonte: Optional[str] = Field(None, description="Fonte da notícia", max_length=100)
    data_publicacao: Optional[datetime] = Field(None, description="Data de publicação da notícia")
    resumo: Optional[str] = Field(None, description="Resumo da notícia")
    conteudo_completo: Optional[str] = Field(None, description="Conteúdo completo da notícia")
    autor: Optional[str] = Field(None, description="Autor da notícia", max_length=100)
    imagem_destaque: Optional[str] = Field(None, description="URL da imagem de destaque", max_length=500)
    clube_id: Optional[int] = Field(None, description="ID do clube relacionado à notícia")


class NoticiaClubeResponse(NoticiaClubeBase, TimestampMixin):
    """Schema de resposta para notícia de clube."""
    id: int = Field(..., description="ID único da notícia")
    clube_id: int = Field(..., description="ID do clube relacionado à notícia")
    clube_nome: Optional[str] = Field(None, description="Nome do clube")
    
    # Campos de análise de sentimento
    sentimento_geral: Optional[float] = Field(
        None, 
        description="Pontuação de sentimento entre -1 (negativo) e 1 (positivo)",
        ge=-1.0,
        le=1.0
    )
    confianca_sentimento: Optional[float] = Field(
        None,
        description="Nível de confiança da análise de sentimento (0 a 1)",
        ge=0.0,
        le=1.0
    )
    polaridade: Optional[str] = Field(
        None,
        description="Classificação do sentimento (positivo, negativo, neutro)",
        pattern="^(positivo|negativo|neutro)?$"
    )
    topicos: Optional[str] = Field(
        None,
        description="Tópicos principais identificados na notícia (separados por vírgula)"
    )
    palavras_chave: Optional[str] = Field(
        None,
        description="Palavras-chave extraídas do conteúdo (separadas por vírgula)"
    )
    modelo_analise: Optional[str] = Field(
        None,
        description="Nome/versão do modelo de análise de sentimento utilizado"
    )
    analisado_em: Optional[datetime] = Field(
        None,
        description="Data e hora em que a análise de sentimento foi realizada"
    )


class NoticiaClubeList(BaseSchema):
    """Schema para lista de notícias de clubes."""
    items: List[NoticiaClubeResponse] = Field(..., description="Lista de notícias")
    total: int = Field(..., description="Total de notícias")
    page: int = Field(1, description="Página atual")
    size: int = Field(50, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")


# ============================================================================
# SCHEMAS DE REDES SOCIAIS
# ============================================================================

class PostRedeSocialBase(BaseModel):
    """Schema base para posts de redes sociais."""
    rede_social: str = Field(..., description="Plataforma de rede social (ex: 'Twitter', 'Instagram', 'Facebook')", max_length=50)
    post_id: str = Field(..., description="ID único do post na plataforma de origem", max_length=100)
    conteudo: str = Field(..., description="Conteúdo textual do post")
    data_postagem: datetime = Field(..., description="Data e hora em que o post foi publicado")
    curtidas: int = Field(..., description="Número de curtidas/reactions do post", ge=0)
    comentarios: int = Field(..., description="Número de comentários no post", ge=0)
    compartilhamentos: int = Field(..., description="Número de compartilhamentos/retweets", ge=0)
    url_post: Optional[str] = Field(None, description="URL direta para o post na rede social")
    midia_url: Optional[str] = Field(None, description="URL da mídia anexada ao post (imagem/vídeo)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "rede_social": "Twitter",
                "post_id": "twitter_123456789",
                "conteudo": "Grande vitória do time hoje! ⚽🔥 #VamosTime",
                "data_postagem": "2025-08-06T20:30:00Z",
                "curtidas": 1250,
                "comentarios": 89,
                "compartilhamentos": 210,
                "url_post": "https://twitter.com/clube/status/123456789",
                "midia_url": "https://picsum.photos/800/600"
            }
        }

class PostRedeSocialCreate(PostRedeSocialBase):
    """Schema para criação de post em rede social."""
    clube_id: int = Field(..., description="ID do clube dono do post")

class PostRedeSocialUpdate(BaseModel):
    """Schema para atualização de post em rede social."""
    conteudo: Optional[str] = Field(None, description="Conteúdo textual do post")
    curtidas: Optional[int] = Field(None, description="Número de curtidas/reactions do post", ge=0)
    comentarios: Optional[int] = Field(None, description="Número de comentários no post", ge=0)
    compartilhamentos: Optional[int] = Field(None, description="Número de compartilhamentos/retweets", ge=0)
    url_post: Optional[str] = Field(None, description="URL direta para o post na rede social")
    midia_url: Optional[str] = Field(None, description="URL da mídia anexada ao post (imagem/vídeo)")

class PostRedeSocialResponse(PostRedeSocialBase):
    """Schema de resposta para post em rede social."""
    id: int = Field(..., description="ID único do post")
    clube_id: int = Field(..., description="ID do clube dono do post")
    clube_nome: Optional[str] = Field(None, description="Nome do clube")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")

class PostRedeSocialList(BaseModel):
    """Schema para lista de posts de redes sociais."""
    items: List[PostRedeSocialResponse] = Field(..., description="Lista de posts")
    total: int = Field(..., description="Total de posts")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=20, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

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


# ============================================================================
# SCHEMAS DE RECOMENDAÇÕES DE APOSTAS
# ============================================================================

class RecomendacaoApostaBase(BaseSchema):
    """Schema base para recomendações de apostas."""
    partida_id: int = Field(..., description="ID da partida")
    mercado_aposta: str = Field(..., description="Tipo de mercado de aposta (ex: '1X2', 'Over/Under')", max_length=100)
    previsao: str = Field(..., description="Previsão do resultado", max_length=100)
    probabilidade: float = Field(..., description="Probabilidade calculada pelo modelo", ge=0.0, le=1.0)
    odd_justa: float = Field(..., description="Odd justa calculada", ge=1.0)
    rating: float = Field(..., description="Rating da recomendação (1-5 estrelas)", ge=1.0, le=5.0)
    confianca_modelo: float = Field(..., description="Confiança do modelo na previsão", ge=0.0, le=1.0)
    modelo_utilizado: str = Field(..., description="Nome/versão do modelo utilizado", max_length=100)
    features_utilizadas: Optional[str] = Field(None, description="Features utilizadas para a previsão")
    status: str = Field(default="pendente", description="Status da recomendação", max_length=50)

class RecomendacaoApostaCreate(RecomendacaoApostaBase):
    """Schema para criação de recomendação de aposta."""
    pass

class RecomendacaoApostaUpdate(BaseSchema):
    """Schema para atualização de recomendação de aposta."""
    mercado_aposta: Optional[str] = Field(None, max_length=100)
    previsao: Optional[str] = Field(None, max_length=100)
    probabilidade: Optional[float] = Field(None, ge=0.0, le=1.0)
    odd_justa: Optional[float] = Field(None, ge=1.0)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    confianca_modelo: Optional[float] = Field(None, ge=0.0, le=1.0)
    modelo_utilizado: Optional[str] = Field(None, max_length=100)
    features_utilizadas: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    resultado_real: Optional[str] = Field(None, description="Resultado real da aposta", max_length=100)
    roi: Optional[float] = Field(None, description="ROI da aposta se foi realizada")

class RecomendacaoApostaResponse(RecomendacaoApostaBase, TimestampMixin):
    """Schema de resposta para recomendação de aposta."""
    id: int = Field(..., description="ID único da recomendação")
    resultado_real: Optional[str] = Field(None, description="Resultado real da aposta")
    roi: Optional[float] = Field(None, description="ROI da aposta se foi realizada")
    partida_info: Optional[Dict[str, Any]] = Field(None, description="Informações básicas da partida")

class RecomendacaoApostaList(BaseSchema):
    """Schema para lista de recomendações de apostas."""
    items: List[RecomendacaoApostaResponse] = Field(..., description="Lista de recomendações")
    total: int = Field(..., description="Total de recomendações")
    page: int = Field(default=1, description="Página atual")
    size: int = Field(default=20, description="Itens por página")
    pages: int = Field(..., description="Total de páginas")

class RecomendacaoEstatisticas(BaseSchema):
    """Schema para estatísticas de recomendações."""
    total_recomendacoes: int = Field(..., description="Total de recomendações")
    recomendacoes_por_mercado: List[Dict[str, Any]] = Field(..., description="Recomendações agrupadas por mercado")
    taxa_acerto: Optional[float] = Field(None, description="Taxa de acerto das recomendações")
    roi_medio: Optional[float] = Field(None, description="ROI médio das apostas realizadas")

# ============================================================================
# SCHEMAS DE ANÁLISE DE SENTIMENTO
# ============================================================================

class SentimentoClubeSchema(BaseModel):
    """Schema para resposta de análise de sentimento de um clube."""
    clube_id: int = Field(..., description="ID do clube")
    nome_clube: str = Field(..., description="Nome do clube")
    sentimento_medio_noticias: float = Field(..., description="Score médio de sentimento das notícias")
    noticias_analisadas: int = Field(..., description="Número de notícias analisadas")
    sentimento_medio_posts: Optional[float] = Field(None, description="Score médio de sentimento dos posts")
    posts_analisados: Optional[int] = Field(None, description="Número de posts analisados")
    sentimento_geral: str = Field(..., description="Classificação geral do sentimento")
    confianca_media: Optional[float] = Field(None, description="Confiança média da análise")
    ultima_atualizacao: Optional[datetime] = Field(None, description="Data da última atualização da análise")

class SentimentoEstatisticasSchema(BaseModel):
    """Schema para estatísticas gerais de sentimento."""
    total_noticias: int = Field(..., description="Total de notícias analisadas")
    total_posts: int = Field(..., description="Total de posts analisados")
    distribuicao_sentimento: Dict[str, int] = Field(..., description="Distribuição por tipo de sentimento")
    score_medio_geral: float = Field(..., description="Score médio geral de sentimento")
    top_clubes_positivos: List[Dict[str, Any]] = Field(..., description="Top clubes com sentimento positivo")
    top_clubes_negativos: List[Dict[str, Any]] = Field(..., description="Top clubes com sentimento negativo")
    ultima_atualizacao: datetime = Field(..., description="Data da última atualização das estatísticas")

# Schemas para Recomendações de Apostas
class RecomendacaoApostaSchema(BaseModel):
    id: int = Field(..., description="ID da recomendação")
    partida_id: int = Field(..., description="ID da partida")
    mercado_aposta: str = Field(..., description="Tipo de mercado (ex: 'Resultado Final', 'Ambas Marcam')")
    previsao: str = Field(..., description="Previsão gerada pelo modelo")
    probabilidade: float = Field(..., description="Probabilidade da previsão (0.0 a 1.0)")
    odd_justa: float = Field(..., description="Odd justa calculada (1/probabilidade)")
    data_geracao: datetime = Field(..., description="Data de geração da recomendação")
    
    # Dados da partida
    time_casa: str = Field(..., description="Nome do time da casa")
    time_visitante: str = Field(..., description="Nome do time visitante")
    data_partida: str = Field(..., description="Data da partida")

class RecomendacaoResumoSchema(BaseModel):
    total_recomendacoes: int = Field(..., description="Total de recomendações geradas")
    recomendacoes_por_mercado: Dict[str, int] = Field(..., description="Distribuição por tipo de mercado")
    probabilidade_media: float = Field(..., description="Probabilidade média das recomendações")
    ultima_atualizacao: datetime = Field(..., description="Data da última atualização")

class GerarRecomendacoesRequest(BaseModel):
    dias_futuros: int = Field(default=7, description="Número de dias no futuro para gerar recomendações")
    forcar_reprocessamento: bool = Field(default=False, description="Forçar reprocessamento mesmo se já existirem recomendações")
