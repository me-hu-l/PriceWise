from fastapi import APIRouter

from app.schemas.common import NotImplementedResponse
from app.services import scenario_service

router = APIRouter(prefix="/api/scenario", tags=["scenario"])


@router.post("", response_model=NotImplementedResponse)
def create_scenario(payload: dict):
    """Phase 5 TODO: what-if simulator reusing the driver model."""
    return scenario_service.run_scenario(payload)
