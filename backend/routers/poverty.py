"""
Indonesia Economic Intelligence — Poverty Router
"""
from fastapi import APIRouter
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/poverty")
def get_poverty():
    loader = get_loader()
    data = loader.get_poverty()
    urban_rural = loader.get_poverty_urban_rural()

    latest = data[-1] if data else {}
    prev = data[-2] if len(data) >= 2 else {}
    oldest = data[0] if data else {}

    return {
        "indicator": "Kemiskinan",
        "source": "BPS",
        "frequency": "Semi-Annual (Mar & Sep)",
        "latest": latest,
        "previous": prev,
        "urban_rural": urban_rural,
        "long_term_change": {
            "rate_change": round(latest.get("rate", 0) - oldest.get("rate", 0), 2) if oldest else None,
            "from_period": oldest.get("period"),
            "to_period": latest.get("period"),
        },
        "data": data,
        "meta": {
            "rate": "Tingkat Kemiskinan (%)",
            "population_m": "Jumlah Penduduk Miskin (juta jiwa)",
            "poverty_line": "Garis Kemiskinan (Rp/kapita/bulan)",
        },
    }
