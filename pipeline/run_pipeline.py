"""
pipeline/run_pipeline.py

Master ETL script — runs all extractors and loads into PostgreSQL.
Run this to populate the database from scratch or refresh data.

Usage:
    python -m pipeline.run_pipeline
    python -m pipeline.run_pipeline --extractors dac nature markets
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.extractors.dac_costs import DACCostExtractor, DACDeploymentExtractor
from pipeline.extractors.nature_based import UrbanForestryExtractor, ReforestationExtractor
from pipeline.extractors.carbon_markets import CarbonCreditPriceExtractor, InvestmentFlowExtractor
from pipeline.extractors.lseg_esg import LSEGESGExtractor
from pipeline.extractors.lseg_commitments import LSEGCommitmentsExtractor
from pipeline.loaders.db_loader import DBLoader


def run_dac(loader: DBLoader):
    print("\n── DAC ─────────────────────────────────────")
    cost_df = DACCostExtractor().extract()
    loader.load_cost_metrics(cost_df)

    deploy_df = DACDeploymentExtractor().extract()
    loader.load_deployment_metrics(deploy_df)


def run_nature(loader: DBLoader):
    print("\n── Nature-Based ─────────────────────────────")
    urban_df = UrbanForestryExtractor().extract()
    # Urban forestry national-level costs
    national = urban_df[urban_df["geo_type"] == "national"].copy()
    national = national.rename(columns={"co2_seq_mt_yr": "capacity_mtco2_yr"})
    loader.load_cost_metrics(
        national[["year", "cost_per_tonne_co2_usd", "technology_slug",
                  "geography_name", "source_name", "notes"]]
        .assign(cost_type="levelized")
    )
    loader.load_deployment_metrics(
        national[["year", "capacity_mtco2_yr", "canopy_cover_pct",
                  "area_mha", "technology_slug", "geography_name", "source_name", "notes"]]
    )

    reforest_df = ReforestationExtractor().extract()
    loader.load_cost_metrics(
        reforest_df[["year", "cost_per_tonne_co2_usd", "cost_type",
                     "technology_slug", "geography_name", "source_name", "notes"]]
    )
    reforest_df["capacity_mtco2_yr"] = reforest_df["forest_sink_mt_co2"]
    loader.load_deployment_metrics(
        reforest_df[["year", "capacity_mtco2_yr", "technology_slug",
                     "geography_name", "source_name", "notes"]]
    )


def run_esg(loader):
    print("\n── LSEG ESG ─────────────────────────────────")
    esg_df = LSEGESGExtractor().extract()
    loader.load_esg_company_data(esg_df)


def run_commitments(loader):
    print("\n── LSEG Commitments ─────────────────────────")
    from pipeline.loaders.db_loader import DBLoader as _DBLoader
    commitments_df = LSEGCommitmentsExtractor().extract()
    loader.load_esg_commitments(commitments_df)


def run_markets(loader: DBLoader):
    print("\n── Carbon Markets ───────────────────────────")
    prices_df = CarbonCreditPriceExtractor().extract()
    loader.load_carbon_credit_prices(prices_df)

    invest_df = InvestmentFlowExtractor().extract()
    loader.load_investment_flows(invest_df)


def main():
    parser = argparse.ArgumentParser(description="Run carbon removal ETL pipeline")
    parser.add_argument(
        "--extractors", nargs="+",
        choices=["dac", "nature", "markets", "esg", "commitments", "all"],
        default=["all"],
        help="Which extractors to run (default: all)"
    )
    args = parser.parse_args()
    run_all = "all" in args.extractors

    print("=" * 50)
    print("  Carbon Removal Tracker — ETL Pipeline")
    print("=" * 50)

    loader = DBLoader()

    if run_all or "dac" in args.extractors:
        run_dac(loader)
    if run_all or "nature" in args.extractors:
        run_nature(loader)
    if run_all or "markets" in args.extractors:
        run_markets(loader)
    if run_all or "esg" in args.extractors:
        run_esg(loader)
    if run_all or "commitments" in args.extractors:
        run_commitments(loader)

    print("\n✓ Pipeline complete.")


if __name__ == "__main__":
    main()
