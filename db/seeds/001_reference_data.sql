-- =============================================================
-- Seed Data — Reference Tables
-- =============================================================

-- Technology categories
INSERT INTO technology_categories (name, slug, track, description) VALUES
    ('Direct Air Capture',          'dac',           'engineered',   'Mechanical/chemical systems that pull CO2 directly from ambient air'),
    ('Point-Source Capture',        'point_source',  'engineered',   'Carbon capture at industrial emission sources: power plants, cement, steel'),
    ('Urban Forestry',              'urban_forestry','nature_based',  'Urban tree canopy planting and management in US cities'),
    ('Reforestation',               'reforestation', 'nature_based',  'Restoring forests on previously forested US land');

-- Geographies — national + key states + key cities
INSERT INTO geographies (name, geo_type, state_code) VALUES
    ('United States',       'national', NULL),
    ('California',          'state',    'CA'),
    ('Texas',               'state',    'TX'),
    ('New York',            'state',    'NY'),
    ('New Jersey',          'state',    'NJ'),
    ('Pennsylvania',        'state',    'PA'),
    ('Washington',          'state',    'WA'),
    ('Oregon',              'state',    'OR'),
    ('New York City',       'city',     'NY'),
    ('Los Angeles',         'city',     'CA'),
    ('Houston',             'city',     'TX'),
    ('Newark',              'city',     'NJ'),
    ('Philadelphia',        'city',     'PA'),
    ('Seattle',             'city',     'WA'),
    ('Portland',            'city',     'OR');

-- Data sources
INSERT INTO data_sources (name, organization, url, source_year, notes) VALUES
    ('IEA World Energy Outlook 2023',
        'IEA', 'https://www.iea.org/reports/world-energy-outlook-2023', 2023, 'Annual flagship report'),
    ('DOE Carbon Negative Shot',
        'U.S. DOE', 'https://www.energy.gov/fecm/carbon-negative-shot', 2023, 'DOE $100/tonne DAC target program'),
    ('CDR.fyi Live DAC Tracker',
        'CDR.fyi', 'https://www.cdr.fyi', 2024, 'Tracks real DAC purchases and deployments'),
    ('USFS Urban Forest Analytics',
        'U.S. Forest Service', 'https://www.fs.usda.gov/managing-land/urban-forests/analytics', 2023, 'i-Tree based city canopy data'),
    ('Global Forest Watch — US',
        'World Resources Institute', 'https://www.globalforestwatch.org', 2024, 'Tree cover loss/gain data'),
    ('Ecosystem Marketplace VCM Report 2023',
        'Forest Trends', 'https://www.ecosystemmarketplace.com', 2023, 'Voluntary carbon market pricing'),
    ('IRA Federal Funding Tracker',
        'DOE / Rhodium Group', 'https://rhg.com/research/inflation-reduction-act/', 2023, 'IRA investment tracking'),
    ('NCASI US Forest Carbon Data',
        'NCASI', 'https://www.ncasi.org', 2023, 'Forest carbon sequestration rates'),
    ('Carbon180 DAC Policy Brief',
        'Carbon180', 'https://carbon180.org', 2023, NULL),
    ('CarbonPlan CDR Database',
        'CarbonPlan', 'https://carbonplan.org/research/cdr-database', 2024, 'Independent CDR project assessments');
