from fastapi import APIRouter

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.recommendation import SupplierClaimAnalysis, SupplierClaimRequest
from app.services import material_service
from app.services import recommendation_service

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/supplier-claim/analyze", response_model=SupplierClaimAnalysis)
def analyze_supplier_claim(payload: SupplierClaimRequest, db: Session = Depends(get_db)):
    material = material_service.get_material(db, payload.material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="material_id not found")
    analysis = recommendation_service.analyze_supplier_claim(
        db, material, payload.claimed_change_pct
    )
    if analysis is None:
        raise HTTPException(status_code=422, detail="Insufficient data for supplier claim analysis")
    return analysis
