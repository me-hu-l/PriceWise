from fastapi import APIRouter

from app.schemas.common import NotImplementedResponse
from app.services import forecast_service

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.post("", response_model=NotImplementedResponse)
def create_forecast(payload: dict):
    """Phase 2 TODO: on-demand forecast for arbitrary driver assumptions."""
    return forecast_service.get_forecast(payload.get("material_id"))
