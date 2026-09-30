"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Check, Pencil, RefreshCw, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Textarea } from "@/components/ui/textarea";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import { PLAN_FEATURE_LINES } from "@/lib/data/pricing-plans";
import type { AdminPlan, AdminPlanSubscriberStats } from "@/lib/types/admin";
import type { SubscriptionPlanFeatures } from "@/lib/types/subscription";
import { cn } from "@/lib/utils/cn";

type Props = {
  plans: AdminPlan[];
  subscriberStats?: AdminPlanSubscriberStats[];
  onChanged: () => void;
};

function planEmoji(plan: AdminPlan): string {
  const f = plan.features as SubscriptionPlanFeatures | undefined;
  return f?.emoji ?? plan.emoji ?? "";
}

function planTier(plan: AdminPlan): string {
  const f = plan.features as SubscriptionPlanFeatures | undefined;
  return f?.plan_tier ?? plan.plan_tier ?? "main";
}

export function AdminPlansPanel({ plans, subscriberStats = [], onChanged }: Props) {
  const { locale, formatMoney } = useI18n();
  const en = locale === "en";
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<AdminPlan | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [form, setForm] = useState({
    code: "",
    name: "",
    description: "",
    price_monthly: "0",
    price_yearly: "",
    currency: "USD",
    max_projects: "",
    max_users: "",
    max_monte_carlo_iterations: "1000",
    display_order: "0",
    is_active: true,
    featuresJson: "{}",
  });
  const [submitting, setSubmitting] = useState(false);

  const statsMap = useMemo(
    () => new Map(subscriberStats.map((s) => [s.plan_code, s])),
    [subscriberStats],
  );

  const mainPlans = plans.filter((p) => planTier(p) === "main");
  const specialPlans = plans.filter((p) => planTier(p) === "special");

  async function handleSyncCatalog() {
    setSyncing(true);
    try {
      const res = await adminApi.syncPlansCatalog();
      toast.success(
        en
          ? `Catalog synced: ${res.created} created, ${res.updated} updated`
          : `Catálogo sincronizado: ${res.created} criados, ${res.updated} actualizados`,
      );
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Sync failed" : "Falha na sincronização");
    } finally {
      setSyncing(false);
    }
  }

  function openEdit(plan: AdminPlan) {
    setEditing(plan);
    setForm({
      code: plan.code,
      name: plan.name,
      description: plan.description ?? "",
      price_monthly: plan.price_monthly,
      price_yearly: plan.price_yearly ?? "",
      currency: plan.currency,
      max_projects: plan.max_projects != null ? String(plan.max_projects) : "",
      max_users: plan.max_users != null ? String(plan.max_users) : "",
      max_monte_carlo_iterations: String(plan.max_monte_carlo_iterations),
      display_order: String(plan.display_order),
      is_active: plan.is_active,
      featuresJson: JSON.stringify(plan.features ?? {}, null, 2),
    });
    setOpen(true);
  }

  async function handleSave() {
    setSubmitting(true);
    try {
      let features = {};
      try {
        features = JSON.parse(form.featuresJson) as Record<string, unknown>;
      } catch {
        toast.error(en ? "Invalid features JSON" : "JSON de features inválido");
        setSubmitting(false);
        return;
      }
      const payload = {
        name: form.name,
        description: form.description || null,
        price_monthly: form.price_monthly,
        price_yearly: form.price_yearly || null,
        currency: form.currency,
        max_projects: form.max_projects ? Number(form.max_projects) : null,
        max_users: form.max_users ? Number(form.max_users) : null,
        max_monte_carlo_iterations: Number(form.max_monte_carlo_iterations),
        display_order: Number(form.display_order),
        is_active: form.is_active,
        features,
      };
      if (editing) {
        await adminApi.updatePlan(editing.id, payload);
        toast.success(en ? "Plan updated" : "Plano actualizado");
      }
      setOpen(false);
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Save failed" : "Falha ao guardar");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(plan: AdminPlan) {
    if (plan.code === "free") return;
    if (!confirm(en ? `Delete ${plan.name}?` : `Remover ${plan.name}?`)) return;
    try {
      await adminApi.deletePlan(plan.id);
      toast.success(en ? "Deleted" : "Removido");
      onChanged();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Delete failed" : "Falha");
    }
  }

  function renderPlanCard(plan: AdminPlan) {
    const emoji = planEmoji(plan);
    const popular = plan.features?.popular ?? plan.popular;
    const contactOnly = plan.features?.contact_only ?? plan.contact_only;
    const lines = PLAN_FEATURE_LINES[plan.code] ?? [];
    const stats = statsMap.get(plan.code);
    const f = plan.features as SubscriptionPlanFeatures | undefined;
    const aoaQ = f?.price_quarterly_aoa;
    const aoaS = f?.price_semiannual_aoa;
    const aoaY = f?.price_yearly_aoa ?? plan.price_yearly_aoa;

    return (
      <article
        key={plan.id}
        className={cn(
          "relative flex flex-col rounded-2xl border bg-white p-5 shadow-sm transition hover:shadow-md",
          popular ? "border-amber-300 bg-gradient-to-b from-amber-50/50 to-white" : "border-zinc-200",
          !plan.is_active && "opacity-60",
        )}
      >
        {popular ? (
          <span className="absolute -top-2.5 left-4 rounded-full bg-amber-500 px-2 py-0.5 text-[10px] font-bold text-white">
            ⭐ POPULAR
          </span>
        ) : null}

        <div className="mb-3">
          <h3 className="text-lg font-bold text-zinc-900">
            {emoji} {plan.name}
          </h3>
          <p className="text-xs text-zinc-500">{plan.code}</p>
          {plan.description ? <p className="mt-1 text-sm text-zinc-600">{plan.description}</p> : null}
        </div>

        <div className="mb-3 rounded-xl bg-teal-50 px-3 py-2 text-xs text-teal-900">
          {aoaQ != null ? <p><strong>T:</strong> {aoaQ.toLocaleString("pt-AO")} Kz</p> : null}
          {aoaS != null ? <p><strong>S:</strong> {aoaS.toLocaleString("pt-AO")} Kz</p> : null}
          {aoaY != null ? <p><strong>A:</strong> {aoaY.toLocaleString("pt-AO")} Kz</p> : null}
          {!aoaQ && !aoaS && !aoaY ? (
            <p className="text-sm font-bold text-teal-800">{en ? "Sync catalog for AOA prices" : "Sincronize o catálogo para preços AOA"}</p>
          ) : null}
          {contactOnly ? (
            <p className="mt-1 text-xs font-semibold text-amber-700">{en ? "Contact sales" : "Sob consulta"}</p>
          ) : null}
        </div>

        {stats ? (
          <p className="mb-2 text-xs font-semibold text-violet-700">
            {stats.active_subscribers} {en ? "active client(s)" : "cliente(s) activo(s)"}
          </p>
        ) : null}

        <ul className="mb-4 flex-1 space-y-1.5 text-xs text-zinc-600">
          {lines.slice(0, 5).map((line) => (
            <li key={line} className="flex gap-1.5">
              <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
              {line}
            </li>
          ))}
        </ul>

        <dl className="mb-3 grid grid-cols-3 gap-2 text-[10px]">
          <div><dt className="text-zinc-400">{en ? "Projects" : "Projectos"}</dt><dd className="font-bold">{plan.max_projects ?? "∞"}</dd></div>
          <div><dt className="text-zinc-400">{en ? "Users" : "Users"}</dt><dd className="font-bold">{plan.max_users ?? "∞"}</dd></div>
          <div><dt className="text-zinc-400">MC</dt><dd className="font-bold">{plan.max_monte_carlo_iterations.toLocaleString()}</dd></div>
        </dl>

        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="flex-1" onClick={() => openEdit(plan)}>
            <Pencil className="h-3.5 w-3.5" />
            {en ? "Edit" : "Editar"}
          </Button>
          {plan.code !== "free" ? (
            <Button size="sm" variant="outline" onClick={() => void handleDelete(plan)}>
              <Trash2 className="h-3.5 w-3.5 text-rose-600" />
            </Button>
          ) : null}
        </div>
      </article>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">{en ? "Plans catalog (/planos)" : "Catálogo de planos (/planos)"}</h2>
          <p className="text-sm text-zinc-500">
            {en ? "Same plans as the public pricing page — sync and edit here" : "Mesmos planos da página pública — sincronize e edite aqui"}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/planos" target="_blank">
            <Button variant="outline" size="sm">{en ? "View public page" : "Ver página pública"}</Button>
          </Link>
          <Button size="sm" onClick={() => void handleSyncCatalog()} disabled={syncing}>
            <RefreshCw className={cn("h-4 w-4", syncing && "animate-spin")} />
            {en ? "Sync catalog" : "Sincronizar catálogo"}
          </Button>
        </div>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-bold uppercase tracking-wide text-zinc-500">
          {en ? "Main plans" : "Planos principais"}
        </h3>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {mainPlans.map(renderPlanCard)}
        </div>
      </div>

      {specialPlans.length > 0 ? (
        <div>
          <h3 className="mb-3 flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-zinc-500">
            <Star className="h-4 w-4" />
            {en ? "Special plans" : "Planos especiais"}
          </h3>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {specialPlans.map(renderPlanCard)}
          </div>
        </div>
      ) : null}

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? `${en ? "Edit" : "Editar"} ${editing.name}` : en ? "Edit plan" : "Editar plano"}
        size="xl"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>{en ? "Cancel" : "Cancelar"}</Button>
            <Button onClick={() => void handleSave()} disabled={submitting}>{en ? "Save" : "Guardar"}</Button>
          </div>
        }
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <Input label={en ? "Name" : "Nome"} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label={en ? "Code" : "Código"} value={form.code} disabled />
          <Input label={en ? "Monthly USD" : "Mensal USD"} value={form.price_monthly} onChange={(e) => setForm({ ...form, price_monthly: e.target.value })} />
          <Input label={en ? "Yearly USD" : "Anual USD"} value={form.price_yearly} onChange={(e) => setForm({ ...form, price_yearly: e.target.value })} />
          <Input label={en ? "Max projects" : "Máx. projectos"} value={form.max_projects} onChange={(e) => setForm({ ...form, max_projects: e.target.value })} />
          <Input label={en ? "Max users" : "Máx. users"} value={form.max_users} onChange={(e) => setForm({ ...form, max_users: e.target.value })} />
          <Input label="Monte Carlo" value={form.max_monte_carlo_iterations} onChange={(e) => setForm({ ...form, max_monte_carlo_iterations: e.target.value })} />
          <Input label={en ? "Display order" : "Ordem"} value={form.display_order} onChange={(e) => setForm({ ...form, display_order: e.target.value })} />
          <div className="sm:col-span-2">
            <Textarea
              label={en ? "Description" : "Descrição"}
              rows={2}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div className="sm:col-span-2">
            <label className="mb-1 block text-xs font-semibold uppercase text-zinc-500">Features (JSON)</label>
            <textarea
              rows={8}
              value={form.featuresJson}
              onChange={(e) => setForm({ ...form, featuresJson: e.target.value })}
              className="w-full rounded-xl border border-zinc-200 p-3 font-mono text-xs"
            />
          </div>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
            {en ? "Active on /planos" : "Activo em /planos"}
          </label>
        </div>
      </Modal>
    </div>
  );
}
