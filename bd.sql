--
-- PostgreSQL database dump
--

\restrict djO9fScVpb4Q9T02j71OKDBIIrX5eKfZ4LxtNiAtPPyc6IifkC2s974qM9uEGdc

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

-- Started on 2026-05-25 17:30:55 -04

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

--
-- TOC entry 905 (class 1247 OID 16530)
-- Name: estado_vacacion; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.estado_vacacion AS ENUM (
    'PENDIENTE',
    'APROBADA',
    'RECHAZADA'
);


ALTER TYPE public.estado_vacacion OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 236 (class 1259 OID 16506)
-- Name: asignacionguardia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asignacionguardia (
    id integer NOT NULL,
    trabajador_id integer,
    guardia_id integer,
    cronograma_id integer,
    fecha date NOT NULL,
    observaciones text
);


ALTER TABLE public.asignacionguardia OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16505)
-- Name: asignacionguardia_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asignacionguardia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asignacionguardia_id_seq OWNER TO postgres;

--
-- TOC entry 3590 (class 0 OID 0)
-- Dependencies: 235
-- Name: asignacionguardia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asignacionguardia_id_seq OWNED BY public.asignacionguardia.id;


--
-- TOC entry 216 (class 1259 OID 16390)
-- Name: cargo; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cargo (
    id integer NOT NULL,
    nombre_cargo character varying(100) NOT NULL,
    descripcion text
);


ALTER TABLE public.cargo OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16389)
-- Name: cargo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cargo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cargo_id_seq OWNER TO postgres;

--
-- TOC entry 3591 (class 0 OID 0)
-- Dependencies: 215
-- Name: cargo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cargo_id_seq OWNED BY public.cargo.id;


--
-- TOC entry 221 (class 1259 OID 16416)
-- Name: configuracionglobal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracionglobal (
    clave character varying(100) NOT NULL,
    valor numeric(12,2),
    ultima_actualizacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.configuracionglobal OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16492)
-- Name: cronograma; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cronograma (
    id integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL
);


ALTER TABLE public.cronograma OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16491)
-- Name: cronograma_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cronograma_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cronograma_id_seq OWNER TO postgres;

--
-- TOC entry 3592 (class 0 OID 0)
-- Dependencies: 231
-- Name: cronograma_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cronograma_id_seq OWNED BY public.cronograma.id;


--
-- TOC entry 230 (class 1259 OID 16482)
-- Name: gerenteguardias; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gerenteguardias (
    id integer NOT NULL,
    cedula character varying(20) NOT NULL,
    nombres character varying(100) NOT NULL,
    activo boolean DEFAULT true
);


ALTER TABLE public.gerenteguardias OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16481)
-- Name: gerenteguardias_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.gerenteguardias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gerenteguardias_id_seq OWNER TO postgres;

--
-- TOC entry 3593 (class 0 OID 0)
-- Dependencies: 229
-- Name: gerenteguardias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.gerenteguardias_id_seq OWNED BY public.gerenteguardias.id;


--
-- TOC entry 234 (class 1259 OID 16499)
-- Name: guardia; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guardia (
    id integer NOT NULL,
    nombre_turno character varying(50) NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL
);


ALTER TABLE public.guardia OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16498)
-- Name: guardia_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.guardia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.guardia_id_seq OWNER TO postgres;

--
-- TOC entry 3594 (class 0 OID 0)
-- Dependencies: 233
-- Name: guardia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.guardia_id_seq OWNED BY public.guardia.id;


--
-- TOC entry 242 (class 1259 OID 16569)
-- Name: logauditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.logauditoria (
    id integer NOT NULL,
    usuario_id integer,
    accion character varying(100),
    tabla_afectada character varying(100),
    id_registro integer,
    valor_anterior text,
    valor_nuevo text,
    fecha_hora timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip character varying(45)
);


ALTER TABLE public.logauditoria OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16568)
-- Name: logauditoria_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.logauditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.logauditoria_id_seq OWNER TO postgres;

--
-- TOC entry 3595 (class 0 OID 0)
-- Dependencies: 241
-- Name: logauditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.logauditoria_id_seq OWNED BY public.logauditoria.id;


--
-- TOC entry 220 (class 1259 OID 16408)
-- Name: permiso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permiso (
    id integer NOT NULL,
    nombre_permiso character varying(100) NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.permiso OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16407)
-- Name: permiso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permiso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permiso_id_seq OWNER TO postgres;

--
-- TOC entry 3596 (class 0 OID 0)
-- Dependencies: 219
-- Name: permiso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permiso_id_seq OWNED BY public.permiso.id;


--
-- TOC entry 244 (class 1259 OID 16584)
-- Name: respaldosistema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.respaldosistema (
    id integer NOT NULL,
    super_admin_id integer,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.respaldosistema OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 16583)
-- Name: respaldosistema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.respaldosistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.respaldosistema_id_seq OWNER TO postgres;

--
-- TOC entry 3597 (class 0 OID 0)
-- Dependencies: 243
-- Name: respaldosistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.respaldosistema_id_seq OWNED BY public.respaldosistema.id;


--
-- TOC entry 218 (class 1259 OID 16399)
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id integer NOT NULL,
    nombre_rol character varying(50) NOT NULL,
    descripcion text
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16398)
-- Name: rol_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rol_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rol_id_seq OWNER TO postgres;

--
-- TOC entry 3598 (class 0 OID 0)
-- Dependencies: 217
-- Name: rol_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rol_id_seq OWNED BY public.rol.id;


--
-- TOC entry 226 (class 1259 OID 16451)
-- Name: rolpermiso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rolpermiso (
    rol_id integer NOT NULL,
    permiso_id integer NOT NULL
);


ALTER TABLE public.rolpermiso OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16557)
-- Name: superadministrador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.superadministrador (
    id integer NOT NULL,
    usuario_id integer,
    rol_especial character varying(50)
);


ALTER TABLE public.superadministrador OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16556)
-- Name: superadministrador_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.superadministrador_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.superadministrador_id_seq OWNER TO postgres;

--
-- TOC entry 3599 (class 0 OID 0)
-- Dependencies: 239
-- Name: superadministrador_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.superadministrador_id_seq OWNED BY public.superadministrador.id;


--
-- TOC entry 228 (class 1259 OID 16467)
-- Name: trabajador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trabajador (
    id integer NOT NULL,
    cedula character varying(20) NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    fecha_ingreso date NOT NULL,
    estatus character varying(20) DEFAULT 'Activo'::character varying,
    cargo_id integer
);


ALTER TABLE public.trabajador OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16466)
-- Name: trabajador_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trabajador_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trabajador_id_seq OWNER TO postgres;

--
-- TOC entry 3600 (class 0 OID 0)
-- Dependencies: 227
-- Name: trabajador_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trabajador_id_seq OWNED BY public.trabajador.id;


--
-- TOC entry 223 (class 1259 OID 16423)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    email character varying(100) NOT NULL,
    is_active boolean DEFAULT true,
    last_login timestamp without time zone
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16422)
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- TOC entry 3601 (class 0 OID 0)
-- Dependencies: 222
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- TOC entry 225 (class 1259 OID 16435)
-- Name: usuariorol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuariorol (
    id integer NOT NULL,
    usuario_id integer,
    rol_id integer
);


ALTER TABLE public.usuariorol OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16434)
-- Name: usuariorol_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuariorol_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuariorol_id_seq OWNER TO postgres;

--
-- TOC entry 3602 (class 0 OID 0)
-- Dependencies: 224
-- Name: usuariorol_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuariorol_id_seq OWNED BY public.usuariorol.id;


--
-- TOC entry 238 (class 1259 OID 16538)
-- Name: vacacionsolicitud; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vacacionsolicitud (
    id integer NOT NULL,
    trabajador_id integer,
    gerente_id integer,
    fecha_solicitud date DEFAULT CURRENT_DATE,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    dias_solicitados integer,
    estado public.estado_vacacion DEFAULT 'PENDIENTE'::public.estado_vacacion
);


ALTER TABLE public.vacacionsolicitud OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16537)
-- Name: vacacionsolicitud_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vacacionsolicitud_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vacacionsolicitud_id_seq OWNER TO postgres;

--
-- TOC entry 3603 (class 0 OID 0)
-- Dependencies: 237
-- Name: vacacionsolicitud_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vacacionsolicitud_id_seq OWNED BY public.vacacionsolicitud.id;


--
-- TOC entry 3378 (class 2604 OID 16509)
-- Name: asignacionguardia id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignacionguardia ALTER COLUMN id SET DEFAULT nextval('public.asignacionguardia_id_seq'::regclass);


--
-- TOC entry 3365 (class 2604 OID 16393)
-- Name: cargo id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cargo ALTER COLUMN id SET DEFAULT nextval('public.cargo_id_seq'::regclass);


--
-- TOC entry 3376 (class 2604 OID 16495)
-- Name: cronograma id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cronograma ALTER COLUMN id SET DEFAULT nextval('public.cronograma_id_seq'::regclass);


--
-- TOC entry 3374 (class 2604 OID 16485)
-- Name: gerenteguardias id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gerenteguardias ALTER COLUMN id SET DEFAULT nextval('public.gerenteguardias_id_seq'::regclass);


--
-- TOC entry 3377 (class 2604 OID 16502)
-- Name: guardia id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guardia ALTER COLUMN id SET DEFAULT nextval('public.guardia_id_seq'::regclass);


--
-- TOC entry 3383 (class 2604 OID 16572)
-- Name: logauditoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logauditoria ALTER COLUMN id SET DEFAULT nextval('public.logauditoria_id_seq'::regclass);


--
-- TOC entry 3367 (class 2604 OID 16411)
-- Name: permiso id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso ALTER COLUMN id SET DEFAULT nextval('public.permiso_id_seq'::regclass);


--
-- TOC entry 3385 (class 2604 OID 16587)
-- Name: respaldosistema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.respaldosistema ALTER COLUMN id SET DEFAULT nextval('public.respaldosistema_id_seq'::regclass);


--
-- TOC entry 3366 (class 2604 OID 16402)
-- Name: rol id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol ALTER COLUMN id SET DEFAULT nextval('public.rol_id_seq'::regclass);


--
-- TOC entry 3382 (class 2604 OID 16560)
-- Name: superadministrador id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.superadministrador ALTER COLUMN id SET DEFAULT nextval('public.superadministrador_id_seq'::regclass);


--
-- TOC entry 3372 (class 2604 OID 16470)
-- Name: trabajador id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trabajador ALTER COLUMN id SET DEFAULT nextval('public.trabajador_id_seq'::regclass);


--
-- TOC entry 3369 (class 2604 OID 16426)
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- TOC entry 3371 (class 2604 OID 16438)
-- Name: usuariorol id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuariorol ALTER COLUMN id SET DEFAULT nextval('public.usuariorol_id_seq'::regclass);


--
-- TOC entry 3379 (class 2604 OID 16541)
-- Name: vacacionsolicitud id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacacionsolicitud ALTER COLUMN id SET DEFAULT nextval('public.vacacionsolicitud_id_seq'::regclass);


--
-- TOC entry 3420 (class 2606 OID 16513)
-- Name: asignacionguardia asignacionguardia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignacionguardia
    ADD CONSTRAINT asignacionguardia_pkey PRIMARY KEY (id);


--
-- TOC entry 3388 (class 2606 OID 16397)
-- Name: cargo cargo_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cargo
    ADD CONSTRAINT cargo_pkey PRIMARY KEY (id);


--
-- TOC entry 3396 (class 2606 OID 16421)
-- Name: configuracionglobal configuracionglobal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracionglobal
    ADD CONSTRAINT configuracionglobal_pkey PRIMARY KEY (clave);


--
-- TOC entry 3416 (class 2606 OID 16497)
-- Name: cronograma cronograma_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cronograma
    ADD CONSTRAINT cronograma_pkey PRIMARY KEY (id);


--
-- TOC entry 3412 (class 2606 OID 16490)
-- Name: gerenteguardias gerenteguardias_cedula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gerenteguardias
    ADD CONSTRAINT gerenteguardias_cedula_key UNIQUE (cedula);


--
-- TOC entry 3414 (class 2606 OID 16488)
-- Name: gerenteguardias gerenteguardias_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gerenteguardias
    ADD CONSTRAINT gerenteguardias_pkey PRIMARY KEY (id);


--
-- TOC entry 3418 (class 2606 OID 16504)
-- Name: guardia guardia_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guardia
    ADD CONSTRAINT guardia_pkey PRIMARY KEY (id);


--
-- TOC entry 3426 (class 2606 OID 16577)
-- Name: logauditoria logauditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logauditoria
    ADD CONSTRAINT logauditoria_pkey PRIMARY KEY (id);


--
-- TOC entry 3392 (class 2606 OID 16415)
-- Name: permiso permiso_codename_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_codename_key UNIQUE (codename);


--
-- TOC entry 3394 (class 2606 OID 16413)
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id);


--
-- TOC entry 3428 (class 2606 OID 16590)
-- Name: respaldosistema respaldosistema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.respaldosistema
    ADD CONSTRAINT respaldosistema_pkey PRIMARY KEY (id);


--
-- TOC entry 3390 (class 2606 OID 16406)
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id);


--
-- TOC entry 3406 (class 2606 OID 16455)
-- Name: rolpermiso rolpermiso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolpermiso
    ADD CONSTRAINT rolpermiso_pkey PRIMARY KEY (rol_id, permiso_id);


--
-- TOC entry 3424 (class 2606 OID 16562)
-- Name: superadministrador superadministrador_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.superadministrador
    ADD CONSTRAINT superadministrador_pkey PRIMARY KEY (id);


--
-- TOC entry 3408 (class 2606 OID 16475)
-- Name: trabajador trabajador_cedula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trabajador
    ADD CONSTRAINT trabajador_cedula_key UNIQUE (cedula);


--
-- TOC entry 3410 (class 2606 OID 16473)
-- Name: trabajador trabajador_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trabajador
    ADD CONSTRAINT trabajador_pkey PRIMARY KEY (id);


--
-- TOC entry 3398 (class 2606 OID 16433)
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- TOC entry 3400 (class 2606 OID 16429)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 3402 (class 2606 OID 16431)
-- Name: usuario usuario_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_username_key UNIQUE (username);


--
-- TOC entry 3404 (class 2606 OID 16440)
-- Name: usuariorol usuariorol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuariorol
    ADD CONSTRAINT usuariorol_pkey PRIMARY KEY (id);


--
-- TOC entry 3422 (class 2606 OID 16545)
-- Name: vacacionsolicitud vacacionsolicitud_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacacionsolicitud
    ADD CONSTRAINT vacacionsolicitud_pkey PRIMARY KEY (id);


--
-- TOC entry 3434 (class 2606 OID 16524)
-- Name: asignacionguardia asignacionguardia_cronograma_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignacionguardia
    ADD CONSTRAINT asignacionguardia_cronograma_id_fkey FOREIGN KEY (cronograma_id) REFERENCES public.cronograma(id);


--
-- TOC entry 3435 (class 2606 OID 16519)
-- Name: asignacionguardia asignacionguardia_guardia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignacionguardia
    ADD CONSTRAINT asignacionguardia_guardia_id_fkey FOREIGN KEY (guardia_id) REFERENCES public.guardia(id);


--
-- TOC entry 3436 (class 2606 OID 16514)
-- Name: asignacionguardia asignacionguardia_trabajador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignacionguardia
    ADD CONSTRAINT asignacionguardia_trabajador_id_fkey FOREIGN KEY (trabajador_id) REFERENCES public.trabajador(id);


--
-- TOC entry 3440 (class 2606 OID 16578)
-- Name: logauditoria logauditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.logauditoria
    ADD CONSTRAINT logauditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- TOC entry 3441 (class 2606 OID 16591)
-- Name: respaldosistema respaldosistema_super_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.respaldosistema
    ADD CONSTRAINT respaldosistema_super_admin_id_fkey FOREIGN KEY (super_admin_id) REFERENCES public.superadministrador(id);


--
-- TOC entry 3431 (class 2606 OID 16461)
-- Name: rolpermiso rolpermiso_permiso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolpermiso
    ADD CONSTRAINT rolpermiso_permiso_id_fkey FOREIGN KEY (permiso_id) REFERENCES public.permiso(id) ON DELETE CASCADE;


--
-- TOC entry 3432 (class 2606 OID 16456)
-- Name: rolpermiso rolpermiso_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolpermiso
    ADD CONSTRAINT rolpermiso_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.rol(id) ON DELETE CASCADE;


--
-- TOC entry 3439 (class 2606 OID 16563)
-- Name: superadministrador superadministrador_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.superadministrador
    ADD CONSTRAINT superadministrador_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- TOC entry 3433 (class 2606 OID 16476)
-- Name: trabajador trabajador_cargo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trabajador
    ADD CONSTRAINT trabajador_cargo_id_fkey FOREIGN KEY (cargo_id) REFERENCES public.cargo(id);


--
-- TOC entry 3429 (class 2606 OID 16446)
-- Name: usuariorol usuariorol_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuariorol
    ADD CONSTRAINT usuariorol_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.rol(id) ON DELETE CASCADE;


--
-- TOC entry 3430 (class 2606 OID 16441)
-- Name: usuariorol usuariorol_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuariorol
    ADD CONSTRAINT usuariorol_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE CASCADE;


--
-- TOC entry 3437 (class 2606 OID 16551)
-- Name: vacacionsolicitud vacacionsolicitud_gerente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacacionsolicitud
    ADD CONSTRAINT vacacionsolicitud_gerente_id_fkey FOREIGN KEY (gerente_id) REFERENCES public.gerenteguardias(id);


--
-- TOC entry 3438 (class 2606 OID 16546)
-- Name: vacacionsolicitud vacacionsolicitud_trabajador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacacionsolicitud
    ADD CONSTRAINT vacacionsolicitud_trabajador_id_fkey FOREIGN KEY (trabajador_id) REFERENCES public.trabajador(id);


-- Completed on 2026-05-25 17:30:56 -04

--
-- PostgreSQL database dump complete
--

\unrestrict djO9fScVpb4Q9T02j71OKDBIIrX5eKfZ4LxtNiAtPPyc6IifkC2s974qM9uEGdc

