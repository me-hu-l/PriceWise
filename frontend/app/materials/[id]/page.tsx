import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { MaterialDetailClient } from "@/components/materials/MaterialDetailClient";

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

  const [
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
  ] = await Promise.all([
    api.getComponents(materialId),
    api.getHistory(materialId),
    api.getDrivers(materialId),
    api.getDriverObservations(materialId),
    api.getMaterialMarketEvents(materialId),
    api.getSuppliers(materialId),
    api.getSupplierClaims(materialId).catch(() => []),
    api.listAllSuppliers().catch(() => []),
    api.getForecast(materialId),
    api.getConfidence(materialId),
    api.getForecastExplanation(materialId),
    api.getRecommendation(materialId),
  ]);

  return (
    <MaterialDetailClient
      material={material}
      components={components}
      history={history}
      drivers={drivers}
      driverHistories={driverHistories}
      events={events}
      suppliers={suppliers}
      supplierQuotes={supplierQuotes}
      allCatalogSuppliers={allCatalogSuppliers}
      forecast={forecast}
      confidence={confidence}
      explanation={explanation}
      recommendation={recommendation}
    />
  );
}
