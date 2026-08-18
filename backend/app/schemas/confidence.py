from pydantic import BaseModel, ConfigDict


class ConfidenceRead(BaseModel):
    """Five-component confidence breakdown (roadmap section 13)."""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    forecast_id: int
    data_score: float
    driver_score: float
    model_score: float
    market_score: float
    stability_score: float
    overall_score: float
    explanation: str
