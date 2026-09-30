"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  Copy,
  Loader2,
  LogIn,
  RefreshCw,
  ShieldCheck,
  Smartphone,
} from "lucide-react";
import { toast } from "sonner";

import { PageLoader } from "@/components/ui/spinner";
import { useAuth } from "@/components/providers/auth-provider";
import { GoogleAuthButton } from "@/features/auth/components/google-auth-button";
import { PricingShell } from "@/features/subscription/components/pricing-shell";
import { subscriptionApi } from "@/lib/api/subscription-api";
import { ApiError, buildQuery } from "@/lib/api/http-client";
import { tokenStore } from "@/lib/auth/token-store";
import type {
  AppyPayInstructions,
  AppyPayMethod,
  AppyPayPayment,
} from "@/lib/types/appypay";
import { periodLabel } from "@/lib/pricing/plan-price";
import type { BillingCycle, BillingPeriod, CheckoutResponse } from "@/lib/types/subscription";

const PAYMENT_ASSETS = {
  appyPay: "/payments/appypay.png",
  mcxExpress: "/payments/multicaixa-express-icon.png",
  multicaixa: "/payments/multicaixa.svg",
  emis: "/payments/emis.png",
} as const;

const SANDBOX_PHONES = [
  { number: "244900000000", label: "Sucesso" },
  { number: "244900000001", label: "Saldo insuficiente" },
  { number: "244900000002", label: "Timeout" },
  { number: "244900000003", label: "Rejeitado" },
] as const;

function normalizePhone(phone: string) {
  const digits = phone.replace(/\D/g, "");
  if (digits.startsWith("244")) return digits;
  if (digits.startsWith("0")) return `244${digits.slice(1)}`;
  if (digits.length === 9) return `244${digits}`;
  return digits;
}

function isSandboxGpoPhone(phone: string) {
  const normalized = normalizePhone(phone);
  return SANDBOX_PHONES.some((item) => item.number === normalized);
}

function paymentStatusLabel(status: AppyPayPayment["status"]) {
  switch (status) {
    case "paid":
      return "Pago";
    case "failed":
      return "Falhou";
    case "processing":
      return "A processar";
    case "pending":
      return "Pendente";
    case "cancelled":
      return "Cancelado";
    case "expired":
      return "Expirado";
    default:
      return status;
  }
}

function PaymentLogo({
  src,
  alt,
  variant = "wide",
}: {
  src: string;
  alt: string;
  variant?: "wide" | "square" | "compact";
}) {
  const box =
    variant === "square"
      ? "h-16 w-16"
      : variant === "compact"
        ? "h-10 w-24"
        : "h-14 w-36";

  return (
    <div
      className={`relative shrink-0 overflow-hidden rounded-2xl border border-zinc-100 bg-white p-2 shadow-sm ${box}`}
    >
      <Image src={src} alt={alt} fill className="object-contain p-1.5" sizes="144px" />
    </div>
  );
}

function MethodCard({
  selected,
  onSelect,
  logo,
  logoVariant,
  title,
  subtitle,
  badge,
}: {
  selected: boolean;
  onSelect: () => void;
  logo: string;
  logoVariant?: "wide" | "square" | "compact";
  title: string;
  subtitle: string;
  badge?: string;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`group w-full rounded-2xl border p-5 text-left transition-all duration-300 ${
        selected
          ? "border-[#00C896] bg-gradient-to-br from-[#f0fdf9] via-white to-white shadow-lg ring-2 ring-[#00C896]/30"
          : "border-zinc-200 bg-white hover:border-zinc-300 hover:shadow-md"
      }`}
    >
      <div className="flex items-center gap-4">
        <PaymentLogo src={logo} alt={title} variant={logoVariant ?? "wide"} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-zinc-900">{title}</p>
            {badge ? (
              <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-zinc-500">
                {badge}
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-xs leading-relaxed text-zinc-500">{subtitle}</p>
        </div>
        {selected ? (
          <CheckCircle2 className="h-6 w-6 shrink-0 text-[#00C896]" />
        ) : (
          <span className="h-6 w-6 shrink-0 rounded-full border-2 border-zinc-200 group-hover:border-zinc-300" />
        )}
      </div>
    </button>
  );
}

function PaymentTrustStrip() {
  return (
    <div className="mt-10 rounded-2xl border border-zinc-200 bg-zinc-50/80 px-5 py-4">
      <p className="text-center text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400">
        Processado com parceiros oficiais
      </p>
      <div className="mt-4 flex flex-wrap items-center justify-center gap-6">
        <div className="relative h-9 w-28 opacity-90">
          <Image src={PAYMENT_ASSETS.appyPay} alt="AppyPay" fill className="object-contain" />
        </div>
        <div className="relative h-8 w-32 opacity-90">
          <Image src={PAYMENT_ASSETS.multicaixa} alt="Multicaixa" fill className="object-contain" />
        </div>
        <div className="relative h-8 w-16 opacity-90">
          <Image src={PAYMENT_ASSETS.emis} alt="EMIS" fill className="object-contain" />
        </div>
      </div>
    </div>
  );
}

function PaymentStatusPanel({
  payment,
  instructions,
  onPoll,
  onMock,
  onRetry,
  polling,
}: {
  payment: AppyPayPayment;
  instructions: AppyPayInstructions;
  onPoll: () => void;
  onMock: () => void;
  onRetry: () => void;
  polling: boolean;
}) {
  const copy = (text: string) => {
    void navigator.clipboard.writeText(text);
    toast.success("Copiado!");
  };

  const statusColor =
    payment.status === "paid"
      ? "text-emerald-700 bg-emerald-50 border-emerald-200"
      : payment.status === "failed"
        ? "text-red-700 bg-red-50 border-red-200"
        : "text-amber-800 bg-amber-50 border-amber-200";

  const methodLogo =
    instructions.type === "gpo" ? PAYMENT_ASSETS.mcxExpress : PAYMENT_ASSETS.multicaixa;

  return (
    <div className="animate-pricing-rise mt-8 overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <div className="flex items-center gap-4 border-b border-zinc-100 bg-zinc-50 px-6 py-4">
        <PaymentLogo
          src={methodLogo}
          alt={instructions.title}
          variant={instructions.type === "gpo" ? "square" : "wide"}
        />
        <div className="min-w-0 flex-1">
          <h3 className="font-[family-name:var(--font-poppins)] text-lg font-bold text-[#0a1a2e]">
            {instructions.title}
          </h3>
          <p className="mt-1 text-xs text-zinc-500">Via AppyPay · gateway angolano</p>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-bold uppercase ${statusColor}`}>
          {paymentStatusLabel(payment.status)}
        </span>
      </div>

      <div className="p-6">
        <p className="text-sm leading-relaxed text-zinc-600">{instructions.message}</p>

        {instructions.type === "ref" && instructions.entity && instructions.reference_number ? (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {[
              { label: "Entidade", value: instructions.entity },
              { label: "Referência", value: instructions.reference_number },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-between rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3"
              >
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                    {item.label}
                  </p>
                  <p className="font-mono text-lg font-bold text-[#0a1a2e]">{item.value}</p>
                </div>
                <button
                  type="button"
                  onClick={() => copy(item.value!)}
                  className="rounded-lg p-2 text-zinc-500 hover:bg-white hover:text-zinc-800"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        ) : null}

        {instructions.type === "gpo" ? (
          <div className="mt-4 flex items-center gap-3 rounded-xl border border-orange-100 bg-orange-50/70 px-4 py-3">
            <PaymentLogo src={PAYMENT_ASSETS.mcxExpress} alt="Multicaixa Express" variant="square" />
            <p className="text-sm text-zinc-600">
              Número:{" "}
              <strong className="font-mono">
                {instructions.phone_number ?? payment.phone_number}
              </strong>
            </p>
          </div>
        ) : null}

        {payment.error_message ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <p className="font-semibold">Pagamento recusado</p>
            <p className="mt-1 leading-relaxed">{payment.error_message}</p>
          </div>
        ) : null}

        <div className="mt-5 flex flex-wrap gap-3">
          {payment.status === "failed" ? (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-2 rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-800"
            >
              Tentar novamente
            </button>
          ) : null}
          {payment.status !== "paid" && payment.status !== "failed" ? (
            <button
              type="button"
              onClick={onPoll}
              disabled={polling}
              className="inline-flex items-center gap-2 rounded-xl bg-[#0a1a2e] px-4 py-2.5 text-sm font-semibold text-white"
            >
              {polling ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Verificar pagamento
            </button>
          ) : null}
          {instructions.type === "ref" && payment.status !== "paid" ? (
            <button
              type="button"
              onClick={onMock}
              disabled={polling}
              className="inline-flex items-center gap-2 rounded-xl border border-dashed border-[#00C896] px-4 py-2.5 text-sm font-semibold text-[#047857]"
            >
              Simular pagamento (Sandbox)
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function CheckoutContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading: authLoading, refreshProfile } = useAuth();

  const planCode = searchParams.get("plan") ?? "";
  const rawCycle = searchParams.get("cycle") ?? "quarterly";
  const cycle = (rawCycle === "monthly" ? "quarterly" : rawCycle) as BillingCycle;
  const period = cycle as BillingPeriod;

  const [checkout, setCheckout] = useState<CheckoutResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [polling, setPolling] = useState(false);
  const [method, setMethod] = useState<AppyPayMethod>("gpo");
  const [phone, setPhone] = useState("244900000000");
  const [payment, setPayment] = useState<AppyPayPayment | null>(null);
  const [instructions, setInstructions] = useState<AppyPayInstructions | null>(null);

  const checkoutPath = `/planos/checkout${buildQuery({ plan: planCode, cycle, currency: "AOA" })}`;

  useEffect(() => {
    if (!planCode) {
      router.replace("/planos");
      return;
    }
    subscriptionApi
      .prepareCheckout(planCode, cycle, "AOA")
      .then((data) => setCheckout(data as CheckoutResponse))
      .catch((err) => {
        toast.error(err instanceof ApiError ? err.message : "Erro ao carregar checkout");
        router.replace("/planos");
      })
      .finally(() => setLoading(false));
  }, [planCode, cycle, router]);

  const pollPayment = useCallback(async (paymentId: string, silent = false) => {
    if (!silent) setPolling(true);
    try {
      const result = await subscriptionApi.pollAppyPayPayment(paymentId);
      setPayment(result.payment);
      setInstructions(result.instructions);
    } catch (err) {
      if (!silent) toast.error(err instanceof ApiError ? err.message : "Erro ao verificar");
    } finally {
      if (!silent) setPolling(false);
    }
  }, []);

  useEffect(() => {
    if (!payment || payment.status === "paid" || payment.status === "failed") return;
    const timer = setInterval(() => {
      void pollPayment(payment.id, true);
    }, 4000);
    return () => clearInterval(timer);
  }, [payment, pollPayment]);

  useEffect(() => {
    if (payment?.status === "paid") {
      sessionStorage.setItem(
        "va_last_payment",
        JSON.stringify({
          reference: payment.merchant_transaction_id,
          plan: checkout?.plan.name,
          total: payment.amount,
          currency: payment.currency,
        }),
      );
      toast.success("Pagamento confirmado!");
      router.push("/planos/sucesso");
    }
  }, [payment?.status, payment, checkout, router]);

  const handlePay = async () => {
    if (!checkout || authLoading) return;

    if (!isAuthenticated && !tokenStore.getAccessToken()) {
      router.push(`/login?redirect=${encodeURIComponent(checkoutPath)}`);
      return;
    }

    if (!isAuthenticated && tokenStore.getAccessToken()) {
      await refreshProfile();
      if (!tokenStore.getAccessToken()) {
        router.push(`/login?redirect=${encodeURIComponent(checkoutPath)}`);
        return;
      }
    }

    if (method === "gpo" && checkout?.appypay?.sandbox && !isSandboxGpoPhone(phone)) {
      toast.error(
        "Ambiente TST: use um número de teste AppyPay (ex.: 244900000000). Números reais não recebem notificação no sandbox.",
      );
      return;
    }

    if (method === "gpo" && !phone.trim()) {
      toast.error("Indique o número Multicaixa Express");
      return;
    }

    setSubmitting(true);
    try {
      const result = await subscriptionApi.initiateAppyPayPayment({
        plan_code: planCode,
        billing_cycle: cycle,
        payment_method: method,
        phone_number: method === "gpo" ? phone : undefined,
      });
      if (result.free_plan) {
        router.push("/planos/sucesso");
        return;
      }
      setPayment(result.payment);
      setInstructions(result.instructions);
      if (result.payment.status === "paid") {
        toast.success("Pagamento confirmado via AppyPay!");
      } else if (result.payment.status === "failed") {
        toast.error(result.payment.error_message ?? "Pagamento recusado pelo Multicaixa Express");
      } else {
        toast.success("Pedido de pagamento criado via AppyPay");
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Falha ao iniciar pagamento AppyPay");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !checkout) {
    return (
      <PricingShell isAuthenticated={isAuthenticated}>
        <PageLoader layout="section" />
      </PricingShell>
    );
  }

  const { plan, amount } = checkout;

  return (
    <PricingShell isAuthenticated={isAuthenticated}>
      <Link
        href="/planos"
        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-zinc-500 hover:text-zinc-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar aos planos
      </Link>

      <div className="mb-8 overflow-hidden rounded-3xl border border-zinc-200 bg-gradient-to-br from-[#0B1F3A] via-[#123456] to-[#1a3a5c] shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-6 p-6 md:p-8">
          <div className="flex items-center gap-5">
            <div className="rounded-2xl bg-white p-3 shadow-lg">
              <div className="relative h-10 w-32">
                <Image
                  src={PAYMENT_ASSETS.appyPay}
                  alt="AppyPay"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-white/50">Pagamento seguro</p>
              <p className="font-[family-name:var(--font-poppins)] text-xl font-bold text-white md:text-2xl">
                AppyPay · Ambiente TST
              </p>
              <p className="mt-1 text-sm text-white/70">
                Multicaixa Express e Referência via gateway EMIS
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/85">
            <ShieldCheck className="h-4 w-4 text-[#00C896]" />
            Processado em AOA
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-6 border-t border-white/10 bg-black/10 px-6 py-4 md:px-8">
          <div className="relative h-8 w-24 brightness-0 invert opacity-90">
            <Image src={PAYMENT_ASSETS.multicaixa} alt="Multicaixa" fill className="object-contain" />
          </div>
          <div className="relative h-8 w-14 brightness-0 invert opacity-90">
            <Image src={PAYMENT_ASSETS.emis} alt="EMIS" fill className="object-contain" />
          </div>
          <div className="relative h-10 w-10 overflow-hidden rounded-xl ring-2 ring-white/20">
            <Image
              src={PAYMENT_ASSETS.mcxExpress}
              alt="Multicaixa Express"
              fill
              className="object-cover"
            />
          </div>
        </div>
      </div>

      {!isAuthenticated && !authLoading ? (
        <div className="mb-6 space-y-4 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm">
          <p>Inicie sessão ou crie conta para concluir o pagamento AppyPay.</p>
          <GoogleAuthButton
            redirectTo={checkoutPath}
            compact
            onSuccess={() => void refreshProfile()}
          />
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href={`/signup?redirect=${encodeURIComponent(checkoutPath)}`}
              className="inline-flex items-center gap-2 rounded-xl border border-[#0a1a2e]/20 bg-white px-4 py-2 text-xs font-bold text-[#0a1a2e]"
            >
              Criar conta
            </Link>
            <Link
              href={`/login?redirect=${encodeURIComponent(checkoutPath)}`}
              className="inline-flex items-center gap-2 rounded-xl bg-[#0a1a2e] px-4 py-2 text-xs font-bold text-white"
            >
              <LogIn className="h-3.5 w-3.5" />
              Entrar
            </Link>
          </div>
        </div>
      ) : null}

      <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
        <div>
          <h1 className="font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#0a1a2e]">
            Escolha o método AppyPay
          </h1>
          <p className="mt-2 text-zinc-600">
            Plano <strong>{plan.name}</strong> · {periodLabel(period, "pt")}
          </p>

          {!payment ? (
            <>
              <div className="mt-8 space-y-4">
                <MethodCard
                  selected={method === "gpo"}
                  onSelect={() => setMethod("gpo")}
                  logo={PAYMENT_ASSETS.mcxExpress}
                  logoVariant="square"
                  title="Multicaixa Express"
                  subtitle="Pagamento instantâneo via número de telefone (GPO)"
                  badge="GPO"
                />
                <MethodCard
                  selected={method === "ref"}
                  onSelect={() => setMethod("ref")}
                  logo={PAYMENT_ASSETS.multicaixa}
                  logoVariant="wide"
                  title="Referência Multicaixa"
                  subtitle="Pague em ATM, Multicaixa ou Internet Banking"
                  badge="REF"
                />
              </div>

              {method === "gpo" ? (
                <div className="mt-6 space-y-4">
                  {checkout.appypay?.sandbox ? (
                    <div className="rounded-2xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                      <p className="font-semibold">Ambiente de teste AppyPay (TST)</p>
                      <p className="mt-1 leading-relaxed">
                        {checkout.appypay.gpo_note ??
                          "Números reais não recebem notificação no Multicaixa Express. Use os números de teste abaixo — o 244900000000 aprova o pagamento automaticamente."}
                      </p>
                    </div>
                  ) : null}

                  <div className="rounded-2xl border border-orange-100 bg-gradient-to-br from-orange-50/80 to-white p-5">
                    <label className="flex items-center gap-2 text-sm font-semibold text-zinc-700">
                      <Smartphone className="h-4 w-4 text-[#E31E24]" />
                      Número Multicaixa Express (teste)
                    </label>
                    <div className="mt-3 flex items-center gap-3">
                      <PaymentLogo
                        src={PAYMENT_ASSETS.mcxExpress}
                        alt="Multicaixa Express"
                        variant="square"
                      />
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="244900000000"
                        className={`w-full rounded-xl border bg-white px-4 py-3 font-mono text-sm outline-none focus:ring-2 ${
                          checkout.appypay?.sandbox && phone && !isSandboxGpoPhone(phone)
                            ? "border-red-300 focus:border-red-400 focus:ring-red-100"
                            : "border-zinc-200 focus:border-[#E31E24] focus:ring-[#E31E24]/15"
                        }`}
                      />
                    </div>
                    {checkout.appypay?.sandbox && phone && !isSandboxGpoPhone(phone) ? (
                      <p className="mt-2 text-xs font-medium text-red-600">
                        Este número não funciona no sandbox. Clique num número de teste abaixo.
                      </p>
                    ) : null}
                    <p className="mt-3 text-xs text-zinc-500">
                      Números de teste AppyPay:{" "}
                      {(checkout.appypay?.sandbox_gpo_phones ?? SANDBOX_PHONES).map((p) => (
                        <button
                          key={p.number}
                          type="button"
                          onClick={() => setPhone(p.number)}
                          className="mr-2 mt-1 inline text-[#047857] underline"
                        >
                          {p.number} ({p.label})
                        </button>
                      ))}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="mt-6 rounded-2xl border border-zinc-200 bg-zinc-50 p-5">
                  <div className="flex items-start gap-4">
                    <PaymentLogo
                      src={PAYMENT_ASSETS.multicaixa}
                      alt="Multicaixa"
                      variant="wide"
                    />
                    <div>
                      <p className="text-sm font-semibold text-zinc-800">Pagamento por referência</p>
                      <p className="mt-1 text-xs leading-relaxed text-zinc-500">
                        Após confirmar, receberá entidade e referência para pagar no Multicaixa, ATM
                        ou homebanking. No sandbox pode simular o pagamento automaticamente.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : null}

          {payment && instructions ? (
            <PaymentStatusPanel
              payment={payment}
              instructions={instructions}
              polling={polling}
              onPoll={() => void pollPayment(payment.id)}
              onRetry={() => {
                setPayment(null);
                setInstructions(null);
                setPhone("244900000000");
              }}
              onMock={() => {
                setPolling(true);
                subscriptionApi
                  .mockAppyPayReference(payment.id)
                  .then((r) => {
                    setPayment(r.payment);
                    setInstructions(r.instructions);
                  })
                  .catch((err) =>
                    toast.error(err instanceof ApiError ? err.message : "Erro na simulação"),
                  )
                  .finally(() => setPolling(false));
              }}
            />
          ) : null}

          {!payment ? <PaymentTrustStrip /> : null}
        </div>

        <aside className="h-fit rounded-2xl border border-zinc-200 bg-white p-6 shadow-lg lg:sticky lg:top-24">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-[family-name:var(--font-poppins)] text-lg font-bold">Resumo</h2>
            <div className="relative h-7 w-20">
              <Image src={PAYMENT_ASSETS.appyPay} alt="AppyPay" fill className="object-contain" />
            </div>
          </div>
          <dl className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-zinc-500">Plano</dt>
              <dd className="font-semibold">{plan.name}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-zinc-500">Método</dt>
              <dd>{method === "gpo" ? "Multicaixa Express" : "Referência"}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-zinc-500">Subtotal</dt>
              <dd>{Number(amount.subtotal).toLocaleString("pt-AO")} AOA</dd>
            </div>
            {Number(amount.vat) > 0 ? (
              <div className="flex justify-between">
                <dt className="text-zinc-500">IVA ({amount.vat_rate_pct}%)</dt>
                <dd>{Number(amount.vat).toLocaleString("pt-AO")} AOA</dd>
              </div>
            ) : null}
            <div className="border-t border-zinc-100 pt-3">
              <div className="flex justify-between">
                <dt className="font-bold">Total AppyPay</dt>
                <dd className="font-[family-name:var(--font-poppins)] text-xl font-bold text-[#0B1F3A]">
                  {Number(amount.total).toLocaleString("pt-AO")} AOA
                </dd>
              </div>
            </div>
          </dl>

          {!payment ? (
            <button
              type="button"
              disabled={submitting || authLoading}
              onClick={() => void handlePay()}
              className="mt-6 flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-[#00C896] to-[#047857] py-4 text-sm font-bold text-white shadow-lg transition hover:opacity-95 disabled:opacity-60"
            >
              {submitting || authLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <div className="relative h-5 w-5 overflow-hidden rounded-md">
                  <Image
                    src={
                      method === "gpo" ? PAYMENT_ASSETS.mcxExpress : PAYMENT_ASSETS.multicaixa
                    }
                    alt=""
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              {authLoading
                ? "A verificar sessão..."
                : isAuthenticated
                  ? "Pagar com AppyPay"
                  : "Entrar e pagar"}
            </button>
          ) : null}
        </aside>
      </div>
    </PricingShell>
  );
}

export function CheckoutPageClient() {
  return (
    <Suspense
      fallback={
        <PricingShell>
          <PageLoader layout="section" />
        </PricingShell>
      }
    >
      <CheckoutContent />
    </Suspense>
  );
}
