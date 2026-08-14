const styles: Record<string, string> = {
  LOW: "bg-green-100 text-green-800",
  MEDIUM: "bg-amber-100 text-amber-800",
  HIGH: "bg-red-100 text-red-800",
  CRITICAL: "bg-red-200 text-red-900",
};

export function Badge({ label, tone = "MEDIUM" }: { label: string; tone?: string }) {
  const style = styles[tone] ?? "bg-slate-100 text-slate-700";
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}
