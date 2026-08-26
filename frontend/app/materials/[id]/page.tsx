import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { Card } from "@/components/common/Card";
import { RiskIndicator } from "@/components/common/RiskIndicator";
import { ForecastCard } from "@/components/forecast/ForecastCard";
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

export default async function MaterialDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const materialId = Number(id);
  if (Number.isNaN(materialId)) notFound();

  let material;
  try {
    material = await api.getMaterial(materialId);
  } catch {
    notFound();
  }

  const [components, history, drivers, driverHistories, events, suppliers, forecast, confidence, explanation, recommendation] =
    await Promise.all([
      api.getComponents(materialId),
      api.getHistory(materialId),
      api.getDrivers(materialId),
      api.getDriverObservations(materialId),
      api.getMaterialMarketEvents(materialId),
      api.getSuppliers(materialId),
      api.getForecast(materialId),
      api.getConfidence(materialId),
      api.getForecastExplanation(materialId),
      api.getRecommendation(materialId),
    ]);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">{material.material_code}</p>
          <h2 className="text-2xl font-semibold text-slate-900">{material.name}</h2>
          <p className="text-slate-500">{material.category}</p>
        </div>
        <RiskIndicator level={material.criticality} />
      </div>

      <KnowledgeGraph materialName={material.name} components={components} drivers={drivers} />

      <PriceHistoryUpload materialId={materialId} />

      <Card>
        <p className="text-3xl font-semibold text-slate-900">
          {material.currency} {material.current_price.toLocaleString()} / {material.unit}
        </p>
        <p className="text-sm text-slate-500">
          As of {new Date(material.current_price_date).toLocaleDateString()} · lead time{" "}
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

      <ScenarioSimulator materialId={materialId} histories={driverHistories} />

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
  );
}
