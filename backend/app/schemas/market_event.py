from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MarketEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    event_type: str
    source_name: str | None
    source_url: str | None
    published_at: datetime
    affected_driver: str | None
    affected_material: str | None
    impact_direction: str
    impact_magnitude: str
    impact_horizon: str
    event_confidence: float | None
    processed_by_llm: bool
