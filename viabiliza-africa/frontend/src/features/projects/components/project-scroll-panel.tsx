"use client";

import { forwardRef, type ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export const ProjectScrollPanel = forwardRef<
  HTMLDivElement,
  {
    children: ReactNode;
    className?: string;
    maxHeight?: string;
  }
>(function ProjectScrollPanel({ children, className, maxHeight = "max-h-[min(52vh,520px)]" }, ref) {
  return (
    <div
      ref={ref}
      className={cn(
        "va-scroll-panel overflow-auto rounded-xl border border-zinc-100 bg-white",
        maxHeight,
        className,
      )}
    >
      {children}
    </div>
  );
});
