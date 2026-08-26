import type { ForecastResponse } from "@/lib/types";
import { Card } from "@/components/common/Card";
import { isInsufficientData } from "./ForecastCard";

const disagreementTone: Record<string, string> = {
  LOW: "text-green-700",
  MEDIUM: "text-amber-700",
  HIGH: "text-red-700",
};

export function ModelDisagreement({ forecast }: { forecast: ForecastResponse }) {
  if (isInsufficientData(forecast)) return null;

  const rows = [
    { label: "Baseline", value: forecast.baseline_pct_change },
    { label: "Driver model", value: forecast.driver_pct_change },
    { label: "ML model", value: forecast.ml_pct_change },
  ].filter((r) => r.value != null) as Array<{ label: string; value: number }>;

  if (rows.length === 0) return null;

  return (
    <Card title="Model disagreement">
      <ul className="space-y-1 text-sm">
        {rows.map((r) => (
          <li key={r.label} className="flex justify-between">
            <span className="text-slate-600">{r.label}</span>
            <span className="font-medium text-slate-900">{(r.value * 100).toFixed(1)}%</span>
          </li>
        ))}
      </ul>
      {forecast.disagreement_level && (
        <p className={`mt-2 text-sm font-medium ${disagreementTone[forecast.disagreement_level]}`}>
          Disagreement: {forecast.disagreement_level}
        </p>
      )}
      {(forecast.mae != null || forecast.directional_accuracy != null) && (
        <p className="mt-2 text-sm text-slate-500">
          Backtest — MAE {forecast.mae?.toFixed(2)} · MAPE {forecast.mape?.toFixed(1)}% · directional
          accuracy {forecast.directional_accuracy != null ? `${(forecast.directional_accuracy * 100).toFixed(0)}%` : "—"}
        </p>
      )}
    </Card>
  );
}
