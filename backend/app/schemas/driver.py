from pydantic import BaseModel, ConfigDict


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    description: str | None
    unit: str | None
    source_type: str | None
    default_lag_days: int
    directionality: str | None
    reliability_score: float | None


class ComponentDriverRead(BaseModel):
    """A knowledge-graph edge: component -> driver, with both names denormalized for display."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    component_id: int
    component_name: str
    driver_id: int
    driver_name: str
    driver_category: str
    relationship_strength: float
    elasticity: float | None
    lag_period: int
    direction: str
    confidence: float | None
    rationale: str | None
