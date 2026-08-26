from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.scenario import ScenarioComparison, ScenarioRequest
from app.services import material_service, scenario_service

router = APIRouter(prefix="/api/scenario", tags=["scenario"])


@router.post("", response_model=ScenarioComparison)
def create_scenario(payload: ScenarioRequest, db: Session = Depends(get_db)):
    material = material_service.get_material(db, payload.material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="material_id not found")
    try:
        comparison = scenario_service.run_scenario(db, material, payload.driver_changes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if comparison is None:
        raise HTTPException(status_code=422, detail="Insufficient data for scenario forecasting")
    return comparison
