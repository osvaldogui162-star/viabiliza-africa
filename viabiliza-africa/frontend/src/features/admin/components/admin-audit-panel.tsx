"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ChevronDown,
  Copy,
  Download,
  GitCommitHorizontal,
  LayoutList,
  Lightbulb,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import {
  AUDIT_CATEGORIES,
  buildCategoryBreakdown,
  buildDailyActivity,
  exportAuditCsv,
  filterAuditByDateRange,
  formatRelativeTime,
  getAuditActionMeta,
  getAuditToneClasses,
  getSmartInsight,
  getTopActors,
  groupAuditByDate,
  type AuditCategory,
  type AuditDateRange,
} from "@/features/admin/lib/admin-audit-utils";
import { adminApi } from "@/lib/api/admin-api";
import { usersApi } from "@/lib/api/users-api";
import type { AuditTrailEntry } from "@/lib/types/admin";
import type { User } from "@/lib/types/auth";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

type ViewMode = "timeline" | "table";

const DATE_RANGES: { id: AuditDateRange; labelPt: string; labelEn: string }[] = [
  { id: "today", labelPt: "Hoje", labelEn: "Today" },
  { id: "7d", labelPt: "7 dias", labelEn: "7 days" },
  { id: "30d", labelPt: "30 dias", labelEn: "30 days" },
  { id: "all", labelPt: "Tudo", labelEn: "All" },
];

const CATEGORY_COLORS: Record<AuditCategory, string> = {
  all: "bg-zinc-400",
  reports: "bg-violet-500",
  budgets: "bg-amber-500",
  ingestion: "bg-cyan-500",
  system: "bg-slate-500",
  other: "bg-zinc-400",
};

function actorInitials(name: string) {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");
}

export function AdminAuditPanel() {
  const { locale, intlLocale } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<AuditTrailEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<AuditCategory>("all");
  const [entityFilter, setEntityFilter] = useState<string>("all");
  const [dateRange, setDateRange] = useState<AuditDateRange>("all");
  const [view, setView] = useState<ViewMode>("timeline");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [liveMode, setLiveMode] = useState(false);

  const load = useCallback(async (offset = 0, append = false, silent = false) => {
    if (append) setLoadingMore(true);
    else if (silent) setRefreshing(true);
    else setLoading(true);
    try {
      const [auditRes, usersRes] = await Promise.all([
        adminApi.auditTrail({ limit: 80, offset }),
        offset === 0 ? usersApi.list() : Promise.resolve(null),
      ]);
      setItems((prev) => (append ? [...prev, ...(auditRes.items ?? [])] : auditRes.items ?? []));
      setTotal(auditRes.total);
      if (usersRes) setUsers(usersRes.items ?? []);
    } finally {
      setLoading(false);
      setLoadingMore(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!liveMode) return;
    const id = window.setInterval(() => void load(0, false, true), 45000);
    return () => window.clearInterval(id);
  }, [liveMode, load]);

  const userMap = useMemo(() => new Map(users.map((u) => [u.id, u])), [users]);

  const entityTypes = useMemo(() => {
    const set = new Set(items.map((i) => i.entity_type).filter(Boolean) as string[]);
    return ["all", ...Array.from(set).sort()];
  }, [items]);

  const dateFiltered = useMemo(
    () => filterAuditByDateRange(items, dateRange),
    [items, dateRange],
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return dateFiltered.filter((entry) => {
      const meta = getAuditActionMeta(entry.action);
      if (category !== "all" && meta.category !== category) return false;
      if (entityFilter !== "all" && entry.entity_type !== entityFilter) return false;
      if (!q) return true;
      const actor = entry.actor_id ? userMap.get(entry.actor_id) : null;
      return (
        entry.action?.toLowerCase().includes(q) ||
        entry.entity_type?.toLowerCase().includes(q) ||
        actor?.full_name.toLowerCase().includes(q) ||
        actor?.email.toLowerCase().includes(q) ||
        entry.project_id?.toLowerCase().includes(q) ||
        JSON.stringify(entry.metadata ?? {}).toLowerCase().includes(q)
      );
    });
  }, [dateFiltered, search, category, entityFilter, userMap]);

  const stats = useMemo(() => {
    const today = new Date().toDateString();
    const todayCount = items.filter((i) => new Date(i.created_at).toDateString() === today).length;
    const reports = items.filter((i) => getAuditActionMeta(i.action).category === "reports").length;
    const budgets = items.filter((i) => getAuditActionMeta(i.action).category === "budgets").length;
    const actors = new Set(items.map((i) => i.actor_id).filter(Boolean)).size;
    return { todayCount, reports, budgets, actors };
  }, [items]);

  const dailyActivity = useMemo(() => buildDailyActivity(filtered, locale, 7), [filtered, locale]);
  const maxDaily = useMemo(() => Math.max(1, ...dailyActivity.map((d) => d.count)), [dailyActivity]);
  const categoryBreakdown = useMemo(() => buildCategoryBreakdown(filtered), [filtered]);
  const topActors = useMemo(
    () =>
      getTopActors(
        filtered,
        (id) => userMap.get(id)?.full_name ?? `${id.slice(0, 8)}…`,
        (id) => userMap.get(id)?.email,
        5,
      ),
    [filtered, userMap],
  );
  const insight = useMemo(() => getSmartInsight(filtered, locale), [filtered, locale]);

  const grouped = useMemo(() => groupAuditByDate(filtered, locale), [filtered, locale]);

  function actorLabel(actorId?: string | null) {
    if (!actorId) return en ? "System" : "Sistema";
    const user = userMap.get(actorId);
    return user ? user.full_name : `${actorId.slice(0, 8)}…`;
  }

  function copyHash(hash?: string) {
    if (!hash) return;
    void navigator.clipboard.writeText(hash);
    toast.success(en ? "Hash copied" : "Hash copiado");
  }

  function handleExport() {
    exportAuditCsv(filtered, (id) => actorLabel(id), locale);
    toast.success(en ? "CSV exported" : "CSV exportado");
  }

  function renderEntry(entry: AuditTrailEntry, index: number) {
    const meta = getAuditActionMeta(entry.action);
    const tone = getAuditToneClasses(meta.tone);
    const Icon = meta.icon;
    const isOpen = expanded === entry.id;
    const actor = entry.actor_id ? userMap.get(entry.actor_id) : null;
    const initials = actor ? actorInitials(actor.full_name) : "SY";

    return (
      <div
        key={entry.id}
        className="va-audit-item relative pl-8"
        style={{ animationDelay: `${Math.min(index, 12) * 35}ms` }}
      >
        <span
          className={cn(
            "absolute left-0 top-3 flex h-6 w-6 items-center justify-center rounded-full ring-4 ring-white shadow-sm",
            tone.bg,
            tone.text,
          )}
        >
          <Icon className="h-3.5 w-3.5" />
        </span>
        <div
          className={cn(
            "rounded-2xl border bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md",
            tone.ring,
            "ring-1",
          )}
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex min-w-0 flex-1 gap-3">
              <div
                className={cn(
                  "flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                  actor ? "bg-gradient-to-br from-violet-100 to-teal-100 text-violet-800" : "bg-zinc-100 text-zinc-500",
                )}
              >
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-bold", tone.bg, tone.text)}>
                    {en ? meta.labelEn : meta.labelPt}
                  </span>
                  <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-[10px] font-semibold uppercase text-zinc-600">
                    {entry.entity_type}
                  </span>
                </div>
                <p className="mt-2 text-sm text-zinc-700">
                  <span className="font-semibold text-zinc-900">{actorLabel(entry.actor_id)}</span>
                  {actor?.email ? <span className="text-zinc-500"> · {actor.email}</span> : null}
                </p>
                <div className="mt-2 flex flex-wrap gap-3 text-xs text-zinc-500">
                  <span title={formatDateTime(entry.created_at, intlLocale)}>
                    {formatRelativeTime(entry.created_at, locale)}
                  </span>
                  {entry.project_id ? (
                    <Link
                      href={`/projects/${entry.project_id}`}
                      className="font-semibold text-teal-700 hover:underline"
                    >
                      {en ? "Open project" : "Abrir projecto"} →
                    </Link>
                  ) : null}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setExpanded(isOpen ? null : entry.id)}
              className="rounded-lg border border-zinc-200 p-1.5 text-zinc-500 transition hover:bg-zinc-50"
              aria-expanded={isOpen}
            >
              <ChevronDown className={cn("h-4 w-4 transition", isOpen && "rotate-180")} />
            </button>
          </div>

          {isOpen ? (
            <div className="va-audit-detail mt-4 space-y-3 border-t border-zinc-100 pt-4 text-xs">
              <div className="grid gap-2 sm:grid-cols-2">
                <div>
                  <p className="font-semibold uppercase tracking-wide text-zinc-400">
                    {en ? "Entity ID" : "ID entidade"}
                  </p>
                  <p className="mt-0.5 break-all font-mono text-zinc-700">{entry.entity_id ?? "—"}</p>
                </div>
                <div>
                  <p className="font-semibold uppercase tracking-wide text-zinc-400">
                    {en ? "Exact time" : "Hora exacta"}
                  </p>
                  <p className="mt-0.5 text-zinc-700">{formatDateTime(entry.created_at, intlLocale)}</p>
                </div>
              </div>
              {entry.data_hash ? (
                <div className="flex items-start gap-2 rounded-xl bg-zinc-50 p-3">
                  <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal-600" />
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-zinc-700">{en ? "Integrity hash" : "Hash de integridade"}</p>
                    <p className="mt-1 break-all font-mono text-[10px] text-zinc-600">{entry.data_hash}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => copyHash(entry.data_hash)}
                    className="text-zinc-500 hover:text-teal-700"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              ) : null}
              {entry.metadata && Object.keys(entry.metadata).length > 0 ? (
                <pre className="max-h-40 overflow-auto rounded-xl bg-slate-900 p-3 font-mono text-[10px] text-emerald-300">
                  {JSON.stringify(entry.metadata, null, 2)}
                </pre>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  if (loading) {
    return <PageLoader message={en ? "Loading audit trail..." : "A carregar auditoria..."} />;
  }

  return (
    <div className="space-y-5">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl border border-violet-200/60 bg-gradient-to-br from-violet-950 via-indigo-950 to-slate-900 px-6 py-6 text-white shadow-xl">
        <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-fuchsia-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-8 left-10 h-32 w-32 rounded-full bg-teal-400/15 blur-3xl" />
        <div className="relative flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.2em] text-violet-200">
              <Activity className="h-4 w-4" />
              {en ? "Smart audit" : "Auditoria inteligente"}
              {liveMode ? (
                <span className="ml-2 inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300">
                  <span className="va-live-dot h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  LIVE
                </span>
              ) : null}
            </p>
            <h2 className="mt-1 text-2xl font-bold">{en ? "Global activity trail" : "Trilho global de actividade"}</h2>
            <p className="mt-1 max-w-xl text-sm text-violet-100/80">
              {en
                ? "Every client action across projects — reports, budgets, ingestion and system events."
                : "Todas as acções dos clientes nos projectos — relatórios, orçamentos, ingestão e sistema."}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              className={cn(
                "border-white/20 bg-white/10 text-white hover:bg-white/20",
                liveMode && "ring-2 ring-emerald-400/50",
              )}
              onClick={() => setLiveMode((v) => !v)}
              title={en ? "Auto-refresh every 45s" : "Actualização automática a cada 45s"}
            >
              <Zap className={cn("h-4 w-4", liveMode && "text-emerald-300")} />
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="border-white/20 bg-white/10 text-white hover:bg-white/20"
              onClick={() => void load(0, false, true)}
              disabled={refreshing}
            >
              <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="border-white/20 bg-white/10 text-white hover:bg-white/20"
              onClick={handleExport}
              disabled={filtered.length === 0}
            >
              <Download className="h-4 w-4" />
            </Button>
            <div className="flex rounded-xl border border-white/15 bg-white/10 p-1">
              <button
                type="button"
                onClick={() => setView("timeline")}
                className={cn(
                  "flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition",
                  view === "timeline" ? "bg-white text-violet-900" : "text-white/80 hover:text-white",
                )}
              >
                <GitCommitHorizontal className="h-3.5 w-3.5" />
                Timeline
              </button>
              <button
                type="button"
                onClick={() => setView("table")}
                className={cn(
                  "flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition",
                  view === "table" ? "bg-white text-violet-900" : "text-white/80 hover:text-white",
                )}
              >
                <LayoutList className="h-3.5 w-3.5" />
                Tabela
              </button>
            </div>
          </div>
        </div>

        <div className="relative mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: en ? "Total records" : "Total registos", value: total, icon: Sparkles },
            { label: en ? "Today" : "Hoje", value: stats.todayCount, icon: TrendingUp },
            { label: en ? "Report events" : "Eventos relatório", value: stats.reports, icon: Activity },
            { label: en ? "Active actors" : "Actores activos", value: stats.actors, icon: Users },
          ].map((s) => (
            <div
              key={s.label}
              className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-sm"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                <s.icon className="h-5 w-5 text-violet-200" />
              </div>
              <div>
                <p className="text-2xl font-bold">{s.value}</p>
                <p className="text-xs text-violet-100/70">{s.label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Smart insight */}
      {insight ? (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-200/80 bg-gradient-to-r from-amber-50 to-orange-50 px-4 py-3 shadow-sm">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
            <Lightbulb className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-amber-800">
              {en ? "Smart insight" : "Insight inteligente"}
            </p>
            <p className="mt-0.5 text-sm text-amber-900/90">{insight}</p>
          </div>
        </div>
      ) : null}

      {/* Analytics row */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-zinc-100 bg-zinc-50/80 px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-wide text-zinc-500">
              {en ? "7-day activity" : "Actividade 7 dias"}
            </p>
          </div>
          <div className="flex h-32 items-end gap-1.5 px-4 pb-4 pt-6">
            {dailyActivity.map((day, i) => (
              <div key={day.key} className="flex flex-1 flex-col items-center gap-1.5">
                <span className="text-[10px] font-semibold text-zinc-500">{day.count || ""}</span>
                <div
                  className="va-audit-spark-bar w-full origin-bottom rounded-t-md bg-gradient-to-t from-violet-600 to-teal-400"
                  style={{
                    height: `${Math.max(8, (day.count / maxDaily) * 72)}px`,
                    animationDelay: `${i * 60}ms`,
                  }}
                  title={`${day.label}: ${day.count}`}
                />
                <span className="text-[9px] font-medium text-zinc-400">{day.label.split(" ")[0]}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="overflow-hidden p-0">
          <div className="border-b border-zinc-100 bg-zinc-50/80 px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-wide text-zinc-500">
              {en ? "By category" : "Por categoria"}
            </p>
          </div>
          <div className="space-y-3 px-4 py-4">
            {categoryBreakdown.length === 0 ? (
              <p className="text-sm text-zinc-400">{en ? "No data" : "Sem dados"}</p>
            ) : (
              categoryBreakdown.map((row) => {
                const catMeta = AUDIT_CATEGORIES.find((c) => c.id === row.category);
                return (
                  <div key={row.category}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span className="font-semibold text-zinc-700">{en ? catMeta?.labelEn : catMeta?.labelPt}</span>
                      <span className="text-zinc-500">
                        {row.count} · {row.pct}%
                      </span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-zinc-100">
                      <div
                        className={cn("h-full rounded-full transition-all duration-700", CATEGORY_COLORS[row.category])}
                        style={{ width: `${row.pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        <Card className="overflow-hidden p-0">
          <div className="border-b border-zinc-100 bg-zinc-50/80 px-4 py-3">
            <p className="text-xs font-bold uppercase tracking-wide text-zinc-500">
              {en ? "Top actors" : "Top actores"}
            </p>
          </div>
          <div className="divide-y divide-zinc-100">
            {topActors.length === 0 ? (
              <p className="px-4 py-6 text-sm text-zinc-400">{en ? "No actors yet" : "Sem actores"}</p>
            ) : (
              topActors.map((actor, i) => (
                <div key={actor.id} className="flex items-center gap-3 px-4 py-3">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-violet-100 text-xs font-bold text-violet-700">
                    {i + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-zinc-800">{actor.name}</p>
                    {actor.email ? <p className="truncate text-xs text-zinc-500">{actor.email}</p> : null}
                  </div>
                  <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-bold text-zinc-600">
                    {actor.count}
                  </span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="sticky top-0 z-10 -mx-1 rounded-2xl border border-zinc-200/80 bg-white/95 px-4 py-3 shadow-sm backdrop-blur-md">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {AUDIT_CATEGORIES.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setCategory(c.id)}
                className={cn(
                  "rounded-full px-3 py-1 text-xs font-semibold transition",
                  category === c.id
                    ? "bg-violet-600 text-white shadow-md shadow-violet-600/30"
                    : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200",
                )}
              >
                {en ? c.labelEn : c.labelPt}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex rounded-xl border border-zinc-200 bg-zinc-50 p-0.5">
              {DATE_RANGES.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setDateRange(r.id)}
                  className={cn(
                    "rounded-lg px-2.5 py-1 text-[11px] font-semibold transition",
                    dateRange === r.id ? "bg-white text-violet-700 shadow-sm" : "text-zinc-500 hover:text-zinc-700",
                  )}
                >
                  {en ? r.labelEn : r.labelPt}
                </button>
              ))}
            </div>
            <select
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
              className="rounded-xl border border-zinc-200 bg-white px-3 py-2 text-xs font-medium"
            >
              {entityTypes.map((t) => (
                <option key={t} value={t}>
                  {t === "all" ? (en ? "All entities" : "Todas entidades") : t}
                </option>
              ))}
            </select>
            <div className="relative min-w-[14rem] flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
              <Input
                placeholder={en ? "Search actor, action, project..." : "Pesquisar actor, acção, projecto..."}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </div>
      </div>

      <p className="text-sm text-zinc-500">
        {filtered.length} / {total} {en ? "events shown" : "eventos visíveis"}
        {dateRange !== "all" ? (
          <span className="text-zinc-400">
            {" "}
            · {en ? "filtered by period" : "filtrado por período"}
          </span>
        ) : null}
      </p>

      {filtered.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 text-center">
          <ShieldCheck className="mb-3 h-12 w-12 text-zinc-300" />
          <p className="font-semibold text-zinc-700">
            {en ? "No events match your filters" : "Nenhum evento corresponde aos filtros"}
          </p>
          <p className="mt-1 text-sm text-zinc-500">
            {en ? "Try adjusting category, date range or search." : "Experimente ajustar categoria, período ou pesquisa."}
          </p>
        </Card>
      ) : view === "timeline" ? (
        <div className="relative space-y-8">
          <div className="pointer-events-none absolute bottom-0 left-3 top-0 w-px bg-gradient-to-b from-violet-300 via-teal-300 to-transparent" />
          {grouped.map((group) => (
            <section key={group.key}>
              <div className="mb-4 flex items-center gap-3 pl-8">
                <h3 className="text-sm font-bold capitalize text-violet-700">{group.label}</h3>
                <span className="rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-bold text-violet-700">
                  {group.items.length}
                </span>
              </div>
              <div className="space-y-4">{group.items.map((entry, index) => renderEntry(entry as AuditTrailEntry, index))}</div>
            </section>
          ))}
        </div>
      ) : (
        <Card className="overflow-hidden p-0 shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
                <tr>
                  <th className="px-4 py-3">{en ? "When" : "Quando"}</th>
                  <th className="px-4 py-3">{en ? "Action" : "Acção"}</th>
                  <th className="px-4 py-3">{en ? "Entity" : "Entidade"}</th>
                  <th className="px-4 py-3">{en ? "Actor" : "Actor"}</th>
                  <th className="px-4 py-3">{en ? "Project" : "Projecto"}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((entry) => {
                  const meta = getAuditActionMeta(entry.action);
                  const tone = getAuditToneClasses(meta.tone);
                  const Icon = meta.icon;
                  return (
                    <tr key={entry.id} className="border-b border-zinc-100 transition hover:bg-violet-50/40">
                      <td className="whitespace-nowrap px-4 py-3 text-zinc-600">
                        {formatRelativeTime(entry.created_at, locale)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold",
                            tone.bg,
                            tone.text,
                          )}
                        >
                          <Icon className="h-3 w-3" />
                          {en ? meta.labelEn : meta.labelPt}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-zinc-700">{entry.entity_type}</td>
                      <td className="px-4 py-3">{actorLabel(entry.actor_id)}</td>
                      <td className="px-4 py-3">
                        {entry.project_id ? (
                          <Link href={`/projects/${entry.project_id}`} className="font-medium text-teal-700 hover:underline">
                            {entry.project_id.slice(0, 8)}…
                          </Link>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {items.length < total ? (
        <div className="flex justify-center">
          <Button variant="outline" disabled={loadingMore} onClick={() => void load(items.length, true)}>
            {loadingMore ? (en ? "Loading..." : "A carregar...") : en ? "Load more events" : "Carregar mais eventos"}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
