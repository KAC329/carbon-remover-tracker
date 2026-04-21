"""
dashboard/pages/esg.py
ESG vs Reality page — the financial angle.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_esg_data


# Company role labels
COMPANY_ROLES = {
    "OXY":   "DAC Operator",
    "MSFT":  "CDR Buyer",
    "GOOGL": "CDR Buyer",
    "AMZN":  "CDR Buyer",
    "AAPL":  "CDR Buyer",
    "JPM":   "Finance",
    "XOM":   "Emitter",
    "CVX":   "Emitter",
    "SHOP":  "CDR Pioneer",
}

COLORS = {
    "DAC Operator": "#2d6a2d",
    "CDR Buyer":    "#4CAF50",
    "Finance":      "#1565c0",
    "Emitter":      "#c0392b",
    "CDR Pioneer":  "#f39c12",
}


def render():
    st.markdown("""
    <h3>ESG vs Reality</h3>
    <h1>Does a high ESG score<br>mean lower emissions?</h1>
    <p style='font-size:1.1rem; color:#444; max-width:650px; line-height:1.7; margin-top:1rem;'>
        Using LSEG (Refinitiv) institutional ESG data for 9 major US companies
        involved in carbon removal — as operators, buyers, financiers, or emitters.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    df = get_esg_data()
    df["role"] = df["ticker"].map(COMPANY_ROLES)
    df["color"] = df["role"].map(COLORS)

    # ── Core finding ──────────────────────────────────────────────
    st.markdown("""
    <div class='insight-box'>
        <p>"Microsoft and Google — the two highest ESG scorers —
        showed emissions increases of 231% and 158% respectively since 2018.
        The culprit: AI data center expansion."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── ESG Score vs Average Emissions ────────────────────────────
    st.markdown("## ESG Score vs. Total Emissions")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7;'>
    Each bubble represents one company. Size = average annual CO₂ emissions.
    Color = role in the carbon removal ecosystem.
    </p>
    """, unsafe_allow_html=True)

    summary = df.groupby(["ticker", "role"]).agg(
        avg_esg=("esg_score", "mean"),
        avg_co2=("co2_total", "mean"),
        company_name=("company_name", "first")
    ).reset_index()
    summary["color"] = summary["role"].map(COLORS)
    summary["company_name"] = summary["company_name"].str.title()

    fig = go.Figure()

    for role in summary["role"].unique():
        sub = summary[summary["role"] == role]
        fig.add_trace(go.Scatter(
            x=sub["avg_esg"],
            y=sub["avg_co2"] / 1e6,
            mode="markers+text",
            name=role,
            text=sub["ticker"],
            textposition="top center",
            textfont=dict(family="DM Mono", size=11, color="#333"),
            marker=dict(
                size=sub["avg_co2"].apply(lambda x: max(12, min(60, x / 2e6 * 40))),
                color=COLORS[role],
                opacity=0.85,
                line=dict(width=1.5, color="white")
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "ESG Score: %{x:.3f}<br>"
                "Avg CO₂: %{y:.1f}M tonnes<br>"
                f"Role: {role}<extra></extra>"
            )
        ))

    fig.update_layout(
        height=480,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Average ESG Score (0–1)", showgrid=True,
                   gridcolor="#f0f0f0", zeroline=False, range=[0.2, 1.0]),
        yaxis=dict(title="Average Annual CO₂ (million tonnes)",
                   showgrid=True, gridcolor="#f0f0f0", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Emissions over time ───────────────────────────────────────
    st.markdown("## Emissions Over Time by Company")

    ticker_options = sorted(df["ticker"].unique())
    selected = st.multiselect(
        "Select companies",
        ticker_options,
        default=["MSFT", "GOOGL", "AMZN", "AAPL"]
    )

    if selected:
        filtered = df[df["ticker"].isin(selected)]
        fig2 = go.Figure()

        for ticker in selected:
            sub = filtered[filtered["ticker"] == ticker].sort_values("year")
            role = COMPANY_ROLES.get(ticker, "Other")
            color = COLORS.get(role, "#888")
            fig2.add_trace(go.Scatter(
                x=sub["year"],
                y=sub["co2_total"] / 1e6,
                mode="lines+markers",
                name=ticker,
                line=dict(color=color, width=2.5),
                marker=dict(size=6, color=color),
                hovertemplate=f"<b>{ticker}</b><br>Year: %{{x}}<br>CO₂: %{{y:.2f}}M tonnes<extra></extra>"
            ))

        fig2.update_layout(
            height=380,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="DM Sans", size=12, color="#333"),
            xaxis=dict(title="Year", showgrid=False, zeroline=False),
            yaxis=dict(title="Total CO₂ Emissions (million tonnes)",
                       showgrid=True, gridcolor="#f0f0f0", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=60, r=40, t=60, b=60),
            hovermode="x unified"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Emissions change table ────────────────────────────────────
    st.markdown("## Emissions Change 2018–2024")

    change = df.groupby("ticker").apply(
        lambda x: pd.Series({
            "company": x["company_name"].iloc[0].title(),
            "role": x["role"].iloc[0],
            "esg_score": round(x["esg_score"].mean(), 3),
            "co2_2018": x[x["year"] == x["year"].min()]["co2_total"].values[0] / 1e6 if len(x[x["year"] == x["year"].min()]) > 0 else None,
            "co2_latest": x[x["year"] == x["year"].max()]["co2_total"].values[0] / 1e6 if len(x[x["year"] == x["year"].max()]) > 0 else None,
        })
    ).reset_index()

    change["pct_change"] = ((change["co2_latest"] - change["co2_2018"]) / change["co2_2018"] * 100).round(1)
    change = change.sort_values("esg_score", ascending=False)
    change.columns = ["Ticker", "Company", "Role", "Avg ESG Score",
                      "CO₂ 2018 (Mt)", "CO₂ Latest (Mt)", "% Change"]

    st.dataframe(
        change.style.background_gradient(subset=["% Change"], cmap="RdYlGn_r")
                    .format({
                        "Avg ESG Score": "{:.3f}",
                        "CO₂ 2018 (Mt)": "{:.2f}",
                        "CO₂ Latest (Mt)": "{:.2f}",
                        "% Change": "{:+.1f}%"
                    }),
        use_container_width=True,
        hide_index=True
    )
