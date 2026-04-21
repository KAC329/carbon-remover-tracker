"""
pipeline/loaders/db_loader.py

Loads cleaned DataFrames from extractors into PostgreSQL.
Handles foreign key lookups so extractors can use human-readable names.
"""

import pandas as pd
from sqlalchemy import text
from db.connection import get_engine


class DBLoader:
    def __init__(self):
        self.engine = get_engine()
        self._tech_cache = {}
        self._geo_cache = {}
        self._source_cache = {}

    # ------------------------------------------------------------------
    # FK lookup helpers
    # ------------------------------------------------------------------

    def _get_tech_id(self, slug: str) -> int:
        if slug not in self._tech_cache:
            with self.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id FROM technology_categories WHERE slug = :s"),
                    {"s": slug}
                ).fetchone()
                if not row:
                    raise ValueError(f"Unknown technology slug: '{slug}'")
                self._tech_cache[slug] = row[0]
        return self._tech_cache[slug]

    def _get_geo_id(self, name: str) -> int:
        if name not in self._geo_cache:
            with self.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id FROM geographies WHERE name = :n"),
                    {"n": name}
                ).fetchone()
                if not row:
                    raise ValueError(f"Unknown geography: '{name}'")
                self._geo_cache[name] = row[0]
        return self._geo_cache[name]

    def _get_source_id(self, name: str) -> int | None:
        if name not in self._source_cache:
            with self.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT id FROM data_sources WHERE name = :n"),
                    {"n": name}
                ).fetchone()
                self._source_cache[name] = row[0] if row else None
        return self._source_cache[name]

    # ------------------------------------------------------------------
    # Loaders per table
    # ------------------------------------------------------------------

    def load_cost_metrics(self, df: pd.DataFrame) -> int:
        rows_loaded = 0
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text("""
                    INSERT INTO cost_metrics
                        (technology_id, geography_id, data_source_id, year,
                         cost_per_tonne_co2_usd, cost_low_usd, cost_high_usd,
                         cost_type, notes)
                    VALUES
                        (:tech_id, :geo_id, :src_id, :year,
                         :cost, :cost_low, :cost_high, :cost_type, :notes)
                    ON CONFLICT (technology_id, geography_id, year, cost_type, data_source_id)
                    DO UPDATE SET
                        cost_per_tonne_co2_usd = EXCLUDED.cost_per_tonne_co2_usd,
                        cost_low_usd = EXCLUDED.cost_low_usd,
                        cost_high_usd = EXCLUDED.cost_high_usd,
                        notes = EXCLUDED.notes
                """), {
                    "tech_id":    self._get_tech_id(row["technology_slug"]),
                    "geo_id":     self._get_geo_id(row["geography_name"]),
                    "src_id":     self._get_source_id(row.get("source_name", "")),
                    "year":       int(row["year"]),
                    "cost":       float(row["cost_per_tonne_co2_usd"]),
                    "cost_low":   float(row.get("cost_low_usd", 0)) or None,
                    "cost_high":  float(row.get("cost_high_usd", 0)) or None,
                    "cost_type":  row.get("cost_type", "levelized"),
                    "notes":      row.get("notes"),
                })
                rows_loaded += 1
        print(f"✓ Loaded {rows_loaded} rows → cost_metrics")
        return rows_loaded

    def load_deployment_metrics(self, df: pd.DataFrame) -> int:
        rows_loaded = 0
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text("""
                    INSERT INTO deployment_metrics
                        (technology_id, geography_id, data_source_id, year,
                         capacity_mtco2_yr, num_facilities,
                         canopy_cover_pct, area_hectares, notes)
                    VALUES
                        (:tech_id, :geo_id, :src_id, :year,
                         :capacity, :facilities,
                         :canopy, :area, :notes)
                    ON CONFLICT (technology_id, geography_id, year, data_source_id)
                    DO UPDATE SET
                        capacity_mtco2_yr = EXCLUDED.capacity_mtco2_yr,
                        num_facilities = EXCLUDED.num_facilities,
                        canopy_cover_pct = EXCLUDED.canopy_cover_pct
                """), {
                    "tech_id":    self._get_tech_id(row["technology_slug"]),
                    "geo_id":     self._get_geo_id(row["geography_name"]),
                    "src_id":     self._get_source_id(row.get("source_name", "")),
                    "year":       int(row["year"]),
                    "capacity":   float(row.get("capacity_mtco2_yr", 0)) or None,
                    "facilities": int(row["num_facilities"]) if pd.notna(row.get("num_facilities")) else None,
                    "canopy":     float(row["canopy_cover_pct"]) if pd.notna(row.get("canopy_cover_pct")) else None,
                    "area":       float(row["area_mha"]) * 1e6 if pd.notna(row.get("area_mha")) else None,
                    "notes":      row.get("notes"),
                })
                rows_loaded += 1
        print(f"✓ Loaded {rows_loaded} rows → deployment_metrics")
        return rows_loaded

    def load_carbon_credit_prices(self, df: pd.DataFrame) -> int:
        rows_loaded = 0
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text("""
                    INSERT INTO carbon_credit_prices
                        (technology_id, data_source_id, date,
                         price_per_tonne_usd, price_low_usd, price_high_usd,
                         registry, credit_type, notes)
                    VALUES
                        (:tech_id, :src_id, :date,
                         :price, :low, :high,
                         :registry, :credit_type, :notes)
                """), {
                    "tech_id":     self._get_tech_id(row["technology_slug"]),
                    "src_id":      self._get_source_id(row.get("source_name", "")),
                    "date":        row["date"],
                    "price":       float(row["price_per_tonne_usd"]),
                    "low":         float(row.get("price_low_usd", 0)) or None,
                    "high":        float(row.get("price_high_usd", 0)) or None,
                    "registry":    row.get("registry"),
                    "credit_type": row.get("credit_type"),
                    "notes":       row.get("notes"),
                })
                rows_loaded += 1
        print(f"✓ Loaded {rows_loaded} rows → carbon_credit_prices")
        return rows_loaded

    def load_investment_flows(self, df: pd.DataFrame) -> int:
        rows_loaded = 0
        with self.engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(text("""
                    INSERT INTO investment_flows
                        (technology_id, geography_id, data_source_id, year,
                         amount_usd_millions, funder_type, program_name,
                         announced_vs_deployed)
                    VALUES
                        (:tech_id, :geo_id, :src_id, :year,
                         :amount, :funder, :program, :status)
                """), {
                    "tech_id": self._get_tech_id(row["technology_slug"]),
                    "geo_id":  self._get_geo_id(row["geography_name"]),
                    "src_id":  self._get_source_id(row.get("source_name", "")),
                    "year":    int(row["year"]),
                    "amount":  float(row["amount_usd_millions"]),
                    "funder":  row.get("funder_type"),
                    "program": row.get("program_name"),
                    "status":  row.get("announced_vs_deployed"),
                })
                rows_loaded += 1
        print(f"✓ Loaded {rows_loaded} rows → investment_flows")
        return rows_loaded
