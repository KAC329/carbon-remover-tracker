"""
pipeline/extractors/lseg_esg.py

Extractor for LSEG (Refinitiv) ESG data downloaded from WRDS.
Reads the long-format CSV and pivots it into one row per company per year.

Source: WRDS tr_esg.esgenvdatapoint
File:   data/raw/lseg_esg_raw.csv
"""

import pandas as pd
import os
from .base import BaseExtractor


class LSEGESGExtractor(BaseExtractor):
    source_name = "LSEG ESG Data (WRDS tr_esg)"

    # Map WRDS fieldnames to our clean column names
    FIELD_MAP = {
        "ESGScore":                               "esg_score",
        "ESGCombinedScore":                       "esg_combined_score",
        "CO2EquivalentsEmissionTotal":            "co2_total",
        "CO2EquivalentsEmissionDirectScope1":     "co2_scope1",
        "CO2EquivalentsEmissionIndirectScope2":   "co2_scope2",
        "CO2EquivalentsEmissionIndirectScope3":   "co2_scope3",
        "CarbonOffsetsCredits":                   "carbon_offsets",
        "EmissionReductionTargetPercentage":      "emission_reduction_target",
        "EmissionReductionTargetYear":            "emission_reduction_year",
    }

    # ESG scores come as letter grades (A+, B-, etc.) — map to numeric
    ESG_GRADE_MAP = {
        "A+": 1.00, "A":  0.95, "A-": 0.90,
        "B+": 0.80, "B":  0.75, "B-": 0.70,
        "C+": 0.60, "C":  0.55, "C-": 0.50,
        "D+": 0.40, "D":  0.35, "D-": 0.30,
    }

    def __init__(self, filepath: str = "data/raw/lseg_esg_raw.csv"):
        self.filepath = filepath

    def extract(self) -> pd.DataFrame:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"ESG data file not found: {self.filepath}")

        raw = pd.read_csv(self.filepath)

        # Filter to only the fields we care about
        raw = raw[raw["fieldname"].isin(self.FIELD_MAP.keys())].copy()

        # Pivot: one row per (ticker, year), one column per field
        pivot = raw.pivot_table(
            index=["ticker", "comname", "year"],
            columns="fieldname",
            values="value",
            aggfunc="first"
        ).reset_index()

        # Flatten column names
        pivot.columns.name = None

        # Rename columns to our clean names
        rename = {"ticker": "ticker", "comname": "company_name", "year": "year"}
        rename.update({k: v for k, v in self.FIELD_MAP.items() if k in pivot.columns})
        pivot = pivot.rename(columns=rename)

        # Convert ESG letter grades to numeric using valuescore instead
        # Re-merge valuescore for ESGScore
        esg_scores = raw[raw["fieldname"] == "ESGScore"][["ticker", "year", "valuescore"]].copy()
        esg_scores = esg_scores.rename(columns={"valuescore": "esg_score_numeric"})
        esg_combined = raw[raw["fieldname"] == "ESGCombinedScore"][["ticker", "year", "valuescore"]].copy()
        esg_combined = esg_combined.rename(columns={"valuescore": "esg_combined_numeric"})

        pivot = pivot.merge(esg_scores, on=["ticker", "year"], how="left")
        pivot = pivot.merge(esg_combined, on=["ticker", "year"], how="left")

        # Use numeric scores (0-1 scale) instead of letter grades
        pivot["esg_score"] = pd.to_numeric(pivot["esg_score_numeric"], errors="coerce")
        pivot["esg_combined_score"] = pd.to_numeric(pivot["esg_combined_numeric"], errors="coerce")

        # Convert numeric fields
        numeric_cols = ["co2_total", "co2_scope1", "co2_scope2", "co2_scope3",
                        "carbon_offsets", "emission_reduction_target", "emission_reduction_year"]
        for col in numeric_cols:
            if col in pivot.columns:
                pivot[col] = pd.to_numeric(pivot[col], errors="coerce")

        pivot["year"] = pivot["year"].astype(int)

        # Keep only the columns we need
        keep = ["ticker", "company_name", "year", "esg_score", "esg_combined_score",
                "co2_total", "co2_scope1", "co2_scope2", "co2_scope3",
                "carbon_offsets", "emission_reduction_target", "emission_reduction_year"]
        keep = [c for c in keep if c in pivot.columns]
        pivot = pivot[keep]

        self.validate(pivot, ["ticker", "year", "esg_score"])
        return pivot
