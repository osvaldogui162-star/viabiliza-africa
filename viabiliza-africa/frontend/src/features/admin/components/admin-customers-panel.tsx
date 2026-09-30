"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ExternalLink, RefreshCw, UserCog } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { usersApi } from "@/lib/api/users-api";
import { ApiError } from "@/lib/api/http-client";
import type { AdminCustomer, AdminPlan } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

type Props = {
  plans: AdminPlan[];
  onChanged: () => void;
};

const STATUS_LABELS: Record<string, { pt: string; en: string; className: string }> = {
  active: { pt: "Activo", en: "Active", className: "bg-emerald-100 text-emerald-700" },
  active_expiring: { pt: "Expira em breve", en: "Expiring soon", className: "bg-amber-100 text-amber-800" },
  payment_pending: { pt: "Pagamento pendente", en: "Payment pending", className: "bg-orange-100 text-orange-800" },
  expired: { pt: "Expirado", en: "Expired", className: "bg-rose-100 text-rose-700" },
  trial: { pt: "Trial", en: "Trial", className: "bg-blue-100 text-blue-700" },
  no_subscription: { pt: "Sem subscrição", en: "No subscription", className: "bg-zinc-200 text-zinc-600" },
};

export function AdminCustomersPanel({ plans, onChanged }: Props) {
  const { locale, intlLocale, formatMoney } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<AdminCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<string>("all");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listCustomers({ limit: 200 });
      setItems(res.items ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load clients" : "Erro ao carregar clientes");
    } finally {
      setLoading(false);
    }
  }, [en]);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    let list = items;
    if (filter !== "all") {
      list = list.filter((c) => c.billing_status === filter);
    }
    const q = search.trim().toLowerCase();
    if (!q) return list;
    return list.filter(
      (c) =>
        c.user.email.toLowerCase().includes(q) ||
        c.user.full_name.toLowerCase().includes(q) ||
        c.subscription?.plan?.name.toLowerCase().includes(q),
    );
  }, [items, search, filter]);

  async function toggleUserActive(customer: AdminCustomer) {
    try {
      await usersApi.update(customer.user.id, { is_active: !customer.user.is_active });
      toast.success(en ? "User updated" : "Utilizador actualizado");
      void load();
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Update failed" : "Falha");
    }
  }

  async function assignFreePlan(customer: AdminCustomer) {
    const freePlan = plans.find((p) => p.code === "free");
    if (!freePlan) {
      toast.error(en ? "Free plan not found — sync catalog first" : "Plano free não encontrado — sincronize o catálogo");
      return;
    }
    try {
      await adminApi.assignSubscription({ user_id: customer.user.id, plan_id: freePlan.id, status: "active" });
      toast.success(en ? "Plan assigned" : "Plano atribuído");
      void load();
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Assign failed" : "Falha ao atribuir");
    }
  }

  const filters = [
    { id: "all", label: en ? "All" : "Todos" },
    { id: "active", label: en ? "Active" : "Activos" },
    { id: "payment_pending", label: en ? "Pending pay" : "Pag. pendente" },
    { id: "active_expiring", label: en ? "Expiring" : "A expirar" },
    { id: "expired", label: en ? "Expired" : "Expirados" },
    { id: "no_subscription", label: en ? "No plan" : "Sem plano" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">{en ? "Clients" : "Clientes"}</h2>
          <p className="text-sm text-zinc-500">
            {en ? "Everything happening with your customers in real time" : "Tudo o que acontece com os clientes em tempo real"}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => { void load(); onChanged(); }}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setFilter(f.id)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-semibold transition",
              filter === f.id ? "bg-teal-600 text-white" : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200",
            )}
          >
            {f.label}
          </button>
        ))}
        <Input
          placeholder={en ? "Search client..." : "Pesquisar cliente..."}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      {loading ? (
        <PageLoader message={en ? "Loading clients..." : "A carregar clientes..."} />
      ) : (
        <Card className="overflow-x-auto p-0">
          <table className="min-w-full text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-500">
              <tr>
                <th className="px-4 py-3">{en ? "Client" : "Cliente"}</th>
                <th className="px-4 py-3">{en ? "Plan" : "Plano"}</th>
                <th className="px-4 py-3">{en ? "Billing" : "Facturação"}</th>
                <th className="px-4 py-3">{en ? "Last payment" : "Último pagamento"}</th>
                <th className="px-4 py-3">{en ? "Projects" : "Projectos"}</th>
                <th className="px-4 py-3">{en ? "Expires" : "Expira"}</th>
                <th className="px-4 py-3">{en ? "Actions" : "Acções"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((customer) => {
                const status = STATUS_LABELS[customer.billing_status] ?? STATUS_LABELS.no_subscription;
                const sub = customer.subscription;
                const pay = customer.latest_payment;
                return (
                  <tr key={customer.user.id} className="border-b border-zinc-100 hover:bg-zinc-50/60">
                    <td className="px-4 py-3">
                      <p className="font-medium text-zinc-900">{customer.user.full_name}</p>
                      <p className="text-xs text-zinc-500">{customer.user.email}</p>
                      <p className="text-[10px] text-zinc-400">
                        {customer.user.role} · {customer.user.is_active ? (en ? "active" : "activo") : en ? "inactive" : "inactivo"}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      {sub?.plan ? (
                        <>
                          <p className="font-medium">{sub.plan.features?.emoji ? `${sub.plan.features.emoji} ` : ""}{sub.plan.name}</p>
                          <p className="text-xs text-zinc-500">{sub.plan.code}</p>
                        </>
                      ) : (
                        <span className="text-zinc-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", status.className)}>
                        {en ? status.en : status.pt}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {pay ? (
                        <>
                          <p className="font-medium">{formatMoney(Number(pay.amount), pay.currency)}</p>
                          <p className="text-xs capitalize text-zinc-500">{pay.status}</p>
                        </>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3 font-semibold">{customer.projects_count}</td>
                    <td className="px-4 py-3">
                      {sub?.ends_at ? (
                        <span className={cn(sub.days_remaining != null && sub.days_remaining <= 7 && "font-bold text-rose-600")}>
                          {sub.days_remaining != null ? `${sub.days_remaining}d` : formatDateTime(sub.ends_at, intlLocale)}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        <Button size="sm" variant="outline" onClick={() => void toggleUserActive(customer)}>
                          <UserCog className="h-3.5 w-3.5" />
                        </Button>
                        {!sub ? (
                          <Button size="sm" variant="outline" onClick={() => void assignFreePlan(customer)}>
                            Free
                          </Button>
                        ) : null}
                        <Link href="/planos" target="_blank" className="inline-flex">
                          <Button size="sm" variant="outline">
                            <ExternalLink className="h-3.5 w-3.5" />
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
