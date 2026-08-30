"use client";

import { useMemo, useState } from "react";
import type { ForecastResponse, PriceObservation } from "@/lib/types";
import { Card } from "@/components/common/Card";
import { isInsufficientData } from "@/components/forecast/ForecastCard";

const WIDTH = 900;
const HEIGHT = 260;
const PADDING = { top: 12, right: 16, bottom: 24, left: 56 };

type TimeRange = "3M" | "6M" | "1Y" | "3Y" | "ALL";

const RANGES: { label: string; value: TimeRange }[] = [
  { label: "3M", value: "3M" },
  { label: "6M", value: "6M" },
  { label: "1Y", value: "1Y" },
  { label: "3Y", value: "3Y" },
  { label: "All", value: "ALL" },
];

/** Recharts' axis/scale computation was unreliable in this environment (axes
 * silently failed to render, degrading lines to a straight diagonal), so this
 * chart is drawn with plain SVG instead of pulling in a charting library. */
export function PriceHistoryChart({
  history,
  forecast,
}: {
  history: PriceObservation[];
  forecast?: ForecastResponse;
}) {
  const [range, setRange] = useState<TimeRange>("ALL");
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const filteredHistory = useMemo(() => {
    if (range === "ALL" || history.length === 0) return history;
    const lastDate = new Date(history[history.length - 1].date);
    const cutoff = new Date(lastDate);

    if (range === "3M") {
      cutoff.setMonth(cutoff.getMonth() - 3);
    } else if (range === "6M") {
      cutoff.setMonth(cutoff.getMonth() - 6);
    } else if (range === "1Y") {
      cutoff.setFullYear(cutoff.getFullYear() - 1);
    } else if (range === "3Y") {
      cutoff.setFullYear(cutoff.getFullYear() - 3);
    }

    const res = history.filter((h) => new Date(h.date) >= cutoff);
    return res.length >= 2 ? res : history.slice(-3);
  }, [history, range]);

  if (history.length === 0) {
    return (
      <Card title="Price history & forecast">
        <p className="text-sm text-slate-400">No price history available.</p>
      </Card>
    );
  }

  const hasForecast = !!forecast && !isInsufficientData(forecast);
  const points = filteredHistory.map((h) => ({ date: h.date, price: h.price }));
  const forecastPoint = hasForecast
    ? { date: forecast!.target_date, price: forecast!.point_forecast }
    : null;

  const allValues = points.map((p) => p.price).concat(
    hasForecast ? [forecast!.lower_bound, forecast!.upper_bound, forecast!.point_forecast] : []
  );
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const valuePad = (maxValue - minValue) * 0.1 || Math.abs(maxValue) * 0.05 || 1;
  const yMin = minValue - valuePad;
  const yMax = maxValue + valuePad;

  const totalPoints = points.length + (forecastPoint ? 1 : 0);
  const innerWidth = WIDTH - PADDING.left - PADDING.right;
  const innerHeight = HEIGHT - PADDING.top - PADDING.bottom;

  const xForIndex = (i: number) =>
    PADDING.left + (totalPoints <= 1 ? 0 : (i / (totalPoints - 1)) * innerWidth);
  const yForValue = (v: number) =>
    PADDING.top + innerHeight - ((v - yMin) / (yMax - yMin || 1)) * innerHeight;

  const priceLinePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${xForIndex(i)},${yForValue(p.price)}`)
    .join(" ");

  const forecastLinePath = forecastPoint
    ? `M${xForIndex(points.length - 1)},${yForValue(points[points.length - 1].price)} L${xForIndex(
        points.length
      )},${yForValue(forecastPoint.price)}`
    : null;

  const rangeX = forecastPoint ? xForIndex(points.length) : 0;

  const yTicks = 4;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) => yMin + ((yMax - yMin) * i) / yTicks);

  // show a handful of evenly-spaced date labels rather than every point
  const xLabelCount = Math.min(6, totalPoints);
  const xLabelIndices = Array.from({ length: xLabelCount }, (_, i) =>
    Math.round((i / (xLabelCount - 1 || 1)) * (totalPoints - 1))
  );
  const allDates = points.map((p) => p.date).concat(forecastPoint ? [forecastPoint.date] : []);

  const hovered =
    hoverIndex != null && hoverIndex < allDates.length
      ? {
          date: allDates[hoverIndex],
          value: hoverIndex < points.length ? points[hoverIndex].price : forecastPoint?.price,
        }
      : null;

  return (
    <Card>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <h3 className="text-sm font-semibold text-slate-700">Price history & forecast</h3>
        <div className="flex items-center gap-1 rounded-md bg-slate-100 p-0.5">
          {RANGES.map((r) => (
            <button
              key={r.value}
              type="button"
              onClick={() => {
                setRange(r.value);
                setHoverIndex(null);
              }}
              className={`rounded px-2.5 py-1 text-[11px] font-medium transition-colors ${
                range === r.value
                  ? "bg-white text-slate-900 shadow-sm font-semibold"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      <div className="relative w-full overflow-x-auto">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" style={{ minWidth: 480 }}>
          {yTickValues.map((v, i) => (
            <g key={i}>
              <line
                x1={PADDING.left}
                x2={WIDTH - PADDING.right}
                y1={yForValue(v)}
                y2={yForValue(v)}
                stroke="#e2e8f0"
                strokeDasharray="3 3"
              />
              <text
                x={PADDING.left - 8}
                y={yForValue(v)}
                textAnchor="end"
                dominantBaseline="middle"
                fontSize={10}
                fill="#94a3b8"
              >
                {v.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </text>
            </g>
          ))}

          {hasForecast && forecastPoint && (
            <rect
              x={rangeX - 3}
              y={yForValue(forecast!.upper_bound)}
              width={6}
              height={Math.max(2, yForValue(forecast!.lower_bound) - yForValue(forecast!.upper_bound))}
              fill="#94a3b8"
              fillOpacity={0.4}
            />
          )}

          <path d={priceLinePath} fill="none" stroke="#334155" strokeWidth={2} />
          {forecastLinePath && (
            <path d={forecastLinePath} fill="none" stroke="#dc2626" strokeWidth={2} strokeDasharray="6 4" />
          )}
          {forecastPoint && (
            <circle cx={xForIndex(points.length)} cy={yForValue(forecastPoint.price)} r={3.5} fill="#dc2626" />
          )}

          {xLabelIndices.map((i) => (
            <text key={i} x={xForIndex(i)} y={HEIGHT - 6} textAnchor="middle" fontSize={10} fill="#94a3b8">
              {new Date(allDates[i]).toLocaleDateString(undefined, { month: "short", year: "2-digit" })}
            </text>
          ))}

          {Array.from({ length: totalPoints }, (_, i) => (
            <rect
              key={i}
              x={xForIndex(i) - innerWidth / (2 * (totalPoints - 1 || 1))}
              y={PADDING.top}
              width={innerWidth / (totalPoints - 1 || 1)}
              height={innerHeight}
              fill="transparent"
              onMouseEnter={() => setHoverIndex(i)}
              onMouseLeave={() => setHoverIndex(null)}
            />
          ))}
          {hoverIndex != null && (
            <line
              x1={xForIndex(hoverIndex)}
              x2={xForIndex(hoverIndex)}
              y1={PADDING.top}
              y2={HEIGHT - PADDING.bottom}
              stroke="#cbd5e1"
            />
          )}
        </svg>
        {hovered && (
          <div className="pointer-events-none absolute right-2 top-0 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs shadow-sm">
            <p className="font-medium text-slate-700">{new Date(hovered.date).toLocaleDateString()}</p>
            <p className="text-slate-500">
              {hovered.value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </p>
          </div>
        )}
      </div>
      <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-slate-700" /> Actual price
        </span>
        {hasForecast && (
          <>
            <span className="flex items-center gap-1.5">
              <span className="h-0.5 w-4 border-t-2 border-dashed border-red-600" /> Forecast
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 bg-slate-400 opacity-40" /> Forecast range
            </span>
          </>
        )}
      </div>
    </Card>
  );
}
