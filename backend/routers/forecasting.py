"""
Indonesia Economic Intelligence — Forecasting Router
"""
from fastapi import APIRouter, Query, HTTPException
from backend.services.data_loader import get_loader
from backend.services.forecasting import run_all_methods

router = APIRouter()

INDICATOR_MAP = {
    "inflation_yoy": {
        "label": "Inflasi YoY",
        "unit": "%",
        "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_inflation_monthly()],
            [x["yoy"] for x in loader.get_inflation_monthly()],
        ),
    },
    "inflation_mom": {
        "label": "Inflasi MoM",
        "unit": "%",
        "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_inflation_monthly()],
            [x["mom"] for x in loader.get_inflation_monthly()],
        ),
    },
    "gdp_annual": {
        "label": "Pertumbuhan PDB Tahunan",
        "unit": "% YoY",
        "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_gdp_annual()],
            [x["value"] for x in loader.get_gdp_annual()],
        ),
    },
    "gdp_quarterly": {
        "label": "Pertumbuhan PDB Kuartalan",
        "unit": "% YoY",
        "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_gdp_quarterly()],
            [x["value"] for x in loader.get_gdp_quarterly()],
        ),
    },
    "exchange_rate": {
        "label": "Kurs USD/IDR",
        "unit": "IDR",
        "source": "Bank Indonesia",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_exchange_rate()],
            [x["usd_idr"] for x in loader.get_exchange_rate()],
        ),
    },
    "bi_rate": {
        "label": "BI Rate",
        "unit": "%",
        "source": "Bank Indonesia",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_bi_rate()],
            [x["rate"] for x in loader.get_bi_rate()],
        ),
    },
}


@router.get("/forecasting/{indicator}")
def get_forecast(
    indicator: str,
    horizon: int = Query(6, ge=1, le=24),
    method: str = Query("all", description="all | moving_average | linear_regression | exponential_smoothing | arima"),
):
    if indicator not in INDICATOR_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Indicator '{indicator}' not found. Available: {list(INDICATOR_MAP.keys())}",
        )

    loader = get_loader()
    cfg = INDICATOR_MAP[indicator]
    periods, values = cfg["getter"](loader)

    result = run_all_methods(values, periods, horizon)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])

    return {
        "indicator": cfg["label"],
        "unit": cfg["unit"],
        "source": cfg["source"],
        "horizon": horizon,
        "requested_method": method,
        **result,
    }


@router.get("/forecasting")
def list_forecastable_indicators():
    return {
        "available_indicators": list(INDICATOR_MAP.keys()),
        "indicator_labels": {k: v["label"] for k, v in INDICATOR_MAP.items()},
        "supported_methods": ["moving_average", "linear_regression", "exponential_smoothing", "arima"],
        "max_horizon": 24,
    }
