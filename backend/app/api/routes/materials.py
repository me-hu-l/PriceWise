import csv
import io
from datetime import date
from typing import Union

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.database import get_db
from app.schemas.common import InsufficientDataResponse
from app.schemas.confidence import ConfidenceRead
from app.schemas.driver import ComponentDriverRead, MaterialDriverHistoryRead
from app.schemas.forecast import ForecastExplanationRead, ForecastRead
from app.schemas.market_event import MarketEventRead
from app.schemas.recommendation import RecommendationRead
from app.schemas.material import (
    MaterialComponentRead,
    MaterialRead,
    PriceObservationRead,
    PriceUploadResult,
)
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
    material = _get_material_or_404(db, material_id)
    forecast_service.get_or_generate_forecast(db, material)
    return driver_service.list_material_component_drivers(db, material_id)


@router.get("/{material_id}/driver-observations", response_model=list[MaterialDriverHistoryRead])
def get_driver_observations(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return driver_service.list_material_driver_histories(db, material_id)


@router.get("/{material_id}/history", response_model=list[PriceObservationRead])
def get_history(material_id: int, db: Session = Depends(get_db)):
    _get_material_or_404(db, material_id)
    return material_service.list_price_history(db, material_id)


@router.post("/{material_id}/history/upload", response_model=PriceUploadResult)
async def upload_price_history(
    material_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    material = _get_material_or_404(db, material_id)
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file.")
    try:
        content = (await file.read()).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        required = {"date", "price"}
        if not reader.fieldnames or not required.issubset({name.strip().lower() for name in reader.fieldnames}):
            raise ValueError("CSV must contain date and price columns.")
        observations = []
        for line_number, row in enumerate(reader, start=2):
            normalized = {str(key).strip().lower(): (value or "").strip() for key, value in row.items()}
            observations.append(
                {
                    "date": date.fromisoformat(normalized["date"]),
                    "price": float(normalized["price"]),
                    "currency": normalized.get("currency") or material.currency,
                    "unit": normalized.get("unit") or material.unit,
                }
            )
            if observations[-1]["price"] <= 0:
                raise ValueError(f"Line {line_number}: price must be positive.")
        if len(observations) < 3:
            raise ValueError("Upload at least 3 observations.")
        if any(row["date"] > date.today() for row in observations):
            raise ValueError("Observation dates cannot be in the future.")
        if len({row["date"] for row in observations}) != len(observations):
            raise ValueError("Observation dates must be unique.")
        observations.sort(key=lambda row: row["date"])
    except (UnicodeDecodeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}") from exc
    material_service.replace_custom_price_history(db, material, observations)
    return PriceUploadResult(
        message="Custom price history uploaded and forecast cache cleared.",
        observation_count=len(observations),
        latest_date=observations[-1]["date"],
        latest_price=observations[-1]["price"],
    )


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


@router.get("/{material_id}/forecast", response_model=Union[ForecastRead, InsufficientDataResponse])
def get_forecast(material_id: int, db: Session = Depends(get_db)):
    material = _get_material_or_404(db, material_id)
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return InsufficientDataResponse(
            reason="Insufficient data for reliable forecast (fewer than 3 price observations)."
        )
    return forecast


@router.get(
    "/{material_id}/forecast/explanation",
    response_model=Union[ForecastExplanationRead, InsufficientDataResponse],
)
def get_forecast_explanation(material_id: int, db: Session = Depends(get_db)):
    material = _get_material_or_404(db, material_id)
    explanation = forecast_service.get_forecast_explanation(db, material)
    if explanation is None:
        return InsufficientDataResponse(
            reason="Insufficient data for reliable forecast (fewer than 3 price observations)."
        )
    return explanation


@router.get("/{material_id}/confidence", response_model=Union[ConfidenceRead, InsufficientDataResponse])
def get_confidence(material_id: int, db: Session = Depends(get_db)):
    material = _get_material_or_404(db, material_id)
    confidence = confidence_service.get_confidence(db, material)
    if confidence is None:
        return InsufficientDataResponse(
            reason="Insufficient data for reliable forecast (fewer than 3 price observations)."
        )
    return confidence


@router.get("/{material_id}/recommendation", response_model=Union[RecommendationRead, InsufficientDataResponse])
def get_recommendation(material_id: int, db: Session = Depends(get_db)):
    material = _get_material_or_404(db, material_id)
    recommendation = recommendation_service.get_recommendation(db, material)
    if recommendation is None:
        return InsufficientDataResponse(reason="Insufficient data for a recommendation.")
    return recommendation
