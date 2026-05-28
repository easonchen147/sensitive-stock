# Backend

Flask API serving market data, AI prediction, quantitative backtesting, and research analysis for the Sensitive Stock platform.

## Setup

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv/bin/python   # Windows: .venv\Scripts\python.exe
poetry sync --with dev

cp .env.example .env
poetry run flask --app wsgi:application run --debug --port 5000
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `akshare` | Primary A-share market data |
| `akquant` | Backtesting engine |
| `tickflow` | Alternative market data provider |
| `pandas` / `numpy` | Data processing |
| `flask` + `pydantic` | API framework + validation |

## Directory Structure

```
backend/
├── app/
│   ├── api/              # Flask blueprints
│   │   ├── market.py     # Quotes, sectors, stock detail, K-line
│   │   ├── backtests.py  # Presets, run, NL strategy generation
│   │   ├── qa.py         # AI stock Q&A
│   │   ├── daily.py      # Daily analysis reports
│   │   └── ...
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   │   ├── stock_detail.py       # Stock fundamentals, K-line, financials
│   │   ├── diagnosis.py          # AI-powered technical diagnosis
│   │   ├── stock_qa.py           # DeepSeek Q&A service
│   │   ├── strategy_generator.py # NL → Python strategy
│   │   ├── daily_analysis.py     # Daily screening + AI reports
│   │   └── ...
│   └── config.py
├── backtesting/
│   ├── presets.py        # 8 strategy presets
│   ├── indicators.py     # Technical indicators (SMA, RSI, MACD, Bollinger, KDJ)
│   └── ...
├── tests/
└── wsgi.py
```

## Data Providers

Default order: `akshare → tickflow → tushare → sina_direct`

Set `BACKEND_MARKET_DATA_PREFER_TICKFLOW=true` to prioritize TickFlow.

## Testing

```bash
poetry run pytest tests -q
poetry run ruff check .
```

## Contract

Runtime OpenAPI: `GET /api/v1/openapi.json`

Regenerate static contract: `uv run python scripts/generate_openapi.py`
