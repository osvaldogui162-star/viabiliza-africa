"use client";

import { cn } from "@/lib/utils/cn";

function Bone({ className }: { className?: string }) {
  return <div className={cn("va-skeleton rounded-md", className)} />;
}

export function DashboardSkeleton() {
  return (
    <div className="mx-auto max-w-[1160px] space-y-4 pb-6" aria-busy="true" aria-label="A carregar dashboard">
      {/* Hero + KPIs unificados */}
      <div className="relative overflow-visible rounded-2xl pb-1 shadow-lg">
        <div className="absolute inset-0 overflow-hidden rounded-2xl bg-[#071612]" />
        <div className="relative space-y-2 px-6 pb-[4.25rem] pt-5">
          <div className="flex gap-2">
            <Bone className="h-4 w-20 bg-white/10" />
            <Bone className="h-4 w-12 bg-white/10" />
          </div>
          <Bone className="h-7 w-48 bg-white/10" />
        </div>
        <div className="relative -mt-10 grid grid-cols-2 gap-2.5 px-3 sm:-mt-11 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className={cn("rounded-xl p-3.5 shadow-md sm:p-3.5", `va-kpi-card va-kpi-card--${i}`)}>
              <Bone className="h-8 w-8 rounded-lg bg-white/10" />
              <Bone className="mt-2.5 h-5 w-16 bg-white/15" />
              <Bone className="mt-1.5 h-3 w-24 bg-white/10" />
              <Bone className="mt-2.5 h-6 w-[68px] bg-white/10" />
            </div>
          ))}
        </div>
      </div>

      {/* Chart + sidebar */}
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_280px]">
        <div className="va-glass-card space-y-3 p-4">
          <div className="flex justify-between gap-2">
            <div className="space-y-2">
              <Bone className="h-3 w-32" />
              <Bone className="h-7 w-28" />
              <Bone className="h-3 w-48" />
            </div>
            <Bone className="h-8 w-40 rounded-md" />
          </div>
          <Bone className="h-8 w-full max-w-xs rounded-md" />
          <Bone className="h-[220px] w-full rounded-lg" />
        </div>

        <div className="space-y-4">
          <div className="va-glass-card space-y-3 p-4">
            <div className="flex justify-between">
              <div className="space-y-2">
                <Bone className="h-3 w-20" />
                <Bone className="h-5 w-24" />
              </div>
              <Bone className="h-[72px] w-[72px] rounded-full" />
            </div>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between">
                  <Bone className="h-3 w-20" />
                  <Bone className="h-3 w-10" />
                </div>
                <Bone className="h-1.5 w-full rounded-full" />
              </div>
            ))}
            <Bone className="h-9 w-full rounded-lg" />
          </div>

          <div className="va-glass-card space-y-2 p-4">
            <Bone className="h-4 w-32" />
            {Array.from({ length: 3 }).map((_, i) => (
              <Bone key={i} className="h-14 w-full rounded-md" />
            ))}
          </div>
        </div>
      </div>

      {/* Recent projects */}
      <div className="va-glass-card overflow-hidden">
        <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
          <div className="space-y-1.5">
            <Bone className="h-4 w-32" />
            <Bone className="h-3 w-48" />
          </div>
          <div className="flex gap-2">
            <Bone className="h-8 w-20 rounded-lg" />
            <Bone className="h-8 w-20 rounded-lg" />
          </div>
        </div>
        <div className="grid gap-2.5 p-3 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-lg border border-[var(--border)] p-3">
              <div className="flex justify-between gap-2">
                <div className="flex-1 space-y-1.5">
                  <Bone className="h-4 w-full max-w-[75%]" />
                  <Bone className="h-3 w-full max-w-[50%]" />
                </div>
                <Bone className="h-5 w-14 rounded-full" />
              </div>
              <Bone className="mt-3 h-5 w-24" />
              <div className="mt-3 flex gap-3">
                <Bone className="h-3 w-16" />
                <Bone className="h-3 w-16" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
