from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401  (populates Base.metadata)
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_material(db_session):
    """Minimal single-material fixture covering every Phase 1 entity."""
    driver = models.Driver(
        name="Rare Earth Index",
        category="RAW_MATERIAL",
        description="Test driver",
        unit="index",
        source_type="commodity_index",
        default_lag_days=30,
        directionality="POSITIVE",
        reliability_score=0.8,
    )
    db_session.add(driver)
    db_session.flush()

    material = models.Material(
        material_code="MAT-TEST",
        name="Test Ceria Slurry",
        category="CMP Consumable",
        description="Test material",
        unit="L",
        currency="USD",
        criticality="HIGH",
        current_price=1240.0,
        current_price_date=date(2026, 7, 1),
        lead_time_days=75,
        single_source_flag=True,
    )
    db_session.add(material)
    db_session.flush()

    component = models.MaterialComponent(
        material_id=material.id,
        component_name="Ceria abrasive",
        component_code="CER",
        percentage_of_cost=42.0,
        unit="%",
        description="Test component",
    )
    db_session.add(component)
    db_session.flush()

    db_session.add(
        models.ComponentDriver(
            component_id=component.id,
            driver_id=driver.id,
            relationship_strength=0.87,
            elasticity=0.9,
            lag_period=30,
            direction="POSITIVE",
            confidence=0.82,
            rationale="Test rationale",
        )
    )

    db_session.add(
        models.PriceObservation(
            material_id=material.id,
            date=date(2026, 7, 1),
            price=1240.0,
            currency="USD",
            unit="L",
            source="test",
            data_quality="SYNTHETIC",
        )
    )

    supplier = models.Supplier(
        name="Supplier A",
        supplier_code="SUP-A-TEST",
        country="Japan",
        qualification_status="QUALIFIED",
        lead_time_days=75,
        single_source=False,
        share_of_supply=0.82,
        risk_score=78.0,
    )
    db_session.add(supplier)
    db_session.flush()

    db_session.add(
        models.SupplierQuote(
            supplier_id=supplier.id,
            material_id=material.id,
            quote_date=date(2026, 7, 1),
            quoted_price=1352.0,
            currency="USD",
            unit="L",
            previous_price=1240.0,
            claimed_change_pct=9.0,
            reason="Test claim",
        )
    )

    db_session.add(
        models.MarketEvent(
            title="Rare-earth export restriction announced",
            description="Test event",
            event_type="EXPORT_RESTRICTION",
            source_name="Test source",
            published_at=datetime(2026, 4, 1),
            affected_driver="Rare Earth Index",
            affected_material="Test Ceria Slurry",
            impact_direction="UP",
            impact_magnitude="HIGH",
            impact_horizon="MEDIUM",
            event_confidence=82.0,
        )
    )

    db_session.commit()
    return material
