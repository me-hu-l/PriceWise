# Data Dictionary

All tables live in `backend/app/db/models/`. Types shown are logical (SQLAlchemy maps them to the active dialect — SQLite or PostgreSQL).

## Material
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| material_code | string, unique | e.g. `MAT-001` |
| name | string | |
| category | string | e.g. "CMP Consumable" |
| description | string, nullable | |
| unit | string | e.g. `L`, `kg` |
| currency | string | ISO code |
| criticality | string | `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` |
| current_price | float | |
| current_price_date | date | |
| lead_time_days | int | |
| single_source_flag | bool | |
| created_at / updated_at | datetime | |

## MaterialComponent
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| material_id | FK → Material | |
| component_name | string | |
| component_code | string, nullable | |
| percentage_of_cost | float | 0–100 |
| unit | string, nullable | |
| description | string, nullable | |

## Driver
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| name | string | |
| category | string | `RAW_MATERIAL`, `ENERGY`, `FX`, `FREIGHT`, `LABOR`, `CAPACITY`, `SUPPLY`, `DEMAND`, `GEOPOLITICAL`, `REGULATORY`, `OTHER` |
| description | string, nullable | |
| unit | string, nullable | |
| source_type | string, nullable | |
| default_lag_days | int | |
| directionality | string, nullable | `POSITIVE` / `NEGATIVE` |
| reliability_score | float, nullable | |

## ComponentDriver (knowledge-graph edge)
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| component_id | FK → MaterialComponent | |
| driver_id | FK → Driver | |
| relationship_strength | float | 0–1 |
| elasticity | float, nullable | |
| lag_period | int | days |
| direction | string | `POSITIVE` / `NEGATIVE` |
| confidence | float, nullable | |
| rationale | string, nullable | human-readable explanation |

## PriceObservation
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| material_id | FK → Material | |
| date | date | |
| price | float | |
| currency | string | |
| unit | string, nullable | |
| supplier_id | FK → Supplier, nullable | |
| quantity | float, nullable | |
| contract_type | string, nullable | |
| source | string, nullable | |
| data_quality | string, nullable | e.g. `SYNTHETIC` |

## DriverObservation
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| driver_id | FK → Driver | |
| date | date | |
| value | float | |
| unit | string, nullable | |
| source | string, nullable | |
| source_quality | float, nullable | |

## MarketEvent
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| title | string | |
| description | string, nullable | |
| event_type | string | `SUPPLY_DISRUPTION`, `CAPACITY_EXPANSION`, `EXPORT_RESTRICTION`, `PRICE_CHANGE`, `ENERGY_EVENT`, `GEOPOLITICAL`, `NATURAL_DISASTER`, `REGULATORY`, `DEMAND_CHANGE`, `OTHER` |
| source_name / source_url | string, nullable | |
| published_at | datetime | used for point-in-time correctness (never `retrieved_at`) |
| affected_driver / affected_material | string, nullable | matched by name in Phase 1 |
| impact_direction | string | `UP` / `DOWN` / `NEUTRAL` |
| impact_magnitude | string | `LOW` / `MEDIUM` / `HIGH` |
| impact_horizon | string | `SHORT` / `MEDIUM` / `LONG` |
| event_confidence | float, nullable | 0–100 |
| processed_by_llm | bool | |
| created_at | datetime | |

## Supplier
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| name | string | |
| supplier_code | string, unique | |
| country | string, nullable | |
| qualification_status | string | |
| lead_time_days | int, nullable | |
| single_source | bool | |
| share_of_supply | float, nullable | 0–1 |
| risk_score | float, nullable | |

## SupplierQuote
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| supplier_id | FK → Supplier | |
| material_id | FK → Material | |
| quote_date | date | |
| quoted_price | float | |
| currency / unit | string | |
| previous_price | float, nullable | |
| claimed_change_pct | float, nullable | |
| reason | string, nullable | |
| valid_until | date, nullable | |

## Forecast *(Phase 2 — table exists, unpopulated)*
`material_id`, `forecast_date`, `target_date`, `horizon`, `point_forecast`, `lower_bound`, `upper_bound`, `direction`, `model_version`, `confidence_score`.

## ForecastContribution *(Phase 2)*
`forecast_id`, `driver_id`, `contribution_value`, `contribution_pct`, `direction`, `rank`.

## ConfidenceComponent *(Phase 2)*
`forecast_id`, `data_score`, `driver_score`, `model_score`, `market_score`, `stability_score`, `overall_score`, `explanation`.

## Recommendation *(Phase 3 — table exists, unpopulated)*
`material_id`, `forecast_id`, `action` (`LOCK`/`SHORT_LOCK`/`WAIT`/`NEGOTIATE`/`STOCK`/`DUAL_SOURCE`/`MONITOR`), `conviction`, `recommended_duration`, `reason`.

## Evidence *(Phase 3)*
`recommendation_id`, `evidence_type`, `title`, `description`, `source`, `weight`.
