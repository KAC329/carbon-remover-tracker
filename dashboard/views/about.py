"""
dashboard/pages/about.py
About page.
"""

import streamlit as st


def render():
    st.markdown("""
    <h3>About</h3>
    <h1>What is this,<br>and why does it matter?</h1>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:1.05rem; color:#444; max-width:700px; line-height:1.8;'>
    The Carbon Removal Tracker is an open-source quantitative analysis platform
    comparing engineered and nature-based carbon dioxide removal (CDR) pathways
    across the United States. It was built to answer a simple but unresolved question:
    <em>given the data we have, where should carbon removal investment go?</em>
    </p>

    <p style='font-size:1.05rem; color:#444; max-width:700px; line-height:1.8;'>
    The IPCC has been clear that achieving net-zero by mid-century requires not just
    reducing emissions, but actively removing CO₂ already in the atmosphere.
    Two broad strategies have emerged — engineered removal (Direct Air Capture,
    industrial carbon capture) and nature-based solutions (forests, urban trees).
    They are rarely compared on the same quantitative terms. This project does that.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    st.markdown("## Methodology")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; padding:1.5rem; margin-bottom:1rem;'>
            <div style='font-family: DM Serif Display, serif; font-size:1.1rem;
                        margin-bottom:0.8rem;'>Climate Scoring</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Each technology is scored 1–10 on two axes:
                abatement potential (Gt or Mt CO₂ by target year)
                and abatement cost ($/tCO₂). The composite score
                is the arithmetic mean.
            </div>
        </div>
        <div style='border:1px solid #d4e4d4; padding:1.5rem; margin-bottom:1rem;'>
            <div style='font-family: DM Serif Display, serif; font-size:1.1rem;
                        margin-bottom:0.8rem;'>DAC Forecasting</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Wright's Law learning curve model.
                Cost = C₀ × (x/x₀)^(−b), where b = log₂(1 − learning_rate).
                Conservative (15%) and optimistic (20%) scenarios.
                Validated against solar PV and battery historical data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; padding:1.5rem; margin-bottom:1rem;'>
            <div style='font-family: DM Serif Display, serif; font-size:1.1rem;
                        margin-bottom:0.8rem;'>Nature-Based Forecasting</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Logistic growth S-curve model.
                C(t) = K / (1 + exp(−r(t − t₀))).
                Carrying capacities set from USFS and EPA technical potential estimates.
                Reforestation K = 950 MtCO₂/yr; Urban Forestry K = 45 MtCO₂/yr.
            </div>
        </div>
        <div style='border:1px solid #d4e4d4; padding:1.5rem; margin-bottom:1rem;'>
            <div style='font-family: DM Serif Display, serif; font-size:1.1rem;
                        margin-bottom:0.8rem;'>ESG Analysis</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Institutional ESG data from LSEG (Refinitiv) via WRDS,
                covering 9 US companies across four roles:
                DAC operators, CDR buyers, industrial emitters, and financiers.
                2018–2024 annual data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)
    st.markdown("## Data Sources")

    sources = [
        ("IEA World Energy Outlook 2023", "DAC cost trajectories", "https://www.iea.org/reports/world-energy-outlook-2023"),
        ("DOE Carbon Negative Shot", "DAC deployment targets and $100/t goal", "https://www.energy.gov/fecm/carbon-negative-shot"),
        ("CDR.fyi", "Real-time DAC project tracking", "https://www.cdr.fyi"),
        ("USFS Urban Forest Analytics (i-Tree)", "Urban canopy and sequestration data", "https://www.fs.usda.gov/managing-land/urban-forests/analytics"),
        ("EPA GHG Inventory (LULUCF)", "US forest carbon sink data", "https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks"),
        ("LSEG ESG Data (via WRDS)", "Institutional ESG scores and emissions", "https://wrds-www.wharton.upenn.edu"),
        ("Ecosystem Marketplace VCM Report", "Voluntary carbon market pricing", "https://www.ecosystemmarketplace.com/carbon-markets/"),
        ("Rhodium Group IRA Tracker", "Federal investment flows", "https://rhg.com/research/inflation-reduction-act/"),
    ]

    for name, desc, url in sources:
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:baseline;
                    padding:0.8rem 0; border-bottom:1px solid #f0f0f0;'>
            <div>
                <div style='font-weight:500; font-size:0.9rem;'>{name}</div>
                <div style='font-size:0.8rem; color:#777;'>{desc}</div>
            </div>
            <a href='{url}' target='_blank'
               style='font-size:0.75rem; color:#2d6a2d; font-family: DM Mono, monospace;
                      text-decoration:none; white-space:nowrap; margin-left:1rem;'>
                View source →
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)
    st.markdown("## Tech Stack")

    stack = [
        ("PostgreSQL 16", "Relational database"),
        ("Python + SQLAlchemy", "ETL pipeline and ORM"),
        ("pandas + NumPy", "Data manipulation and modeling"),
        ("Wright's Law + Logistic Growth", "Forecasting models"),
        ("Streamlit + Plotly", "Dashboard and visualization"),
        ("LSEG ESG via WRDS", "Institutional financial data"),
        ("Git + GitHub", "Version control"),
    ]

    cols = st.columns(3)
    for i, (tool, desc) in enumerate(stack):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#f7f9f7; border:1px solid #d4e4d4;
                        padding:1rem; margin-bottom:0.8rem;'>
                <div style='font-family: DM Mono, monospace; font-size:0.85rem;
                            color:#0f1f0f; font-weight:600;'>{tool}</div>
                <div style='font-size:0.78rem; color:#666; margin-top:0.2rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding:2rem 0; color:#888;'>
        <div style='font-family: DM Serif Display, serif; font-size:1.1rem;
                    color:#0f1f0f; margin-bottom:0.5rem;'>Kaitlin Ciuba</div>
        <div style='font-size:0.8rem; letter-spacing:0.08em; text-transform:uppercase;'>
            MS Applied Mathematics · Stevens Institute of Technology
        </div>
        <a href='https://github.com/KAC329/carbon-remover-tracker' target='_blank'
           style='display:inline-block; margin-top:1rem; font-family: DM Mono, monospace;
                  font-size:0.8rem; color:#2d6a2d; text-decoration:none;'>
            github.com/KAC329/carbon-remover-tracker →
        </a>
    </div>
    """, unsafe_allow_html=True)
