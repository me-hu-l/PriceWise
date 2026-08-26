"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { PriceUploadResult } from "@/lib/types";

export function PriceHistoryUpload({ materialId }: { materialId: number }) {
  const [result, setResult] = useState<PriceUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  async function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setResult(null);
    setUploading(true);
    try {
      setResult(await api.uploadHistory(materialId, file));
      window.location.reload();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload failed.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-800">Use custom price history</h3>
          <p className="text-xs text-slate-500">Uploads are kept separate from the preloaded database history.</p>
        </div>
        <label className="cursor-pointer rounded-md bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-700">
          {uploading ? "Uploading..." : "Upload CSV"}
          <input type="file" accept=".csv,text/csv" onChange={handleChange} disabled={uploading} className="sr-only" />
        </label>
      </div>
      <p className="mt-2 text-xs text-slate-500">
        Required columns: <span className="font-medium">date, price</span>. Optional: currency, unit. Minimum 3 unique dates.
      </p>
      <a href="/sample_ceria_cmp_slurry_price_history.csv" download className="mt-2 inline-block text-xs font-medium text-teal-700 underline underline-offset-2">
        Download Ceria CMP Slurry sample CSV
      </a>
      {result && <p className="mt-2 text-xs text-emerald-700">{result.message} {result.observation_count} observations loaded.</p>}
      {error && <p className="mt-2 text-xs text-red-700">{error}</p>}
    </section>
  );
}