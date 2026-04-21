-- =============================================================
-- Carbon Removal Tracker — Initial Schema
-- =============================================================
-- Four technology tracks:
--   1. Direct Air Capture (DAC)
--   2. Point-Source Carbon Capture (industrial)
--   3. Urban Forestry
--   4. Reforestation / Afforestation
-- =============================================================

-- ---------------------------------------------------------------
-- REFERENCE / LOOKUP TABLES
-- ---------------------------------------------------------------

CREATE TABLE technology_categories (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,   -- e.g. 'Direct Air Capture'
    slug            VARCHAR(50)  NOT NULL UNIQUE,   -- e.g. 'dac'
    track           VARCHAR(50)  NOT NULL,          -- 'engineered' | 'nature_based'
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE geographies (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,          -- e.g. 'United States', 'New Jersey', 'New York City'
    geo_type        VARCHAR(20)  NOT NULL,          -- 'national' | 'state' | 'city'
    state_code      CHAR(2),                        -- NULL for national
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE data_sources (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,          -- e.g. 'IEA World Energy Outlook 2023'
    organization    VARCHAR(100),                   -- e.g. 'IEA', 'DOE', 'USFS'
    url             TEXT,
    source_year     INT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------
-- CORE METRICS TABLES
-- ---------------------------------------------------------------

-- Annual cost & deployment data per technology
CREATE TABLE cost_metrics (
    id                      SERIAL PRIMARY KEY,
    technology_id           INT NOT NULL REFERENCES technology_categories(id),
    geography_id            INT NOT NULL REFERENCES geographies(id),
    data_source_id          INT REFERENCES data_sources(id),
    year                    INT NOT NULL,
    cost_per_tonne_co2_usd  NUMERIC(12, 2),         -- $/tCO2 removed
    cost_low_usd            NUMERIC(12, 2),         -- low estimate
    cost_high_usd           NUMERIC(12, 2),         -- high estimate
    cost_type               VARCHAR(50),            -- 'levelized' | 'marginal' | 'reported'
    notes                   TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (technology_id, geography_id, year, cost_type, data_source_id)
);

-- Annual deployment / capacity data
CREATE TABLE deployment_metrics (
    id                      SERIAL PRIMARY KEY,
    technology_id           INT NOT NULL REFERENCES technology_categories(id),
    geography_id            INT NOT NULL REFERENCES geographies(id),
    data_source_id          INT REFERENCES data_sources(id),
    year                    INT NOT NULL,
    -- engineered tracks
    capacity_mtco2_yr       NUMERIC(15, 4),         -- operational capacity (MtCO2/yr)
    cumulative_capacity_mt  NUMERIC(15, 4),         -- cumulative deployed (MtCO2)
    num_facilities          INT,
    -- nature-based tracks
    area_hectares           NUMERIC(15, 2),         -- trees/forest area
    trees_planted           BIGINT,
    canopy_cover_pct        NUMERIC(5, 2),
    notes                   TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (technology_id, geography_id, year, data_source_id)
);

-- GHG abatement potential estimates
CREATE TABLE abatement_potential (
    id                      SERIAL PRIMARY KEY,
    technology_id           INT NOT NULL REFERENCES technology_categories(id),
    geography_id            INT NOT NULL REFERENCES geographies(id),
    data_source_id          INT REFERENCES data_sources(id),
    target_year             INT NOT NULL,           -- e.g. 2030, 2035, 2050
    potential_mt_co2        NUMERIC(15, 4),         -- MtCO2e potential by target_year
    potential_low_mt        NUMERIC(15, 4),
    potential_high_mt       NUMERIC(15, 4),
    scenario                VARCHAR(50),            -- 'baseline' | 'accelerated' | 'net_zero'
    notes                   TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Climate scores (mirrors the Boundless scoring framework)
CREATE TABLE climate_scores (
    id                          SERIAL PRIMARY KEY,
    technology_id               INT NOT NULL REFERENCES technology_categories(id),
    geography_id                INT NOT NULL REFERENCES geographies(id),
    scored_at_year              INT NOT NULL,        -- year this score was produced
    target_year                 INT NOT NULL,        -- horizon being scored (2030, 2035...)
    abatement_potential_score   NUMERIC(4, 2),       -- 1–10
    abatement_cost_score        NUMERIC(4, 2),       -- 1–10
    composite_score             NUMERIC(4, 2),       -- 1–10
    tier                        VARCHAR(10),         -- 'tier1'=Gt | 'tier2'=Mt
    notes                       TEXT,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (technology_id, geography_id, scored_at_year, target_year)
);

-- ---------------------------------------------------------------
-- FINANCIAL / MARKET TABLES
-- ---------------------------------------------------------------

-- Voluntary carbon market credit prices by type
CREATE TABLE carbon_credit_prices (
    id                  SERIAL PRIMARY KEY,
    technology_id       INT REFERENCES technology_categories(id),
    data_source_id      INT REFERENCES data_sources(id),
    date                DATE NOT NULL,
    price_per_tonne_usd NUMERIC(10, 2) NOT NULL,
    price_low_usd       NUMERIC(10, 2),
    price_high_usd      NUMERIC(10, 2),
    registry            VARCHAR(100),               -- 'Verra', 'Gold Standard', 'CAR', etc.
    credit_type         VARCHAR(100),               -- 'removal' | 'avoidance' | 'nature-based'
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Federal + private investment / funding flows
CREATE TABLE investment_flows (
    id                  SERIAL PRIMARY KEY,
    technology_id       INT NOT NULL REFERENCES technology_categories(id),
    geography_id        INT REFERENCES geographies(id),
    data_source_id      INT REFERENCES data_sources(id),
    year                INT NOT NULL,
    amount_usd_millions NUMERIC(12, 2) NOT NULL,
    funder_type         VARCHAR(50),                -- 'federal' | 'state' | 'private' | 'vc'
    program_name        VARCHAR(200),               -- e.g. 'DOE DAC Hubs Program (IRA)'
    announced_vs_deployed VARCHAR(20),              -- 'announced' | 'deployed'
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------
-- CO-BENEFITS TABLE (urban trees, reforestation extras)
-- ---------------------------------------------------------------

CREATE TABLE co_benefits (
    id                  SERIAL PRIMARY KEY,
    technology_id       INT NOT NULL REFERENCES technology_categories(id),
    geography_id        INT NOT NULL REFERENCES geographies(id),
    data_source_id      INT REFERENCES data_sources(id),
    year                INT NOT NULL,
    benefit_type        VARCHAR(100) NOT NULL,      -- 'heat_island_reduction_c' | 'air_quality_pm25' | 'stormwater_mgmt_liters' | 'biodiversity_index'
    value               NUMERIC(15, 4),
    unit                VARCHAR(50),
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------------
-- FORECASTING OUTPUTS (written back by Python models)
-- ---------------------------------------------------------------

CREATE TABLE forecast_results (
    id                      SERIAL PRIMARY KEY,
    technology_id           INT NOT NULL REFERENCES technology_categories(id),
    geography_id            INT NOT NULL REFERENCES geographies(id),
    model_name              VARCHAR(100) NOT NULL,  -- 'wrights_law' | 'bass_diffusion' | 'arima'
    forecast_year           INT NOT NULL,
    predicted_cost_usd      NUMERIC(12, 2),
    predicted_capacity_mt   NUMERIC(15, 4),
    predicted_score         NUMERIC(4, 2),
    ci_lower                NUMERIC(12, 4),
    ci_upper                NUMERIC(12, 4),
    run_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (technology_id, geography_id, model_name, forecast_year)
);

-- ---------------------------------------------------------------
-- INDEXES for common query patterns
-- ---------------------------------------------------------------

CREATE INDEX idx_cost_metrics_tech_year      ON cost_metrics(technology_id, year);
CREATE INDEX idx_deployment_tech_year        ON deployment_metrics(technology_id, year);
CREATE INDEX idx_abatement_tech_target       ON abatement_potential(technology_id, target_year);
CREATE INDEX idx_credit_prices_tech_date     ON carbon_credit_prices(technology_id, date);
CREATE INDEX idx_investment_tech_year        ON investment_flows(technology_id, year);
CREATE INDEX idx_forecast_tech_model_year    ON forecast_results(technology_id, model_name, forecast_year);
CREATE INDEX idx_co_benefits_tech_geo_year   ON co_benefits(technology_id, geography_id, year);
