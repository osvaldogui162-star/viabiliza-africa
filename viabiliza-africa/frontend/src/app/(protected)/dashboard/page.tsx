"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { DashboardAlertsPanel } from "@/features/dashboard/components/dashboard-alerts-panel";
import { DashboardHeroSection } from "@/features/dashboard/components/dashboard-hero-section";
import { DashboardInvestmentChart } from "@/features/dashboard/components/dashboard-investment-chart";
import { DashboardPlanWidget } from "@/features/dashboard/components/dashboard-plan-widget";
import { DashboardRecentProjects } from "@/features/dashboard/components/dashboard-recent-projects";
import { PageLoader } from "@/components/ui/spinner";
import { PlanLimitBanner } from "@/features/dashboard/components/plan-limit-banner";
import {
  buildDashboardAlerts,
  buildDashboardMetrics,
} from "@/features/dashboard/lib/dashboard-analytics";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi } from "@/lib/api/projects-api";
import { subscriptionApi } from "@/lib/api/subscription-api";
import type { Project } from "@/lib/types/project";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

export default function DashboardPage() {
  return (
    <Suspense fallback={<PageLoader layout="section" />}>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const { user } = useAuth();
  const { t, intlLocale, currency } = useI18n();
  const searchParams = useSearchParams();
  const isWelcome = searchParams.get("welcome") === "1";

  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [subscription, setSubscription] = useState<MySubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [revealed, setRevealed] = useState(false);

  const canCreate = user?.role === "admin" || user?.role === "financial";

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setRevealed(false);
      try {
        const [analyticsRes, subscriptionRes] = await Promise.all([
          projectsApi.list({ limit: 50 }),
          subscriptionApi.getMySubscription().catch(() => null),
        ]);
        if (cancelled) return;
        setAllProjects(analyticsRes.items);
        setRecentProjects(analyticsRes.items.slice(0, 6));
        setTotal(analyticsRes.total);
        setSubscription(subscriptionRes);
      } catch (error) {
        if (!cancelled) {
          toast.error(error instanceof ApiError ? error.message : t("dashboard.loadError"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [t]);

  useEffect(() => {
    if (!loading) {
      const tId = requestAnimationFrame(() => setRevealed(true));
      return () => cancelAnimationFrame(tId);
    }
    setRevealed(false);
    return undefined;
  }, [loading]);

  const metrics = useMemo(
    () => buildDashboardMetrics(allProjects, subscription, intlLocale, currency),
    [allProjects, subscription, intlLocale, currency],
  );

  const alerts = useMemo(
    () => buildDashboardAlerts(allProjects, subscription, canCreate, t),
    [allProjects, subscription, canCreate, t],
  );

  const planName = subscription?.plan.name ?? t("onboarding.freePlan");

  if (loading) {
    return <PageLoader message={t("common.loadingDashboard")} layout="section" />;
  }

  return (
    <div className={`mx-auto max-w-[1160px] space-y-4 pb-6 ${revealed ? "va-dashboard-ready" : ""}`}>
      <DashboardHeroSection
        userName={user?.full_name ?? ""}
        isWelcome={isWelcome || total === 0}
        canCreate={canCreate}
        planName={planName}
        projectsTotal={total}
        metrics={metrics}
        delay={0}
      />

      {subscription ? (
        <div className="va-dash-enter" style={{ animationDelay: "180ms" }}>
          <PlanLimitBanner subscription={subscription} />
        </div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_280px]">
        <DashboardInvestmentChart metrics={metrics} enterDelay={260} />
        <div className="space-y-4">
          <DashboardPlanWidget subscription={subscription} metricsPlanPct={metrics.planUsagePct} enterDelay={320} />
          <DashboardAlertsPanel alerts={alerts} enterDelay={380} />
        </div>
      </div>

      <DashboardRecentProjects
        projects={recentProjects}
        canCreate={canCreate}
        total={total}
        enterDelay={440}
      />
    </div>
  );
}
