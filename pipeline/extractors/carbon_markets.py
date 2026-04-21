"""
pipeline/extractors/carbon_markets.py

Voluntary carbon market (VCM) price data by credit type.
Source: Ecosystem Marketplace State of the Voluntary Carbon Markets reports,
        CarbonPlan CDR database, BloombergNEF.

Key insight: nature-based credits trade at $5-25/t while DAC credits
trade at $300-600/t — the spread tells the market's story.
"""

import pandas as pd
from .base import BaseExtractor


class CarbonCreditPriceExtractor(BaseExtractor):
    source_name = "Ecosystem Marketplace VCM Report 2023"

    # Annual average VCM prices by credit type
    # date = year-end snapshot, price in USD/tCO2
    RAW_DATA = [
        # date, technology_slug, credit_type, registry, price_ref, price_low, price_high, notes
        # --- Nature-based: Urban / Reforestation ---
        ("2018-12-31", "reforestation", "nature_based_removal", "Verra",
            5.5,  3.0,  9.0,  "REDD+ and ARR credits — EM 2019 report"),
        ("2019-12-31", "reforestation", "nature_based_removal", "Verra",
            5.8,  3.5,  9.5,  "EM 2020 report"),
        ("2020-12-31", "reforestation", "nature_based_removal", "Verra",
            6.2,  3.8, 10.0,  "EM 2021 report"),
        ("2021-12-31", "reforestation", "nature_based_removal", "Verra",
           11.0,  6.0, 18.0,  "VCM boom year — corporate net-zero demand surge"),
        ("2022-12-31", "reforestation", "nature_based_removal", "Verra",
           14.0,  7.0, 25.0,  "Peak VCM pricing before scandals"),
        ("2023-12-31", "reforestation", "nature_based_removal", "Verra",
            7.5,  4.0, 14.0,  "VCM correction after Guardian/Zeit integrity reporting"),
        ("2024-06-30", "reforestation", "nature_based_removal", "Verra",
            6.0,  3.0, 12.0,  "Continued market softness"),

        # --- Urban forestry credits (smaller, city-program based) ---
        ("2020-12-31", "urban_forestry", "nature_based_removal", "CAR",
           12.0,  8.0, 18.0,  "California Air Resources Board urban forestry protocol"),
        ("2021-12-31", "urban_forestry", "nature_based_removal", "CAR",
           15.0, 10.0, 22.0,  "Growing urban forestry credit market"),
        ("2022-12-31", "urban_forestry", "nature_based_removal", "CAR",
           18.0, 11.0, 28.0,  "Premium for co-benefits (air quality, heat island)"),
        ("2023-12-31", "urban_forestry", "nature_based_removal", "CAR",
           14.0,  9.0, 22.0,  "Slight pullback with broader VCM"),

        # --- DAC credits ---
        ("2021-12-31", "dac", "engineered_removal", "Puro.earth",
          450.0, 300.0, 700.0, "Early Climeworks Orca offtake agreements"),
        ("2022-12-31", "dac", "engineered_removal", "Puro.earth",
          400.0, 250.0, 600.0, "Stripe/Shopify advance market commitments"),
        ("2023-12-31", "dac", "engineered_removal", "Puro.earth",
          350.0, 200.0, 550.0, "Frontier $925M commitment driving price discovery"),
        ("2024-06-30", "dac", "engineered_removal", "Puro.earth",
          300.0, 150.0, 500.0, "Stratos operational; cost declining"),
    ]

    def extract(self) -> pd.DataFrame:
        df = pd.DataFrame(self.RAW_DATA, columns=[
            "date", "technology_slug", "credit_type", "registry",
            "price_per_tonne_usd", "price_low_usd", "price_high_usd", "notes"
        ])
        df["date"] = pd.to_datetime(df["date"])
        df["source_name"] = self.source_name

        self.validate(df, ["date", "technology_slug", "price_per_tonne_usd"])
        return df


class InvestmentFlowExtractor(BaseExtractor):
    source_name = "IRA Federal Funding Tracker"

    # Federal + major private investment flows in USD millions
    RAW_DATA = [
        # year, technology_slug, geography, amount_usd_mm, funder_type, program, announced_vs_deployed
        (2022, "dac",           "United States", 3500.0, "federal",  "DOE DAC Hubs (IRA)",                    "announced"),
        (2022, "dac",           "United States",  100.0, "federal",  "DOE Carbon Negative Shot R&D",          "deployed"),
        (2022, "reforestation", "United States", 1500.0, "federal",  "IRA Reforestation Act",                  "announced"),
        (2022, "urban_forestry","United States",  1400.0, "federal", "IRA Urban & Community Forestry",         "announced"),
        (2023, "dac",           "United States",  600.0, "federal",  "DOE DAC Hubs Phase 1 awards",           "deployed"),
        (2023, "dac",           "United States",  925.0, "private",  "Frontier advance market commitment",     "announced"),
        (2023, "reforestation", "United States",  320.0, "federal",  "IRA Reforestation Act disbursements",    "deployed"),
        (2023, "urban_forestry","United States",  180.0, "federal",  "USFS Urban Forestry grants Round 1",    "deployed"),
        (2023, "point_source",  "United States", 8000.0, "federal",  "DOE Clean Hydrogen + CCUS Hubs (IRA)",  "announced"),
        (2024, "dac",           "United States",  800.0, "federal",  "DOE DAC Hubs Phase 1 continued",        "deployed"),
        (2024, "dac",           "United States",  200.0, "private",  "Stripe/Microsoft/Alphabet CDR purchases","deployed"),
        (2024, "reforestation", "United States",  400.0, "federal",  "IRA Reforestation disbursements",        "deployed"),
        (2024, "urban_forestry","United States",  250.0, "federal",  "USFS Urban Forestry grants Round 2",    "deployed"),
    ]

    def extract(self) -> pd.DataFrame:
        df = pd.DataFrame(self.RAW_DATA, columns=[
            "year", "technology_slug", "geography_name", "amount_usd_millions",
            "funder_type", "program_name", "announced_vs_deployed"
        ])
        df["source_name"] = self.source_name

        self.validate(df, ["year", "technology_slug", "amount_usd_millions"])
        return df
