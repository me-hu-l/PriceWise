import { api } from "@/lib/api";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { MaterialList } from "@/components/materials/MaterialList";

export default async function HomePage() {
  const [summary, materials] = await Promise.all([
    api.getDashboardSummary(),
    api.listMaterials(),
  ]);

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Executive control tower</h2>
        <SummaryCards summary={summary} />
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Materials</h2>
        <MaterialList materials={materials} />
      </section>
    </div>
  );
}
