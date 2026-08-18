export interface Material {
  id: number;
  material_code: string;
  name: string;
  category: string;
  description: string | null;
  unit: string;
  currency: string;
  criticality: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  current_price: number;
  current_price_date: string;
  lead_time_days: number;
  single_source_flag: boolean;
  created_at: string;
  updated_at: string;
}

export interface MaterialComponent {
  id: number;
  material_id: number;
  component_name: string;
  component_code: string | null;
  percentage_of_cost: number;
  unit: string | null;
  description: string | null;
}

export interface PriceObservation {
  id: number;
  material_id: number;
  date: string;
  price: number;
  currency: string;
  unit: string | null;
  supplier_id: number | null;
  quantity: number | null;
  contract_type: string | null;
  source: string | null;
  data_quality: string | null;
}

export interface ComponentDriver {
  id: number;
  component_id: number;
  component_name: string;
  driver_id: number;
  driver_name: string;
  driver_category: string;
  relationship_strength: number;
  elasticity: number | null;
  lag_period: number;
  direction: string;
  confidence: number | null;
  rationale: string | null;
}

export interface MarketEvent {
  id: number;
  title: string;
  description: string | null;
  event_type: string;
  source_name: string | null;
  source_url: string | null;
  published_at: string;
  affected_driver: string | null;
  affected_material: string | null;
  impact_direction: "UP" | "DOWN" | "NEUTRAL";
  impact_magnitude: "LOW" | "MEDIUM" | "HIGH";
  impact_horizon: "SHORT" | "MEDIUM" | "LONG";
  event_confidence: number | null;
  processed_by_llm: boolean;
}

export interface Supplier {
  id: number;
  name: string;
  supplier_code: string;
  country: string | null;
  qualification_status: string;
  lead_time_days: number | null;
  single_source: boolean;
  share_of_supply: number | null;
  risk_score: number | null;
}

export interface SupplierQuote {
  id: number;
  supplier_id: number;
  material_id: number;
  quote_date: string;
  quoted_price: number;
  currency: string;
  unit: string | null;
  previous_price: number | null;
  claimed_change_pct: number | null;
  reason: string | null;
  valid_until: string | null;
}

export interface DashboardSummary {
  materials_monitored: number;
  high_or_critical_criticality: number;
  single_source_materials: number;
}

/** Structured placeholder returned by endpoints not yet implemented (Phase 3+). */
export interface NotImplementedResponse {
  status: "not_implemented";
  feature: string;
  phase: string;
  reason: string;
}

/** Returned instead of a forecast/confidence when a material genuinely lacks history. */
export interface InsufficientDataResponse {
  status: "insufficient_data";
  reason: string;
}

export interface Forecast {
  id: number;
  material_id: number;
  forecast_date: string;
  target_date: string;
  horizon: string;
  point_forecast: number;
  lower_bound: number;
  upper_bound: number;
  direction: "INCREASING" | "DECREASING" | "STABLE";
  model_version: string;
  confidence_score: number;
  baseline_pct_change: number | null;
  driver_pct_change: number | null;
  ml_pct_change: number | null;
  disagreement_level: "LOW" | "MEDIUM" | "HIGH" | null;
  data_mode: "LOW_DATA" | "LIMITED_DATA" | "MODERATE" | "STRONG" | null;
  regime_change_detected: boolean;
  mae: number | null;
  rmse: number | null;
  mape: number | null;
  directional_accuracy: number | null;
  interval_coverage: number | null;
  created_at: string;
}

export interface ForecastContributionRow {
  label: string;
  contribution_value: number;
  contribution_pct: number;
  direction: string;
  rank: number;
}

export interface ForecastExplanation {
  forecast_id: number;
  waterfall: ForecastContributionRow[];
  market_events: MarketEvent[];
  narrative: string;
}

export interface Confidence {
  forecast_id: number;
  data_score: number;
  driver_score: number;
  model_score: number;
  market_score: number;
  stability_score: number;
  overall_score: number;
  explanation: string;
}

export type ForecastResponse = Forecast | InsufficientDataResponse;
export type ForecastExplanationResponse = ForecastExplanation | InsufficientDataResponse;
export type ConfidenceResponse = Confidence | InsufficientDataResponse;

