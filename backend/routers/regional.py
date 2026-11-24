"""
Indonesia Economic Intelligence — Regional Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/regional")
def get_regional(indicator: str = Query("gdp", description="gdp | unemployment | poverty | inflation")):
    loader = get_loader()

    if indicator == "unemployment":
        data = loader.get_regional_unemployment()
        field = "tpt"
        label = "TPT (%)"
        source = "BPS"
        period = "2024-02"
    elif indicator == "poverty":
        data = loader.get_regional_poverty()
        field = "rate"
        label = "Tingkat Kemiskinan (%)"
        source = "BPS"
        period = "2024-03"
    elif indicator == "inflation":
        data = loader.get_inflation_provincial()
        field = "yoy"
        label = "Inflasi YoY (%)"
        source = "BPS"
        period = "2024-12"
    else:  # gdp default
        data = loader.get_regional_gdp()
        field = "gdp_growth"
        label = "Pertumbuhan PDB (%)"
        source = "BPS"
        period = "2023"

    # Rank provinces
    ranked = sorted(data, key=lambda x: x.get(field, 0) or 0, reverse=True)
    for i, item in enumerate(ranked, 1):
        item["rank"] = i

    values = [d.get(field) for d in data if d.get(field) is not None]

    return {
        "indicator": label,
        "field": field,
        "period": period,
        "source": source,
        "total_provinces": len(data),
        "highest": ranked[0] if ranked else None,
        "lowest": ranked[-1] if ranked else None,
        "national_avg": round(sum(values) / len(values), 2) if values else None,
        "data": data,
        "ranked": ranked[:10],  # top 10
    }


@router.get("/regional/province/{province_code}")
def get_province_detail(province_code: str):
    loader = get_loader()

    gdp_data = next((d for d in loader.get_regional_gdp() if d["province_code"] == province_code), None)
    unemp_data = next((d for d in loader.get_regional_unemployment() if d["province_code"] == province_code), None)
    pov_data = next((d for d in loader.get_regional_poverty() if d["province_code"] == province_code), None)
    inf_data = next((d for d in loader.get_inflation_provincial() if d["province_code"] == province_code), None)

    if not gdp_data and not unemp_data and not pov_data:
        return {"error": f"Province {province_code} not found in dataset"}

    province_name = (gdp_data or unemp_data or pov_data or inf_data or {}).get("province_name", "Unknown")

    return {
        "province_code": province_code,
        "province_name": province_name,
        "gdp": gdp_data,
        "unemployment": unemp_data,
        "poverty": pov_data,
        "inflation": inf_data,
        "source": "BPS",
    }
