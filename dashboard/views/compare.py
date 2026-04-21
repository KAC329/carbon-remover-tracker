"""
dashboard/views/compare.py
Compare Technologies page — with full context, annotations, takeaways, and sources.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dashboard.data import get_all_costs, get_deployment, get_carbon_prices, get_investment_flows


TECH_COLORS = {
    "Direct Air Capture":   "#1565c0",
    "Point-Source Capture": "#1976d2",
    "Urban Forestry":       "#2e7d32",
    "Reforestation":        "#4CAF50",
}


def render():
    st.markdown("""
    <h3>Compare Technologies</h3>
    <h1>Cost, scale, and market<br>across four pathways</h1>
    <p style='font-size:1.1rem; color:#444; max-width:650px; line-height:1.7; margin-top:1rem;'>
        Nature-based removal is cheap and already operating at scale.
        Engineered removal is expensive today but costs are falling rapidly —
        and unlike forests, it has no land constraint or permanence risk.
        The question is whether engineered costs fall fast enough to matter.
    </p>
    <hr class='section-divider'/>
    """, unsafe_allow_html=True)

    costs = get_all_costs()
    deploy = get_deployment()
    prices = get_carbon_prices()
    invest = get_investment_flows()

    # ── Glossary ──────────────────────────────────────────────────
    with st.expander("📖 Glossary — abbreviations used on this page"):
        st.markdown("""
        | Term | Definition |
        |---|---|
        | **DAC** | Direct Air Capture — machines that pull CO₂ from the air using chemical processes |
        | **Point-Source Capture** | Carbon capture at industrial sites (power plants, cement, steel) where CO₂ is highly concentrated |
        | **LCOE** | Levelized Cost of Energy — a standard way to compare energy costs across technologies |
        | **$/tCO₂** | US dollars per tonne of CO₂ removed or avoided |
        | **VCM** | Voluntary Carbon Market — where companies voluntarily buy carbon credits to offset emissions |
        | **Carbon credit** | A certificate representing one tonne of CO₂ removed or avoided |
        | **IRA** | Inflation Reduction Act (2022) — US law allocating ~$370B to clean energy and carbon removal |
        | **45Q** | A US tax credit of up to $180/tonne for geologically stored carbon — major DAC incentive |
        | **Permanence** | How long a carbon removal lasts — DAC removal is considered permanent; forest removal is not |
        """)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Cost comparison ───────────────────────────────────────────
    st.markdown("## Figure 1 — Cost of Carbon Removal Over Time")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            The cost in US dollars to remove or avoid one tonne of CO₂ for each of the four
            technology pathways, from historical data through projected costs.
            <strong>Note: this chart uses a logarithmic (log) scale on the vertical axis</strong> —
            each gridline represents a 10× increase, not a fixed dollar amount. This is necessary
            because the values span from ~$10/tonne (reforestation) to ~$1,000/tonne (early DAC),
            a 100× range that would be impossible to show clearly on a regular scale.
            <br><br>
            Solid lines = historical reported data. Dashed lines = projections.
            Blue tones = engineered removal. Green tones = nature-based removal.
            Sources: <a href='https://www.iea.org/reports/direct-air-capture-2022' target='_blank'
            style='color:#2d6a2d;'>IEA</a>,
            <a href='https://www.energy.gov/fecm/carbon-negative-shot' target='_blank'
            style='color:#2d6a2d;'>DOE</a>,
            <a href='https://www.fs.usda.gov/managing-land/urban-forests/analytics' target='_blank'
            style='color:#2d6a2d;'>USFS</a>,
            <a href='https://www.epa.gov/ghgemissions' target='_blank'
            style='color:#2d6a2d;'>EPA</a>.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
                legendgroup=tech,
                hovertemplate=f"<b>{tech}</b><br>Year: %{{x}}<br>Cost: $%{{y:,.0f}}/tCO₂<extra></extra>"
            ))
        if len(projected) > 0:
            fig.add_trace(go.Scatter(
                x=projected["year"], y=projected["cost"],
                mode="lines", name=f"{tech} (projected)",
                line=dict(color=color, width=1.5, dash="dash"),
                legendgroup=tech, showlegend=False,
                hovertemplate=f"<b>{tech} (projected)</b><br>Year: %{{x}}<br>Cost: $%{{y:,.0f}}/tCO₂<extra></extra>"
            ))

    # Key annotations
    fig.add_annotation(x=2010, y=1000, text="DAC: ~$1,000/t<br>in 2010",
                       showarrow=True, arrowhead=2, arrowcolor="#1565c0",
                       font=dict(size=10, color="#1565c0"), ax=60, ay=0)
    fig.add_annotation(x=2024, y=270, text="DAC today:<br>~$270/t",
                       showarrow=True, arrowhead=2, arrowcolor="#1565c0",
                       font=dict(size=10, color="#1565c0"), ax=60, ay=0)
    fig.add_annotation(x=2022, y=10, text="Reforestation:<br>~$10/t consistently",
                       showarrow=True, arrowhead=2, arrowcolor="#4CAF50",
                       font=dict(size=10, color="#4CAF50"), ax=0, ay=60)

    fig.update_layout(
        height=440,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Cost (USD per tonne CO₂)",
           showgrid=True, gridcolor="#f0f0f0",
           range=[0, 1100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=70, r=40, t=60, b=60),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
        <p>"Reforestation has been consistently cheap (~$10–15/tonne) for decades.
        DAC started at ~$1,000/tonne in 2010 and has fallen ~70% to ~$270/tonne today.
        The gap between them is still enormous — but the direction of travel for DAC is clear.
        Point-source industrial capture sits in the middle: cheaper than DAC because
        CO₂ concentrations at industrial sites are 250× higher than ambient air."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── Carbon credit prices ──────────────────────────────────────
    st.markdown("## Figure 2 — Voluntary Carbon Market (VCM) Prices")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            The price per tonne of CO₂ in the <strong>Voluntary Carbon Market (VCM)</strong> —
            the market where companies voluntarily purchase carbon credits to offset their emissions.
            Error bars show the reported price range (low to high) for each year.
            <br><br>
            There are two very different markets here. <strong>Nature-based credits</strong>
            (reforestation, urban forestry) trade at $5–25/tonne and have been in decline since
            a 2021–2022 peak driven by corporate net-zero announcements, followed by a correction
            after investigative reporting raised questions about the quality of some offset projects.
            <strong>DAC credits</strong> trade at $300–500/tonne — dramatically more expensive,
            but considered higher quality because the removal is permanent and verifiable.
            <br><br>
            Source: <a href='https://www.ecosystemmarketplace.com/carbon-markets/' target='_blank'
            style='color:#2d6a2d;'>Ecosystem Marketplace State of the Voluntary Carbon Markets</a>,
            <a href='https://www.cdr.fyi' target='_blank' style='color:#2d6a2d;'>CDR.fyi</a>.
        </p>
    </div>
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
                type="data", symmetric=False,
                array=sub["price_high"] - sub["price"],
                arrayminus=sub["price"] - sub["price_low"],
                visible=True, color=color, thickness=1
            ),
            hovertemplate=f"<b>{tech}</b><br>Date: %{{x}}<br>Price: $%{{y:,.0f}}/tCO₂<extra></extra>"
        ))

    # Key event annotations
    fig2.add_annotation(x="2021-12-31", y=11,
                       text="VCM boom:<br>corporate net-zero<br>commitments surge",
                       showarrow=True, arrowhead=2, arrowcolor="#555",
                       font=dict(size=9, color="#555"), ax=-80, ay=-50)
    fig2.add_annotation(x="2023-12-31", y=7.5,
                       text="VCM correction:<br>offset quality<br>concerns",
                       showarrow=True, arrowhead=2, arrowcolor="#c0392b",
                       font=dict(size=9, color="#c0392b"), ax=60, ay=-40)

    fig2.update_layout(
        height=420,
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="Price (USD per tonne CO₂)",
                   showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
        <p>"The 50× price gap between nature-based credits (~$7/t) and DAC credits (~$350/t)
        reflects the cost of permanence. A forest credit can be reversed by wildfire, drought,
        or land-use change. A DAC credit — CO₂ stored underground — cannot.
        As corporate buyers become more sophisticated, demand is shifting toward
        higher-quality, higher-permanence removal."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'/>", unsafe_allow_html=True)

    # ── IRA Investment flows ──────────────────────────────────────
    st.markdown("## Figure 3 — Investment Flows by Technology")

    st.markdown("""
    <div style='background:#f0f7f0; border-left:4px solid #2d6a2d; padding:1rem 1.5rem; margin-bottom:1.5rem;'>
        <div style='font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;
                    color:#2d6a2d; margin-bottom:0.4rem;'>What this chart shows</div>
        <p style='font-size:0.9rem; color:#333; line-height:1.7; margin:0;'>
            Total investment in each technology from 2022–2024, broken down by funder type.
            <strong>Federal</strong> = US government funding, primarily through the
            <a href='https://www.congress.gov/bill/117th-congress/house-bill/5376' target='_blank'
            style='color:#2d6a2d;'>Inflation Reduction Act (IRA)</a>.
            <strong>Private</strong> = corporate investments and advance market commitments
            (e.g. the <a href='https://frontierclimate.com' target='_blank' style='color:#2d6a2d;'>Frontier</a>
            $925M advance market commitment co-founded by Stripe, Google, Meta, and Shopify).
            <br><br>
            Note that some amounts are <em>announced</em> rather than deployed — meaning the money
            has been committed but not yet spent. IRA funding in particular is largely announced;
            actual deployment happens over several years.
            <br><br>
            Source: <a href='https://rhg.com/research/inflation-reduction-act/' target='_blank'
            style='color:#2d6a2d;'>Rhodium Group IRA Tracker</a>,
            <a href='https://www.energy.gov' target='_blank' style='color:#2d6a2d;'>DOE</a>
            program announcements.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>" + funder.title() + " investment: $%{y:,.0f}M<extra></extra>"
        ))

    fig3.update_layout(
        height=400,
        barmode="stack",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="DM Sans", size=12, color="#333"),
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Investment (USD millions)", showgrid=True, gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=60, b=60),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
        <p>"Point-source industrial capture received the most total investment (~$8B announced)
        because it is the most cost-competitive near-term option for large emitters.
        DAC received ~$4.8B — mostly federal IRA funding — reflecting the DOE's bet that
        costs will fall with scale. Nature-based solutions received ~$2.9B,
        split between reforestation and urban forestry programs."</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='font-size:0.78rem; color:#888; margin-top:0.5rem;'>
    Note: investment figures include both announced and deployed amounts from 2022–2024.
    IRA funding is largely announced; actual deployment occurs over multiple years.
    Private figures based on publicly disclosed commitments only — actual private investment
    is likely higher.
    </p>
    """, unsafe_allow_html=True)
