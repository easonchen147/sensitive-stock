# Sensitive Stock

A full-stack A-share research terminal — real-time market intelligence, AI-powered diagnosis, quantitative backtesting, and portfolio analysis in one unified workspace.

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![Python](https://img.shields.io/badge/Python-3.12-yellow)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

| Module | Description |
|--------|-------------|
| **Market Overview** | Real-time quotes, sector heatmaps, multi-source news aggregation from 9+ channels |
| **AI Diagnosis** | Technical indicator scoring, DeepSeek-powered analysis with risk assessment |
| **Backtesting** | 8 preset strategies, custom Python strategies, natural language strategy generation |
| **Stock Screener** | Multi-factor filtering (PE, market cap, industry, volume ratio), sortable results |
| **AI Q&A** | Chat-based stock analysis powered by DeepSeek with data-backed responses |
| **Daily Report** | AI-generated daily market summaries with top picks and sector analysis |
| **Factor Research** | Factor snapshots, IC ranking, rolling window statistics |
| **Portfolio Optimization** | Equal weight, minimum variance, max Sharpe, risk parity |

## Tech Stack

**Frontend** — Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui · Recharts

**Backend** — Flask 3.1 · Pydantic v2 · AKShare · AKQuant · TickFlow

**AI** — DeepSeek `deepseek-v4-flash` with thinking mode

**News Sources** — Jin10 · East Money · Sina Finance · CLS · STCN · 21 Jingji · CNINFO

## Quick Start

### Prerequisites

- Python 3.12
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) + [Poetry](https://python-poetry.org)

### Backend

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv/bin/python   # Windows: .venv\Scripts\python.exe
poetry sync --with dev

cp .env.example .env              # configure credentials
poetry run flask --app wsgi:application run --debug --port 5000
```

Health check: `curl http://127.0.0.1:5000/api/v1/health`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:3000 — default login: `admin` / `SensitiveStock-Internal-MVP`

## Architecture

```
sensitive-stock/
├── backend/
│   ├── app/
│   │   ├── api/           # Flask blueprints (market, backtests, qa, daily, ...)
│   │   ├── schemas/       # Pydantic request/response models
│   │   └── services/      # Business logic (stock detail, diagnosis, prediction, ...)
│   ├── backtesting/       # Strategy presets, indicators, AKQuant integration
│   ├── tests/             # Pytest suite
│   └── wsgi.py
├── frontend/
│   ├── app/               # Next.js App Router pages + API proxy
│   │   ├── api/backend/   # Catch-all proxy → Flask
│   │   ├── backtests/
│   │   ├── market/
│   │   ├── diagnosis/
│   │   ├── screener/
│   │   ├── factors/
│   │   ├── portfolio/
│   │   ├── qa/
│   │   └── daily/
│   ├── components/        # UI components + workbench logic
│   ├── lib/               # API client, auth, OpenAPI bindings
│   └── types/             # TypeScript interfaces
├── openapi.json           # Static OpenAPI 3.1 contract
└── docs/
```

### Data Flow

```
Browser → Next.js (SSR) → /api/backend/[...slug] → Flask → AKShare/DeepSeek
                                      ↓
                              Bearer token auth
```

All business endpoints require `Authorization: Bearer <token>`. The frontend proxy attaches the session token automatically.

## API Endpoints

Public:
- `POST /api/v1/auth/login` — authentication
- `GET /api/v1/health` — health check
- `GET /api/v1/openapi.json` — live contract

Market:
- `GET /api/v1/market` — overview
- `GET /api/v1/market/quotes` — real-time quotes
- `GET /api/v1/market/sectors` — sector data
- `GET /api/v1/market/stock/{symbol}/detail` — stock fundamentals
- `GET /api/v1/market/stock/{symbol}/kline` — K-line data
- `GET /api/v1/market/stock/{symbol}/financials` — financial summary
- `GET /api/v1/market/stock/{symbol}/news` — stock news

News & Prediction:
- `GET /api/v1/market/news` — aggregated news
- `GET /api/v1/market/news/intelligence` — keywords, events, sector hints
- `GET /api/v1/market/news/predictions` — AI predictions
- `GET /api/v1/market/news/categories` — news categories

Backtesting:
- `GET /api/v1/backtests/presets` — strategy presets
- `POST /api/v1/backtests/run` — run backtest
- `POST /api/v1/backtests/generate-strategy` — NL strategy generation

Research:
- `POST /api/v1/screener/run` — stock screening
- `POST /api/v1/diagnosis/run` — AI diagnosis
- `POST /api/v1/factors/analyze` — factor analysis
- `POST /api/v1/portfolio/optimize` — portfolio optimization
- `POST /api/v1/qa/ask` — AI stock Q&A

Daily:
- `POST /api/v1/daily/run` — generate daily report
- `GET /api/v1/daily/latest` — latest report
- `GET /api/v1/daily/history` — report history

## Configuration

Backend `.env` key settings:

| Variable | Description |
|----------|-------------|
| `BACKEND_DEEPSEEK_API_KEY` | DeepSeek API key (required for AI features) |
| `BACKEND_AUTH_ADMIN_USERNAME` | Admin username |
| `BACKEND_AUTH_ADMIN_PASSWORD` | Admin password |
| `BACKEND_MARKET_DATA_PREFER_TICKFLOW` | Prefer TickFlow over AKShare |
| `TICKFLOW_API_KEY` | TickFlow API key (optional, for real-time quotes) |

See `backend/.env.example` for the full list.

## Development

```bash
# Backend
cd backend && poetry run pytest tests -q && poetry run ruff check .

# Frontend
cd frontend && npx tsc --noEmit && npm run build

# Regenerate OpenAPI contract
cd backend && uv run python scripts/generate_openapi.py
```

## License

[MIT](LICENSE)
