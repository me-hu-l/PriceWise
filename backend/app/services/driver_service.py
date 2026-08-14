from sqlalchemy.orm import Session

from app.db.models import ComponentDriver, Driver, MaterialComponent


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
