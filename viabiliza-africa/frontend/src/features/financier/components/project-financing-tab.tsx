"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowRight, Clock, Landmark, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { BankInstitutionSelect } from "@/features/financier/components/bank-institution-select";
import { findAngolanBank } from "@/lib/data/angolan-banks";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";
import { financierApi } from "@/lib/api/financier-api";
import { projectsApi } from "@/lib/api/projects-api";
import { ApiError } from "@/lib/api/http-client";
import type { Project } from "@/lib/types/project";
import type { FinancingListItem } from "@/lib/types/financier";
import { PageLoader } from "@/components/ui/spinner";
import { toast } from "sonner";
import { cn } from "@/lib/utils/cn";

function workflowStep(active: boolean, done: boolean) {
  return cn(
    "flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold",
    done && "bg-[var(--brand-teal)] text-white",
    active && !done && "bg-amber-400 text-[var(--brand-navy)]",
    !active && !done && "bg-zinc-100 text-zinc-400",
  );
}

export function ProjectFinancingTab({ project }: { project: Project }) {
  const { user } = useAuth();
  const { t, formatMoney } = useI18n();
  const [items, setItems] = useState<FinancingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [bankCode, setBankCode] = useState(
    () => findAngolanBank(project.bank_code)?.code ?? "bfa",
  );
  const [approvedAmount, setApprovedAmount] = useState(project.investment_amount || "");
  const [adminDirect, setAdminDirect] = useState(false);
  const [adminDecision, setAdminDecision] = useState<"approved" | "conditional">("approved");
  const [disbursed, setDisbursed] = useState("");
  const [erpLabel, setErpLabel] = useState("");
  const [billingStatus, setBillingStatus] = useState<string | null>(null);
  const [syncEndpoint, setSyncEndpoint] = useState("/api/v1/terminal/billing/sync");
  const [syncHeader, setSyncHeader] = useState("X-Terminal-Api-Key");
  const [apiKeyHint, setApiKeyHint] = useState<string | null>(null);
  const [apiKeyModal, setApiKeyModal] = useState(false);
  const [apiKeyOnce, setApiKeyOnce] = useState<string | null>(null);

  const isAdmin = user?.role === "admin";
  const canViewFinancing =
    isAdmin ||
    project.is_owner ||
    project.my_access?.effective_capabilities?.view_financing === true;
  const canRegister =
    user?.role === "admin" || (user?.role === "financial" && project.is_owner);

  if (!canViewFinancing) {
    return (
      <p className="rounded-xl border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-500">
        {t("financier.noAccessFinancing")}
      </p>
    );
  }

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [res, billing] = await Promise.all([
        financierApi.listProjectFinancing(project.id),
        projectsApi.getBillingIntegration(project.id).catch(() => null),
      ]);
      setItems(res.items);
      setBillingStatus(billing?.integration?.connection_status ?? null);
      if (billing?.integration?.erp_label) setErpLabel(billing.integration.erp_label);
      setSyncEndpoint(billing?.sync_endpoint ?? billing?.integration?.sync_endpoint ?? syncEndpoint);
      setSyncHeader(billing?.sync_header ?? billing?.integration?.sync_header ?? syncHeader);
      setApiKeyHint(billing?.integration?.api_key_hint ?? null);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [project.id]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCreate() {
    setSubmitting(true);
    try {
      await financierApi.createProjectFinancing(project.id, {
        bank_code: bankCode,
        decision: isAdmin && adminDirect ? adminDecision : "pending",
        approved_amount: approvedAmount,
        currency: project.currency,
        disbursed_amount: isAdmin && adminDirect ? disbursed || undefined : undefined,
      });
      toast.success(
        isAdmin && adminDirect ? t("financier.registerSuccess") : t("financier.submitSuccess"),
      );
      setOpen(false);
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  }

  const statusLabel = (s: FinancingListItem["monitoring_status"]) => {
    if (s === "on_track") return t("financier.statusOnTrack");
    if (s === "attention") return t("financier.statusAttention");
    return t("financier.statusCritical");
  };

  const decisionLabel = (item: FinancingListItem) => {
    if (item.workflow_status === "pending_bank" || item.decision === "pending") {
      return t("financier.decisionPending");
    }
    if (item.decision === "approved") return t("financier.decisionApproved");
    if (item.decision === "conditional") return t("financier.decisionConditional");
    return t("financier.decisionRejected");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-teal-100 bg-gradient-to-r from-teal-50/80 to-white p-5">
        <div>
          <h2 className="flex items-center gap-2 font-[family-name:var(--font-poppins)] text-lg font-bold text-[#011636]">
            <Landmark className="h-5 w-5 text-[#00777f]" />
            {t("financier.projectTabTitle")}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-zinc-600">
            {canRegister ? t("financier.projectTabHint") : t("financier.readOnlyFinancing")}
          </p>
          <ol className="mt-4 flex flex-wrap items-center gap-2 text-xs font-medium text-zinc-600">
            <li className="flex items-center gap-2">
              <span className={workflowStep(true, items.some((i) => i.workflow_status !== "pending_bank"))}>1</span>
              {t("financier.stepSubmit")}
            </li>
            <span className="text-zinc-300">→</span>
            <li className="flex items-center gap-2">
              <span
                className={workflowStep(
                  items.some((i) => i.workflow_status === "pending_bank"),
                  items.some((i) => i.workflow_status === "active"),
                )}
              >
                2
              </span>
              {t("financier.stepBankReview")}
            </li>
            <span className="text-zinc-300">→</span>
            <li className="flex items-center gap-2">
              <span className={workflowStep(false, items.some((i) => i.workflow_status === "active"))}>3</span>
              {t("financier.stepMonitoring")}
            </li>
          </ol>
        </div>
        {canRegister ? (
          <Button onClick={() => setOpen(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            {t("financier.submitFinancing")}
          </Button>
        ) : null}
      </div>

      {loading ? (
        <PageLoader layout="embedded" message={t("common.loading")} />
      ) : items.length === 0 ? (
        <p className="rounded-xl border border-dashed border-zinc-200 px-4 py-8 text-center text-sm text-zinc-500">
          {t("financier.projectEmpty")}
        </p>
      ) : (
        <ul className="space-y-3">
          {items.map((item) => {
            const pending = item.workflow_status === "pending_bank";
            const active = item.workflow_status === "active";
            return (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-zinc-100 bg-white p-4 shadow-sm"
              >
                <div className="flex items-center gap-4">
                  <BankLogoBadge bank={item.bank} />
                  <div>
                    <p className="font-semibold text-zinc-900">{item.bank.label_pt}</p>
                    <p className="text-sm text-zinc-500">
                      {formatMoney(parseFloat(item.approved_amount), item.currency)} ·{" "}
                      {t("financier.decision")}: {decisionLabel(item)}
                    </p>
                    {pending ? (
                      <p className="mt-1 flex items-center gap-1 text-xs font-medium text-amber-700">
                        <Clock className="h-3.5 w-3.5" />
                        {t("financier.awaitingBank")}
                      </p>
                    ) : null}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {active ? (
                    <FinancierStatusPill status={item.monitoring_status} label={statusLabel(item.monitoring_status)} />
                  ) : null}
                  {active || pending ? (
                    <Link
                      href={`/financiador/${item.id}`}
                      className="inline-flex items-center gap-1 text-sm font-semibold text-[#00777f] hover:underline"
                    >
                      {pending ? t("financier.viewRequest") : t("financier.viewCharts")}
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  ) : null}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {canRegister ? (
        <section className="mt-8 rounded-2xl border border-[var(--border)] bg-[var(--accent-soft)]/40 p-5">
          <h3 className="text-sm font-bold text-[var(--brand-navy)]">{t("terminal.integrationTitle")}</h3>
          <p className="mt-1 text-xs text-[var(--muted)]">{t("terminal.integrationSubtitle")}</p>
          <div className="mt-4 flex flex-wrap items-end gap-3">
            <Input
              label="ERP / Facturação"
              value={erpLabel}
              onChange={(e) => setErpLabel(e.target.value)}
              placeholder="Ex.: Primavera, SAP, PHC"
              className="min-w-[220px] flex-1"
            />
            <Button
              variant="outline"
              onClick={() =>
                void projectsApi
                  .configureBillingIntegration(project.id, erpLabel)
                  .then((res) => {
                    if (res.api_key) {
                      setApiKeyOnce(res.api_key);
                      setApiKeyModal(true);
                    }
                    toast.success(t("financier.submitSuccess"));
                    void load();
                  })
                  .catch((e) => toast.error(e instanceof ApiError ? e.message : t("common.error")))
              }
            >
              {t("terminal.navIntegration")}
            </Button>
            <Button
              variant="outline"
              onClick={() =>
                void projectsApi
                  .regenerateBillingApiKey(project.id)
                  .then((res) => {
                    setApiKeyOnce(res.api_key);
                    setApiKeyModal(true);
                    void load();
                  })
                  .catch((e) => toast.error(e instanceof ApiError ? e.message : t("common.error")))
              }
            >
              {t("terminal.regenerateApiKey")}
            </Button>
            <Button
              onClick={() =>
                void projectsApi
                  .syncBillingIntegration(project.id, { source: "manual_demo" })
                  .then(() => {
                    toast.success(t("financier.submitSuccess"));
                    void load();
                  })
                  .catch((e) => toast.error(e instanceof ApiError ? e.message : t("common.error")))
              }
            >
              {t("terminal.syncTest")}
            </Button>
          </div>
          <div className="mt-3 rounded-lg border border-[var(--border)] bg-white/80 px-3 py-2 text-xs text-[var(--muted)]">
            <p>
              <span className="font-semibold text-[var(--brand-navy)]">POST</span> {syncEndpoint}
            </p>
            <p className="mt-1">
              {syncHeader}: {apiKeyHint ?? t("terminal.apiKeyAfterConfigure")}
            </p>
          </div>
          {billingStatus ? (
            <p className="mt-2 text-xs font-semibold text-[var(--brand-teal)]">
              {t("terminal.billingConnected")}: {billingStatus}
            </p>
          ) : null}
        </section>
      ) : null}

      <Modal
        open={apiKeyModal}
        onClose={() => {
          setApiKeyModal(false);
          setApiKeyOnce(null);
        }}
        title={t("terminal.apiKeyTitle")}
        description={t("terminal.apiKeyShowOnce")}
        footer={
          <div className="flex justify-end gap-2">
            <Button
              onClick={() => {
                if (apiKeyOnce) void navigator.clipboard.writeText(apiKeyOnce);
                toast.success(t("terminal.apiKeyCopied"));
              }}
            >
              {t("terminal.copyApiKey")}
            </Button>
            <Button variant="outline" onClick={() => setApiKeyModal(false)}>
              {t("common.close")}
            </Button>
          </div>
        }
      >
        <code className="block break-all rounded-lg bg-zinc-900 p-3 text-xs text-emerald-300">{apiKeyOnce}</code>
        <p className="mt-3 text-xs text-[var(--muted)]">{t("terminal.apiKeyErpHint")}</p>
      </Modal>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={t("financier.submitFinancing")}
        description={t("financier.submitModalHint")}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void handleCreate()} loading={submitting}>
              {t("common.confirm")}
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <BankInstitutionSelect
            label={t("reports.bank")}
            value={bankCode}
            onChange={setBankCode}
            hint={t("financier.bankFromProjectHint")}
          />
          <Input
            label={t("financier.requestedAmount")}
            value={approvedAmount}
            onChange={(e) => setApprovedAmount(e.target.value)}
          />
          {isAdmin ? (
            <>
              <label className="flex items-center gap-2 text-sm text-zinc-700">
                <input
                  type="checkbox"
                  checked={adminDirect}
                  onChange={(e) => setAdminDirect(e.target.checked)}
                  className="rounded border-zinc-300"
                />
                {t("financier.adminDirectApproval")}
              </label>
              {adminDirect ? (
                <>
                  <Select
                    label={t("financier.decision")}
                    value={adminDecision}
                    onChange={(e) => setAdminDecision(e.target.value as "approved" | "conditional")}
                  >
                    <option value="approved">{t("financier.decisionApproved")}</option>
                    <option value="conditional">{t("financier.decisionConditional")}</option>
                  </Select>
                  <Input
                    label={t("financier.disbursedAmount")}
                    value={disbursed}
                    onChange={(e) => setDisbursed(e.target.value)}
                    placeholder={t("common.optional")}
                  />
                </>
              ) : null}
            </>
          ) : (
            <p className="rounded-lg border border-teal-100 bg-teal-50/80 px-3 py-2 text-sm text-teal-900">
              {t("financier.analystSubmitNote")}
            </p>
          )}
        </div>
      </Modal>
    </div>
  );
}
