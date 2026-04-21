# Carbon Removal Tracker

**A quantitative analysis platform comparing engineered and nature-based carbon dioxide removal (CDR) pathways across the United States.**

🌐 **Live dashboard: [carbon-remover-tracker.streamlit.app](https://carbon-remover-tracker.streamlit.app)**

---

## What it does

The Carbon Removal Tracker answers a simple but unresolved question: *given the data we have, where should carbon removal investment go?*

The IPCC has been clear that achieving net-zero by mid-century requires not just reducing emissions, but actively removing CO₂ already in the atmosphere. Two broad strategies have emerged — engineered removal (Direct Air Capture, industrial carbon capture) and nature-based solutions (forests, urban trees). They are rarely compared on the same quantitative terms. This project does that.

### Four technology pathways tracked:

| Technology | Track | Current Cost | Scale Potential |
|---|---|---|---|
| Direct Air Capture (DAC) | Engineered | ~$270/tCO₂ | 50 Mt/yr by 2030 (DOE target) |
| Point-Source Capture | Engineered | $50–100/tCO₂ | Hundreds of Mt/yr |
| Urban Forestry | Nature-Based | $29–48/tCO₂ | 26–45 Mt/yr nationally |
| Reforestation | Nature-Based | $10–15/tCO₂ | 750–950 Mt/yr US forest sink |

### Key findings:

- DAC costs have fallen ~70% since 2010. Wright's Law modeling suggests the DOE's $100/tonne target is achievable by 2030.
- US forests already absorb ~750 MtCO₂/yr — roughly 12% of total US emissions — but face hard limits from wildfire, drought, and land availability.
- **High ESG score ≠ declining emissions.** Microsoft and Google — the two highest ESG scorers in our dataset — showed emissions increases of 231% and 158% respectively since 2018, driven by AI data center expansion.
- Nature-based carbon credits ($5–25/t) and DAC credits ($300–500/t) represent fundamentally different products: one is cheap and reversible, the other is expensive and permanent.

---

## Dashboard pages

- **Home** — Key metrics, DAC cost curve overview, four pathway summaries
- **Compare Technologies** — Cost over time, voluntary carbon market prices, investment flows
- **ESG vs Reality** — Corporate ESG scores vs. actual emissions (LSEG institutional data)
- **Forecasts** — Wright's Law DAC cost projections, logistic growth nature-based deployment
- **About** — Methodology, data sources, tech stack

---

## Tech stack

| Component | Tool |
|---|---|
| Database | PostgreSQL 16 (local) + Supabase (cloud) |
| ORM / pipeline | Python, SQLAlchemy, pandas |
| Forecasting | NumPy, SciPy — Wright's Law + logistic growth |
| Dashboard | Streamlit + Plotly |
| ESG data | LSEG (Refinitiv) via Wharton WRDS |
| Version control | Git / GitHub |

---

## Local setup

### Prerequisites
- Python 3.10+
- PostgreSQL 16
- Git

### Install

```bash
git clone https://github.com/KAC329/carbon-remover-tracker.git
cd carbon-remover-tracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your DB credentials
```

### Database setup

```bash
psql -U your_user -d your_db -f db/migrations/001_initial_schema.sql
psql -U your_user -d your_db -f db/migrations/002_esg_commitments.sql
psql -U your_user -d your_db -f db/seeds/001_reference_data.sql
```

### Run the pipeline

```bash
python -m pipeline.run_pipeline          # load all data
python -m pipeline.run_pipeline --extractors dac    # specific extractor
python -m forecasting.run_forecasts      # run forecasting models
```

### Launch dashboard

```bash
streamlit run dashboard/app.py
```

---

## Project structure

```
carbon-remover-tracker/
│
├── db/
│   ├── connection.py           # SQLAlchemy engine (local + Supabase)
│   ├── migrations/             # SQL schema files
│   └── seeds/                  # Reference data
│
├── pipeline/
│   ├── extractors/             # One file per data source
│   │   ├── dac_costs.py        # DAC cost + deployment (IEA, DOE, CDR.fyi)
│   │   ├── nature_based.py     # Urban forestry + reforestation (USFS, EPA)
│   │   ├── carbon_markets.py   # VCM prices + investment flows
│   │   ├── lseg_esg.py         # LSEG ESG scores (via WRDS)
│   │   └── lseg_commitments.py # Carbon offsets + reduction targets (WRDS)
│   ├── loaders/
│   │   └── db_loader.py        # Writes DataFrames → PostgreSQL
│   └── run_pipeline.py         # Master ETL runner
│
├── forecasting/
│   ├── cost_curves.py          # Wright's Law + logistic growth models
│   ├── scoring.py              # Climate impact scoring framework
│   └── run_forecasts.py        # Runs models, writes to DB
│
├── dashboard/
│   ├── app.py                  # Main Streamlit entry point
│   ├── data.py                 # Cached DB queries
│   └── views/                  # One file per page
│       ├── home.py
│       ├── compare.py
│       ├── esg.py
│       ├── forecasts.py
│       └── about.py
│
├── data/
│   ├── raw/                    # Downloaded source files
│   └── processed/              # Cleaned intermediate files
│
├── .streamlit/config.toml      # Streamlit theme config
├── requirements.txt
└── README.md
```

---

## Data sources

| Source | Used For |
|---|---|
| [IEA Direct Air Capture 2022](https://www.iea.org/reports/direct-air-capture-2022) | DAC cost trajectories |
| [DOE Carbon Negative Shot](https://www.energy.gov/fecm/carbon-negative-shot) | DAC deployment targets |
| [CDR.fyi](https://www.cdr.fyi) | Real-time DAC project tracking |
| [USFS Urban Forest Analytics](https://www.fs.usda.gov/managing-land/urban-forests/analytics) | Urban canopy + sequestration |
| [EPA GHG Inventory (LULUCF)](https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks) | Reforestation sink data |
| [LSEG ESG (via WRDS)](https://wrds-www.wharton.upenn.edu) | Corporate ESG scores + emissions |
| [Ecosystem Marketplace](https://www.ecosystemmarketplace.com/carbon-markets/) | Voluntary carbon market prices |
| [Rhodium Group IRA Tracker](https://rhg.com/research/inflation-reduction-act/) | Federal investment flows |

---

## Forecasting models

**Wright's Law** (DAC cost trajectory)
> Cost = C₀ × (x/x₀)^(−b), where b = log₂(1 − learning_rate)
>
> Conservative scenario: 15% cost reduction per doubling of cumulative capacity
> Optimistic scenario: 20% (matching solar PV's historical learning rate)
> Reference: [Wright (1936)](https://doi.org/10.2514/8.155)

**Logistic Growth** (nature-based deployment)
> C(t) = K / (1 + exp(−r(t − t₀)))
>
> Reforestation carrying capacity K = 950 MtCO₂/yr
> Urban Forestry carrying capacity K = 45 MtCO₂/yr
> Reference: [Bass (1969)](https://doi.org/10.1287/mnsc.15.5.215)

---

## Author

**Kaitlin Ciuba**
MS Applied Mathematics, Stevens Institute of Technology
BS Biology, The College of New Jersey

*Built as a portfolio project combining quantitative ecology background with applied mathematics, data engineering, and climate finance.*
