"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Ban,
  CalendarClock,
  CheckCircle2,
  Clock,
  RefreshCw,
  ShieldCheck,
  UserPlus,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/ui/spinner";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { RegisterUserModal } from "@/features/users/components/register-user-modal";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { usersApi } from "@/lib/api/users-api";
import { ApiError } from "@/lib/api/http-client";
import type { AdminPlan, AdminUserSubscription } from "@/lib/types/admin";
import type { User, UserRole } from "@/lib/types/auth";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

type FilterTab = "pending" | "all" | "active" | "inactive";

const ACCESS_PRESETS = [30, 90, 180, 365] as const;

function roleLabel(role: UserRole, en: boolean) {
  if (role === "admin") return en ? "Admin" : "Administrador";
  if (role === "financial") return en ? "Analyst" : "Analista";
  if (role === "bank") return en ? "Bank portal" : "Portal bancário";
  return en ? "Collaborator" : "Colaborador";
}

export function AdminUsersPanel() {
  const { locale, intlLocale, t } = useI18n();
  const en = locale === "en";

  const [users, setUsers] = useState<User[]>([]);
  const [subscriptions, setSubscriptions] = useState<AdminUserSubscription[]>([]);
  const [plans, setPlans] = useState<AdminPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<FilterTab>("pending");
  const [search, setSearch] = useState("");
  const [registerOpen, setRegisterOpen] = useState(false);

  const [approveTarget, setApproveTarget] = useState<User | null>(null);
  const [extendTarget, setExtendTarget] = useState<User | null>(null);
  const [modalRole, setModalRole] = useState<"financial" | "user">("financial");
  const [modalPlanId, setModalPlanId] = useState("");
  const [modalDays, setModalDays] = useState<number>(90);
  const [submitting, setSubmitting] = useState(false);

  const subByUser = useMemo(() => {
    const map = new Map<string, AdminUserSubscription>();
    for (const sub of subscriptions) {
      const existing = map.get(sub.user_id);
      if (!existing || sub.status === "active") map.set(sub.user_id, sub);
    }
    return map;
  }, [subscriptions]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [usersRes, subsRes, plansRes] = await Promise.all([
        usersApi.list({ limit: 200 }),
        adminApi.listSubscriptions({ limit: 200 }),
        adminApi.listPlans(true),
      ]);
      setUsers(usersRes.items);
      setSubscriptions(subsRes.items ?? []);
      setPlans(plansRes.items ?? []);
      if (!modalPlanId && plansRes.items?.length) {
        const free = plansRes.items.find((p) => p.code === "free");
        setModalPlanId(free?.id ?? plansRes.items[0].id);
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("adminUsers.loadError"));
    } finally {
      setLoading(false);
    }
  }, [modalPlanId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const pendingCount = users.filter((u) => !u.is_active).length;

  const filtered = useMemo(() => {
    let list = users;
    if (tab === "pending") list = list.filter((u) => !u.is_active);
    else if (tab === "active") list = list.filter((u) => u.is_active);
    else if (tab === "inactive") list = list.filter((u) => !u.is_active);

    const q = search.trim().toLowerCase();
    if (!q) return list;
    return list.filter(
      (u) => u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q),
    );
  }, [users, tab, search]);

  async function handleApprove() {
    if (!approveTarget) return;
    setSubmitting(true);
    try {
      await usersApi.approve(approveTarget.id, {
        role: modalRole,
        plan_id: modalRole === "financial" ? modalPlanId : undefined,
        access_days: modalRole === "financial" ? modalDays : undefined,
      });
      toast.success(t("adminUsers.approveSuccess"));
      setApproveTarget(null);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleExtend() {
    if (!extendTarget) return;
    setSubmitting(true);
    try {
      await usersApi.extendAccess(extendTarget.id, {
        plan_id: modalPlanId,
        access_days: modalDays,
      });
      toast.success(t("adminUsers.extendSuccess"));
      setExtendTarget(null);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleBlock(user: User) {
    try {
      await usersApi.update(user.id, { is_active: false });
      toast.success(t("adminUsers.blockSuccess"));
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    }
  }

  function openApprove(user: User) {
    setApproveTarget(user);
    setModalRole(user.role === "user" ? "user" : "financial");
    setModalDays(90);
  }

  function openExtend(user: User) {
    setExtendTarget(user);
    const sub = subByUser.get(user.id);
    if (sub?.plan_id) setModalPlanId(sub.plan_id);
    setModalDays(90);
  }

  const tabs: { id: FilterTab; label: string; badge?: number }[] = [
    { id: "pending", label: t("adminUsers.tabPending"), badge: pendingCount },
    { id: "all", label: t("adminUsers.tabAll") },
    { id: "active", label: t("adminUsers.tabActive") },
    { id: "inactive", label: t("adminUsers.tabInactive") },
  ];

  return (
    <>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {tabs.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition",
                tab === item.id
                  ? "bg-teal-600 text-white shadow-sm"
                  : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200",
              )}
            >
              {item.label}
              {item.badge ? (
                <span className="rounded-full bg-white/20 px-1.5 text-xs font-bold">{item.badge}</span>
              ) : null}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => void load()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button size="sm" onClick={() => setRegisterOpen(true)}>
            <UserPlus className="h-4 w-4" />
            {t("adminUsers.registerManual")}
          </Button>
        </div>
      </div>

      <Input
        placeholder={t("adminUsers.searchPlaceholder")}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-4 max-w-md"
      />

      {loading ? (
        <PageLoader layout="section" message={t("common.loading")} />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-zinc-200/80 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="border-b bg-zinc-50/80 text-left text-xs uppercase tracking-wide text-zinc-500">
              <tr>
                <th className="p-3">{t("adminUsers.colUser")}</th>
                <th className="p-3">{t("adminUsers.colRole")}</th>
                <th className="p-3">{t("adminUsers.colPlan")}</th>
                <th className="p-3">{t("adminUsers.colAccessUntil")}</th>
                <th className="p-3">{t("adminUsers.colStatus")}</th>
                <th className="p-3 text-right">{t("adminUsers.colActions")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-zinc-500">
                    {t("adminUsers.empty")}
                  </td>
                </tr>
              ) : (
                filtered.map((user) => {
                  const sub = subByUser.get(user.id);
                  const pending = !user.is_active;
                  return (
                    <tr key={user.id} className="border-t border-zinc-100">
                      <td className="p-3">
                        <p className="font-medium text-zinc-900">{user.full_name}</p>
                        <p className="text-xs text-zinc-500">{user.email}</p>
                      </td>
                      <td className="p-3">{roleLabel(user.role, en)}</td>
                      <td className="p-3">{sub?.plan?.name ?? "—"}</td>
                      <td className="p-3">
                        {sub?.ends_at ? (
                          <span className="inline-flex items-center gap-1 text-xs">
                            <CalendarClock className="h-3.5 w-3.5 text-teal-600" />
                            {formatDateTime(sub.ends_at, intlLocale)}
                            {sub.days_remaining != null ? (
                              <span className="text-zinc-400">
                                ({sub.days_remaining}d)
                              </span>
                            ) : null}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="p-3">
                        {pending ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                            <Clock className="h-3 w-3" />
                            {t("adminUsers.statusPending")}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-800">
                            <CheckCircle2 className="h-3 w-3" />
                            {t("adminUsers.statusActive")}
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        <div className="flex justify-end gap-1.5">
                          {pending ? (
                            <Button size="sm" onClick={() => openApprove(user)}>
                              <ShieldCheck className="h-3.5 w-3.5" />
                              {t("adminUsers.approve")}
                            </Button>
                          ) : (
                            <>
                              {user.role === "financial" ? (
                                <Button size="sm" variant="outline" onClick={() => openExtend(user)}>
                                  {t("adminUsers.extend")}
                                </Button>
                              ) : null}
                              {user.role !== "admin" ? (
                                <Button size="sm" variant="outline" onClick={() => void handleBlock(user)}>
                                  <Ban className="h-3.5 w-3.5" />
                                  {t("adminUsers.block")}
                                </Button>
                              ) : null}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={!!approveTarget}
        onClose={() => setApproveTarget(null)}
        title={t("adminUsers.approveTitle")}
      >
        {approveTarget ? (
          <div className="space-y-4">
            <p className="text-sm text-zinc-600">
              {approveTarget.full_name} · {approveTarget.email}
            </p>
            <Select
              label={t("adminUsers.fieldRole")}
              value={modalRole}
              onChange={(e) => setModalRole(e.target.value as "financial" | "user")}
            >
              <option value="financial">{en ? "Financial analyst" : "Analista financeiro"}</option>
              <option value="user">{en ? "Collaborator" : "Colaborador"}</option>
            </Select>
            {modalRole === "financial" ? (
              <>
                <Select
                  label={t("adminUsers.fieldPlan")}
                  value={modalPlanId}
                  onChange={(e) => setModalPlanId(e.target.value)}
                >
                  {plans.map((plan) => (
                    <option key={plan.id} value={plan.id}>
                      {plan.name}
                    </option>
                  ))}
                </Select>
                <div>
                  <p className="mb-2 text-sm font-medium text-zinc-700">{t("adminUsers.fieldDuration")}</p>
                  <div className="mb-2 flex flex-wrap gap-2">
                    {ACCESS_PRESETS.map((days) => (
                      <button
                        key={days}
                        type="button"
                        onClick={() => setModalDays(days)}
                        className={cn(
                          "rounded-lg border px-3 py-1 text-xs font-semibold",
                          modalDays === days
                            ? "border-teal-600 bg-teal-50 text-teal-800"
                            : "border-zinc-200 text-zinc-600",
                        )}
                      >
                        {days} {en ? "days" : "dias"}
                      </button>
                    ))}
                  </div>
                  <Input
                    type="number"
                    min={1}
                    max={3650}
                    label={t("adminUsers.fieldDaysCustom")}
                    value={modalDays}
                    onChange={(e) => setModalDays(Number(e.target.value) || 1)}
                  />
                </div>
              </>
            ) : (
              <p className="rounded-xl bg-zinc-50 p-3 text-xs text-zinc-600">
                {t("adminUsers.collaboratorHint")}
              </p>
            )}
            <Button className="w-full" loading={submitting} onClick={() => void handleApprove()}>
              {t("adminUsers.confirmApprove")}
            </Button>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={!!extendTarget}
        onClose={() => setExtendTarget(null)}
        title={t("adminUsers.extendTitle")}
      >
        {extendTarget ? (
          <div className="space-y-4">
            <p className="text-sm text-zinc-600">
              {extendTarget.full_name} · {extendTarget.email}
            </p>
            <Select
              label={t("adminUsers.fieldPlan")}
              value={modalPlanId}
              onChange={(e) => setModalPlanId(e.target.value)}
            >
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.name}
                </option>
              ))}
            </Select>
            <div className="flex flex-wrap gap-2">
              {ACCESS_PRESETS.map((days) => (
                <button
                  key={days}
                  type="button"
                  onClick={() => setModalDays(days)}
                  className={cn(
                    "rounded-lg border px-3 py-1 text-xs font-semibold",
                    modalDays === days
                      ? "border-teal-600 bg-teal-50 text-teal-800"
                      : "border-zinc-200 text-zinc-600",
                  )}
                >
                  {days} {en ? "days" : "dias"}
                </button>
              ))}
            </div>
            <Input
              type="number"
              min={1}
              max={3650}
              label={t("adminUsers.fieldDaysCustom")}
              value={modalDays}
              onChange={(e) => setModalDays(Number(e.target.value) || 1)}
            />
            <Button className="w-full" loading={submitting} onClick={() => void handleExtend()}>
              {t("adminUsers.confirmExtend")}
            </Button>
          </div>
        ) : null}
      </Modal>

      <RegisterUserModal
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onSuccess={() => void load()}
      />
    </>
  );
}
