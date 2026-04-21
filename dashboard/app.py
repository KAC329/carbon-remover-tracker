"""
dashboard/app.py
Carbon Removal Tracker — Main Streamlit Application
"""

import streamlit as st

st.set_page_config(
    page_title="Carbon Removal Tracker",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a1a;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1f0f;
    border-right: 1px solid #1e3a1e;
}
[data-testid="stSidebar"] * {
    color: #e8f0e8 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Main content */
.main .block-container {
    padding: 2rem 3rem;
    max-width: 1100px;
}

/* Typography */
h1 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 3.2rem !important;
    font-weight: 400 !important;
    line-height: 1.1 !important;
    letter-spacing: -0.02em !important;
    color: #0f1f0f !important;
}
h2 {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2rem !important;
    font-weight: 400 !important;
    color: #0f1f0f !important;
    margin-top: 2rem !important;
}
h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #5a7a5a !important;
}

/* Metric cards */
.metric-card {
    background: #f7f9f7;
    border: 1px solid #d4e4d4;
    border-left: 4px solid #2d6a2d;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.metric-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #0f1f0f;
    line-height: 1;
}
.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a7a5a;
    margin-top: 0.3rem;
}
.metric-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.5rem;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #d4e4d4;
    margin: 2rem 0;
}

/* Insight box */
.insight-box {
    background: #0f1f0f;
    color: #e8f0e8;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    border-left: 4px solid #4CAF50;
}
.insight-box p {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    font-style: italic;
    color: #e8f0e8;
    margin: 0;
    line-height: 1.6;
}

/* Tag pills */
.tag {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-right: 0.4rem;
}
.tag-engineered {
    background: #e8f4fd;
    color: #1565c0;
    border: 1px solid #90caf9;
}
.tag-nature {
    background: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #a5d6a7;
}

/* Plotly chart container */
.chart-container {
    border: 1px solid #d4e4d4;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar Navigation ────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1.5rem 0 2rem 0;'>
        <div style='font-family: DM Serif Display, serif; font-size: 1.4rem; color: #e8f0e8; line-height: 1.2;'>
            Carbon<br>Removal<br>Tracker
        </div>
        <div style='font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase;
                    color: #5a9a5a; margin-top: 0.5rem;'>
            US · 2018–2050
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        ["Home", "Compare Technologies", "ESG vs Reality", "Forecasts", "About"],
        label_visibility="collapsed"
    )

# ── Page Routing ──────────────────────────────────────────────────
if page == "Home":
    from pages.home import render
    render()
elif page == "Compare Technologies":
    from pages.compare import render
    render()
elif page == "ESG vs Reality":
    from pages.esg import render
    render()
elif page == "Forecasts":
    from pages.forecasts import render
    render()
elif page == "About":
    from pages.about import render
    render()