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
