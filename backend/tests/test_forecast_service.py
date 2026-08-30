import pytest

from app.services import forecast_service


def test_generate_forecast_bounds_ordered_and_versioned(db_session, material_with_history):
    forecast = forecast_service.generate_forecast(db_session, material_with_history)

    assert forecast is not None
    assert forecast.lower_bound <= forecast.upper_bound
    assert forecast.model_version == forecast_service.MODEL_VERSION
    assert forecast.data_mode in ("LOW_DATA", "LIMITED_DATA", "MODERATE", "STRONG")
    assert forecast.direction in ("INCREASING", "DECREASING", "STABLE")
    assert 0 <= forecast.confidence_score <= 100

    explanation = forecast_service.get_forecast_explanation(db_session, material_with_history)
    assert all(row["label"] != "ML Residual" for row in explanation["waterfall"])
    attributed_change = sum(row["contribution_value"] for row in explanation["waterfall"])
    expected_change = forecast.point_forecast / material_with_history.current_price - 1
    assert attributed_change == pytest.approx(expected_change)
    assert sum(row["contribution_pct"] for row in explanation["waterfall"]) == pytest.approx(100.0)


def test_generate_forecast_returns_none_for_too_little_history(db_session, seeded_material):
    """seeded_material has only 1 price observation."""
    forecast = forecast_service.generate_forecast(db_session, seeded_material)
    assert forecast is None


def test_get_or_generate_forecast_is_cached(db_session, material_with_history):
    first = forecast_service.get_or_generate_forecast(db_session, material_with_history)
    second = forecast_service.get_or_generate_forecast(db_session, material_with_history)
    assert first.id == second.id  # second call reads the persisted row, doesn't regenerate


def test_recommendation_is_precomputed_and_cached(db_session, material_with_history):
    from app.services import recommendation_service

    forecast = forecast_service.generate_forecast(db_session, material_with_history)
    assert forecast is not None

    rec1 = recommendation_service.get_recommendation(db_session, material_with_history)
    assert rec1 is not None
    assert rec1.forecast_id == forecast.id
    assert len(rec1.evidence) >= 2
    assert rec1.action in {"SHORT_LOCK", "LONG_LOCK", "WAIT", "NEGOTIATE", "STOCK", "DUAL_SOURCE", "MONITOR"}
    assert rec1.forecast_direction
    assert rec1.confidence_score >= 0
    assert rec1.supply_risk in {"HIGH", "MANAGEABLE"}

    rec2 = recommendation_service.get_recommendation(db_session, material_with_history)
    assert rec2 is not None
    assert rec1.id == rec2.id  # reads the persisted row, does not delete or regenerate

