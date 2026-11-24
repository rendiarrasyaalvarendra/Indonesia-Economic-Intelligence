"""
Indonesia Economic Intelligence — Overview & KPI Router
"""
from fastapi import APIRouter
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/overview")
def get_overview():
    loader = get_loader()
    kpis = loader.get_latest_kpis()
    gdp = loader.get_gdp_annual()
    inf = loader.get_inflation_monthly()
    er = loader.get_exchange_rate()
    bi = loader.get_bi_rate()

    # Trend data for sparklines (last 12 months or 10 years)
    return {
        "kpis": kpis,
        "gdp_trend": gdp[-10:],
        "inflation_trend": [{"period": x["period"], "yoy": x["yoy"]} for x in inf[-24:]],
        "exchange_rate_trend": er[-24:],
        "bi_rate_trend": bi[-24:],
        "data_sources": [
            {"name": "BPS", "url": "https://www.bps.go.id", "last_updated": "2024-12"},
            {"name": "Bank Indonesia", "url": "https://www.bi.go.id", "last_updated": "2024-12"},
        ],
    }


@router.get("/overview/kpis")
def get_kpis():
    loader = get_loader()
    return loader.get_latest_kpis()
