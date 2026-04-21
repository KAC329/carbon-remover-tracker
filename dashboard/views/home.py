"""
dashboard/views/home.py
Home page — the hook.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_dac_costs, get_forecasts


def render():
    # ── Hero ──────────────────────────────────────────────────────
    st.markdown("""
    <h3>Carbon Removal Tracker</h3>
    <h1>Can we remove enough<br>carbon to matter?</h1>
    <p style='font-size:1.1rem; color:#444; max-width:600px; line-height:1.7; margin-top:1rem;'>
        A quantitative comparison of engineered and nature-based carbon dioxide removal (CDR)
        pathways across the United States — from Direct Air Capture (DAC) to urban forests.
        Built using institutional data from the IEA, DOE, EPA, USFS, and LSEG.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    # ── Key numbers ───────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>$100</div>
            <div class='metric-label'>DOE DAC Target</div>
            <div class='metric-sub'>per tonne CO₂ by 2030
            <br><a href='https://www.energy.gov/fecm/carbon-negative-shot'
            target='_blank' style='color:#5a7a5a; font-size:0.75rem;'>DOE Carbon Negative Shot →</a></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>800Mt</div>
            <div class='metric-label'>US Forest Sink</div>
            <div class='metric-sub'>CO₂ sequestered per year
            <br><a href='https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks'
            target='_blank' style='color:#5a7a5a; font-size:0.75rem;'>EPA GHG Inventory →</a></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>$5B+</div>
            <div class='metric-label'>IRA Investment</div>
            <div class='metric-sub'>federal CDR funding
            <br><a href='https://rhg.com/research/inflation-reduction-act/'
            target='_blank' style='color:#5a7a5a; font-size:0.75rem;'>Rhodium Group IRA Tracker →</a></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-number'>97%</div>
            <div class='metric-label'>DAC Cost Drop</div>
            <div class='metric-sub'>projected 2010–2050
            <br><a href='https://www.iea.org/reports/direct-air-capture-2022'
            target='_blank' style='color:#5a7a5a; font-size:0.75rem;'>IEA DAC Report →</a></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Core insight ──────────────────────────────────────────────
    st.markdown("""
    <div class='insight-box'>
        <p>"Nature-based removal is cheap but constrained by land.
        Engineered removal is expensive but unconstrained —
        and costs are falling fast. The question is whether they fall fast enough."</p>
    </div>
    """, unsafe_allow_html=True)

    # ── DAC cost curve ─────────────────────────────────────────────
    st.markdown("## The DAC Cost Curve")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7;'>
    Direct Air Capture (DAC) has dropped from ~$1,000 per tonne of CO₂ in 2010 to under $300 today —
    a 70% cost reduction in 14 years. The
    <a href='https://www.energy.gov/fecm/carbon-negative-shot' target='_blank' style='color:#2d6a2d;'>
    DOE's Carbon Negative Shot</a> targets $100/tonne by 2030.
    The dashed lines show two forecasting scenarios based on
    <a href='https://doi.org/10.2514/8.155' target='_blank' style='color:#2d6a2d;'>Wright's Law</a>
    — the same learning curve model that predicted solar PV's 90% cost decline.
    See the <strong>Forecasts</strong> page for the full model details.
    </p>
    """, unsafe_allow_html=True)

    dac = get_dac_costs()
    forecasts = get_forecasts()
    dac_fc_con = forecasts[(forecasts["slug"] == "dac") &
                           (forecasts["model_name"] == "wrights_law_conservative")]
    dac_fc_opt = forecasts[(forecasts["slug"] == "dac") &
                           (forecasts["model_name"] == "wrights_law_optimistic")]

    historical = dac[dac["cost_type"].isin(["levelized", "reported"])]

    fig = go.Figure()

    # Confidence band
    fig.add_trace(go.Scatter(
        x=list(dac_fc_con["year"]) + list(dac_fc_con["year"])[::-1],
        y=list(dac_fc_con["ci_upper"]) + list(dac_fc_con["ci_lower"])[::-1],
        fill="toself", fillcolor="rgba(45,106,45,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=dac_fc_con["year"], y=dac_fc_con["cost"],
        mode="lines", name="Conservative forecast (15% learning rate)",
        line=dict(color="#2d6a2d", width=2, dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=dac_fc_opt["year"], y=dac_fc_opt["cost"],
        mode="lines", name="Optimistic forecast (20% learning rate)",
        line=dict(color="#4CAF50", width=2, dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=historical["year"], y=historical["cost"],
        mode="lines+markers", name="Historical reported cost",
        line=dict(color="#0f1f0f", width=3),
        marker=dict(size=7, color="#0f1f0f"),
        hovertemplate="Year: %{x}<br>Cost: $%{y:,.0f}/tCO₂<extra>Historical</extra>"
    ))

    # Annotations
    fig.add_annotation(x=2021, y=400, text="Orca plant opens<br>(Iceland)",
                       showarrow=True, arrowhead=2, arrowcolor="#666",
                       font=dict(size=10, color="#666"), ax=50, ay=-40)
    fig.add_annotation(x=2024, y=270, text="Stratos opens<br>(Texas)",
                       showarrow=True, arrowhead=2, arrowcolor="#666",
                       font=dict(size=10, color="#666"), ax=50, ay=-30)

    fig.add_hline(y=100, line_dash="solid", line_color="#c0392b", line_width=1.5,
                  annotation_text="DOE $100/t target (2030)",
                  annotation_position="right",
                  annotation_font_color="#c0392b")

    fig.update_layout(
        height=420,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False, zeroline=False),
        yaxis=dict(title="Cost (USD per tonne CO₂)", showgrid=True,
                   gridcolor="#f0f0f0", zeroline=False, range=[0, 1100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=120, t=40, b=60),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888;'>
    Sources: <a href='https://www.iea.org/reports/direct-air-capture-2022' target='_blank'
    style='color:#2d6a2d;'>IEA Direct Air Capture 2022</a> ·
    <a href='https://www.energy.gov/fecm/carbon-negative-shot' target='_blank'
    style='color:#2d6a2d;'>DOE Carbon Negative Shot</a> ·
    <a href='https://www.cdr.fyi' target='_blank' style='color:#2d6a2d;'>CDR.fyi</a>
    </p>
    """, unsafe_allow_html=True)

    # ── Technology overview ───────────────────────────────────────
    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)
    st.markdown("## Four Pathways to Carbon Removal")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7; margin-bottom:1.5rem;'>
    This project tracks four distinct approaches to removing or avoiding CO₂ emissions.
    Each has different costs, scale potential, permanence, and co-benefits.
    Use the sidebar to explore each in depth.
    </p>
    """, unsafe_allow_html=True)

    technologies = [
        {
            "name": "Direct Air Capture",
            "track": "engineered",
            "cost": "$270 / tonne today",
            "potential": "50 Mt/yr by 2030 (DOE target)",
            "desc": "Machines pull CO₂ directly from ambient air using chemical sorbents. Location-independent, permanent, and verifiable — but currently expensive. Costs are falling fast.",
            "source_url": "https://www.iea.org/reports/direct-air-capture-2022",
            "source_label": "IEA DAC Report"
        },
        {
            "name": "Point-Source Capture",
            "track": "engineered",
            "cost": "$50–100 / tonne",
            "potential": "Hundreds of Mt/yr from industry",
            "desc": "Captures CO₂ at industrial sources — power plants, cement factories, steel mills — where CO₂ concentrations are 250× higher than air. Cheaper than DAC but prevents rather than removes historical emissions.",
            "source_url": "https://www.iea.org/reports/world-energy-outlook-2023",
            "source_label": "IEA World Energy Outlook"
        },
        {
            "name": "Urban Forestry",
            "track": "nature",
            "cost": "$29–48 / tonne",
            "potential": "26–45 Mt/yr nationally",
            "desc": "City tree canopy sequesters carbon while also reducing urban heat islands, improving air quality, managing stormwater, and providing mental health benefits. The IRA invested $1.5B in urban greening.",
            "source_url": "https://www.fs.usda.gov/managing-land/urban-forests/analytics",
            "source_label": "USFS Urban Forest Analytics"
        },
        {
            "name": "Reforestation",
            "track": "nature",
            "cost": "$10–15 / tonne",
            "potential": "750–950 Mt/yr US forest sink",
            "desc": "Restoring forest cover on previously forested US land. The cheapest pathway by far — but faces permanence risks from wildfire, drought, and land competition. US forests currently absorb ~12% of national emissions.",
            "source_url": "https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks",
            "source_label": "EPA GHG Inventory"
        }
    ]

    col1, col2 = st.columns(2)
    for i, tech in enumerate(technologies):
        col = col1 if i % 2 == 0 else col2
        tag_class = "tag-engineered" if tech["track"] == "engineered" else "tag-nature"
        tag_label = "Engineered" if tech["track"] == "engineered" else "Nature-Based"
        border_color = "#1565c0" if tech["track"] == "engineered" else "#2e7d32"
        with col:
            st.markdown(f"""
            <div style='border:1px solid #d4e4d4; padding:1.5rem; margin-bottom:1rem;
                        border-top: 3px solid {border_color};'>
                <span class='tag {tag_class}'>{tag_label}</span>
                <div style='font-family: DM Serif Display, serif; font-size:1.3rem;
                            margin: 0.7rem 0 0.3rem 0;'>{tech["name"]}</div>
                <div style='font-size:0.85rem; color:#555; line-height:1.6;
                            margin-bottom:1rem;'>{tech["desc"]}</div>
                <div style='display:flex; gap:2rem; margin-bottom:0.8rem;'>
                    <div>
                        <div style='font-size:0.7rem; font-weight:600; letter-spacing:0.1em;
                                    text-transform:uppercase; color:#5a7a5a;'>Cost</div>
                        <div style='font-family: DM Mono, monospace; font-size:0.9rem;
                                    color:#0f1f0f;'>{tech["cost"]}</div>
                    </div>
                    <div>
                        <div style='font-size:0.7rem; font-weight:600; letter-spacing:0.1em;
                                    text-transform:uppercase; color:#5a7a5a;'>Potential</div>
                        <div style='font-family: DM Mono, monospace; font-size:0.9rem;
                                    color:#0f1f0f;'>{tech["potential"]}</div>
                    </div>
                </div>
                <a href='{tech["source_url"]}' target='_blank'
                   style='font-size:0.75rem; color:#5a7a5a; text-decoration:none;'>
                   Source: {tech["source_label"]} →</a>
            </div>
            """, unsafe_allow_html=True)
