# PriceWise

**Material Price Intelligence & Procurement Decision Engine** — a FABathon 2026 concept for Tata Electronics / TSMPL's semiconductor material price forecasting challenge.

> All data in this repository (materials, prices, drivers, suppliers, market events) is **synthetic demo data**, generated for demonstration purposes. It is not real Tata Electronics / TSMPL procurement data.

## 1. Problem

Supply chain teams struggle to forecast semiconductor material prices due to limited historical data, fragmented market intelligence, and reliance on individual expertise. PriceWise aims to be an **explainable procurement intelligence platform** — not a black-box forecasting model — that answers four questions for any material:

1. **WHAT** is likely to happen to the price?
2. **WHY** is it likely to happen?
3. **HOW CONFIDENT** are we?
4. **WHAT SHOULD PROCUREMENT DO?**

## 2. Solution (current state — Phase 3)

Phase 1 delivers the **foundation**: a real database schema modeling the full material → component → driver → supplier knowledge graph, a working FastAPI backend serving that data, a seeded set of realistic demo materials, and a Next.js dashboard that can browse materials, see price history, composition, price drivers, market events, and suppliers.

Forecasting, confidence scoring, recommendations, and supplier-claim analysis are implemented as deterministic Phase 2/3 services. Scenario simulation remains deferred and is exposed as a structured "not yet implemented" API response rather than fabricated numbers.

## 3. Architecture

```
Next.js (frontend) ──HTTP──> FastAPI (backend) ──SQLAlchemy──> SQLite (dev) / PostgreSQL (docker)
```

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + Recharts.
- **Backend**: FastAPI + Pydantic + SQLAlchemy 2.0 + Alembic.
- **Database**: SQLite for local dev (`backend/pricewise.db`), PostgreSQL via `docker-compose`.
- **ML/Intelligence**: `backend/app/ml/` and `backend/app/intelligence/` contain scaffolded, documented interfaces for Phase 2/4 work (driver model, ML residual model, ensemble, SHAP, confidence, LLM event extraction) — not yet implemented.

See [docs/architecture.md](docs/architecture.md) for the full component/data-flow diagram and [docs/data_dictionary.md](docs/data_dictionary.md) for every table/column.

## 4. Repository structure

```
pricewise/
├── backend/        FastAPI app, models, services, routes, ML/intelligence stubs, seed data, tests
├── frontend/        Next.js app, components, API client
├── data/            Generated demo CSVs (written by the seed script)
├── ml_artifacts/    Reserved for cached model artifacts (Phase 2+)
├── docs/            Architecture, data dictionary, demo script
└── docker-compose.yml
```

## 5. Setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\alembic upgrade head
.venv\Scripts\python -m app.seed.seed_database
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Copy `.env.example` to `.env` at the repo root first if you want to override defaults (SQLite is used out of the box, no `.env` required).

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`. The frontend calls the backend at `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).

### Docker (Postgres + backend + frontend)

```powershell
docker compose up --build
```

This runs migrations and seeds the database automatically on backend startup.

### Tests

```powershell
cd backend
.venv\Scripts\pytest -q
```

## 6. Demo data

Run `python -m app.seed.seed_database` (idempotent — safe to re-run). It generates:

- **4 materials**: Ceria CMP Slurry (complex, single-source, 48 months of history), Hydrogen Peroxide (commodity-driven, 42 months), Specialty Photoresist Polymer (sparse history — only 8 months, demonstrates LOW_DATA mode), Copper Sputtering Target (metal-index driven, 40 months).
- Material components, price drivers, and the component→driver knowledge graph edges.
- Correlated (noisy, not perfectly correlated) driver index series and derived price histories.
- Suppliers, supplier quotes (including the hero-narrative +9% claim on Ceria CMP Slurry), and market events.

The same data is written to `data/*.csv` for inspection.

## 7. ML methodology (implemented — Phase 2)

Per the roadmap, forecasting uses a **hybrid** approach rather than a single ML model, because historical data is limited:

1. **Baselines** (`app/ml/baselines.py`) — last value, moving average, exponential smoothing, seasonal naive.
2. **Driver model** (`app/ml/driver_model.py`) — Ridge regression: `price_pct_change = intercept + Σ(beta_i * driver_i_pct_change)`, features = drivers linked to the material's components via the knowledge graph (weighted by cost share × elasticity).
3. **ML residual model** (`app/ml/residual_model.py`) — LightGBM trained on `residual = actual_pct_change − driver_model_fitted_pct_change`. Skipped automatically below 18 monthly observations — this is what makes the Specialty Photoresist Polymer material fall back to driver model + baseline only.
4. **Ensemble** (`app/ml/ensemble.py`) — weighted combination of baseline/driver/driver+ML, weights from walk-forward (never random-split) validation (`app/ml/backtesting.py`); falls back to fixed driver-favoring weights when there's too little history to backtest at all (roadmap §10).
5. **Explainability** (`app/ml/explainability.py`) — driver contribution waterfall, with the full forecast move allocated across explainable economic drivers, plus a plain-English narrative. The ML residual is retained as an internal model component and is not exposed as a driver contribution. No LLM involved.

Forecasts are precomputed by the seed pipeline (`app/seed/generate_forecasts.py`) and lazily regenerated on first request if missing — never retrained on every page load.

## 8. Confidence methodology (implemented — Phase 2)

Five weighted components (`app/ml/confidence.py`), configurable in `app/core/config.py`:

```
overall = 0.20*data_quality + 0.25*driver_strength + 0.25*model_performance
        + 0.15*market_signal_quality + 0.15*forecast_stability
```

Clamped to 0–100. Data quality comes from the LOW_DATA/LIMITED_DATA/MODERATE/STRONG thresholds (§10); driver strength from the knowledge-graph relationship strength × confidence; model performance from walk-forward backtest directional accuracy/MAPE; market signals from related `MarketEvent` confidence/agreement; stability from model disagreement (§15) and a lightweight regime-change check (§25, last-3-month volatility vs. prior period). This is a decision-support heuristic, not a statistically validated probability — the UI always calls it "forecast confidence score."

## 9. Recommendation rules (implemented — Phase 3)

Rule-based (not LLM-driven) decision engine mapping forecast direction + confidence + supply risk to one of: `SHORT_LOCK`, `LONG_LOCK`, `WAIT`, `NEGOTIATE`, `STOCK`, `DUAL_SOURCE`, `MONITOR`. Recommendations persist an evidence trail from forecast, supplier risk, and market events. Supplier claims are compared with the forecasted market-supported change and classified as `SUPPORTED`, `PARTIALLY_SUPPORTED`, or `UNSUPPORTED`. See roadmap §20–21.

## 10. Phase plan

| Phase | Scope | Status |
|---|---|---|
| 1 | Repo, DB schema, migrations, seed data, FastAPI, Next.js, API client | ✅ Done |
| 2 | Driver model, baseline forecast, ML residual, ensemble, SHAP, confidence | ✅ Done |
| 3 | Recommendation engine, supplier claim analyzer, criticality, supply risk | ✅ Done |
| 4 | Market event model, mock LLM extraction, event impact, source quality | Not started |
| 5 | Scenario engine (what-if simulator) | Not started |
| 6 | UX polish (executive dashboard, evidence trail, waterfall charts) | Not started |

## 11. API documentation

Interactive OpenAPI docs are available at `http://localhost:8000/docs` once the backend is running. Implemented (real data) endpoints:

- `GET /api/materials`, `GET /api/materials/{id}`, `.../components`, `.../drivers`, `.../history`, `.../suppliers`, `.../supplier-claims`, `.../market-events`
- `GET /api/materials/{id}/forecast`, `.../forecast/explanation`, `.../confidence` — real (Phase 2), return a structured `insufficient_data` payload instead of a forecast when history is too sparse (< 3 observations)
- `POST /api/forecast` — real (Phase 2), same pipeline as the GET forecast endpoint
- `GET /api/drivers`, `GET /api/suppliers`, `GET /api/market/events`, `GET /api/dashboard/summary`

Stub (structured `not_implemented` response) endpoints, reserved for Phase 5:

- `POST /api/scenario`

## 12. Future improvements

See [§10 Phase plan](#10-phase-plan) and roadmap.md for the full backlog (driver/ML forecasting, confidence engine, recommendation engine, market intelligence pipeline, scenario simulator, evidence/audit trail, executive dashboard polish).
