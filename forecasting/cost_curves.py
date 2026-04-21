"""
forecasting/cost_curves.py

Two forecasting models for carbon removal cost trajectories:

1. Wright's Law (learning curve)
   - Cost drops by a fixed % for every doubling of cumulative deployment
   - Standard model for DAC, solar, batteries
   - Formula: C(x) = C0 * (x / x0) ^ (-b)
     where b = log2(1 - learning_rate)

2. Logistic growth (Bass diffusion simplified)
   - Models adoption S-curve for nature-based deployment
   - Useful for reforestation / urban forestry area growth

Usage:
    from forecasting.cost_curves import WrightsLawModel, LogisticGrowthModel
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class WrightsLawModel:
    """
    Wright's Law cost curve model.

    Parameters
    ----------
    learning_rate : float
        Fraction cost drops per doubling of cumulative capacity.
        DAC historical estimate: ~15-20% (0.15-0.20)
        Solar PV for reference: ~20-23%
    c0 : float
        Cost at reference deployment level (USD/tCO2)
    x0 : float
        Reference cumulative deployment (MtCO2)
    """
    learning_rate: float
    c0: float
    x0: float

    def predict_cost(self, cumulative_capacity: np.ndarray) -> np.ndarray:
        """Given array of cumulative capacities, return predicted costs."""
        b = np.log2(1 - self.learning_rate)
        return self.c0 * (cumulative_capacity / self.x0) ** b

    def forecast(
        self,
        deployment_df: pd.DataFrame,
        target_years: list[int],
        growth_rate: float = 0.50
    ) -> pd.DataFrame:
        """
        Forecast costs for target years assuming exponential deployment growth.

        Parameters
        ----------
        deployment_df : DataFrame with columns [year, capacity_mtco2_yr]
        target_years  : list of years to forecast
        growth_rate   : annual growth rate of deployment (default 50%)
        """
        last = deployment_df.sort_values("year").iloc[-1]
        last_year = int(last["year"])
        last_capacity = float(last["capacity_mtco2_yr"])

        results = []
        cumulative = deployment_df["capacity_mtco2_yr"].sum()

        for year in target_years:
            years_ahead = year - last_year
            annual_capacity = last_capacity * ((1 + growth_rate) ** years_ahead)
            # Approximate cumulative as sum of geometric series
            if growth_rate > 0:
                cumulative_proj = cumulative + last_capacity * (
                    ((1 + growth_rate) ** years_ahead - 1) / growth_rate
                )
            else:
                cumulative_proj = cumulative + annual_capacity * years_ahead

            predicted_cost = self.predict_cost(np.array([cumulative_proj]))[0]

            results.append({
                "year": year,
                "cumulative_capacity_mt": round(cumulative_proj, 4),
                "annual_capacity_mt": round(annual_capacity, 4),
                "predicted_cost_usd": round(predicted_cost, 2),
                "model": "wrights_law",
                "learning_rate": self.learning_rate,
                "growth_rate_assumption": growth_rate,
            })

        return pd.DataFrame(results)


@dataclass
class LogisticGrowthModel:
    """
    Logistic (S-curve) growth model for nature-based deployment.

    Parameters
    ----------
    k : float
        Carrying capacity — max achievable deployment (MtCO2/yr or Mha)
    r : float
        Intrinsic growth rate
    t0 : int
        Inflection point year (midpoint of S-curve)
    """
    k: float
    r: float
    t0: int

    def predict(self, years: np.ndarray) -> np.ndarray:
        """Logistic function: K / (1 + exp(-r*(t - t0)))"""
        return self.k / (1 + np.exp(-self.r * (years - self.t0)))

    def forecast(self, target_years: list[int]) -> pd.DataFrame:
        years = np.array(target_years)
        values = self.predict(years)
        return pd.DataFrame({
            "year": target_years,
            "predicted_deployment": np.round(values, 4),
            "model": "logistic_growth",
            "carrying_capacity": self.k,
            "growth_rate_r": self.r,
            "inflection_year": self.t0,
        })


# ------------------------------------------------------------------
# Pre-configured model instances based on literature estimates
# ------------------------------------------------------------------

DAC_CONSERVATIVE = WrightsLawModel(
    learning_rate=0.15,   # 15% cost reduction per doubling
    c0=300.0,             # ~$300/t in 2023
    x0=0.001,             # ~1 ktCO2 cumulative by 2023
)

DAC_OPTIMISTIC = WrightsLawModel(
    learning_rate=0.20,   # 20% — matches solar PV historical rate
    c0=300.0,
    x0=0.001,
)

REFORESTATION_LOGISTIC = LogisticGrowthModel(
    k=950.0,    # ~950 MtCO2/yr max US forest sink potential
    r=0.08,
    t0=2035,    # inflection around 2035 with IRA funding
)

URBAN_FORESTRY_LOGISTIC = LogisticGrowthModel(
    k=45.0,     # ~45 MtCO2/yr if US cities hit 40% canopy target
    r=0.06,
    t0=2038,
)
