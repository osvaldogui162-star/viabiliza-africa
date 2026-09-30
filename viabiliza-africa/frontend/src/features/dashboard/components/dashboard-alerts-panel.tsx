"use client";

import Link from "next/link";
import { AlertTriangle, ArrowRight, BellRing, CheckCircle2, Info } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import type { DashboardAlert } from "@/features/dashboard/lib/dashboard-analytics";

const toneStyles = {
  info: { border: "border-l-sky-500", icon: "text-sky-600", Icon: Info },
  warning: { border: "border-l-amber-500", icon: "text-amber-600", Icon: AlertTriangle },
  success: { border: "border-l-emerald-500", icon: "text-emerald-600", Icon: CheckCircle2 },
  danger: { border: "border-l-rose-500", icon: "text-rose-600", Icon: AlertTriangle },
};

export function DashboardAlertsPanel({
  alerts,
  enterDelay = 0,
}: {
  alerts: DashboardAlert[];
  enterDelay?: number;
}) {
  const { t } = useI18n();

  return (
    <section className="va-glass-card va-dash-enter p-4" style={{ animationDelay: `${enterDelay}ms` }}>
      <div className="mb-3 flex items-center gap-2">
        <span className="va-icon-box h-8 w-8">
          <BellRing className="h-4 w-4" />
        </span>
        <div>
          <h2 className="va-section-title">{t("dashboard.alerts.title")}</h2>
          <p className="va-section-sub">{t("dashboard.alerts.subtitle")}</p>
        </div>
      </div>

      <div className="space-y-2">
        {alerts.map((alert, index) => {
          const style = toneStyles[alert.tone];
          const Icon = style.Icon;
          const inner = (
            <div
              className={`va-dash-enter rounded-md border border-[var(--border)] border-l-[3px] bg-slate-50/80 px-3 py-2.5 transition duration-200 ${style.border} ${
                alert.href ? "hover:bg-white hover:shadow-sm" : ""
              }`}
              style={{ animationDelay: `${enterDelay + 80 + index * 60}ms` }}
            >
              <div className="flex items-start gap-2">
                <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${style.icon}`} />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-[var(--foreground)]">{alert.title}</p>
                  <p className="mt-0.5 text-[11px] leading-snug text-[var(--muted)]">{alert.message}</p>
                  {alert.href && alert.actionLabel ? (
                    <span className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-semibold text-[var(--primary)]">
                      {alert.actionLabel}
                      <ArrowRight className="h-3 w-3" />
                    </span>
                  ) : null}
                </div>
              </div>
            </div>
          );

          return alert.href ? (
            <Link key={alert.id} href={alert.href} className="block">
              {inner}
            </Link>
          ) : (
            <div key={alert.id}>{inner}</div>
          );
        })}
      </div>
    </section>
  );
}
