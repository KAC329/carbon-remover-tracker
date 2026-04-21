"""
forecasting/scoring.py

Replicates and extends the Boundless Impact 2030 Climate Score framework.

Score = average of:
  - Abatement Potential Score (1-10) based on MtCO2 tier
  - Abatement Cost Score (1-10) based on $/tCO2

Tiers:
  Tier 1: Gt scale (gigatonnes)  — large engineered, reforestation
  Tier 2: Mt scale (megatonnes)  — urban forestry, early DAC
"""

import pandas as pd
import numpy as np


COST_SCORE_THRESHOLDS = [900, 800, 700, 600, 500, 400, 300, 200, 100, 0]

TIER_THRESHOLDS = {
    "tier1": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],    # GtCO2
    "tier2": [0, 100, 200, 300, 400, 500, 600, 700, 800, 900],  # MtCO2
}


def score_abatement_cost(cost_usd_per_tonne: float) -> float:
    """Score 1-10: lower cost = higher score."""
    for i, threshold in enumerate(COST_SCORE_THRESHOLDS):
        if cost_usd_per_tonne >= threshold:
            return float(i + 1)
    return 10.0


def score_abatement_potential(potential: float, tier: str) -> float:
    """
    Score 1-10 based on abatement potential.
    potential in Gt for tier1, Mt for tier2.
    """
    thresholds = TIER_THRESHOLDS.get(tier, TIER_THRESHOLDS["tier2"])
    score = 1
    for i, threshold in enumerate(thresholds):
        if potential >= threshold:
            score = i + 1
    return float(min(score, 10))


def compute_climate_score(
    abatement_potential: float,
    cost_per_tonne: float,
    tier: str = "tier2"
) -> dict:
    """
    Compute composite climate score for a technology.

    Returns dict with individual and composite scores.
    """
    potential_score = score_abatement_potential(abatement_potential, tier)
    cost_score = score_abatement_cost(cost_per_tonne)
    composite = round((potential_score + cost_score) / 2, 2)

    return {
        "abatement_potential_score": potential_score,
        "abatement_cost_score": cost_score,
        "composite_score": composite,
        "tier": tier,
    }


def score_all_technologies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score a DataFrame of technology projections.

    Expected columns: technology_slug, year, abatement_potential_mt, cost_per_tonne_usd, tier
    Returns DataFrame with scores appended.
    """
    results = []
    for _, row in df.iterrows():
        tier = row.get("tier", "tier2")
        # Convert to Gt if tier1
        potential = row["abatement_potential_mt"]
        if tier == "tier1":
            potential = potential / 1000  # Mt → Gt

        scores = compute_climate_score(potential, row["cost_per_tonne_usd"], tier)
        results.append({
            "technology_slug": row["technology_slug"],
            "year": row["year"],
            **scores,
        })

    return pd.DataFrame(results)
