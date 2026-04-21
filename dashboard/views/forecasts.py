"""
dashboard/views/forecasts.py
Forecasts page — with full context, annotations, takeaways, and sources.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_forecasts, get_dac_costs, get_deployment


def render():
    st.markdown("""
    <h3>Forecasts</h3>
    <h1>Where are these technologies<br>headed by 2050?</h1>
    <p style='font-size:1.1rem; color:#444; max-width:650px; line-height:1.7; margin-top:1rem;'>
        Using two established forecasting models — Wright's Law for engineered removal
        and logistic growth for nature-based solutions — we project cost and deployment
        trajectories through 2050 under conservative and optimistic scenarios.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    forecasts = get_forecasts()
    dac_hist = get_dac_costs()
    deploy_hist = get_deployment()

    # ── GLOSSARY ──────────────────────────────────────────────────
    with st.expander("📖 Glossary — abbreviations used on this page"):
        st.markdown("""
        | Term | Definition |
        |---|---|
        | **DAC** | Direct Air Capture — mechanical systems that pull CO₂ from ambient air using chemical sorbents |
        | **MtCO₂/yr** | Megatonnes of CO₂ per year — one megatonne = one million tonnes |
        | **GtCO₂** | Gigatonnes of CO₂ — one gigatonne = one billion tonnes |
        | **$/tCO₂** | US dollars per tonne of CO₂ removed — the standard unit of carbon removal cost |
        | **Wright's Law** | A learning curve model: costs fall by a fixed % for every doubling of cumulative production |
        | **Learning rate** | The % cost reduction achieved per doubling of cumulative capacity |
        | **Logistic growth** | An S-curve model where growth starts slow, accelerates, then levels off at a maximum |
        | **Carrying capacity (K)** | The maximum deployment level a technology can reach given land, policy, and resource constraints |
        | **IRA** | Inflation Reduction Act (2022) — US federal law that allocated ~$5B to carbon removal programs |
        | **DOE** | US Department of Energy — set the $100/tCO₂ DAC cost target via the Carbon Negative Shot program |
        """)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── DAC Cost Forecast ─────────────────────────────────────────
    st.markdown("## Figure 1 — DAC Cost Trajectory")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            The black line shows the actual reported cost of Direct Air Capture (DAC) from 2010 to 2024,
            based on data from the IEA and DOE. The dashed lines show our model's projections forward to 2050
            under two scenarios. The red horizontal line is the US Department of Energy's official target of
            $100 per tonne of CO₂ by 2030 — set under the <a href='https://www.energy.gov/fecm/carbon-negative-shot'
            target='_blank' style='color:#2d6a2d;'>Carbon Negative Shot program</a>.
            The shaded band shows the uncertainty range around the conservative forecast.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        scenario = st.radio("Scenario", ["Both", "Conservative only", "Optimistic only"],
                            horizontal=True)
    with col2:
        show_ci = st.checkbox("Show uncertainty range", value=True)

    dac_con = forecasts[(forecasts["slug"] == "dac") &
                        (forecasts["model_name"] == "wrights_law_conservative")]
    dac_opt = forecasts[(forecasts["slug"] == "dac") &
                        (forecasts["model_name"] == "wrights_law_optimistic")]
    hist = dac_hist[dac_hist["cost_type"].isin(["levelized", "reported"])]

    fig = go.Figure()

    if show_ci and scenario != "Optimistic only":
        fig.add_trace(go.Scatter(
            x=list(dac_con["year"]) + list(dac_con["year"])[::-1],
            y=list(dac_con["ci_upper"]) + list(dac_con["ci_lower"])[::-1],
            fill="toself", fillcolor="rgba(45,106,45,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
            name="Uncertainty range"
        ))

    if scenario != "Optimistic only":
        fig.add_trace(go.Scatter(
            x=dac_con["year"], y=dac_con["cost"],
            mode="lines", name="Conservative scenario (15% learning rate)",
            line=dict(color="#2d6a2d", width=2, dash="dash")
        ))

    if scenario != "Conservative only":
        fig.add_trace(go.Scatter(
            x=dac_opt["year"], y=dac_opt["cost"],
            mode="lines", name="Optimistic scenario (20% learning rate — matches solar PV)",
            line=dict(color="#4CAF50", width=2, dash="dot")
        ))

    fig.add_trace(go.Scatter(
        x=hist["year"], y=hist["cost"],
        mode="lines+markers", name="Historical reported cost",
        line=dict(color="#0f1f0f", width=3),
        marker=dict(size=7)
    ))

    # Key event annotations
    fig.add_annotation(x=2021, y=400, text="Orca plant opens<br>(Iceland)", 
                       showarrow=True, arrowhead=2, arrowcolor="#666",
                       font=dict(size=10, color="#666"), ax=40, ay=-40)
    fig.add_annotation(x=2024, y=270, text="Stratos opens<br>(Texas, USA)",
                       showarrow=True, arrowhead=2, arrowcolor="#666",
                       font=dict(size=10, color="#666"), ax=40, ay=-40)
    fig.add_annotation(x=2022, y=350, text="IRA: $3.5B<br>DAC Hubs",
                       showarrow=True, arrowhead=2, arrowcolor="#c0392b",
                       font=dict(size=10, color="#c0392b"), ax=-50, ay=-50)

    fig.add_hline(y=100, line_dash="solid", line_color="#c0392b", line_width=1.5,
                  annotation_text="DOE $100/t target (2030)",
                  annotation_position="right",
                  annotation_font_color="#c0392b")

    fig.update_layout(
        height=440,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Cost (USD per tonne CO₂ removed)", showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=120, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Key takeaway
    st.markdown("""
    <div class='insight-box'>
        <p>"DAC costs have fallen ~70% since 2010. Our conservative model — based on the same
        learning curve that drove solar costs down 90% — suggests the DOE's $100/tonne target
        is achievable by 2030. The optimistic scenario, matching solar PV's historical learning rate,
        reaches $100/t even sooner and falls below $10/t by 2050."</p>
    </div>
    """, unsafe_allow_html=True)

    # Milestone table
    milestones = pd.concat([
        dac_con[dac_con["year"].isin([2025,2030,2035,2040,2050])][["year","cost","capacity"]].assign(scenario="Conservative"),
        dac_opt[dac_opt["year"].isin([2025,2030,2035,2040,2050])][["year","cost","capacity"]].assign(scenario="Optimistic")
    ])
    milestones.columns = ["Year", "Cost ($/tCO₂)", "Capacity (MtCO₂/yr)", "Scenario"]
    milestones["Cost ($/tCO₂)"] = milestones["Cost ($/tCO₂)"].round(2)
    milestones["Capacity (MtCO₂/yr)"] = milestones["Capacity (MtCO₂/yr)"].round(4)
    milestones["Year"] = milestones["Year"].astype(int).astype(str)

    with st.expander("View milestone projections table"):
        st.markdown("""
        <p style='font-size:0.85rem; color:#666; margin-bottom:0.5rem;'>
        Projected cost (USD per tonne CO₂) and annual removal capacity (megatonnes CO₂ per year)
        at key milestone years. Capacity assumes 50% annual growth in DAC deployment.
        </p>
        """, unsafe_allow_html=True)
        st.dataframe(milestones, use_container_width=True, hide_index=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888; margin-top:0.5rem;'>
    Sources: <a href='https://www.iea.org/reports/direct-air-capture-2022' target='_blank' style='color:#2d6a2d;'>IEA Direct Air Capture 2022</a> ·
    <a href='https://www.energy.gov/fecm/carbon-negative-shot' target='_blank' style='color:#2d6a2d;'>DOE Carbon Negative Shot</a> ·
    <a href='https://www.cdr.fyi' target='_blank' style='color:#2d6a2d;'>CDR.fyi deployment tracker</a> ·
    Wright (1936) learning curve model
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Nature-Based Deployment ───────────────────────────────────
    st.markdown("## Figure 2 — Nature-Based Carbon Removal Deployment")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            The solid lines show historical US carbon sequestration (absorption) by reforestation and urban forests,
            measured in megatonnes of CO₂ per year (MtCO₂/yr). The dashed lines show model projections forward
            to 2050. Unlike DAC, nature-based removal is already operating at large scale — US forests currently
            absorb ~750–800 MtCO₂/yr — but growth is constrained by available land and policy support.
            The curves level off at a "carrying capacity" — the estimated maximum achievable sequestration
            given these constraints.
            Data sources: <a href='https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks'
            target='_blank' style='color:#2d6a2d;'>EPA GHG Inventory</a> and
            <a href='https://www.fs.usda.gov/managing-land/urban-forests/analytics' target='_blank'
            style='color:#2d6a2d;'>USFS Urban Forest Analytics</a>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    reforest_fc = forecasts[(forecasts["slug"] == "reforestation") &
                            (forecasts["model_name"] == "logistic_growth")]
    urban_fc = forecasts[(forecasts["slug"] == "urban_forestry") &
                         (forecasts["model_name"] == "logistic_growth")]

    reforest_hist = deploy_hist[deploy_hist["slug"] == "reforestation"]
    urban_hist = deploy_hist[deploy_hist["slug"] == "urban_forestry"]

    fig2 = go.Figure()

    # Reforestation confidence band
    fig2.add_trace(go.Scatter(
        x=list(reforest_fc["year"]) + list(reforest_fc["year"])[::-1],
        y=list(reforest_fc["ci_upper"]) + list(reforest_fc["ci_lower"])[::-1],
        fill="toself", fillcolor="rgba(45,106,45,0.08)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip"
    ))

    fig2.add_trace(go.Scatter(
        x=reforest_fc["year"], y=reforest_fc["capacity"],
        mode="lines", name="Reforestation (projected)",
        line=dict(color="#2d6a2d", width=2, dash="dash")
    ))
    fig2.add_trace(go.Scatter(
        x=reforest_hist["year"], y=reforest_hist["capacity_mtco2_yr"],
        mode="lines+markers", name="Reforestation (historical, EPA)",
        line=dict(color="#0f1f0f", width=2.5),
        marker=dict(size=6)
    ))
    fig2.add_trace(go.Scatter(
        x=urban_fc["year"], y=urban_fc["capacity"],
        mode="lines", name="Urban Forestry (projected)",
        line=dict(color="#4CAF50", width=2, dash="dot")
    ))
    fig2.add_trace(go.Scatter(
        x=urban_hist[urban_hist["capacity_mtco2_yr"].notna()]["year"],
        y=urban_hist[urban_hist["capacity_mtco2_yr"].notna()]["capacity_mtco2_yr"],
        mode="lines+markers", name="Urban Forestry (historical, USFS)",
        line=dict(color="#1b5e20", width=2.5),
        marker=dict(size=6)
    ))

    # Key policy annotations
    fig2.add_annotation(x=2022, y=760, text="IRA: $1.5B reforestation<br>+ $1.5B urban forestry",
                       showarrow=True, arrowhead=2, arrowcolor="#c0392b",
                       font=dict(size=10, color="#c0392b"), ax=80, ay=-40)
    fig2.add_annotation(x=2020, y=755, text="Wildfire impacts<br>reduce sink",
                       showarrow=True, arrowhead=2, arrowcolor="#666",
                       font=dict(size=10, color="#666"), ax=-70, ay=-50)

    # Carrying capacity reference lines
    fig2.add_hline(y=950, line_dash="dot", line_color="#2d6a2d", line_width=1,
                  annotation_text="Reforestation max capacity (950 MtCO₂/yr)",
                  annotation_position="right", annotation_font_color="#2d6a2d",
                  annotation_font_size=10)
    fig2.add_hline(y=45, line_dash="dot", line_color="#4CAF50", line_width=1,
                  annotation_text="Urban forestry max capacity (45 MtCO₂/yr)",
                  annotation_position="right", annotation_font_color="#4CAF50",
                  annotation_font_size=10)

    fig2.update_layout(
        height=460,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Carbon sequestered (MtCO₂ per year)",
                   showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=160, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Key takeaway
    st.markdown("""
    <div class='insight-box'>
        <p>"US forests already absorb ~750 MtCO₂/yr — roughly 12% of total US emissions.
        IRA funding could grow this to ~900 MtCO₂/yr by 2035. But nature-based removal
        faces hard limits: land availability, wildfire risk, and drought. It is cheap and
        already operating at scale, but cannot grow indefinitely. Engineered removal has
        no such ceiling — only a cost barrier."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888; margin-top:0.5rem;'>
    Sources: <a href='https://www.epa.gov/ghgemissions/inventory-us-greenhouse-gas-emissions-and-sinks' target='_blank' style='color:#2d6a2d;'>EPA GHG Inventory (LULUCF chapter)</a> ·
    <a href='https://www.fs.usda.gov/managing-land/urban-forests/analytics' target='_blank' style='color:#2d6a2d;'>USFS Urban Forest Analytics (i-Tree)</a> ·
    <a href='https://www.ncasi.org' target='_blank' style='color:#2d6a2d;'>NCASI Forest Carbon Data</a> ·
    Bass (1969) logistic growth model
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Model explainer ───────────────────────────────────────────
    st.markdown("## How the Models Work")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7; margin-bottom:1.5rem;'>
    Each technology track uses a different forecasting model, chosen based on the
    underlying dynamics of how that technology grows and improves over time.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; border-top:3px solid #1565c0; padding:1.5rem;'>
            <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em;
                        text-transform:uppercase; color:#1565c0;'>Used for: Direct Air Capture</div>
            <div style='font-family: DM Serif Display, serif; font-size:1.2rem;
                        margin:0.5rem 0;'>Wright's Law</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                First described by Theodore Wright in 1936 studying aircraft manufacturing costs,
                Wright's Law states that for every doubling of cumulative production, costs fall
                by a fixed percentage called the <strong>learning rate</strong>.
                <br><br>
                <strong>Formula:</strong> Cost = C₀ × (x / x₀)^(−b),
                where b = log₂(1 − learning rate)
                <br><br>
                This model has been validated across solar panels (20% learning rate),
                wind turbines (12%), and lithium-ion batteries (18%). We apply it to DAC
                using a conservative 15% and optimistic 20% learning rate based on
                early deployment data and analogies to similar chemical processes.
            </div>
            <div style='font-family: DM Mono, monospace; font-size:0.8rem;
                        background:#f7f9f7; padding:0.8rem; margin-top:1rem; color:#333;'>
                Conservative scenario: 15% cost reduction per doubling<br>
                Optimistic scenario: 20% cost reduction per doubling<br>
                Reference: <a href='https://doi.org/10.2514/8.155' target='_blank' style='color:#1565c0;'>Wright (1936)</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; border-top:3px solid #2e7d32; padding:1.5rem;'>
            <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em;
                        text-transform:uppercase; color:#2e7d32;'>Used for: Reforestation & Urban Forestry</div>
            <div style='font-family: DM Serif Display, serif; font-size:1.2rem;
                        margin:0.5rem 0;'>Logistic Growth</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Nature-based deployment doesn't follow a cost curve — it's constrained by
                available land, institutional capacity, and policy support. These dynamics
                naturally produce an S-curve: slow initial growth, a period of rapid expansion,
                then leveling off as physical and policy limits are reached.
                <br><br>
                <strong>Formula:</strong> C(t) = K / (1 + exp(−r(t − t₀))),
                where K = carrying capacity, r = growth rate, t₀ = inflection year
                <br><br>
                Carrying capacities are set from published US technical potential estimates
                from the EPA and USFS.
            </div>
            <div style='font-family: DM Mono, monospace; font-size:0.8rem;
                        background:#f7f9f7; padding:0.8rem; margin-top:1rem; color:#333;'>
                Reforestation max capacity (K): 950 MtCO₂/yr<br>
                Urban Forestry max capacity (K): 45 MtCO₂/yr<br>
                Reference: <a href='https://doi.org/10.1287/mnsc.15.5.215' target='_blank' style='color:#2e7d32;'>Bass (1969)</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
