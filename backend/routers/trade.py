"""
Indonesia Economic Intelligence — Trade Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.data_loader import get_loader
import numpy as np

router = APIRouter()


@router.get("/trade")
def get_trade(
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
):
    loader = get_loader()
    data = loader.get_trade()

    if year_start:
        data = [d for d in data if int(d["period"][:4]) >= year_start]
    if year_end:
        data = [d for d in data if int(d["period"][:4]) <= year_end]

    # Enrich with balance
    enriched = []
    for d in data:
        balance = d["exports"] - d["imports"]
        enriched.append({**d, "balance": balance, "surplus": balance >= 0})

    latest = enriched[-1] if enriched else {}
    exports = [d["exports"] for d in enriched]
    imports = [d["imports"] for d in enriched]
    surplus_months = sum(1 for d in enriched if d["surplus"])

    # YoY growth for latest month
    if len(enriched) >= 13:
        yoy_period = enriched[-13]
        exp_growth = round((latest["exports"] - yoy_period["exports"]) / yoy_period["exports"] * 100, 2)
        imp_growth = round((latest["imports"] - yoy_period["imports"]) / yoy_period["imports"] * 100, 2)
    else:
        exp_growth = None
        imp_growth = None

    return {
        "indicator": "Neraca Perdagangan",
        "unit": "USD Juta",
        "source": "BPS",
        "latest": latest,
        "yoy_growth": {
            "exports_growth_pct": exp_growth,
            "imports_growth_pct": imp_growth,
        },
        "summary": {
            "total_months": len(enriched),
            "surplus_months": surplus_months,
            "deficit_months": len(enriched) - surplus_months,
            "avg_exports": round(float(np.mean(exports)), 2) if exports else None,
            "avg_imports": round(float(np.mean(imports)), 2) if imports else None,
        },
        "top_export_commodities": loader.get_top_export_commodities(),
        "data": enriched,
    }
