import type { Supplier } from "@/lib/types";
import { Card } from "@/components/common/Card";

export function SupplierList({ suppliers }: { suppliers: Supplier[] }) {
  return (
    <Card title="Suppliers">
      <ul className="space-y-3">
        {suppliers.map((s) => (
          <li key={s.id} className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3 text-sm last:border-0 last:pb-0">
            <div className="flex items-start gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
              <div>
                <p className="font-medium text-slate-900">{s.name}</p>
                <p className="text-sm text-slate-500">
                  {s.country} · lead time {s.lead_time_days ?? "—"} days
                  {s.single_source && " · single-source"}
                </p>
              </div>
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
