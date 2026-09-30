"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  FolderKanban,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  Share2,
  UserPlus,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { OfficeAssignWizard, type ProjectAssignmentPayload } from "@/features/office/components/office-assign-wizard";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { officeApi } from "@/lib/api/office-api";
import { ApiError } from "@/lib/api/http-client";
import type { OfficeDashboard, OfficeMember, OfficeProjectRow } from "@/lib/types/office";
import { PageLoader } from "@/components/ui/spinner";
import { useInView } from "@/hooks/use-in-view";
import { cn } from "@/lib/utils/cn";
import { toast } from "sonner";

type Tab = "team" | "projects";

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");
}

export function OfficeView({ ownerId }: { ownerId?: string }) {
  const { user } = useAuth();
  const { t } = useI18n();
  const { ref: shellRef, inView } = useInView(0.06);
  const [dashboard, setDashboard] = useState<OfficeDashboard | null>(null);
  const [members, setMembers] = useState<OfficeMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("team");
  const [projectQuery, setProjectQuery] = useState("");
  const [memberModal, setMemberModal] = useState(false);
  const [editMember, setEditMember] = useState<OfficeMember | null>(null);
  const [assignModal, setAssignModal] = useState<OfficeMember | null>(null);
  const [assignInitialProjects, setAssignInitialProjects] = useState<string[] | undefined>();
  const [assignSubmitting, setAssignSubmitting] = useState(false);
  const [form, setForm] = useState({ email: "", full_name: "", job_title: "Colaborador", notes: "" });

  const canManage = user?.role === "admin" || user?.role === "financial";

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [dash, mem] = await Promise.all([
        officeApi.dashboard(ownerId),
        officeApi.members(ownerId),
      ]);
      setDashboard(dash);
      setMembers(mem.items);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [ownerId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  const catalog = useMemo(() => dashboard?.capability_catalog ?? [], [dashboard]);

  const filteredProjects = useMemo(() => {
    if (!dashboard) return [];
    const q = projectQuery.trim().toLowerCase();
    if (!q) return dashboard.projects;
    return dashboard.projects.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.company_name.toLowerCase().includes(q) ||
        p.status.toLowerCase().includes(q),
    );
  }, [dashboard, projectQuery]);

  function openAssign(member: OfficeMember, initialProjects?: string[]) {
    setAssignInitialProjects(initialProjects ?? member.project_ids);
    setAssignModal(member);
  }

  async function createMember() {
    try {
      const created = await officeApi.createMember(form, ownerId);
      toast.success(t("office.memberCreated"));
      setMemberModal(false);
      setForm({ email: "", full_name: "", job_title: "Colaborador", notes: "" });
      await load();
      openAssign(created, []);
      toast.message(t("office.wizardAfterCreate"));
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    }
  }

  async function saveMemberEdit() {
    if (!editMember) return;
    try {
      await officeApi.updateMember(editMember.id, {
        full_name: form.full_name,
        job_title: form.job_title,
        notes: form.notes || null,
      });
      toast.success(t("office.memberUpdated"));
      setEditMember(null);
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    }
  }

  async function submitAssignments(assignments: ProjectAssignmentPayload[]) {
    if (!assignModal) return;
    setAssignSubmitting(true);
    try {
      await officeApi.assignProjects(assignModal.id, { assignments });
      toast.success(t("office.assignSuccess"));
      setAssignModal(null);
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setAssignSubmitting(false);
    }
  }

  async function archiveMember(member: OfficeMember) {
    try {
      await officeApi.archiveMember(member.id);
      toast.success(t("office.memberArchived"));
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    }
  }

  if (loading && !dashboard) {
    return <PageLoader layout="section" message={t("common.loading")} />;
  }

  const stats = dashboard?.stats;

  return (
    <div ref={shellRef} className={cn("office-shell", inView && "office-shell--ready")}>
      <header className="office-hero office-hero--compact office-rise" style={{ animationDelay: "40ms" }}>
        <div className="office-hero-inner">
          <div className="min-w-0">
            <h1 className="font-[family-name:var(--font-poppins)] text-lg font-bold tracking-tight text-white sm:text-xl">
              {t("office.title")}
            </h1>
            {stats ? (
              <p className="mt-0.5 text-xs text-white/75">
                {t("office.statsBrief", {
                  projects: stats.projects_count,
                  members: stats.members_count,
                  shares: stats.shared_slots,
                })}
              </p>
            ) : null}
          </div>
          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-8 border-white/25 bg-white/10 px-2.5 text-white hover:bg-white/20 sm:px-3"
              onClick={() => void load()}
              aria-label={t("office.refresh")}
            >
              <RefreshCw className="h-4 w-4 sm:mr-1.5" />
              <span className="hidden sm:inline">{t("office.refresh")}</span>
            </Button>
            {canManage ? (
              <Button
                size="sm"
                className="h-8 bg-white px-2.5 text-[#011636] hover:bg-teal-50 sm:px-3"
                aria-label={t("office.addProfessional")}
                onClick={() => {
                  setForm({ email: "", full_name: "", job_title: "Colaborador", notes: "" });
                  setMemberModal(true);
                }}
              >
                <UserPlus className="h-4 w-4 sm:mr-1.5" />
                <span className="hidden sm:inline">{t("office.addProfessional")}</span>
              </Button>
            ) : null}
          </div>
        </div>
      </header>

      <div className="office-workspace">
        <nav className="office-rail office-rise" style={{ animationDelay: "100ms" }} aria-label={t("office.navLabel")}>
          <button
            type="button"
            className={cn("office-rail-link mb-1", tab === "team" && "office-rail-link--active")}
            onClick={() => setTab("team")}
          >
            <Users className="h-4 w-4 shrink-0" />
            {t("office.tabTeam")}
          </button>
          <button
            type="button"
            className={cn("office-rail-link", tab === "projects" && "office-rail-link--active")}
            onClick={() => setTab("projects")}
          >
            <FolderKanban className="h-4 w-4 shrink-0" />
            {t("office.tabProjects")}
          </button>
          <div className="mt-4 border-t border-[var(--border)] pt-3">
            <Link href="/projects/new" className="office-rail-link text-[var(--brand-teal)]">
              <Plus className="h-4 w-4" />
              {t("office.newProject")}
            </Link>
          </div>
        </nav>

        <div className="office-panel office-rise min-w-0" style={{ animationDelay: "160ms" }}>
          {tab === "team" ? (
            <>
              <div className="office-panel-head">
                <div>
                  <h2 className="font-[family-name:var(--font-poppins)] text-base font-bold text-[var(--brand-navy)]">
                    {t("office.teamTitle")}
                  </h2>
                  <p className="text-xs text-[var(--muted)]">{t("office.teamHint")}</p>
                </div>
              </div>
              {members.length === 0 ? (
                <OfficeEmpty
                  icon={Users}
                  title={t("office.emptyTeamTitle")}
                  hint={t("office.emptyTeam")}
                  action={
                    canManage ? (
                      <Button onClick={() => setMemberModal(true)} className="gap-2">
                        <Plus className="h-4 w-4" />
                        {t("office.addProfessional")}
                      </Button>
                    ) : null
                  }
                />
              ) : (
                <div className="office-table-wrap">
                  <table className="office-table">
                    <thead>
                      <tr>
                        <th>{t("office.colProfessional")}</th>
                        <th>{t("office.fieldRole")}</th>
                        <th>{t("office.projectsLinked")}</th>
                        <th>{t("office.colStatus")}</th>
                        <th className="text-right">{t("office.colActions")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {members.map((m) => (
                        <tr key={m.id}>
                          <td>
                            <div className="flex items-center gap-3">
                              <span className="office-avatar">{initials(m.full_name)}</span>
                              <div className="min-w-0">
                                <p className="font-semibold text-[var(--foreground)]">{m.full_name}</p>
                                <p className="truncate text-xs text-[var(--muted)]">{m.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="text-[var(--foreground)]">{m.job_title}</td>
                          <td>
                            <span className="font-semibold tabular-nums text-[var(--brand-teal)]">
                              {m.project_ids.length}
                            </span>
                          </td>
                          <td>
                            {m.user_id ? (
                              <span className="office-badge office-badge--active">{t("office.statusActive")}</span>
                            ) : (
                              <span className="office-badge office-badge--pending">{t("office.pendingAccount")}</span>
                            )}
                          </td>
                          <td>
                            <div className="flex flex-wrap justify-end gap-1.5">
                              <Button variant="outline" size="sm" onClick={() => openAssign(m)}>
                                <Share2 className="mr-1 h-3.5 w-3.5" />
                                {t("office.manageAccess")}
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setEditMember(m);
                                  setForm({
                                    email: m.email,
                                    full_name: m.full_name,
                                    job_title: m.job_title,
                                    notes: m.notes ?? "",
                                  });
                                }}
                              >
                                <Pencil className="h-3.5 w-3.5" />
                              </Button>
                              <Button variant="outline" size="sm" onClick={() => void archiveMember(m)}>
                                {t("office.archive")}
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="office-panel-head">
                <div>
                  <h2 className="font-[family-name:var(--font-poppins)] text-base font-bold text-[var(--brand-navy)]">
                    {t("office.myProjects")}
                  </h2>
                  <p className="text-xs text-[var(--muted)]">{t("office.projectsHint")}</p>
                </div>
                <div className="office-toolbar">
                  <div className="office-search-wrap">
                    <Search />
                    <input
                      type="search"
                      className="office-search"
                      placeholder={t("office.searchProjects")}
                      value={projectQuery}
                      onChange={(e) => setProjectQuery(e.target.value)}
                    />
                  </div>
                </div>
              </div>
              {filteredProjects.length === 0 ? (
                <OfficeEmpty
                  icon={FolderKanban}
                  title={t("office.emptyProjectsTitle")}
                  hint={t("office.emptyProjects")}
                  action={
                    <Link href="/projects/new">
                      <Button className="gap-2">
                        <Plus className="h-4 w-4" />
                        {t("office.newProject")}
                      </Button>
                    </Link>
                  }
                />
              ) : (
                <div className="office-table-wrap">
                  <table className="office-table">
                    <thead>
                      <tr>
                        <th>{t("office.colProject")}</th>
                        <th>{t("office.colCompany")}</th>
                        <th>{t("office.colStatus")}</th>
                        <th>{t("office.collaborators")}</th>
                        <th className="text-right">{t("office.colActions")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredProjects.map((p) => (
                        <ProjectRow key={p.id} project={p} t={t} />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <MemberFormModal
        open={memberModal}
        onClose={() => setMemberModal(false)}
        title={t("office.addProfessional")}
        form={form}
        setForm={setForm}
        onSubmit={() => void createMember()}
        t={t}
        showEmail
      />

      <MemberFormModal
        open={editMember !== null}
        onClose={() => setEditMember(null)}
        title={t("office.editProfessional")}
        form={form}
        setForm={setForm}
        onSubmit={() => void saveMemberEdit()}
        t={t}
        showEmail={false}
        emailReadOnly={editMember?.email}
      />

      <OfficeAssignWizard
        open={assignModal !== null}
        member={assignModal}
        projects={dashboard?.projects ?? []}
        catalog={catalog}
        initialProjectIds={assignInitialProjects}
        onClose={() => setAssignModal(null)}
        onSubmit={submitAssignments}
        submitting={assignSubmitting}
      />
    </div>
  );
}

function ProjectRow({
  project: p,
  t,
}: {
  project: OfficeProjectRow;
  t: (key: string) => string;
}) {
  return (
    <tr>
      <td className="font-semibold text-[var(--foreground)]">{p.name}</td>
      <td className="text-[var(--muted)]">{p.company_name || "—"}</td>
      <td>
        <span className="office-badge office-badge--active">{p.status}</span>
      </td>
      <td className="tabular-nums">{p.shares_count}</td>
      <td className="text-right">
        <Link
          href={`/projects/${p.id}`}
          className="inline-flex items-center gap-1 text-sm font-semibold text-[var(--brand-teal)] hover:underline"
        >
          {t("office.openProject")}
          <ArrowUpRight className="h-3.5 w-3.5" />
        </Link>
      </td>
    </tr>
  );
}

function OfficeEmpty({
  icon: Icon,
  title,
  hint,
  action,
}: {
  icon: typeof Users;
  title: string;
  hint: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="office-empty">
      <div className="office-empty-icon">
        <Icon className="h-6 w-6" />
      </div>
      <p className="font-semibold text-[var(--foreground)]">{title}</p>
      <p className="mx-auto mt-1 max-w-md text-sm text-[var(--muted)]">{hint}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

function MemberFormModal({
  open,
  onClose,
  title,
  form,
  setForm,
  onSubmit,
  t,
  showEmail,
  emailReadOnly,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  form: { email: string; full_name: string; job_title: string; notes: string };
  setForm: React.Dispatch<
    React.SetStateAction<{ email: string; full_name: string; job_title: string; notes: string }>
  >;
  onSubmit: () => void;
  t: (key: string) => string;
  showEmail: boolean;
  emailReadOnly?: string;
}) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            {t("common.cancel")}
          </Button>
          <Button onClick={onSubmit}>{t("common.confirm")}</Button>
        </div>
      }
    >
      <div className="space-y-3">
        <Input
          label={t("office.fieldName")}
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
        />
        {showEmail ? (
          <Input
            label={t("office.fieldEmail")}
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        ) : emailReadOnly ? (
          <Input label={t("office.fieldEmail")} value={emailReadOnly} readOnly disabled />
        ) : null}
        <Input
          label={t("office.fieldRole")}
          value={form.job_title}
          onChange={(e) => setForm({ ...form, job_title: e.target.value })}
        />
        <Input
          label={t("office.fieldNotes")}
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
        />
      </div>
    </Modal>
  );
}
