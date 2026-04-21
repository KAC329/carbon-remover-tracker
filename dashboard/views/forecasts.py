"""
dashboard/pages/forecasts.py
Forecasts page — technical depth.
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
        Two models: Wright's Law learning curves for DAC cost,
        and logistic S-curve growth for nature-based deployment.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    forecasts = get_forecasts()
    dac_hist = get_dac_costs()
    deploy_hist = get_deployment()

    # ── DAC Cost Forecast ─────────────────────────────────────────
    st.markdown("## DAC Cost Trajectory — Wright's Law")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7;'>
    Wright's Law states that costs fall by a fixed % for every doubling of cumulative production.
    Conservative scenario assumes 15% learning rate; optimistic assumes 20% (matching solar PV's historical rate).
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        scenario = st.radio("Scenario", ["Both", "Conservative only", "Optimistic only"],
                            horizontal=True)
    with col2:
        show_ci = st.checkbox("Show confidence intervals", value=True)

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
            showlegend=False, hoverinfo="skip"
        ))

    if scenario != "Optimistic only":
        fig.add_trace(go.Scatter(
            x=dac_con["year"], y=dac_con["cost"],
            mode="lines", name="Conservative (15%)",
            line=dict(color="#2d6a2d", width=2, dash="dash")
        ))

    if scenario != "Conservative only":
        fig.add_trace(go.Scatter(
            x=dac_opt["year"], y=dac_opt["cost"],
            mode="lines", name="Optimistic (20%)",
            line=dict(color="#4CAF50", width=2, dash="dot")
        ))

    fig.add_trace(go.Scatter(
        x=hist["year"], y=hist["cost"],
        mode="lines+markers", name="Historical",
        line=dict(color="#0f1f0f", width=3),
        marker=dict(size=7)
    ))

    fig.add_hline(y=100, line_dash="solid", line_color="#c0392b", line_width=1.5,
                  annotation_text="DOE $100/t target",
                  annotation_position="right",
                  annotation_font_color="#c0392b")

    fig.update_layout(
        height=400,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="USD / tonne CO₂", showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Key milestones table
    milestones = pd.concat([
        dac_con[dac_con["year"].isin([2025,2030,2035,2040,2050])][["year","cost","capacity"]].assign(scenario="Conservative"),
        dac_opt[dac_opt["year"].isin([2025,2030,2035,2040,2050])][["year","cost","capacity"]].assign(scenario="Optimistic")
    ])
    milestones.columns = ["Year", "Cost ($/t)", "Capacity (MtCO₂/yr)", "Scenario"]
    milestones["Cost ($/t)"] = milestones["Cost ($/t)"].round(2)
    milestones["Year"] = milestones["Year"].astype(int)
    milestones["Year"] = milestones["Year"].astype(str)
    milestones["Capacity (MtCO₂/yr)"] = milestones["Capacity (MtCO₂/yr)"].round(4)

    with st.expander("View milestone table"):
        st.dataframe(milestones, use_container_width=True, hide_index=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Nature-Based Deployment ───────────────────────────────────
    st.markdown("## Nature-Based Deployment — Logistic Growth")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7;'>
    Nature-based deployment follows an S-curve: slow start, rapid middle growth,
    then leveling off at a carrying capacity defined by available land and policy support.
    </p>
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
        mode="lines", name="Reforestation (forecast)",
        line=dict(color="#2d6a2d", width=2, dash="dash")
    ))
    fig2.add_trace(go.Scatter(
        x=reforest_hist["year"], y=reforest_hist["capacity_mtco2_yr"],
        mode="lines+markers", name="Reforestation (historical)",
        line=dict(color="#0f1f0f", width=2.5),
        marker=dict(size=6)
    ))
    fig2.add_trace(go.Scatter(
        x=urban_fc["year"], y=urban_fc["capacity"],
        mode="lines", name="Urban Forestry (forecast)",
        line=dict(color="#4CAF50", width=2, dash="dot")
    ))
    fig2.add_trace(go.Scatter(
        x=urban_hist[urban_hist["capacity_mtco2_yr"].notna()]["year"],
        y=urban_hist[urban_hist["capacity_mtco2_yr"].notna()]["capacity_mtco2_yr"],
        mode="lines+markers", name="Urban Forestry (historical)",
        line=dict(color="#1b5e20", width=2.5),
        marker=dict(size=6)
    ))

    fig2.update_layout(
        height=400,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="MtCO₂ sequestered per year",
                   showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Model explainer ───────────────────────────────────────────
    st.markdown("## About the Models")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; border-top:3px solid #1565c0; padding:1.5rem;'>
            <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em;
                        text-transform:uppercase; color:#1565c0;'>Engineered</div>
            <div style='font-family: DM Serif Display, serif; font-size:1.2rem;
                        margin:0.5rem 0;'>Wright's Law</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                Cost = C₀ × (x / x₀)^(−b), where b = log₂(1 − learning_rate).
                For every doubling of cumulative DAC capacity, costs fall by the learning rate %.
                Validated across solar PV, wind, and lithium-ion batteries.
            </div>
            <div style='font-family: DM Mono, monospace; font-size:0.8rem;
                        background:#f7f9f7; padding:0.8rem; margin-top:1rem; color:#333;'>
                Conservative: 15% / doubling<br>
                Optimistic: 20% / doubling
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='border:1px solid #d4e4d4; border-top:3px solid #2e7d32; padding:1.5rem;'>
            <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em;
                        text-transform:uppercase; color:#2e7d32;'>Nature-Based</div>
            <div style='font-family: DM Serif Display, serif; font-size:1.2rem;
                        margin:0.5rem 0;'>Logistic Growth</div>
            <div style='font-size:0.85rem; color:#555; line-height:1.7;'>
                C(t) = K / (1 + exp(−r(t − t₀))).
                Growth follows an S-curve bounded by a carrying capacity K —
                the maximum achievable deployment given land and policy constraints.
            </div>
            <div style='font-family: DM Mono, monospace; font-size:0.8rem;
                        background:#f7f9f7; padding:0.8rem; margin-top:1rem; color:#333;'>
                Reforestation K: 950 MtCO₂/yr<br>
                Urban Forestry K: 45 MtCO₂/yr
            </div>
        </div>
        """, unsafe_allow_html=True)
