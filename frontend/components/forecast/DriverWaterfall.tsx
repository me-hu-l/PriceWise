"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ForecastExplanationResponse } from "@/lib/types";
import { Card } from "@/components/common/Card";
import { isInsufficientData } from "./ForecastCard";

export function DriverWaterfall({ explanation }: { explanation: ForecastExplanationResponse }) {
  if (isInsufficientData(explanation)) {
    return (
      <Card title="Why is price moving?">
        <p className="text-sm text-slate-400">{explanation.reason}</p>
      </Card>
    );
  }

  const data = explanation.waterfall.map((row) => ({
    label: row.label,
    pct: row.contribution_value * 100,
  }));

  return (
    <Card title="Why is price moving?">
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" tick={{ fontSize: 11 }} unit="%" />
            <YAxis type="category" dataKey="label" tick={{ fontSize: 11 }} width={140} />
            <Tooltip formatter={(v: number) => `${v.toFixed(1)}%`} />
            <Bar dataKey="pct">
              {data.map((row, i) => (
                <Cell key={i} fill={row.pct >= 0 ? "#dc2626" : "#16a34a"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-3 text-sm text-slate-600">{explanation.narrative}</p>
    </Card>
  );
}
