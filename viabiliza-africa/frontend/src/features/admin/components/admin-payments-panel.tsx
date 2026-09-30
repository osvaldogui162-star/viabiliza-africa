"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { AdminPayment } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

const PAYMENT_FILTERS = ["all", "paid", "pending", "failed"] as const;

type Props = { onChanged: () => void };

function PaymentStatusBadge({ status, en }: { status: string; en: boolean }) {
  const map: Record<string, string> = {
    paid: "bg-emerald-100 text-emerald-700",
    pending: "bg-amber-100 text-amber-800",
    failed: "bg-rose-100 text-rose-700",
    cancelled: "bg-zinc-200 text-zinc-600",
    expired: "bg-zinc-200 text-zinc-600",
  };
  const labels: Record<string, string> = en
    ? { paid: "Paid", pending: "Pending", failed: "Failed", cancelled: "Cancelled", expired: "Expired" }
    : { paid: "Pago", pending: "Pendente", failed: "Falhou", cancelled: "Cancelado", expired: "Expirado" };
  return (
    <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", map[status] ?? "bg-zinc-100")}>
      {labels[status] ?? status}
    </span>
  );
}

export function AdminPaymentsPanel({ onChanged }: Props) {
  const { locale, intlLocale, formatMoney } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<AdminPayment[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<(typeof PAYMENT_FILTERS)[number]>("all");
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listPayments({
        status: filter === "all" ? undefined : filter === "failed" ? undefined : filter,
        limit: 100,
      });
      let list = res.items ?? [];
      if (filter === "failed") {
        list = list.filter((p) => ["failed", "cancelled", "expired"].includes(p.status));
      }
      setItems(list);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load payments" : "Erro ao carregar pagamentos");
    } finally {
      setLoading(false);
    }
  }, [filter, en]);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter(
      (p) =>
        p.user_email?.toLowerCase().includes(q) ||
        p.user_name?.toLowerCase().includes(q) ||
        p.plan_code.toLowerCase().includes(q) ||
        p.merchant_transaction_id.toLowerCase().includes(q),
    );
  }, [items, search]);

  const totals = useMemo(() => {
    const paid = filtered.filter((p) => p.status === "paid");
    const pending = filtered.filter((p) => p.status === "pending");
    const sum = paid.reduce((acc, p) => acc + Number(p.amount), 0);
    return { paid: paid.length, pending: pending.length, sum, currency: paid[0]?.currency ?? "AOA" };
  }, [filtered]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">{en ? "Payments" : "Pagamentos"}</h2>
          <p className="text-sm text-zinc-500">
            {en ? "Track who paid, pending and failed transactions" : "Acompanhe quem pagou, pendentes e falhas"}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => { void load(); onChanged(); }}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <Card className="p-4">
          <p className="text-xs text-zinc-500">{en ? "Paid (visible)" : "Pagos (visíveis)"}</p>
          <p className="text-xl font-bold text-emerald-700">{totals.paid}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-zinc-500">{en ? "Pending" : "Pendentes"}</p>
          <p className="text-xl font-bold text-amber-700">{totals.pending}</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-zinc-500">{en ? "Amount paid" : "Valor pago"}</p>
          <p className="text-xl font-bold text-teal-700">{formatMoney(totals.sum, totals.currency)}</p>
        </Card>
      </div>

      <div className="flex flex-wrap gap-2">
        {PAYMENT_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setFilter(s)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-semibold transition",
              filter === s ? "bg-teal-600 text-white" : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200",
            )}
          >
            {s === "all" ? (en ? "All" : "Todos") : s === "paid" ? (en ? "Paid" : "Pagos") : s === "pending" ? (en ? "Pending" : "Pendentes") : en ? "Failed" : "Falhados"}
          </button>
        ))}
        <Input
          placeholder={en ? "Search..." : "Pesquisar..."}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      {loading ? (
        <PageLoader message={en ? "Loading..." : "A carregar..."} />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="min-w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-500">
              <tr>
                <th className="px-4 py-3">{en ? "User" : "Utilizador"}</th>
                <th className="px-4 py-3">{en ? "Plan" : "Plano"}</th>
                <th className="px-4 py-3">{en ? "Amount" : "Valor"}</th>
                <th className="px-4 py-3">{en ? "Method" : "Método"}</th>
                <th className="px-4 py-3">{en ? "Status" : "Estado"}</th>
                <th className="px-4 py-3">{en ? "Date" : "Data"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-zinc-500">
                    {en ? "No payments found" : "Nenhum pagamento encontrado"}
                  </td>
                </tr>
              ) : (
                filtered.map((p) => (
                  <tr key={p.id} className="border-b border-zinc-100 hover:bg-zinc-50/60">
                    <td className="px-4 py-3">
                      <p className="font-medium">{p.user_name ?? "—"}</p>
                      <p className="text-xs text-zinc-500">{p.user_email}</p>
                    </td>
                    <td className="px-4 py-3">
                      <p>{p.plan_code}</p>
                      <p className="text-xs text-zinc-500">{p.billing_cycle}</p>
                    </td>
                    <td className="px-4 py-3 font-semibold">{formatMoney(Number(p.amount), p.currency)}</td>
                    <td className="px-4 py-3 uppercase text-xs">{p.payment_method}</td>
                    <td className="px-4 py-3">
                      <PaymentStatusBadge status={p.status} en={en} />
                    </td>
                    <td className="px-4 py-3 text-zinc-600">
                      {formatDateTime(p.paid_at ?? p.created_at, intlLocale)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
