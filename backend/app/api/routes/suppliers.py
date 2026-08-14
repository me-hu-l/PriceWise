from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Supplier
from app.schemas.supplier import SupplierRead

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    """Full supplier catalog (not scoped to a material)."""
    return db.query(Supplier).order_by(Supplier.name).all()
