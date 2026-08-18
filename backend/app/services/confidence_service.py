"""Confidence retrieval — the five-component formula itself lives in app.ml.confidence.

Confidence is always read off the persisted ConfidenceComponent tied to a
material's latest Forecast (roadmap section 39 — precomputed, not recomputed
per request).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ConfidenceComponent, Material
from app.services import forecast_service


def get_confidence(db: Session, material: Material) -> ConfidenceComponent | None:
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return None
    return (
        db.query(ConfidenceComponent)
        .filter(ConfidenceComponent.forecast_id == forecast.id)
        .first()
    )

