"""
dashboard/views/esg.py
ESG vs Reality page — with full context, annotations, takeaways, and sources.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_esg_data, get_esg_commitments


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

COMPANY_DESCRIPTIONS = {
    "OXY":   "Occidental Petroleum — operates Stratos, the world's largest DAC facility (Texas)",
    "MSFT":  "Microsoft — committed carbon negative by 2030; largest corporate DAC buyer",
    "GOOGL": "Alphabet/Google — $200M+ in carbon removal purchases; major CDR investor",
    "AMZN":  "Amazon — The Climate Pledge; largest nature-based credit buyer",
    "AAPL":  "Apple — significant reforestation investments; reports carbon neutrality for operations",
    "JPM":   "JPMorgan Chase — largest US bank; finances both fossil fuels and clean energy",
    "XOM":   "ExxonMobil — largest US oil company by emissions; CCS investments in progress",
    "CVX":   "Chevron — major US oil and gas company; carbon capture commitments",
    "SHOP":  "Shopify — co-founded Frontier, a $925M advance market commitment for CDR",
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
        ESG scores are used by investors to assess how seriously a company takes
        environmental, social, and governance issues. But do companies with high ESG scores
        actually emit less carbon? We use institutional ESG data from
        <a href='https://www.lseg.com/en/data-analytics/sustainable-finance/esg-scores'
        target='_blank' style='color:#2d6a2d;'>LSEG (formerly Refinitiv)</a> — the same
        data used by hedge funds and asset managers — to find out.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    df = get_esg_data()
    df["role"] = df["ticker"].map(COMPANY_ROLES)
    df["color"] = df["role"].map(COLORS)

    # Get commitments data for bubble sizing
    commitments = get_esg_commitments()
    avg_offsets = commitments.groupby("ticker")["carbon_offsets_t"].mean().reset_index()
    avg_offsets.columns = ["ticker", "avg_offsets_t"]

    # ── Glossary ──────────────────────────────────────────────────
    with st.expander("📖 Glossary — abbreviations and terms used on this page"):
        st.markdown("""
        | Term | Definition |
        |---|---|
        | **ESG Score** | Environmental, Social, and Governance score — a 0–1 rating of a company's sustainability practices, assigned by LSEG based on reported data |
        | **ESG Combined Score** | A blended score that also factors in public controversy incidents (scandals, lawsuits, etc.) |
        | **CO₂ total (Mt)** | Total greenhouse gas emissions in megatonnes of CO₂ equivalent — includes all gases converted to a common unit |
        | **Scope 1** | Direct emissions from company-owned operations (e.g. burning fuel in factories or vehicles) |
        | **Scope 2** | Indirect emissions from purchased electricity and heat |
        | **Scope 3** | All other indirect emissions across the value chain — suppliers, customers, business travel, product use |
        | **CDR** | Carbon Dioxide Removal — any process that actively removes CO₂ from the atmosphere |
        | **DAC** | Direct Air Capture — mechanical systems that pull CO₂ from ambient air |
        | **VCM** | Voluntary Carbon Market — where companies buy carbon credits to offset emissions |
        | **IRA** | Inflation Reduction Act (2022) — US federal law allocating billions to clean energy and carbon removal |
        """)

    # ── Core finding ──────────────────────────────────────────────
    st.markdown("""
    <div class='insight-box'>
        <p>"Microsoft and Google — the two highest ESG scorers in this dataset —
        showed emissions increases of 231% and 158% respectively since 2018.
        The culprit: AI data center expansion. A high ESG score reflects
        how well a company reports and manages emissions — not necessarily
        whether those emissions are going down."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Company profiles ──────────────────────────────────────────
    st.markdown("## The Nine Companies")
    st.markdown("""
    <p style='color:#555; max-width:650px; line-height:1.7; margin-bottom:1rem;'>
    We selected nine US companies that represent different roles in the carbon removal
    ecosystem — from companies actively building removal infrastructure, to those buying
    credits, financing fossil fuels, or emitting at industrial scale.
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    role_colors = {"DAC Operator": "#2d6a2d", "CDR Buyer": "#4CAF50",
                   "Finance": "#1565c0", "Emitter": "#c0392b", "CDR Pioneer": "#f39c12"}

    for i, (ticker, desc) in enumerate(COMPANY_DESCRIPTIONS.items()):
        role = COMPANY_ROLES[ticker]
        color = role_colors[role]
        with cols[i % 3]:
            st.markdown(f"""
            <div style='border:1px solid #e0e0e0; border-top:3px solid {color};
                        padding:0.8rem; margin-bottom:0.8rem;'>
                <div style='font-family: DM Mono, monospace; font-size:1rem;
                            font-weight:600; color:#0f1f0f;'>{ticker}</div>
                <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.08em;
                            text-transform:uppercase; color:{color}; margin:0.2rem 0;'>{role}</div>
                <div style='font-size:0.78rem; color:#555; line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── ESG Score vs Average Emissions ────────────────────────────
    st.markdown("## Figure 1 — ESG Score vs. Total Emissions")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            Each bubble is one company. Its position on the horizontal axis shows its average
            <strong>ESG score</strong> (0 = worst, 1 = best) across 2018–2024. Its position on the
            vertical axis shows its average annual <strong>total CO₂ emissions</strong> in million tonnes.
            The <strong>size</strong> of the bubble represents average annual carbon offsets/credits purchased — bigger bubble means more carbon removal activity.
            <strong>Color</strong> indicates the company's role in the carbon removal ecosystem.
            <br><br>
            If ESG scores reflected real-world emissions, we'd expect a downward slope —
            high ESG scores on the right with low emissions at the bottom.
            That's not what we see.
        </p>
    </div>
    """, unsafe_allow_html=True)

    summary = df.groupby(["ticker", "role"]).agg(
        avg_esg=("esg_score", "mean"),
        avg_co2=("co2_total", "mean"),
        company_name=("company_name", "first")
    ).reset_index()
    summary = summary.merge(avg_offsets, on="ticker", how="left")
    summary["avg_offsets_t"] = summary["avg_offsets_t"].fillna(0)
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
                size=sub["avg_offsets_t"].apply(lambda x: max(10, min(60, (x / 5e6) * 50 + 10))),
                color=COLORS[role],
                opacity=0.85,
                line=dict(width=1.5, color="white")
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Avg ESG Score: %{x:.3f} (0=worst, 1=best)<br>"
                "Avg Annual CO₂: %{y:.1f} million tonnes<br>"
                "Avg Annual Carbon Offsets: " + sub["avg_offsets_t"].apply(lambda x: f"{x:,.0f} tonnes").iloc[0] + "<br>"
                f"Role: {role}<extra></extra>"
            )
        ))

    # Annotations for key outliers
    fig.add_annotation(x=0.91, y=6, text="Highest ESG score,<br>but emissions up 231%",
                       showarrow=True, arrowhead=2, arrowcolor="#555",
                       font=dict(size=10, color="#555"), ax=60, ay=40)
    fig.add_annotation(x=0.72, y=105, text="Low ESG, massive emissions<br>(~104Mt/yr avg)",
                       showarrow=True, arrowhead=2, arrowcolor="#c0392b",
                       font=dict(size=10, color="#c0392b"), ax=-80, ay=-30)
    fig.add_annotation(x=0.37, y=0.5, text="Tiny emissions but<br>low ESG — small company<br>reporting gap",
                       showarrow=True, arrowhead=2, arrowcolor="#f39c12",
                       font=dict(size=10, color="#888"), ax=70, ay=30)

    fig.update_layout(
        height=520,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Average ESG Score (0 = worst, 1 = best)", showgrid=True,
                   gridcolor="#f0f0f0", zeroline=False, range=[0.2, 1.05]),
        yaxis=dict(title="Average Annual CO₂ Emissions (million tonnes)",
                   showgrid=True, gridcolor="#f0f0f0", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=80, b=60),
    )

    st.markdown("""
    <p style='font-size:0.8rem; color:#777; font-style:italic; margin-bottom:0.3rem;'>
    Bubble size = average annual carbon offsets/credits purchased (larger bubble = more carbon removal activity). Hover over any bubble for exact figures.
    </p>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
        <p>"There is no clear relationship between ESG score and emissions level in this dataset.
        ExxonMobil (XOM) emits 18× more than Microsoft but has only a slightly lower ESG score.
        Shopify (SHOP) has the lowest ESG score but the smallest emissions — because it's a small
        company with less reporting infrastructure, not because it's a worse environmental actor."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888; margin-top:0.5rem;'>
    Source: <a href='https://www.lseg.com/en/data-analytics/sustainable-finance/esg-scores'
    target='_blank' style='color:#2d6a2d;'>LSEG ESG Scores (formerly Refinitiv)</a>,
    accessed via <a href='https://wrds-www.wharton.upenn.edu' target='_blank'
    style='color:#2d6a2d;'>Wharton Research Data Services (WRDS)</a>, 2018–2024.
    ESG scores normalized to 0–1 scale using LSEG valuescore field.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Emissions over time ───────────────────────────────────────
    st.markdown("## Figure 2 — Emissions Over Time")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            Annual total CO₂ emissions (in million tonnes) for each selected company from 2018 to 2024.
            Use the selector below to add or remove companies. The default view shows the four big tech
            companies — Microsoft, Google, Amazon, and Apple — all of which have made high-profile
            carbon removal commitments. Note how emissions trend upward for most of them despite
            these commitments. This reflects the gap between offsetting (buying credits) and
            actually reducing emissions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ticker_options = sorted(df["ticker"].unique())
    selected = st.multiselect(
        "Select companies to display",
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
                name=f"{ticker} ({role})",
                line=dict(color=color, width=2.5),
                marker=dict(size=6, color=color),
                hovertemplate=f"<b>{ticker}</b><br>Year: %{{x}}<br>Total CO₂: %{{y:.2f}} million tonnes<extra></extra>"
            ))

        # Add IRA annotation if years overlap
        fig2.add_vline(x=2022, line_dash="dot", line_color="#c0392b", line_width=1.5)
        fig2.add_annotation(x=2022, y=0.02, text="IRA signed<br>(Aug 2022)",
                           showarrow=False, font=dict(size=9, color="#c0392b"),
                           xanchor="left", yanchor="bottom", yref="paper")

        fig2.update_layout(
            height=400,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans", size=12, color="#333"),
            xaxis=dict(title="Year", showgrid=False, zeroline=False),
            yaxis=dict(title="Total CO₂ Emissions (million tonnes)",
                       showgrid=True, gridcolor="#f0f0f0", zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(l=60, r=40, t=60, b=60),
            hovermode="x unified"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <p style='font-size:0.78rem; color:#888; margin-top:0.5rem;'>
        Try adding XOM and CVX to compare tech company emissions against industrial emitters.
        The scale difference is stark.
        </p>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Emissions change table ────────────────────────────────────
    st.markdown("## Figure 3 — Emissions Change 2018–2024")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this table shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            Each row is one company, sorted by average ESG score (highest first).
            The <strong>% Change</strong> column shows how total CO₂ emissions changed from 2018 to the
            most recent year in our dataset. Red = emissions increased. Green = emissions decreased.
            The color gradient makes the direction immediately visible.
            <br><br>
            Note that the two companies with the <em>highest</em> ESG scores (MSFT, AMZN) also have
            some of the largest emissions <em>increases</em>. Meanwhile the industrial emitters
            (XOM, CVX) — despite lower ESG scores — show more modest emissions growth,
            partly because they started from a much higher base.
        </p>
    </div>
    """, unsafe_allow_html=True)

    change = df.groupby("ticker").apply(
        lambda x: pd.Series({
            "company": x["company_name"].iloc[0].title(),
            "role": x["role"].iloc[0],
            "esg_score": round(x["esg_score"].mean(), 3),
            "co2_2018": x[x["year"] == x["year"].min()]["co2_total"].values[0] / 1e6
                        if len(x[x["year"] == x["year"].min()]) > 0 else None,
            "co2_latest": x[x["year"] == x["year"].max()]["co2_total"].values[0] / 1e6
                          if len(x[x["year"] == x["year"].max()]) > 0 else None,
        })
    ).reset_index()

    change["pct_change"] = ((change["co2_latest"] - change["co2_2018"])
                             / change["co2_2018"] * 100).round(1)
    change = change.sort_values("esg_score", ascending=False)
    change.columns = ["Ticker", "Company", "Role", "Avg ESG Score (0–1)",
                      "CO₂ 2018 (Mt)", "CO₂ 2024 (Mt)", "% Change"]

    st.dataframe(
        change.style
              .background_gradient(subset=["% Change"], cmap="RdYlGn_r")
              .format({
                  "Avg ESG Score (0–1)": "{:.3f}",
                  "CO₂ 2018 (Mt)": "{:.2f}",
                  "CO₂ 2024 (Mt)": "{:.2f}",
                  "% Change": "{:+.1f}%"
              }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("""
    <div class='insight-box' style='margin-top:1.5rem;'>
        <p>"The data suggests ESG scores measure reporting quality and management systems —
        not emissions trajectories. Companies like Microsoft score highly because they
        have robust sustainability programs and transparent reporting. But their actual
        emissions have risen sharply as AI infrastructure demands more energy.
        This is the central tension in corporate climate commitments."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888; margin-top:1rem;'>
    Source: <a href='https://www.lseg.com/en/data-analytics/sustainable-finance/esg-scores'
    target='_blank' style='color:#2d6a2d;'>LSEG ESG Scores</a> via
    <a href='https://wrds-www.wharton.upenn.edu' target='_blank'
    style='color:#2d6a2d;'>WRDS</a> · Dataset covers 2018–2024 ·
    Emissions reported in metric tonnes CO₂ equivalent (tCO₂e), converted to million tonnes (Mt) for display ·
    % Change calculated from earliest to latest available year per company
    </p>
    """, unsafe_allow_html=True)
