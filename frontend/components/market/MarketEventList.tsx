import type { MarketEvent } from "@/lib/types";
import { Card } from "@/components/common/Card";

const directionIcon: Record<string, string> = { UP: "🔴", DOWN: "🟢", NEUTRAL: "🟡" };

export function MarketEventList({ events }: { events: MarketEvent[] }) {
  if (events.length === 0) {
    return (
      <Card title="Market intelligence">
        <p className="text-sm text-slate-400">No market events recorded for this material.</p>
      </Card>
    );
  }
  return (
    <Card title="Market intelligence">
      <ul className="space-y-3">
        {events.map((e) => (
          <li key={e.id} className="border-b border-slate-100 pb-3 last:border-0">
            <p className="text-sm font-medium text-slate-900">
              {directionIcon[e.impact_direction] ?? "🟡"} {e.title}
            </p>
            <p className="text-xs text-slate-500">
              {e.source_name ?? "Unknown source"} · {new Date(e.published_at).toLocaleDateString()}
              {" · "}
              {e.impact_magnitude} impact · {e.impact_horizon.toLowerCase()} horizon
              {typeof e.event_confidence === "number" && ` · ${e.event_confidence}% confidence`}
            </p>
          </li>
        ))}
      </ul>
    </Card>
  );
}
