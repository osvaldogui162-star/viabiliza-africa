"use client";

import { Skeleton } from "@/components/ui/skeleton";

export function ProjectsSkeleton() {
  return (
    <div className="space-y-4" aria-busy="true">
      <div className="va-glass-card flex flex-wrap gap-3 p-4">
        <Skeleton className="h-10 w-full max-w-md flex-1" />
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-10 w-24" />
      </div>
      <Skeleton className="h-4 w-48" />
      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        <Skeleton className="h-10 w-full rounded-none" />
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex gap-3 border-t border-zinc-100 px-4 py-3">
            <Skeleton className="h-4 w-4 shrink-0" />
            <Skeleton className="h-4 w-48" />
            <Skeleton className="h-4 w-24 hidden md:block" />
            <Skeleton className="h-4 w-20 ml-auto" />
          </div>
        ))}
        <Skeleton className="h-12 w-full rounded-none" />
      </div>
    </div>
  );
}
