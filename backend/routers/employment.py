"""
Indonesia Economic Intelligence — Employment Router
"""
from fastapi import APIRouter
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/employment")
def get_employment():
    loader = get_loader()
    data = loader.get_employment()

    latest = data[-1] if data else {}
    prev = data[-2] if len(data) >= 2 else {}

    return {
        "indicator": "Ketenagakerjaan",
        "source": "BPS",
        "frequency": "Semi-Annual (Feb & Agt)",
        "latest": latest,
        "previous": prev,
        "changes": {
            "tpt_change": round(latest.get("tpt", 0) - prev.get("tpt", 0), 2) if prev else None,
            "employed_change_m": round(
                latest.get("employed_m", 0) - prev.get("employed_m", 0), 2
            ) if prev else None,
        },
        "data": data,
        "meta": {
            "tpt": "Tingkat Pengangguran Terbuka (%)",
            "tpak": "Tingkat Partisipasi Angkatan Kerja (%)",
            "employed_m": "Penduduk Bekerja (juta jiwa)",
            "unemployed_m": "Pengangguran (juta jiwa)",
        },
    }
