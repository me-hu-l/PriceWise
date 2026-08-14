from datetime import date

from app.db import models


def test_material_component_relationship(db_session):
    material = models.Material(
        material_code="MAT-X",
        name="Test Material",
        category="Test Category",
        description=None,
        unit="kg",
        currency="USD",
        criticality="MEDIUM",
        current_price=100.0,
        current_price_date=date(2026, 1, 1),
        lead_time_days=30,
        single_source_flag=False,
    )
    db_session.add(material)
    db_session.flush()

    component = models.MaterialComponent(
        material_id=material.id,
        component_name="Test component",
        component_code="TC",
        percentage_of_cost=50.0,
        unit="%",
    )
    db_session.add(component)
    db_session.commit()

    db_session.refresh(material)
    assert len(material.components) == 1
    assert material.components[0].component_name == "Test component"
    assert component.material.material_code == "MAT-X"


def test_component_driver_knowledge_graph_edge(db_session):
    driver = models.Driver(name="Test Driver", category="ENERGY", default_lag_days=10)
    material = models.Material(
        material_code="MAT-Y",
        name="Y",
        category="Y",
        unit="kg",
        currency="USD",
        criticality="LOW",
        current_price=1.0,
        current_price_date=date(2026, 1, 1),
        lead_time_days=1,
        single_source_flag=False,
    )
    db_session.add_all([driver, material])
    db_session.flush()

    component = models.MaterialComponent(
        material_id=material.id, component_name="C", percentage_of_cost=100.0
    )
    db_session.add(component)
    db_session.flush()

    edge = models.ComponentDriver(
        component_id=component.id,
        driver_id=driver.id,
        relationship_strength=0.5,
        lag_period=10,
        direction="POSITIVE",
    )
    db_session.add(edge)
    db_session.commit()

    assert component.component_drivers[0].driver.name == "Test Driver"
    assert driver.component_links[0].component.component_name == "C"
