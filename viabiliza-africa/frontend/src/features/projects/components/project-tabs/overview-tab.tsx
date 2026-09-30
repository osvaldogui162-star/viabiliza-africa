"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import {
  Briefcase,
  CalendarDays,
  CheckCircle2,
  Globe2,
  Landmark,
  MapPin,
  Percent,
  Phone,
  Share2,
  Trash2,
  User,
  UserPlus,
  Wallet,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Select } from "@/components/ui/select";
import { ProjectInfoTile } from "@/features/projects/components/project-info-tile";
import { ProjectWizard } from "@/features/projects/components/project-wizard";
import { SectorProfilePanel } from "@/features/projects/components/sector-profile-panel";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi } from "@/lib/api/projects-api";
import type { MetadataOption, Project, ProjectShare } from "@/lib/types/project";

const TILE_ACCENTS = ["#2dd4bf", "#34d399", "#4ade80", "#14b8a6", "#22d3ee", "#a3e635"];

export function OverviewTab({
  project,
  onUpdate,
}: {
  project: Project;
  onUpdate: (p: Project) => void;
}) {
  const { user } = useAuth();
  const { t, locale, formatMoney } = useI18n();
  const [editing, setEditing] = useState(false);
  const [shares, setShares] = useState<ProjectShare[]>([]);
  const [banks, setBanks] = useState<MetadataOption[]>([]);
  const [shareModal, setShareModal] = useState(false);
  const [shareEmail, setShareEmail] = useState("");
  const [sharePermission, setSharePermission] = useState("view");
  const [sharing, setSharing] = useState(false);

  const canEdit = user?.role === "admin" || (user?.role === "financial" && project.is_owner);

  const selectedBank = useMemo(
    () => banks.find((bank) => bank.value === project.bank_code) ?? null,
    [banks, project.bank_code],
  );

  useEffect(() => {
    void projectsApi.listShares(project.id).then((r) => setShares(r.items));
  }, [project.id]);

  useEffect(() => {
    void projectsApi
      .metadata()
      .then((meta) => setBanks(meta.banks ?? []))
      .catch(() => setBanks([]));
  }, []);

  async function handleShare() {
    setSharing(true);
    try {
      const result = await projectsApi.share(project.id, shareEmail, sharePermission);
      if ("pending_invite" in result && result.pending_invite) {
        toast.success(result.message ?? t("overview.shareInviteSent"));
      } else {
        toast.success(t("overview.shareSuccess"));
      }
      setShareModal(false);
      setShareEmail("");
      const updated = await projectsApi.listShares(project.id);
      setShares(updated.items);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("overview.shareError"));
    } finally {
      setSharing(false);
    }
  }

  async function handleRemoveShare(userId: string) {
    try {
      await projectsApi.removeShare(project.id, userId);
      toast.success(t("overview.removeShareSuccess"));
      setShares((prev) => prev.filter((s) => s.user_id !== userId));
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("overview.removeShareError"));
    }
  }

  if (editing) {
    return (
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-teal-700">
              {t("overview.editProject")}
            </p>
            <h2 className="text-xl font-bold tracking-tight text-zinc-900">{project.name}</h2>
          </div>
          <Button variant="outline" size="sm" onClick={() => setEditing(false)}>
            {t("common.cancel")}
          </Button>
        </div>
        <div className="va-project-panel rounded-2xl border border-zinc-200/80 bg-white p-4 sm:p-6">
          <ProjectWizard
            project={project}
            onSuccess={(p) => {
              onUpdate(p);
              setEditing(false);
            }}
          />
        </div>
      </div>
    );
  }

  const infoTiles = [
    {
      label: t("common.status"),
      value: <Badge variant="success">{project.status_label}</Badge>,
      icon: <CheckCircle2 className="h-4 w-4" />,
    },
    {
      label: locale === "en" ? "Sector" : "Sector",
      value: project.sector_label,
      icon: <Briefcase className="h-4 w-4" />,
    },
    {
      label: locale === "en" ? "Country" : "País",
      value: project.country_label,
      icon: <Globe2 className="h-4 w-4" />,
    },
    {
      label: t("overview.investment"),
      value: formatMoney(project.investment_amount, project.currency),
      icon: <Wallet className="h-4 w-4" />,
    },
    {
      label: t("overview.horizon"),
      value: `${project.project_horizon_years} ${t("common.years")}`,
      icon: <CalendarDays className="h-4 w-4" />,
    },
    {
      label: t("overview.discountRate"),
      value: project.discount_rate ? `${project.discount_rate}%` : "—",
      icon: <Percent className="h-4 w-4" />,
    },
    {
      label: locale === "en" ? "Approved budget" : "Orçamento aprovado",
      value: project.has_approved_budget ? t("common.yes") : t("common.no"),
      icon: <CheckCircle2 className="h-4 w-4" />,
    },
    ...(project.owner
      ? [
          {
            label: locale === "en" ? "Owner" : "Proprietário",
            value: project.owner.full_name,
            icon: <User className="h-4 w-4" />,
          },
        ]
      : []),
    ...(project.rep_full_name
      ? [
          {
            label: locale === "en" ? "Representative" : "Representante",
            value: project.rep_full_name,
            icon: <User className="h-4 w-4" />,
          },
        ]
      : []),
    ...(project.company_province_label
      ? [
          {
            label: locale === "en" ? "Location" : "Localização",
            value: `${project.company_municipality_label ?? ""}, ${project.company_province_label}`,
            icon: <MapPin className="h-4 w-4" />,
          },
        ]
      : []),
    ...(project.company_phone
      ? [
          {
            label: locale === "en" ? "Company phone" : "Tel. empresa",
            value: project.company_phone,
            icon: <Phone className="h-4 w-4" />,
          },
        ]
      : []),
  ];

  return (
    <div className="space-y-6">
      {project.is_shared && !project.is_owner ? (
        <div className="flex items-start gap-3 rounded-xl border border-teal-200/80 bg-gradient-to-r from-teal-50 to-emerald-50/60 px-4 py-3.5">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-teal-700 shadow-sm">
            <Share2 className="h-4 w-4" />
          </span>
          <p className="text-sm leading-relaxed text-teal-950">
            {t("overview.sharedBanner")}
            {project.owner ? (
              <>
                {" "}
                — <strong>{project.owner.full_name}</strong> ({project.owner.email})
              </>
            ) : null}
          </p>
        </div>
      ) : null}

      <Card variant="panel">
        <CardHeader
          eyebrow={t("projectTabs.overview")}
          title={project.name}
          description={project.company_name}
          action={
            canEdit ? (
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                {t("common.edit")}
              </Button>
            ) : null
          }
        />

        {project.bank_code || selectedBank ? (
          <div className="va-project-bank-card mb-6 overflow-hidden rounded-xl border border-teal-100/80 bg-gradient-to-br from-teal-50/90 via-white to-emerald-50/50 p-4 sm:p-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-teal-100 bg-white text-teal-700 shadow-sm">
                  <Landmark className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-teal-700">
                    {t("overview.bank")}
                  </p>
                  <p className="mt-1 text-base font-bold text-zinc-900">
                    {selectedBank?.label ?? project.bank_code?.toUpperCase() ?? "—"}
                  </p>
                  {project.bank_branch ? (
                    <p className="mt-0.5 text-xs text-zinc-500">{project.bank_branch}</p>
                  ) : null}
                  {project.financing_type_label ? (
                    <p className="mt-0.5 text-xs text-zinc-500">{project.financing_type_label}</p>
                  ) : null}
                </div>
              </div>
              {selectedBank?.logo ? (
                <div className="flex h-16 w-full items-center justify-center rounded-xl border border-white bg-white px-5 shadow-sm sm:w-44">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={selectedBank.logo}
                    alt={selectedBank.label}
                    className="max-h-12 max-w-full object-contain"
                    onError={(event) => {
                      event.currentTarget.style.display = "none";
                    }}
                  />
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {infoTiles.map((tile, index) => (
            <ProjectInfoTile
              key={tile.label}
              label={tile.label}
              value={tile.value}
              icon={tile.icon}
              accent={TILE_ACCENTS[index % TILE_ACCENTS.length]}
            />
          ))}
        </div>

        {project.description ? (
          <div className="mt-6 rounded-xl border border-zinc-100 bg-zinc-50/60 px-4 py-3.5">
            <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
              {locale === "en" ? "Description" : "Descrição"}
            </p>
            <p className="mt-2 text-sm leading-relaxed text-zinc-700">{project.description}</p>
          </div>
        ) : null}
      </Card>

      <SectorProfilePanel projectId={project.id} />

      {canEdit ? (
        <Card variant="panel">
          <CardHeader
            eyebrow={t("projectTabs.collaboration")}
            title={t("overview.collaborators")}
            description={
              shares.length === 0
                ? t("overview.noCollaborators")
                : `${shares.length} ${locale === "en" ? "member(s)" : "membro(s)"}`
            }
            action={
              <Button size="sm" onClick={() => setShareModal(true)}>
                <UserPlus className="h-4 w-4" />
                {t("overview.share")}
              </Button>
            }
          />
          {shares.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-200 bg-zinc-50/50 px-6 py-10 text-center">
              <UserPlus className="mb-2 h-8 w-8 text-zinc-300" />
              <p className="text-sm text-zinc-500">{t("overview.noCollaborators")}</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {shares.map((share) => (
                <li
                  key={share.id}
                  className="flex items-center justify-between gap-3 rounded-xl border border-zinc-100 bg-gradient-to-r from-white to-zinc-50/80 px-4 py-3 transition hover:border-teal-100 hover:shadow-sm"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-teal-100 text-sm font-bold text-teal-800">
                      {share.user_full_name.charAt(0).toUpperCase()}
                    </span>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-zinc-900">{share.user_full_name}</p>
                      <p className="truncate text-xs text-zinc-500">{share.user_email}</p>
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Badge>
                      {share.permission === "collaborate"
                        ? t("overview.canEdit")
                        : t("overview.viewOnly")}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => void handleRemoveShare(share.user_id)}
                      aria-label={t("common.delete")}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      ) : null}

      <Modal open={shareModal} onClose={() => setShareModal(false)} title={t("overview.shareModal")}>
        <div className="space-y-4">
          <Input
            label={t("overview.shareEmail")}
            type="email"
            value={shareEmail}
            onChange={(e) => setShareEmail(e.target.value)}
            placeholder="user@company.com"
          />
          <Select
            label={t("overview.permission")}
            value={sharePermission}
            onChange={(e) => setSharePermission(e.target.value)}
          >
            <option value="view">{t("overview.viewOnly")}</option>
            <option value="collaborate">{t("overview.canEdit")}</option>
          </Select>
          <Button onClick={() => void handleShare()} loading={sharing} disabled={!shareEmail}>
            {t("overview.share")}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
