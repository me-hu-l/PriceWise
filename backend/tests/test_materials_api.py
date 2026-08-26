from app.db import models


def test_list_materials(client, seeded_material):
    res = client.get("/api/materials")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert body[0]["material_code"] == "MAT-TEST"


def test_get_material_detail(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Test Ceria Slurry"


def test_get_material_not_found(client, seeded_material):
    res = client.get("/api/materials/9999")
    assert res.status_code == 404


def test_get_components(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/components")
    assert res.status_code == 200
    assert res.json()[0]["component_name"] == "Ceria abrasive"


def test_get_drivers_knowledge_graph(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/drivers")
    assert res.status_code == 200
    body = res.json()
    assert body[0]["driver_name"] == "Rare Earth Index"
    assert body[0]["relationship_strength"] == 0.87


def test_get_history(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/history")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_upload_history_uses_overlay_and_preserves_seeded_rows(
    client, db_session, seeded_material
):
    csv_content = "date,price,currency,unit\n2026-01-01,1300,USD,L\n2026-02-01,1315,USD,L\n2026-03-01,1330,USD,L\n"
    res = client.post(
        f"/api/materials/{seeded_material.id}/history/upload",
        files={"file": ("history.csv", csv_content, "text/csv")},
    )
    assert res.status_code == 200
    assert res.json()["observation_count"] == 3

    history = client.get(f"/api/materials/{seeded_material.id}/history").json()
    assert [row["price"] for row in history] == [1300.0, 1315.0, 1330.0]
    assert (
        len(
            db_session.query(models.PriceObservation)
            .filter_by(material_id=seeded_material.id)
            .all()
        )
        == 1
    )


def test_get_suppliers(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/suppliers")
    assert res.status_code == 200
    assert res.json()[0]["supplier_code"] == "SUP-A-TEST"


def test_get_supplier_claims(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/supplier-claims")
    assert res.status_code == 200
    assert res.json()[0]["claimed_change_pct"] == 9.0


def test_get_material_market_events(client, seeded_material):
    res = client.get(f"/api/materials/{seeded_material.id}/market-events")
    assert res.status_code == 200
    assert res.json()[0]["event_type"] == "EXPORT_RESTRICTION"


def test_list_all_market_events(client, seeded_material):
    res = client.get("/api/market/events")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_dashboard_summary(client, seeded_material):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    body = res.json()
    assert body["materials_monitored"] == 1
    assert body["high_or_critical_criticality"] == 1
    assert body["single_source_materials"] == 1
