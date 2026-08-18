from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.common import InsufficientDataResponse
from app.schemas.forecast import ForecastRead
from app.services import forecast_service, material_service

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.post("", response_model=Union[ForecastRead, InsufficientDataResponse])
def create_forecast(payload: dict, db: Session = Depends(get_db)):
    """Returns the material's current precomputed forecast (regenerating if missing).

    Phase 5 TODO: accept driver-assumption overrides for on-demand what-if forecasts
    (this endpoint currently reuses the same pipeline as GET .../forecast).
    """
    material_id = payload.get("material_id")
    material = material_service.get_material(db, material_id) if material_id else None
    if material is None:
        raise HTTPException(status_code=404, detail="material_id not found")
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return InsufficientDataResponse(
            reason="Insufficient data for reliable forecast (fewer than 3 price observations)."
        )
    return forecast
