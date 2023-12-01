--
-- PostgreSQL database dump
--

-- Dumped from database version 10.16 (Ubuntu 10.16-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 13.11 (Debian 13.11-0+deb11u1)

-- Started on 2023-10-03 12:06:21 EDT

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

-- ****************************************** --
-- CREATE INIT GTFS SCHEMA --
-- ****************************************** --

CREATE SCHEMA gtfs;

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS postgis_raster WITH SCHEMA public;

CREATE FUNCTION gtfs.drop_feed(startdate text, enddate text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN 
EXECUTE 'DROP TABLE IF EXISTS gtfs.agency_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.calendar_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.calendar_attributes_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.calendar_dates_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.checkpoints_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.directions_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.facilities_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.facilities_properties_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.fare_attributes_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.fare_rules_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.frequencies_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.levels_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.lines_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.multi_route_trips_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.pathways_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.route_patterns_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.routes_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.shapes_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.shapes_geog_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.stop_in_pattern_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.stop_times_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.stops_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.stops_geog_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.transfers_' || startdate || '_' || enddate;
EXECUTE 'DROP TABLE IF EXISTS gtfs.trips_' || startdate || '_' || enddate;
END;$$;


SET default_tablespace = '';

CREATE TABLE gtfs.agency (
    agency_id text NOT NULL,
    agency_name text NOT NULL,
    agency_url text NOT NULL,
    agency_timezone text NOT NULL,
    agency_lang text,
    agency_phone text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT agency_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT agency_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.calendar (
    service_id text NOT NULL,
    monday integer NOT NULL,
    tuesday integer NOT NULL,
    wednesday integer NOT NULL,
    thursday integer NOT NULL,
    friday integer NOT NULL,
    saturday integer NOT NULL,
    sunday integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT calendar_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT calendar_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.calendar_attributes (
    service_id text NOT NULL,
    service_description text,
    service_schedule_name text,
    service_schedule_type text,
    service_schedule_typicality integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT calendar_attributes_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT calendar_attributes_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.calendar_dates (
    service_id text NOT NULL,
    date date NOT NULL,
    exception_type integer NOT NULL,
    holiday_name text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT calendar_dates_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT calendar_dates_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.checkpoints (
    checkpoint_id text NOT NULL,
    checkpoint_name text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT checkpoints_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT checkpoints_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.directions (
    route_id text NOT NULL,
    direction_id integer NOT NULL,
    direction text,
    direction_destination text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT directions_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT directions_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.facilities (
    facility_id text NOT NULL,
    facility_code text,
    facility_class integer,
    facility_type text,
    stop_id text,
    facility_short_name text,
    facility_long_name text,
    facility_desc text,
    facility_lat double precision,
    facility_lon double precision,
    wheelchair_facility integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT facilities_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT facilities_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.facilities_properties (
    facility_id text NOT NULL,
    property_id text NOT NULL,
    value text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT facilities_properties_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT facilities_properties_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.feed_info (
    feed_publisher_name text NOT NULL,
    feed_publisher_url text NOT NULL,
    feed_lang text NOT NULL,
    feed_start_date date NOT NULL,
    feed_end_date date NOT NULL,
    feed_version text,
    feed_contact_email text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    creation_timestamp timestamp with time zone NOT NULL,
    etag text
);

CREATE TABLE gtfs.levels (
    level_id text NOT NULL,
    level_index integer,
    level_name text,
    level_elevation text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT levels_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT levels_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.lines (
    line_id text NOT NULL,
    line_short_name text,
    line_long_name text,
    line_desc text,
    line_url text,
    line_color text,
    line_text_color text,
    line_sort_order integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT lines_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT lines_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.multi_route_trips (
    added_route_id text NOT NULL,
    trip_id text NOT NULL,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT multi_route_trips_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT multi_route_trips_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.pathways (
    pathway_id text NOT NULL,
    from_stop_id text NOT NULL,
    to_stop_id text NOT NULL,
    facility_id text,
    pathway_mode integer,
    pathway_type integer,
    traversal_time integer,
    wheelchair_traversal_time integer,
    ramp_slope integer,
    stair_count integer,
    pathway_name text,
    pathway_code text,
    signposted_as text,
    instructions text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT pathways_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT pathways_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.route_patterns (
    route_pattern_id text NOT NULL,
    route_id text NOT NULL,
    direction_id integer NOT NULL,
    route_pattern_name text,
    route_pattern_time_desc text,
    route_pattern_typicality integer,
    route_pattern_sort_order integer,
    representative_trip_id text NOT NULL,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT route_patterns_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT route_patterns_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.routes (
    route_id text NOT NULL,
    agency_id text,
    route_short_name text,
    route_long_name text,
    route_desc text,
    route_type integer NOT NULL,
    route_url text,
    route_color text,
    route_text_color text,
    route_sort_order integer,
    route_fare_class text,
    line_id text,
    listed_route text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT routes_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT routes_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.shapes (
    shape_id text NOT NULL,
    shape_pt_lat double precision NOT NULL,
    shape_pt_lon double precision NOT NULL,
    shape_pt_sequence integer NOT NULL,
    shape_dist_traveled double precision,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT shapes_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT shapes_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.shapes_geog (
    shape_id text NOT NULL,
    shape public.geometry(LineString,4326),
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT shapes_geog_shape_check CHECK (((public.geometrytype(shape) = 'LINESTRING'::text) OR (shape IS NULL))),
    CONSTRAINT shapes_geog_shape_check1 CHECK ((public.st_srid(shape) = 4326)),
    CONSTRAINT shapes_geog_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT shapes_geog_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.stop_in_pattern (
    shape_id text NOT NULL,
    stop_sequence integer NOT NULL,
    stop_id text NOT NULL,
    cumulative_distance integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT stop_in_pattern_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT stop_in_pattern_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.stop_times (
    trip_id text NOT NULL,
    arrival_time interval NOT NULL,
    departure_time interval NOT NULL,
    stop_id text NOT NULL,
    stop_sequence integer NOT NULL,
    stop_headsign text,
    pickup_type integer,
    drop_off_type integer,
    timepoint text,
    checkpoint_id text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT stop_times_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT stop_times_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.stops (
    stop_id text NOT NULL,
    stop_code text,
    stop_name text NOT NULL,
    stop_desc text,
    stop_lat double precision,
    stop_lon double precision,
    zone_id text,
    stop_address text,
    stop_url text,
    level_id text,
    location_type integer,
    parent_station text,
    stop_timezone text,
    wheelchair_boarding integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT stops_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT stops_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.stops_geog (
    stop_id text NOT NULL,
    parent_station text,
    geog_latlon public.geography(Point,4326),
    geom public.geometry,
    easting integer,
    northing integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT stops_geog_geom_check CHECK ((public.st_ndims(geom) = 2)),
    CONSTRAINT stops_geog_geom_check1 CHECK (((public.geometrytype(geom) = 'POINT'::text) OR (geom IS NULL))),
    CONSTRAINT stops_geog_geom_check2 CHECK ((public.st_srid(geom) = 4326)),
    CONSTRAINT stops_geog_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT stops_geog_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.transfers (
    from_stop_id text NOT NULL,
    to_stop_id text NOT NULL,
    transfer_type integer NOT NULL,
    min_transfer_time integer,
    min_walk_time integer,
    min_wheelchair_time integer,
    suggested_buffer_time integer,
    wheelchair_transfer integer,
    from_trip_id text,
    to_trip_id text,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT transfers_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT transfers_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

CREATE TABLE gtfs.trips (
    route_id text NOT NULL,
    service_id text NOT NULL,
    trip_id text NOT NULL,
    trip_headsign text,
    trip_short_name text,
    direction_id integer,
    block_id text,
    shape_id text,
    wheelchair_accessible integer,
    trip_route_type integer,
    route_pattern_id text,
    bikes_allowed integer,
    valid_start_date date NOT NULL,
    valid_end_date date NOT NULL,
    CONSTRAINT trips_valid_end_date_check CHECK ((valid_end_date = '1900-01-01'::date)) NO INHERIT,
    CONSTRAINT trips_valid_start_date_check CHECK ((valid_start_date = '1900-01-01'::date)) NO INHERIT
);

ALTER TABLE ONLY gtfs.agency
    ADD CONSTRAINT agency_pkey PRIMARY KEY (valid_start_date, valid_end_date, agency_id);

ALTER TABLE ONLY gtfs.calendar_dates
    ADD CONSTRAINT calendar_dates_pkey PRIMARY KEY (valid_start_date, valid_end_date, service_id, date);

ALTER TABLE ONLY gtfs.calendar
    ADD CONSTRAINT calendar_pkey PRIMARY KEY (valid_start_date, valid_end_date, service_id);

ALTER TABLE ONLY gtfs.checkpoints
    ADD CONSTRAINT checkpoints_pkey PRIMARY KEY (valid_start_date, valid_end_date, checkpoint_id);

ALTER TABLE ONLY gtfs.directions
    ADD CONSTRAINT directions_pkey PRIMARY KEY (valid_start_date, valid_end_date, route_id, direction_id);

ALTER TABLE ONLY gtfs.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (valid_start_date, valid_end_date, facility_id);

ALTER TABLE ONLY gtfs.feed_info
    ADD CONSTRAINT feed_info_feed_start_date_feed_end_date_key UNIQUE (feed_start_date, feed_end_date);

ALTER TABLE ONLY gtfs.feed_info
    ADD CONSTRAINT feed_info_pkey PRIMARY KEY (valid_start_date, valid_end_date);

ALTER TABLE ONLY gtfs.levels
    ADD CONSTRAINT levels_pkey PRIMARY KEY (valid_start_date, valid_end_date, level_id);

ALTER TABLE ONLY gtfs.lines
    ADD CONSTRAINT lines_pkey PRIMARY KEY (valid_start_date, valid_end_date, line_id);

ALTER TABLE ONLY gtfs.multi_route_trips
    ADD CONSTRAINT multi_route_trips_pkey PRIMARY KEY (valid_start_date, valid_end_date, added_route_id, trip_id);

ALTER TABLE ONLY gtfs.pathways
    ADD CONSTRAINT pathways_pkey PRIMARY KEY (valid_start_date, valid_end_date, pathway_id);

ALTER TABLE ONLY gtfs.route_patterns
    ADD CONSTRAINT route_patterns_pkey PRIMARY KEY (valid_start_date, valid_end_date, route_pattern_id);

ALTER TABLE ONLY gtfs.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (valid_start_date, valid_end_date, route_id);

ALTER TABLE ONLY gtfs.shapes_geog
    ADD CONSTRAINT shapes_geog_pkey PRIMARY KEY (valid_start_date, valid_end_date, shape_id);

ALTER TABLE ONLY gtfs.shapes
    ADD CONSTRAINT shapes_pkey PRIMARY KEY (valid_start_date, valid_end_date, shape_id, shape_pt_sequence);

ALTER TABLE ONLY gtfs.stop_in_pattern
    ADD CONSTRAINT stop_in_pattern_pkey PRIMARY KEY (valid_start_date, valid_end_date, shape_id, stop_sequence);

ALTER TABLE ONLY gtfs.stop_times
    ADD CONSTRAINT stop_times_pkey PRIMARY KEY (valid_start_date, valid_end_date, trip_id, stop_sequence);

ALTER TABLE ONLY gtfs.stops_geog
    ADD CONSTRAINT stops_geog_pkey PRIMARY KEY (valid_start_date, valid_end_date, stop_id);

ALTER TABLE ONLY gtfs.stops
    ADD CONSTRAINT stops_pkey PRIMARY KEY (valid_start_date, valid_end_date, stop_id);

ALTER TABLE ONLY gtfs.trips
    ADD CONSTRAINT trips_pkey PRIMARY KEY (valid_start_date, valid_end_date, route_id);

-- ****************************************** --
-- END INIT GTFS SCHEMA --
-- ****************************************** --

-- ****************************************** --
-- CREATE INIT ODX2 SCHEMA --
-- ****************************************** --

CREATE SCHEMA odx2;

CREATE TABLE odx2.fleet (
    fleet_key smallint NOT NULL,
    fleet_name text NOT NULL,
    operator_id text NOT NULL
);

CREATE TABLE odx2.od_code (
    od_code smallint NOT NULL,
    od_code_name text,
    od_code_desc text
);

CREATE TABLE odx2.pattern (
    pattern_id text NOT NULL,
    route_id text NOT NULL,
    gtfs_dir smallint,
    dir_id text,
    pattern_name text,
    in_service boolean,
    CONSTRAINT pattern_gtfs_dir_check CHECK ((gtfs_dir = ANY (ARRAY[0, 1])))
);

CREATE TABLE odx2.pattern_flow (
    svc_date date NOT NULL,
    pattern_id text NOT NULL,
    hhr interval NOT NULL,
    trip_hhr interval NOT NULL,
    stop_seq smallint NOT NULL,
    ons real,
    offs real,
    flow_out real,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.pattern_stop (
    pattern_id text NOT NULL,
    stop_seq integer NOT NULL,
    stop_id text NOT NULL,
    meters double precision
);

CREATE TABLE odx2.ride (
    stage_key bigint NOT NULL,
    ride_seq smallint NOT NULL,
    svc_date date NOT NULL,
    start_visit_key bigint,
    end_visit_key bigint,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.stage (
    stage_key bigint NOT NULL,
    svc_date date NOT NULL,
    card text,
    jny_seq smallint NOT NULL,
    stage_seq smallint NOT NULL,
    origin text,
    destination text,
    o_time timestamp with time zone,
    d_time timestamp with time zone,
    num_riders smallint NOT NULL,
    o_txn_key bigint,
    d_txn_key bigint,
    o_code smallint NOT NULL,
    d_code smallint NOT NULL,
    x_code smallint NOT NULL,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.trip (
    trip_key bigint NOT NULL,
    svc_date date NOT NULL,
    vehicle_day_key bigint NOT NULL,
    in_service boolean,
    trip_id text,
    sched_trip text,
    num_visits integer NOT NULL,
    route_id text,
    dir_id text,
    pattern_id text,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.vehicle_day (
    vehicle_day_key bigint NOT NULL,
    svc_date date NOT NULL,
    vehicle_id text,
    fleet_key smallint NOT NULL,
    num_cars smallint,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.visit (
    visit_key bigint NOT NULL,
    svc_date date NOT NULL,
    vehicle_day_key bigint NOT NULL,
    seq_in_day integer NOT NULL,
    arrival timestamp with time zone,
    door_open timestamp with time zone,
    door_close timestamp with time zone,
    departure timestamp with time zone,
    trip_key bigint NOT NULL,
    seq_in_trip integer NOT NULL,
    seq_in_pattern integer,
    scheduled boolean,
    stop_id text,
    lat double precision,
    lon double precision,
    ons real,
    offs real,
    load_out real,
    apc_ons real,
    apc_offs real,
    apc_load_out real,
    insert_dt timestamp with time zone NOT NULL
);

CREATE TABLE odx2.xfer_code (
    xfer_code smallint NOT NULL,
    xfer_code_name text,
    xfer_code_desc text
);

-- ****************************************** --
-- END INIT ODX2 SCHEMA --
-- ****************************************** --




-- Completed on 2023-10-03 12:47:44 EDT

--
-- PostgreSQL database dump complete
--

