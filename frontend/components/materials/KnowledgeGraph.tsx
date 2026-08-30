"use client";

import { useMemo, useState } from "react";
import type { ComponentDriver, MaterialComponent } from "@/lib/types";
import { Card } from "@/components/common/Card";

const WIDTH = 960;
const ROW_MATERIAL_Y = 40;
const ROW_COMPONENT_Y = 170;
const ROW_DRIVER_Y = 320;
const PADDING_X = 90;
const NODE_W_COMPONENT = 148;
const NODE_H = 44;
const NODE_W_DRIVER = 136;

interface UniqueDriver {
  id: number;
  name: string;
  category: string;
  maxStrength: number;
  edges: { componentId: number; strength: number }[];
}

/** Blue for components (shaded by cost share), amber/red for drivers (shaded by
 * knowledge-graph relationship strength — the weight the driver model assigns them). */
function componentFill(pctOfCost: number): string {
  const t = Math.max(0, Math.min(1, pctOfCost / 100));
  return `hsl(217, 72%, ${88 - t * 48}%)`;
}
function driverFill(strength: number): string {
  const t = Math.max(0, Math.min(1, strength));
  return `hsl(14, 82%, ${88 - t * 50}%)`;
}
function textColorFor(lightness: number): string {
  return lightness > 60 ? "#1e293b" : "#ffffff";
}
function truncate(label: string, max: number): string {
  return label.length > max ? `${label.slice(0, max - 1)}…` : label;
}

export function KnowledgeGraph({
  materialName,
  components,
  drivers,
}: {
  materialName: string;
  components: MaterialComponent[];
  drivers: ComponentDriver[];
}) {
  const [hovered, setHovered] = useState<{ type: "component" | "driver"; id: number } | null>(null);

  const layout = useMemo(() => {
    const innerWidth = WIDTH - PADDING_X * 2;
    const compCount = Math.max(components.length, 1);
    const compX = new Map<number, number>();
    components.forEach((c, i) => {
      compX.set(c.id, PADDING_X + ((i + 0.5) / compCount) * innerWidth);
    });

    const uniqueByDriver = new Map<number, UniqueDriver>();
    for (const edge of drivers) {
      let ud = uniqueByDriver.get(edge.driver_id);
      if (!ud) {
        ud = { id: edge.driver_id, name: edge.driver_name, category: edge.driver_category, maxStrength: 0, edges: [] };
        uniqueByDriver.set(edge.driver_id, ud);
      }
      ud.edges.push({ componentId: edge.component_id, strength: edge.relationship_strength });
      ud.maxStrength = Math.max(ud.maxStrength, edge.relationship_strength);
    }

    const uniqueDrivers = Array.from(uniqueByDriver.values()).sort((a, b) => {
      const avg = (ud: UniqueDriver) =>
        ud.edges.reduce((sum, e) => sum + (compX.get(e.componentId) ?? WIDTH / 2), 0) / ud.edges.length;
      return avg(a) - avg(b);
    });

    const driverCount = Math.max(uniqueDrivers.length, 1);
    const driverX = new Map<number, number>();
    uniqueDrivers.forEach((d, i) => {
      driverX.set(d.id, PADDING_X + ((i + 0.5) / driverCount) * innerWidth);
    });

    return { compX, uniqueDrivers, driverX };
  }, [components, drivers]);

  if (components.length === 0) {
    return (
      <Card title="Material knowledge graph">
        <p className="text-sm text-slate-400">No composition data available.</p>
      </Card>
    );
  }

  const materialX = WIDTH / 2;

  const isComponentDimmed = (id: number) =>
    hovered != null &&
    !(
      (hovered.type === "component" && hovered.id === id) ||
      (hovered.type === "driver" &&
        layout.uniqueDrivers.find((d) => d.id === hovered.id)?.edges.some((e) => e.componentId === id))
    );
  const isDriverDimmed = (ud: UniqueDriver) =>
    hovered != null &&
    !(
      (hovered.type === "driver" && hovered.id === ud.id) ||
      (hovered.type === "component" && ud.edges.some((e) => e.componentId === hovered.id))
    );
  const isEdgeDimmed = (componentId: number, driverId: number) =>
    hovered != null &&
    !(
      (hovered.type === "component" && hovered.id === componentId) ||
      (hovered.type === "driver" && hovered.id === driverId)
    );

  return (
    <Card title="Material knowledge graph">
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${WIDTH} ${ROW_DRIVER_Y + NODE_H + 30}`} className="w-full" style={{ minWidth: 640 }}>
          {/* material -> component edges */}
          {components.map((c) => (
            <line
              key={`mc-${c.id}`}
              x1={materialX}
              y1={ROW_MATERIAL_Y + NODE_H / 2}
              x2={layout.compX.get(c.id)}
              y2={ROW_COMPONENT_Y - NODE_H / 2}
              stroke="#94a3b8"
              strokeWidth={2}
              opacity={isComponentDimmed(c.id) ? 0.15 : 0.7}
            />
          ))}

          {/* component -> driver edges */}
          {layout.uniqueDrivers.flatMap((ud) =>
            ud.edges.map((e) => (
              <line
                key={`cd-${e.componentId}-${ud.id}`}
                x1={layout.compX.get(e.componentId)}
                y1={ROW_COMPONENT_Y + NODE_H / 2}
                x2={layout.driverX.get(ud.id)}
                y2={ROW_DRIVER_Y - NODE_H / 2}
                stroke="#cbd5e1"
                strokeWidth={1 + e.strength * 3}
                opacity={isEdgeDimmed(e.componentId, ud.id) ? 0.1 : 0.8}
              />
            ))
          )}

          {/* material node */}
          <g>
            <rect
              x={materialX - NODE_W_COMPONENT / 2}
              y={ROW_MATERIAL_Y}
              width={NODE_W_COMPONENT}
              height={NODE_H}
              rx={10}
              fill="#0f172a"
            />
            <text x={materialX} y={ROW_MATERIAL_Y + NODE_H / 2} textAnchor="middle" dominantBaseline="middle" fontSize={13} fontWeight={600} fill="#ffffff">
              {truncate(materialName, 20)}
            </text>
            <title>{materialName}</title>
          </g>

          {/* component nodes */}
          {components.map((c) => {
            const x = layout.compX.get(c.id)!;
            const fill = componentFill(c.percentage_of_cost);
            const dimmed = isComponentDimmed(c.id);
            return (
              <g
                key={c.id}
                onMouseEnter={() => setHovered({ type: "component", id: c.id })}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor: "pointer" }}
                opacity={dimmed ? 0.35 : 1}
              >
                <rect
                  x={x - NODE_W_COMPONENT / 2}
                  y={ROW_COMPONENT_Y - NODE_H / 2}
                  width={NODE_W_COMPONENT}
                  height={NODE_H}
                  rx={10}
                  fill={fill}
                  stroke="#1e293b"
                  strokeOpacity={0.15}
                />
                <text
                  x={x}
                  y={ROW_COMPONENT_Y - 4}
                  textAnchor="middle"
                  fontSize={12}
                  fontWeight={600}
                  fill={textColorFor(88 - Math.min(1, c.percentage_of_cost / 100) * 48)}
                >
                  {truncate(c.component_name, 18)}
                </text>
                <text
                  x={x}
                  y={ROW_COMPONENT_Y + 13}
                  textAnchor="middle"
                  fontSize={11}
                  fill={textColorFor(88 - Math.min(1, c.percentage_of_cost / 100) * 48)}
                  opacity={0.9}
                >
                  {c.percentage_of_cost}% of cost
                </text>
                <title>{c.component_name}: {c.percentage_of_cost}% of material cost</title>
              </g>
            );
          })}

          {/* driver nodes */}
          {layout.uniqueDrivers.map((ud) => {
            const x = layout.driverX.get(ud.id)!;
            const fill = driverFill(ud.maxStrength);
            const dimmed = isDriverDimmed(ud);
            return (
              <g
                key={ud.id}
                onMouseEnter={() => setHovered({ type: "driver", id: ud.id })}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor: "pointer" }}
                opacity={dimmed ? 0.35 : 1}
              >
                <rect
                  x={x - NODE_W_DRIVER / 2}
                  y={ROW_DRIVER_Y - NODE_H / 2}
                  width={NODE_W_DRIVER}
                  height={NODE_H}
                  rx={10}
                  fill={fill}
                  stroke="#1e293b"
                  strokeOpacity={0.15}
                />
                <text
                  x={x}
                  y={ROW_DRIVER_Y - 4}
                  textAnchor="middle"
                  fontSize={11.5}
                  fontWeight={600}
                  fill={textColorFor(88 - ud.maxStrength * 50)}
                >
                  {truncate(ud.name, 17)}
                </text>
                <text
                  x={x}
                  y={ROW_DRIVER_Y + 13}
                  textAnchor="middle"
                  fontSize={10.5}
                  fill={textColorFor(88 - ud.maxStrength * 50)}
                  opacity={0.9}
                >
                  strength {(ud.maxStrength * 100).toFixed(0)}%
                </text>
                <title>{ud.name} ({ud.category}): relationship strength up to {(ud.maxStrength * 100).toFixed(0)}%</title>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-500">
        <span className="flex items-center gap-2">
          <span className="flex h-3 w-8 rounded" style={{ background: "linear-gradient(to right, hsl(217,72%,88%), hsl(217,72%,40%))" }} />
          Component shade = share of material cost
        </span>
        <span className="flex items-center gap-2">
          <span className="flex h-3 w-8 rounded" style={{ background: "linear-gradient(to right, hsl(14,82%,88%), hsl(14,82%,38%))" }} />
          Driver shade = knowledge-graph relationship strength
        </span>
        <span>Hover a node to trace its connections.</span>
      </div>
    </Card>
  );
}
