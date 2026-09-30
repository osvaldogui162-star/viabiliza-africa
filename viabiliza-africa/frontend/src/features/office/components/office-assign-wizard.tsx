"use client";

import { useEffect, useMemo, useState } from "react";
import { Check, ChevronLeft, ChevronRight, FolderKanban, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { useI18n } from "@/components/providers/locale-provider";
import { officeApi } from "@/lib/api/office-api";
import type { OfficeCapability, OfficeMember, OfficeProjectRow } from "@/lib/types/office";
import { cn } from "@/lib/utils/cn";

export type CapabilityPreset = "viewer" | "collaborator" | "assistant";

const CAP_KEYS = [
  "view_project",
  "edit_project",
  "manage_costs",
  "run_analysis",
  "manage_reports",
  "manage_collaboration",
  "manage_ingestion",
  "view_financing",
] as const;

export function buildCapabilities(preset: CapabilityPreset): Record<string, boolean> {
  const base = Object.fromEntries(CAP_KEYS.map((k) => [k, false])) as Record<string, boolean>;
  base.view_project = true;
  if (preset === "collaborator") base.manage_collaboration = true;
  if (preset === "assistant") {
    base.manage_collaboration = true;
    base.manage_costs = true;
    base.run_analysis = true;
    base.manage_reports = true;
    base.manage_ingestion = true;
    base.view_financing = true;
  }
  return base;
}

export type ProjectAssignmentPayload = {
  project_id: string;
  permission: "view" | "collaborate";
  capabilities: Record<string, boolean>;
};

type Step = 1 | 2 | 3;

export function OfficeAssignWizard({
  open,
  member,
  projects,
  catalog,
  initialProjectIds,
  onClose,
  onSubmit,
  submitting,
}: {
  open: boolean;
  member: OfficeMember | null;
  projects: OfficeProjectRow[];
  catalog: OfficeCapability[];
  initialProjectIds?: string[];
  onClose: () => void;
  onSubmit: (assignments: ProjectAssignmentPayload[]) => void | Promise<void>;
  submitting?: boolean;
}) {
  const { t } = useI18n();
  const [step, setStep] = useState<Step>(1);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [capPreset, setCapPreset] = useState<CapabilityPreset>("collaborator");
  const [capabilities, setCapabilities] = useState(buildCapabilities("collaborator"));
  const [perProject, setPerProject] = useState(false);
  const [perProjectCaps, setPerProjectCaps] = useState<Record<string, Record<string, boolean>>>({});

  useEffect(() => {
    if (!open || !member) return;
    setStep(1);
    const ids = initialProjectIds?.length ? [...initialProjectIds] : [];
    setSelectedIds(ids);
    setCapPreset("collaborator");
    setCapabilities(buildCapabilities("collaborator"));
    setPerProject(false);
    setPerProjectCaps({});

    if (ids.length === 0) return;

    void officeApi.memberAccess(member.id).then((access) => {
      if (!access.items.length) return;
      const capMap: Record<string, Record<string, boolean>> = {};
      for (const item of access.items) {
        capMap[item.project_id] = { ...item.effective_capabilities };
      }
      const distinct = new Set(
        access.items.map((i) => JSON.stringify(i.effective_capabilities)),
      );
      if (distinct.size > 1) {
        setPerProject(true);
        setPerProjectCaps(capMap);
      } else if (access.items[0]) {
        setCapabilities({ ...access.items[0].effective_capabilities });
      }
    });
  }, [open, member?.id, initialProjectIds]);

  const selectedProjects = useMemo(
    () => projects.filter((p) => selectedIds.includes(p.id)),
    [projects, selectedIds],
  );

  function applyPreset(preset: CapabilityPreset) {
    setCapPreset(preset);
    const caps = buildCapabilities(preset);
    setCapabilities(caps);
    if (perProject) {
      const next: Record<string, Record<string, boolean>> = {};
      for (const id of selectedIds) next[id] = { ...caps };
      setPerProjectCaps(next);
    }
  }

  function toggleProject(id: string) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  function buildAssignments(): ProjectAssignmentPayload[] {
    const permission = capabilities.manage_collaboration ? "collaborate" : "view";
    return selectedIds.map((project_id) => ({
      project_id,
      permission,
      capabilities: perProject ? (perProjectCaps[project_id] ?? capabilities) : capabilities,
    }));
  }

  const canNextStep1 = selectedIds.length > 0;
  const canConfirm = selectedIds.length > 0 && capabilities.view_project;

  return (
    <Modal
      open={open && member !== null}
      onClose={onClose}
      title={t("office.assignWizardTitle")}
      description={member?.full_name}
      footer={
        <div className="flex w-full flex-wrap items-center justify-between gap-2">
          <div className="flex gap-1">
            {[1, 2, 3].map((s) => (
              <span
                key={s}
                className={cn(
                  "h-1.5 w-8 rounded-full transition-colors",
                  step >= s ? "bg-[var(--brand-teal)]" : "bg-zinc-200",
                )}
              />
            ))}
          </div>
          <div className="flex gap-2">
            {step > 1 ? (
              <Button variant="outline" onClick={() => setStep((step - 1) as Step)}>
                <ChevronLeft className="mr-1 h-4 w-4" />
                {t("office.wizardBack")}
              </Button>
            ) : (
              <Button variant="outline" onClick={onClose}>
                {t("common.cancel")}
              </Button>
            )}
            {step === 1 ? (
              <Button disabled={!canNextStep1} onClick={() => setStep(2)}>
                {t("office.wizardNext")}
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            ) : null}
            {step === 2 ? (
              <Button disabled={!canConfirm} onClick={() => setStep(3)}>
                {t("office.wizardReview")}
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            ) : null}
            {step === 3 ? (
              <Button
                loading={submitting}
                disabled={!canConfirm}
                onClick={() => void onSubmit(buildAssignments())}
              >
                <Check className="mr-1 h-4 w-4" />
                {t("office.confirmAssign")}
              </Button>
            ) : null}
          </div>
        </div>
      }
    >
      {member ? (
        <div className="space-y-4">
          {step === 1 ? (
            <>
              <p className="text-sm text-[var(--muted)]">{t("office.wizardStep1Hint")}</p>
              <ul className="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-[var(--border)] p-1">
                {projects.map((p) => {
                  const checked = selectedIds.includes(p.id);
                  return (
                    <li key={p.id}>
                      <button
                        type="button"
                        onClick={() => toggleProject(p.id)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left text-sm transition",
                          checked
                            ? "bg-teal-50 ring-1 ring-teal-200"
                            : "hover:bg-zinc-50",
                        )}
                      >
                        <FolderKanban
                          className={cn("h-4 w-4 shrink-0", checked ? "text-teal-700" : "text-zinc-400")}
                        />
                        <span className="min-w-0 flex-1">
                          <span className="block font-semibold text-[var(--foreground)]">{p.name}</span>
                          <span className="block truncate text-xs text-[var(--muted)]">{p.company_name}</span>
                        </span>
                        <span
                          className={cn(
                            "flex h-5 w-5 shrink-0 items-center justify-center rounded border",
                            checked ? "border-teal-600 bg-teal-600 text-white" : "border-zinc-300",
                          )}
                        >
                          {checked ? <Check className="h-3 w-3" /> : null}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
              {projects.length === 0 ? (
                <p className="text-sm text-amber-800">{t("office.wizardNoProjects")}</p>
              ) : null}
            </>
          ) : null}

          {step === 2 ? (
            <>
              <div className="rounded-lg bg-teal-50/80 px-3 py-2 text-xs text-teal-900">
                {t("office.wizardSelectedCount", { count: selectedIds.length })}
              </div>
              <p className="text-sm text-[var(--muted)]">{t("office.wizardStep2Hint")}</p>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={perProject}
                  onChange={(e) => {
                    setPerProject(e.target.checked);
                    if (e.target.checked) {
                      const next: Record<string, Record<string, boolean>> = {};
                      for (const id of selectedIds) next[id] = { ...capabilities };
                      setPerProjectCaps(next);
                    }
                  }}
                />
                {t("office.perProjectPermissions")}
              </label>
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wider text-[var(--muted)]">
                  {t("office.presetPermissions")}
                </p>
                <div className="office-preset-row">
                  {(["viewer", "collaborator", "assistant"] as CapabilityPreset[]).map((p) => (
                    <button
                      key={p}
                      type="button"
                      className={cn("office-preset-btn", capPreset === p && "office-preset-btn--active")}
                      onClick={() => applyPreset(p)}
                    >
                      {t(`office.preset.${p}`)}
                    </button>
                  ))}
                </div>
              </div>
              {!perProject ? (
                <CapabilityGrid
                  catalog={catalog}
                  capabilities={capabilities}
                  onChange={setCapabilities}
                />
              ) : (
                <div className="max-h-56 space-y-3 overflow-y-auto">
                  {selectedProjects.map((p) => (
                    <div key={p.id} className="rounded-lg border border-[var(--border)] p-3">
                      <p className="mb-2 text-sm font-semibold">{p.name}</p>
                      <CapabilityGrid
                        catalog={catalog}
                        capabilities={perProjectCaps[p.id] ?? capabilities}
                        onChange={(caps) =>
                          setPerProjectCaps((prev) => ({ ...prev, [p.id]: caps }))
                        }
                      />
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : null}

          {step === 3 ? (
            <>
              <p className="text-sm text-[var(--muted)]">{t("office.wizardStep3Hint")}</p>
              <ul className="space-y-2">
                {buildAssignments().map((a) => {
                  const p = projects.find((x) => x.id === a.project_id);
                  const enabled = Object.entries(a.capabilities).filter(([, v]) => v).length;
                  return (
                    <li
                      key={a.project_id}
                      className="flex items-start gap-3 rounded-lg border border-[var(--border)] px-3 py-2"
                    >
                      <Shield className="mt-0.5 h-4 w-4 shrink-0 text-[var(--brand-teal)]" />
                      <div>
                        <p className="font-semibold text-sm">{p?.name ?? a.project_id}</p>
                        <p className="text-xs text-[var(--muted)]">
                          {a.permission} · {enabled} {t("office.permissionsActive")}
                        </p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </>
          ) : null}
        </div>
      ) : null}
    </Modal>
  );
}

function CapabilityGrid({
  catalog,
  capabilities,
  onChange,
}: {
  catalog: OfficeCapability[];
  capabilities: Record<string, boolean>;
  onChange: (c: Record<string, boolean>) => void;
}) {
  return (
    <div className="office-cap-grid">
      {catalog.map((c) => (
        <label key={c.key} className="office-cap-item">
          <input
            type="checkbox"
            checked={capabilities[c.key] ?? false}
            disabled={c.key === "view_project"}
            onChange={(e) => onChange({ ...capabilities, [c.key]: e.target.checked })}
          />
          <span>{c.label_pt}</span>
        </label>
      ))}
    </div>
  );
}
