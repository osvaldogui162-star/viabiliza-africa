"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, FolderPlus, Sparkles, TrendingUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useI18n } from "@/components/providers/locale-provider";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

type WelcomePanelProps = {
  userName: string;
  subscription: MySubscriptionResponse | null;
  isWelcome?: boolean;
  canCreateProjects: boolean;
  projectsTotal: number;
};

export function WelcomePanel({
  userName,
  subscription,
  isWelcome,
  canCreateProjects,
  projectsTotal,
}: WelcomePanelProps) {
  const { t } = useI18n();

  const planName = subscription?.plan.name ?? t("onboarding.freePlan");
  const projectsUsed = subscription?.usage.projects_count ?? projectsTotal;
  const projectsLimit = subscription?.usage.projects_limit ?? subscription?.capabilities.projects_limit;
  const limitLabel =
    projectsLimit == null ? t("onboarding.unlimitedProjects") : String(projectsLimit);
  const isFree = subscription?.plan.code === "free" || subscription?.is_implicit_free;

  const steps = canCreateProjects
    ? [
        {
          icon: FolderPlus,
          title: t("onboarding.stepCreateTitle"),
          text: t("onboarding.stepCreateText"),
          done: projectsTotal > 0,
          href: "/projects/new",
        },
        {
          icon: TrendingUp,
          title: t("onboarding.stepAnalyzeTitle"),
          text: t("onboarding.stepAnalyzeText"),
          done: projectsTotal > 0,
          href: projectsTotal > 0 ? "/projects" : undefined,
        },
        {
          icon: Sparkles,
          title: t("onboarding.stepUpgradeTitle"),
          text: t("onboarding.stepUpgradeText"),
          done: !isFree,
          href: "/planos",
        },
      ]
    : [
        {
          icon: CheckCircle2,
          title: t("onboarding.stepSharedTitle"),
          text: t("onboarding.stepSharedText"),
          done: projectsTotal > 0,
        },
      ];

  return (
    <Card className="overflow-hidden border-emerald-200/80 bg-gradient-to-br from-emerald-50/90 via-white to-sky-50/40 p-0 shadow-sm">
      <div className="border-b border-emerald-100/80 px-5 py-4 sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
          {isWelcome ? t("onboarding.welcomeBadge") : t("onboarding.accountBadge")}
        </p>
        <h2 className="mt-1 text-xl font-semibold text-zinc-900 sm:text-[1.35rem]">
          {isWelcome
            ? t("onboarding.welcomeTitle", { name: userName })
            : t("onboarding.accountTitle", { name: userName })}
        </h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-zinc-600">
          {canCreateProjects ? t("onboarding.analystIntro") : t("onboarding.collaboratorIntro")}
        </p>
      </div>

      <div className="grid gap-4 px-5 py-4 sm:grid-cols-[1fr_auto] sm:items-center sm:px-6 sm:py-5">
        <div className="space-y-1">
          <p className="text-sm font-medium text-zinc-800">
            {t("onboarding.currentPlan", { plan: planName })}
          </p>
          <p className="text-sm text-zinc-600">
            {t("onboarding.projectsUsage", {
              used: projectsUsed,
              limit: limitLabel,
            })}
          </p>
          {subscription?.capabilities.support_sla ? (
            <p className="text-xs text-zinc-500">
              {t("onboarding.supportSla", { sla: subscription.capabilities.support_sla })}
            </p>
          ) : null}
        </div>

        <div className="flex flex-wrap gap-2">
          {canCreateProjects && projectsTotal === 0 ? (
            <Link href="/projects/new">
              <Button size="sm">
                <FolderPlus className="h-4 w-4" />
                {t("onboarding.createFirstProject")}
              </Button>
            </Link>
          ) : null}
          <Link href="/conta/assinatura">
            <Button size="sm" variant="outline">
              {t("onboarding.viewSubscription")}
            </Button>
          </Link>
          {isFree ? (
            <Link href="/planos">
              <Button size="sm" variant="outline">
                {t("onboarding.upgradePlan")}
              </Button>
            </Link>
          ) : null}
        </div>
      </div>

      <div className="border-t border-emerald-100/70 bg-white/70 px-5 py-4 sm:px-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-zinc-500">
          {t("onboarding.nextSteps")}
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          {steps.map((step) => {
            const Icon = step.icon;
            const content = (
              <div
                className={`rounded-xl border px-4 py-3 transition ${
                  step.done
                    ? "border-emerald-200 bg-emerald-50/60"
                    : "border-zinc-200 bg-white hover:border-emerald-200 hover:bg-emerald-50/30"
                }`}
              >
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${
                      step.done ? "bg-emerald-100 text-emerald-700" : "bg-zinc-100 text-zinc-600"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-zinc-900">{step.title}</p>
                    <p className="mt-1 text-xs leading-relaxed text-zinc-600">{step.text}</p>
                    {"href" in step && step.href && !step.done ? (
                      <span className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-emerald-700">
                        {t("onboarding.startNow")}
                        <ArrowRight className="h-3.5 w-3.5" />
                      </span>
                    ) : null}
                  </div>
                </div>
              </div>
            );

            return "href" in step && step.href && !step.done ? (
              <Link key={step.title} href={step.href} className="block">
                {content}
              </Link>
            ) : (
              <div key={step.title}>{content}</div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
