from sqlalchemy.orm import Session

from app.db.models import Supplier, SupplierQuote


def list_suppliers_for_material(db: Session, material_id: int) -> list[Supplier]:
    supplier_ids = (
        db.query(SupplierQuote.supplier_id)
        .filter(SupplierQuote.material_id == material_id)
        .distinct()
    )
    return db.query(Supplier).filter(Supplier.id.in_(supplier_ids)).all()


def list_quotes_for_material(db: Session, material_id: int) -> list[SupplierQuote]:
    return (
        db.query(SupplierQuote)
        .filter(SupplierQuote.material_id == material_id)
        .order_by(SupplierQuote.quote_date.desc())
        .all()
    )
