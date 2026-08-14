import type { DashboardSummary } from "@/lib/types";
import { Card } from "@/components/common/Card";

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  const items = [
    { label: "Materials monitored", value: summary.materials_monitored },
    { label: "High / critical criticality", value: summary.high_or_critical_criticality },
    { label: "Single-source materials", value: summary.single_source_materials },
  ];
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {items.map((item) => (
        <Card key={item.label}>
          <p className="text-3xl font-semibold text-slate-900">{item.value}</p>
          <p className="text-sm text-slate-500">{item.label}</p>
        </Card>
      ))}
    </div>
  );
}
