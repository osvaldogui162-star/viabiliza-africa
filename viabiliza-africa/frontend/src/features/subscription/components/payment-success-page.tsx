"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CheckCircle2, Download, LayoutDashboard } from "lucide-react";

import { PricingShell } from "@/features/subscription/components/pricing-shell";

type PaymentSummary = {
  reference: string;
  plan: string;
  total: string;
  currency: string;
};

export function PaymentSuccessPage() {
  const [summary, setSummary] = useState<PaymentSummary | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("va_last_payment");
    if (raw) {
      try {
        setSummary(JSON.parse(raw) as PaymentSummary);
        sessionStorage.removeItem("va_last_payment");
      } catch {
        setSummary(null);
      }
    }
  }, []);

  return (
    <PricingShell isAuthenticated>
      <div className="mx-auto max-w-lg py-10 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
          <CheckCircle2 className="h-10 w-10 text-emerald-600" />
        </div>
        <h1 className="mt-6 font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#0a1a2e]">
          Pagamento confirmado!
        </h1>
        <p className="mt-3 text-zinc-600">
          A sua assinatura foi activada com sucesso. Já pode utilizar todas as funcionalidades do
          plano seleccionado.
        </p>

        {summary ? (
          <div className="mt-8 rounded-2xl border border-zinc-200 bg-zinc-50 p-6 text-left text-sm">
            <p className="font-semibold text-zinc-900">Detalhes do pagamento</p>
            <dl className="mt-4 space-y-2">
              <div className="flex justify-between">
                <dt className="text-zinc-500">Referência</dt>
                <dd className="font-mono font-semibold">{summary.reference}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-zinc-500">Plano</dt>
                <dd>{summary.plan}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-zinc-500">Total pago</dt>
                <dd className="font-bold">
                  {Number(summary.total).toLocaleString("pt-AO")} {summary.currency}
                </dd>
              </div>
            </dl>
          </div>
        ) : null}

        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#0a1a2e] px-6 py-3.5 text-sm font-bold text-white transition hover:bg-[#1a3a5c]"
          >
            <LayoutDashboard className="h-4 w-4" />
            Ir para o Dashboard
          </Link>
          <Link
            href="/conta/assinatura"
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-zinc-200 bg-white px-6 py-3.5 text-sm font-bold text-zinc-800 transition hover:bg-zinc-50"
          >
            <Download className="h-4 w-4" />
            Ver assinatura
          </Link>
        </div>
      </div>
    </PricingShell>
  );
}
