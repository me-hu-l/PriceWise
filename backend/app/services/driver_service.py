from datetime import date

from sqlalchemy.orm import Session

from app.db.models import ComponentDriver, Driver, DriverObservation, MaterialComponent


def list_material_component_drivers(db: Session, material_id: int) -> list[dict]:
    """Knowledge-graph edges (component -> driver) for every component of a material."""
    rows = (
        db.query(ComponentDriver, MaterialComponent, Driver)
        .join(MaterialComponent, ComponentDriver.component_id == MaterialComponent.id)
        .join(Driver, ComponentDriver.driver_id == Driver.id)
        .filter(MaterialComponent.material_id == material_id)
        .order_by(ComponentDriver.relationship_strength.desc())
        .all()
    )
    return [
        {
            "id": cd.id,
            "component_id": component.id,
            "component_name": component.component_name,
            "driver_id": driver.id,
            "driver_name": driver.name,
            "driver_category": driver.category,
            "relationship_strength": cd.relationship_strength,
            "elasticity": cd.elasticity,
            "lag_period": cd.lag_period,
            "direction": cd.direction,
            "confidence": cd.confidence,
            "rationale": cd.rationale,
        }
        for cd, component, driver in rows
    ]


def list_drivers(db: Session) -> list[Driver]:
    return db.query(Driver).order_by(Driver.category, Driver.name).all()


def list_material_driver_histories(db: Session, material_id: int) -> list[dict]:
    edges = (
        db.query(ComponentDriver, Driver)
        .join(MaterialComponent, ComponentDriver.component_id == MaterialComponent.id)
        .join(Driver, ComponentDriver.driver_id == Driver.id)
        .filter(MaterialComponent.material_id == material_id)
        .all()
    )
    drivers = {driver.id: driver for _, driver in edges}
    histories = []
    for driver in sorted(drivers.values(), key=lambda item: item.name):
        observations = (
            db.query(DriverObservation)
            .filter(DriverObservation.driver_id == driver.id)
            .order_by(DriverObservation.date)
            .all()
        )
        values = [observation.value for observation in observations]
        projected_value = None
        projected_date = None
        if values:
            changes = [current / prior - 1 for prior, current in zip(values, values[1:]) if prior]
            momentum = sum(changes[-3:]) / len(changes[-3:]) if changes else 0.0
            projected_value = values[-1] * (1 + momentum)
            latest_date = observations[-1].date
            projected_date = (
                date(latest_date.year + 1, 1, 1)
                if latest_date.month == 12
                else date(latest_date.year, latest_date.month + 1, 1)
            )
        histories.append(
            {
                "driver_id": driver.id,
                "driver_name": driver.name,
                "unit": driver.unit,
                "observations": [{"date": o.date, "value": o.value} for o in observations],
                "projected_date": projected_date,
                "projected_value": projected_value,
            }
        )
    return histories
