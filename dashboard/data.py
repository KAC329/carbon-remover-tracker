"""
dashboard/data.py
Cached database queries for the dashboard.
Using st.cache_data so queries only run once per session.
"""

import streamlit as st
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import get_engine


@st.cache_data
def get_dac_costs():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT cm.year, cm.cost_per_tonne_co2_usd as cost,
                   cm.cost_low_usd as cost_low, cm.cost_high_usd as cost_high,
                   cm.cost_type
            FROM cost_metrics cm
            JOIN technology_categories tc ON tc.id = cm.technology_id
            WHERE tc.slug = 'dac'
            ORDER BY cm.year
        """, conn)


@st.cache_data
def get_all_costs():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT tc.name, tc.slug, tc.track,
                   cm.year, cm.cost_per_tonne_co2_usd as cost,
                   cm.cost_low_usd as cost_low, cm.cost_high_usd as cost_high,
                   cm.cost_type
            FROM cost_metrics cm
            JOIN technology_categories tc ON tc.id = cm.technology_id
            ORDER BY tc.name, cm.year
        """, conn)


@st.cache_data
def get_deployment():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT tc.name, tc.slug, tc.track,
                   dm.year, dm.capacity_mtco2_yr,
                   dm.canopy_cover_pct, dm.area_hectares
            FROM deployment_metrics dm
            JOIN technology_categories tc ON tc.id = dm.technology_id
            JOIN geographies g ON g.id = dm.geography_id
            WHERE g.name = 'United States'
            ORDER BY tc.name, dm.year
        """, conn)


@st.cache_data
def get_forecasts():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT tc.name, tc.slug, tc.track,
                   fr.model_name, fr.forecast_year as year,
                   fr.predicted_cost_usd as cost,
                   fr.predicted_capacity_mt as capacity,
                   fr.ci_lower, fr.ci_upper
            FROM forecast_results fr
            JOIN technology_categories tc ON tc.id = fr.technology_id
            ORDER BY tc.name, fr.model_name, fr.forecast_year
        """, conn)


@st.cache_data
def get_esg_data():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT ticker, company_name, year,
                   esg_score, co2_total, co2_scope1, co2_scope2, co2_scope3
            FROM esg_company_data
            WHERE co2_total IS NOT NULL
            ORDER BY ticker, year
        """, conn)


@st.cache_data
def get_carbon_prices():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT tc.name, tc.slug,
                   cp.date, cp.price_per_tonne_usd as price,
                   cp.price_low_usd as price_low,
                   cp.price_high_usd as price_high,
                   cp.credit_type, cp.registry
            FROM carbon_credit_prices cp
            JOIN technology_categories tc ON tc.id = cp.technology_id
            ORDER BY tc.name, cp.date
        """, conn)


@st.cache_data
def get_investment_flows():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT tc.name, tc.slug,
                   inv.year, inv.amount_usd_millions,
                   inv.funder_type, inv.program_name,
                   inv.announced_vs_deployed
            FROM investment_flows inv
            JOIN technology_categories tc ON tc.id = inv.technology_id
            ORDER BY tc.name, inv.year
        """, conn)
