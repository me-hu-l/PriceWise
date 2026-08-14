You are the lead software architect and senior full-stack/ML engineer for a semiconductor supply-chain hackathon project.

We are building a FABathon 2026 solution for Tata Electronics / TSMPL's:

"Material Price Intelligence & Forecasting Engine"

OFFICIAL PROBLEM:

Supply chain teams struggle to accurately forecast material prices because of:
- limited historical data
- fragmented market intelligence
- dependency on individual expertise

For critical semiconductor materials, the system should understand underlying cost drivers and predict future price movements to support:
- sourcing
- inventory planning
- contract negotiations

The platform must:
1. identify and track price drivers
2. provide prediction confidence scoring
3. integrate external market intelligence

The intended product is NOT merely a forecasting model.

It is an explainable Procurement Intelligence Platform.

CORE USER JOURNEY:

Material
→ Material/component breakdown
→ Price drivers
→ Historical/internal data
→ External market intelligence
→ Forecast
→ Forecast range
→ Explainability
→ Confidence
→ Supplier/market assessment
→ Procurement recommendation

IMPORTANT PRODUCT PRINCIPLE:

The system should answer four questions:

1. WHAT is likely to happen to the material price?
2. WHY is it likely to happen?
3. HOW CONFIDENT are we?
4. WHAT SHOULD PROCUREMENT DO?

Do not build a generic ML dashboard.
Do not make an LLM the numerical forecasting engine.
Do not over-engineer infrastructure.
Prioritize an excellent working demonstration.

==================================================
1. PRODUCT NAME
==================================================

Working name:

"PRICEWISE"

Subtitle:

"Material Price Intelligence & Procurement Decision Engine"

Keep the branding configurable so it can be changed later.

==================================================
2. TARGET USERS
==================================================

Primary:
- Procurement / sourcing teams
- Supply chain planners
- Category managers

Secondary:
- Supply chain leadership
- Finance
- Operations

A procurement manager should be able to open a material and understand its price outlook in under 30 seconds.

==================================================
3. CORE PRODUCT MODULES
==================================================

Build the system around these modules:

A. Material Intelligence
B. Material Composition / Breakdown
C. Driver Intelligence
D. Historical Price Intelligence
E. Forecasting Engine
F. Explainability Engine
G. Confidence Engine
H. External Market Intelligence
I. Supplier Intelligence
J. Procurement Decision Engine
K. Scenario Simulator
L. Dashboard / Visualization
M. Evidence / Audit Trail

==================================================
4. HIGH-LEVEL ARCHITECTURE
==================================================

Use:

Frontend:
- Next.js
- TypeScript
- Tailwind CSS
- Recharts or Plotly
- clean enterprise dashboard UI

Backend:
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

Database:
- PostgreSQL in production
- SQLite-compatible development mode if convenient

ML:
- Pandas
- NumPy
- scikit-learn
- LightGBM
- SHAP
- statsmodels if useful

LLM:
- provider abstraction
- do not hard-code one LLM provider
- optional integration
- system must work without LLM access

Recommended architecture:

                ┌───────────────────────┐
                │ Internal Procurement  │
                │ Data                  │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │ External Market Data  │
                │ FX / Commodity / News │
                └───────────┬───────────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │ Data / Feature     │
                 │ Layer              │
                 └─────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Material Knowledge  │
                │ Graph                │
                │                     │
                │ Material            │
                │ → Component         │
                │ → Driver            │
                │ → Supplier          │
                └──────────┬──────────┘
                           │
              ┌────────────┴─────────────┐
              ▼                          ▼
    ┌──────────────────┐       ┌───────────────────┐
    │ Forecast Engine  │       │ Market Intelligence│
    │                  │       │ Engine             │
    │ Baseline         │       │ News/event parsing │
    │ Driver model     │       │ Impact scoring     │
    │ ML residual      │       │                   │
    └─────────┬────────┘       └─────────┬─────────┘
              │                          │
              └───────────┬──────────────┘
                          ▼
                ┌────────────────────┐
                │ Confidence Engine  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Decision Engine    │
                │                    │
                │ LOCK               │
                │ WAIT               │
                │ NEGOTIATE          │
                │ STOCK              │
                │ DUAL-SOURCE        │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Next.js Dashboard  │
                └────────────────────┘

==================================================
5. REPOSITORY STRUCTURE
==================================================

Create a monorepo:

pricewise/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── materials.py
│   │   │   │   ├── forecasts.py
│   │   │   │   ├── drivers.py
│   │   │   │   ├── market.py
│   │   │   │   ├── suppliers.py
│   │   │   │   ├── recommendations.py
│   │   │   │   └── scenarios.py
│   │   │   └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   │
│   │   ├── schemas/
│   │   │   ├── material.py
│   │   │   ├── forecast.py
│   │   │   ├── driver.py
│   │   │   ├── market_event.py
│   │   │   ├── supplier.py
│   │   │   └── recommendation.py
│   │   │
│   │   ├── services/
│   │   │   ├── material_service.py
│   │   │   ├── driver_service.py
│   │   │   ├── forecast_service.py
│   │   │   ├── confidence_service.py
│   │   │   ├── market_service.py
│   │   │   ├── supplier_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── scenario_service.py
│   │   │
│   │   ├── ml/
│   │   │   ├── preprocessing.py
│   │   │   ├── baselines.py
│   │   │   ├── driver_model.py
│   │   │   ├── residual_model.py
│   │   │   ├── ensemble.py
│   │   │   ├── explainability.py
│   │   │   ├── confidence.py
│   │   │   └── backtesting.py
│   │   │
│   │   ├── intelligence/
│   │   │   ├── event_extractor.py
│   │   │   ├── event_impact.py
│   │   │   └── source_quality.py
│   │   │
│   │   └── seed/
│   │       ├── seed_database.py
│   │       └── demo_data.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── alembic/
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── materials/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── market/
│   │   │   └── page.tsx
│   │   └── scenarios/
│   │       └── page.tsx
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   ├── materials/
│   │   ├── forecast/
│   │   ├── drivers/
│   │   ├── market/
│   │   ├── recommendations/
│   │   └── common/
│   │
│   ├── lib/
│   │   ├── api.ts
│   │   └── types.ts
│   │
│   └── package.json
│
├── data/
│   ├── materials.csv
│   ├── material_components.csv
│   ├── drivers.csv
│   ├── component_drivers.csv
│   ├── price_history.csv
│   ├── market_indices.csv
│   ├── market_events.csv
│   ├── suppliers.csv
│   └── supplier_quotes.csv
│
├── ml_artifacts/
│   └── .gitkeep
│
└── docs/
    ├── architecture.md
    ├── data_dictionary.md
    └── demo_script.md

==================================================
6. DATABASE MODEL
==================================================

Create the following core entities.

--------------------------------------------------
6.1 MATERIAL
--------------------------------------------------

Material:

id
material_code
name
category
description
unit
currency
criticality
current_price
current_price_date
lead_time_days
single_source_flag
created_at
updated_at

Example:

MAT-001
Ceria CMP Slurry
CMP Consumable
USD/L
HIGH

--------------------------------------------------
6.2 MATERIAL COMPONENT
--------------------------------------------------

MaterialComponent:

id
material_id
component_name
component_code
percentage_of_cost
unit
description

Example:

Ceria abrasive
42%

H2O2
18%

Dispersant
12%

DI water + additives
28%

The composition must be represented as a graph/tree, not just flat text.

--------------------------------------------------
6.3 DRIVER
--------------------------------------------------

Driver:

id
name
category
description
unit
source_type
default_lag_days
directionality
reliability_score

Categories:

RAW_MATERIAL
ENERGY
FX
FREIGHT
LABOR
CAPACITY
SUPPLY
DEMAND
GEOPOLITICAL
REGULATORY
OTHER

--------------------------------------------------
6.4 COMPONENT DRIVER
--------------------------------------------------

ComponentDriver:

id
component_id
driver_id
relationship_strength
elasticity
lag_period
direction
confidence
rationale

Example:

Ceria abrasive
→ Rare Earth Index

relationship_strength = 0.87

This table is extremely important.

It represents the material knowledge graph.

--------------------------------------------------
6.5 PRICE HISTORY
--------------------------------------------------

PriceObservation:

id
material_id
date
price
currency
unit
supplier_id
quantity
contract_type
source
data_quality

--------------------------------------------------
6.6 DRIVER OBSERVATION
--------------------------------------------------

DriverObservation:

id
driver_id
date
value
unit
source
source_quality

--------------------------------------------------
6.7 MARKET EVENT
--------------------------------------------------

MarketEvent:

id
title
description
event_type
source_name
source_url
published_at
affected_driver
affected_material
impact_direction
impact_magnitude
impact_horizon
event_confidence
processed_by_llm
created_at

event_type examples:

SUPPLY_DISRUPTION
CAPACITY_EXPANSION
EXPORT_RESTRICTION
PRICE_CHANGE
ENERGY_EVENT
GEOPOLITICAL
NATURAL_DISASTER
REGULATORY
DEMAND_CHANGE
OTHER

--------------------------------------------------
6.8 SUPPLIER
--------------------------------------------------

Supplier:

id
name
supplier_code
country
qualification_status
lead_time_days
single_source
share_of_supply
risk_score

--------------------------------------------------
6.9 SUPPLIER QUOTE
--------------------------------------------------

SupplierQuote:

id
supplier_id
material_id
quote_date
quoted_price
currency
unit
previous_price
claimed_change_pct
reason
valid_until

This enables supplier claim validation.

--------------------------------------------------
6.10 FORECAST
--------------------------------------------------

Forecast:

id
material_id
forecast_date
target_date
horizon
point_forecast
lower_bound
upper_bound
direction
model_version
confidence_score
created_at

--------------------------------------------------
6.11 FORECAST CONTRIBUTION
--------------------------------------------------

ForecastContribution:

id
forecast_id
driver_id
contribution_value
contribution_pct
direction
rank

This stores SHAP/driver explanations.

--------------------------------------------------
6.12 CONFIDENCE COMPONENT
--------------------------------------------------

ConfidenceComponent:

id
forecast_id
data_score
driver_score
model_score
market_score
stability_score
overall_score
explanation

--------------------------------------------------
6.13 RECOMMENDATION
--------------------------------------------------

Recommendation:

id
material_id
forecast_id
action
conviction
recommended_duration
reason
created_at

Actions:

LOCK
SHORT_LOCK
WAIT
NEGOTIATE
STOCK
DUAL_SOURCE
MONITOR

--------------------------------------------------
6.14 EVIDENCE
--------------------------------------------------

Evidence:

id
recommendation_id
evidence_type
title
description
source
weight
created_at

Evidence types:

PRICE_HISTORY
DRIVER
MARKET_EVENT
SUPPLIER
FORECAST
SUPPLY_RISK
MODEL

==================================================
7. MATERIAL / DRIVER ONTOLOGY
==================================================

The most important conceptual structure is:

Material
    ↓
Component
    ↓
Driver
    ↓
External signal
    ↓
Price impact

Example:

CMP Slurry
│
├── Ceria abrasive
│   ├── Rare-earth index
│   ├── Mining supply
│   ├── Export restrictions
│   └── FX
│
├── Oxidizer
│   ├── H2O2 price
│   └── Energy
│
├── Dispersant
│   ├── Chemical feedstock
│   └── Energy
│
└── Logistics
    ├── Freight
    ├── Fuel
    └── FX

Do not hard-code this only into frontend components.

Represent it in the database.

==================================================
8. FORECASTING STRATEGY
==================================================

IMPORTANT:

Do NOT make XGBoost/LightGBM the sole forecasting model.

Because the problem explicitly involves limited historical data.

Use a hybrid approach.

--------------------------------------------------
8.1 BASELINE MODELS
--------------------------------------------------

Implement:

1. Last value
2. Moving average
3. Exponential smoothing
4. Seasonal naive if applicable

These are benchmark models.

--------------------------------------------------
8.2 DRIVER MODEL
--------------------------------------------------

Create an economically interpretable driver model.

Conceptually:

price_change =
    beta_1 * driver_1_change
  + beta_2 * driver_2_change
  + ...
  + error

Use regularization where necessary.

The driver model should produce:

- forecast
- driver contributions
- sensitivity
- confidence

--------------------------------------------------
8.3 ML RESIDUAL MODEL
--------------------------------------------------

Train LightGBM on:

residual =
actual_price - driver_model_prediction

Features can include:

- lagged price
- rolling mean
- rolling volatility
- driver changes
- driver lags
- seasonality
- market event scores
- supplier signals

The ML model predicts the residual.

Final:

final_forecast =
driver_forecast + ML_residual_forecast

This is much more explainable than directly asking LightGBM to predict price.

--------------------------------------------------
8.4 ENSEMBLE
--------------------------------------------------

Allow:

baseline
+
driver model
+
ML residual

to form a weighted ensemble.

Weights should be determined from rolling validation performance.

Do not use random train/test split.

Use time-series / walk-forward validation.

==================================================
9. FORECAST OUTPUT
==================================================

Never return only a point prediction.

Return:

point forecast
lower bound
upper bound
direction
confidence
top drivers
model performance

Example:

Current:
₹1,240/kg

Q3 Forecast:
₹1,324/kg

Expected change:
+6.8%

Range:
₹1,270 - ₹1,390

Direction:
INCREASING

Confidence:
78%

Top drivers:
1. Ceria / rare earth +4.1%
2. Energy +1.2%
3. Freight +0.8%
4. FX +0.7%

==================================================
10. LOW-DATA MODE
==================================================

This is a critical feature.

If historical observations are insufficient:

DO NOT pretend the ML model is highly confident.

Define a minimum data threshold.

For example:

< 12 observations:
LOW_DATA mode

12–24:
LIMITED_DATA

24–48:
MODERATE

> 48:
STRONG

These thresholds should be configurable.

In LOW_DATA mode:

increase weight on:
- driver model
- comparable materials
- external market signals

decrease weight on:
- historical ML

Show:

"LOW DATA MODE"

and explain why confidence is reduced.

==================================================
11. COMPARABLE MATERIAL INTELLIGENCE
==================================================

If target material has sparse history, allow comparable materials.

Represent:

target material
→ shared component
→ comparable material

Example:

Material A:
Ceria component

Material B:
Ceria component

Material B has longer history.

Use B as supporting evidence, not as direct replacement.

UI:

"Comparable material signal"

Material B
Historical trend:
+5.2%

Relevance:
72%

==================================================
12. EXPLAINABILITY
==================================================

Use SHAP for the ML residual component.

But do not rely only on SHAP.

The final explanation should combine:

1. Economic driver contribution
2. ML contribution
3. Market event evidence

Example:

Forecast:
+6.8%

Explanation:

Ceria / rare-earth:
+4.1%

Energy:
+1.2%

Freight:
+0.8%

FX:
+0.7%

ML residual:
0.0%

Create a waterfall chart.

Also expose "Why?"

==================================================
13. CONFIDENCE ENGINE
==================================================

Confidence must be explainable.

Do not simply output a random percentage.

Create five components:

A. Data quality
B. Driver strength
C. Model performance
D. Market signal quality
E. Forecast stability

Example:

Data quality       82
Driver strength    91
Model performance  74
Market signals     67
Stability          80

Overall confidence:
78%

Create a transparent configurable formula.

For MVP:

overall =
0.20 * data
+ 0.25 * driver
+ 0.25 * model
+ 0.15 * market
+ 0.15 * stability

Clamp to 0–100.

Document the formula.

This formula is a prototype decision framework, not a scientifically validated probability.

UI must call it:

"Forecast confidence score"

not:

"Probability that forecast is correct"

==================================================
14. CONFIDENCE PENALTIES
==================================================

Confidence should decrease when:

- historical data is sparse
- model disagreement is high
- drivers disagree
- recent regime change occurs
- external data is stale
- market events are contradictory
- supplier information is missing

Confidence should increase when:

- multiple models agree
- driver relationships are historically strong
- recent data is available
- market signals agree
- rolling backtest is strong

==================================================
15. MODEL DISAGREEMENT
==================================================

Expose:

Baseline:
+2.8%

Driver model:
+5.1%

ML model:
+6.2%

Ensemble:
+5.0%

Disagreement:
MEDIUM

This disagreement should influence confidence.

==================================================
16. MARKET INTELLIGENCE
==================================================

The market intelligence layer must convert unstructured information into structured events.

Pipeline:

News / report
    ↓
LLM extraction
    ↓
event
    ↓
affected commodity/driver
    ↓
affected material
    ↓
direction
    ↓
magnitude
    ↓
time horizon
    ↓
confidence
    ↓
forecast impact

LLM should NOT directly produce numerical material price forecasts.

It should extract and classify information.

==================================================
17. MARKET EVENT SCHEMA
==================================================

Each event should contain:

title
summary
source
published date
affected commodity
affected driver
affected material
direction:
  UP
  DOWN
  NEUTRAL

magnitude:
  LOW
  MEDIUM
  HIGH

horizon:
  SHORT
  MEDIUM
  LONG

confidence:
  0–100

Example:

Event:
"Rare-earth export restriction announced"

Affected driver:
Rare Earth Index

Affected material:
Ceria CMP Slurry

Direction:
UP

Magnitude:
HIGH

Horizon:
MEDIUM

Confidence:
82

==================================================
18. SOURCE QUALITY
==================================================

Every external source should have a source-quality score.

Example:

Government source:
95

Major financial/news source:
90

Industry publication:
80

Supplier communication:
75

General news:
65

Unknown:
40

These are prototype weights and should be configurable.

==================================================
19. MARKET EVENT IMPACT
==================================================

Do not blindly add news impacts.

Use:

event
→ affected driver
→ driver relevance to material
→ estimated impact
→ confidence

Example:

Export restriction
↓
Rare-earth driver
↓
Ceria component
↓
42% material composition
↓
expected price pressure

This produces a traceable chain.

==================================================
20. SUPPLIER CLAIM VALIDATION
==================================================

This is a key differentiator.

Allow procurement user to enter:

Supplier:
Supplier A

Material:
Ceria Slurry

Current:
₹1,240/kg

Supplier requested:
₹1,352/kg

Claim:
+9.0%

System calculates:

Market-supported increase:
+6.2%

Unexplained:
+2.8%

Assessment:

PARTIALLY SUPPORTED

Recommendation:

"Use market-supported range as negotiation anchor."

This should be a first-class feature.

==================================================
21. PROCUREMENT DECISION ENGINE
==================================================

Possible actions:

SHORT_LOCK
LONG_LOCK
WAIT
NEGOTIATE
STOCK
DUAL_SOURCE
MONITOR

Inputs:

forecast direction
forecast confidence
forecast range
price volatility
supplier concentration
lead time
material criticality
market event risk
single-source status
inventory coverage

Rules should be transparent.

Example:

IF:
forecast ↑
AND confidence HIGH
AND supply risk HIGH
THEN:
SECURE / SHORT_LOCK

IF:
forecast ↑
AND confidence HIGH
AND supply risk LOW
THEN:
NEGOTIATE / PARTIAL_LOCK

IF:
forecast ↓
AND confidence HIGH
AND supply risk LOW
THEN:
WAIT

IF:
price stable
AND supply risk HIGH
THEN:
DUAL_SOURCE / SECURE

Do not let the LLM determine these decisions.

==================================================
22. MATERIAL CRITICALITY
==================================================

Create a criticality score.

Factors:

production impact
lead time
single-source risk
qualification difficulty
supplier concentration

Example:

criticality_score =
weighted combination of above

Display:

LOW
MEDIUM
HIGH
CRITICAL

==================================================
23. SUPPLIER RISK
==================================================

Include:

supplier concentration
number of qualified suppliers
lead time
qualification status
historical reliability if data exists

Example:

Supplier A:
82% share

Supplier B:
18%

System:

"High concentration risk"

==================================================
24. SCENARIO ENGINE
==================================================

Build a simple what-if simulator.

Inputs:

FX change
energy change
raw material change
freight change
market shock

Example:

BASE:
FX +1%
Energy +2%
Raw material +3%

Forecast:
+3.8%

BULL:
FX +4%
Energy +8%
Raw material +10%

Forecast:
+11.2%

BEAR:
FX -2%
Energy -5%
Raw material -6%

Forecast:
-7.4%

The scenario engine must reuse the driver model.

Do not create an unrelated fake calculator.

==================================================
25. REGIME CHANGE
==================================================

Implement a lightweight regime-change indicator.

Possible signals:

- driver distribution shift
- price volatility spike
- model residual spike
- unusual market event

If regime change detected:

reduce confidence.

UI:

"⚠ Market regime changed"

"Historical model reliability may be reduced."

This is more important than pretending historical accuracy always applies.

==================================================
26. TIME-SERIES VALIDATION
==================================================

Never use random train/test splitting for the forecasting pipeline.

Use walk-forward validation.

Example:

Train:
2022-01 → 2023-12

Test:
2024-01 → 2024-06

Then:

Train:
2022-01 → 2024-06

Test:
2024-07 → 2024-12

Metrics:

MAE
RMSE
MAPE when appropriate
directional accuracy
prediction interval coverage

==================================================
27. FORECAST METRICS
==================================================

Display:

MAE:
X

MAPE:
X%

Directional accuracy:
X%

Interval coverage:
X%

Do not claim "accuracy" from a single metric.

==================================================
28. DATA LEAKAGE PROTECTION
==================================================

Every observation must have a timestamp.

At forecast time T:

ONLY use information available before T.

External news must use:

published_at

not:

retrieved_at

Document this explicitly.

==================================================
29. API DESIGN
==================================================

Implement REST APIs.

GET /api/materials

GET /api/materials/{id}

GET /api/materials/{id}/components

GET /api/materials/{id}/drivers

GET /api/materials/{id}/history

GET /api/materials/{id}/forecast

GET /api/materials/{id}/forecast/explanation

GET /api/materials/{id}/confidence

GET /api/materials/{id}/recommendation

GET /api/materials/{id}/market-events

GET /api/materials/{id}/suppliers

GET /api/materials/{id}/supplier-claims

POST /api/forecast

POST /api/scenario

POST /api/supplier-claim/analyze

GET /api/dashboard/summary

GET /api/market/events

==================================================
30. DASHBOARD
==================================================

Build these screens.

--------------------------------------------------
30.1 EXECUTIVE CONTROL TOWER
--------------------------------------------------

Cards:

Materials monitored
Increasing
Decreasing
High-risk materials
Actions required

Then:

"Action Required"

Material
Forecast
Confidence
Supply risk
Recommendation

--------------------------------------------------
30.2 MATERIAL EXPLORER
--------------------------------------------------

Search/select material.

Show:

Material name
Current price
Forecast
Confidence
Criticality
Supply risk

--------------------------------------------------
30.3 MATERIAL DRILLDOWN
--------------------------------------------------

Sections:

1. Price history + forecast chart
2. Forecast range
3. Component breakdown
4. Driver contribution waterfall
5. Market intelligence
6. Supplier information
7. Recommendation
8. Evidence

--------------------------------------------------
30.4 DRIVER ANALYSIS
--------------------------------------------------

Show:

driver
current value
trend
relationship strength
material impact
source

--------------------------------------------------
30.5 MARKET INTELLIGENCE
--------------------------------------------------

Cards:

event
affected material
impact
direction
confidence
source
date

--------------------------------------------------
30.6 SCENARIO SIMULATOR
--------------------------------------------------

Sliders/inputs:

FX
energy
raw material
freight

Output:

expected price
range
recommendation

--------------------------------------------------
30.7 SUPPLIER CLAIM ANALYZER
--------------------------------------------------

Input:

supplier
material
current price
claimed increase
reason

Output:

market-supported increase
unexplained increase
assessment
negotiation guidance

==================================================
31. HERO UI
==================================================

The material drilldown should look approximately like:

CERIA CMP SLURRY                         ⚠ ACTION

Current price:
₹1,240/kg

Forecast:
+6.8%

Range:
₹1,270–₹1,390

Confidence:
78%

Supply risk:
HIGH

WHY IS PRICE MOVING?

Ceria / Rare Earth       +4.1%
Energy                    +1.2%
Freight                   +0.8%
FX                        +0.7%
Dispersant                 0.0%

MARKET SIGNALS

🔴 Rare-earth supply restriction
🟡 Energy cost pressure

RECOMMENDATION

SHORT LOCK — 3 MONTHS

Conviction:
72%

Reason:
- high supply concentration
- strong raw material pressure
- long lead time
- expected easing later

==================================================
32. DEMO MATERIALS
==================================================

Seed 3–5 realistic demonstration materials.

At least:

1. CMP Slurry / Ceria

Complex material.

2. Hydrogen Peroxide / relevant chemical

Commodity-driven.

3. A sparse-history specialty material

Demonstrates LOW DATA MODE.

4. Optional second semiconductor consumable.

IMPORTANT:

Use clearly labelled synthetic/demo data unless real internal data is explicitly authorized.

Never imply synthetic data is actual Tata procurement data.

==================================================
33. DEMO DATA GENERATION
==================================================

Generate 36–60 monthly observations for strong demo materials.

Generate 6–10 observations for sparse material.

Create correlated driver series.

Example:

Ceria slurry price influenced by:

rare-earth index
energy
freight
FX

Do not create perfectly correlated data.

Add realistic noise.

Create a few events:

- supply disruption
- export restriction
- capacity expansion
- energy shock

These should visibly affect forecasts.

==================================================
34. DEMO STORY
==================================================

The primary demo should be:

SUPPLIER REQUESTS:
+9% PRICE INCREASE

User opens PRICEWISE.

Step 1:
Select material.

Step 2:
System decomposes material.

Step 3:
Shows driver contribution.

Step 4:
Shows market event.

Step 5:
Forecast says:

+6.8%

Step 6:
Confidence:

78%

Step 7:
System compares:

Supplier claim:
+9.0%

Market-supported:
+6.2%

Unexplained:
+2.8%

Step 8:
Recommendation:

"Negotiate toward 6–7% and secure 3 months."

Step 9:
Show evidence.

This is the hero narrative.

==================================================
35. FRONTEND DESIGN
==================================================

Style:

Enterprise
Clean
Professional
Semiconductor / supply-chain aesthetic

Avoid:

- excessive gradients
- excessive animations
- gimmicky AI visuals
- dark hacker aesthetic
- clutter

Use:

- white/light neutral background
- cards
- clear typography
- restrained accent colors
- clear red/yellow/green risk indicators
- high information density

Responsive desktop-first.

==================================================
36. UX PRINCIPLE
==================================================

A user should answer within 30 seconds:

WHAT?
WHY?
HOW SURE?
WHAT SHOULD I DO?

Every material page should prioritize those four.

==================================================
37. LLM ABSTRACTION
==================================================

Create:

LLMProvider interface.

Methods:

extract_market_event(text)
summarize_event(event)
generate_explanation(structured_evidence)

Implement:

MockLLMProvider

first.

Optional:

OpenAIProvider
AnthropicProvider

later.

The system must function without external LLM access.

==================================================
38. LLM SAFETY / TRUST
==================================================

LLM output must never overwrite:

- price
- forecast
- confidence
- recommendation

LLM only explains structured facts.

All generated explanations must include source/evidence references where available.

==================================================
39. PERFORMANCE
==================================================

Precompute demo forecasts.

Do not retrain models on every page load.

Use:

forecast cache

and:

material-level precomputed artifacts.

API should feel instantaneous for demo.

==================================================
40. ERROR HANDLING
==================================================

If forecast unavailable:

show:

"Insufficient data for reliable forecast."

Then show:

available driver intelligence
market signals
low-data assessment

Do not fabricate a forecast.

If market data unavailable:

show:

"Market intelligence unavailable as of <date>"

and reduce confidence.

==================================================
41. TESTING
==================================================

At minimum:

Unit tests for:

- driver calculations
- confidence calculation
- recommendation rules
- scenario engine
- forecast response schema

ML tests:

- no future leakage
- time-series split
- prediction output valid
- bounds correctly ordered

API tests:

- materials
- forecasts
- recommendations
- scenarios

==================================================
42. DOCUMENTATION
==================================================

README must contain:

1. Problem
2. Solution
3. Architecture
4. Setup
5. Running locally
6. Demo data
7. ML methodology
8. Confidence methodology
9. Recommendation rules
10. API documentation
11. Future improvements

Also create:

docs/architecture.md

docs/data_dictionary.md

docs/demo_script.md

==================================================
43. ENVIRONMENT
==================================================

Create .env.example:

DATABASE_URL=
LLM_PROVIDER=
LLM_API_KEY=
MARKET_DATA_API_KEY=
NEXT_PUBLIC_API_URL=

Do not commit secrets.

==================================================
44. DOCKER
==================================================

Provide:

docker-compose.yml

services:

postgres
backend
frontend

But ensure local development can also run without Docker if possible.

==================================================
45. SEEDING
==================================================

Provide:

python -m app.seed.seed_database

This should:

- create materials
- create components
- create drivers
- create relationships
- create suppliers
- create price history
- create driver observations
- create market events
- create demo forecasts
- create recommendations

One command should create the full demo.

==================================================
46. INITIAL BOILERPLATE PRIORITY
==================================================

For the first implementation, DO NOT attempt to implement every sophisticated feature.

Phase 1 must produce a working vertical slice:

Material
→ components
→ drivers
→ price history
→ forecast
→ confidence
→ explanation
→ recommendation
→ dashboard

Everything else can be stubbed behind interfaces.

==================================================
47. PHASE PLAN
==================================================

PHASE 1 — Foundation

- repository
- database
- models
- migrations
- seed data
- FastAPI
- Next.js
- API client

PHASE 2 — Core intelligence

- driver model
- baseline forecast
- residual ML
- ensemble
- SHAP
- confidence

PHASE 3 — Decision intelligence

- recommendation engine
- supplier claim analyzer
- criticality
- supply risk

PHASE 4 — Market intelligence

- market event model
- mock event extraction
- event impact
- source quality

PHASE 5 — Scenario engine

- what-if analysis

PHASE 6 — UX polish

- executive dashboard
- material drilldown
- charts
- evidence trail

==================================================
48. ACCEPTANCE CRITERIA
==================================================

The boilerplate is considered successful when:

1. `docker compose up` works.

2. Backend starts.

3. Frontend starts.

4. Database initializes.

5. Seed command works.

6. Dashboard displays seeded materials.

7. Clicking a material displays:
   - current price
   - historical chart
   - forecast
   - confidence
   - components
   - drivers
   - explanation
   - recommendation

8. Scenario endpoint works.

9. Supplier claim endpoint works.

10. No external API is required for the base demo.

11. All data is clearly labelled as demo/synthetic where appropriate.

==================================================
49. IMPORTANT ENGINEERING PRINCIPLES
==================================================

1. Keep business logic out of React.

2. Keep forecasting logic out of API routes.

3. Use service classes/modules.

4. Keep ML code independently testable.

5. Keep database models separate from API schemas.

6. Use typed schemas.

7. No hardcoded UI-only business rules.

8. Configuration-driven thresholds.

9. No secrets in source control.

10. Every forecast should have a model version.

11. Every market event should have a source.

12. Every recommendation should have evidence.

13. Every confidence score should be explainable.

14. Never fabricate data.

15. Never use future data in historical forecasting.

==================================================
50. MOST IMPORTANT PRODUCT PRINCIPLE
==================================================

The product should not say:

"AI predicts material prices."

It should say:

"PRICEWISE combines material composition, market drivers, historical signals and external intelligence to produce explainable price outlooks and procurement actions."

The final system should make the user feel:

"I understand what is happening,
I understand why,
I know how much to trust it,
and I know what action I should take."

==================================================
51. CLAUDE EXECUTION INSTRUCTION
==================================================

Do NOT simply describe the architecture back to me.

Start generating the actual repository.

First:

1. Create the complete directory structure.
2. Create backend FastAPI skeleton.
3. Create SQLAlchemy models.
4. Create Pydantic schemas.
5. Create database initialization.
6. Create Alembic configuration.
7. Create seed data generator.
8. Create demo CSV/data files.
9. Create core service interfaces.
10. Create baseline forecasting implementation.
11. Create confidence implementation.
12. Create recommendation engine.
13. Create API routes.
14. Create Next.js frontend.
15. Create dashboard.
16. Create material drilldown.
17. Connect frontend to backend.
18. Add tests.
19. Add README.
20. Add Docker Compose.

DO NOT implement fake functionality merely to make endpoints return random values.

Where sophisticated functionality is not yet implemented, create a clean interface/stub with TODO documentation and deterministic demo behavior.

The application must run end-to-end with demo data.

After generating the boilerplate, provide:

A. Exact commands to run it
B. Repository tree
C. What is implemented
D. What remains
E. Suggested next implementation steps

Prioritize a working vertical slice over completeness.