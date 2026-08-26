import type { ForecastExplanationResponse } from "@/lib/types";
import { Card } from "@/components/common/Card";
import { splitSentences } from "@/lib/text";
import { isInsufficientData } from "./ForecastCard";

/** Rendered as plain HTML bars instead of a recharts BarChart — recharts'
 * ResponsiveContainer/axis scaling was unreliable in this environment. */
export function DriverWaterfall({ explanation }: { explanation: ForecastExplanationResponse }) {
  if (isInsufficientData(explanation)) {
    return (
      <Card title="Why is price moving?">
        <p className="text-sm text-slate-400">{explanation.reason}</p>
      </Card>
    );
  }

  const rows = explanation.waterfall.map((row) => ({
    label: row.label,
    pct: row.contribution_value * 100,
  }));
  const maxAbs = Math.max(...rows.map((r) => Math.abs(r.pct)), 0.1);

  return (
    <Card title="Why is price moving?">
      <ul className="space-y-2.5">
        {rows.map((row) => (
          <li key={row.label} className="flex items-center gap-3 text-sm">
            <span className="w-36 shrink-0 truncate text-slate-700">{row.label}</span>
            <div className="relative h-4 flex-1 rounded bg-slate-100">
              <div className="absolute inset-y-0 left-1/2 w-px bg-slate-300" />
              <div
                className={`absolute inset-y-0 rounded ${row.pct >= 0 ? "bg-red-600" : "bg-green-600"}`}
                style={
                  row.pct >= 0
                    ? { left: "50%", width: `${(Math.abs(row.pct) / maxAbs) * 50}%` }
                    : { right: "50%", width: `${(Math.abs(row.pct) / maxAbs) * 50}%` }
                }
              />
            </div>
            <span className="w-14 shrink-0 text-right font-medium text-slate-900">
              {row.pct >= 0 ? "+" : ""}
              {row.pct.toFixed(2)}%
            </span>
          </li>
        ))}
      </ul>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">
        {splitSentences(explanation.narrative).map((sentence, i) => (
          <li key={i}>{sentence}</li>
        ))}
      </ul>
    </Card>
  );
}
