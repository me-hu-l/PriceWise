from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Supplier
from app.schemas.supplier import (
    SupplierQuoteBatchAnalysisRequest,
    SupplierQuoteBatchAnalysisResponse,
    SupplierRead,
)
from app.services import material_service, recommendation_service

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    """Full supplier catalog (not scoped to a material)."""
    return db.query(Supplier).order_by(Supplier.name).all()


@router.post("/analyze-quotes", response_model=SupplierQuoteBatchAnalysisResponse)
def analyze_supplier_quotes(
    payload: SupplierQuoteBatchAnalysisRequest,
    db: Session = Depends(get_db),
):
    material = material_service.get_material(db, payload.material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    analysis = recommendation_service.analyze_supplier_quotes(
        db, material, payload.driver_changes, payload.quotes
    )
    if analysis is None:
        raise HTTPException(
            status_code=422, detail="Insufficient data for supplier quote analysis"
        )
    return analysis
