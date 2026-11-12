-- AapadaOps PostGIS & Extension Initialization Script
-- Automatically executed upon container first initialization

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "postgis_topology";
CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- Performance tuning for spatial geometry index builds
SET maintenance_work_mem = '128MB';
SET random_page_cost = 1.1;
SET effective_io_concurrency = 200;

-- Verification query
DO $$
BEGIN
    RAISE NOTICE 'PostGIS version: %', PostGIS_Full_Version();
END $$;
