# Directory Map

This repository is split into a frontend workspace, a backend workspace,
OpenSpec change control, and project documentation.

```text
.
├── backend/
│   ├── app/
│   │   ├── api/             # Flask blueprints, including /api/v1/openapi.json
│   │   ├── schemas/         # Pydantic request schemas
│   │   ├── services/        # Backend service layer and compatibility adapters
│   │   └── openapi.py       # Global OpenAPI emitter
│   ├── backtesting/         # Compatibility support for AKQuant-backed execution
│   ├── scripts/
│   │   └── generate_openapi.py
│   ├── tests/
│   ├── factor_analysis.py
│   ├── portfolio_optimizer.py
│   └── wsgi.py
├── frontend/
│   ├── app/
│   ├── components/          # App shell, workbenches, shared Huashu layout/state components
│   ├── lib/                 # Auth, OpenAPI-governed client bindings, server helpers
│   └── types/
├── docs/
│   ├── brainstorms/
│   ├── plans/
│   └── solutions/
├── openspec/
├── openapi.json             # Generated global backend OpenAPI artifact
└── README.md
```

Runtime code belongs under `backend/` or `frontend/`. The repo root keeps
workspace-level files, documentation, OpenSpec artifacts, and the generated
global `openapi.json`.

Backend public API facts:

- `GET /api/v1/openapi.json` publishes the runtime OpenAPI document.
- `backend/scripts/generate_openapi.py` writes the static root artifact.
- Business APIs other than health, OpenAPI discovery, and login require
  bearer-token authentication.
- Screener, diagnosis, factors, and portfolio are formal API/workbench surfaces,
  not transitional route markers.

Frontend contract and design facts:

- `frontend/lib/openapi-client.ts` is the frontend route binding table for the
  generated backend `openapi.json`.
- `frontend/components/workbench-layout.tsx` owns the shared research workbench
  header, metric, and workflow-state surfaces.
- `frontend/app/globals.css` defines the Quiet Capital Terminal visual language
  used across all formal pages.
