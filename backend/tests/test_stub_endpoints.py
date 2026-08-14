"""Stub endpoints must never fabricate numbers — only a structured not-implemented payload."""


def test_forecast_endpoint_is_stub(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/forecast")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "not_implemented"
    assert "point_forecast" not in body


def test_forecast_explanation_endpoint_is_stub(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/forecast/explanation")
    assert res.json()["status"] == "not_implemented"


def test_confidence_endpoint_is_stub(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/confidence")
    body = res.json()
    assert body["status"] == "not_implemented"
    assert "overall_score" not in body


def test_recommendation_endpoint_is_stub(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/recommendation")
    body = res.json()
    assert body["status"] == "not_implemented"
    assert "action" not in body


def test_post_forecast_is_stub(client, seeded_material):
    res = client.post("/api/forecast", json={"material_id": seeded_material.id})
    assert res.json()["status"] == "not_implemented"


def test_post_scenario_is_stub(client, seeded_material):
    res = client.post("/api/scenario", json={"fx_change": 0.02})
    assert res.json()["status"] == "not_implemented"


def test_post_supplier_claim_analyze_is_stub(client, seeded_material):
    res = client.post(
        "/api/supplier-claim/analyze",
        json={"material_id": seeded_material.id, "claimed_change_pct": 9.0},
    )
    assert res.json()["status"] == "not_implemented"
