"""
Indonesia Economic Intelligence — Pydantic data models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class DataFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class DataSource(BaseModel):
    name: str
    url: str
    accessed: Optional[str] = None


class DatasetMeta(BaseModel):
    indicator: str
    source: str
    unit: str
    frequency: DataFrequency
    period_start: str
    period_end: str
    updated: Optional[str] = None
    notes: Optional[str] = None


class TimeSeriesPoint(BaseModel):
    period: str
    value: Optional[float]
    label: Optional[str] = None


class TimeSeries(BaseModel):
    meta: DatasetMeta
    data: List[TimeSeriesPoint]


class KPICard(BaseModel):
    indicator: str
    value: Optional[float]
    unit: str
    period: str
    previous_value: Optional[float] = None
    previous_period: Optional[str] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    trend: str = "stable"   # up | down | stable
    source: str
    notes: Optional[str] = None


class RegionalDataPoint(BaseModel):
    province_code: str
    province_name: str
    value: Optional[float]
    period: str
    rank: Optional[int] = None


class ForecastPoint(BaseModel):
    period: str
    value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    is_forecast: bool = True


class ForecastResult(BaseModel):
    indicator: str
    method: str
    horizon: int
    frequency: DataFrequency
    history: List[TimeSeriesPoint]
    forecast: List[ForecastPoint]
    mae: Optional[float] = None
    rmse: Optional[float] = None
    notes: Optional[str] = None


class AnomalyPoint(BaseModel):
    period: str
    value: float
    z_score: Optional[float] = None
    iqr_flag: Optional[bool] = None
    ma_deviation: Optional[float] = None
    is_anomaly: bool
    method: str
    description: str


class AnomalyResult(BaseModel):
    indicator: str
    unit: str
    source: str
    anomalies: List[AnomalyPoint]
    total_observations: int
    total_anomalies: int


class Insight(BaseModel):
    id: str
    title: str
    description: str
    indicator: str
    period: str
    value: Optional[float] = None
    comparison_value: Optional[float] = None
    comparison_period: Optional[str] = None
    source: str
    category: str   # trend | extreme | anomaly | regional | comparative


class ChatMessage(BaseModel):
    role: str   # user | assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = []
    charts: Optional[List[Dict[str, Any]]] = []


class ReportRequest(BaseModel):
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    indicators: Optional[List[str]] = None
    format: str = "html"   # html | pdf


class DataExplorerQuery(BaseModel):
    indicator: Optional[str] = None
    source: Optional[str] = None
    frequency: Optional[DataFrequency] = None
    region: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 50
    sort_by: Optional[str] = "period"
    sort_dir: str = "desc"
    export_format: Optional[str] = None   # csv | json
