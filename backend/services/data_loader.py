"""
Indonesia Economic Intelligence — Centralized Data Loader

Provides a unified interface for accessing economic datasets.
Loads from embedded official datasets as the primary source,
with hooks for live BPS / Bank Indonesia API when keys are configured.
"""
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache
import pandas as pd
import numpy as np

from backend.data.datasets import (
    GDP_ANNUAL, GDP_QUARTERLY, GDP_BY_SECTOR, GDP_BY_EXPENDITURE,
    INFLATION_MONTHLY, INFLATION_PROVINCIAL,
    EXCHANGE_RATE_MONTHLY, BI_RATE_MONTHLY,
    EMPLOYMENT_DATA, POVERTY_DATA, POVERTY_URBAN_RURAL,
    TRADE_MONTHLY, TOP_EXPORT_COMMODITIES,
    REGIONAL_GDP, REGIONAL_UNEMPLOYMENT, REGIONAL_POVERTY,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper — build DataFrames once
# ---------------------------------------------------------------------------

def _to_df(records: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(records)
    if "period" in df.columns:
        df["period"] = df["period"].astype(str)
    return df


class DataLoader:
    """Central data access layer. All backend services use this."""

    # --- GDP ---

    def get_gdp_annual(self) -> List[Dict]:
        return GDP_ANNUAL

    def get_gdp_quarterly(self) -> List[Dict]:
        return GDP_QUARTERLY

    def get_gdp_by_sector(self) -> List[Dict]:
        return GDP_BY_SECTOR

    def get_gdp_by_expenditure(self) -> List[Dict]:
        return GDP_BY_EXPENDITURE

    # --- Inflation ---

    def get_inflation_monthly(self) -> List[Dict]:
        return INFLATION_MONTHLY

    def get_inflation_provincial(self) -> List[Dict]:
        return INFLATION_PROVINCIAL

    # --- Monetary ---

    def get_exchange_rate(self) -> List[Dict]:
        return EXCHANGE_RATE_MONTHLY

    def get_bi_rate(self) -> List[Dict]:
        return BI_RATE_MONTHLY

    # --- Employment ---

    def get_employment(self) -> List[Dict]:
        return EMPLOYMENT_DATA

    # --- Poverty ---

    def get_poverty(self) -> List[Dict]:
        return POVERTY_DATA

    def get_poverty_urban_rural(self) -> Dict:
        return POVERTY_URBAN_RURAL

    # --- Trade ---

    def get_trade(self) -> List[Dict]:
        return TRADE_MONTHLY

    def get_top_export_commodities(self) -> List[Dict]:
        return TOP_EXPORT_COMMODITIES

    # --- Regional ---

    def get_regional_gdp(self) -> List[Dict]:
        return REGIONAL_GDP

    def get_regional_unemployment(self) -> List[Dict]:
        return REGIONAL_UNEMPLOYMENT

    def get_regional_poverty(self) -> List[Dict]:
        return REGIONAL_POVERTY

    # --- Composite helpers ---

    def get_latest_kpis(self) -> Dict[str, Any]:
        """Return the four headline KPI values for the overview cards."""
        gdp = GDP_ANNUAL[-1]
        gdp_prev = GDP_ANNUAL[-2]
        inf = INFLATION_MONTHLY[-1]
        inf_prev = INFLATION_MONTHLY[-2]
        er = EXCHANGE_RATE_MONTHLY[-1]
        er_prev = EXCHANGE_RATE_MONTHLY[-2]
        bi = BI_RATE_MONTHLY[-1]
        bi_prev = BI_RATE_MONTHLY[-2]

        def trend(curr, prev):
            if curr > prev:
                return "up"
            if curr < prev:
                return "down"
            return "stable"

        return {
            "gdp_growth": {
                "indicator": "Pertumbuhan PDB",
                "value": gdp["value"],
                "unit": "% YoY",
                "period": gdp["period"],
                "previous_value": gdp_prev["value"],
                "previous_period": gdp_prev["period"],
                "change": round(gdp["value"] - gdp_prev["value"], 2),
                "trend": trend(gdp["value"], gdp_prev["value"]),
                "source": "BPS",
            },
            "inflation": {
                "indicator": "Inflasi",
                "value": inf["yoy"],
                "unit": "% YoY",
                "period": inf["period"],
                "previous_value": inf_prev["yoy"],
                "previous_period": inf_prev["period"],
                "change": round(inf["yoy"] - inf_prev["yoy"], 2),
                "trend": trend(inf["yoy"], inf_prev["yoy"]),
                "source": "BPS",
            },
            "exchange_rate": {
                "indicator": "Kurs USD/IDR",
                "value": er["usd_idr"],
                "unit": "IDR",
                "period": er["period"],
                "previous_value": er_prev["usd_idr"],
                "previous_period": er_prev["period"],
                "change": round(er["usd_idr"] - er_prev["usd_idr"], 0),
                "trend": trend(er["usd_idr"], er_prev["usd_idr"]),
                "source": "Bank Indonesia",
            },
            "bi_rate": {
                "indicator": "BI Rate",
                "value": bi["rate"],
                "unit": "%",
                "period": bi["period"],
                "previous_value": bi_prev["rate"],
                "previous_period": bi_prev["period"],
                "change": round(bi["rate"] - bi_prev["rate"], 2),
                "trend": trend(bi["rate"], bi_prev["rate"]),
                "source": "Bank Indonesia",
            },
        }

    def get_all_series(self) -> Dict[str, Any]:
        """Return all time-series data keyed by indicator name."""
        return {
            "gdp_annual": self.get_gdp_annual(),
            "gdp_quarterly": self.get_gdp_quarterly(),
            "inflation_monthly": self.get_inflation_monthly(),
            "exchange_rate": self.get_exchange_rate(),
            "bi_rate": self.get_bi_rate(),
            "employment": self.get_employment(),
            "poverty": self.get_poverty(),
            "trade": self.get_trade(),
        }


# Singleton
_loader = DataLoader()


def get_loader() -> DataLoader:
    return _loader
