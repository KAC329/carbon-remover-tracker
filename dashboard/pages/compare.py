"""
dashboard/pages/compare.py
Compare Technologies page.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_all_costs, get_deployment, get_carbon_prices, get_investment_flows


TECH_COLORS = {
    "Direct Air Capture":  "#1565c0",
    "Point-Source Capture": "#1976d2",
    "Urban Forestry":      "#2e7d32",
    "Reforestation":       "#4CAF50",
}


def render():
    st.markdown("""
    <h3>Compare Technologies</h3>
    <h1>Cost, scale, and market<br>across four pathways</h1>
    <p style='font-size:1.1rem; color:#444; max-width:650px; line-height:1.7; margin-top:1rem;'>
        Nature-based removal is cheap and already at scale.
        Engineered removal is expensive but falling fast — and is the only pathway
        that can scale beyond land constraints.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    costs = get_all_costs()
    deploy = get_deployment()
    prices = get_carbon_prices()
    invest = get_investment_flows()

    # ── Cost comparison ───────────────────────────────────────────
    st.markdown("## Cost of Removal Over Time")

    fig = go.Figure()
    for tech in costs["name"].unique():
        sub = costs[costs["name"] == tech].sort_values("year")
        historical = sub[sub["cost_type"].isin(["levelized", "reported"])]
        projected = sub[sub["cost_type"] == "projected"]
        color = TECH_COLORS.get(tech, "#888")

        if len(historical) > 0:
            fig.add_trace(go.Scatter(
                x=historical["year"], y=historical["cost"],
                mode="lines+markers", name=tech,
                line=dict(color=color, width=2.5),
                marker=dict(size=6),
                legendgroup=tech
            ))
        if len(projected) > 0:
            fig.add_trace(go.Scatter(
                x=projected["year"], y=projected["cost"],
                mode="lines", name=f"{tech} (projected)",
                line=dict(color=color, width=1.5, dash="dash"),
                legendgroup=tech, showlegend=False
            ))

    fig.update_layout(
        height=400,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="USD / tonne CO₂", showgrid=True, gridcolor="#f0f0f0",
                   type="log", title_text="USD / tonne CO₂ (log scale)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Carbon credit prices ──────────────────────────────────────
    st.markdown("## Voluntary Carbon Market Prices")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7;'>
    Nature-based credits trade at $5–25/tonne. DAC credits trade at $300–500/tonne.
    The spread reflects the cost of permanence — a DAC credit lasts forever;
    a forest credit depends on the forest surviving.
    </p>
    """, unsafe_allow_html=True)

    fig2 = go.Figure()
    for tech in prices["name"].unique():
        sub = prices[prices["name"] == tech].sort_values("date")
        color = TECH_COLORS.get(tech, "#888")
        fig2.add_trace(go.Scatter(
            x=sub["date"], y=sub["price"],
            mode="lines+markers", name=tech,
            line=dict(color=color, width=2.5),
            marker=dict(size=7),
            error_y=dict(
                type="data",
                symmetric=False,
                array=sub["price_high"] - sub["price"],
                arrayminus=sub["price"] - sub["price_low"],
                visible=True, color=color, thickness=1
            )
        ))

    fig2.update_layout(
        height=380,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="USD / tonne CO₂", showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── IRA Investment flows ──────────────────────────────────────
    st.markdown("## Federal & Private Investment (IRA + Private)")

    invest_summary = invest.groupby(["name", "funder_type", "announced_vs_deployed"])[
        "amount_usd_millions"].sum().reset_index()

    fig3 = go.Figure()
    funder_colors = {"federal": "#1565c0", "private": "#2e7d32", "vc": "#f39c12"}

    for funder in invest_summary["funder_type"].unique():
        sub = invest_summary[invest_summary["funder_type"] == funder]
        fig3.add_trace(go.Bar(
            x=sub["name"],
            y=sub["amount_usd_millions"],
            name=funder.title(),
            marker_color=funder_colors.get(funder, "#888"),
            text=sub["amount_usd_millions"].apply(lambda x: f"${x:,.0f}M"),
            textposition="auto"
        ))

    fig3.update_layout(
        height=380,
        barmode="stack",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="USD millions", showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    st.plotly_chart(fig3, use_container_width=True)
