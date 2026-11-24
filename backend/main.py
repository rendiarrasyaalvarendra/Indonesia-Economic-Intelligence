"""
Indonesia Economic Intelligence — FastAPI Application Entry Point
"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.routers import (
    overview, gdp, inflation, monetary, employment,
    poverty, regional, trade, forecasting, anomaly,
    insights, ai_analyst, reports, data_explorer,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("indonesia_economic_intelligence")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Indonesia Economic Intelligence API",
    description=(
        "AI-powered national economic data analytics and intelligence platform "
        "for Indonesia. All data sourced from BPS and Bank Indonesia."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API Routers
# ---------------------------------------------------------------------------
API_PREFIX = "/api"

app.include_router(overview.router, prefix=API_PREFIX, tags=["Overview"])
app.include_router(gdp.router, prefix=API_PREFIX, tags=["GDP"])
app.include_router(inflation.router, prefix=API_PREFIX, tags=["Inflation"])
app.include_router(monetary.router, prefix=API_PREFIX, tags=["Monetary"])
app.include_router(employment.router, prefix=API_PREFIX, tags=["Employment"])
app.include_router(poverty.router, prefix=API_PREFIX, tags=["Poverty"])
app.include_router(regional.router, prefix=API_PREFIX, tags=["Regional"])
app.include_router(trade.router, prefix=API_PREFIX, tags=["Trade"])
app.include_router(forecasting.router, prefix=API_PREFIX, tags=["Forecasting"])
app.include_router(anomaly.router, prefix=API_PREFIX, tags=["Anomaly Detection"])
app.include_router(insights.router, prefix=API_PREFIX, tags=["Insights"])
app.include_router(ai_analyst.router, prefix=API_PREFIX, tags=["AI Analyst"])
app.include_router(reports.router, prefix=API_PREFIX, tags=["Reports"])
app.include_router(data_explorer.router, prefix=API_PREFIX, tags=["Data Explorer"])

# ---------------------------------------------------------------------------
# Frontend static files
# ---------------------------------------------------------------------------
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(frontend_dir / "index.html"))

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": "Indonesia Economic Intelligence",
        "version": "1.0.0",
        "data_sources": ["BPS", "Bank Indonesia"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
