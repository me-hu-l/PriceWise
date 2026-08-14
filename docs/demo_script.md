# Demo Script (Phase 1)

Phase 1 does not yet implement forecasting/confidence/recommendation (see roadmap §34 for the full future hero narrative). This script covers what is demonstrable **today**.

## Setup

1. `docker compose up --build` (or run backend + frontend locally per README §5).
2. Open `http://localhost:3000`.

## Walkthrough

1. **Executive control tower** (home page) — shows materials monitored, high/critical-criticality count, single-source count, and the full material list with criticality badges.
2. Click **Ceria CMP Slurry** (`MAT-001`).
   - Current price, lead time, single-source flag.
   - **Price history chart** — 48 months of realistic, noisy, driver-correlated price data.
   - **Material composition** — Ceria abrasive (42%), H2O2 (18%), Dispersant (12%), DI water + additives (28%).
   - **Price drivers** — the knowledge-graph edges to Rare Earth Index, Energy, Freight, FX, Chemical Feedstock, with relationship strength.
   - **Market intelligence** — the seeded "Rare-earth export restriction" and "Energy cost pressure" events.
   - **Suppliers** — Supplier A (Japan, 82% share) and Supplier B (South Korea, 18% share), illustrating supply concentration.
   - Forecast / Confidence / Recommendation cards are clearly labeled "Coming in Phase 2/3" — no fabricated numbers.
3. Click **Specialty Photoresist Polymer** (`MAT-003`) to see the **sparse-history** example (only 8 monthly observations) — this is the material Phase 2's LOW_DATA mode will apply to.
4. Inspect `GET /api/materials/1/supplier-claims` (via `/docs`) to see the seeded +9% supplier quote on Ceria CMP Slurry — the raw data Phase 3's supplier-claim analyzer will consume.

## What to say

> "This is the foundation: every material's cost structure, its economic drivers, its suppliers, and relevant market events are already modeled as a real knowledge graph in the database — not hardcoded in the UI. Phase 2 plugs a driver model + ML residual + ensemble into this graph to produce the forecast, confidence, and recommendation you'd expect to see next to it."
