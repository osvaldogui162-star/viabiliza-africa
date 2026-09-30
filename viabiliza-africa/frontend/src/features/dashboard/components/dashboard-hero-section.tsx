"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowUpRight, FolderKanban, Layers, Plus, Share2, Sparkles, TrendingDown, TrendingUp, Wallet } from "lucide-react";

import { DashboardActionButton } from "@/features/dashboard/components/dashboard-action-button";
import { Sparkline } from "@/features/dashboard/components/sparkline";
import { type DashboardMetrics } from "@/features/dashboard/lib/dashboard-analytics";
import { BRAND_SLIDE_IMAGES, DASHBOARD_HERO_SLIDE_INTERVAL_MS } from "@/lib/constants/brand-slides";
import { useI18n } from "@/components/providers/locale-provider";
import { useAnimatedNumber } from "@/hooks/use-animated-number";
import { useInView } from "@/hooks/use-in-view";
import { cn } from "@/lib/utils/cn";
import { spawnRipple } from "@/lib/utils/ripple";

type DashboardHeroSectionProps = {
  userName: string;
  isWelcome?: boolean;
  canCreate: boolean;
  planName: string;
  projectsTotal: number;
  metrics: DashboardMetrics;
  delay?: number;
};

function TrendChip({ value }: { value: number | null }) {
  if (value == null || value === 0) return null;
  const up = value > 0;
  const Icon = up ? TrendingUp : TrendingDown;
  return (
    <span
      className={cn(
        "va-badge-pop inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-[10px] font-semibold",
        up ? "bg-emerald-300/15 text-emerald-200" : "bg-rose-300/15 text-rose-200",
      )}
    >
      <Icon className="h-2.5 w-2.5" />
      {up ? "+" : ""}
      {value}%
    </span>
  );
}

function HeroSlideshow() {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setFade(false);
      window.setTimeout(() => {
        setIndex((prev) => (prev + 1) % BRAND_SLIDE_IMAGES.length);
        setFade(true);
      }, 400);
    }, DASHBOARD_HERO_SLIDE_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute inset-0 bg-[#071612]" aria-hidden />

      {BRAND_SLIDE_IMAGES.map((src, i) => (
        <div
          key={src}
          className={cn(
            "absolute inset-0 transition-opacity duration-[1200ms] ease-in-out",
            i === index && fade ? "opacity-100" : "opacity-0",
          )}
          aria-hidden={i !== index}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={src}
            alt=""
            className="auth-slide-branded auth-slide-branded--dashboard absolute inset-0 h-full w-full"
            loading={i === 0 ? "eager" : "lazy"}
            decoding="async"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#030c0a]/55 via-transparent to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#030c0a]/25 via-transparent to-[#030c0a]/15" />
        </div>
      ))}

      <div className="va-dashboard-hero-overlay absolute inset-0" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_75%_55%_at_12%_0%,rgba(45,212,191,0.14),transparent_58%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_40%_at_92%_85%,rgba(13,148,136,0.1),transparent_55%)]" />
    </div>
  );
}

export function DashboardHeroSection({
  userName,
  isWelcome,
  canCreate,
  planName,
  metrics,
  delay = 0,
}: DashboardHeroSectionProps) {
  const { t, formatCompactMoney } = useI18n();
  const { ref, inView } = useInView(0.08);
  const firstName = userName.trim().split(/\s+/)[0] || userName;

  const animProjects = useAnimatedNumber(metrics.totalProjects, 1000, inView);
  const animInvestment = useAnimatedNumber(metrics.totalInvestment, 1400, inView);
  const animBudgets = useAnimatedNumber(metrics.approvedBudgets, 900, inView);
  const animShared = useAnimatedNumber(metrics.sharedProjects, 800, inView);

  const projectSpark = metrics.monthlyTrend.map((m) => m.projects);
  const investSpark = metrics.monthlyTrend.map((m) => m.investment);

  const kpiCards = [
    {
      href: "/projects",
      label: t("dashboard.totalProjects"),
      display: String(Math.round(animProjects)),
      icon: FolderKanban,
      spark: projectSpark,
      trend: metrics.projectsGrowthPct,
      variant: 0,
      compactValue: false,
      delay: delay + 120,
    },
    {
      href: "/projects",
      label: t("dashboard.kpi.investmentTotal"),
      display: formatCompactMoney(animInvestment),
      icon: Wallet,
      spark: investSpark,
      trend: metrics.investmentGrowthPct,
      variant: 1,
      compactValue: true,
      delay: delay + 180,
    },
    {
      href: "/projects",
      label: t("dashboard.kpi.approvedBudgets"),
      display: String(Math.round(animBudgets)),
      icon: Layers,
      spark: investSpark.map((v, i) => (projectSpark[i] > 0 ? v / projectSpark[i] : 0)),
      trend: null,
      variant: 2,
      compactValue: false,
      delay: delay + 240,
    },
    {
      href: "/projects",
      label: t("dashboard.sharedWithMe"),
      display: String(Math.round(animShared)),
      icon: Share2,
      spark: projectSpark,
      trend: null,
      variant: 3,
      compactValue: false,
      delay: delay + 300,
    },
  ];

  return (
    <section ref={ref} className="relative mb-2" data-tour="dashboard-hero">
      <div className="relative overflow-hidden rounded-2xl shadow-xl shadow-teal-950/25 ring-1 ring-black/5">
        {isWelcome ? (
          <div className="pointer-events-none absolute -inset-1 rounded-[1.1rem] va-welcome-hero-glow" aria-hidden />
        ) : null}

        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <HeroSlideshow />
        </div>

        <div className="relative z-10 px-5 pb-[4.25rem] pt-4 sm:px-6 sm:pb-[4.5rem] sm:pt-5">
          <div
            className="va-dash-enter flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
            style={{ animationDelay: `${delay}ms` }}
          >
            <div className="min-w-0 space-y-1.5">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="inline-flex items-center gap-1 rounded-full border border-white/12 bg-white/8 px-2 py-0.5 text-[10px] font-semibold text-teal-100/90 backdrop-blur-sm">
                  <Sparkles className={cn("h-2.5 w-2.5 text-teal-300", isWelcome && "va-welcome-sparkle")} />
                  {isWelcome ? t("onboarding.welcomeBadge") : t("dashboard.hero.badge")}
                </span>
                <span className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-300/90">
                  <span className="va-live-dot h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  {t("dashboard.hero.live")}
                </span>
                <span className="text-[10px] font-medium text-white/45">{planName}</span>
              </div>
              <h1 className={cn("text-xl font-bold tracking-tight text-white sm:text-2xl", isWelcome && "va-welcome-hero-title")}>
                {isWelcome
                  ? t("onboarding.welcomeTitle", { name: firstName })
                  : t("dashboard.hero.greeting", { name: firstName })}
              </h1>
            </div>

            <div className="flex shrink-0 flex-wrap gap-2">
              {canCreate ? (
                <DashboardActionButton
                  href="/projects/new"
                  variant="primary"
                  className="inline-flex items-center gap-1.5 text-sm shadow-lg shadow-teal-900/30"
                >
                  <Plus className="h-3.5 w-3.5" />
                  {t("dashboard.new")}
                </DashboardActionButton>
              ) : null}
              <DashboardActionButton
                href="/planos"
                variant="secondary"
                className="inline-flex items-center gap-1.5 text-sm !border-white/20 !bg-white/10 !text-white hover:!border-white/30 hover:!bg-white/15"
              >
                {t("dashboard.hero.explorePlans")}
                <ArrowUpRight className="h-3.5 w-3.5 text-white/70" />
              </DashboardActionButton>
            </div>
          </div>
        </div>

        <div className="relative z-10 -mt-10 grid grid-cols-2 gap-2.5 px-3 pb-3 sm:-mt-11 sm:gap-3 sm:px-4 sm:pb-4 xl:grid-cols-4">
          {kpiCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.label}
                href={card.href}
                aria-label={card.label}
                onClick={(e) => spawnRipple(e, "va-ripple-light")}
                className={cn(
                  "va-kpi-card va-dash-enter group relative block p-3 sm:p-3.5",
                  `va-kpi-card--${card.variant}`,
                  "active:scale-[0.99]",
                )}
                style={{ animationDelay: `${card.delay}ms` }}
              >
                <div className="relative flex items-start justify-between gap-1.5">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] text-teal-200/90 backdrop-blur-sm transition duration-250 group-hover:border-teal-300/20 group-hover:bg-white/10">
                    <Icon className="h-3.5 w-3.5" strokeWidth={2.25} />
                  </span>
                  <TrendChip value={card.trend} />
                </div>

                <p
                  className={cn(
                    "relative mt-2.5 truncate font-bold leading-none tracking-tight text-white",
                    card.compactValue ? "text-lg sm:text-xl" : "text-xl sm:text-[1.35rem]",
                  )}
                >
                  {card.display}
                </p>

                <p className="relative mt-1.5 truncate text-[11px] font-semibold text-teal-100/80 sm:text-xs">
                  {card.label}
                </p>

                <div className="relative mt-2.5 flex items-center justify-between gap-1.5">
                  <Sparkline data={card.spark} active={inView} variant="light" className="h-6 w-[68px]" />
                  <ArrowUpRight className="h-3 w-3 shrink-0 text-teal-100/35 transition duration-250 group-hover:-translate-y-px group-hover:translate-x-px group-hover:text-teal-100/80" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
