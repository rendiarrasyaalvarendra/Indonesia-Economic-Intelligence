"""
Indonesia Economic Intelligence — Insights Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from backend.services.insights import generate_insights

router = APIRouter()


@router.get("/insights")
def get_insights(
    category: Optional[str] = Query(None, description="trend | extreme | anomaly | regional | comparative"),
    limit: int = Query(10, ge=1, le=50),
):
    insights = generate_insights()
    if category:
        insights = [i for i in insights if i["category"] == category]
    return {
        "total": len(insights),
        "insights": insights[:limit],
        "categories": ["trend", "extreme", "anomaly", "regional", "comparative"],
    }
