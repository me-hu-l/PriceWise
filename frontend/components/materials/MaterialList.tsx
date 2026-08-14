import type { Material } from "@/lib/types";
import { MaterialCard } from "./MaterialCard";

export function MaterialList({ materials }: { materials: Material[] }) {
  if (materials.length === 0) {
    return <p className="text-sm text-slate-500">No materials found.</p>;
  }
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {materials.map((m) => (
        <MaterialCard key={m.id} material={m} />
      ))}
    </div>
  );
}
