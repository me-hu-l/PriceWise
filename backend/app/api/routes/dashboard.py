from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Material

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    materials_monitored: int
    high_or_critical_criticality: int
    single_source_materials: int
    # Forecast-derived cards (increasing/decreasing/actions required) land in Phase 2/3.


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return DashboardSummary(
        materials_monitored=len(materials),
        high_or_critical_criticality=sum(
            1 for m in materials if m.criticality in ("HIGH", "CRITICAL")
        ),
        single_source_materials=sum(1 for m in materials if m.single_source_flag),
    )
