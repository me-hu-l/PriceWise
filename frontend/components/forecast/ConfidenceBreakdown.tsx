import type { Confidence, ConfidenceResponse } from "@/lib/types";
import { splitSentences } from "@/lib/text";
import { isInsufficientData } from "./ForecastCard";

const components: Array<{ key: keyof Omit<Confidence, "forecast_id" | "overall_score" | "explanation">; label: string }> = [
  { key: "data_score", label: "Data quality" },
  { key: "driver_score", label: "Driver strength" },
  { key: "model_score", label: "Model performance" },
  { key: "market_score", label: "Market signals" },
  { key: "stability_score", label: "Stability" },
];

export function ConfidenceBreakdown({ confidence }: { confidence: ConfidenceResponse }) {
  if (isInsufficientData(confidence)) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5">
        <h3 className="mb-1 text-sm font-semibold text-slate-500">Forecast confidence score</h3>
        <p className="text-sm text-slate-400">{confidence.reason}</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">Forecast confidence score</h3>
        <span className="text-lg font-semibold text-slate-900">
          {confidence.overall_score.toFixed(0)}%
        </span>
      </div>
      <ul className="space-y-2">
        {components.map((c) => (
          <li key={c.key} className="flex items-center gap-2 text-sm">
            <span className="w-36 shrink-0 text-slate-600">{c.label}</span>
            <div className="h-2 flex-1 rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-slate-700"
                style={{ width: `${confidence[c.key]}%` }}
              />
            </div>
            <span className="w-10 text-right font-medium text-slate-900">
              {confidence[c.key].toFixed(0)}
            </span>
          </li>
        ))}
      </ul>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-500">
        {splitSentences(confidence.explanation).map((sentence, i) => (
          <li key={i}>{sentence}</li>
        ))}
      </ul>
    </div>
  );
}
