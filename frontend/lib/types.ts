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

/** Structured placeholder returned by endpoints not yet implemented (Phase 2+). */
export interface NotImplementedResponse {
  status: "not_implemented";
  feature: string;
  phase: string;
  reason: string;
}
