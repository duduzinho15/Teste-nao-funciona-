--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-08-10 21:27:12

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

--
-- TOC entry 2 (class 3079 OID 33622)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 4970 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 33654)
-- Name: clubes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clubes (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    abreviacao character varying(20),
    pais_id integer,
    cidade character varying(100),
    fundacao date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.clubes OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 33653)
-- Name: clubes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clubes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clubes_id_seq OWNER TO postgres;

--
-- TOC entry 4982 (class 0 OID 0)
-- Dependencies: 222
-- Name: clubes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clubes_id_seq OWNED BY public.clubes.id;


--
-- TOC entry 221 (class 1259 OID 33645)
-- Name: competicoes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competicoes (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    nome_curto character varying(50),
    tipo character varying(50),
    pais character varying(100),
    nivel character varying(10),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.competicoes OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 33644)
-- Name: competicoes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.competicoes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competicoes_id_seq OWNER TO postgres;

--
-- TOC entry 4985 (class 0 OID 0)
-- Dependencies: 220
-- Name: competicoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.competicoes_id_seq OWNED BY public.competicoes.id;


--
-- TOC entry 225 (class 1259 OID 33670)
-- Name: estadios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estadios (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    apelido character varying(100),
    cidade character varying(100),
    capacidade integer,
    inauguracao date,
    gramado character varying(50),
    clube_id integer,
    pais_id integer,
    ativo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.estadios OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 33669)
-- Name: estadios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estadios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estadios_id_seq OWNER TO postgres;

--
-- TOC entry 4988 (class 0 OID 0)
-- Dependencies: 224
-- Name: estadios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estadios_id_seq OWNED BY public.estadios.id;


--
-- TOC entry 219 (class 1259 OID 33634)
-- Name: paises_clubes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.paises_clubes (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    codigo_iso character(3),
    continente character varying(50),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.paises_clubes OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 33633)
-- Name: paises_clubes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.paises_clubes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paises_clubes_id_seq OWNER TO postgres;

--
-- TOC entry 4991 (class 0 OID 0)
-- Dependencies: 218
-- Name: paises_clubes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.paises_clubes_id_seq OWNED BY public.paises_clubes.id;


--
-- TOC entry 227 (class 1259 OID 33692)
-- Name: partidas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.partidas (
    id integer NOT NULL,
    competicao_id integer,
    clube_casa_id integer,
    clube_visitante_id integer,
    data_partida timestamp with time zone,
    rodada character varying(50),
    temporada character varying(20),
    gols_casa integer,
    gols_visitante integer,
    status character varying(50),
    estadio_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.partidas OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 33691)
-- Name: partidas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.partidas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partidas_id_seq OWNER TO postgres;

--
-- TOC entry 4994 (class 0 OID 0)
-- Dependencies: 226
-- Name: partidas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.partidas_id_seq OWNED BY public.partidas.id;


--
-- TOC entry 4779 (class 2604 OID 33657)
-- Name: clubes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clubes ALTER COLUMN id SET DEFAULT nextval('public.clubes_id_seq'::regclass);


--
-- TOC entry 4776 (class 2604 OID 33648)
-- Name: competicoes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competicoes ALTER COLUMN id SET DEFAULT nextval('public.competicoes_id_seq'::regclass);


--
-- TOC entry 4782 (class 2604 OID 33673)
-- Name: estadios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estadios ALTER COLUMN id SET DEFAULT nextval('public.estadios_id_seq'::regclass);


--
-- TOC entry 4773 (class 2604 OID 33637)
-- Name: paises_clubes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paises_clubes ALTER COLUMN id SET DEFAULT nextval('public.paises_clubes_id_seq'::regclass);


--
-- TOC entry 4786 (class 2604 OID 33695)
-- Name: partidas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas ALTER COLUMN id SET DEFAULT nextval('public.partidas_id_seq'::regclass);


--
-- TOC entry 4960 (class 0 OID 33654)
-- Dependencies: 223
-- Data for Name: clubes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clubes (id, nome, abreviacao, pais_id, cidade, fundacao, created_at, updated_at) FROM stdin;
1	Flamengo	FLA	1	Rio de Janeiro	1895-11-15	2025-08-10 17:25:43.21138-03	2025-08-10 17:25:43.21138-03
2	Barcelona	BAR	2	Barcelona	1899-11-29	2025-08-10 17:25:43.21138-03	2025-08-10 17:25:43.21138-03
3	Real Madrid	RMA	2	Madrid	1902-03-06	2025-08-10 17:25:43.21138-03	2025-08-10 17:25:43.21138-03
\.


--
-- TOC entry 4958 (class 0 OID 33645)
-- Dependencies: 221
-- Data for Name: competicoes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competicoes (id, nome, nome_curto, tipo, pais, nivel, created_at, updated_at) FROM stdin;
1	Campeonato Brasileiro SÃ©rie A	BrasileirÃ£o	Liga	Brasil	A	2025-08-10 17:25:43.210001-03	2025-08-10 17:25:43.210001-03
2	La Liga	LaLiga	Liga	Espanha	A	2025-08-10 17:25:43.210001-03	2025-08-10 17:25:43.210001-03
\.


--
-- TOC entry 4962 (class 0 OID 33670)
-- Dependencies: 225
-- Data for Name: estadios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estadios (id, nome, apelido, cidade, capacidade, inauguracao, gramado, clube_id, pais_id, ativo, created_at, updated_at) FROM stdin;
1	MaracanÃ£	Maraca	Rio de Janeiro	78838	1950-06-16	Natural	1	1	t	2025-08-10 17:25:43.213694-03	2025-08-10 17:25:43.213694-03
2	Camp Nou	Camp Nou	Barcelona	99354	1957-09-24	Natural	2	2	t	2025-08-10 17:25:43.213694-03	2025-08-10 17:25:43.213694-03
3	Santiago BernabÃ©u	BernabÃ©u	Madrid	81044	1947-12-14	HÃ­brido	3	2	t	2025-08-10 17:25:43.213694-03	2025-08-10 17:25:43.213694-03
\.


--
-- TOC entry 4956 (class 0 OID 33634)
-- Dependencies: 219
-- Data for Name: paises_clubes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.paises_clubes (id, nome, codigo_iso, continente, created_at, updated_at) FROM stdin;
1	Brasil	BRA	AmÃ©rica do Sul	2025-08-10 17:25:43.20703-03	2025-08-10 17:25:43.20703-03
2	Espanha	ESP	Europa	2025-08-10 17:25:43.20703-03	2025-08-10 17:25:43.20703-03
3	Inglaterra	ENG	Europa	2025-08-10 17:25:43.20703-03	2025-08-10 17:25:43.20703-03
\.


--
-- TOC entry 4964 (class 0 OID 33692)
-- Dependencies: 227
-- Data for Name: partidas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.partidas (id, competicao_id, clube_casa_id, clube_visitante_id, data_partida, rodada, temporada, gols_casa, gols_visitante, status, estadio_id, created_at, updated_at) FROM stdin;
1	1	1	2	2025-08-03 00:00:00-03	1Âª Rodada	2024	2	1	Finalizada	1	2025-08-10 17:25:43.215453-03	2025-08-10 17:25:43.215453-03
2	2	2	3	2025-08-05 00:00:00-03	Jogo 10	2023/2024	1	1	Finalizada	2	2025-08-10 17:25:43.215453-03	2025-08-10 17:25:43.215453-03
3	1	1	3	2025-08-13 00:00:00-03	2Âª Rodada	2024	\N	\N	Agendada	1	2025-08-10 17:25:43.215453-03	2025-08-10 17:25:43.215453-03
\.


--
-- TOC entry 4996 (class 0 OID 0)
-- Dependencies: 222
-- Name: clubes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clubes_id_seq', 1, false);


--
-- TOC entry 4997 (class 0 OID 0)
-- Dependencies: 220
-- Name: competicoes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.competicoes_id_seq', 1, false);


--
-- TOC entry 4998 (class 0 OID 0)
-- Dependencies: 224
-- Name: estadios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estadios_id_seq', 1, false);


--
-- TOC entry 4999 (class 0 OID 0)
-- Dependencies: 218
-- Name: paises_clubes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.paises_clubes_id_seq', 1, false);


--
-- TOC entry 5000 (class 0 OID 0)
-- Dependencies: 226
-- Name: partidas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.partidas_id_seq', 1, false);


--
-- TOC entry 4796 (class 2606 OID 33661)
-- Name: clubes clubes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clubes
    ADD CONSTRAINT clubes_pkey PRIMARY KEY (id);


--
-- TOC entry 4794 (class 2606 OID 33652)
-- Name: competicoes competicoes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competicoes
    ADD CONSTRAINT competicoes_pkey PRIMARY KEY (id);


--
-- TOC entry 4800 (class 2606 OID 33680)
-- Name: estadios estadios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estadios
    ADD CONSTRAINT estadios_pkey PRIMARY KEY (id);


--
-- TOC entry 4790 (class 2606 OID 33643)
-- Name: paises_clubes paises_clubes_codigo_iso_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paises_clubes
    ADD CONSTRAINT paises_clubes_codigo_iso_key UNIQUE (codigo_iso);


--
-- TOC entry 4792 (class 2606 OID 33641)
-- Name: paises_clubes paises_clubes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paises_clubes
    ADD CONSTRAINT paises_clubes_pkey PRIMARY KEY (id);


--
-- TOC entry 4802 (class 2606 OID 33699)
-- Name: partidas partidas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_pkey PRIMARY KEY (id);


--
-- TOC entry 4798 (class 2606 OID 33663)
-- Name: clubes uq_clube_nome; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clubes
    ADD CONSTRAINT uq_clube_nome UNIQUE (nome);


--
-- TOC entry 4803 (class 2606 OID 33664)
-- Name: clubes clubes_pais_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clubes
    ADD CONSTRAINT clubes_pais_id_fkey FOREIGN KEY (pais_id) REFERENCES public.paises_clubes(id) ON DELETE SET NULL;


--
-- TOC entry 4804 (class 2606 OID 33681)
-- Name: estadios estadios_clube_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estadios
    ADD CONSTRAINT estadios_clube_id_fkey FOREIGN KEY (clube_id) REFERENCES public.clubes(id) ON DELETE SET NULL;


--
-- TOC entry 4805 (class 2606 OID 33686)
-- Name: estadios estadios_pais_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estadios
    ADD CONSTRAINT estadios_pais_id_fkey FOREIGN KEY (pais_id) REFERENCES public.paises_clubes(id) ON DELETE SET NULL;


--
-- TOC entry 4806 (class 2606 OID 33705)
-- Name: partidas partidas_clube_casa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_clube_casa_id_fkey FOREIGN KEY (clube_casa_id) REFERENCES public.clubes(id) ON DELETE SET NULL;


--
-- TOC entry 4807 (class 2606 OID 33710)
-- Name: partidas partidas_clube_visitante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_clube_visitante_id_fkey FOREIGN KEY (clube_visitante_id) REFERENCES public.clubes(id) ON DELETE SET NULL;


--
-- TOC entry 4808 (class 2606 OID 33700)
-- Name: partidas partidas_competicao_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_competicao_id_fkey FOREIGN KEY (competicao_id) REFERENCES public.competicoes(id) ON DELETE SET NULL;


--
-- TOC entry 4809 (class 2606 OID 33715)
-- Name: partidas partidas_estadio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.partidas
    ADD CONSTRAINT partidas_estadio_id_fkey FOREIGN KEY (estadio_id) REFERENCES public.estadios(id) ON DELETE SET NULL;


--
-- TOC entry 4971 (class 0 OID 0)
-- Dependencies: 233
-- Name: FUNCTION uuid_generate_v1(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1() TO apostapro_user;


--
-- TOC entry 4972 (class 0 OID 0)
-- Dependencies: 234
-- Name: FUNCTION uuid_generate_v1mc(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v1mc() TO apostapro_user;


--
-- TOC entry 4973 (class 0 OID 0)
-- Dependencies: 235
-- Name: FUNCTION uuid_generate_v3(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v3(namespace uuid, name text) TO apostapro_user;


--
-- TOC entry 4974 (class 0 OID 0)
-- Dependencies: 236
-- Name: FUNCTION uuid_generate_v4(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v4() TO apostapro_user;


--
-- TOC entry 4975 (class 0 OID 0)
-- Dependencies: 237
-- Name: FUNCTION uuid_generate_v5(namespace uuid, name text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_generate_v5(namespace uuid, name text) TO apostapro_user;


--
-- TOC entry 4976 (class 0 OID 0)
-- Dependencies: 228
-- Name: FUNCTION uuid_nil(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_nil() TO apostapro_user;


--
-- TOC entry 4977 (class 0 OID 0)
-- Dependencies: 229
-- Name: FUNCTION uuid_ns_dns(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_dns() TO apostapro_user;


--
-- TOC entry 4978 (class 0 OID 0)
-- Dependencies: 231
-- Name: FUNCTION uuid_ns_oid(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_oid() TO apostapro_user;


--
-- TOC entry 4979 (class 0 OID 0)
-- Dependencies: 230
-- Name: FUNCTION uuid_ns_url(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_url() TO apostapro_user;


--
-- TOC entry 4980 (class 0 OID 0)
-- Dependencies: 232
-- Name: FUNCTION uuid_ns_x500(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.uuid_ns_x500() TO apostapro_user;


--
-- TOC entry 4981 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE clubes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clubes TO apostapro_user;


--
-- TOC entry 4983 (class 0 OID 0)
-- Dependencies: 222
-- Name: SEQUENCE clubes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clubes_id_seq TO apostapro_user;


--
-- TOC entry 4984 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE competicoes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.competicoes TO apostapro_user;


--
-- TOC entry 4986 (class 0 OID 0)
-- Dependencies: 220
-- Name: SEQUENCE competicoes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.competicoes_id_seq TO apostapro_user;


--
-- TOC entry 4987 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE estadios; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.estadios TO apostapro_user;


--
-- TOC entry 4989 (class 0 OID 0)
-- Dependencies: 224
-- Name: SEQUENCE estadios_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.estadios_id_seq TO apostapro_user;


--
-- TOC entry 4990 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE paises_clubes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.paises_clubes TO apostapro_user;


--
-- TOC entry 4992 (class 0 OID 0)
-- Dependencies: 218
-- Name: SEQUENCE paises_clubes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.paises_clubes_id_seq TO apostapro_user;


--
-- TOC entry 4993 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE partidas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.partidas TO apostapro_user;


--
-- TOC entry 4995 (class 0 OID 0)
-- Dependencies: 226
-- Name: SEQUENCE partidas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.partidas_id_seq TO apostapro_user;


-- Completed on 2025-08-10 21:27:13

--
-- PostgreSQL database dump complete
--

