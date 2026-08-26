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
    throw new Error(`API request failed: ${init?.method ?? "GET"} ${path} (${res.status})`);
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
