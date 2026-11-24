"""
Indonesia Economic Intelligence — Data Explorer Router
"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import csv
import io
import json

from backend.services.data_loader import get_loader

router = APIRouter()


def _build_flat_records(loader):
    """Build a flat list of all time-series records for the data explorer."""
    records = []

    for row in loader.get_gdp_annual():
        records.append({
            "indicator": "PDB Tahunan",
            "source": "BPS",
            "unit": "% YoY",
            "frequency": "annual",
            "region": "Nasional",
            "period": row["period"],
            "value": row["value"],
        })

    for row in loader.get_gdp_quarterly():
        records.append({
            "indicator": "PDB Kuartalan",
            "source": "BPS",
            "unit": "% YoY",
            "frequency": "quarterly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["value"],
        })

    for row in loader.get_inflation_monthly():
        records.append({
            "indicator": "Inflasi YoY",
            "source": "BPS",
            "unit": "% YoY",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["yoy"],
        })
        records.append({
            "indicator": "Inflasi MoM",
            "source": "BPS",
            "unit": "% MoM",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["mom"],
        })
        records.append({
            "indicator": "CPI (IHK)",
            "source": "BPS",
            "unit": "Index (2018=100)",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["cpi"],
        })

    for row in loader.get_exchange_rate():
        records.append({
            "indicator": "Kurs USD/IDR",
            "source": "Bank Indonesia",
            "unit": "IDR",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["usd_idr"],
        })

    for row in loader.get_bi_rate():
        records.append({
            "indicator": "BI Rate",
            "source": "Bank Indonesia",
            "unit": "%",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["rate"],
        })

    for row in loader.get_employment():
        for metric, label, unit in [
            ("tpt", "TPT (Pengangguran)", "%"),
            ("tpak", "TPAK (Partisipasi Kerja)", "%"),
            ("employed_m", "Penduduk Bekerja", "Juta Jiwa"),
            ("unemployed_m", "Pengangguran", "Juta Jiwa"),
        ]:
            records.append({
                "indicator": label,
                "source": "BPS",
                "unit": unit,
                "frequency": "semi-annual",
                "region": "Nasional",
                "period": row["period"],
                "value": row.get(metric),
            })

    for row in loader.get_poverty():
        records.append({
            "indicator": "Tingkat Kemiskinan",
            "source": "BPS",
            "unit": "%",
            "frequency": "semi-annual",
            "region": "Nasional",
            "period": row["period"],
            "value": row["rate"],
        })

    for row in loader.get_trade():
        records.append({
            "indicator": "Ekspor",
            "source": "BPS",
            "unit": "USD Juta",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["exports"],
        })
        records.append({
            "indicator": "Impor",
            "source": "BPS",
            "unit": "USD Juta",
            "frequency": "monthly",
            "region": "Nasional",
            "period": row["period"],
            "value": row["imports"],
        })

    # Provincial data
    for row in loader.get_regional_gdp():
        records.append({
            "indicator": "Pertumbuhan PDB Regional",
            "source": "BPS",
            "unit": "% YoY",
            "frequency": "annual",
            "region": row["province_name"],
            "period": "2023",
            "value": row["gdp_growth"],
        })

    return records


@router.get("/data/explore")
def explore_data(
    indicator: Optional[str] = None,
    source: Optional[str] = None,
    frequency: Optional[str] = None,
    region: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("period"),
    sort_dir: str = Query("desc"),
    export_format: Optional[str] = None,
):
    loader = get_loader()
    records = _build_flat_records(loader)

    # Filter
    if indicator:
        records = [r for r in records if indicator.lower() in r["indicator"].lower()]
    if source:
        records = [r for r in records if r["source"].lower() == source.lower()]
    if frequency:
        records = [r for r in records if r["frequency"] == frequency]
    if region:
        records = [r for r in records if region.lower() in r["region"].lower()]
    if year_start:
        records = [r for r in records if int(str(r["period"])[:4]) >= year_start]
    if year_end:
        records = [r for r in records if int(str(r["period"])[:4]) <= year_end]
    if search:
        s = search.lower()
        records = [r for r in records if s in r["indicator"].lower() or s in r["region"].lower()]

    # Sort
    reverse = sort_dir == "desc"
    try:
        records = sorted(records, key=lambda x: str(x.get(sort_by, "")), reverse=reverse)
    except Exception:
        pass

    total = len(records)

    # Export
    if export_format == "csv":
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data-ekonomi-indonesia.csv"},
        )
    if export_format == "json":
        return StreamingResponse(
            io.BytesIO(json.dumps(records, ensure_ascii=False).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=data-ekonomi-indonesia.json"},
        )

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_data = records[start:end]

    indicators_list = sorted(set(r["indicator"] for r in _build_flat_records(loader)))
    regions_list = sorted(set(r["region"] for r in _build_flat_records(loader)))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": page_data,
        "filters": {
            "available_indicators": indicators_list,
            "available_regions": regions_list[:50],
            "available_sources": ["BPS", "Bank Indonesia"],
            "available_frequencies": ["monthly", "quarterly", "semi-annual", "annual"],
        },
    }
