from fastapi import APIRouter

from app.schemas.common import NotImplementedResponse
from app.services import recommendation_service

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/supplier-claim/analyze", response_model=NotImplementedResponse)
def analyze_supplier_claim(payload: dict):
    """Phase 3 TODO: market-supported vs. unexplained increase (roadmap section 20)."""
    return recommendation_service.analyze_supplier_claim(payload)
