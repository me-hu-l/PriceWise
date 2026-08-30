"""One-command demo seed: `python -m app.seed.seed_database`.

Populates the database from app.seed.demo_data.generate_all() and mirrors the
same data to CSV files under data/ for transparency (roadmap section 33/45).
Idempotent: clears existing rows before inserting.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from app.db.database import Base, SessionLocal, engine
from app.db.models import (
    ComponentDriver,
    ConfidenceComponent,
    Driver,
    DriverObservation,
    Evidence,
    Forecast,
    ForecastContribution,
    Material,
    MaterialComponent,
    MarketEvent,
    PriceObservation,
    Recommendation,
    Supplier,
    SupplierQuote,
)
from app.seed.demo_data import generate_all
from app.seed.generate_forecasts import generate_all_forecasts

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def _clear_all(db) -> None:
    for model in (
        Evidence,
        Recommendation,
        ForecastContribution,
        ConfidenceComponent,
        Forecast,
        SupplierQuote,
        PriceObservation,
        ComponentDriver,
        DriverObservation,
        MaterialComponent,
        MarketEvent,
        Material,
        Supplier,
        Driver,
    ):
        db.query(model).delete()
    db.commit()


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    data = generate_all()
    db = SessionLocal()
    try:
        _clear_all(db)

        # --- Drivers ---
        driver_rows_csv = []
        driver_id_by_key = {}
        for d in data.drivers:
            row = Driver(
                name=d["name"],
                category=d["category"],
                description=d["description"],
                unit=d["unit"],
                source_type=d["source_type"],
                default_lag_days=d["default_lag_days"],
                directionality=d["directionality"],
                reliability_score=d["reliability_score"],
            )
            db.add(row)
            db.flush()
            driver_id_by_key[d["key"]] = row.id
            driver_rows_csv.append({"driver_key": d["key"], "id": row.id, **{k: d[k] for k in ("name", "category", "unit", "source_type", "default_lag_days", "directionality", "reliability_score")}})

        # --- Driver observations ---
        driver_obs_rows_csv = []
        for driver_key, series in data.driver_observations.items():
            for obs_date, value in series:
                db.add(
                    DriverObservation(
                        driver_id=driver_id_by_key[driver_key],
                        date=obs_date,
                        value=round(value, 4),
                        unit="index",
                        source="synthetic_demo",
                        source_quality=80.0,
                    )
                )
                driver_obs_rows_csv.append({"driver_key": driver_key, "date": obs_date.isoformat(), "value": round(value, 4)})
        db.flush()

        # --- Materials, components, component_drivers, price observations, suppliers, quotes ---
        material_rows_csv = []
        component_rows_csv = []
        component_driver_rows_csv = []
        price_rows_csv = []
        supplier_rows_csv = []
        quote_rows_csv = []

        for m in data.materials:
            price_series = data.price_observations[m.material_code]
            current_price = price_series[-1][1]
            current_date = price_series[-1][0]

            material_row = Material(
                material_code=m.material_code,
                name=m.name,
                category=m.category,
                description=m.description,
                unit=m.unit,
                currency=m.currency,
                criticality=m.criticality,
                current_price=current_price,
                current_price_date=current_date,
                lead_time_days=m.lead_time_days,
                single_source_flag=m.single_source_flag,
            )
            db.add(material_row)
            db.flush()
            material_rows_csv.append(
                {
                    "material_code": m.material_code,
                    "name": m.name,
                    "category": m.category,
                    "unit": m.unit,
                    "currency": m.currency,
                    "criticality": m.criticality,
                    "current_price": current_price,
                    "current_price_date": current_date.isoformat(),
                    "lead_time_days": m.lead_time_days,
                    "single_source_flag": m.single_source_flag,
                }
            )

            # Suppliers (created once, but definitions are per-material here so upsert by code)
            supplier_id_by_code = {}
            for s in m.suppliers:
                existing = db.query(Supplier).filter(Supplier.supplier_code == s["supplier_code"]).first()
                if existing:
                    supplier_id_by_code[s["supplier_code"]] = existing.id
                    continue
                supplier_row = Supplier(
                    name=s["name"],
                    supplier_code=s["supplier_code"],
                    country=s["country"],
                    qualification_status="QUALIFIED",
                    lead_time_days=s["lead_time_days"],
                    single_source=s["single_source"],
                    share_of_supply=s["share_of_supply"],
                    risk_score=s["risk_score"],
                )
                db.add(supplier_row)
                db.flush()
                supplier_id_by_code[s["supplier_code"]] = supplier_row.id
                supplier_rows_csv.append(
                    {
                        "supplier_code": s["supplier_code"],
                        "name": s["name"],
                        "country": s["country"],
                        "share_of_supply": s["share_of_supply"],
                        "lead_time_days": s["lead_time_days"],
                        "single_source": s["single_source"],
                        "risk_score": s["risk_score"],
                    }
                )

            primary_supplier_code = max(m.suppliers, key=lambda s: s["share_of_supply"])["supplier_code"]
            primary_supplier_id = supplier_id_by_code[primary_supplier_code]

            # Components
            component_id_by_code = {}
            for c in m.components:
                comp_row = MaterialComponent(
                    material_id=material_row.id,
                    component_name=c["component_name"],
                    component_code=c["component_code"],
                    percentage_of_cost=c["percentage_of_cost"],
                    unit=c["unit"],
                    description=c["description"],
                )
                db.add(comp_row)
                db.flush()
                component_id_by_code[c["component_code"]] = comp_row.id
                component_rows_csv.append(
                    {
                        "material_code": m.material_code,
                        "component_code": c["component_code"],
                        "component_name": c["component_name"],
                        "percentage_of_cost": c["percentage_of_cost"],
                    }
                )

            # Component -> driver edges (knowledge graph)
            for cd in m.component_drivers:
                db.add(
                    ComponentDriver(
                        component_id=component_id_by_code[cd["component_code"]],
                        driver_id=driver_id_by_key[cd["driver_key"]],
                        relationship_strength=cd["relationship_strength"],
                        elasticity=cd["elasticity"],
                        lag_period=cd["lag_period"],
                        direction=cd["direction"],
                        confidence=cd["confidence"],
                        rationale=cd["rationale"],
                    )
                )
                component_driver_rows_csv.append(
                    {
                        "material_code": m.material_code,
                        "component_code": cd["component_code"],
                        "driver_key": cd["driver_key"],
                        "relationship_strength": cd["relationship_strength"],
                        "elasticity": cd["elasticity"],
                    }
                )

            # Price history
            for obs_date, price in price_series:
                db.add(
                    PriceObservation(
                        material_id=material_row.id,
                        date=obs_date,
                        price=price,
                        currency=m.currency,
                        unit=m.unit,
                        supplier_id=primary_supplier_id,
                        contract_type="SPOT",
                        source="synthetic_demo",
                        data_quality="SYNTHETIC",
                    )
                )
                price_rows_csv.append(
                    {"material_code": m.material_code, "date": obs_date.isoformat(), "price": price}
                )

            # Supplier quotes: hero narrative uses +9% claim on Ceria CMP Slurry (roadmap section 34)
            for s in m.suppliers:
                sup_id = supplier_id_by_code[s["supplier_code"]]
                is_primary = s["supplier_code"] == primary_supplier_code
                s_claimed_pct = (
                    (0.09 if is_primary else 0.04)
                    if m.material_code == "MAT-001"
                    else (0.03 if is_primary else 0.015)
                )
                s_quoted_price = round(current_price * (1 + s_claimed_pct), 2)
                db.add(
                    SupplierQuote(
                        supplier_id=sup_id,
                        material_id=material_row.id,
                        quote_date=current_date,
                        quoted_price=s_quoted_price,
                        currency=m.currency,
                        unit=m.unit,
                        previous_price=current_price,
                        claimed_change_pct=s_claimed_pct * 100,
                        reason=f"Raw material and supply chain adjustment ({s['name']}).",
                        valid_until=None,
                    )
                )
                quote_rows_csv.append(
                    {
                        "material_code": m.material_code,
                        "supplier_code": s["supplier_code"],
                        "quote_date": current_date.isoformat(),
                        "quoted_price": s_quoted_price,
                        "previous_price": current_price,
                        "claimed_change_pct": s_claimed_pct * 100,
                    }
                )

        # --- Market events ---
        event_rows_csv = []
        for e in data.market_events:
            month = 8 - e["months_ago"]
            year = 2026
            while month <= 0:
                month += 12
                year -= 1
            published_at = datetime(year, month, 1)
            db.add(
                MarketEvent(
                    title=e["title"],
                    description=e["description"],
                    event_type=e["event_type"],
                    source_name=e["source_name"],
                    source_url=e["source_url"],
                    published_at=published_at,
                    affected_driver=e["affected_driver"],
                    affected_material=e["affected_material"],
                    impact_direction=e["impact_direction"],
                    impact_magnitude=e["impact_magnitude"],
                    impact_horizon=e["impact_horizon"],
                    event_confidence=e["event_confidence"],
                    processed_by_llm=False,
                )
            )
            event_rows_csv.append(
                {
                    "title": e["title"],
                    "event_type": e["event_type"],
                    "published_at": published_at.isoformat(),
                    "affected_driver": e["affected_driver"],
                    "affected_material": e["affected_material"],
                    "impact_direction": e["impact_direction"],
                    "impact_magnitude": e["impact_magnitude"],
                    "event_confidence": e["event_confidence"],
                }
            )

        db.commit()

        _write_csv(DATA_DIR / "drivers.csv", driver_rows_csv)
        _write_csv(DATA_DIR / "market_indices.csv", driver_obs_rows_csv)
        _write_csv(DATA_DIR / "materials.csv", material_rows_csv)
        _write_csv(DATA_DIR / "material_components.csv", component_rows_csv)
        _write_csv(DATA_DIR / "component_drivers.csv", component_driver_rows_csv)
        _write_csv(DATA_DIR / "price_history.csv", price_rows_csv)
        _write_csv(DATA_DIR / "suppliers.csv", supplier_rows_csv)
        _write_csv(DATA_DIR / "supplier_quotes.csv", quote_rows_csv)
        _write_csv(DATA_DIR / "market_events.csv", event_rows_csv)

        print(
            f"Seeded {len(material_rows_csv)} materials, {len(driver_rows_csv)} drivers, "
            f"{len(price_rows_csv)} price observations, {len(event_rows_csv)} market events."
        )
    finally:
        db.close()

    n_forecasts = generate_all_forecasts()
    print(f"Precomputed forecasts for {n_forecasts} materials.")


if __name__ == "__main__":
    seed()
