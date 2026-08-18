# Demo Script

## Setup

1. `docker compose up --build` (or run backend + frontend locally per README §5).
2. Open `http://localhost:3000`.

## Walkthrough

1. **Executive control tower** (home page) — shows materials monitored, high/critical-criticality count, single-source count, and the full material list with criticality badges.
2. Click **Ceria CMP Slurry** (`MAT-001`).
   - Current price, lead time, single-source flag.
   - **Forecast** — point forecast, range, direction, and a "LOW DATA MODE" badge if applicable.
   - **Forecast confidence score** — the five-component breakdown (data quality, driver strength, model performance, market signals, stability) with a plain-English explanation.
   - **Why is price moving?** — the driver contribution waterfall (Rare Earth Index, Energy, Freight, FX, plus an "ML Residual" line) with a narrative summary.
   - **Model disagreement** — baseline vs. driver vs. ML pct-change forecasts, disagreement level, and backtest metrics (MAE/MAPE/directional accuracy).
   - **Price history chart** — 48 months of realistic, noisy, driver-correlated price data.
   - **Material composition**, **Price drivers** (knowledge graph), **Market intelligence**, **Suppliers**.
   - Recommendation card is clearly labeled "Coming in Phase 3" — no fabricated action yet.
3. Click **Specialty Photoresist Polymer** (`MAT-003`) to see the **LOW_DATA mode** in action — only 8 monthly observations, so the ML residual model is skipped entirely and the confidence breakdown shows a lower data-quality score.
4. Inspect `GET /api/materials/1/supplier-claims` (via `/docs`) to see the seeded +9% supplier quote on Ceria CMP Slurry — Phase 3's supplier-claim analyzer will compare this against the forecast.

## What to say

> "Every material's cost structure, economic drivers, suppliers, and market events are modeled as a real knowledge graph in the database. On top of that, a driver model plus an ML residual model plus a baseline are combined into an ensemble whose weights come from walk-forward backtesting — not a single black-box prediction. The confidence score and the driver waterfall explain exactly why, and how much to trust it. Phase 3 turns this into a procurement recommendation."

