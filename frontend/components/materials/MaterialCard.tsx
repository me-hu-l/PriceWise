import Link from "next/link";
import type { Material } from "@/lib/types";
import { Card } from "@/components/common/Card";
import { RiskIndicator } from "@/components/common/RiskIndicator";

export function MaterialCard({ material }: { material: Material }) {
  return (
    <Link href={`/materials/${material.id}`}>
      <Card className="transition hover:border-slate-300 hover:shadow-md">
        <div className="mb-2 flex items-start justify-between">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-400">
              {material.material_code}
            </p>
            <h3 className="font-semibold text-slate-900">{material.name}</h3>
            <p className="text-sm text-slate-500">{material.category}</p>
          </div>
          <RiskIndicator level={material.criticality} />
        </div>
        <p className="text-lg font-semibold text-slate-900">
          {material.currency} {material.current_price.toLocaleString()} / {material.unit}
        </p>
        {material.single_source_flag && (
          <p className="mt-1 text-xs font-medium text-red-600">Single-source</p>
        )}
      </Card>
    </Link>
  );
}
