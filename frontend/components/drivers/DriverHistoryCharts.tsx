"use client";

import type { MaterialDriverHistory } from "@/lib/types";
import { useState } from "react";
import { Card } from "@/components/common/Card";

const WIDTH = 760;
const HEIGHT = 190;
const PADDING = { top: 16, right: 18, bottom: 28, left: 52 };

export function DriverHistoryCharts({ histories }: { histories: MaterialDriverHistory[] }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <Card title="Driver history & next projection">
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="mb-3 text-xs font-medium text-slate-500 underline underline-offset-2"
      >
        {expanded ? "Roll up driver plots" : "Show driver plots"}
      </button>
      {!expanded ? null : histories.length === 0 ? (
        <p className="text-sm text-slate-400">No historical observations available for the involved drivers.</p>
      ) : (
        <div className="flex snap-x gap-4 overflow-x-auto pb-2">
          {histories.map((history) => {
            const values = history.observations.map((observation) => observation.value);
            if (values.length === 0) {
              return <p key={history.driver_id} className="text-sm text-slate-400">{history.driver_name}: no observations</p>;
            }
            const allValues = history.projected_value == null ? values : [...values, history.projected_value];
            const min = Math.min(...allValues);
            const max = Math.max(...allValues);
            const pad = (max - min) * 0.12 || Math.abs(max) * 0.05 || 1;
            const yMin = min - pad;
            const yMax = max + pad;
            const plotWidth = WIDTH - PADDING.left - PADDING.right;
            const plotHeight = HEIGHT - PADDING.top - PADDING.bottom;
            const total = values.length + (history.projected_value == null ? 0 : 1);
            const x = (index: number) => PADDING.left + (index / Math.max(total - 1, 1)) * plotWidth;
            const y = (value: number) => PADDING.top + plotHeight - ((value - yMin) / (yMax - yMin || 1)) * plotHeight;
            const path = values.map((value, index) => `${index === 0 ? "M" : "L"}${x(index)},${y(value)}`).join(" ");
            const latest = history.observations[history.observations.length - 1];
            return (
              <div
                key={history.driver_id}
                className="min-w-[280px] flex-none snap-start lg:min-w-0 lg:w-[calc((100%-1rem)/2)]"
              >
                <div className="mb-2 flex items-baseline justify-between gap-3">
                  <div>
                    <h4 className="text-sm font-semibold text-slate-800">{history.driver_name}</h4>
                    <p className="text-xs text-slate-500">Latest {latest.value.toLocaleString()} {history.unit ?? ""}</p>
                  </div>
                  {history.projected_value != null && (
                    <p className="text-right text-xs text-slate-600">
                      Projected {history.projected_value.toLocaleString(undefined, { maximumFractionDigits: 2 })} {history.unit ?? ""}
                    </p>
                  )}
                </div>
                <div className="overflow-x-auto">
                  <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" style={{ minWidth: 260 }}>
                    <line x1={PADDING.left} x2={WIDTH - PADDING.right} y1={HEIGHT - PADDING.bottom} y2={HEIGHT - PADDING.bottom} stroke="#e2e8f0" />
                    <path d={path} fill="none" stroke="#c2410c" strokeWidth={2.5} />
                    {values.map((value, index) => <circle key={index} cx={x(index)} cy={y(value)} r={2.5} fill="#c2410c" />)}
                    {history.projected_value != null && (
                      <>
                        <line x1={x(values.length - 1)} x2={x(values.length)} y1={y(values[values.length - 1])} y2={y(history.projected_value)} stroke="#0f766e" strokeWidth={2} strokeDasharray="5 4" />
                        <circle cx={x(values.length)} cy={y(history.projected_value)} r={4} fill="#0f766e" />
                        <text x={x(values.length)} y={HEIGHT - 8} textAnchor="middle" fontSize={10} fill="#0f766e">Projected</text>
                      </>
                    )}
                    <text x={PADDING.left - 8} y={PADDING.top} textAnchor="end" fontSize={10} fill="#94a3b8">{yMax.toLocaleString(undefined, { maximumFractionDigits: 0 })}</text>
                    <text x={PADDING.left - 8} y={HEIGHT - PADDING.bottom} textAnchor="end" fontSize={10} fill="#94a3b8">{yMin.toLocaleString(undefined, { maximumFractionDigits: 0 })}</text>
                  </svg>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
