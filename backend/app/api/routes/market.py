from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.market_event import MarketEventRead
from app.services import market_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/events", response_model=list[MarketEventRead])
def list_events(db: Session = Depends(get_db)):
    return market_service.list_events(db)
