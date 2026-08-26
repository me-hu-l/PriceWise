from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_code: str
    name: str
    category: str
    description: str | None
    unit: str
    currency: str
    criticality: str
    current_price: float
    current_price_date: date
    lead_time_days: int
    single_source_flag: bool
    created_at: datetime
    updated_at: datetime


class MaterialComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    component_name: str
    component_code: str | None
    percentage_of_cost: float
    unit: str | None
    description: str | None


class PriceObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    date: date
    price: float
    currency: str
    unit: str | None
    supplier_id: int | None
    quantity: float | None
    contract_type: str | None
    source: str | None
    data_quality: str | None


class PriceUploadResult(BaseModel):
    message: str
    observation_count: int
    latest_date: date
    latest_price: float
