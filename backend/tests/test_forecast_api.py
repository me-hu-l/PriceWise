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


def test_recommendation_still_stub_for_material_with_history(client, material_with_history):
    """Recommendation stays a Phase 3 stub even once forecast/confidence are real."""
    res = client.get(f"/api/materials/{material_with_history.id}/recommendation")
    assert res.json()["status"] == "not_implemented"


def test_post_forecast_endpoint_returns_real_forecast(client, material_with_history):
    res = client.post("/api/forecast", json={"material_id": material_with_history.id})
    assert "point_forecast" in res.json()
