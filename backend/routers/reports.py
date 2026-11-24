"""
Indonesia Economic Intelligence — Report Generation Router
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from backend.models import ReportRequest
from backend.services.report_generator import generate_html_report, generate_pdf_report
import io

router = APIRouter()


@router.post("/reports/generate")
async def generate_report(request: ReportRequest):
    if request.format == "pdf":
        try:
            pdf_bytes = generate_pdf_report(
                period_start=request.period_start,
                period_end=request.period_end,
                indicators=request.indicators,
            )
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=laporan-ekonomi-indonesia.pdf"},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    # Default: HTML
    html = generate_html_report(
        period_start=request.period_start,
        period_end=request.period_end,
        indicators=request.indicators,
    )
    return HTMLResponse(content=html)


@router.get("/reports/preview")
def preview_report():
    """Quick HTML preview with no parameters."""
    html = generate_html_report()
    return HTMLResponse(content=html)
