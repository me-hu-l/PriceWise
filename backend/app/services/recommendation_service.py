"""Rule-based procurement recommendations and supplier claim analysis."""

from sqlalchemy.orm import Session

from app.db.models import Evidence, Forecast, Material, Recommendation, Supplier
from app.schemas.recommendation import SupplierClaimAnalysis
from app.services import forecast_service, market_service, supplier_service


def _supply_risk(material: Material, suppliers: list[Supplier]) -> tuple[bool, list[str]]:
    reasons = []
    concentration = max((s.share_of_supply or 0.0 for s in suppliers), default=0.0)
    high_risk_supplier = any((s.risk_score or 0.0) >= 70 for s in suppliers)
    high_risk = (
        material.single_source_flag
        or concentration >= 0.7
        or high_risk_supplier
        or material.lead_time_days >= 60
    )
    if material.single_source_flag:
        reasons.append("single-source material")
    if concentration >= 0.7:
        reasons.append(f"supplier concentration at {concentration * 100:.0f}%")
    if material.lead_time_days >= 60:
        reasons.append(f"lead time of {material.lead_time_days} days")
    return high_risk, reasons


def _recommendation_rule(material: Material, forecast: Forecast, suppliers: list[Supplier]):
    supply_risk, supply_reasons = _supply_risk(material, suppliers)
    confidence = forecast.confidence_score
    forecast_change_pct = (forecast.point_forecast / material.current_price - 1) * 100
    rising = forecast.direction == "INCREASING"
    falling = forecast.direction == "DECREASING"
    high_confidence = confidence >= 70

    if rising and high_confidence and supply_risk:
        action, duration = "SHORT_LOCK", "3 months"
        decision_rule = "Rising forecast + high confidence + elevated supply risk -> secure near-term supply."
    elif rising and high_confidence:
        action, duration = "NEGOTIATE", "1-3 months"
        decision_rule = "Rising forecast + high confidence + manageable supply risk -> negotiate before prices rise."
    elif falling and high_confidence and not supply_risk:
        action, duration = "WAIT", "1 month"
        decision_rule = "Falling forecast + high confidence + manageable supply risk -> wait for a better price."
    elif not rising and supply_risk:
        action, duration = "DUAL_SOURCE", "3-6 months"
        decision_rule = "Stable/falling forecast + elevated supply risk -> reduce dependency through dual sourcing."
    else:
        action, duration = "MONITOR", "1 month"
        decision_rule = "Confidence or directional signal is not strong enough for an aggressive commitment -> monitor."

    conviction = min(100.0, max(0.0, confidence + (10 if supply_risk else 0)))
    movement = f"forecast {forecast.direction.lower()} by {abs(forecast_change_pct):.1f}%"
    reason_parts = [movement, f"confidence score is {confidence:.0f}/100"]
    if supply_reasons:
        reason_parts.extend(supply_reasons)
    if not supply_reasons:
        reason_parts.append("no high-concentration supply signal")
    return action, duration, conviction, "; ".join(reason_parts), supply_risk, decision_rule, forecast_change_pct, supply_reasons


def get_recommendation(db: Session, material: Material) -> Recommendation | None:
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return None
    suppliers = supplier_service.list_suppliers_for_material(db, material.id)
    action, duration, conviction, reason, supply_risk, decision_rule, forecast_change_pct, supply_reasons = _recommendation_rule(
        material, forecast, suppliers
    )
    old_ids = [r.id for r in db.query(Recommendation.id).filter_by(material_id=material.id).all()]
    if old_ids:
        db.query(Evidence).filter(Evidence.recommendation_id.in_(old_ids)).delete(
            synchronize_session=False
        )
        db.query(Recommendation).filter(Recommendation.id.in_(old_ids)).delete(
            synchronize_session=False
        )
    recommendation = Recommendation(
        material_id=material.id,
        forecast_id=forecast.id,
        action=action,
        conviction=round(conviction, 1),
        recommended_duration=duration,
        reason=reason,
    )
    db.add(recommendation)
    db.flush()
    evidence = [
        ("FORECAST", "Forecast outlook", f"The forecast is {forecast.direction.lower()} with confidence {forecast.confidence_score:.0f}.", "forecast"),
        ("SUPPLY_RISK", "Supply risk", "Supply concentration and lead-time indicators support elevated risk." if supply_risk else "No elevated supply concentration or lead-time signal was found.", "supplier data"),
    ]
    for evidence_type, title, description, source in evidence:
        db.add(Evidence(recommendation_id=recommendation.id, evidence_type=evidence_type, title=title, description=description, source=source, weight=1.0))
    events = market_service.list_events_for_material(db, material.id, db_material=material)
    for event in events[:3]:
        db.add(Evidence(recommendation_id=recommendation.id, evidence_type="MARKET_EVENT", title=event.title, description=event.description, source=event.source_name, weight=event.event_confidence))
    db.commit()
    db.refresh(recommendation)
    recommendation.forecast_direction = forecast.direction
    recommendation.forecast_change_pct = forecast_change_pct
    recommendation.confidence_score = forecast.confidence_score
    recommendation.supply_risk = "HIGH" if supply_risk else "MANAGEABLE"
    recommendation.supply_risk_factors = supply_reasons
    recommendation.decision_rule = decision_rule
    return recommendation


def analyze_supplier_claim(db: Session, material: Material, claimed_change_pct: float) -> SupplierClaimAnalysis | None:
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return None
    market_supported = (forecast.point_forecast / material.current_price - 1) * 100
    unexplained = claimed_change_pct - market_supported
    aligned = claimed_change_pct == 0 or market_supported == 0 or claimed_change_pct * market_supported > 0
    if abs(unexplained) <= 1.0:
        assessment = "SUPPORTED"
    elif aligned:
        assessment = "PARTIALLY_SUPPORTED"
    else:
        assessment = "UNSUPPORTED"
    guidance = (
        f"Use the market-supported range of {market_supported:.1f}% as the negotiation anchor; "
        f"{abs(unexplained):.1f} percentage points remain unexplained."
    )
    return SupplierClaimAnalysis(
        material_id=material.id,
        forecast_id=forecast.id,
        claimed_change_pct=claimed_change_pct,
        market_supported_change_pct=market_supported,
        unexplained_change_pct=unexplained,
        assessment=assessment,
        guidance=guidance,
    )
