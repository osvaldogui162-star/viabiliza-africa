import type { DisplayCurrency } from "@/lib/currency";
import { parseInvestmentToDisplay } from "@/lib/currency/format-display";
import type { Project } from "@/lib/types/project";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

export type DashboardAlert = {
  id: string;
  tone: "info" | "warning" | "success" | "danger";
  title: string;
  message: string;
  href?: string;
  actionLabel?: string;
};

export type MonthlyPoint = {
  label: string;
  projects: number;
  investment: number;
};

export type SectorSlice = {
  label: string;
  count: number;
  pct: number;
};

export type DashboardMetrics = {
  totalProjects: number;
  activeProjects: number;
  draftProjects: number;
  sharedProjects: number;
  totalInvestment: number;
  displayCurrency: DisplayCurrency;
  approvedBudgets: number;
  monthlyTrend: MonthlyPoint[];
  sectorBreakdown: SectorSlice[];
  planUsagePct: number | null;
  investmentGrowthPct: number | null;
  projectsGrowthPct: number | null;
  budgetApprovalRate: number;
};

function monthKey(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function monthLabel(key: string, locale: string) {
  const [year, month] = key.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString(locale, {
    month: "short",
  });
}

export function buildDashboardMetrics(
  projects: Project[],
  subscription: MySubscriptionResponse | null,
  locale: string,
  displayCurrency: DisplayCurrency,
): DashboardMetrics {
  const toDisplay = (value: string, currency: string) =>
    parseInvestmentToDisplay(value, currency, displayCurrency);

  const totalInvestment = projects.reduce(
    (sum, p) => sum + toDisplay(p.investment_amount, p.currency),
    0,
  );

  const now = new Date();
  const months: string[] = [];
  for (let i = 5; i >= 0; i -= 1) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(monthKey(d));
  }

  const monthlyTrend = months.map((key) => {
    const inMonth = projects.filter((p) => monthKey(new Date(p.created_at)) === key);
    return {
      label: monthLabel(key, locale),
      projects: inMonth.length,
      investment: inMonth.reduce((sum, p) => sum + toDisplay(p.investment_amount, p.currency), 0),
    };
  });

  const sectorMap = new Map<string, number>();
  for (const project of projects) {
    const label = project.sector_label || project.sector;
    sectorMap.set(label, (sectorMap.get(label) ?? 0) + 1);
  }
  const total = projects.length || 1;
  const sectorBreakdown = [...sectorMap.entries()]
    .map(([label, count]) => ({
      label,
      count,
      pct: Math.round((count / total) * 100),
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const limit = subscription?.usage.projects_limit ?? subscription?.capabilities.projects_limit;
  const used = subscription?.usage.projects_count ?? projects.length;
  const planUsagePct = limit != null ? Math.min(100, Math.round((used / limit) * 100)) : null;

  const lastMonth = monthlyTrend[monthlyTrend.length - 1];
  const prevMonth = monthlyTrend[monthlyTrend.length - 2];
  const investmentGrowthPct =
    prevMonth && prevMonth.investment > 0
      ? Math.round(((lastMonth.investment - prevMonth.investment) / prevMonth.investment) * 100)
      : lastMonth.investment > 0
        ? 100
        : null;
  const projectsGrowthPct =
    prevMonth && prevMonth.projects > 0
      ? Math.round(((lastMonth.projects - prevMonth.projects) / prevMonth.projects) * 100)
      : lastMonth.projects > 0
        ? 100
        : null;
  const budgetApprovalRate =
    projects.length > 0 ? Math.round((projects.filter((p) => p.has_approved_budget).length / projects.length) * 100) : 0;

  return {
    totalProjects: projects.length,
    activeProjects: projects.filter((p) => p.status === "active").length,
    draftProjects: projects.filter((p) => p.status === "draft").length,
    sharedProjects: projects.filter((p) => p.is_shared).length,
    totalInvestment,
    displayCurrency,
    approvedBudgets: projects.filter((p) => p.has_approved_budget).length,
    monthlyTrend,
    sectorBreakdown,
    planUsagePct,
    investmentGrowthPct,
    projectsGrowthPct,
    budgetApprovalRate,
  };
}

export function buildDashboardAlerts(
  projects: Project[],
  subscription: MySubscriptionResponse | null,
  canCreate: boolean,
  t: (key: string, params?: Record<string, string | number>) => string,
): DashboardAlert[] {
  const alerts: DashboardAlert[] = [];
  const usage = subscription?.usage;
  const limit = usage?.projects_limit ?? subscription?.capabilities.projects_limit;
  const used = usage?.projects_count ?? projects.length;
  const planName = subscription?.plan.name ?? t("onboarding.freePlan");
  const isFree = subscription?.plan.code === "free" || subscription?.is_implicit_free;

  if (canCreate && projects.length === 0) {
    alerts.push({
      id: "no-projects",
      tone: "info",
      title: t("dashboard.alerts.noProjectsTitle"),
      message: t("dashboard.alerts.noProjectsMessage"),
      href: "/projects/new",
      actionLabel: t("dashboard.createProject"),
    });
  }

  if (limit != null) {
    const remaining = limit - used;
    if (remaining <= 0) {
      alerts.push({
        id: "plan-full",
        tone: "danger",
        title: t("dashboard.alerts.planFullTitle"),
        message: t("dashboard.alerts.planFullMessage", { plan: planName, limit }),
        href: "/planos",
        actionLabel: t("onboarding.upgradePlan"),
      });
    } else if (used / limit >= 0.85) {
      alerts.push({
        id: "plan-near",
        tone: "warning",
        title: t("dashboard.alerts.planNearTitle"),
        message: t("dashboard.alerts.planNearMessage", { used, limit }),
        href: "/planos",
        actionLabel: t("onboarding.upgradePlan"),
      });
    }
  }

  const drafts = projects.filter((p) => p.status === "draft" && p.is_owner);
  if (drafts.length > 0) {
    alerts.push({
      id: "drafts",
      tone: "warning",
      title: t("dashboard.alerts.draftsTitle", { count: drafts.length }),
      message: t("dashboard.alerts.draftsMessage"),
      href: `/projects/${drafts[0].id}`,
      actionLabel: t("dashboard.alerts.continueProject"),
    });
  }

  const noBudget = projects.filter((p) => p.is_owner && !p.has_approved_budget && p.status !== "draft");
  if (noBudget.length > 0) {
    alerts.push({
      id: "no-budget",
      tone: "info",
      title: t("dashboard.alerts.noBudgetTitle", { count: noBudget.length }),
      message: t("dashboard.alerts.noBudgetMessage"),
      href: `/projects/${noBudget[0].id}?tab=ingestion`,
      actionLabel: t("dashboard.alerts.openIngestion"),
    });
  }

  if (isFree && canCreate && projects.length > 0) {
    alerts.push({
      id: "upgrade",
      tone: "success",
      title: t("dashboard.alerts.upgradeTitle"),
      message: t("dashboard.alerts.upgradeMessage"),
      href: "/planos",
      actionLabel: t("onboarding.upgradePlan"),
    });
  }

  const endsAt = subscription?.subscription?.ends_at;
  if (endsAt) {
    const daysLeft = Math.ceil((new Date(endsAt).getTime() - Date.now()) / 86400000);
    if (daysLeft > 0 && daysLeft <= 14) {
      alerts.push({
        id: "renewal",
        tone: "warning",
        title: t("dashboard.alerts.renewalTitle"),
        message: t("dashboard.alerts.renewalMessage", { days: daysLeft }),
        href: "/conta/assinatura",
        actionLabel: t("dashboard.alerts.manageSubscription"),
      });
    }
  }

  const scrapingLimit = usage?.scraping_items_limit;
  const scrapingUsed = usage?.scraping_items_this_month ?? 0;
  if (scrapingLimit != null && scrapingLimit > 0 && scrapingUsed / scrapingLimit >= 0.9) {
    alerts.push({
      id: "scraping",
      tone: "warning",
      title: t("dashboard.alerts.scrapingTitle"),
      message: t("dashboard.alerts.scrapingMessage", { used: scrapingUsed, limit: scrapingLimit }),
      href: "/planos",
      actionLabel: t("onboarding.upgradePlan"),
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      id: "all-good",
      tone: "success",
      title: t("dashboard.alerts.allGoodTitle"),
      message: t("dashboard.alerts.allGoodMessage"),
    });
  }

  return alerts.slice(0, 5);
}

/** @deprecated Use formatCompactMoney from useI18n() */
export function formatCompactUsd(value: number, locale: string) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
