"use client";

import { useAuth } from "@/components/providers/auth-provider";
import { FinancierDashboardView } from "@/features/financier/components/financier-dashboard-view";
import { FinancierPortfolioView } from "@/features/financier/components/financier-portfolio-view";

export function FinancierHomePage() {
  const { user } = useAuth();
  if (user?.role === "bank") {
    return <FinancierDashboardView />;
  }
  return <FinancierPortfolioView />;
}
