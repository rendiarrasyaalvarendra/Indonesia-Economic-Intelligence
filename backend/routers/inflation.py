"""
Indonesia Economic Intelligence — Inflation Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/inflation")
def get_inflation(
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
):
    loader = get_loader()
    data = loader.get_inflation_monthly()

    if year_start:
        data = [d for d in data if int(d["period"][:4]) >= year_start]
    if year_end:
        data = [d for d in data if int(d["period"][:4]) <= year_end]

    # Compute YTD for current year
    latest = data[-1] if data else {}
    current_year = latest.get("period", "2024")[:4]
    ytd_data = [d for d in data if d["period"].startswith(current_year)]
    if ytd_data:
        # YTD = last CPI / Jan CPI - 1 (approximate)
        jan = ytd_data[0]
        ytd = round(((ytd_data[-1]["cpi"] - jan["cpi"]) / jan["cpi"]) * 100, 2)
    else:
        ytd = None

    return {
        "indicator": "Inflasi / IHK",
        "unit_mom": "% MoM",
        "unit_yoy": "% YoY",
        "cpi_base_year": "2018",
        "source": "BPS",
        "latest": latest,
        "ytd": ytd,
        "current_year": current_year,
        "data": data,
    }


@router.get("/inflation/provincial")
def get_inflation_provincial():
    loader = get_loader()
    data = loader.get_inflation_provincial()
    sorted_data = sorted(data, key=lambda x: x["yoy"], reverse=True)
    return {
        "indicator": "Inflasi Provinsi",
        "unit": "% YoY",
        "period": "2024-12",
        "source": "BPS",
        "data": sorted_data,
        "highest": sorted_data[0] if sorted_data else None,
        "lowest": sorted_data[-1] if sorted_data else None,
    }
