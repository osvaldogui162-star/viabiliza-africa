"use client";

import { useEffect, useState } from "react";
import { Layers, Leaf, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardHeader } from "@/components/ui/card";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { projectsApi } from "@/lib/api/projects-api";
import type { SectorProfile, UseCaseStatus } from "@/lib/types/sector-profile";

function statusVariant(status: UseCaseStatus): "success" | "warning" | "default" {
  if (status === "automated") return "success";
  if (status === "partial") return "warning";
  return "default";
}

function statusLabel(status: UseCaseStatus, t: (key: string) => string): string {
  if (status === "automated") return t("sectorProfile.statusAutomated");
  if (status === "partial") return t("sectorProfile.statusPartial");
  return t("sectorProfile.statusPlanned");
}

export function SectorProfilePanel({ projectId }: { projectId: string }) {
  const { t, locale } = useI18n();
  const [profile, setProfile] = useState<SectorProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);
    void projectsApi
      .getSectorProfile(projectId, locale === "en" ? "en" : "pt")
      .then((data) => {
        if (!cancelled) setProfile(data);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, locale]);

  if (loading) {
    return (
      <Card>
        <PageLoader message={t("sectorProfile.loading")} layout="embedded" />
      </Card>
    );
  }

  if (error || !profile) {
    return null;
  }

  const { primary_module: primary, esg_module: esg, coverage } = profile;

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden border-indigo-100">
        <div className="border-b border-indigo-100 bg-gradient-to-r from-indigo-50/80 via-white to-violet-50/60 px-5 py-4">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-indigo-700 shadow-sm ring-1 ring-indigo-100">
              <Layers className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-indigo-700">
                {t("sectorProfile.moduleLabel")}
              </p>
              <h3 className="mt-1 text-base font-semibold text-zinc-900">{primary.name}</h3>
              <p className="mt-1 text-sm text-zinc-600">{primary.description}</p>
            </div>
          </div>
        </div>

        <div className="space-y-5 p-5">
          <div className="grid gap-3 sm:grid-cols-3">
            <CoverageStat label={t("sectorProfile.automated")} value={coverage.automated} tone="emerald" />
            <CoverageStat label={t("sectorProfile.partial")} value={coverage.partial} tone="amber" />
            <CoverageStat label={t("sectorProfile.planned")} value={coverage.planned} tone="zinc" />
          </div>

          {primary.kpis.length > 0 ? (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                {t("sectorProfile.kpis")}
              </p>
              <div className="flex flex-wrap gap-2">
                {primary.kpis.map((kpi) => (
                  <Badge key={kpi} variant="default">
                    {kpi}
                  </Badge>
                ))}
              </div>
            </div>
          ) : null}

          {profile.recommended_certifications.length > 0 ? (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                {t("sectorProfile.certifications")}
              </p>
              <div className="flex flex-wrap gap-2">
                {profile.recommended_certifications.map((cert) => (
                  <Badge key={cert} variant="success">
                    {cert}
                  </Badge>
                ))}
              </div>
            </div>
          ) : null}

          <UseCaseList title={t("sectorProfile.useCases")} useCases={primary.use_cases} t={t} />

          {profile.benchmarks.length > 0 ? (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
                {t("sectorProfile.benchmarks")}
              </p>
              <ul className="grid gap-2 sm:grid-cols-2">
                {profile.benchmarks.slice(0, 6).map((b) => (
                  <li
                    key={b.key}
                    className="rounded-lg border border-zinc-100 bg-zinc-50/80 px-3 py-2 text-sm"
                  >
                    <p className="text-zinc-600">{b.label}</p>
                    <p className="font-medium text-zinc-900">
                      {b.value} {b.unit}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </Card>

      <Card className="border-emerald-100">
        <div className="mb-4 flex items-start gap-2">
          <Leaf className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
          <div>
            <h2 className="text-lg font-semibold text-zinc-900">{esg.name}</h2>
            <p className="mt-1 text-sm text-zinc-500">{esg.description}</p>
          </div>
        </div>
        <div className="px-0 pb-0">
          <UseCaseList title={t("sectorProfile.esgUseCases")} useCases={esg.use_cases} t={t} compact />
        </div>
      </Card>

      {profile.related_modules.length > 0 ? (
        <Card>
          <div className="mb-4 flex items-start gap-2">
            <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-violet-600" />
            <h2 className="text-lg font-semibold text-zinc-900">{t("sectorProfile.relatedModules")}</h2>
          </div>
          <ul className="divide-y">
            {profile.related_modules.map((mod) => (
              <li key={mod.code} className="py-3 text-sm">
                <p className="font-medium text-zinc-900">{mod.name}</p>
                <p className="text-zinc-500">{mod.description}</p>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}

function CoverageStat({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
  tone: "emerald" | "amber" | "zinc";
}) {
  const colors = {
    emerald: "border-emerald-100 bg-emerald-50 text-emerald-800",
    amber: "border-amber-100 bg-amber-50 text-amber-800",
    zinc: "border-zinc-100 bg-zinc-50 text-zinc-700",
  };
  return (
    <div className={`rounded-xl border px-4 py-3 ${colors[tone]}`}>
      <p className="text-xs uppercase tracking-wide opacity-80">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function UseCaseList({
  title,
  useCases,
  t,
  compact = false,
}: {
  title: string;
  useCases: SectorProfile["primary_module"]["use_cases"];
  t: (key: string) => string;
  compact?: boolean;
}) {
  const visible = compact ? useCases.slice(0, 4) : useCases;
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">{title}</p>
      <ul className="space-y-2">
        {visible.map((uc) => (
          <li
            key={uc.code}
            className="flex flex-col gap-1 rounded-lg border border-zinc-100 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p className="text-xs font-mono text-zinc-400">{uc.code}</p>
              <p className="text-sm font-medium text-zinc-800">{uc.title}</p>
            </div>
            <Badge variant={statusVariant(uc.status)}>{statusLabel(uc.status, t)}</Badge>
          </li>
        ))}
      </ul>
    </div>
  );
}
