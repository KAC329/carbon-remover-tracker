"""
forecasting/run_forecasts.py

Pulls historical data from PostgreSQL, runs forecasting models,
and writes predictions back to the forecast_results table.

Models:
  - Wright's Law (learning curve) for DAC cost trajectory
  - Logistic growth for urban forestry and reforestation deployment

Usage:
    python -m forecasting.run_forecasts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sqlalchemy import text
from db.connection import get_engine
from forecasting.cost_curves import (
    DAC_CONSERVATIVE, DAC_OPTIMISTIC,
    REFORESTATION_LOGISTIC, URBAN_FORESTRY_LOGISTIC
)

TARGET_YEARS = list(range(2024, 2051))


def get_ids(engine):
    """Fetch technology and geography IDs we need."""
    with engine.connect() as conn:
        techs = pd.read_sql("SELECT id, slug FROM technology_categories", conn)
        geos  = pd.read_sql("SELECT id, name FROM geographies", conn)

    tech_map = dict(zip(techs["slug"], techs["id"]))
    geo_map  = dict(zip(geos["name"], geos["id"]))
    return tech_map, geo_map


def write_forecast(engine, rows: list[dict]):
    """Upsert forecast rows into forecast_results table."""
    with engine.begin() as conn:
        for row in rows:
            conn.execute(text("""
                INSERT INTO forecast_results
                    (technology_id, geography_id, model_name, forecast_year,
                     predicted_cost_usd, predicted_capacity_mt, predicted_score,
                     ci_lower, ci_upper)
                VALUES
                    (:tech_id, :geo_id, :model, :year,
                     :cost, :capacity, :score,
                     :ci_lower, :ci_upper)
                ON CONFLICT (technology_id, geography_id, model_name, forecast_year)
                DO UPDATE SET
                    predicted_cost_usd    = EXCLUDED.predicted_cost_usd,
                    predicted_capacity_mt = EXCLUDED.predicted_capacity_mt,
                    predicted_score       = EXCLUDED.predicted_score,
                    ci_lower              = EXCLUDED.ci_lower,
                    ci_upper              = EXCLUDED.ci_upper,
                    run_at                = NOW()
            """), row)
    print(f"✓ Wrote {len(rows)} forecast rows to database.")


# ------------------------------------------------------------------
# Model 1: Wright's Law — DAC cost forecast
# ------------------------------------------------------------------

def run_dac_wrights_law(engine, tech_map, geo_map):
    print("\n── Wright's Law: DAC Cost Forecast ─────────────")

    # Pull historical DAC deployment from DB
    with engine.connect() as conn:
        deploy_df = pd.read_sql("""
            SELECT dm.year, dm.capacity_mtco2_yr
            FROM deployment_metrics dm
            JOIN technology_categories tc ON tc.id = dm.technology_id
            JOIN geographies g ON g.id = dm.geography_id
            WHERE tc.slug = 'dac'
              AND g.name = 'United States'
              AND dm.capacity_mtco2_yr IS NOT NULL
            ORDER BY dm.year
        """, conn)

    print(f"  Historical deployment rows: {len(deploy_df)}")

    rows = []
    for label, model in [("wrights_law_conservative", DAC_CONSERVATIVE),
                          ("wrights_law_optimistic",   DAC_OPTIMISTIC)]:
        forecast_df = model.forecast(deploy_df, TARGET_YEARS, growth_rate=0.50)

        for _, row in forecast_df.iterrows():
            # Simple confidence interval: ±20% for conservative, ±15% for optimistic
            ci_pct = 0.20 if "conservative" in label else 0.15
            cost = row["predicted_cost_usd"]
            rows.append({
                "tech_id":  tech_map["dac"],
                "geo_id":   geo_map["United States"],
                "model":    label,
                "year":     int(row["year"]),
                "cost":     round(cost, 2),
                "capacity": round(row["annual_capacity_mt"], 4),
                "score":    None,
                "ci_lower": round(cost * (1 - ci_pct), 2),
                "ci_upper": round(cost * (1 + ci_pct), 2),
            })

        print(f"  {label}: {len(forecast_df)} years forecast")
        # Print a few key years
        key = forecast_df[forecast_df["year"].isin([2025, 2030, 2035, 2040, 2050])]
        print(key[["year", "predicted_cost_usd", "annual_capacity_mt"]].to_string(index=False))

    write_forecast(engine, rows)


# ------------------------------------------------------------------
# Model 2: Logistic Growth — Reforestation deployment
# ------------------------------------------------------------------

def run_reforestation_logistic(engine, tech_map, geo_map):
    print("\n── Logistic Growth: Reforestation Deployment ───")

    forecast_df = REFORESTATION_LOGISTIC.forecast(TARGET_YEARS)

    # Pull historical costs to use as cost estimate
    with engine.connect() as conn:
        cost_df = pd.read_sql("""
            SELECT cm.year, cm.cost_per_tonne_co2_usd
            FROM cost_metrics cm
            JOIN technology_categories tc ON tc.id = cm.technology_id
            WHERE tc.slug = 'reforestation'
            ORDER BY cm.year DESC
            LIMIT 1
        """, conn)

    latest_cost = float(cost_df["cost_per_tonne_co2_usd"].iloc[0]) if len(cost_df) > 0 else 10.5

    rows = []
    for _, row in forecast_df.iterrows():
        capacity = float(row["predicted_deployment"])
        rows.append({
            "tech_id":  tech_map["reforestation"],
            "geo_id":   geo_map["United States"],
            "model":    "logistic_growth",
            "year":     int(row["year"]),
            "cost":     latest_cost,
            "capacity": round(capacity, 4),
            "score":    None,
            "ci_lower": round(capacity * 0.85, 4),
            "ci_upper": round(capacity * 1.15, 4),
        })

    print(f"  Logistic growth: {len(forecast_df)} years forecast")
    key = forecast_df[forecast_df["year"].isin([2025, 2030, 2035, 2040, 2050])]
    print(key[["year", "predicted_deployment"]].to_string(index=False))

    write_forecast(engine, rows)


# ------------------------------------------------------------------
# Model 3: Logistic Growth — Urban forestry deployment
# ------------------------------------------------------------------

def run_urban_forestry_logistic(engine, tech_map, geo_map):
    print("\n── Logistic Growth: Urban Forestry Deployment ──")

    forecast_df = URBAN_FORESTRY_LOGISTIC.forecast(TARGET_YEARS)

    with engine.connect() as conn:
        cost_df = pd.read_sql("""
            SELECT cm.year, cm.cost_per_tonne_co2_usd
            FROM cost_metrics cm
            JOIN technology_categories tc ON tc.id = cm.technology_id
            WHERE tc.slug = 'urban_forestry'
            ORDER BY cm.year DESC
            LIMIT 1
        """, conn)

    latest_cost = float(cost_df["cost_per_tonne_co2_usd"].iloc[0]) if len(cost_df) > 0 else 29.0

    rows = []
    for _, row in forecast_df.iterrows():
        capacity = float(row["predicted_deployment"])
        rows.append({
            "tech_id":  tech_map["urban_forestry"],
            "geo_id":   geo_map["United States"],
            "model":    "logistic_growth",
            "year":     int(row["year"]),
            "cost":     latest_cost,
            "capacity": round(capacity, 4),
            "score":    None,
            "ci_lower": round(capacity * 0.85, 4),
            "ci_upper": round(capacity * 1.15, 4),
        })

    print(f"  Logistic growth: {len(forecast_df)} years forecast")
    key = forecast_df[forecast_df["year"].isin([2025, 2030, 2035, 2040, 2050])]
    print(key[["year", "predicted_deployment"]].to_string(index=False))

    write_forecast(engine, rows)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    print("=" * 50)
    print("  Carbon Removal Tracker — Forecasting")
    print("=" * 50)

    engine = get_engine()
    tech_map, geo_map = get_ids(engine)

    run_dac_wrights_law(engine, tech_map, geo_map)
    run_reforestation_logistic(engine, tech_map, geo_map)
    run_urban_forestry_logistic(engine, tech_map, geo_map)

    print("\n✓ All forecasts complete.")


if __name__ == "__main__":
    main()
