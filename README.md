# Carbon Removal Tracker

A quantitative analysis and forecasting platform comparing engineered and nature-based carbon removal pathways across the United States.

**Technologies tracked:**
- Direct Air Capture (DAC)
- Point-Source Industrial Carbon Capture
- Urban Forestry (city canopy data)
- Reforestation / Afforestation

**What it does:**
- Stores historical cost, deployment, and market data in PostgreSQL
- Scores technologies using a climate impact framework (abatement potential vs. cost)
- Forecasts cost trajectories using Wright's Law learning curves and logistic growth models
- Tracks voluntary carbon market prices and federal investment flows (IRA)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Database | PostgreSQL 16 |
| ORM / pipeline | Python, SQLAlchemy, pandas |
| Forecasting | NumPy, SciPy, scikit-learn |
| Dashboard | Streamlit + Plotly |

---

## Local Setup

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 16 ([download](https://www.postgresql.org/download/))
- Git

### 2. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/carbon-removal-tracker.git
cd carbon-removal-tracker
```

### 3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Open `psql` and run:

```sql
CREATE USER carbon_user WITH PASSWORD 'your_password_here';
CREATE DATABASE carbon_removal_db OWNER carbon_user;
GRANT ALL PRIVILEGES ON DATABASE carbon_removal_db TO carbon_user;
\q
```

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=carbon_removal_db
DB_USER=carbon_user
DB_PASSWORD=your_password_here
```

### 6. Run the schema migration

```bash
psql -U carbon_user -d carbon_removal_db -f db/migrations/001_initial_schema.sql
psql -U carbon_user -d carbon_removal_db -f db/seeds/001_reference_data.sql
```

### 7. Run the ETL pipeline

This loads all historical data into the database:

```bash
python -m pipeline.run_pipeline
```

To run only specific extractors:

```bash
python -m pipeline.run_pipeline --extractors dac
python -m pipeline.run_pipeline --extractors nature markets
```

### 8. Verify the data loaded

```bash
psql -U carbon_user -d carbon_removal_db
```

```sql
SELECT tc.name, COUNT(*) as rows
FROM cost_metrics cm
JOIN technology_categories tc ON tc.id = cm.technology_id
GROUP BY tc.name;
```

---

## Project Structure

```
carbon_removal_tracker/
│
├── db/
│   ├── connection.py          # SQLAlchemy engine
│   ├── migrations/            # SQL schema files (run in order)
│   └── seeds/                 # Reference / lookup data
│
├── pipeline/
│   ├── extractors/            # One file per data source
│   │   ├── base.py            # Abstract base class
│   │   ├── dac_costs.py       # DAC cost + deployment data
│   │   ├── nature_based.py    # Urban forestry + reforestation
│   │   └── carbon_markets.py  # VCM prices + investment flows
│   ├── loaders/
│   │   └── db_loader.py       # Writes DataFrames → PostgreSQL
│   └── run_pipeline.py        # Master ETL runner
│
├── forecasting/
│   ├── cost_curves.py         # Wright's Law + logistic growth models
│   └── scoring.py             # Climate score framework
│
├── dashboard/                 # Streamlit app (Phase 4)
├── notebooks/                 # Exploratory analysis
├── data/
│   ├── raw/                   # Downloaded source files (gitignored)
│   └── processed/             # Cleaned intermediate files (gitignored)
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Database Schema

Core tables:

| Table | Description |
|---|---|
| `technology_categories` | The four technology tracks |
| `geographies` | National, state, and city level |
| `data_sources` | Source citations for all data |
| `cost_metrics` | Annual $/tCO2 by technology |
| `deployment_metrics` | Annual capacity and area data |
| `abatement_potential` | CO2 reduction estimates by target year |
| `climate_scores` | Computed 1-10 scores |
| `carbon_credit_prices` | VCM market prices by credit type |
| `investment_flows` | Federal + private funding flows |
| `co_benefits` | Non-GHG benefits (air quality, heat island) |
| `forecast_results` | Model outputs written back to DB |

---

## Roadmap

- [x] Phase 1 — Database schema design
- [x] Phase 2 — ETL pipeline (extractors + loaders)
- [ ] Phase 3 — Forecasting models (Wright's Law, logistic growth)
- [ ] Phase 4 — Streamlit dashboard with Plotly maps
- [ ] Phase 5 — Financial market overlay (VCM price spreads, IRA funding)

---

## Data Sources

| Source | Used For |
|---|---|
| IEA World Energy Outlook | DAC cost trajectories |
| DOE Carbon Negative Shot | DAC deployment targets |
| CDR.fyi | Real-time DAC project tracking |
| USFS i-Tree Analytics | Urban canopy + sequestration |
| EPA GHG Inventory (LULUCF) | Reforestation sink data |
| Ecosystem Marketplace | Voluntary carbon market prices |
| Rhodium Group / IRA Tracker | Federal investment flows |

---

## Skills Demonstrated

- PostgreSQL schema design (normalization, indexes, constraints)
- Python ETL pipelines (extract → transform → load)
- Time series and learning curve forecasting
- Data visualization (Plotly, Streamlit)
- Climate impact quantification (LCA concepts, abatement cost/potential)
