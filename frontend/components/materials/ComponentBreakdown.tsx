import type { MaterialComponent } from "@/lib/types";
import { Card } from "@/components/common/Card";

export function ComponentBreakdown({ components }: { components: MaterialComponent[] }) {
  return (
    <Card title="Material composition">
      <ul className="space-y-2">
        {components.map((c) => (
          <li key={c.id} className="flex items-center justify-between text-sm">
            <span className="text-slate-700">{c.component_name}</span>
            <div className="flex w-1/2 items-center gap-2">
              <div className="h-2 flex-1 rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-slate-700"
                  style={{ width: `${c.percentage_of_cost}%` }}
                />
              </div>
              <span className="w-12 text-right font-medium text-slate-900">
                {c.percentage_of_cost}%
              </span>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
