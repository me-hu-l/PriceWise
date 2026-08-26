from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.models import (
    ComponentDriver,
    ConfidenceComponent,
    CustomPriceObservation,
    Forecast,
    ForecastContribution,
    Material,
    MaterialComponent,
    PriceObservation,
)


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


def list_price_history(db: Session, material_id: int) -> list[PriceObservation | CustomPriceObservation]:
    try:
        custom = (
            db.query(CustomPriceObservation)
            .filter(CustomPriceObservation.material_id == material_id)
            .order_by(CustomPriceObservation.date)
            .all()
        )
    except OperationalError:
        # Older local databases can run on seeded history until the migration is applied.
        db.rollback()
        custom = []
    if custom:
        return custom
    return (
        db.query(PriceObservation)
        .filter(PriceObservation.material_id == material_id)
        .order_by(PriceObservation.date)
        .all()
    )


def replace_custom_price_history(
    db: Session, material: Material, observations: list[dict]
) -> list[CustomPriceObservation]:
    """Replace only this material's upload overlay and invalidate derived outputs."""
    db.query(CustomPriceObservation).filter(
        CustomPriceObservation.material_id == material.id
    ).delete(synchronize_session=False)
    rows = [
        CustomPriceObservation(
            material_id=material.id,
            date=row["date"],
            price=row["price"],
            currency=row.get("currency") or material.currency,
            unit=row.get("unit") or material.unit,
            source="user_upload",
            data_quality="USER_UPLOAD",
        )
        for row in observations
    ]
    db.add_all(rows)
    latest = max(observations, key=lambda row: row["date"])
    material.current_price = latest["price"]
    material.current_price_date = latest["date"]

    forecast_ids = [
        row.id for row in db.query(Forecast.id).filter(Forecast.material_id == material.id).all()
    ]
    if forecast_ids:
        db.query(ForecastContribution).filter(
            ForecastContribution.forecast_id.in_(forecast_ids)
        ).delete(synchronize_session=False)
        db.query(ConfidenceComponent).filter(
            ConfidenceComponent.forecast_id.in_(forecast_ids)
        ).delete(synchronize_session=False)
        db.query(Forecast).filter(Forecast.id.in_(forecast_ids)).delete(
            synchronize_session=False
        )
    db.commit()
    return rows
