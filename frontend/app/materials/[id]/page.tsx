import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { Card } from "@/components/common/Card";
import { RiskIndicator } from "@/components/common/RiskIndicator";
import { NotAvailableCard } from "@/components/forecast/NotAvailableCard";
import { ForecastCard } from "@/components/forecast/ForecastCard";
import { ConfidenceBreakdown } from "@/components/forecast/ConfidenceBreakdown";
import { DriverWaterfall } from "@/components/forecast/DriverWaterfall";
import { ModelDisagreement } from "@/components/forecast/ModelDisagreement";
import { PriceHistoryChart } from "@/components/materials/PriceHistoryChart";
import { ComponentBreakdown } from "@/components/materials/ComponentBreakdown";
import { SupplierList } from "@/components/materials/SupplierList";
import { DriverList } from "@/components/drivers/DriverList";
import { MarketEventList } from "@/components/market/MarketEventList";

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

  const [components, history, drivers, events, suppliers, forecast, confidence, explanation] =
    await Promise.all([
      api.getComponents(materialId),
      api.getHistory(materialId),
      api.getDrivers(materialId),
      api.getMaterialMarketEvents(materialId),
      api.getSuppliers(materialId),
      api.getForecast(materialId),
      api.getConfidence(materialId),
      api.getForecastExplanation(materialId),
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

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ForecastCard forecast={forecast} />
        <ConfidenceBreakdown confidence={confidence} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DriverWaterfall explanation={explanation} />
        <ModelDisagreement forecast={forecast} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <PriceHistoryChart history={history} />
        <ComponentBreakdown components={components} />
      </div>

      <DriverList drivers={drivers} />
      <MarketEventList events={events} />
      <SupplierList suppliers={suppliers} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <NotAvailableCard title="Recommendation" phase="Phase 3" />
      </div>
    </div>
  );
}
