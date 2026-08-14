import type { Supplier } from "@/lib/types";
import { Card } from "@/components/common/Card";

export function SupplierList({ suppliers }: { suppliers: Supplier[] }) {
  return (
    <Card title="Suppliers">
      <ul className="space-y-2">
        {suppliers.map((s) => (
          <li key={s.id} className="flex items-center justify-between text-sm">
            <div>
              <p className="font-medium text-slate-900">{s.name}</p>
              <p className="text-xs text-slate-500">
                {s.country} · lead time {s.lead_time_days ?? "—"} days
              </p>
            </div>
            <span className="font-semibold text-slate-900">
              {s.share_of_supply != null ? `${(s.share_of_supply * 100).toFixed(0)}%` : "—"}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
