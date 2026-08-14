from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.driver import DriverRead
from app.services import driver_service

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverRead])
def list_drivers(db: Session = Depends(get_db)):
    """Full driver catalog (not scoped to a material)."""
    return driver_service.list_drivers(db)
