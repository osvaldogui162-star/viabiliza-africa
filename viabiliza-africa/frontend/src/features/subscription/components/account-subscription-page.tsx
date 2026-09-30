"use client";



import Link from "next/link";

import { useEffect, useState } from "react";

import { ArrowUpRight, Check, RefreshCw, X } from "lucide-react";
import { PageLoader } from "@/components/ui/spinner";

import { toast } from "sonner";



import { useAuth } from "@/components/providers/auth-provider";

import { PricingShell } from "@/features/subscription/components/pricing-shell";

import { subscriptionApi } from "@/lib/api/subscription-api";

import { ApiError } from "@/lib/api/http-client";

import type { MySubscriptionResponse, PlanCapabilities } from "@/lib/types/subscription";



function UsageBar({

  label,

  used,

  limit,

}: {

  label: string;

  used: number;

  limit: number | null | undefined;

}) {

  const pct =

    limit != null && limit > 0 ? Math.min(100, (used / limit) * 100) : null;



  return (

    <div className="rounded-2xl border border-zinc-200 bg-white p-5">

      <div className="flex justify-between text-sm">

        <span className="font-medium text-zinc-700">{label}</span>

        <span className="font-bold text-zinc-900">

          {used}

          {limit != null ? ` / ${limit}` : " / ∞"}

        </span>

      </div>

      {pct != null ? (

        <div className="mt-3 h-2 overflow-hidden rounded-full bg-zinc-100">

          <div

            className="h-full rounded-full bg-emerald-500 transition-all"

            style={{ width: `${pct}%` }}

          />

        </div>

      ) : null}

    </div>

  );

}



function CapabilityRow({

  label,

  enabled,

  detail,

}: {

  label: string;

  enabled: boolean;

  detail?: string;

}) {

  return (

    <li className="flex items-start gap-2.5 text-sm text-zinc-600">

      {enabled ? (

        <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />

      ) : (

        <X className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />

      )}

      <span>

        {label}

        {detail ? <span className="text-zinc-400"> — {detail}</span> : null}

      </span>

    </li>

  );

}



function buildCapabilityRows(cap: PlanCapabilities) {

  return [

    {

      label: "Projectos activos",

      enabled: true,

      detail: cap.projects_limit_label,

    },

    {

      label: "Ingestão automática / scraping",

      enabled: cap.auto_ingestion_enabled,

      detail: cap.scraping_limit_label,

    },

    {

      label: "Monte Carlo",

      enabled: cap.monte_carlo_enabled,

      detail: `até ${cap.monte_carlo_iterations_limit.toLocaleString("pt-AO")} iterações`,

    },

    { label: "Análise de sensibilidade", enabled: cap.sensitivity_enabled },

    { label: "Relatório internacional", enabled: cap.reports_international },

    { label: "Relatório BFA", enabled: cap.reports_bfa },

    { label: "Relatório BDA", enabled: cap.reports_bda },

    { label: "Relatório AIPEX", enabled: cap.reports_aipex },

    { label: "API bancária", enabled: cap.bank_api_enabled },

    { label: "Análise ESG", enabled: cap.esg_enabled, detail: cap.esg_advanced_enabled ? "Avançada" : cap.esg_enabled ? "Básica" : undefined },

    { label: "Digital Twin", enabled: cap.digital_twin_enabled },

    { label: "SROI / impacto social", enabled: cap.sroi_enabled },

    {

      label: "Utilizadores na equipa",

      enabled: true,

      detail: cap.team_members_limit_label,

    },

    {

      label: "Suporte",

      enabled: true,

      detail: cap.support_sla ?? "—",

    },

  ];

}



export function AccountSubscriptionPage() {

  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [data, setData] = useState<MySubscriptionResponse | null>(null);

  const [loading, setLoading] = useState(true);



  const load = async () => {

    setLoading(true);

    try {

      const sub = await subscriptionApi.getMySubscription();

      setData(sub);

    } catch (err) {

      toast.error(err instanceof ApiError ? err.message : "Erro ao carregar assinatura");

    } finally {

      setLoading(false);

    }

  };



  useEffect(() => {

    if (!authLoading && isAuthenticated) void load();

  }, [authLoading, isAuthenticated]);



  if (authLoading || loading) {

    return (

      <PricingShell isAuthenticated>

        <PageLoader layout="section" />

      </PricingShell>

    );

  }



  const plan = data?.plan;

  const usage = data?.usage;

  const subscription = data?.subscription;

  const capabilities = data?.capabilities;

  const capabilityRows = capabilities ? buildCapabilityRows(capabilities) : [];



  return (

    <PricingShell isAuthenticated>

      <div className="flex flex-wrap items-start justify-between gap-4">

        <div>

          <h1 className="font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#0a1a2e]">

            Minha assinatura

          </h1>

          <p className="mt-2 text-zinc-600">

            Limites e funcionalidades do seu plano — alinhados com a página de preços

          </p>

        </div>

        <button

          type="button"

          onClick={() => void load()}

          className="inline-flex items-center gap-2 rounded-xl border border-zinc-200 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"

        >

          <RefreshCw className="h-4 w-4" />

          Actualizar

        </button>

      </div>



      <div className="mt-8 grid gap-6 lg:grid-cols-2">

        <div className="rounded-2xl border border-zinc-200 bg-gradient-to-br from-[#0a1a2e] to-[#1a3a5c] p-6 text-white shadow-lg">

          <p className="text-xs font-semibold uppercase tracking-widest text-white/60">Plano actual</p>

          <p className="mt-2 font-[family-name:var(--font-poppins)] text-3xl font-bold">

            {plan?.emoji ? `${plan.emoji} ` : ""}

            {plan?.name ?? "—"}

          </p>

          <p className="mt-2 text-sm text-white/70">{plan?.description}</p>

          {capabilities?.support_sla ? (

            <p className="mt-3 text-xs text-white/60">SLA: {capabilities.support_sla}</p>

          ) : null}

          {subscription?.ends_at ? (

            <p className="mt-2 text-xs text-white/50">

              Renovação: {new Date(subscription.ends_at).toLocaleDateString("pt-AO")}

            </p>

          ) : null}

          <Link

            href="/planos"

            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#c6a43f] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#a8892e]"

          >

            Alterar plano

            <ArrowUpRight className="h-4 w-4" />

          </Link>

        </div>



        <div className="space-y-4">

          <UsageBar

            label="Projectos activos"

            used={usage?.projects_count ?? 0}

            limit={usage?.projects_limit}

          />

          <UsageBar

            label="Scraping / ingestão automática (este mês)"

            used={usage?.scraping_items_this_month ?? 0}

            limit={

              capabilities?.scraping_enabled ? usage?.scraping_items_limit : 0

            }

          />

          <UsageBar

            label="Colaboradores na equipa"

            used={usage?.collaborators_count ?? 0}

            limit={

              usage?.team_members_limit != null

                ? Math.max(0, usage.team_members_limit - 1)

                : null

            }

          />

        </div>

      </div>



      {capabilities ? (

        <div className="mt-8 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">

          <h2 className="font-[family-name:var(--font-poppins)] text-lg font-bold text-[#0a1a2e]">

            Funcionalidades incluídas

          </h2>

          <p className="mt-1 text-sm text-zinc-500">

            O que o sistema permite com o plano «{capabilities.plan_name}»

          </p>

          <ul className="mt-5 grid gap-2 sm:grid-cols-2">

            {capabilityRows.map((row) => (

              <CapabilityRow

                key={row.label}

                label={row.label}

                enabled={row.enabled}

                detail={row.detail}

              />

            ))}

          </ul>

        </div>

      ) : null}

    </PricingShell>

  );

}


