export function NotAvailableCard({ title, phase }: { title: string; phase: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-5">
      <h3 className="mb-1 text-sm font-semibold text-slate-500">{title}</h3>
      <p className="text-sm text-slate-400">Coming in {phase}.</p>
    </div>
  );
}
