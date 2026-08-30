from datetime import date

from pydantic import BaseModel, ConfigDict


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    supplier_code: str
    country: str | None
    qualification_status: str
    lead_time_days: int | None
    single_source: bool
    share_of_supply: float | None
    risk_score: float | None


class SupplierQuoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    material_id: int
    quote_date: date
    quoted_price: float
    currency: str
    unit: str | None
    previous_price: float | None
    claimed_change_pct: float | None
    reason: str | None
    valid_until: date | None


class SupplierQuoteItemInput(BaseModel):
    supplier_id: int
    quoted_price: float
    valid_until: date | None = None
    reason: str | None = None


class SupplierQuoteBatchAnalysisRequest(BaseModel):
    material_id: int
    driver_changes: dict[str, float] | None = None
    quotes: list[SupplierQuoteItemInput]


class AnalyzedSupplierQuote(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_code: str
    country: str | None = None
    qualification_status: str
    lead_time_days: int | None = None
    share_of_supply: float | None = None
    risk_score: float | None = None
    single_source: bool = False
    quoted_price: float
    baseline_quoted_price: float | None = None
    is_custom_quote: bool = False
    active_forecast_price: float
    quote_vs_forecast_gap_pct: float
    claimed_change_pct: float
    market_supported_change_pct: float
    unexplained_change_pct: float
    assessment: str
    recommendation: str
    recommendation_reason: str
    guidance: str


class SupplierQuoteBatchAnalysisResponse(BaseModel):
    material_id: int
    active_forecast_price: float
    active_forecast_direction: str
    confidence_score: float
    is_scenario: bool
    analyzed_quotes: list[AnalyzedSupplierQuote]
