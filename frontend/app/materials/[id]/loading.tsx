import { Card } from "@/components/common/Card";

function Skeleton({ className }: { className: string }) {
  return <div className={`animate-pulse rounded bg-slate-200 ${className}`} />;
}

export default function Loading() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading material forecast">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-8 w-20 rounded-full" />
      </div>

      <Card title="Material knowledge graph">
        <Skeleton className="h-56 w-full" />
      </Card>

      <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(220px,0.42fr)]">
        <Card title="Price history & forecast">
          <Skeleton className="h-64 w-full" />
        </Card>
        <Card title="Forecast">
          <div className="space-y-4">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-4 w-44" />
            <Skeleton className="h-4 w-28" />
          </div>
        </Card>
      </div>

      <Card title="Driver history & next projection">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Skeleton className="h-44 w-full" />
          <Skeleton className="h-44 w-full" />
        </div>
      </Card>

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
        <Card title="Forecast confidence score">
          <Skeleton className="h-36 w-full" />
        </Card>
        <Card title="Why is price moving?">
          <Skeleton className="h-36 w-full" />
        </Card>
      </div>
    </div>
  );
}
