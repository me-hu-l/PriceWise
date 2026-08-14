import { api } from "@/lib/api";
import { MaterialList } from "@/components/materials/MaterialList";

export default async function MaterialsPage() {
  const materials = await api.listMaterials();
  return (
    <div>
      <h2 className="mb-4 text-lg font-semibold text-slate-900">Material explorer</h2>
      <MaterialList materials={materials} />
    </div>
  );
}
