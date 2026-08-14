from sqlalchemy.orm import Session

from app.db.models import Material, MaterialComponent, PriceObservation


def list_materials(db: Session) -> list[Material]:
    return db.query(Material).order_by(Material.name).all()


def get_material(db: Session, material_id: int) -> Material | None:
    return db.get(Material, material_id)


def get_material_by_code(db: Session, material_code: str) -> Material | None:
    return db.query(Material).filter(Material.material_code == material_code).first()


def list_components(db: Session, material_id: int) -> list[MaterialComponent]:
    return (
        db.query(MaterialComponent)
        .filter(MaterialComponent.material_id == material_id)
        .order_by(MaterialComponent.percentage_of_cost.desc())
        .all()
    )


def list_price_history(db: Session, material_id: int) -> list[PriceObservation]:
    return (
        db.query(PriceObservation)
        .filter(PriceObservation.material_id == material_id)
        .order_by(PriceObservation.date)
        .all()
    )
