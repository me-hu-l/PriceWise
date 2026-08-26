"""Forecast generation + retrieval (roadmap section 8).

Forecasts are precomputed by the seed pipeline (roadmap section 39 — never
retrain on page load) and lazily (re)generated on first request if missing.
Never fabricates a forecast: materials with too little price history get a
structured "insufficient data" response instead (roadmap section 40).
"""

from __future__ import annotations

from datetime import date

import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import (
    ComponentDriver,
    ConfidenceComponent,
    Driver,
    Forecast,
    ForecastContribution,
    Material,
    MaterialComponent,
)
from app.ml import confidence as confidence_ml
from app.ml import ensemble, explainability, preprocessing
from app.services import market_service

MODEL_VERSION = "phase2-ensemble-v1"
MIN_OBSERVATIONS_FOR_FORECAST = 3
REGIME_CHANGE_WINDOW = 3
REGIME_CHANGE_MULTIPLIER = 1.5


def _next_month(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def _detect_regime_change(pct_changes: list[float]) -> bool:
    if len(pct_changes) < REGIME_CHANGE_WINDOW * 2:
        return False
    recent = pct_changes[-REGIME_CHANGE_WINDOW:]
    prior = pct_changes[:-REGIME_CHANGE_WINDOW]
    recent_vol = float(np.std(recent))
    prior_vol = float(np.std(prior))
    return prior_vol > 0 and recent_vol > REGIME_CHANGE_MULTIPLIER * prior_vol


def _select_best_metrics(backtest_metrics: dict[str, dict | None]) -> dict | None:
    """Pick the candidate model with the lowest backtest MAE, not just whichever
    key happens to be non-None first (that previously always preferred "ml")."""
    available = [m for m in backtest_metrics.values() if m is not None]
    if not available:
        return None
    return min(available, key=lambda m: m["mae"])


def _driver_edge_strengths(db: Session, material_id: int) -> list[tuple[float, float]]:
    edges = (
        db.query(ComponentDriver)
        .join(MaterialComponent, ComponentDriver.component_id == MaterialComponent.id)
        .filter(MaterialComponent.material_id == material_id)
        .all()
    )
    return [(e.relationship_strength, e.confidence or 0.5) for e in edges]


def _update_driver_edge_strengths(
    db: Session, material_id: int, waterfall: list[dict]
) -> None:
    attribution_by_driver = {
        row["label"]: abs(row["contribution_pct"]) / 100.0 for row in waterfall
    }
    edges = (
        db.query(ComponentDriver, Driver)
        .join(MaterialComponent, ComponentDriver.component_id == MaterialComponent.id)
        .join(Driver, ComponentDriver.driver_id == Driver.id)
        .filter(MaterialComponent.material_id == material_id)
        .all()
    )
    for edge, driver in edges:
        edge.relationship_strength = attribution_by_driver.get(driver.name, 0.0)


def _refresh_cached_driver_attributions(
    db: Session, forecast: Forecast, material: Material
) -> None:
    rows = (
        db.query(ForecastContribution, Driver)
        .join(Driver, ForecastContribution.driver_id == Driver.id)
        .filter(ForecastContribution.forecast_id == forecast.id)
        .filter(Driver.name != explainability.ML_RESIDUAL_DRIVER_NAME)
        .all()
    )
    raw_rows = [
        {
            "driver_name": driver.name,
            "contribution_value": contribution.contribution_value,
            "direction": contribution.direction,
        }
        for contribution, driver in rows
    ]
    target_pct_change = (
        forecast.point_forecast / material.current_price - 1 if material.current_price else None
    )
    waterfall = explainability.build_waterfall(raw_rows, target_pct_change=target_pct_change)
    by_driver_name = {driver.name: contribution for contribution, driver in rows}
    for row in waterfall:
        contribution = by_driver_name.get(row["label"])
        if contribution is None:
            continue
        contribution.contribution_value = row["contribution_value"]
        contribution.contribution_pct = row["contribution_pct"]
        contribution.direction = row["direction"]
        contribution.rank = row["rank"]
    _update_driver_edge_strengths(db, forecast.material_id, waterfall)


def generate_forecast(db: Session, material: Material) -> Forecast | None:
    """(Re)compute and persist the latest forecast for a material. Returns None if
    there isn't even enough data for a baseline forecast."""
    settings = get_settings()
    price_df = preprocessing.build_price_series(db, material.id)
    n = len(price_df)
    if n < MIN_OBSERVATIONS_FOR_FORECAST:
        return None

    dates = price_df["date"].tolist()
    driver_df = preprocessing.build_driver_pct_change_matrix(db, material.id, dates)

    result = ensemble.build_ensemble(
        price_df, driver_df, driver_weight_boost=ensemble.DRIVER_WEIGHT_BOOST
    )

    current_price = float(price_df["price"].iloc[-1])
    point_forecast = current_price * (1 + result.ensemble_pct_change)
    spread = ensemble.INTERVAL_Z * result.interval_std_pct
    lower_bound = current_price * (1 + result.ensemble_pct_change - spread)
    upper_bound = current_price * (1 + result.ensemble_pct_change + spread)
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound

    if result.ensemble_pct_change > 0.005:
        direction = "INCREASING"
    elif result.ensemble_pct_change < -0.005:
        direction = "DECREASING"
    else:
        direction = "STABLE"

    pct_changes = price_df["pct_change"].dropna().tolist()
    regime_change = _detect_regime_change(pct_changes)
    data_mode = confidence_ml.classify_data_mode(n, settings)

    best_metrics = _select_best_metrics(result.backtest_metrics)

    events = market_service.list_events_for_material(db, material.id, db_material=material)
    event_confidences = [e.event_confidence for e in events if e.event_confidence is not None]
    event_directions = [e.impact_direction for e in events]

    confidence_result = confidence_ml.compute_confidence(
        settings=settings,
        n_observations=n,
        edge_strengths_confidences=_driver_edge_strengths(db, material.id),
        best_candidate_metrics=best_metrics,
        event_confidences=event_confidences,
        event_directions=event_directions,
        disagreement_level=result.disagreement_level,
        regime_change_detected=regime_change,
    )

    forecast_date = dates[-1]

    # Idempotent: replace any previous forecast for this material (delete children
    # explicitly first — bulk Query.delete() bypasses ORM cascade behavior).
    old_forecast_ids = [
        f.id for f in db.query(Forecast.id).filter(Forecast.material_id == material.id).all()
    ]
    if old_forecast_ids:
        db.query(ForecastContribution).filter(
            ForecastContribution.forecast_id.in_(old_forecast_ids)
        ).delete(synchronize_session=False)
        db.query(ConfidenceComponent).filter(
            ConfidenceComponent.forecast_id.in_(old_forecast_ids)
        ).delete(synchronize_session=False)
        db.query(Forecast).filter(Forecast.id.in_(old_forecast_ids)).delete(
            synchronize_session=False
        )
    db.flush()

    forecast = Forecast(
        material_id=material.id,
        forecast_date=forecast_date,
        target_date=_next_month(forecast_date),
        horizon="1M",
        point_forecast=round(point_forecast, 2),
        lower_bound=round(lower_bound, 2),
        upper_bound=round(upper_bound, 2),
        direction=direction,
        model_version=MODEL_VERSION,
        confidence_score=round(confidence_result.overall_score, 1),
        baseline_pct_change=result.baseline_pct_change,
        driver_pct_change=result.driver_pct_change,
        ml_pct_change=result.ml_pct_change,
        disagreement_level=result.disagreement_level,
        data_mode=data_mode,
        regime_change_detected=regime_change,
        mae=best_metrics["mae"] if best_metrics else None,
        rmse=best_metrics["rmse"] if best_metrics else None,
        mape=best_metrics["mape"] if best_metrics else None,
        directional_accuracy=best_metrics["directional_accuracy"] if best_metrics else None,
        interval_coverage=None,
    )
    db.add(forecast)
    db.flush()

    waterfall = explainability.build_waterfall(
        result.contributions, target_pct_change=result.ensemble_pct_change
    )
    _update_driver_edge_strengths(db, material.id, waterfall)
    for row in waterfall:
        driver_id = preprocessing.get_driver_id_by_name(db, row["label"])
        if driver_id is None:
            continue
        db.add(
            ForecastContribution(
                forecast_id=forecast.id,
                driver_id=driver_id,
                contribution_value=row["contribution_value"],
                contribution_pct=row["contribution_pct"],
                direction=row["direction"],
                rank=row["rank"],
            )
        )

    db.add(
        ConfidenceComponent(
            forecast_id=forecast.id,
            data_score=confidence_result.data_score,
            driver_score=confidence_result.driver_score,
            model_score=confidence_result.model_score,
            market_score=confidence_result.market_score,
            stability_score=confidence_result.stability_score,
            overall_score=confidence_result.overall_score,
            explanation=confidence_result.explanation,
        )
    )

    db.commit()
    db.refresh(forecast)
    return forecast


def get_or_generate_forecast(db: Session, material: Material) -> Forecast | None:
    existing = (
        db.query(Forecast)
        .filter(Forecast.material_id == material.id)
        .order_by(Forecast.created_at.desc())
        .first()
    )
    if existing is not None:
        _refresh_cached_driver_attributions(db, existing, material)
        db.commit()
        return existing
    return generate_forecast(db, material)


def get_forecast_explanation(db: Session, material: Material) -> dict | None:
    forecast = get_or_generate_forecast(db, material)
    if forecast is None:
        return None
    contributions = (
        db.query(ForecastContribution)
        .join(Driver, ForecastContribution.driver_id == Driver.id)
        .filter(ForecastContribution.forecast_id == forecast.id)
        .filter(Driver.name != explainability.ML_RESIDUAL_DRIVER_NAME)
        .order_by(ForecastContribution.rank)
        .all()
    )
    waterfall = [
        {
            "label": c.driver.name,
            "contribution_value": c.contribution_value,
            "contribution_pct": c.contribution_pct,
            "direction": c.direction,
            "rank": c.rank,
        }
        for c in contributions
    ]
    events = market_service.list_events_for_material(db, material.id, db_material=material)
    narrative = explainability.build_narrative(
        material.name,
        (forecast.point_forecast / material.current_price - 1) if material.current_price else 0.0,
        waterfall,
        forecast.data_mode or "STRONG",
    )
    return {
        "forecast_id": forecast.id,
        "waterfall": waterfall,
        "market_events": events,
        "narrative": narrative,
    }

