--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13 (Debian 15.13-1.pgdg120+1)
-- Dumped by pg_dump version 15.13 (Debian 15.13-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: vitaladmin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO vitaladmin;

--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: vitaladmin
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(255),
    "timestamp" timestamp without time zone
);


ALTER TABLE public.audit_log OWNER TO vitaladmin;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: vitaladmin
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO vitaladmin;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vitaladmin
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: contact_bericht; Type: TABLE; Schema: public; Owner: vitaladmin
--

CREATE TABLE public.contact_bericht (
    id integer NOT NULL,
    naam character varying(100) NOT NULL,
    emailadres character varying(120) NOT NULL,
    onderwerp character varying(100) NOT NULL,
    telefoonnummer character varying(20),
    bericht text NOT NULL,
    verzonden_op timestamp without time zone
);


ALTER TABLE public.contact_bericht OWNER TO vitaladmin;

--
-- Name: contact_bericht_id_seq; Type: SEQUENCE; Schema: public; Owner: vitaladmin
--

CREATE SEQUENCE public.contact_bericht_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contact_bericht_id_seq OWNER TO vitaladmin;

--
-- Name: contact_bericht_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vitaladmin
--

ALTER SEQUENCE public.contact_bericht_id_seq OWNED BY public.contact_bericht.id;


--
-- Name: health_data; Type: TABLE; Schema: public; Owner: vitaladmin
--

CREATE TABLE public.health_data (
    id integer NOT NULL,
    user_id integer,
    date date NOT NULL,
    heart_rate integer,
    steps integer,
    sleep_hours double precision,
    stress_level character varying(10)
);


ALTER TABLE public.health_data OWNER TO vitaladmin;

--
-- Name: health_data_id_seq; Type: SEQUENCE; Schema: public; Owner: vitaladmin
--

CREATE SEQUENCE public.health_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.health_data_id_seq OWNER TO vitaladmin;

--
-- Name: health_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vitaladmin
--

ALTER SEQUENCE public.health_data_id_seq OWNED BY public.health_data.id;


--
-- Name: inlog_gegevens; Type: TABLE; Schema: public; Owner: vitaladmin
--

CREATE TABLE public.inlog_gegevens (
    id integer NOT NULL,
    email character varying(120) NOT NULL,
    voornaam character varying(100),
    achternaam character varying(100),
    telefoonnummer character varying(20),
    date_joined timestamp without time zone,
    role character varying(20),
    hashed_password character varying(200) NOT NULL
);


ALTER TABLE public.inlog_gegevens OWNER TO vitaladmin;

--
-- Name: inlog_gegevens_id_seq; Type: SEQUENCE; Schema: public; Owner: vitaladmin
--

CREATE SEQUENCE public.inlog_gegevens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inlog_gegevens_id_seq OWNER TO vitaladmin;

--
-- Name: inlog_gegevens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vitaladmin
--

ALTER SEQUENCE public.inlog_gegevens_id_seq OWNED BY public.inlog_gegevens.id;


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: contact_bericht id; Type: DEFAULT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.contact_bericht ALTER COLUMN id SET DEFAULT nextval('public.contact_bericht_id_seq'::regclass);


--
-- Name: health_data id; Type: DEFAULT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.health_data ALTER COLUMN id SET DEFAULT nextval('public.health_data_id_seq'::regclass);


--
-- Name: inlog_gegevens id; Type: DEFAULT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.inlog_gegevens ALTER COLUMN id SET DEFAULT nextval('public.inlog_gegevens_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: vitaladmin
--

COPY public.alembic_version (version_num) FROM stdin;
2b629c503aa7
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: vitaladmin
--

COPY public.audit_log (id, user_id, action, "timestamp") FROM stdin;
\.


--
-- Data for Name: contact_bericht; Type: TABLE DATA; Schema: public; Owner: vitaladmin
--

COPY public.contact_bericht (id, naam, emailadres, onderwerp, telefoonnummer, bericht, verzonden_op) FROM stdin;
1	Mathijs Adriaensen	mathijs.adriaensen1@gmail.com	Feedback	\N	rttrrt	2025-06-15 17:30:18.007893
2	Mathijs Adriaensen	mathijs.adriaensen1@gmail.com	Feedback	\N	xccxx	2025-06-15 17:53:08.494493
3	Mathijs Adriaensen	mathijs.adriaensen1@gmail.com	Vraag	\N	rtttr	2025-06-15 18:05:41.639282
4	jef datzzz	mathijs.adriaensen1@gmail.com	Feedback	\N	moiuhggtrretrz	2025-06-15 18:07:13.03901
\.


--
-- Data for Name: health_data; Type: TABLE DATA; Schema: public; Owner: vitaladmin
--

COPY public.health_data (id, user_id, date, heart_rate, steps, sleep_hours, stress_level) FROM stdin;
\.


--
-- Data for Name: inlog_gegevens; Type: TABLE DATA; Schema: public; Owner: vitaladmin
--

COPY public.inlog_gegevens (id, email, voornaam, achternaam, telefoonnummer, date_joined, role, hashed_password) FROM stdin;
1	mathijs.adriaensen1@gmail.com	\N	\N	\N	2025-06-15 19:20:27.987927	user	scrypt:32768:8:1$yjvGMNuSwNkjiq2D$d4d41f0f763fed7e0d33bb25331d140be75dc1a6776a7d260f416a8fed79618294278e6297b43f7c1a2bddd0dc8257b393187dc5652eb657bc09519958abbf6d
\.


--
-- Name: audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vitaladmin
--

SELECT pg_catalog.setval('public.audit_log_id_seq', 1, false);


--
-- Name: contact_bericht_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vitaladmin
--

SELECT pg_catalog.setval('public.contact_bericht_id_seq', 4, true);


--
-- Name: health_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vitaladmin
--

SELECT pg_catalog.setval('public.health_data_id_seq', 1, false);


--
-- Name: inlog_gegevens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vitaladmin
--

SELECT pg_catalog.setval('public.inlog_gegevens_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: contact_bericht contact_bericht_pkey; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.contact_bericht
    ADD CONSTRAINT contact_bericht_pkey PRIMARY KEY (id);


--
-- Name: health_data health_data_pkey; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.health_data
    ADD CONSTRAINT health_data_pkey PRIMARY KEY (id);


--
-- Name: inlog_gegevens inlog_gegevens_email_key; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.inlog_gegevens
    ADD CONSTRAINT inlog_gegevens_email_key UNIQUE (email);


--
-- Name: inlog_gegevens inlog_gegevens_pkey; Type: CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.inlog_gegevens
    ADD CONSTRAINT inlog_gegevens_pkey PRIMARY KEY (id);


--
-- Name: health_data health_data_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vitaladmin
--

ALTER TABLE ONLY public.health_data
    ADD CONSTRAINT health_data_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.inlog_gegevens(id);


--
-- PostgreSQL database dump complete
--

