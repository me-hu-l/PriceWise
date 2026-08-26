from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	evidence_type: str
	title: str
	description: str | None
	source: str | None
	weight: float | None
	created_at: datetime


class RecommendationRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	material_id: int
	forecast_id: int | None
	action: str
	conviction: float
	recommended_duration: str | None
	reason: str | None
	created_at: datetime
	evidence: list[EvidenceRead]
	forecast_direction: str
	forecast_change_pct: float
	confidence_score: float
	supply_risk: str
	supply_risk_factors: list[str]
	decision_rule: str


class SupplierClaimRequest(BaseModel):
	material_id: int
	claimed_change_pct: float = Field(description="Supplier's claimed change in percentage points")
	current_price: float | None = None


class SupplierClaimAnalysis(BaseModel):
	material_id: int
	forecast_id: int
	claimed_change_pct: float
	market_supported_change_pct: float
	unexplained_change_pct: float
	assessment: str
	guidance: str
