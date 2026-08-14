"""Phase 3 TODO: rule-based recommendation engine (roadmap section 21) and
supplier claim analyzer (roadmap section 20)."""

from app.schemas.common import NotImplementedResponse


def get_recommendation(material_id: int) -> NotImplementedResponse:
    return NotImplementedResponse(
        feature="recommendation",
        phase="Phase 3 — Decision intelligence",
        reason="Recommendation rules require forecast direction/confidence, which are not available yet.",
    )


def analyze_supplier_claim(payload: dict) -> NotImplementedResponse:
    return NotImplementedResponse(
        feature="supplier_claim_analysis",
        phase="Phase 3 — Decision intelligence",
        reason="Market-supported vs. unexplained increase requires the forecast engine.",
    )
