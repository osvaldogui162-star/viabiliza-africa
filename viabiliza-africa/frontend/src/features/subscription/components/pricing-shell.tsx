import type { ReactNode } from "react";

import { MarketingHeader } from "@/features/marketing/components/marketing-header";

export function PricingShell({ children }: { children: ReactNode; isAuthenticated?: boolean }) {
  return (
    <div className="landing-page pricing-page min-h-screen bg-[#f8faf9] font-[family-name:var(--font-inter)] text-zinc-900">
      <MarketingHeader />
      <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 sm:py-10">{children}</main>
    </div>
  );
}
