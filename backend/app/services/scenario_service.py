"""What-if forecasts using explicit next-month driver assumptions."""

from sqlalchemy.orm import Session

from app.db.models import Material
from app.ml import confidence as confidence_ml
from app.ml import ensemble, explainability, preprocessing
from app.schemas.scenario import ScenarioComparison, ScenarioForecast
from app.services import forecast_service, market_service, recommendation_service, supplier_service


def _direction(change: float) -> str:
    if change > 0.005:
        return "INCREASING"
    if change < -0.005:
        return "DECREASING"
    return "STABLE"


def _snapshot(
    db: Session,
    material: Material,
    price_df,
    driver_df,
    overrides: dict[str, float] | None,
) -> ScenarioForecast:
    result = ensemble.build_ensemble(
        price_df,
        driver_df,
        projected_driver_changes=overrides,
        driver_weight_boost=ensemble.DRIVER_WEIGHT_BOOST,
    )
    current_price = float(price_df["price"].iloc[-1])
    point_forecast = current_price * (1 + result.ensemble_pct_change)
    spread = ensemble.INTERVAL_Z * result.interval_std_pct
    lower_bound = current_price * (1 + result.ensemble_pct_change - spread)
    upper_bound = current_price * (1 + result.ensemble_pct_change + spread)
    contributions = explainability.build_waterfall(
        result.contributions, target_pct_change=result.ensemble_pct_change
    )
    events = market_service.list_events_for_material(db, material.id, db_material=material)
    metrics = forecast_service._select_best_metrics(result.backtest_metrics)
    confidence_result = confidence_ml.compute_confidence(
        settings=forecast_service.get_settings(),
        n_observations=len(price_df),
        edge_strengths_confidences=forecast_service._driver_edge_strengths(db, material.id),
        best_candidate_metrics=metrics,
        event_confidences=[e.event_confidence for e in events if e.event_confidence is not None],
        event_directions=[e.impact_direction for e in events],
        disagreement_level=result.disagreement_level,
        regime_change_detected=forecast_service._detect_regime_change(
            price_df["pct_change"].dropna().tolist()
        ),
    )
    scenario_values = type(
        "ScenarioForecastValues",
        (),
        {
            "direction": _direction(result.ensemble_pct_change),
            "point_forecast": point_forecast,
            "confidence_score": confidence_result.overall_score,
        },
    )()
    action, duration, conviction, reason, supply_risk, decision_rule, forecast_change_pct, supply_reasons = recommendation_service._recommendation_rule(
        material,
        scenario_values,
        supplier_service.list_suppliers_for_material(db, material.id),
    )
    return ScenarioForecast(
        point_forecast=round(point_forecast, 2),
        lower_bound=round(min(lower_bound, upper_bound), 2),
        upper_bound=round(max(lower_bound, upper_bound), 2),
        direction=_direction(result.ensemble_pct_change),
        confidence_score=round(confidence_result.overall_score, 1),
        contributions=contributions,
        driver_weights=result.weights,
        recommendation_action=action,
        recommendation_duration=duration,
        recommendation_conviction=round(conviction, 1),
        forecast_change_pct=round(forecast_change_pct, 2),
        supply_risk="HIGH" if supply_risk else "MANAGEABLE",
        supply_risk_factors=supply_reasons,
        decision_rule=decision_rule,
        recommendation_reason=reason,
    )


def run_scenario(
    db: Session, material: Material, driver_changes: dict[str, float]
) -> ScenarioComparison | None:
    price_df = preprocessing.build_price_series(db, material.id)
    if len(price_df) < forecast_service.MIN_OBSERVATIONS_FOR_FORECAST:
        return None
    dates = price_df["date"].tolist()
    driver_df = preprocessing.build_driver_pct_change_matrix(db, material.id, dates)
    unknown = set(driver_changes) - set(driver_df.columns)
    if unknown:
        raise ValueError(f"Unknown material drivers: {', '.join(sorted(unknown))}")
    normal_forecast = forecast_service.get_or_generate_forecast(db, material)
    if normal_forecast is None:
        return None
    normal = _snapshot(db, material, price_df, driver_df, None)
    return ScenarioComparison(
        material_id=material.id,
        normal=normal,
        scenario=_snapshot(db, material, price_df, driver_df, driver_changes),
    )
