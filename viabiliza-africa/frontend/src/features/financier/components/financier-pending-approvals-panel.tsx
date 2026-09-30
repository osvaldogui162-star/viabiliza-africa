"use client";

import { useState } from "react";
import { CheckCircle2, Clock, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { useI18n } from "@/components/providers/locale-provider";
import { financierApi } from "@/lib/api/financier-api";
import { ApiError } from "@/lib/api/http-client";
import type { FinancingListItem } from "@/lib/types/financier";
import { toast } from "sonner";

export function FinancierPendingApprovalsPanel({
  items,
  onDecided,
  compact,
}: {
  items: FinancingListItem[];
  onDecided?: () => void;
  compact?: boolean;
}) {
  const { t, formatMoney } = useI18n();
  const [selected, setSelected] = useState<FinancingListItem | null>(null);
  const [decision, setDecision] = useState<"approved" | "conditional" | "rejected">("approved");
  const [amount, setAmount] = useState("");
  const [disbursed, setDisbursed] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (items.length === 0) return null;

  function openItem(item: FinancingListItem) {
    setSelected(item);
    setDecision("approved");
    setAmount(item.approved_amount);
    setDisbursed("");
  }

  async function submitDecision() {
    if (!selected) return;
    setSubmitting(true);
    try {
      await financierApi.decideFinancing(selected.id, {
        decision,
        approved_amount: decision === "rejected" ? undefined : amount,
        disbursed_amount: disbursed || undefined,
      });
      toast.success(t("financier.decisionRecorded"));
      setSelected(null);
      onDecided?.();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <section
        className={
          compact
            ? "bank-dash-card bank-dash-rise space-y-3 p-4"
            : "bank-dash-card bank-dash-rise mb-4 space-y-4 p-5"
        }
      >
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-[var(--brand-gold)]" />
          <div>
            <h2 className="font-[family-name:var(--font-poppins)] text-base font-bold text-[var(--brand-navy)]">
              {t("financier.pendingApprovalsTitle")}
            </h2>
            <p className="text-xs text-[var(--muted)]">{t("financier.pendingApprovalsHint")}</p>
          </div>
          <span className="ml-auto rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-900">
            {items.length}
          </span>
        </div>
        <ul className="space-y-2">
          {items.slice(0, compact ? 4 : 10).map((item) => (
            <li
              key={item.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-100 bg-amber-50/60 px-3 py-2.5"
            >
              <div className="flex min-w-0 items-center gap-3">
                <BankLogoBadge bank={item.bank} size="sm" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-[var(--brand-navy)]">{item.project_name}</p>
                  <p className="text-xs text-[var(--muted)]">
                    {formatMoney(parseFloat(item.approved_amount), item.currency)} · {item.company_name ?? "—"}
                  </p>
                </div>
              </div>
              <Button size="sm" variant="outline" className="shrink-0" onClick={() => openItem(item)}>
                {t("financier.reviewRequest")}
              </Button>
            </li>
          ))}
        </ul>
      </section>

      <Modal
        open={selected !== null}
        onClose={() => setSelected(null)}
        title={t("financier.decideFinancingTitle")}
        description={selected ? selected.project_name : undefined}
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setSelected(null)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void submitDecision()} loading={submitting}>
              {t("financier.confirmDecision")}
            </Button>
          </div>
        }
      >
        {selected ? (
          <div className="space-y-4">
            <Select
              label={t("financier.decision")}
              value={decision}
              onChange={(e) => setDecision(e.target.value as typeof decision)}
            >
              <option value="approved">{t("financier.decisionApproved")}</option>
              <option value="conditional">{t("financier.decisionConditional")}</option>
              <option value="rejected">{t("financier.decisionRejected")}</option>
            </Select>
            {decision !== "rejected" ? (
              <>
                <Input label={t("financier.approvedAmount")} value={amount} onChange={(e) => setAmount(e.target.value)} />
                <Input
                  label={t("financier.disbursedAmount")}
                  value={disbursed}
                  onChange={(e) => setDisbursed(e.target.value)}
                  placeholder={t("common.optional")}
                />
              </>
            ) : (
              <p className="flex items-start gap-2 rounded-lg border border-rose-100 bg-rose-50 px-3 py-2 text-sm text-rose-900">
                <XCircle className="mt-0.5 h-4 w-4 shrink-0" />
                {t("financier.rejectHint")}
              </p>
            )}
            {decision !== "rejected" ? (
              <p className="flex items-start gap-2 text-xs text-[var(--muted)]">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--brand-teal)]" />
                {t("financier.approveActivatesMonitoring")}
              </p>
            ) : null}
          </div>
        ) : null}
      </Modal>
    </>
  );
}
