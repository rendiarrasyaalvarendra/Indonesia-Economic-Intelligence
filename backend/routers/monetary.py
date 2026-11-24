"""
Indonesia Economic Intelligence — Monetary Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.data_loader import get_loader
import numpy as np

router = APIRouter()


@router.get("/monetary")
def get_monetary(
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
):
    loader = get_loader()
    er = loader.get_exchange_rate()
    bi = loader.get_bi_rate()

    if year_start:
        er = [d for d in er if int(d["period"][:4]) >= year_start]
        bi = [d for d in bi if int(d["period"][:4]) >= year_start]
    if year_end:
        er = [d for d in er if int(d["period"][:4]) <= year_end]
        bi = [d for d in bi if int(d["period"][:4]) <= year_end]

    # Statistical summary for exchange rate
    er_values = [d["usd_idr"] for d in er]
    bi_values = [d["rate"] for d in bi]

    return {
        "exchange_rate": {
            "indicator": "Kurs USD/IDR",
            "unit": "IDR",
            "source": "Bank Indonesia",
            "latest": er[-1] if er else None,
            "data": er,
            "stats": {
                "mean": round(float(np.mean(er_values)), 2) if er_values else None,
                "min": min(er_values) if er_values else None,
                "max": max(er_values) if er_values else None,
                "std": round(float(np.std(er_values)), 2) if er_values else None,
            },
        },
        "bi_rate": {
            "indicator": "BI Rate (Suku Bunga Acuan)",
            "unit": "%",
            "source": "Bank Indonesia",
            "latest": bi[-1] if bi else None,
            "data": bi,
            "stats": {
                "mean": round(float(np.mean(bi_values)), 2) if bi_values else None,
                "min": min(bi_values) if bi_values else None,
                "max": max(bi_values) if bi_values else None,
            },
        },
    }
