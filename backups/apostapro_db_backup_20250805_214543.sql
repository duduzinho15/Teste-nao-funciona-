--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO apostapro_user;

--
-- Name: clubes; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.clubes (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    nome_completo character varying(500),
    url_fbref text,
    pais_id integer,
    cidade character varying(100),
    fundacao integer,
    ativo boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.clubes OWNER TO apostapro_user;

--
-- Name: clubes_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.clubes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clubes_id_seq OWNER TO apostapro_user;

--
-- Name: clubes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.clubes_id_seq OWNED BY public.clubes.id;


--
-- Name: competicoes; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.competicoes (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    url text NOT NULL,
    contexto character varying(100),
    pais character varying(100),
    tipo character varying(50),
    ativa boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.competicoes OWNER TO apostapro_user;

--
-- Name: competicoes_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.competicoes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competicoes_id_seq OWNER TO apostapro_user;

--
-- Name: competicoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.competicoes_id_seq OWNED BY public.competicoes.id;


--
-- Name: estatisticas_clube; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.estatisticas_clube (
    id integer NOT NULL,
    clube_id integer NOT NULL,
    competicao_id integer NOT NULL,
    temporada character varying(20) NOT NULL,
    jogos integer,
    vitorias integer,
    empates integer,
    derrotas integer,
    gols_pro integer,
    gols_contra integer,
    saldo_gols integer,
    pontos integer,
    posicao integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.estatisticas_clube OWNER TO apostapro_user;

--
-- Name: estatisticas_clube_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.estatisticas_clube_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estatisticas_clube_id_seq OWNER TO apostapro_user;

--
-- Name: estatisticas_clube_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.estatisticas_clube_id_seq OWNED BY public.estatisticas_clube.id;


--
-- Name: estatisticas_jogador_competicao; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.estatisticas_jogador_competicao (
    id integer NOT NULL,
    jogador_id integer NOT NULL,
    competicao_id integer NOT NULL,
    temporada character varying(20) NOT NULL,
    jogos integer,
    jogos_titularidade integer,
    minutos integer,
    gols integer,
    assistencias integer,
    cartoes_amarelos integer,
    cartoes_vermelhos integer,
    chutes integer,
    chutes_no_gol integer,
    passes_certos integer,
    passes_tentados integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    xg double precision,
    xa double precision,
    posicao_principal character varying(20),
    minutos_por_jogo double precision
);


ALTER TABLE public.estatisticas_jogador_competicao OWNER TO apostapro_user;

--
-- Name: COLUMN estatisticas_jogador_competicao.xg; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_jogador_competicao.xg IS 'Expected Goals do jogador';


--
-- Name: COLUMN estatisticas_jogador_competicao.xa; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_jogador_competicao.xa IS 'Expected Assists do jogador';


--
-- Name: COLUMN estatisticas_jogador_competicao.posicao_principal; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_jogador_competicao.posicao_principal IS 'Posição principal jogada na competição';


--
-- Name: COLUMN estatisticas_jogador_competicao.minutos_por_jogo; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_jogador_competicao.minutos_por_jogo IS 'Média de minutos por jogo';


--
-- Name: estatisticas_jogador_competicao_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.estatisticas_jogador_competicao_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estatisticas_jogador_competicao_id_seq OWNER TO apostapro_user;

--
-- Name: estatisticas_jogador_competicao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.estatisticas_jogador_competicao_id_seq OWNED BY public.estatisticas_jogador_competicao.id;


--
-- Name: estatisticas_jogador_geral; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.estatisticas_jogador_geral (
    id integer NOT NULL,
    jogador_id integer NOT NULL,
    temporada character varying(20) NOT NULL,
    jogos integer,
    jogos_titularidade integer,
    minutos integer,
    gols integer,
    assistencias integer,
    cartoes_amarelos integer,
    cartoes_vermelhos integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.estatisticas_jogador_geral OWNER TO apostapro_user;

--
-- Name: estatisticas_jogador_geral_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.estatisticas_jogador_geral_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estatisticas_jogador_geral_id_seq OWNER TO apostapro_user;

--
-- Name: estatisticas_jogador_geral_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.estatisticas_jogador_geral_id_seq OWNED BY public.estatisticas_jogador_geral.id;


--
-- Name: estatisticas_partidas; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.estatisticas_partidas (
    id integer NOT NULL,
    partida_id integer NOT NULL,
    posse_bola_casa double precision,
    posse_bola_visitante double precision,
    chutes_casa integer,
    chutes_visitante integer,
    chutes_no_gol_casa integer,
    chutes_no_gol_visitante integer,
    cartoes_amarelos_casa integer,
    cartoes_amarelos_visitante integer,
    cartoes_vermelhos_casa integer,
    cartoes_vermelhos_visitante integer,
    faltas_casa integer,
    faltas_visitante integer,
    escanteios_casa integer,
    escanteios_visitante integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    xg_casa double precision,
    xg_visitante double precision,
    xa_casa double precision,
    xa_visitante double precision,
    formacao_casa character varying(20),
    formacao_visitante character varying(20)
);


ALTER TABLE public.estatisticas_partidas OWNER TO apostapro_user;

--
-- Name: COLUMN estatisticas_partidas.xg_casa; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.xg_casa IS 'Expected Goals do time da casa';


--
-- Name: COLUMN estatisticas_partidas.xg_visitante; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.xg_visitante IS 'Expected Goals do time visitante';


--
-- Name: COLUMN estatisticas_partidas.xa_casa; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.xa_casa IS 'Expected Assists do time da casa';


--
-- Name: COLUMN estatisticas_partidas.xa_visitante; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.xa_visitante IS 'Expected Assists do time visitante';


--
-- Name: COLUMN estatisticas_partidas.formacao_casa; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.formacao_casa IS 'Formação tática do time da casa (ex: 4-3-3)';


--
-- Name: COLUMN estatisticas_partidas.formacao_visitante; Type: COMMENT; Schema: public; Owner: apostapro_user
--

COMMENT ON COLUMN public.estatisticas_partidas.formacao_visitante IS 'Formação tática do time visitante (ex: 4-3-3)';


--
-- Name: estatisticas_partidas_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.estatisticas_partidas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estatisticas_partidas_id_seq OWNER TO apostapro_user;

--
-- Name: estatisticas_partidas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.estatisticas_partidas_id_seq OWNED BY public.estatisticas_partidas.id;


--
-- Name: jogadores; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.jogadores (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    nome_completo character varying(500),
    url_fbref text,
    data_nascimento date,
    pais_id integer,
    posicao character varying(50),
    pe_preferido character varying(20),
    altura integer,
    peso integer,
    clube_atual_id integer,
    ativo boolean NOT NULL,
    aposentado boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jogadores OWNER TO apostapro_user;

--
-- Name: jogadores_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.jogadores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jogadores_id_seq OWNER TO apostapro_user;

--
-- Name: jogadores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.jogadores_id_seq OWNED BY public.jogadores.id;


--
-- Name: links_para_coleta; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.links_para_coleta (
    id integer NOT NULL,
    competicao_id integer NOT NULL,
    url text NOT NULL,
    tipo character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    tentativas integer NOT NULL,
    ultimo_erro text,
    processado_em timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_links_status CHECK (((status)::text = ANY (ARRAY[('pendente'::character varying)::text, ('processando'::character varying)::text, ('concluido'::character varying)::text, ('erro'::character varying)::text])))
);


ALTER TABLE public.links_para_coleta OWNER TO apostapro_user;

--
-- Name: links_para_coleta_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.links_para_coleta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.links_para_coleta_id_seq OWNER TO apostapro_user;

--
-- Name: links_para_coleta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.links_para_coleta_id_seq OWNED BY public.links_para_coleta.id;


--
-- Name: paises_clubes; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.paises_clubes (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    codigo_iso character varying(3),
    continente character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.paises_clubes OWNER TO apostapro_user;

--
-- Name: paises_clubes_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.paises_clubes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paises_clubes_id_seq OWNER TO apostapro_user;

--
-- Name: paises_clubes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.paises_clubes_id_seq OWNED BY public.paises_clubes.id;


--
-- Name: paises_jogadores; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.paises_jogadores (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    codigo_iso character varying(3),
    continente character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.paises_jogadores OWNER TO apostapro_user;

--
-- Name: paises_jogadores_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.paises_jogadores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paises_jogadores_id_seq OWNER TO apostapro_user;

--
-- Name: paises_jogadores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.paises_jogadores_id_seq OWNED BY public.paises_jogadores.id;


--
-- Name: partidas; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.partidas (
    id integer NOT NULL,
    competicao_id integer NOT NULL,
    clube_casa_id integer NOT NULL,
    clube_visitante_id integer NOT NULL,
    data_partida date,
    horario character varying(10),
    rodada character varying(50),
    temporada character varying(20),
    gols_casa integer,
    gols_visitante integer,
    resultado character varying(1),
    url_fbref text,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_partidas_clubes_diferentes CHECK ((clube_casa_id <> clube_visitante_id)),
    CONSTRAINT ck_partidas_status CHECK (((status)::text = ANY (ARRAY[('agendada'::character varying)::text, ('em_andamento'::character varying)::text, ('finalizada'::character varying)::text, ('cancelada'::character varying)::text])))
);


ALTER TABLE public.partidas OWNER TO apostapro_user;

--
-- Name: partidas_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.partidas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partidas_id_seq OWNER TO apostapro_user;

--
-- Name: partidas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.partidas_id_seq OWNED BY public.partidas.id;


--
-- Name: records_vs_opponents; Type: TABLE; Schema: public; Owner: apostapro_user
--

CREATE TABLE public.records_vs_opponents (
    id integer NOT NULL,
    clube_id integer NOT NULL,
    oponente_id integer NOT NULL,
    jogos_total integer,
    vitorias integer,
    empates integer,
    derrotas integer,
    gols_pro integer,
    gols_contra integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_records_clubes_diferentes CHECK ((clube_id <> oponente_id))
);


ALTER TABLE public.records_vs_opponents OWNER TO apostapro_user;

--
-- Name: records_vs_opponents_id_seq; Type: SEQUENCE; Schema: public; Owner: apostapro_user
--

CREATE SEQUENCE public.records_vs_opponents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.records_vs_opponents_id_seq OWNER TO apostapro_user;

--
-- Name: records_vs_opponents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: apostapro_user
--

ALTER SEQUENCE public.records_vs_opponents_id_seq OWNED BY public.records_vs_opponents.id;


--
-- Name: clubes id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.clubes ALTER COLUMN id SET DEFAULT nextval('public.clubes_id_seq'::regclass);


--
-- Name: competicoes id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.competicoes ALTER COLUMN id SET DEFAULT nextval('public.competicoes_id_seq'::regclass);


--
-- Name: estatisticas_clube id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_clube ALTER COLUMN id SET DEFAULT nextval('public.estatisticas_clube_id_seq'::regclass);


--
-- Name: estatisticas_jogador_competicao id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_competicao ALTER COLUMN id SET DEFAULT nextval('public.estatisticas_jogador_competicao_id_seq'::regclass);


--
-- Name: estatisticas_jogador_geral id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_geral ALTER COLUMN id SET DEFAULT nextval('public.estatisticas_jogador_geral_id_seq'::regclass);


--
-- Name: estatisticas_partidas id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_partidas ALTER COLUMN id SET DEFAULT nextval('public.estatisticas_partidas_id_seq'::regclass);


--
-- Name: jogadores id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.jogadores ALTER COLUMN id SET DEFAULT nextval('public.jogadores_id_seq'::regclass);


--
-- Name: links_para_coleta id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.links_para_coleta ALTER COLUMN id SET DEFAULT nextval('public.links_para_coleta_id_seq'::regclass);


--
-- Name: paises_clubes id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_clubes ALTER COLUMN id SET DEFAULT nextval('public.paises_clubes_id_seq'::regclass);


--
-- Name: paises_jogadores id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_jogadores ALTER COLUMN id SET DEFAULT nextval('public.paises_jogadores_id_seq'::regclass);


--
-- Name: partidas id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.partidas ALTER COLUMN id SET DEFAULT nextval('public.partidas_id_seq'::regclass);


--
-- Name: records_vs_opponents id; Type: DEFAULT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.records_vs_opponents ALTER COLUMN id SET DEFAULT nextval('public.records_vs_opponents_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: clubes clubes_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.clubes
    ADD CONSTRAINT clubes_pkey PRIMARY KEY (id);


--
-- Name: competicoes competicoes_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.competicoes
    ADD CONSTRAINT competicoes_pkey PRIMARY KEY (id);


--
-- Name: estatisticas_clube estatisticas_clube_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_clube
    ADD CONSTRAINT estatisticas_clube_pkey PRIMARY KEY (id);


--
-- Name: estatisticas_jogador_competicao estatisticas_jogador_competicao_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_competicao
    ADD CONSTRAINT estatisticas_jogador_competicao_pkey PRIMARY KEY (id);


--
-- Name: estatisticas_jogador_geral estatisticas_jogador_geral_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_geral
    ADD CONSTRAINT estatisticas_jogador_geral_pkey PRIMARY KEY (id);


--
-- Name: estatisticas_partidas estatisticas_partidas_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_partidas
    ADD CONSTRAINT estatisticas_partidas_pkey PRIMARY KEY (id);


--
-- Name: jogadores jogadores_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.jogadores
    ADD CONSTRAINT jogadores_pkey PRIMARY KEY (id);


--
-- Name: links_para_coleta links_para_coleta_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.links_para_coleta
    ADD CONSTRAINT links_para_coleta_pkey PRIMARY KEY (id);


--
-- Name: paises_clubes paises_clubes_nome_key; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_clubes
    ADD CONSTRAINT paises_clubes_nome_key UNIQUE (nome);


--
-- Name: paises_clubes paises_clubes_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_clubes
    ADD CONSTRAINT paises_clubes_pkey PRIMARY KEY (id);


--
-- Name: paises_jogadores paises_jogadores_nome_key; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_jogadores
    ADD CONSTRAINT paises_jogadores_nome_key UNIQUE (nome);


--
-- Name: paises_jogadores paises_jogadores_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.paises_jogadores
    ADD CONSTRAINT paises_jogadores_pkey PRIMARY KEY (id);


--
-- Name: partidas partidas_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_pkey PRIMARY KEY (id);


--
-- Name: records_vs_opponents records_vs_opponents_pkey; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.records_vs_opponents
    ADD CONSTRAINT records_vs_opponents_pkey PRIMARY KEY (id);


--
-- Name: competicoes uq_competicao_nome_contexto; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.competicoes
    ADD CONSTRAINT uq_competicao_nome_contexto UNIQUE (nome, contexto);


--
-- Name: estatisticas_clube uq_estatistica_clube_temporada; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_clube
    ADD CONSTRAINT uq_estatistica_clube_temporada UNIQUE (clube_id, competicao_id, temporada);


--
-- Name: estatisticas_jogador_competicao uq_estatistica_jogador_competicao_temporada; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_competicao
    ADD CONSTRAINT uq_estatistica_jogador_competicao_temporada UNIQUE (jogador_id, competicao_id, temporada);


--
-- Name: estatisticas_jogador_geral uq_estatistica_jogador_geral_temporada; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_geral
    ADD CONSTRAINT uq_estatistica_jogador_geral_temporada UNIQUE (jogador_id, temporada);


--
-- Name: records_vs_opponents uq_record_clube_oponente; Type: CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.records_vs_opponents
    ADD CONSTRAINT uq_record_clube_oponente UNIQUE (clube_id, oponente_id);


--
-- Name: idx_clubes_ativo; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_clubes_ativo ON public.clubes USING btree (ativo);


--
-- Name: idx_clubes_nome; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_clubes_nome ON public.clubes USING btree (nome);


--
-- Name: idx_clubes_pais; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_clubes_pais ON public.clubes USING btree (pais_id);


--
-- Name: idx_competicoes_ativa; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_competicoes_ativa ON public.competicoes USING btree (ativa);


--
-- Name: idx_competicoes_contexto; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_competicoes_contexto ON public.competicoes USING btree (contexto);


--
-- Name: idx_competicoes_nome; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_competicoes_nome ON public.competicoes USING btree (nome);


--
-- Name: idx_estatisticas_clube_clube; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_clube_clube ON public.estatisticas_clube USING btree (clube_id);


--
-- Name: idx_estatisticas_clube_competicao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_clube_competicao ON public.estatisticas_clube USING btree (competicao_id);


--
-- Name: idx_estatisticas_clube_temporada; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_clube_temporada ON public.estatisticas_clube USING btree (temporada);


--
-- Name: idx_estatisticas_jogador_comp_competicao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_jogador_comp_competicao ON public.estatisticas_jogador_competicao USING btree (competicao_id);


--
-- Name: idx_estatisticas_jogador_comp_jogador; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_jogador_comp_jogador ON public.estatisticas_jogador_competicao USING btree (jogador_id);


--
-- Name: idx_estatisticas_jogador_comp_temporada; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_jogador_comp_temporada ON public.estatisticas_jogador_competicao USING btree (temporada);


--
-- Name: idx_estatisticas_jogador_geral_jogador; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_jogador_geral_jogador ON public.estatisticas_jogador_geral USING btree (jogador_id);


--
-- Name: idx_estatisticas_jogador_geral_temporada; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_jogador_geral_temporada ON public.estatisticas_jogador_geral USING btree (temporada);


--
-- Name: idx_estatisticas_partida; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_partida ON public.estatisticas_partidas USING btree (partida_id);


--
-- Name: idx_estatisticas_partida_formacao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_partida_formacao ON public.estatisticas_partidas USING btree (formacao_casa, formacao_visitante);


--
-- Name: idx_estatisticas_partida_xg; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_estatisticas_partida_xg ON public.estatisticas_partidas USING btree (xg_casa, xg_visitante);


--
-- Name: idx_jogadores_ativo; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_jogadores_ativo ON public.jogadores USING btree (ativo);


--
-- Name: idx_jogadores_clube_atual; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_jogadores_clube_atual ON public.jogadores USING btree (clube_atual_id);


--
-- Name: idx_jogadores_nome; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_jogadores_nome ON public.jogadores USING btree (nome);


--
-- Name: idx_jogadores_pais; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_jogadores_pais ON public.jogadores USING btree (pais_id);


--
-- Name: idx_jogadores_posicao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_jogadores_posicao ON public.jogadores USING btree (posicao);


--
-- Name: idx_links_competicao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_links_competicao ON public.links_para_coleta USING btree (competicao_id);


--
-- Name: idx_links_processado; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_links_processado ON public.links_para_coleta USING btree (processado_em);


--
-- Name: idx_links_status; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_links_status ON public.links_para_coleta USING btree (status);


--
-- Name: idx_links_tipo; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_links_tipo ON public.links_para_coleta USING btree (tipo);


--
-- Name: idx_partidas_casa; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_casa ON public.partidas USING btree (clube_casa_id);


--
-- Name: idx_partidas_competicao; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_competicao ON public.partidas USING btree (competicao_id);


--
-- Name: idx_partidas_data; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_data ON public.partidas USING btree (data_partida);


--
-- Name: idx_partidas_status; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_status ON public.partidas USING btree (status);


--
-- Name: idx_partidas_temporada; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_temporada ON public.partidas USING btree (temporada);


--
-- Name: idx_partidas_visitante; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_partidas_visitante ON public.partidas USING btree (clube_visitante_id);


--
-- Name: idx_records_clube; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_records_clube ON public.records_vs_opponents USING btree (clube_id);


--
-- Name: idx_records_oponente; Type: INDEX; Schema: public; Owner: apostapro_user
--

CREATE INDEX idx_records_oponente ON public.records_vs_opponents USING btree (oponente_id);


--
-- Name: clubes clubes_pais_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.clubes
    ADD CONSTRAINT clubes_pais_id_fkey FOREIGN KEY (pais_id) REFERENCES public.paises_clubes(id);


--
-- Name: estatisticas_clube estatisticas_clube_clube_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_clube
    ADD CONSTRAINT estatisticas_clube_clube_id_fkey FOREIGN KEY (clube_id) REFERENCES public.clubes(id) ON DELETE CASCADE;


--
-- Name: estatisticas_clube estatisticas_clube_competicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_clube
    ADD CONSTRAINT estatisticas_clube_competicao_id_fkey FOREIGN KEY (competicao_id) REFERENCES public.competicoes(id);


--
-- Name: estatisticas_jogador_competicao estatisticas_jogador_competicao_competicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_competicao
    ADD CONSTRAINT estatisticas_jogador_competicao_competicao_id_fkey FOREIGN KEY (competicao_id) REFERENCES public.competicoes(id);


--
-- Name: estatisticas_jogador_competicao estatisticas_jogador_competicao_jogador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_competicao
    ADD CONSTRAINT estatisticas_jogador_competicao_jogador_id_fkey FOREIGN KEY (jogador_id) REFERENCES public.jogadores(id) ON DELETE CASCADE;


--
-- Name: estatisticas_jogador_geral estatisticas_jogador_geral_jogador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_jogador_geral
    ADD CONSTRAINT estatisticas_jogador_geral_jogador_id_fkey FOREIGN KEY (jogador_id) REFERENCES public.jogadores(id) ON DELETE CASCADE;


--
-- Name: estatisticas_partidas estatisticas_partidas_partida_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.estatisticas_partidas
    ADD CONSTRAINT estatisticas_partidas_partida_id_fkey FOREIGN KEY (partida_id) REFERENCES public.partidas(id) ON DELETE CASCADE;


--
-- Name: jogadores jogadores_clube_atual_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.jogadores
    ADD CONSTRAINT jogadores_clube_atual_id_fkey FOREIGN KEY (clube_atual_id) REFERENCES public.clubes(id);


--
-- Name: jogadores jogadores_pais_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.jogadores
    ADD CONSTRAINT jogadores_pais_id_fkey FOREIGN KEY (pais_id) REFERENCES public.paises_jogadores(id);


--
-- Name: links_para_coleta links_para_coleta_competicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.links_para_coleta
    ADD CONSTRAINT links_para_coleta_competicao_id_fkey FOREIGN KEY (competicao_id) REFERENCES public.competicoes(id) ON DELETE CASCADE;


--
-- Name: partidas partidas_clube_casa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_clube_casa_id_fkey FOREIGN KEY (clube_casa_id) REFERENCES public.clubes(id);


--
-- Name: partidas partidas_clube_visitante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_clube_visitante_id_fkey FOREIGN KEY (clube_visitante_id) REFERENCES public.clubes(id);


--
-- Name: partidas partidas_competicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_competicao_id_fkey FOREIGN KEY (competicao_id) REFERENCES public.competicoes(id);


--
-- Name: records_vs_opponents records_vs_opponents_clube_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.records_vs_opponents
    ADD CONSTRAINT records_vs_opponents_clube_id_fkey FOREIGN KEY (clube_id) REFERENCES public.clubes(id) ON DELETE CASCADE;


--
-- Name: records_vs_opponents records_vs_opponents_oponente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: apostapro_user
--

ALTER TABLE ONLY public.records_vs_opponents
    ADD CONSTRAINT records_vs_opponents_oponente_id_fkey FOREIGN KEY (oponente_id) REFERENCES public.clubes(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO apostapro_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO apostapro_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO apostapro_user;


--
-- PostgreSQL database dump complete
--

