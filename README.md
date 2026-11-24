# Indonesia Economic Intelligence

An AI-powered national economic data analytics and intelligence platform for Indonesia. The platform collects, processes, visualizes, and analyzes Indonesian economic data from official sources (BPS and Bank Indonesia).

---

## Features

- **Economic Overview** — Latest KPI cards, historical trends, auto-generated insights
- **Inflation Analysis** — MoM, YoY, YTD, CPI, provincial comparison
- **GDP Analysis** — Current/constant prices, sector & expenditure breakdown, regional GDP
- **Monetary Analysis** — USD/IDR trends, BI rate history
- **Employment Analysis** — TPT, TPAK, employed/unemployed population
- **Poverty Analysis** — Poverty rate, poverty line, urban vs rural
- **Regional Economic Analysis** — Interactive Indonesia map, provincial indicators
- **Trade Analysis** — Exports, imports, trade balance, commodity breakdown
- **AI Economic Analyst** — Natural-language chatbot grounded in real datasets
- **Data Explorer** — Searchable/sortable datasets, CSV/JSON export
- **Economic Insights** — Auto-generated findings from real data
- **Economic Forecasting** — Moving Average, Linear Regression, Exponential Smoothing, ARIMA
- **Anomaly Detection** — Z-Score, IQR, Moving Average Deviation
- **AI Economic Reports** — Full structured PDF/HTML reports

---

## Project Structure

```
indonesia-economic-intelligence/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Settings and environment variables
│   ├── routers/                 # API route modules
│   │   ├── overview.py
│   │   ├── inflation.py
│   │   ├── gdp.py
│   │   ├── monetary.py
│   │   ├── employment.py
│   │   ├── poverty.py
│   │   ├── regional.py
│   │   ├── trade.py
│   │   ├── forecasting.py
│   │   ├── anomaly.py
│   │   ├── insights.py
│   │   ├── ai_analyst.py
│   │   ├── reports.py
│   │   └── data_explorer.py
│   ├── services/
│   │   ├── data_loader.py       # Centralized data loading & cache
│   │   ├── data_pipeline.py     # Validation, cleaning, normalization
│   │   ├── bps_client.py        # BPS API client
│   │   ├── bi_client.py         # Bank Indonesia API client
│   │   ├── forecasting.py       # Forecasting models
│   │   ├── anomaly.py           # Anomaly detection
│   │   ├── insights.py          # Auto insight generation
│   │   ├── ai_service.py        # OpenAI integration
│   │   └── report_generator.py  # PDF/HTML report builder
│   └── data/
│       ├── raw/                 # Raw CSV/Excel datasets (official)
│       └── processed/           # Cleaned, normalized JSON datasets
├── frontend/
│   ├── index.html               # Main single-page application
│   ├── css/
│   │   └── dashboard.css        # Custom styles extending Tailwind
│   └── js/
│       ├── app.js               # App init, routing, global state
│       ├── api.js               # API client for backend
│       ├── charts.js            # Chart.js helpers & chart builders
│       ├── filters.js           # Global filter management
│       ├── modules/
│       │   ├── overview.js
│       │   ├── kpi_cards.js
│       │   ├── inflation.js
│       │   ├── gdp.js
│       │   ├── monetary.js
│       │   ├── employment.js
│       │   ├── poverty.js
│       │   ├── regional.js
│       │   ├── trade.js
│       │   ├── data_explorer.js
│       │   ├── insights.js
│       │   ├── forecasting.js
│       │   ├── anomaly.js
│       │   ├── ai_analyst.js
│       │   └── reports.js
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.11+
- pip

---

## Installation

### 1. Clone / download the project

```bash
cd "Indonesia Economic Intelligence"
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux
```

Edit `.env` and provide your API keys:
- `OPENAI_API_KEY` — OpenAI key for the AI Economic Analyst
- `BPS_API_KEY` — BPS Open API key (register at https://webapi.bps.go.id/)

> The application will fall back to bundled official datasets when API keys are not provided or when upstream APIs are unavailable.

---

## Running the Application

```bash
# From the project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser at: **http://localhost:8000**

---

## API Documentation

Interactive Swagger UI: **http://localhost:8000/docs**  
ReDoc: **http://localhost:8000/redoc**

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/overview` | National economic overview & KPIs |
| GET | `/api/inflation` | Inflation data (MoM, YoY, CPI) |
| GET | `/api/gdp` | GDP data by sector, expenditure, region |
| GET | `/api/monetary` | Exchange rate & BI rate data |
| GET | `/api/employment` | Employment & labor force data |
| GET | `/api/poverty` | Poverty rate & poverty line data |
| GET | `/api/regional` | Provincial economic indicators |
| GET | `/api/trade` | Export, import & trade balance |
| GET | `/api/forecasting/{indicator}` | Forecasting for a given indicator |
| GET | `/api/anomaly/{indicator}` | Anomaly detection results |
| GET | `/api/insights` | Auto-generated economic insights |
| POST | `/api/ai/chat` | AI Economic Analyst (chat) |
| POST | `/api/reports/generate` | Generate structured economic report |
| GET | `/api/data/explore` | Data explorer with filters & pagination |

---

## Data Sources

| Source | Description | URL |
|--------|-------------|-----|
| BPS (Statistics Indonesia) | GDP, inflation, employment, poverty, trade, regional | https://www.bps.go.id |
| Bank Indonesia | Exchange rate, BI rate, monetary policy | https://www.bi.go.id |

---

## Verification Steps

```bash
# Health check
curl http://localhost:8000/health

# Test KPI overview
curl http://localhost:8000/api/overview

# Test inflation endpoint
curl "http://localhost:8000/api/inflation?frequency=monthly"

# Test AI chat
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the latest GDP growth rate in Indonesia?"}'
```

---

## Notes

- All data shown is sourced from official BPS and BI publications.
- Forecasts are estimates; they are clearly labeled and include uncertainty intervals.
- Anomalies are statistical observations and do not automatically indicate crises.
- AI-generated text is grounded in the loaded datasets and will cite its sources.
