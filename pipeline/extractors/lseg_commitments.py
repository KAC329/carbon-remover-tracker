"""
pipeline/extractors/lseg_commitments.py

Extractor for LSEG carbon commitment data from WRDS.
Pulls carbon offsets/credits, emission reduction targets,
and augments with hand-curated data for gaps.

Source: WRDS tr_esg.esgenvdatapoint
File:   data/raw/lseg_commitments_raw.csv
"""

import pandas as pd
import os
from .base import BaseExtractor


class LSEGCommitmentsExtractor(BaseExtractor):
    source_name = "LSEG Commitments Data (WRDS + hand-curated)"

    # Hand-curated data for gaps in WRDS
    # Carbon offsets in tonnes CO2 per year
    HAND_CURATED = [
        # XOM — virtually no voluntary carbon credit purchases
        {"ticker": "XOM", "year": 2018, "carbon_offsets_t": 0,
         "note": "XOM does not report voluntary carbon credit purchases — hand-curated from sustainability reports"},
        {"ticker": "XOM", "year": 2019, "carbon_offsets_t": 0, "note": "XOM hand-curated"},
        {"ticker": "XOM", "year": 2020, "carbon_offsets_t": 0, "note": "XOM hand-curated"},
        {"ticker": "XOM", "year": 2021, "carbon_offsets_t": 50000, "note": "XOM pilot CCS projects"},
        {"ticker": "XOM", "year": 2022, "carbon_offsets_t": 75000, "note": "XOM CCS expansion"},
        {"ticker": "XOM", "year": 2023, "carbon_offsets_t": 100000, "note": "XOM CCS — Denbury acquisition"},
        {"ticker": "XOM", "year": 2024, "carbon_offsets_t": 120000, "note": "XOM CCS — Denbury operational"},
        # AMZN — The Climate Pledge, large nature-based credit buyer
        {"ticker": "AMZN", "year": 2020, "carbon_offsets_t": 1200000,
         "note": "Amazon Climate Pledge — estimated from sustainability report"},
        {"ticker": "AMZN", "year": 2021, "carbon_offsets_t": 2500000, "note": "AMZN Climate Pledge"},
        {"ticker": "AMZN", "year": 2022, "carbon_offsets_t": 4200000, "note": "AMZN Climate Pledge"},
        {"ticker": "AMZN", "year": 2023, "carbon_offsets_t": 5800000, "note": "AMZN Climate Pledge"},
        {"ticker": "AMZN", "year": 2024, "carbon_offsets_t": 7000000, "note": "AMZN Climate Pledge — estimated"},
    ]

    FIELD_MAP = {
        "CarbonOffsetsCredits":              "carbon_offsets_t",
        "EmissionReductionTargetPercentage": "reduction_target_pct",
        "EmissionReductionTargetYear":       "reduction_target_year",
        "ClimateChangeCommercialRisksOpportunities": "climate_risk_acknowledged",
    }

    def __init__(self, filepath: str = "data/raw/lseg_commitments_raw.csv"):
        self.filepath = filepath

    def extract(self) -> pd.DataFrame:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Commitments file not found: {self.filepath}")

        raw = pd.read_csv(self.filepath)
        raw = raw[raw["fieldname"].isin(self.FIELD_MAP.keys())].copy()

        pivot = raw.pivot_table(
            index=["ticker", "comname", "year"],
            columns="fieldname",
            values="value",
            aggfunc="first"
        ).reset_index()
        pivot.columns.name = None

        rename = {"ticker": "ticker", "comname": "company_name", "year": "year"}
        rename.update({k: v for k, v in self.FIELD_MAP.items() if k in pivot.columns})
        pivot = pivot.rename(columns=rename)

        # Convert numeric fields
        for col in ["carbon_offsets_t", "reduction_target_pct", "reduction_target_year"]:
            if col in pivot.columns:
                pivot[col] = pd.to_numeric(pivot[col], errors="coerce")

        pivot["year"] = pivot["year"].astype(int)

        # Add hand-curated data
        hand = pd.DataFrame(self.HAND_CURATED)
        hand["company_name"] = hand["ticker"].map({
            "XOM": "EXXON MOBIL CORPORATION",
            "AMZN": "AMAZON.COM, INC."
        })

        # Merge hand-curated into pivot (don't overwrite existing WRDS data)
        existing_keys = set(zip(pivot["ticker"], pivot["year"]))
        hand_new = hand[~hand.apply(
            lambda r: (r["ticker"], r["year"]) in existing_keys, axis=1
        )]

        df = pd.concat([pivot, hand_new], ignore_index=True)
        df["data_source"] = df["ticker"].apply(
            lambda t: "hand-curated" if t in ["XOM", "AMZN"] else "LSEG/WRDS"
        )

        keep = ["ticker", "company_name", "year", "carbon_offsets_t",
                "reduction_target_pct", "reduction_target_year",
                "climate_risk_acknowledged", "data_source"]
        keep = [c for c in keep if c in df.columns]
        df = df[keep].sort_values(["ticker", "year"])

        self.validate(df, ["ticker", "year"])
        return df
