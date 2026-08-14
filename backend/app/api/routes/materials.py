from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import get_db
from app.schemas.common import NotImplementedResponse
from app.schemas.driver import ComponentDriverRead
from app.schemas.market_event import MarketEventRead
from app.schemas.material import MaterialComponentRead, MaterialRead, PriceObservationRead
from app.schemas.supplier import SupplierQuoteRead, SupplierRead
from app.services import (
    confidence_service,
    driver_service,
    market_service,
    material_service,
    recommendation_service,
    forecast_service,
    supplier_service,
)

router = APIRouter(prefix="/api/materials", tags=["materials"])


def _get_material_or_404(db: Session, material_id: int):
    material = material_service.get_material(db, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.get("", response_model=list[MaterialRead])
def list_materials(db: Session = Depends(get_db)):
    return material_service.list_materials(db)


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id: int, db: Session = Depends(get_db)):
    return _get_material_or_404(db, material_id)


@router.get("/{material_id}/components", response_model=list[MaterialComponentRead])
def get_components(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return material_service.list_components(db, material_id)


@router.get("/{material_id}/drivers", response_model=list[ComponentDriverRead])
def get_drivers(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return driver_service.list_material_component_drivers(db, material_id)


@router.get("/{material_id}/history", response_model=list[PriceObservationRead])
def get_history(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return material_service.list_price_history(db, material_id)


@router.get("/{material_id}/suppliers", response_model=list[SupplierRead])
def get_suppliers(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return supplier_service.list_suppliers_for_material(db, material_id)


@router.get("/{material_id}/supplier-claims", response_model=list[SupplierQuoteRead])
def get_supplier_claims(material_id: int, db: Session = Depends(get_db)):
    """Phase 1: raw supplier quotes only; claim vs. market-supported analysis is Phase 3."""
    _get_material_or_404(db, material_id)
    return supplier_service.list_quotes_for_material(db, material_id)


@router.get("/{material_id}/market-events", response_model=list[MarketEventRead])
def get_market_events(material_id: int, db: Session = Depends(get_db)):
    material = _get_material_or_404(db, material_id)
    return market_service.list_events_for_material(db, material_id, db_material=material)


@router.get("/{material_id}/forecast", response_model=NotImplementedResponse)
def get_forecast(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return forecast_service.get_forecast(material_id)


@router.get("/{material_id}/forecast/explanation", response_model=NotImplementedResponse)
def get_forecast_explanation(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return forecast_service.get_forecast_explanation(material_id)


@router.get("/{material_id}/confidence", response_model=NotImplementedResponse)
def get_confidence(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return confidence_service.get_confidence(material_id)


@router.get("/{material_id}/recommendation", response_model=NotImplementedResponse)
def get_recommendation(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return recommendation_service.get_recommendation(material_id)
