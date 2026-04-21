"""
pipeline/extractors/dac_costs.py

Extractor for Direct Air Capture historical cost data.
Sources: IEA, DOE, published literature on DAC cost trajectories.

Data represents best available public estimates for US DAC costs.
All costs in USD/tCO2 removed.
"""

import pandas as pd
from .base import BaseExtractor


class DACCostExtractor(BaseExtractor):
    source_name = "DAC Cost Historical (IEA/DOE/Literature)"

    # Hand-curated from IEA, DOE Carbon Negative Shot, and peer-reviewed sources.
    # These are the most cited public estimates for DAC levelized cost.
    RAW_DATA = [
        # year, cost_ref, cost_low, cost_high, cost_type, notes
        (2010, 1000.0,  600.0,  1500.0, "levelized", "Early Climeworks prototype estimates"),
        (2015,  700.0,  500.0,  1000.0, "levelized", "First commercial pilots (Climeworks, Carbon Engineering)"),
        (2017,  600.0,  400.0,   900.0, "levelized", "Carbon Engineering techno-economic analysis (Keith et al.)"),
        (2019,  500.0,  250.0,   800.0, "levelized", "IEA CCUS report estimate range"),
        (2021,  400.0,  200.0,   700.0, "levelized", "Post-Orca deployment (Climeworks Iceland)"),
        (2022,  350.0,  150.0,   600.0, "levelized", "DOE Carbon Negative Shot baseline"),
        (2023,  300.0,  130.0,   500.0, "levelized", "Stratos (1PointFive) pre-commissioning estimate"),
        (2024,  270.0,  100.0,   450.0, "levelized", "Stratos operational; DOE DAC Hubs announcements"),
        # Forward projections per DOE Carbon Negative Shot target
        (2025,  220.0,   80.0,   400.0, "projected", "DOE trajectory toward $100/t target"),
        (2026,  180.0,   70.0,   350.0, "projected", "DOE trajectory"),
        (2027,  150.0,   60.0,   300.0, "projected", "DOE trajectory"),
        (2028,  130.0,   50.0,   250.0, "projected", "DOE trajectory"),
        (2029,  115.0,   45.0,   200.0, "projected", "DOE trajectory"),
        (2030,  100.0,   40.0,   180.0, "projected", "DOE $100/t target year"),
        (2035,   60.0,   30.0,   120.0, "projected", "Optimistic scale scenario"),
        (2050,   30.0,   15.0,    80.0, "projected", "Long-run learning curve estimate"),
    ]

    def extract(self) -> pd.DataFrame:
        df = pd.DataFrame(self.RAW_DATA, columns=[
            "year", "cost_per_tonne_co2_usd", "cost_low_usd",
            "cost_high_usd", "cost_type", "notes"
        ])
        df["technology_slug"] = "dac"
        df["geography_name"] = "United States"
        df["source_name"] = "DOE Carbon Negative Shot"

        required = ["year", "cost_per_tonne_co2_usd", "technology_slug", "geography_name"]
        self.validate(df, required)
        return df


class DACDeploymentExtractor(BaseExtractor):
    source_name = "DAC Deployment Historical (CDR.fyi / IEA)"

    # US operational DAC capacity in ktCO2/yr
    # Converted to MtCO2/yr for DB storage (divide by 1000)
    RAW_DATA = [
        # year, capacity_kt_co2_yr, num_facilities, notes
        (2017,  0.0009, 1, "Squamish pilot (Carbon Engineering) — tiny scale"),
        (2019,  0.0009, 1, "CE continued operation"),
        (2021,  0.004,  2, "CE + early US pilots"),
        (2022,  0.010,  3, "Expanded US demonstration projects"),
        (2023,  0.025,  5, "Multiple DOE-funded demos; Heirloom first US deployment"),
        (2024,  0.500,  8, "Stratos (1PointFive) ~500 tCO2/yr operational in Texas"),
        # Projections assuming IRA DAC Hub funding deploys on schedule
        (2025,  2.0,   12, "DAC Hub Phase 1 projects begin"),
        (2026,  5.0,   15, "Projected"),
        (2027, 10.0,   20, "Projected"),
        (2028, 20.0,   25, "Projected"),
        (2029, 35.0,   30, "Projected"),
        (2030, 50.0,   35, "DOE 2030 target scenario"),
    ]

    def extract(self) -> pd.DataFrame:
        df = pd.DataFrame(self.RAW_DATA, columns=[
            "year", "capacity_kt_co2_yr", "num_facilities", "notes"
        ])
        # Convert kt → Mt
        df["capacity_mtco2_yr"] = df["capacity_kt_co2_yr"] / 1000
        df["technology_slug"] = "dac"
        df["geography_name"] = "United States"
        df["source_name"] = "CDR.fyi Live DAC Tracker"

        self.validate(df, ["year", "capacity_mtco2_yr", "technology_slug"])
        return df
