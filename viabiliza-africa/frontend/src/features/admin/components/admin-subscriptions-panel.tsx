"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CalendarClock, Plus, RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { AdminPlan, AdminUserSubscription } from "@/lib/types/admin";
import type { User } from "@/lib/types/auth";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

const STATUS_FILTERS = ["all", "active", "trial", "expired", "cancelled"] as const;

type Props = {
  plans: AdminPlan[];
  users: User[];
  onChanged: () => void;
};

function StatusBadge({ status, en }: { status: string; en: boolean }) {
  const map: Record<string, string> = {
    active: "bg-emerald-100 text-emerald-700",
    trial: "bg-blue-100 text-blue-700",
    expired: "bg-rose-100 text-rose-700",
    cancelled: "bg-zinc-200 text-zinc-600",
  };
  const labels: Record<string, string> = en
    ? { active: "Active", trial: "Trial", expired: "Expired", cancelled: "Cancelled" }
    : { active: "Activa", trial: "Trial", expired: "Expirada", cancelled: "Cancelada" };
  return (
    <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", map[status] ?? "bg-zinc-100")}>
      {labels[status] ?? status}
    </span>
  );
}

export function AdminSubscriptionsPanel({ plans, users, onChanged }: Props) {
  const { locale, intlLocale } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<AdminUserSubscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<(typeof STATUS_FILTERS)[number]>("all");
  const [search, setSearch] = useState("");
  const [assignOpen, setAssignOpen] = useState(false);
  const [assignUserId, setAssignUserId] = useState("");
  const [assignPlanId, setAssignPlanId] = useState("");
  const [assignEndsAt, setAssignEndsAt] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listSubscriptions({
        status: statusFilter === "all" ? undefined : statusFilter,
        limit: 100,
      });
      setItems(res.items ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load subscriptions" : "Erro ao carregar subscrições");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, en]);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter(
      (s) =>
        s.user_email?.toLowerCase().includes(q) ||
        s.user_name?.toLowerCase().includes(q) ||
        s.plan?.name.toLowerCase().includes(q),
    );
  }, [items, search]);

  async function handleStatusChange(sub: AdminUserSubscription, status: string) {
    try {
      await adminApi.updateSubscription(sub.id, { status });
      toast.success(en ? "Subscription updated" : "Subscrição actualizada");
      void load();
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Update failed" : "Falha ao actualizar");
    }
  }

  async function handleAssign() {
    if (!assignUserId || !assignPlanId) return;
    setSubmitting(true);
    try {
      await adminApi.assignSubscription({
        user_id: assignUserId,
        plan_id: assignPlanId,
        status: "active",
        ends_at: assignEndsAt ? new Date(assignEndsAt).toISOString() : undefined,
      });
      toast.success(en ? "Subscription assigned" : "Subscrição atribuída");
      setAssignOpen(false);
      setAssignUserId("");
      setAssignPlanId("");
      setAssignEndsAt("");
      void load();
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Assign failed" : "Falha ao atribuir");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">{en ? "User subscriptions" : "Subscrições de utilizadores"}</h2>
          <p className="text-sm text-zinc-500">
            {en ? "Who paid, who owes, expiration dates" : "Quem pagou, quem deve, datas de expiração"}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => void load()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button size="sm" onClick={() => setAssignOpen(true)}>
            <Plus className="h-4 w-4" />
            {en ? "Assign plan" : "Atribuir plano"}
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatusFilter(s)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-semibold transition",
              statusFilter === s ? "bg-teal-600 text-white" : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200",
            )}
          >
            {s === "all" ? (en ? "All" : "Todas") : s}
          </button>
        ))}
        <Input
          placeholder={en ? "Search user or plan..." : "Pesquisar utilizador ou plano..."}
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
                <th className="px-4 py-3">{en ? "Status" : "Estado"}</th>
                <th className="px-4 py-3">{en ? "Expires" : "Expira"}</th>
                <th className="px-4 py-3">{en ? "Days left" : "Dias restantes"}</th>
                <th className="px-4 py-3">{en ? "Actions" : "Acções"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-zinc-500">
                    {en ? "No subscriptions found" : "Nenhuma subscrição encontrada"}
                  </td>
                </tr>
              ) : (
                filtered.map((sub) => (
                  <tr key={sub.id} className="border-b border-zinc-100 hover:bg-zinc-50/60">
                    <td className="px-4 py-3">
                      <p className="font-medium text-zinc-900">{sub.user_name ?? "—"}</p>
                      <p className="text-xs text-zinc-500">{sub.user_email ?? sub.user_id}</p>
                    </td>
                    <td className="px-4 py-3">{sub.plan?.name ?? sub.plan_id}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={sub.status} en={en} />
                    </td>
                    <td className="px-4 py-3 text-zinc-600">
                      {sub.ends_at ? formatDateTime(sub.ends_at, intlLocale) : en ? "No expiry" : "Sem expiração"}
                    </td>
                    <td className="px-4 py-3">
                      {sub.days_remaining != null ? (
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 font-semibold",
                            sub.days_remaining <= 7 ? "text-rose-600" : sub.is_expiring_soon ? "text-amber-600" : "text-emerald-600",
                          )}
                        >
                          <CalendarClock className="h-3.5 w-3.5" />
                          {sub.days_remaining}d
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        value={sub.status}
                        onChange={(e) => void handleStatusChange(sub, e.target.value)}
                        className="min-w-[7rem] text-xs"
                      >
                        <option value="active">{en ? "Active" : "Activa"}</option>
                        <option value="trial">Trial</option>
                        <option value="expired">{en ? "Expired" : "Expirada"}</option>
                        <option value="cancelled">{en ? "Cancelled" : "Cancelada"}</option>
                      </Select>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </Card>
      )}

      <Modal
        open={assignOpen}
        onClose={() => setAssignOpen(false)}
        title={en ? "Assign subscription" : "Atribuir subscrição"}
        size="md"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setAssignOpen(false)}>
              {en ? "Cancel" : "Cancelar"}
            </Button>
            <Button onClick={() => void handleAssign()} disabled={submitting || !assignUserId || !assignPlanId}>
              {en ? "Assign" : "Atribuir"}
            </Button>
          </div>
        }
      >
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium">{en ? "User" : "Utilizador"}</label>
            <Select value={assignUserId} onChange={(e) => setAssignUserId(e.target.value)}>
              <option value="">{en ? "Select user" : "Seleccionar utilizador"}</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.email})
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{en ? "Plan" : "Plano"}</label>
            <Select value={assignPlanId} onChange={(e) => setAssignPlanId(e.target.value)}>
              <option value="">{en ? "Select plan" : "Seleccionar plano"}</option>
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{en ? "Expiry date (optional)" : "Data de expiração (opcional)"}</label>
            <Input type="datetime-local" value={assignEndsAt} onChange={(e) => setAssignEndsAt(e.target.value)} />
          </div>
        </div>
      </Modal>
    </div>
  );
}
