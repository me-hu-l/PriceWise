"use client";

import { useState } from "react";
import type {
  ComponentDriver,
  ConfidenceResponse,
  ForecastExplanationResponse,
  ForecastResponse,
  MarketEvent,
  Material,
  MaterialComponent,
  MaterialDriverHistory,
  PriceObservation,
  RecommendationResponse,
  ScenarioComparison,
  Supplier,
  SupplierQuote,
} from "@/lib/types";

import { Card } from "@/components/common/Card";
import { RiskIndicator } from "@/components/common/RiskIndicator";
import { ForecastCard, isInsufficientData } from "@/components/forecast/ForecastCard";
import { ConfidenceBreakdown } from "@/components/forecast/ConfidenceBreakdown";
import { DriverWaterfall } from "@/components/forecast/DriverWaterfall";
import { ModelDisagreement } from "@/components/forecast/ModelDisagreement";
import { ScenarioSimulator } from "@/components/forecast/ScenarioSimulator";
import { PriceHistoryChart } from "@/components/materials/PriceHistoryChart";
import { PriceHistoryUpload } from "@/components/materials/PriceHistoryUpload";
import { ComponentBreakdown } from "@/components/materials/ComponentBreakdown";
import { KnowledgeGraph } from "@/components/materials/KnowledgeGraph";
import { SupplierList } from "@/components/materials/SupplierList";
import { DriverList } from "@/components/drivers/DriverList";
import { DriverHistoryCharts } from "@/components/drivers/DriverHistoryCharts";
import { MarketEventList } from "@/components/market/MarketEventList";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";

import { SupplierIntelligence } from "@/components/suppliers/SupplierIntelligence";

interface MaterialDetailClientProps {
  material: Material;
  components: MaterialComponent[];
  history: PriceObservation[];
  drivers: ComponentDriver[];
  driverHistories: MaterialDriverHistory[];
  events: MarketEvent[];
  suppliers: Supplier[];
  supplierQuotes: SupplierQuote[];
  allCatalogSuppliers: Supplier[];
  forecast: ForecastResponse;
  confidence: ConfidenceResponse;
  explanation: ForecastExplanationResponse;
  recommendation: RecommendationResponse;
}

// Client container for Material Detail tabs
export function MaterialDetailClient({
  material,
  components,
  history,
  drivers,
  driverHistories,
  events,
  suppliers,
  supplierQuotes,
  allCatalogSuppliers,
  forecast,
  confidence,
  explanation,
  recommendation,
}: MaterialDetailClientProps) {
  const [activeTab, setActiveTab] = useState<"OVERVIEW" | "SUPPLIER_INTELLIGENCE">("OVERVIEW");

  // Shared active scenario state across tabs
  const [activeDriverChanges, setActiveDriverChanges] = useState<Record<string, number>>(() =>
    Object.fromEntries(
      driverHistories.map((h) => [
        h.driver_name,
        h.projected_value && h.observations.length
          ? h.projected_value / h.observations[h.observations.length - 1].value - 1
          : 0,
      ])
    )
  );
  const [activeScenarioComparison, setActiveScenarioComparison] =
    useState<ScenarioComparison | null>(null);

  function handleScenarioChange(
    changes: Record<string, number>,
    comparison: ScenarioComparison | null
  ) {
    setActiveDriverChanges(changes);
    setActiveScenarioComparison(comparison);
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-200 pb-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">{material.material_code}</p>
          <h2 className="text-2xl font-semibold text-slate-900">{material.name}</h2>
          <p className="text-slate-500">{material.category}</p>
        </div>
        <div className="flex items-center gap-3">
          <RiskIndicator level={material.criticality} />
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-200">
        <nav className="-mb-px flex space-x-6">
          <button
            type="button"
            onClick={() => setActiveTab("OVERVIEW")}
            className={`border-b-2 pb-3 text-sm font-semibold transition-colors ${
              activeTab === "OVERVIEW"
                ? "border-teal-700 text-teal-800"
                : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
            }`}
          >
            📊 Market & Forecast Overview
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("SUPPLIER_INTELLIGENCE")}
            className={`border-b-2 pb-3 text-sm font-semibold transition-colors ${
              activeTab === "SUPPLIER_INTELLIGENCE"
                ? "border-teal-700 text-teal-800"
                : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
            }`}
          >
            🤝 Supplier Intelligence
          </button>
        </nav>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "OVERVIEW" && (
        <div className="space-y-6">
          <KnowledgeGraph materialName={material.name} components={components} drivers={drivers} />

          <PriceHistoryUpload materialId={material.id} />

          <Card>
            <p className="text-3xl font-semibold text-slate-900">
              {material.currency} {material.current_price.toLocaleString()} / {material.unit}
            </p>
            <p className="text-sm text-slate-500">
              As of {new Date(material.current_price_date).toLocaleDateString("en-GB", { timeZone: "UTC" })} · lead time{" "}
              {material.lead_time_days} days
              {material.single_source_flag && " · single-source"}
            </p>
          </Card>

          <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(220px,0.42fr)]">
            <PriceHistoryChart history={history} forecast={forecast} />
            <div className="lg:max-w-sm">
              <ForecastCard forecast={forecast} />
            </div>
          </div>

          <DriverHistoryCharts histories={driverHistories} />

          <ScenarioSimulator materialId={material.id} histories={driverHistories} />

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
            <ConfidenceBreakdown confidence={confidence} />
            <DriverWaterfall explanation={explanation} />
          </div>

          <ModelDisagreement forecast={forecast} />

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
            <ComponentBreakdown components={components} />
            <SupplierList suppliers={suppliers} />
          </div>

          <DriverList drivers={drivers} />
          <MarketEventList events={events} />

          <RecommendationCard recommendation={recommendation} />
        </div>
      )}

      {/* TAB 2: SUPPLIER INTELLIGENCE */}
      {activeTab === "SUPPLIER_INTELLIGENCE" && (
        <SupplierIntelligence
          material={material}
          baseForecast={forecast && !isInsufficientData(forecast) ? forecast : null}
          histories={driverHistories}
          initialSuppliers={suppliers}
          initialQuotes={supplierQuotes}
          allCatalogSuppliers={allCatalogSuppliers}
          activeDriverChanges={activeDriverChanges}
          activeScenarioComparison={activeScenarioComparison}
          onScenarioChange={handleScenarioChange}
        />
      )}
    </div>
  );
}
