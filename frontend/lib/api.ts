import type {
  ComponentDriver,
  MaterialDriverHistory,
  ConfidenceResponse,
  DashboardSummary,
  Material,
  MaterialComponent,
  MarketEvent,
  NotImplementedResponse,
  RecommendationResponse,
  ForecastExplanationResponse,
  ForecastResponse,
  PriceObservation,
  PriceUploadResult,
  ScenarioComparison,
  Supplier,
  SupplierQuote,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: isFormData ? init?.headers : { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => null);
    const detail = typeof error?.detail === "string" ? `: ${error.detail}` : "";
    throw new Error(`API request failed: ${init?.method ?? "GET"} ${path} (${res.status})${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listMaterials: () => apiFetch<Material[]>("/api/materials"),
  getMaterial: (id: number) => apiFetch<Material>(`/api/materials/${id}`),
  getComponents: (id: number) => apiFetch<MaterialComponent[]>(`/api/materials/${id}/components`),
  getDrivers: (id: number) => apiFetch<ComponentDriver[]>(`/api/materials/${id}/drivers`),
  getDriverObservations: (id: number) =>
    apiFetch<MaterialDriverHistory[]>(`/api/materials/${id}/driver-observations`),
  getHistory: (id: number) => apiFetch<PriceObservation[]>(`/api/materials/${id}/history`),
  uploadHistory: (id: number, file: File) => {
    const body = new FormData();
    body.append("file", file);
    return apiFetch<PriceUploadResult>(`/api/materials/${id}/history/upload`, {
      method: "POST",
      body,
      headers: {},
    });
  },
  runScenario: async (materialId: number, driverChanges: Record<string, number>) => {
    const response = await apiFetch<Partial<ScenarioComparison> & {
      normal_forecast?: ScenarioComparison["normal"];
      scenario_forecast?: ScenarioComparison["scenario"];
    }>("/api/scenario", {
      method: "POST",
      body: JSON.stringify({ material_id: materialId, driver_changes: driverChanges }),
    });
    const normal = response.normal ?? response.normal_forecast;
    const scenario = response.scenario ?? response.scenario_forecast;
    if (!normal || !scenario) {
      throw new Error("Scenario response did not include normal and what-if forecasts.");
    }
    const normalizeSnapshot = (snapshot: ScenarioComparison["normal"]): ScenarioComparison["normal"] => ({
      ...snapshot,
      recommendation_duration: snapshot.recommendation_duration ?? "See recommendation below",
      recommendation_conviction: snapshot.recommendation_conviction ?? snapshot.confidence_score ?? 0,
      forecast_change_pct: snapshot.forecast_change_pct ?? 0,
      supply_risk: snapshot.supply_risk ?? "UNKNOWN",
      supply_risk_factors: snapshot.supply_risk_factors ?? [],
      decision_rule: snapshot.decision_rule ?? snapshot.recommendation_reason ?? "No decision rule was returned.",
    });
    return {
      material_id: response.material_id ?? materialId,
      normal: normalizeSnapshot(normal),
      scenario: normalizeSnapshot(scenario),
    } satisfies ScenarioComparison;
  },
  getSuppliers: (id: number) => apiFetch<Supplier[]>(`/api/materials/${id}/suppliers`),
  getSupplierClaims: (id: number) => apiFetch<SupplierQuote[]>(`/api/materials/${id}/supplier-claims`),
  getMaterialMarketEvents: (id: number) => apiFetch<MarketEvent[]>(`/api/materials/${id}/market-events`),
  getForecast: (id: number) => apiFetch<ForecastResponse>(`/api/materials/${id}/forecast`),
  getForecastExplanation: (id: number) =>
    apiFetch<ForecastExplanationResponse>(`/api/materials/${id}/forecast/explanation`),
  getConfidence: (id: number) => apiFetch<ConfidenceResponse>(`/api/materials/${id}/confidence`),
  getRecommendation: (id: number) => apiFetch<RecommendationResponse>(`/api/materials/${id}/recommendation`),
  listMarketEvents: () => apiFetch<MarketEvent[]>("/api/market/events"),
  getDashboardSummary: () => apiFetch<DashboardSummary>("/api/dashboard/summary"),
};
