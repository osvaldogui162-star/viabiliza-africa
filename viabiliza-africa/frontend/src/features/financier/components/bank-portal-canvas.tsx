"use client";

import { cn } from "@/lib/utils/cn";
import { BankPortalRail } from "@/features/financier/components/bank-portal-rail";

export function BankPortalCanvas({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className="bank-portal-fin-body bank-portal-fin-stage">
      <div className="bank-portal-fin-frame">
        <div className="bank-portal-rail-slot hidden lg:block">
          <BankPortalRail />
        </div>
        <div className={cn("bank-portal-fin-main min-w-0 flex-1", className)}>{children}</div>
      </div>
    </div>
  );
}
