"""
pipeline/extractors/base.py
Abstract base class for all data extractors.
Each extractor is responsible for ONE data source → returns a clean DataFrame.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseExtractor(ABC):
    """
    Subclass this for every data source.
    Contract: extract() always returns a pandas DataFrame with
    standardized column names ready for the loader.
    """

    source_name: str = ""

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Pull raw data, return cleaned DataFrame."""
        pass

    def validate(self, df: pd.DataFrame, required_cols: list) -> None:
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"[{self.source_name}] Missing columns: {missing}")
        if df.empty:
            raise ValueError(f"[{self.source_name}] Extractor returned empty DataFrame.")
        print(f"✓ [{self.source_name}] Extracted {len(df)} rows.")
