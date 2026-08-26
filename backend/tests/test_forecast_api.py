import pytest


def test_forecast_endpoint_returns_real_forecast(client, material_with_history):
    res = client.get(f"/api/materials/{material_with_history.id}/forecast")
    assert res.status_code == 200
    body = res.json()
    assert "point_forecast" in body
    assert body["lower_bound"] <= body["upper_bound"]
    assert body["model_version"]


def test_confidence_endpoint_returns_real_breakdown(client, material_with_history):
    res = client.get(f"/api/materials/{material_with_history.id}/confidence")
    body = res.json()
    assert 0 <= body["overall_score"] <= 100
    assert body["explanation"]


def test_forecast_explanation_endpoint_returns_waterfall(client, material_with_history):
    res = client.get(f"/api/materials/{material_with_history.id}/forecast/explanation")
    body = res.json()
    assert "waterfall" in body
    assert "narrative" in body
    assert len(body["waterfall"]) >= 1


def test_driver_observations_endpoint_returns_history_and_projection(client, material_with_history):
    res = client.get(f"/api/materials/{material_with_history.id}/driver-observations")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert len(body[0]["observations"]) == 24
    assert body[0]["projected_date"]
    assert body[0]["projected_value"] is not None


def test_recommendation_endpoint_returns_rule_based_result(client, material_with_history):
    res = client.get(f"/api/materials/{material_with_history.id}/recommendation")
    body = res.json()
    assert body["action"] in {"SHORT_LOCK", "LONG_LOCK", "WAIT", "NEGOTIATE", "STOCK", "DUAL_SOURCE", "MONITOR"}
    assert 0 <= body["conviction"] <= 100
    assert len(body["evidence"]) >= 2
    assert body["forecast_direction"]
    assert body["confidence_score"] >= 0
    assert body["supply_risk"] in {"HIGH", "MANAGEABLE"}
    assert body["decision_rule"]


def test_supplier_claim_analysis_compares_forecast(client, material_with_history):
    res = client.post(
        "/api/supplier-claim/analyze",
        json={"material_id": material_with_history.id, "claimed_change_pct": 9.0},
    )
    body = res.json()
    assert res.status_code == 200
    assert body["assessment"] in {"SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"}
    assert body["unexplained_change_pct"] == pytest.approx(
        body["claimed_change_pct"] - body["market_supported_change_pct"]
    )


def test_scenario_compares_normal_and_driver_override(client, material_with_history):
    res = client.post(
        "/api/scenario",
        json={"material_id": material_with_history.id, "driver_changes": {"Test Energy Index": 0.15}},
    )
    body = res.json()
    assert res.status_code == 200
    assert body["normal"]["point_forecast"] != body["scenario"]["point_forecast"]
    assert body["normal"]["recommendation_action"] != "NORMAL FORECAST"
    assert body["normal"]["driver_weights"] == body["scenario"]["driver_weights"]
    regular = client.get(f"/api/materials/{material_with_history.id}/forecast").json()
    assert regular["point_forecast"] == body["normal"]["point_forecast"]
    assert body["normal"]["recommendation_duration"]
    assert body["scenario"]["recommendation_duration"]
    assert 0 <= body["scenario"]["recommendation_conviction"] <= 100
    assert body["scenario"]["supply_risk"] in {"HIGH", "MANAGEABLE"}
    assert body["scenario"]["decision_rule"]
    assert body["scenario"]["contributions"]
    assert body["scenario"]["recommendation_action"]


def test_post_forecast_endpoint_returns_real_forecast(client, material_with_history):
    res = client.post("/api/forecast", json={"material_id": material_with_history.id})
    assert "point_forecast" in res.json()
