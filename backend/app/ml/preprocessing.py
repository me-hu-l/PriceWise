"""Feature builders for the driver model + residual model (roadmap section 8).

Pure functions over DB-loaded rows -> pandas DataFrames. No lag-shifting is
applied to driver series before regression (the synthetic demo generator
itself does not lag drivers before combining them into price), which is a
documented simplification for Phase 2.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import Driver, DriverObservation
from app.services import driver_service, material_service


def build_price_series(db: Session, material_id: int) -> pd.DataFrame:
    """DataFrame indexed by date with columns: price, pct_change (sorted ascending)."""
    obs = material_service.list_price_history(db, material_id)
    df = pd.DataFrame({"date": [o.date for o in obs], "price": [o.price for o in obs]})
    df = df.sort_values("date").reset_index(drop=True)
    df["pct_change"] = df["price"].pct_change()
    return df


def material_driver_weights(db: Session, material_id: int) -> dict[int, float]:
    """driver_id -> aggregated weight (component cost share * elasticity), summed
    across every component of the material linked to that driver."""
    edges = driver_service.list_material_component_drivers(db, material_id)
    components = {c.id: c for c in material_service.list_components(db, material_id)}
    weights: dict[int, float] = {}
    for edge in edges:
        component = components.get(edge["component_id"])
        if component is None:
            continue
        share = component.percentage_of_cost / 100.0
        elasticity = edge["elasticity"] or 0.0
        weights[edge["driver_id"]] = weights.get(edge["driver_id"], 0.0) + share * elasticity
    return weights


def build_driver_pct_change_matrix(
    db: Session, material_id: int, price_dates: list
) -> pd.DataFrame:
    """DataFrame indexed to price_dates, one column per driver relevant to the
    material, containing each driver's month-over-month pct change on those dates."""
    weights = material_driver_weights(db, material_id)
    driver_ids = list(weights.keys())
    if not driver_ids:
        return pd.DataFrame(index=range(len(price_dates)))

    columns: dict[str, list[float]] = {}
    for driver_id in driver_ids:
        driver = db.get(Driver, driver_id)
        obs = (
            db.query(DriverObservation)
            .filter(DriverObservation.driver_id == driver_id)
            .order_by(DriverObservation.date)
            .all()
        )
        series = pd.DataFrame({"date": [o.date for o in obs], "value": [o.value for o in obs]})
        series = series.sort_values("date").reset_index(drop=True)
        series["pct_change"] = series["value"].pct_change()
        by_date = dict(zip(series["date"], series["pct_change"]))
        columns[driver.name] = [by_date.get(d, 0.0) for d in price_dates]

    return pd.DataFrame(columns, index=range(len(price_dates)))


def get_driver_id_by_name(db: Session, name: str) -> int | None:
    driver = db.query(Driver).filter(Driver.name == name).first()
    return driver.id if driver else None
