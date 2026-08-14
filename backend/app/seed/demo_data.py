"""Synthetic demo data generator for PriceWise (roadmap sections 32-33).

Produces plain dict/list structures (no DB/ORM dependency) so the same data
can be written to CSV and inserted into the database from a single source of
truth. All data is clearly synthetic — never implied to be real Tata data.

Reproducible via a fixed RNG seed. Deterministic across runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np

SEED = 42
END_DATE = date(2026, 8, 1)  # "current" month for demo purposes


def _month_range(n_months: int, end_date: date = END_DATE) -> list[date]:
    """n_months dates, first-of-month, ending at end_date (inclusive)."""
    months = []
    year, month = end_date.year, end_date.month
    for _ in range(n_months):
        months.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


def _random_walk_index(
    rng: np.random.Generator,
    n_months: int,
    start_value: float,
    drift: float,
    volatility: float,
    shock_at: int | None = None,
    shock_pct: float = 0.0,
) -> list[float]:
    """Monthly index series: geometric random walk + drift + one optional shock."""
    values = [start_value]
    for month_idx in range(1, n_months):
        pct_change = drift + rng.normal(0, volatility)
        if shock_at is not None and month_idx == shock_at:
            pct_change += shock_pct
        values.append(values[-1] * (1 + pct_change))
    return values


# ---------------------------------------------------------------------------
# Drivers (shared catalog, roadmap section 6.3)
# ---------------------------------------------------------------------------

DRIVER_DEFS = [
    {
        "key": "rare_earth_index",
        "name": "Rare Earth Index",
        "category": "RAW_MATERIAL",
        "description": "Global rare-earth oxide price index (cerium, lanthanum basket).",
        "unit": "index (base 100)",
        "source_type": "commodity_index",
        "default_lag_days": 30,
        "directionality": "POSITIVE",
        "reliability_score": 0.8,
        "start_value": 100.0,
        "drift": 0.004,
        "volatility": 0.03,
    },
    {
        "key": "energy_price_index",
        "name": "Energy Price Index",
        "category": "ENERGY",
        "description": "Composite industrial energy price index (electricity + natural gas).",
        "unit": "index (base 100)",
        "source_type": "commodity_index",
        "default_lag_days": 15,
        "directionality": "POSITIVE",
        "reliability_score": 0.85,
        "start_value": 100.0,
        "drift": 0.003,
        "volatility": 0.025,
    },
    {
        "key": "freight_index",
        "name": "Freight Index",
        "category": "FREIGHT",
        "description": "Global container/bulk freight rate index.",
        "unit": "index (base 100)",
        "source_type": "logistics_index",
        "default_lag_days": 20,
        "directionality": "POSITIVE",
        "reliability_score": 0.7,
        "start_value": 100.0,
        "drift": 0.001,
        "volatility": 0.04,
    },
    {
        "key": "fx_index",
        "name": "FX Index (USD Basket)",
        "category": "FX",
        "description": "Trade-weighted USD index against key sourcing-country currencies.",
        "unit": "index (base 100)",
        "source_type": "fx_index",
        "default_lag_days": 5,
        "directionality": "POSITIVE",
        "reliability_score": 0.9,
        "start_value": 100.0,
        "drift": 0.0005,
        "volatility": 0.015,
    },
    {
        "key": "chemical_feedstock_index",
        "name": "Chemical Feedstock Index",
        "category": "RAW_MATERIAL",
        "description": "Petrochemical feedstock price index for specialty chemicals.",
        "unit": "index (base 100)",
        "source_type": "commodity_index",
        "default_lag_days": 25,
        "directionality": "POSITIVE",
        "reliability_score": 0.75,
        "start_value": 100.0,
        "drift": 0.002,
        "volatility": 0.03,
    },
    {
        "key": "copper_lme_index",
        "name": "Copper LME Index",
        "category": "RAW_MATERIAL",
        "description": "London Metal Exchange copper cash price index.",
        "unit": "index (base 100)",
        "source_type": "commodity_index",
        "default_lag_days": 10,
        "directionality": "POSITIVE",
        "reliability_score": 0.85,
        "start_value": 100.0,
        "drift": 0.0035,
        "volatility": 0.035,
    },
    {
        "key": "specialty_polymer_feedstock_index",
        "name": "Specialty Polymer Feedstock Index",
        "category": "RAW_MATERIAL",
        "description": "Niche photoresist-grade polymer/monomer feedstock index.",
        "unit": "index (base 100)",
        "source_type": "commodity_index",
        "default_lag_days": 40,
        "directionality": "POSITIVE",
        "reliability_score": 0.55,
        "start_value": 100.0,
        "drift": 0.003,
        "volatility": 0.05,
    },
]


@dataclass
class MaterialDef:
    material_code: str
    name: str
    category: str
    description: str
    unit: str
    currency: str
    criticality: str
    lead_time_days: int
    single_source_flag: bool
    n_months: int
    base_price: float
    price_volatility: float
    components: list[dict]  # component_code, component_name, percentage_of_cost, unit, description
    component_drivers: list[dict]  # component_code, driver_key, relationship_strength, elasticity, lag_period, direction, confidence, rationale
    suppliers: list[dict]  # supplier_code, name, country, share_of_supply, lead_time_days, single_source, risk_score
    price_shock_at: int | None = None
    price_shock_pct: float = 0.0


MATERIAL_DEFS = [
    MaterialDef(
        material_code="MAT-001",
        name="Ceria CMP Slurry",
        category="CMP Consumable",
        description="Chemical-mechanical polishing slurry for wafer planarization (synthetic demo data).",
        unit="L",
        currency="USD",
        criticality="HIGH",
        lead_time_days=75,
        single_source_flag=True,
        n_months=48,
        base_price=1240.0,
        price_volatility=0.02,
        price_shock_at=44,
        price_shock_pct=0.05,
        components=[
            {"component_code": "CER", "component_name": "Ceria abrasive", "percentage_of_cost": 42.0, "unit": "%", "description": "Cerium oxide abrasive particles."},
            {"component_code": "H2O2", "component_name": "H2O2 (Oxidizer)", "percentage_of_cost": 18.0, "unit": "%", "description": "Hydrogen peroxide oxidizing agent."},
            {"component_code": "DISP", "component_name": "Dispersant", "percentage_of_cost": 12.0, "unit": "%", "description": "Specialty dispersant chemical."},
            {"component_code": "DIW", "component_name": "DI water + additives", "percentage_of_cost": 28.0, "unit": "%", "description": "Deionized water and minor additives."},
        ],
        component_drivers=[
            {"component_code": "CER", "driver_key": "rare_earth_index", "relationship_strength": 0.87, "elasticity": 0.9, "lag_period": 30, "direction": "POSITIVE", "confidence": 0.82, "rationale": "Ceria abrasive is refined directly from rare-earth ore."},
            {"component_code": "CER", "driver_key": "fx_index", "relationship_strength": 0.3, "elasticity": 0.3, "lag_period": 5, "direction": "POSITIVE", "confidence": 0.6, "rationale": "Ceria is imported; priced in supplier-country currency."},
            {"component_code": "H2O2", "driver_key": "energy_price_index", "relationship_strength": 0.5, "elasticity": 0.4, "lag_period": 15, "direction": "POSITIVE", "confidence": 0.7, "rationale": "H2O2 production is energy-intensive."},
            {"component_code": "H2O2", "driver_key": "chemical_feedstock_index", "relationship_strength": 0.4, "elasticity": 0.35, "lag_period": 25, "direction": "POSITIVE", "confidence": 0.65, "rationale": "H2O2 is a petrochemical-adjacent commodity."},
            {"component_code": "DISP", "driver_key": "chemical_feedstock_index", "relationship_strength": 0.6, "elasticity": 0.5, "lag_period": 25, "direction": "POSITIVE", "confidence": 0.6, "rationale": "Dispersant is a specialty petrochemical formulation."},
            {"component_code": "DISP", "driver_key": "energy_price_index", "relationship_strength": 0.3, "elasticity": 0.25, "lag_period": 15, "direction": "POSITIVE", "confidence": 0.55, "rationale": "Dispersant synthesis requires process heat."},
            {"component_code": "DIW", "driver_key": "freight_index", "relationship_strength": 0.25, "elasticity": 0.2, "lag_period": 20, "direction": "POSITIVE", "confidence": 0.5, "rationale": "Bulk logistics cost for finished slurry."},
            {"component_code": "DIW", "driver_key": "fx_index", "relationship_strength": 0.15, "elasticity": 0.15, "lag_period": 5, "direction": "POSITIVE", "confidence": 0.45, "rationale": "Minor imported additive content."},
        ],
        suppliers=[
            {"supplier_code": "SUP-A", "name": "Supplier A (Japan)", "country": "Japan", "share_of_supply": 0.82, "lead_time_days": 75, "single_source": False, "risk_score": 78.0},
            {"supplier_code": "SUP-B", "name": "Supplier B (South Korea)", "country": "South Korea", "share_of_supply": 0.18, "lead_time_days": 60, "single_source": False, "risk_score": 40.0},
        ],
    ),
    MaterialDef(
        material_code="MAT-002",
        name="Hydrogen Peroxide (Electronic Grade)",
        category="Oxidizer Chemical",
        description="High-purity H2O2 used across wet-clean and CMP processes (synthetic demo data).",
        unit="L",
        currency="USD",
        criticality="MEDIUM",
        lead_time_days=30,
        single_source_flag=False,
        n_months=42,
        base_price=185.0,
        price_volatility=0.025,
        price_shock_at=30,
        price_shock_pct=-0.06,
        components=[
            {"component_code": "H2O2P", "component_name": "H2O2 (Pure)", "percentage_of_cost": 85.0, "unit": "%", "description": "Purified hydrogen peroxide."},
            {"component_code": "STAB", "component_name": "Stabilizer", "percentage_of_cost": 15.0, "unit": "%", "description": "Decomposition-inhibiting stabilizer additive."},
        ],
        component_drivers=[
            {"component_code": "H2O2P", "driver_key": "energy_price_index", "relationship_strength": 0.65, "elasticity": 0.55, "lag_period": 15, "direction": "POSITIVE", "confidence": 0.75, "rationale": "Electrolytic H2O2 production is energy-intensive."},
            {"component_code": "H2O2P", "driver_key": "chemical_feedstock_index", "relationship_strength": 0.45, "elasticity": 0.4, "lag_period": 25, "direction": "POSITIVE", "confidence": 0.65, "rationale": "Anthraquinone feedstock tracks petrochemical prices."},
            {"component_code": "STAB", "driver_key": "chemical_feedstock_index", "relationship_strength": 0.3, "elasticity": 0.25, "lag_period": 25, "direction": "POSITIVE", "confidence": 0.5, "rationale": "Stabilizer is a specialty chemical additive."},
            {"component_code": "H2O2P", "driver_key": "freight_index", "relationship_strength": 0.2, "elasticity": 0.15, "lag_period": 20, "direction": "POSITIVE", "confidence": 0.45, "rationale": "Hazmat freight cost for bulk chemical shipping."},
        ],
        suppliers=[
            {"supplier_code": "SUP-C", "name": "Supplier C (USA)", "country": "USA", "share_of_supply": 0.6, "lead_time_days": 30, "single_source": False, "risk_score": 35.0},
            {"supplier_code": "SUP-D", "name": "Supplier D (Germany)", "country": "Germany", "share_of_supply": 0.4, "lead_time_days": 35, "single_source": False, "risk_score": 32.0},
        ],
    ),
    MaterialDef(
        material_code="MAT-003",
        name="Specialty Photoresist Polymer",
        category="Photoresist Specialty Chemical",
        description="Niche polymer resin for advanced-node photoresist formulation; sparse purchase history (synthetic demo data).",
        unit="kg",
        currency="USD",
        criticality="CRITICAL",
        lead_time_days=120,
        single_source_flag=True,
        n_months=8,  # LOW_DATA demo (< 12 observations, roadmap section 10)
        base_price=4200.0,
        price_volatility=0.03,
        components=[
            {"component_code": "RESIN", "component_name": "Specialty polymer resin", "percentage_of_cost": 60.0, "unit": "%", "description": "Base polymer resin backbone."},
            {"component_code": "PAG", "component_name": "Photoacid generator", "percentage_of_cost": 25.0, "unit": "%", "description": "Photoacid generator compound."},
            {"component_code": "SOLV", "component_name": "Solvent carrier", "percentage_of_cost": 15.0, "unit": "%", "description": "Casting solvent carrier."},
        ],
        component_drivers=[
            {"component_code": "RESIN", "driver_key": "specialty_polymer_feedstock_index", "relationship_strength": 0.75, "elasticity": 0.7, "lag_period": 40, "direction": "POSITIVE", "confidence": 0.5, "rationale": "Resin backbone tracks niche monomer feedstock, thinly traded."},
            {"component_code": "PAG", "driver_key": "chemical_feedstock_index", "relationship_strength": 0.4, "elasticity": 0.35, "lag_period": 25, "direction": "POSITIVE", "confidence": 0.45, "rationale": "PAG synthesis uses specialty petrochemical inputs."},
            {"component_code": "SOLV", "driver_key": "energy_price_index", "relationship_strength": 0.3, "elasticity": 0.2, "lag_period": 15, "direction": "POSITIVE", "confidence": 0.4, "rationale": "Solvent distillation is energy-intensive."},
        ],
        suppliers=[
            {"supplier_code": "SUP-E", "name": "Supplier E (Japan)", "country": "Japan", "share_of_supply": 1.0, "lead_time_days": 120, "single_source": True, "risk_score": 88.0},
        ],
    ),
    MaterialDef(
        material_code="MAT-004",
        name="Copper Sputtering Target",
        category="Metal Consumable",
        description="High-purity copper target for PVD interconnect deposition (synthetic demo data).",
        unit="kg",
        currency="USD",
        criticality="MEDIUM",
        lead_time_days=50,
        single_source_flag=False,
        n_months=40,
        base_price=68.0,
        price_volatility=0.03,
        price_shock_at=36,
        price_shock_pct=0.08,
        components=[
            {"component_code": "CU", "component_name": "Copper (99.999% purity)", "percentage_of_cost": 88.0, "unit": "%", "description": "Refined high-purity copper."},
            {"component_code": "FAB", "component_name": "Target fabrication", "percentage_of_cost": 12.0, "unit": "%", "description": "Bonding, machining, and QA labor/overhead."},
        ],
        component_drivers=[
            {"component_code": "CU", "driver_key": "copper_lme_index", "relationship_strength": 0.9, "elasticity": 0.95, "lag_period": 10, "direction": "POSITIVE", "confidence": 0.85, "rationale": "Refined copper price tracks LME cash price closely."},
            {"component_code": "CU", "driver_key": "fx_index", "relationship_strength": 0.25, "elasticity": 0.2, "lag_period": 5, "direction": "POSITIVE", "confidence": 0.55, "rationale": "LME copper is USD-denominated globally."},
            {"component_code": "FAB", "driver_key": "energy_price_index", "relationship_strength": 0.35, "elasticity": 0.3, "lag_period": 15, "direction": "POSITIVE", "confidence": 0.55, "rationale": "Machining/bonding is energy-intensive."},
            {"component_code": "FAB", "driver_key": "freight_index", "relationship_strength": 0.2, "elasticity": 0.15, "lag_period": 20, "direction": "POSITIVE", "confidence": 0.4, "rationale": "Finished target freight/logistics cost."},
        ],
        suppliers=[
            {"supplier_code": "SUP-F", "name": "Supplier F (Chile)", "country": "Chile", "share_of_supply": 0.55, "lead_time_days": 50, "single_source": False, "risk_score": 42.0},
            {"supplier_code": "SUP-G", "name": "Supplier G (Taiwan)", "country": "Taiwan", "share_of_supply": 0.45, "lead_time_days": 45, "single_source": False, "risk_score": 38.0},
        ],
    ),
]


MARKET_EVENT_DEFS = [
    {
        "title": "Rare-earth export restriction announced",
        "description": "A major rare-earth producing country tightened export quotas on cerium/lanthanum oxides.",
        "event_type": "EXPORT_RESTRICTION",
        "source_name": "Ministry of Commerce Notice (demo)",
        "source_url": None,
        "months_ago": 4,
        "affected_driver": "Rare Earth Index",
        "affected_material": "Ceria CMP Slurry",
        "impact_direction": "UP",
        "impact_magnitude": "HIGH",
        "impact_horizon": "MEDIUM",
        "event_confidence": 82.0,
    },
    {
        "title": "Regional energy cost pressure from natural gas prices",
        "description": "Industrial natural gas prices rose sharply in a key manufacturing region.",
        "event_type": "ENERGY_EVENT",
        "source_name": "Energy Market Report (demo)",
        "source_url": None,
        "months_ago": 2,
        "affected_driver": "Energy Price Index",
        "affected_material": "Ceria CMP Slurry",
        "impact_direction": "UP",
        "impact_magnitude": "MEDIUM",
        "impact_horizon": "SHORT",
        "event_confidence": 70.0,
    },
    {
        "title": "New hydrogen peroxide production capacity online",
        "description": "A new electrolytic H2O2 plant reached full production capacity, easing regional supply tightness.",
        "event_type": "CAPACITY_EXPANSION",
        "source_name": "Industry Publication (demo)",
        "source_url": None,
        "months_ago": 6,
        "affected_driver": "Energy Price Index",
        "affected_material": "Hydrogen Peroxide (Electronic Grade)",
        "impact_direction": "DOWN",
        "impact_magnitude": "MEDIUM",
        "impact_horizon": "MEDIUM",
        "event_confidence": 65.0,
    },
    {
        "title": "Copper mine labor strike disrupts supply",
        "description": "A strike at a major copper mine reduced regional refined copper output.",
        "event_type": "SUPPLY_DISRUPTION",
        "source_name": "General News Wire (demo)",
        "source_url": None,
        "months_ago": 3,
        "affected_driver": "Copper LME Index",
        "affected_material": "Copper Sputtering Target",
        "impact_direction": "UP",
        "impact_magnitude": "HIGH",
        "impact_horizon": "SHORT",
        "event_confidence": 75.0,
    },
]


def build_driver_observations(rng: np.random.Generator) -> dict[str, list[tuple[date, float]]]:
    """One 60-month series per driver (longest material history needed), keyed by driver key."""
    max_months = max(m.n_months for m in MATERIAL_DEFS) + 12
    series: dict[str, list[tuple[date, float]]] = {}
    dates = _month_range(max_months)
    for d in DRIVER_DEFS:
        values = _random_walk_index(rng, max_months, d["start_value"], d["drift"], d["volatility"])
        series[d["key"]] = list(zip(dates, values))
    return series


def _cumulative_pct_change(series: list[float]) -> list[float]:
    base = series[0]
    return [(v - base) / base for v in series]


def build_price_observations(
    material: MaterialDef, driver_series: dict[str, list[tuple[date, float]]], rng: np.random.Generator
) -> list[tuple[date, float]]:
    """Weighted combination of component-driver cumulative moves + idiosyncratic noise,
    anchored so the series ends at material.base_price (the 'current price')."""
    dates = _month_range(material.n_months)
    driver_dates_full = [dt for dt, _ in next(iter(driver_series.values()))]
    offset = len(driver_dates_full) - material.n_months

    weight_by_component = {c["component_code"]: c["percentage_of_cost"] / 100.0 for c in material.components}

    combined_pct_change = [0.0] * material.n_months
    for cd in material.component_drivers:
        driver_vals = [v for _, v in driver_series[cd["driver_key"]]][offset:]
        pct_change = _cumulative_pct_change(driver_vals)
        weight = weight_by_component[cd["component_code"]]
        elasticity = cd["elasticity"]
        for i, pc in enumerate(pct_change):
            combined_pct_change[i] += weight * elasticity * pc

    prices = []
    for i, month_pct in enumerate(combined_pct_change):
        shock = material.price_shock_pct if material.price_shock_at == i else 0.0
        noise = rng.normal(0, material.price_volatility)
        price = material.base_price * (1 + month_pct + shock + noise)
        # keep the last point anchored near base_price by damping noise on final month
        if i == material.n_months - 1:
            price = material.base_price * (1 + month_pct * 0.3 + shock)
        prices.append(round(price, 2))

    return list(zip(dates, prices))


@dataclass
class GeneratedData:
    drivers: list[dict]
    driver_observations: dict[str, list[tuple[date, float]]]
    materials: list[MaterialDef]
    price_observations: dict[str, list[tuple[date, float]]]
    market_events: list[dict]


def generate_all(seed: int = SEED) -> GeneratedData:
    rng = np.random.default_rng(seed)
    driver_obs = build_driver_observations(rng)
    price_obs = {
        m.material_code: build_price_observations(m, driver_obs, rng) for m in MATERIAL_DEFS
    }
    return GeneratedData(
        drivers=DRIVER_DEFS,
        driver_observations=driver_obs,
        materials=MATERIAL_DEFS,
        price_observations=price_obs,
        market_events=MARKET_EVENT_DEFS,
    )
