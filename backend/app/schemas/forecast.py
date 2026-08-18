from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.market_event import MarketEventRead


class ForecastRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    material_id: int
    forecast_date: date
    target_date: date
    horizon: str
    point_forecast: float
    lower_bound: float
    upper_bound: float
    direction: str
    model_version: str
    confidence_score: float
    baseline_pct_change: float | None
    driver_pct_change: float | None
    ml_pct_change: float | None
    disagreement_level: str | None
    data_mode: str | None
    regime_change_detected: bool
    mae: float | None
    rmse: float | None
    mape: float | None
    directional_accuracy: float | None
    interval_coverage: float | None
    created_at: datetime


class ForecastContributionRow(BaseModel):
    label: str
    contribution_value: float
    contribution_pct: float
    direction: str
    rank: int


class ForecastExplanationRead(BaseModel):
    forecast_id: int
    waterfall: list[ForecastContributionRow]
    market_events: list[MarketEventRead]
    narrative: str
