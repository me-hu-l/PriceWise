# Architecture

## Component overview

```
┌─────────────────────┐        ┌──────────────────────┐
│  Next.js frontend    │  HTTP  │   FastAPI backend    │
│  (App Router, TS,    │───────>│   app/api/routes/*    │
│  Tailwind, Recharts)  │<───────│   app/services/*      │
└─────────────────────┘  JSON   │   app/db/models/*     │
                                 │   app/ml/* (stubs)    │
                                 │   app/intelligence/*  │
                                 │   (stubs)             │
                                 └──────────┬────────────┘
                                            │ SQLAlchemy
                                            ▼
                              ┌───────────────────────────┐
                              │ SQLite (dev) / PostgreSQL  │
                              │ (docker-compose)           │
                              └───────────────────────────┘
```

## Backend layering

- **`app/db/models/`** — SQLAlchemy ORM models, one file per domain (material, driver, price, market_event, supplier, forecast, recommendation). This is the source of truth for the schema; Alembic migrations are generated from it.
- **`app/schemas/`** — Pydantic request/response models. Kept separate from ORM models so the API contract can evolve independently of storage.
- **`app/services/`** — business logic / DB queries. Routes never touch the DB directly. Phase 1 services (`material_service`, `driver_service`, `market_service`, `supplier_service`) are real; Phase 2+ services (`forecast_service`, `confidence_service`, `recommendation_service`, `scenario_service`) are stubs that return a structured `NotImplementedResponse` instead of fabricated data.
- **`app/api/routes/`** — thin FastAPI route handlers, one file per resource, aggregated in `app/api/router.py`.
- **`app/ml/`** — forecasting internals (baselines, driver model, residual model, ensemble, explainability, confidence, backtesting). All Phase 2 stubs today, documented with the exact roadmap section they implement.
- **`app/intelligence/`** — market intelligence pipeline (event extraction, event impact chain, source quality). Phase 4 stubs.
- **`app/seed/`** — `demo_data.py` (pure data generation, no DB dependency) + `seed_database.py` (writes to DB and mirrors to `data/*.csv`).

## Material knowledge graph

The core domain model is a graph, not a flat table:

```
Material → MaterialComponent → ComponentDriver (edge) → Driver
```

`ComponentDriver` rows carry `relationship_strength`, `elasticity`, `lag_period`, `direction`, and `confidence` — this is what Phase 2's driver model will consume directly, and what the frontend's driver-contribution view (`GET /api/materials/{id}/drivers`) already exposes.

## Why forecasting is not in Phase 1

The roadmap explicitly prioritizes a working vertical slice over a fake forecasting demo. Phase 1 builds every table Phase 2+ needs (`Forecast`, `ForecastContribution`, `ConfidenceComponent`, `Recommendation`, `Evidence`) but leaves them unpopulated, and the corresponding API endpoints return a structured "not implemented" payload rather than random or hardcoded numbers. See `app/schemas/common.py::NotImplementedResponse`.

## Dev vs. prod-like database

`app/db/database.py` builds a SQLAlchemy engine from `DATABASE_URL` alone, so the exact same models/migrations work against both SQLite (`sqlite:///./pricewise.db`, the local dev default) and PostgreSQL (`postgresql+psycopg2://...`, used in `docker-compose.yml`). No dialect-specific column types are used in the models.
