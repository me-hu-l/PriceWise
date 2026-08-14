import type { ComponentDriver } from "@/lib/types";
import { Card } from "@/components/common/Card";

export function DriverList({ drivers }: { drivers: ComponentDriver[] }) {
  return (
    <Card title="Price drivers (material knowledge graph)">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
            <th className="pb-2">Component</th>
            <th className="pb-2">Driver</th>
            <th className="pb-2">Category</th>
            <th className="pb-2 text-right">Strength</th>
          </tr>
        </thead>
        <tbody>
          {drivers.map((d) => (
            <tr key={d.id} className="border-b border-slate-100 last:border-0">
              <td className="py-2 text-slate-700">{d.component_name}</td>
              <td className="py-2 font-medium text-slate-900">{d.driver_name}</td>
              <td className="py-2 text-slate-500">{d.driver_category}</td>
              <td className="py-2 text-right text-slate-900">
                {(d.relationship_strength * 100).toFixed(0)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
