"""
Indonesia Economic Intelligence — GDP Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.data_loader import get_loader

router = APIRouter()


@router.get("/gdp")
def get_gdp(
    frequency: str = Query("annual", description="annual | quarterly"),
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
):
    loader = get_loader()
    if frequency == "quarterly":
        data = loader.get_gdp_quarterly()
    else:
        data = loader.get_gdp_annual()

    if year_start:
        data = [d for d in data if int(str(d["period"])[:4]) >= year_start]
    if year_end:
        data = [d for d in data if int(str(d["period"])[:4]) <= year_end]

    return {
        "indicator": "PDB (Produk Domestik Bruto)",
        "unit": "% YoY",
        "frequency": frequency,
        "source": "BPS",
        "data": data,
        "meta": {
            "description": "Pertumbuhan PDB berdasarkan harga konstan 2010",
            "note": "Annual: tahun; Quarterly: Q1-Q4 YoY",
        },
    }


@router.get("/gdp/sector")
def get_gdp_sector():
    loader = get_loader()
    sectors = loader.get_gdp_by_sector()
    return {
        "indicator": "PDB menurut Lapangan Usaha",
        "unit": "% share & % YoY growth",
        "period": "2023",
        "source": "BPS",
        "data": sectors,
    }


@router.get("/gdp/expenditure")
def get_gdp_expenditure():
    loader = get_loader()
    exp = loader.get_gdp_by_expenditure()
    return {
        "indicator": "PDB menurut Pengeluaran",
        "unit": "% share & % YoY growth",
        "period": "2023",
        "source": "BPS",
        "data": exp,
    }
