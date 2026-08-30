"""Rule-based procurement recommendations and supplier claim analysis."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Evidence, Forecast, Material, Recommendation, Supplier
from app.schemas.recommendation import SupplierClaimAnalysis
from app.schemas.supplier import AnalyzedSupplierQuote, SupplierQuoteBatchAnalysisResponse
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
    forecast_change_pct = (forecast.point_forecast / material.current_price - 1) * 100 if material.current_price else 0.0
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


def _attach_transient_fields(
    recommendation: Recommendation,
    material: Material,
    forecast: Forecast,
    suppliers: list[Supplier],
) -> Recommendation:
    _, _, _, _, supply_risk, decision_rule, forecast_change_pct, supply_reasons = _recommendation_rule(
        material, forecast, suppliers
    )
    recommendation.forecast_direction = forecast.direction
    recommendation.forecast_change_pct = forecast_change_pct
    recommendation.confidence_score = forecast.confidence_score
    recommendation.supply_risk = "HIGH" if supply_risk else "MANAGEABLE"
    recommendation.supply_risk_factors = supply_reasons
    recommendation.decision_rule = decision_rule
    return recommendation


def generate_recommendation(
    db: Session, material: Material, forecast: Forecast
) -> Recommendation:
    suppliers = supplier_service.list_suppliers_for_material(db, material.id)
    (
        action,
        duration,
        conviction,
        reason,
        supply_risk,
        decision_rule,
        forecast_change_pct,
        supply_reasons,
    ) = _recommendation_rule(material, forecast, suppliers)

    old_ids = [
        r.id
        for r in db.query(Recommendation.id)
        .filter(
            (Recommendation.material_id == material.id)
            | (Recommendation.forecast_id == forecast.id)
        )
        .all()
    ]
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
        (
            "FORECAST",
            "Forecast outlook",
            f"The forecast is {forecast.direction.lower()} with confidence {forecast.confidence_score:.0f}.",
            "forecast",
        ),
        (
            "SUPPLY_RISK",
            "Supply risk",
            (
                "Supply concentration and lead-time indicators support elevated risk."
                if supply_risk
                else "No elevated supply concentration or lead-time signal was found."
            ),
            "supplier data",
        ),
    ]
    for evidence_type, title, description, source in evidence:
        db.add(
            Evidence(
                recommendation_id=recommendation.id,
                evidence_type=evidence_type,
                title=title,
                description=description,
                source=source,
                weight=1.0,
            )
        )

    events = market_service.list_events_for_material(db, material.id, db_material=material)
    for event in events[:3]:
        db.add(
            Evidence(
                recommendation_id=recommendation.id,
                evidence_type="MARKET_EVENT",
                title=event.title,
                description=event.description,
                source=event.source_name,
                weight=event.event_confidence,
            )
        )

    db.commit()
    db.refresh(recommendation)
    recommendation.forecast_direction = forecast.direction
    recommendation.forecast_change_pct = forecast_change_pct
    recommendation.confidence_score = forecast.confidence_score
    recommendation.supply_risk = "HIGH" if supply_risk else "MANAGEABLE"
    recommendation.supply_risk_factors = supply_reasons
    recommendation.decision_rule = decision_rule
    return recommendation


def get_recommendation(db: Session, material: Material) -> Recommendation | None:
    forecast = forecast_service.get_or_generate_forecast(db, material)
    if forecast is None:
        return None
    existing = (
        db.query(Recommendation)
        .filter(
            Recommendation.material_id == material.id,
            Recommendation.forecast_id == forecast.id,
        )
        .order_by(Recommendation.created_at.desc())
        .first()
    )
    if existing is not None:
        suppliers = supplier_service.list_suppliers_for_material(db, material.id)
        return _attach_transient_fields(existing, material, forecast, suppliers)
    return generate_recommendation(db, material, forecast)


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


def analyze_supplier_quotes(
    db: Session,
    material: Material,
    driver_changes: dict[str, float] | None,
    quotes: list,
) -> SupplierQuoteBatchAnalysisResponse | None:
    from app.schemas.supplier import AnalyzedSupplierQuote, SupplierQuoteBatchAnalysisResponse
    from app.services import scenario_service

    has_scenario = bool(
        driver_changes and any(abs(float(val)) > 0.0001 for val in driver_changes.values())
    )

    if has_scenario:
        scenario_comp = scenario_service.run_scenario(db, material, driver_changes)
        if scenario_comp is None:
            return None
        active_forecast_price = scenario_comp.scenario.point_forecast
        active_direction = scenario_comp.scenario.direction
        confidence_score = scenario_comp.scenario.confidence_score
        is_scenario = True
    else:
        forecast = forecast_service.get_or_generate_forecast(db, material)
        if forecast is None:
            return None
        active_forecast_price = forecast.point_forecast
        active_direction = forecast.direction
        confidence_score = forecast.confidence_score
        is_scenario = False

    db_quotes = supplier_service.list_quotes_for_material(db, material.id)
    baseline_quote_by_supplier = {q.supplier_id: q.quoted_price for q in db_quotes}

    analyzed_list = []
    for q_input in quotes:
        supplier_id = getattr(q_input, "supplier_id", None) or q_input.get("supplier_id")
        quoted_price = getattr(q_input, "quoted_price", None) or q_input.get("quoted_price")
        if supplier_id is None or quoted_price is None:
            continue

        supplier = db.get(Supplier, supplier_id)
        if supplier is None:
            continue

        baseline_price = baseline_quote_by_supplier.get(supplier.id)
        is_custom_quote = (
            baseline_price is not None and abs(quoted_price - baseline_price) > 0.01
        ) or (baseline_price is None)

        gap_pct = (
            ((quoted_price - active_forecast_price) / active_forecast_price) * 100
            if active_forecast_price
            else 0.0
        )
        claimed_change = (
            ((quoted_price - material.current_price) / material.current_price) * 100
            if material.current_price
            else 0.0
        )
        market_supported_change = (
            ((active_forecast_price - material.current_price) / material.current_price) * 100
            if material.current_price
            else 0.0
        )
        unexplained = claimed_change - market_supported_change

        high_risk_supplier = (
            (supplier.risk_score or 0) >= 70
            or supplier.single_source
            or material.single_source_flag
        )

        scenario_label = "custom driver scenario" if is_scenario else "base market forecast"

        if gap_pct <= 0.0:
            recommendation = "ACCEPT"
            assessment = "SUPPORTED"
            reason = f"Under the active {scenario_label} (expected price {material.currency} {active_forecast_price:,.2f}), the supplier quote of {material.currency} {quoted_price:,.2f} is within or below the expected market range (gap {gap_pct:+.1f}%)."
            guidance = "Quote is fully supported by active market forecast. Proceed to accept quote or lock in volume."
        elif gap_pct <= 2.0:
            recommendation = "ACCEPT" if not high_risk_supplier else "NEGOTIATE"
            assessment = "SUPPORTED"
            reason = f"Under the active {scenario_label} (expected price {material.currency} {active_forecast_price:,.2f}), the supplier quote of {material.currency} {quoted_price:,.2f} exceeds forecast by +{gap_pct:.1f}%, within acceptable tolerance."
            guidance = "Quote aligns closely with forecast. Minor negotiation optional unless high supplier risk applies."
        elif gap_pct <= 8.0:
            recommendation = "NEGOTIATE"
            assessment = "PARTIALLY_SUPPORTED"
            reason = f"Supplier quote ({material.currency} {quoted_price:,.2f}) exceeds active market forecast ({material.currency} {active_forecast_price:,.2f}) by +{gap_pct:.1f}% ({unexplained:+.1f}% unexplained relative to market drivers)."
            guidance = f"Use market-supported target price of {material.currency} {active_forecast_price:,.2f} as negotiation anchor."
        else:
            recommendation = "DUAL_SOURCE" if high_risk_supplier else "REJECT"
            assessment = "UNSUPPORTED"
            reason = f"Supplier quote ({material.currency} {quoted_price:,.2f}) significantly exceeds active market forecast ({material.currency} {active_forecast_price:,.2f}) by +{gap_pct:.1f}%."
            guidance = f"Unexplained gap of {unexplained:+.1f}%. Reject price increase or request cost breakdown; consider alternative suppliers."

        analyzed_list.append(
            AnalyzedSupplierQuote(
                supplier_id=supplier.id,
                supplier_name=supplier.name,
                supplier_code=supplier.supplier_code,
                country=supplier.country,
                qualification_status=supplier.qualification_status,
                lead_time_days=supplier.lead_time_days,
                share_of_supply=supplier.share_of_supply,
                risk_score=supplier.risk_score,
                single_source=supplier.single_source,
                quoted_price=round(quoted_price, 2),
                baseline_quoted_price=round(baseline_price, 2)
                if baseline_price is not None
                else None,
                is_custom_quote=is_custom_quote,
                active_forecast_price=round(active_forecast_price, 2),
                quote_vs_forecast_gap_pct=round(gap_pct, 2),
                claimed_change_pct=round(claimed_change, 2),
                market_supported_change_pct=round(market_supported_change, 2),
                unexplained_change_pct=round(unexplained, 2),
                assessment=assessment,
                recommendation=recommendation,
                recommendation_reason=reason,
                guidance=guidance,
            )
        )

    return SupplierQuoteBatchAnalysisResponse(
        material_id=material.id,
        active_forecast_price=round(active_forecast_price, 2),
        active_forecast_direction=active_direction,
        confidence_score=round(confidence_score, 1),
        is_scenario=is_scenario,
        analyzed_quotes=analyzed_list,
    )
