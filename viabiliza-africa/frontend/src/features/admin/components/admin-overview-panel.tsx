"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  CreditCard,
  Megaphone,
  ScrollText,
  Users,
  Wallet,
  XCircle,
} from "lucide-react";

import { Card } from "@/components/ui/card";
import { useI18n } from "@/components/providers/locale-provider";
import type { AdminTabId } from "@/features/admin/components/admin-settings-hub";
import type { AdminBillingOverview } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";

type Props = {
  overview: AdminBillingOverview;
  onNavigate: (tab: AdminTabId) => void;
};

export function AdminOverviewPanel({ overview, onNavigate }: Props) {
  const { locale, formatMoney } = useI18n();
  const en = locale === "en";
  const { subscriptions: subs, payments, system } = overview;

  const kpis = [
    {
      label: en ? "Total users" : "Utilizadores",
      value: String(overview.users_total),
      icon: Users,
      color: "text-blue-600 bg-blue-50",
      tab: "clients" as AdminTabId,
    },
    {
      label: en ? "Active subscriptions" : "Subscrições activas",
      value: String(subs.active),
      icon: CheckCircle2,
      color: "text-emerald-600 bg-emerald-50",
      tab: "subscriptions" as AdminTabId,
    },
    {
      label: en ? "Expiring in 7 days" : "Expiram em 7 dias",
      value: String(subs.expiring_7_days),
      icon: AlertTriangle,
      color: "text-amber-600 bg-amber-50",
      tab: "subscriptions" as AdminTabId,
    },
    {
      label: en ? "Expired / cancelled" : "Expiradas / canceladas",
      value: String(subs.expired + subs.cancelled),
      icon: XCircle,
      color: "text-rose-600 bg-rose-50",
      tab: "subscriptions" as AdminTabId,
    },
    {
      label: en ? "Pending payments" : "Pagamentos pendentes",
      value: String(payments.pending_count),
      icon: Clock,
      color: "text-orange-600 bg-orange-50",
      tab: "payments" as AdminTabId,
    },
    {
      label: en ? "Paid (total)" : "Pagos (total)",
      value: formatMoney(Number(payments.paid_total_amount), payments.paid_currency),
      icon: Wallet,
      color: "text-teal-600 bg-teal-50",
      tab: "payments" as AdminTabId,
    },
    {
      label: en ? "Paid this month" : "Pagos este mês",
      value: formatMoney(Number(payments.paid_this_month_amount), payments.paid_currency),
      sub: `${payments.paid_this_month_count} ${en ? "transactions" : "transacções"}`,
      icon: CreditCard,
      color: "text-violet-600 bg-violet-50",
      tab: "payments" as AdminTabId,
    },
    {
      label: en ? "Failed payments" : "Pagamentos falhados",
      value: String(payments.failed_count),
      icon: XCircle,
      color: "text-zinc-600 bg-zinc-100",
      tab: "payments" as AdminTabId,
    },
  ];

  const systemCards = [
    { label: en ? "Plans" : "Planos", value: system.subscription_plans, tab: "plans" as AdminTabId },
    {
      label: en ? "Promotions" : "Promoções",
      value: en ? "Campaign" : "Campanha",
      tab: "promotions" as AdminTabId,
      highlight: true,
    },
    { label: en ? "Integrations" : "Integrações", value: system.integrations, tab: "integrations" as AdminTabId },
    { label: en ? "Scraping sources" : "Fontes scraping", value: system.scraping_sources, tab: "scraping" as AdminTabId },
    { label: en ? "Budget templates" : "Templates", value: system.budget_templates, tab: "templates" as AdminTabId },
    { label: en ? "Audit records" : "Auditoria", value: system.audit_records, tab: "audit" as AdminTabId },
  ];

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <button
              key={kpi.label}
              type="button"
              onClick={() => onNavigate(kpi.tab)}
              className="rounded-2xl border border-zinc-200 bg-white p-4 text-left transition hover:border-teal-200 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-2">
                <span className={cn("rounded-xl p-2.5", kpi.color)}>
                  <Icon className="h-5 w-5" />
                </span>
              </div>
              <p className="mt-3 text-2xl font-bold text-zinc-900">{kpi.value}</p>
              <p className="text-sm font-medium text-zinc-600">{kpi.label}</p>
              {"sub" in kpi && kpi.sub ? <p className="text-xs text-zinc-400">{kpi.sub}</p> : null}
            </button>
          );
        })}
      </div>

      <Card>
        <div className="mb-4 flex items-center gap-2">
          <ScrollText className="h-5 w-5 text-teal-600" />
          <h2 className="text-lg font-semibold">{en ? "System resources" : "Recursos do sistema"}</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {systemCards.map((item) => (
            <button
              key={item.label}
              type="button"
              onClick={() => onNavigate(item.tab)}
              className={cn(
                "rounded-xl border px-4 py-3 text-left transition",
                "highlight" in item && item.highlight
                  ? "border-[#ffa900]/40 bg-gradient-to-br from-amber-50 to-teal-50 hover:border-[#ffa900]"
                  : "border-zinc-200 bg-zinc-50/60 hover:border-teal-200 hover:bg-teal-50/40",
              )}
            >
              {"highlight" in item && item.highlight ? (
                <Megaphone className="mb-1 h-4 w-4 text-[#ffa900]" />
              ) : null}
              <p className="text-2xl font-bold text-zinc-900">{item.value}</p>
              <p className="text-sm text-zinc-600">{item.label}</p>
            </button>
          ))}
        </div>
      </Card>

      {(subs.expiring_7_days > 0 || payments.pending_count > 0) && (
        <Card className="border-amber-200 bg-amber-50/50">
          <h3 className="font-semibold text-amber-900">
            {en ? "Attention required" : "Acção necessária"}
          </h3>
          <ul className="mt-2 space-y-1 text-sm text-amber-800">
            {subs.expiring_7_days > 0 ? (
              <li>
                • {subs.expiring_7_days}{" "}
                {en ? "subscription(s) expire within 7 days" : "subscrição(ões) expiram em 7 dias"}
              </li>
            ) : null}
            {payments.pending_count > 0 ? (
              <li>
                • {payments.pending_count}{" "}
                {en ? "pending payment(s) awaiting confirmation" : "pagamento(s) pendente(s) aguardam confirmação"}
              </li>
            ) : null}
          </ul>
        </Card>
      )}

      {overview.subscribers_by_plan && overview.subscribers_by_plan.length > 0 ? (
        <Card>
          <h2 className="mb-4 text-lg font-semibold">{en ? "Clients by plan" : "Clientes por plano"}</h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {overview.subscribers_by_plan.map((plan) => (
              <button
                key={plan.plan_code}
                type="button"
                onClick={() => onNavigate("plans")}
                className="rounded-xl border border-zinc-200 bg-zinc-50/80 px-4 py-3 text-left transition hover:border-teal-200 hover:bg-teal-50/40"
              >
                <p className="font-semibold text-zinc-900">
                  {plan.emoji ? `${plan.emoji} ` : ""}{plan.plan_name}
                </p>
                <p className="text-2xl font-bold text-teal-700">{plan.active_subscribers}</p>
                <p className="text-xs text-zinc-500">
                  {en ? "active clients" : "clientes activos"} · {plan.total_subscriptions} {en ? "total" : "total"}
                </p>
              </button>
            ))}
          </div>
        </Card>
      ) : null}

      {overview.recent_payments && overview.recent_payments.length > 0 ? (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">{en ? "Recent payments" : "Pagamentos recentes"}</h2>
            <button type="button" onClick={() => onNavigate("payments")} className="text-sm font-semibold text-teal-700 hover:underline">
              {en ? "View all" : "Ver todos"}
            </button>
          </div>
          <div className="space-y-2">
            {overview.recent_payments.map((p) => (
              <div key={p.id} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 text-sm">
                <div>
                  <p className="font-medium">{p.user_name ?? p.user_email ?? p.user_id}</p>
                  <p className="text-xs text-zinc-500">{p.plan_code} · {p.status}</p>
                </div>
                <p className="font-semibold text-teal-700">{formatMoney(Number(p.amount), p.currency)}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
