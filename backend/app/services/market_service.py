from sqlalchemy.orm import Session

from app.db.models import Material, MarketEvent


def list_events(db: Session) -> list[MarketEvent]:
    return db.query(MarketEvent).order_by(MarketEvent.published_at.desc()).all()


def list_events_for_material(db: Session, material_id: int, db_material: Material | None = None) -> list[MarketEvent]:
    material = db_material or db.get(Material, material_id)
    if material is None:
        return []
    return (
        db.query(MarketEvent)
        .filter(MarketEvent.affected_material == material.name)
        .order_by(MarketEvent.published_at.desc())
        .all()
    )
