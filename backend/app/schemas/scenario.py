from pydantic import BaseModel, Field


class ScenarioRequest(BaseModel):
    material_id: int
    driver_changes: dict[str, float] = Field(
        description="Next-month driver percentage changes as decimals, keyed by driver name"
    )


class ScenarioForecast(BaseModel):
    point_forecast: float
    lower_bound: float
    upper_bound: float
    direction: str
    confidence_score: float
    contributions: list[dict]
    driver_weights: dict[str, float]
    recommendation_action: str
    recommendation_duration: str
    recommendation_conviction: float
    forecast_change_pct: float
    supply_risk: str
    supply_risk_factors: list[str]
    decision_rule: str
    recommendation_reason: str


class ScenarioComparison(BaseModel):
    material_id: int
    normal: ScenarioForecast
    scenario: ScenarioForecast