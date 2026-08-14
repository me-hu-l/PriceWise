import { Badge } from "./Badge";

/** Maps a criticality/risk level to a consistent red/yellow/green indicator (roadmap section 35). */
export function RiskIndicator({ level }: { level: string }) {
  return <Badge label={level} tone={level} />;
}
