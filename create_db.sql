-- Script para criar o banco de dados e as tabelas necessárias

-- Cria o banco de dados (execute como superusuário)
-- CREATE DATABASE apostapro
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'Portuguese_Brazil.1252'
--     LC_CTYPE = 'Portuguese_Brazil.1252'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1;

-- Conecta ao banco de dados
\c apostapro

-- Cria a tabela de países
CREATE TABLE IF NOT EXISTS public.paises_clubes
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nome character varying(100) COLLATE pg_catalog."default" NOT NULL,
    codigo_iso character(3) COLLATE pg_catalog."default",
    continente character varying(50) COLLATE pg_catalog."default",
    CONSTRAINT paises_clubes_pkey PRIMARY KEY (id),
    CONSTRAINT paises_clubes_nome_key UNIQUE (nome)
)
TABLESPACE pg_default;

-- Cria a tabela de clubes
CREATE TABLE IF NOT EXISTS public.clubes
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nome character varying(255) COLLATE pg_catalog."default" NOT NULL,
    pais_id integer,
    ativo boolean NOT NULL DEFAULT true,
    CONSTRAINT clubes_pkey PRIMARY KEY (id),
    CONSTRAINT fk_pais FOREIGN KEY (pais_id)
        REFERENCES public.paises_clubes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
)
TABLESPACE pg_default;

-- Cria a tabela de competições
CREATE TABLE IF NOT EXISTS public.competicoes
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    nome character varying(255) COLLATE pg_catalog."default" NOT NULL,
    url character varying(500) COLLATE pg_catalog."default",
    contexto character varying(100) COLLATE pg_catalog."default",
    pais character varying(100) COLLATE pg_catalog."default",
    tipo character varying(50) COLLATE pg_catalog."default",
    ativa boolean NOT NULL DEFAULT true,
    CONSTRAINT competicoes_pkey PRIMARY KEY (id)
)
TABLESPACE pg_default;

-- Cria a tabela de partidas
CREATE TABLE IF NOT EXISTS public.partidas
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    competicao_id integer NOT NULL,
    clube_casa_id integer NOT NULL,
    clube_visitante_id integer NOT NULL,
    data_partida date,
    rodada character varying(50) COLLATE pg_catalog."default",
    temporada character varying(20) COLLATE pg_catalog."default",
    gols_casa integer,
    gols_visitante integer,
    url_fbref character varying(500) COLLATE pg_catalog."default",
    status character varying(20) COLLATE pg_catalog."default" NOT NULL DEFAULT 'agendada'::character varying,
    CONSTRAINT partidas_pkey PRIMARY KEY (id),
    CONSTRAINT fk_clube_casa FOREIGN KEY (clube_casa_id)
        REFERENCES public.clubes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_clube_visitante FOREIGN KEY (clube_visitante_id)
        REFERENCES public.clubes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT fk_competicao FOREIGN KEY (competicao_id)
        REFERENCES public.competicoes (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
TABLESPACE pg_default;

-- Cria a tabela de estatísticas de partidas
CREATE TABLE IF NOT EXISTS public.estatisticas_partidas
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    partida_id integer NOT NULL,
    xg_casa double precision,
    xg_visitante double precision,
    formacao_casa character varying(20) COLLATE pg_catalog."default",
    formacao_visitante character varying(20) COLLATE pg_catalog."default",
    CONSTRAINT estatisticas_partidas_pkey PRIMARY KEY (id),
    CONSTRAINT fk_partida FOREIGN KEY (partida_id)
        REFERENCES public.partidas (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
TABLESPACE pg_default;

-- Cria índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_clubes_nome
    ON public.clubes USING btree
    (nome COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_partidas_data
    ON public.partidas USING btree
    (data_partida ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_partidas_status
    ON public.partidas USING btree
    (status COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Permissões
ALTER TABLE public.paises_clubes OWNER to postgres;
GRANT ALL ON TABLE public.paises_clubes TO postgres;

ALTER TABLE public.clubes OWNER to postgres;
GRANT ALL ON TABLE public.clubes TO postgres;

ALTER TABLE public.competicoes OWNER to postgres;
GRANT ALL ON TABLE public.competicoes TO postgres;

ALTER TABLE public.partidas OWNER to postgres;
GRANT ALL ON TABLE public.partidas TO postgres;

ALTER TABLE public.estatisticas_partidas OWNER to postgres;
GRANT ALL ON TABLE public.estatisticas_partidas TO postgres;
