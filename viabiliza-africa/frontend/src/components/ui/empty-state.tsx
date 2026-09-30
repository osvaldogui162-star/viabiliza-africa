import { Inbox } from "lucide-react";

import { cn } from "@/lib/utils/cn";

export function EmptyState({
  title,
  description,
  action,
  compact,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-200 bg-gradient-to-b from-zinc-50/80 to-white text-center",
        compact ? "px-4 py-8" : "px-6 py-12",
      )}
    >
      <Inbox className={cn("text-zinc-300", compact ? "mb-2 h-8 w-8" : "mb-3 h-10 w-10")} />
      <h3 className="font-semibold text-zinc-800">{title}</h3>
      {description ? (
        <p className="mt-1 max-w-sm text-sm leading-relaxed text-zinc-500">{description}</p>
      ) : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
