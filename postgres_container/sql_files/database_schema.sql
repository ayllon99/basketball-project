--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2 (Debian 17.2-1.pgdg120+1)
-- Dumped by pg_dump version 17.0

-- Started on 2025-01-19 18:30:09 UTC

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
-- TOC entry 239 (class 1255 OID 25589)
-- Name: check_and_insert_away_team_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_and_insert_away_team_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM teams WHERE team_id = NEW.away_team_id) THEN
        INSERT INTO teams (team_id) VALUES (NEW.away_team_id);
    END IF;
    RETURN NEW;
END;
$$;


--
-- TOC entry 240 (class 1255 OID 25591)
-- Name: check_and_insert_home_team_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_and_insert_home_team_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM teams WHERE team_id = NEW.home_team_id) THEN
        INSERT INTO teams (team_id) VALUES (NEW.home_team_id);
    END IF;
    RETURN NEW;
END;
$$;


--
-- TOC entry 241 (class 1255 OID 25593)
-- Name: check_and_insert_player_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_and_insert_player_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM players_info WHERE player_id = NEW.player_id) THEN
        INSERT INTO players_info (player_id,player_link) VALUES (NEW.player_id,NEW.player_link);
    END IF;
    RETURN NEW;
END;
$$;


--
-- TOC entry 238 (class 1255 OID 25587)
-- Name: check_and_insert_stage_id(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_and_insert_stage_id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM results WHERE stage_id = NEW.stage_id) THEN
        INSERT INTO stages (stage_id) VALUES (NEW.stage_id);
    END IF;
    RETURN NEW;
END;
$$;


--
-- TOC entry 253 (class 1255 OID 26246)
-- Name: shootings_insert_function(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.shootings_insert_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.shoot_from := 
    CASE 
        WHEN NEW.shooting_type = 'Zone' THEN 'Zone'
        WHEN NEW.shooting_type = 'Middle' AND NEW.top_top > 10 AND NEW.top_top < 38 AND NEW.left_left < 10 THEN 'Left Corner Middle'
        WHEN NEW.shooting_type = 'Middle' AND NEW.top_top > 62 AND NEW.top_top < 90 AND NEW.left_left < 10 THEN 'Right Corner Middle'
        WHEN NEW.shooting_type = 'Middle' AND NEW.top_top > 38 AND NEW.top_top < 62 THEN 'Front Middle'
        WHEN NEW.shooting_type = 'Middle' AND NEW.top_top < 50 THEN 'Left Side Middle'
        WHEN NEW.shooting_type = 'Middle' AND NEW.top_top > 50 THEN 'Right Side Middle'
        WHEN NEW.shooting_type = 'Three' AND NEW.top_top > 90 AND NEW.left_left < 10 THEN 'Right Corner Three'
        WHEN NEW.shooting_type = 'Three' AND NEW.top_top < 10 AND NEW.left_left > 90 THEN 'Left Corner Three'
        WHEN NEW.shooting_type = 'Three' AND NEW.top_top > 38 AND NEW.top_top < 62 THEN 'Front Three'
        WHEN NEW.shooting_type = 'Three' AND NEW.top_top < 50 THEN 'Left Side Three'
        WHEN NEW.shooting_type = 'Three' AND NEW.top_top > 50 THEN 'Right Side Three'
    END;
    
    NEW.season := 
    CASE 
        WHEN EXTRACT(MONTH FROM NEW.date) < 8 THEN EXTRACT(YEAR FROM NEW.date) - 1
        ELSE EXTRACT(YEAR FROM NEW.date)
    END;
    
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 25426)
-- Name: match_partials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.match_partials (
    match_id integer NOT NULL,
    q1_home integer,
    q2_home integer,
    q3_home integer,
    q4_home integer,
    q1_away integer,
    q2_away integer,
    q3_away integer,
    q4_away integer
);


--
-- TOC entry 222 (class 1259 OID 25429)
-- Name: players_career_path; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players_career_path (
    identifier integer NOT NULL,
    player_id bigint NOT NULL,
    season character varying(255),
    league character varying(255),
    team_id bigint,
    team_name character varying(255),
    license character varying(255),
    date_in date,
    date_out date
);


--
-- TOC entry 223 (class 1259 OID 25434)
-- Name: players_career_path_identifier_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.players_career_path_identifier_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3467 (class 0 OID 0)
-- Dependencies: 223
-- Name: players_career_path_identifier_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.players_career_path_identifier_seq OWNED BY public.players_career_path.identifier;


--
-- TOC entry 224 (class 1259 OID 25435)
-- Name: players_info; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players_info (
    player_id bigint NOT NULL,
    player_name character varying(255),
    "position" character varying(255),
    height bigint,
    weight bigint,
    birthday date,
    nationality character varying(255),
    player_link character varying(255) NOT NULL
);


--
-- TOC entry 235 (class 1259 OID 25820)
-- Name: players_matches_stats_identifier_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.players_matches_stats_identifier_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 225 (class 1259 OID 25440)
-- Name: players_matches_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players_matches_stats (
    identifier integer DEFAULT nextval('public.players_matches_stats_identifier_seq'::regclass) NOT NULL,
    match_id integer,
    team_id integer,
    vs_team_id integer,
    player_id integer,
    player_link character varying(255),
    starting boolean,
    number integer,
    player_name character varying(255),
    minutes time without time zone,
    points integer,
    two_points_in integer,
    two_points_tried integer,
    two_points_perc double precision,
    three_points_in integer,
    three_points_tried integer,
    three_points_perc double precision,
    field_goals_in integer,
    field_goals_tried integer,
    field_goals_perc double precision,
    free_throws_in integer,
    free_throws_tried integer,
    free_throws_perc double precision,
    offensive_rebounds integer,
    deffensive_rebounds integer,
    total_rebounds integer,
    assists integer,
    steals integer,
    turnovers integer,
    blocks_favor integer,
    blocks_against integer,
    dunks integer,
    personal_fouls integer,
    fouls_received integer,
    efficiency integer,
    balance integer,
    middle_shootings_in integer,
    middle_shootings_tried integer,
    middle_shootings_perc double precision,
    zone_shootings_in integer,
    zone_shootings_tried integer,
    zone_shootings_perc double precision
);


--
-- TOC entry 226 (class 1259 OID 25445)
-- Name: players_stats_career; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.players_stats_career (
    player_id integer NOT NULL,
    season character varying(255),
    team_name_extended character varying(255),
    stage_abbrev character varying(255),
    stage_name_extended character varying(255),
    n_matches bigint,
    min_total character varying(255),
    min_avg time(0) without time zone,
    points_total bigint,
    points_avg double precision,
    twos_in_total bigint,
    twos_tried_total bigint,
    twos_perc double precision,
    twos_in_avg double precision,
    twos_tried_avg double precision,
    threes_in_total bigint,
    threes_tried_total bigint,
    threes_perc double precision,
    threes_in_avg double precision,
    threes_tried_avg double precision,
    field_goals_in_total bigint,
    field_goals_tried_total bigint,
    field_goals_perc double precision,
    field_goals_in_avg double precision,
    field_goals_tried_avg double precision,
    free_throws_in_total bigint,
    free_throws_tried_total bigint,
    free_throws_perc double precision,
    free_throws_in_avg double precision,
    free_throws_tried_avg double precision,
    offensive_rebounds_total bigint,
    offensive_rebounds_avg double precision,
    deffensive_rebounds_total bigint,
    deffensive_rebounds_avg double precision,
    total_rebounds_total bigint,
    total_rebounds_avg double precision,
    assists_total bigint,
    assists_avg double precision,
    turnovers_total bigint,
    turnovers_avg double precision,
    blocks_favor_total bigint,
    blocks_favor_avg double precision,
    blocks_against_total bigint,
    blocks_against_avg double precision,
    dunks_total bigint,
    dunks_avg double precision,
    personal_fouls_total bigint,
    personal_fouls_avg double precision,
    fouls_received_total bigint,
    fouls_received_avg double precision,
    efficiency_total bigint,
    efficiency_avg double precision,
    identifier integer NOT NULL
);


--
-- TOC entry 227 (class 1259 OID 25450)
-- Name: players_stats_career_identifier_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.players_stats_career_identifier_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3468 (class 0 OID 0)
-- Dependencies: 227
-- Name: players_stats_career_identifier_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.players_stats_career_identifier_seq OWNED BY public.players_stats_career.identifier;


--
-- TOC entry 228 (class 1259 OID 25451)
-- Name: players_stats_career_view; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.players_stats_career_view AS
 SELECT DISTINCT player_id,
    season,
    team_name_extended,
    stage_abbrev,
    stage_name_extended,
    n_matches,
    min_total,
    (regexp_replace((min_total)::text, ':.*'::text, ''::text))::integer AS min_total_mins,
    min_avg,
    points_total,
    points_avg,
    twos_in_total,
    twos_tried_total,
    twos_perc,
    twos_in_avg,
    twos_tried_avg,
    threes_in_total,
    threes_perc,
    threes_in_avg,
    threes_tried_avg,
    field_goals_tried_total,
    field_goals_perc,
    field_goals_in_avg,
    field_goals_tried_avg,
    free_throws_tried_total,
    free_throws_perc,
    free_throws_in_avg,
    free_throws_tried_avg,
    offensive_rebounds_total,
    offensive_rebounds_avg,
    deffensive_rebounds_total,
    deffensive_rebounds_avg,
    total_rebounds_total,
    total_rebounds_avg,
    assists_total,
    assists_avg,
    turnovers_total,
    turnovers_avg,
    blocks_favor_total,
    blocks_favor_avg,
    blocks_against_total,
    blocks_against_avg,
    dunks_total,
    dunks_avg,
    personal_fouls_total,
    personal_fouls_avg,
    fouls_received_total,
    fouls_received_avg,
    efficiency_total,
    efficiency_avg
   FROM public.players_stats_career;


--
-- TOC entry 229 (class 1259 OID 25456)
-- Name: results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.results (
    match_id integer NOT NULL,
    home_team_id integer,
    away_team_id integer,
    stage_id integer,
    matchday integer,
    home_score integer,
    away_score integer,
    date date,
    match_link character varying(255),
    "time" time without time zone,
    category character varying(255)
);


--
-- TOC entry 230 (class 1259 OID 25461)
-- Name: shooting_chart_availability; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shooting_chart_availability (
    match_id integer NOT NULL,
    availability boolean
);


--
-- TOC entry 237 (class 1259 OID 25822)
-- Name: shootings_identifier_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.shootings_identifier_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 231 (class 1259 OID 25464)
-- Name: shootings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shootings (
    identifier integer DEFAULT nextval('public.shootings_identifier_seq'::regclass) NOT NULL,
    player_id integer NOT NULL,
    match_id integer NOT NULL,
    team_id integer,
    home_away character varying(255),
    vs_team_id integer,
    number integer,
    player_name character varying(255),
    success boolean,
    quarter integer,
    shoot_time time without time zone,
    top_top double precision,
    left_left double precision,
    shooting_type character varying(255),
    shoot_from text,
    season integer
);


--
-- TOC entry 232 (class 1259 OID 25469)
-- Name: stages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stages (
    stage_id integer NOT NULL,
    stage_name character varying(255),
    year integer
);


--
-- TOC entry 233 (class 1259 OID 25472)
-- Name: teams; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams (
    team_id integer NOT NULL,
    team_name character varying(255)
);


--
-- TOC entry 236 (class 1259 OID 25821)
-- Name: teams_matches_stats_identifier_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.teams_matches_stats_identifier_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 234 (class 1259 OID 25475)
-- Name: teams_matches_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.teams_matches_stats (
    identifier integer DEFAULT nextval('public.teams_matches_stats_identifier_seq'::regclass) NOT NULL,
    match_id integer NOT NULL,
    team_id integer,
    vs_team_id integer,
    points integer,
    two_points_in integer,
    two_points_tried integer,
    two_points_perc double precision,
    three_points_in integer,
    three_points_tried integer,
    three_points_perc double precision,
    field_goals_in integer,
    field_goals_tried integer,
    field_goals_perc double precision,
    free_throws_in integer,
    free_throws_tried integer,
    free_throws_perc double precision,
    offensive_rebounds integer,
    deffensive_rebounds integer,
    total_rebounds integer,
    assists integer,
    steals integer,
    turnovers integer,
    blocks_favor integer,
    blocks_against integer,
    dunks integer,
    personal_fouls integer,
    fouls_received integer,
    efficiency integer,
    middle_shootings_in integer,
    middle_shootings_tried integer,
    middle_shootings_perc double precision,
    zone_shootings_in integer,
    zone_shootings_tried integer,
    zone_shootings_perc double precision,
    minutes character varying(255)
);


--
-- TOC entry 3267 (class 2604 OID 25478)
-- Name: players_career_path identifier; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_career_path ALTER COLUMN identifier SET DEFAULT nextval('public.players_career_path_identifier_seq'::regclass);


--
-- TOC entry 3269 (class 2604 OID 25479)
-- Name: players_stats_career identifier; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_stats_career ALTER COLUMN identifier SET DEFAULT nextval('public.players_stats_career_identifier_seq'::regclass);


--
-- TOC entry 3273 (class 2606 OID 25481)
-- Name: match_partials match_partials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match_partials
    ADD CONSTRAINT match_partials_pkey PRIMARY KEY (match_id);


--
-- TOC entry 3275 (class 2606 OID 25483)
-- Name: players_career_path players_career_path_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_career_path
    ADD CONSTRAINT players_career_path_pkey PRIMARY KEY (identifier);


--
-- TOC entry 3277 (class 2606 OID 25485)
-- Name: players_info players_info_PKEY; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_info
    ADD CONSTRAINT "players_info_PKEY" PRIMARY KEY (player_id);


--
-- TOC entry 3279 (class 2606 OID 25487)
-- Name: players_matches_stats players_matches_stats_2_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_matches_stats
    ADD CONSTRAINT players_matches_stats_2_pkey PRIMARY KEY (identifier);


--
-- TOC entry 3281 (class 2606 OID 25489)
-- Name: players_stats_career players_stats_career_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_stats_career
    ADD CONSTRAINT players_stats_career_pkey PRIMARY KEY (identifier);


--
-- TOC entry 3283 (class 2606 OID 25491)
-- Name: results results_leb_oro_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT results_leb_oro_pkey PRIMARY KEY (match_id);


--
-- TOC entry 3285 (class 2606 OID 25493)
-- Name: shooting_chart_availability shooting_chart_availability_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shooting_chart_availability
    ADD CONSTRAINT shooting_chart_availability_pkey PRIMARY KEY (match_id);


--
-- TOC entry 3287 (class 2606 OID 25495)
-- Name: shootings shootings_pkey_2; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shootings
    ADD CONSTRAINT shootings_pkey_2 PRIMARY KEY (identifier);


--
-- TOC entry 3289 (class 2606 OID 25497)
-- Name: stages stages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stages
    ADD CONSTRAINT stages_pkey PRIMARY KEY (stage_id);


--
-- TOC entry 3293 (class 2606 OID 25499)
-- Name: teams_matches_stats teams_matches_stats_2_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_matches_stats
    ADD CONSTRAINT teams_matches_stats_2_pkey PRIMARY KEY (identifier);


--
-- TOC entry 3291 (class 2606 OID 25501)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 3312 (class 2620 OID 25590)
-- Name: results check_and_insert_away_team_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER check_and_insert_away_team_id_trigger BEFORE INSERT ON public.results FOR EACH ROW EXECUTE FUNCTION public.check_and_insert_away_team_id();


--
-- TOC entry 3313 (class 2620 OID 25592)
-- Name: results check_and_insert_home_team_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER check_and_insert_home_team_id_trigger BEFORE INSERT ON public.results FOR EACH ROW EXECUTE FUNCTION public.check_and_insert_home_team_id();


--
-- TOC entry 3311 (class 2620 OID 26022)
-- Name: players_matches_stats check_and_insert_player_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER check_and_insert_player_id_trigger BEFORE INSERT ON public.players_matches_stats FOR EACH ROW EXECUTE FUNCTION public.check_and_insert_player_id();


--
-- TOC entry 3314 (class 2620 OID 25588)
-- Name: results check_and_insert_stage_id_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER check_and_insert_stage_id_trigger BEFORE INSERT ON public.results FOR EACH ROW EXECUTE FUNCTION public.check_and_insert_stage_id();


--
-- TOC entry 3315 (class 2620 OID 26247)
-- Name: shootings shootings_insert_trigger; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER shootings_insert_trigger BEFORE INSERT ON public.shootings FOR EACH ROW EXECUTE FUNCTION public.shootings_insert_function();


--
-- TOC entry 3301 (class 2606 OID 25502)
-- Name: results away_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT away_team_id FOREIGN KEY (away_team_id) REFERENCES public.teams(team_id);


--
-- TOC entry 3302 (class 2606 OID 25507)
-- Name: results home_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT home_team_id FOREIGN KEY (home_team_id) REFERENCES public.teams(team_id);


--
-- TOC entry 3304 (class 2606 OID 25512)
-- Name: shooting_chart_availability match_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shooting_chart_availability
    ADD CONSTRAINT match_id FOREIGN KEY (match_id) REFERENCES public.results(match_id) NOT VALID;


--
-- TOC entry 3294 (class 2606 OID 25517)
-- Name: match_partials match_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.match_partials
    ADD CONSTRAINT match_id FOREIGN KEY (match_id) REFERENCES public.results(match_id) NOT VALID;


--
-- TOC entry 3297 (class 2606 OID 25522)
-- Name: players_matches_stats match_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_matches_stats
    ADD CONSTRAINT match_id FOREIGN KEY (match_id) REFERENCES public.results(match_id) NOT VALID;


--
-- TOC entry 3308 (class 2606 OID 25527)
-- Name: teams_matches_stats match_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_matches_stats
    ADD CONSTRAINT match_id FOREIGN KEY (match_id) REFERENCES public.results(match_id) NOT VALID;


--
-- TOC entry 3305 (class 2606 OID 25532)
-- Name: shootings match_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shootings
    ADD CONSTRAINT match_id FOREIGN KEY (match_id) REFERENCES public.results(match_id) NOT VALID;


--
-- TOC entry 3295 (class 2606 OID 25537)
-- Name: players_career_path player_idFK; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_career_path
    ADD CONSTRAINT "player_idFK" FOREIGN KEY (player_id) REFERENCES public.players_info(player_id) NOT VALID;


--
-- TOC entry 3300 (class 2606 OID 25542)
-- Name: players_stats_career player_idFK; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_stats_career
    ADD CONSTRAINT "player_idFK" FOREIGN KEY (player_id) REFERENCES public.players_info(player_id) NOT VALID;


--
-- TOC entry 3303 (class 2606 OID 25547)
-- Name: results stage_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.results
    ADD CONSTRAINT stage_id FOREIGN KEY (stage_id) REFERENCES public.stages(stage_id);


--
-- TOC entry 3298 (class 2606 OID 25552)
-- Name: players_matches_stats team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_matches_stats
    ADD CONSTRAINT team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3309 (class 2606 OID 25557)
-- Name: teams_matches_stats team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_matches_stats
    ADD CONSTRAINT team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3306 (class 2606 OID 25562)
-- Name: shootings team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shootings
    ADD CONSTRAINT team_id FOREIGN KEY (team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3296 (class 2606 OID 25567)
-- Name: players_career_path team_idFK; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_career_path
    ADD CONSTRAINT "team_idFK" FOREIGN KEY (team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3299 (class 2606 OID 25572)
-- Name: players_matches_stats vs_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.players_matches_stats
    ADD CONSTRAINT vs_team_id FOREIGN KEY (vs_team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3310 (class 2606 OID 25577)
-- Name: teams_matches_stats vs_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.teams_matches_stats
    ADD CONSTRAINT vs_team_id FOREIGN KEY (vs_team_id) REFERENCES public.teams(team_id) NOT VALID;


--
-- TOC entry 3307 (class 2606 OID 25582)
-- Name: shootings vs_team_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shootings
    ADD CONSTRAINT vs_team_id FOREIGN KEY (vs_team_id) REFERENCES public.teams(team_id) NOT VALID;


-- Completed on 2025-01-19 18:30:09 UTC

--
-- PostgreSQL database dump complete
--

