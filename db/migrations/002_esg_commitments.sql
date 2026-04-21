-- Migration 002: ESG commitments table
CREATE TABLE esg_commitments (
    id                          SERIAL PRIMARY KEY,
    ticker                      VARCHAR(10) NOT NULL,
    company_name                VARCHAR(200),
    year                        INT NOT NULL,
    carbon_offsets_t            NUMERIC(15, 0),     -- tonnes CO2 offset/purchased
    reduction_target_pct        NUMERIC(6, 2),      -- % reduction target
    reduction_target_year       INT,                -- target year
    climate_risk_acknowledged   BOOLEAN,
    data_source                 VARCHAR(50),        -- 'LSEG/WRDS' or 'hand-curated'
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (ticker, year)
);

CREATE INDEX idx_esg_commitments_ticker_year ON esg_commitments(ticker, year);
