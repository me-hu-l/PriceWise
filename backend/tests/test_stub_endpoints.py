"""Forecast/confidence/
explanation became real in Phase 2 (see test_forecast_api.py) but still return a
structured "insufficient_data" payload (not fake numbers) when history is too sparse."""


def test_forecast_endpoint_insufficient_data(client, seeded_material):
    """seeded_material has only 1 price observation — below the forecast minimum."""
    res = client.get(f"/api/materials/{seeded_material.id}/forecast")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "insufficient_data"
    assert "point_forecast" not in body


def test_forecast_explanation_endpoint_insufficient_data(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/forecast/explanation")
    assert res.json()["status"] == "insufficient_data"


def test_confidence_endpoint_insufficient_data(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/confidence")
    body = res.json()
    assert body["status"] == "insufficient_data"
    assert "overall_score" not in body


def test_recommendation_endpoint_returns_insufficient_data(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/recommendation")
    body = res.json()
    assert body["status"] == "insufficient_data"


def test_post_forecast_insufficient_data(client, seeded_material):
    res = client.post("/api/forecast", json={"material_id": seeded_material.id})
    assert res.json()["status"] == "insufficient_data"


def test_post_scenario_returns_insufficient_data(client, seeded_material):
    res = client.post(
        "/api/scenario",
        json={"material_id": seeded_material.id, "driver_changes": {"Rare Earth Index": 0.02}},
    )
    assert res.status_code == 422



def test_post_supplier_claim_analyze_returns_insufficient_data(client, seeded_material):
    res = client.post(
        "/api/supplier-claim/analyze",
        json={"material_id": seeded_material.id, "claimed_change_pct": 9.0},
    )
    assert res.status_code == 422
