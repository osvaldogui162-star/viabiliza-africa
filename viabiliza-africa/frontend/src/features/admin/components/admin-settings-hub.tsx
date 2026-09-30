"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { PageLoader } from "@/components/ui/spinner";
import { Tabs } from "@/components/ui/tabs";
import { AdminCustomersPanel } from "@/features/admin/components/admin-customers-panel";
import { AdminAuditPanel } from "@/features/admin/components/admin-audit-panel";
import { AdminIntegrationsPanel } from "@/features/admin/components/admin-integrations-panel";
import { AdminOverviewPanel } from "@/features/admin/components/admin-overview-panel";
import { AdminPaymentsPanel } from "@/features/admin/components/admin-payments-panel";
import { AdminPlansPanel } from "@/features/admin/components/admin-plans-panel";
import { AdminPromotionsPanel } from "@/features/admin/components/admin-promotions-panel";
import { AdminScrapingPanel } from "@/features/admin/components/admin-scraping-panel";
import { AdminSubscriptionsPanel } from "@/features/admin/components/admin-subscriptions-panel";
import { AdminTemplatesPanel } from "@/features/admin/components/admin-templates-panel";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { AdminBillingOverview, AdminPlan } from "@/lib/types/admin";
import { usersApi } from "@/lib/api/users-api";
import type { User } from "@/lib/types/auth";

const TABS = [
  { id: "overview", labelPt: "Visão geral", labelEn: "Overview" },
  { id: "clients", labelPt: "Clientes", labelEn: "Clients" },
  { id: "subscriptions", labelPt: "Subscrições", labelEn: "Subscriptions" },
  { id: "payments", labelPt: "Pagamentos", labelEn: "Payments" },
  { id: "plans", labelPt: "Planos", labelEn: "Plans" },
  { id: "promotions", labelPt: "Promoções", labelEn: "Promotions" },
  { id: "integrations", labelPt: "Integrações", labelEn: "Integrations" },
  { id: "scraping", labelPt: "Scraping", labelEn: "Scraping" },
  { id: "templates", labelPt: "Templates", labelEn: "Templates" },
  { id: "audit", labelPt: "Auditoria", labelEn: "Audit" },
] as const;

export type AdminTabId =
  | "overview"
  | "clients"
  | "subscriptions"
  | "payments"
  | "plans"
  | "promotions"
  | "integrations"
  | "scraping"
  | "templates"
  | "audit";

const TAB_IDS = new Set(TABS.map((t) => t.id));

export function AdminSettingsHub() {
  const { locale } = useI18n();
  const en = locale === "en";
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab");
  const [tab, setTab] = useState<AdminTabId>(
    initialTab && TAB_IDS.has(initialTab as (typeof TABS)[number]["id"])
      ? (initialTab as AdminTabId)
      : "overview",
  );
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<AdminBillingOverview | null>(null);
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [users, setUsers] = useState<User[]>([]);

  const reload = useCallback(async () => {
    try {
      const [billing, plansRes, usersRes] = await Promise.all([
        adminApi.billingOverview(),
        adminApi.listPlans(),
        usersApi.list(),
      ]);
      setOverview(billing);
      setPlans(plansRes.items ?? []);
      setUsers(usersRes.items ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load admin data" : "Erro ao carregar dados admin");
    } finally {
      setLoading(false);
    }
  }, [en]);

  useEffect(() => {
    void reload();
  }, [reload]);

  useEffect(() => {
    const fromUrl = searchParams.get("tab");
    if (fromUrl && TAB_IDS.has(fromUrl as (typeof TABS)[number]["id"])) {
      setTab(fromUrl as AdminTabId);
    }
  }, [searchParams]);

  function selectTab(id: AdminTabId) {
    setTab(id);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("tab", id);
      window.history.replaceState({}, "", url.pathname + url.search);
    }
  }

  if (loading || !overview) {
    return <PageLoader message={en ? "Loading admin console..." : "A carregar consola admin..."} />;
  }

  const tabs = TABS.map((t) => ({ id: t.id, label: en ? t.labelEn : t.labelPt }));

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-teal-700">
          {en ? "System management" : "Gestão do sistema"}
        </p>
        <h1 className="mt-1 text-2xl font-bold text-zinc-900">
          {en ? "Administration console" : "Consola de administração"}
        </h1>
        <p className="mt-1 max-w-3xl text-sm text-zinc-500">
          {en
            ? "Full control: subscriptions, payments, plans, promotions, integrations, scraping, templates and audit."
            : "Controlo total: subscrições, pagamentos, planos, promoções, integrações, scraping, templates e auditoria."}
        </p>
      </div>

      <div className="rounded-2xl border border-zinc-200 bg-white p-1 shadow-sm">
        <Tabs tabs={tabs} active={tab} onChange={(id) => selectTab(id as AdminTabId)} variant="pills" />
      </div>

      {tab === "overview" ? (
        <AdminOverviewPanel overview={overview} onNavigate={selectTab} />
      ) : null}
      {tab === "clients" ? (
        <AdminCustomersPanel plans={plans} onChanged={reload} />
      ) : null}
      {tab === "subscriptions" ? (
        <AdminSubscriptionsPanel plans={plans} users={users} onChanged={reload} />
      ) : null}
      {tab === "payments" ? <AdminPaymentsPanel onChanged={reload} /> : null}
      {tab === "plans" ? (
        <AdminPlansPanel
          plans={plans}
          subscriberStats={overview.subscribers_by_plan}
          onChanged={reload}
        />
      ) : null}
      {tab === "promotions" ? <AdminPromotionsPanel /> : null}
      {tab === "integrations" ? <AdminIntegrationsPanel /> : null}
      {tab === "scraping" ? <AdminScrapingPanel /> : null}
      {tab === "templates" ? <AdminTemplatesPanel /> : null}
      {tab === "audit" ? <AdminAuditPanel /> : null}
    </div>
  );
}
