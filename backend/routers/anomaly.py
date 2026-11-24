"""
Indonesia Economic Intelligence — Anomaly Detection Router
"""
from fastapi import APIRouter, Query, HTTPException
from backend.services.data_loader import get_loader
from backend.services.anomaly import detect_anomalies

router = APIRouter()

INDICATOR_MAP = {
    "inflation_yoy": {
        "label": "Inflasi YoY", "unit": "%", "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_inflation_monthly()],
            [x["yoy"] for x in loader.get_inflation_monthly()],
        ),
    },
    "gdp_annual": {
        "label": "Pertumbuhan PDB", "unit": "% YoY", "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_gdp_annual()],
            [x["value"] for x in loader.get_gdp_annual()],
        ),
    },
    "exchange_rate": {
        "label": "Kurs USD/IDR", "unit": "IDR", "source": "Bank Indonesia",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_exchange_rate()],
            [x["usd_idr"] for x in loader.get_exchange_rate()],
        ),
    },
    "bi_rate": {
        "label": "BI Rate", "unit": "%", "source": "Bank Indonesia",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_bi_rate()],
            [x["rate"] for x in loader.get_bi_rate()],
        ),
    },
    "trade_balance": {
        "label": "Neraca Perdagangan", "unit": "USD Juta", "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_trade()],
            [x["exports"] - x["imports"] for x in loader.get_trade()],
        ),
    },
    "unemployment": {
        "label": "TPT", "unit": "%", "source": "BPS",
        "getter": lambda loader: (
            [x["period"] for x in loader.get_employment()],
            [x["tpt"] for x in loader.get_employment()],
        ),
    },
}


@router.get("/anomaly/{indicator}")
def get_anomaly(
    indicator: str,
    z_threshold: float = Query(2.5, description="Z-Score threshold"),
    iqr_multiplier: float = Query(1.5, description="IQR multiplier"),
):
    if indicator not in INDICATOR_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"Indicator '{indicator}' not found. Available: {list(INDICATOR_MAP.keys())}",
        )

    loader = get_loader()
    cfg = INDICATOR_MAP[indicator]
    periods, values = cfg["getter"](loader)

    result = detect_anomalies(
        values=values,
        periods=periods,
        indicator=cfg["label"],
        unit=cfg["unit"],
        source=cfg["source"],
        z_threshold=z_threshold,
        iqr_multiplier=iqr_multiplier,
    )
    return result


@router.get("/anomaly")
def list_anomaly_indicators():
    return {
        "available_indicators": list(INDICATOR_MAP.keys()),
        "indicator_labels": {k: v["label"] for k, v in INDICATOR_MAP.items()},
    }
