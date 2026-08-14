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
