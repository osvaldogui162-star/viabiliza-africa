import type { LucideIcon } from "lucide-react";
import {
  Banknote,
  FileBarChart,
  FileText,
  Mail,
  Printer,
  RefreshCw,
  Settings,
  Share2,
  Shield,
  Sparkles,
  Trash2,
  Upload,
  UserCog,
  Wallet,
} from "lucide-react";

import type { AuditTrailEntry } from "@/lib/types/admin";

export type AuditCategory = "all" | "reports" | "budgets" | "ingestion" | "system" | "other";

export type AuditActionMeta = {
  labelPt: string;
  labelEn: string;
  icon: LucideIcon;
  tone: string;
  category: AuditCategory;
};

const ACTION_MAP: Record<string, AuditActionMeta> = {
  report_generated: {
    labelPt: "Relatório gerado",
    labelEn: "Report generated",
    icon: FileBarChart,
    tone: "violet",
    category: "reports",
  },
  report_sent_email: {
    labelPt: "Relatório enviado por email",
    labelEn: "Report emailed",
    icon: Mail,
    tone: "blue",
    category: "reports",
  },
  report_shared: {
    labelPt: "Relatório partilhado",
    labelEn: "Report shared",
    icon: Share2,
    tone: "indigo",
    category: "reports",
  },
  report_submitted_bank: {
    labelPt: "Enviado ao banco",
    labelEn: "Submitted to bank",
    icon: Banknote,
    tone: "emerald",
    category: "reports",
  },
  report_printed: {
    labelPt: "Relatório impresso",
    labelEn: "Report printed",
    icon: Printer,
    tone: "zinc",
    category: "reports",
  },
  budget_generated: {
    labelPt: "Orçamento gerado",
    labelEn: "Budget generated",
    icon: Wallet,
    tone: "amber",
    category: "budgets",
  },
  budget_approved: {
    labelPt: "Orçamento aprovado",
    labelEn: "Budget approved",
    icon: Shield,
    tone: "teal",
    category: "budgets",
  },
  proforma_generated: {
    labelPt: "Proforma gerada",
    labelEn: "Proforma generated",
    icon: FileText,
    tone: "orange",
    category: "budgets",
  },
  scraping_completed: {
    labelPt: "Scraping concluído",
    labelEn: "Scraping completed",
    icon: Sparkles,
    tone: "cyan",
    category: "ingestion",
  },
  supplier_selected: {
    labelPt: "Fornecedor seleccionado",
    labelEn: "Supplier selected",
    icon: UserCog,
    tone: "sky",
    category: "ingestion",
  },
  imported: {
    labelPt: "Dados importados",
    labelEn: "Data imported",
    icon: Upload,
    tone: "lime",
    category: "ingestion",
  },
  created: {
    labelPt: "Registo criado",
    labelEn: "Record created",
    icon: Sparkles,
    tone: "emerald",
    category: "other",
  },
  updated: {
    labelPt: "Registo actualizado",
    labelEn: "Record updated",
    icon: RefreshCw,
    tone: "blue",
    category: "other",
  },
  deleted: {
    labelPt: "Registo removido",
    labelEn: "Record deleted",
    icon: Trash2,
    tone: "rose",
    category: "other",
  },
  config_updated: {
    labelPt: "Configuração actualizada",
    labelEn: "Config updated",
    icon: Settings,
    tone: "slate",
    category: "system",
  },
  plan_updated: {
    labelPt: "Plano actualizado",
    labelEn: "Plan updated",
    icon: Settings,
    tone: "violet",
    category: "system",
  },
  subscription_assigned: {
    labelPt: "Subscrição atribuída",
    labelEn: "Subscription assigned",
    icon: UserCog,
    tone: "teal",
    category: "system",
  },
};

const TONE_CLASS: Record<string, { bg: string; text: string; ring: string; dot: string }> = {
  violet: { bg: "bg-violet-100", text: "text-violet-800", ring: "ring-violet-200", dot: "bg-violet-500" },
  blue: { bg: "bg-blue-100", text: "text-blue-800", ring: "ring-blue-200", dot: "bg-blue-500" },
  indigo: { bg: "bg-indigo-100", text: "text-indigo-800", ring: "ring-indigo-200", dot: "bg-indigo-500" },
  emerald: { bg: "bg-emerald-100", text: "text-emerald-800", ring: "ring-emerald-200", dot: "bg-emerald-500" },
  amber: { bg: "bg-amber-100", text: "text-amber-800", ring: "ring-amber-200", dot: "bg-amber-500" },
  teal: { bg: "bg-teal-100", text: "text-teal-800", ring: "ring-teal-200", dot: "bg-teal-500" },
  orange: { bg: "bg-orange-100", text: "text-orange-800", ring: "ring-orange-200", dot: "bg-orange-500" },
  cyan: { bg: "bg-cyan-100", text: "text-cyan-800", ring: "ring-cyan-200", dot: "bg-cyan-500" },
  sky: { bg: "bg-sky-100", text: "text-sky-800", ring: "ring-sky-200", dot: "bg-sky-500" },
  lime: { bg: "bg-lime-100", text: "text-lime-800", ring: "ring-lime-200", dot: "bg-lime-500" },
  rose: { bg: "bg-rose-100", text: "text-rose-800", ring: "ring-rose-200", dot: "bg-rose-500" },
  slate: { bg: "bg-slate-100", text: "text-slate-800", ring: "ring-slate-200", dot: "bg-slate-500" },
  zinc: { bg: "bg-zinc-100", text: "text-zinc-800", ring: "ring-zinc-200", dot: "bg-zinc-500" },
};

export function getAuditActionMeta(action?: string): AuditActionMeta {
  if (!action) {
    return {
      labelPt: "Evento",
      labelEn: "Event",
      icon: Shield,
      tone: "zinc",
      category: "other",
    };
  }
  return (
    ACTION_MAP[action] ?? {
      labelPt: action.replace(/_/g, " "),
      labelEn: action.replace(/_/g, " "),
      icon: Shield,
      tone: "zinc",
      category: "other",
    }
  );
}

export function getAuditToneClasses(tone: string) {
  return TONE_CLASS[tone] ?? TONE_CLASS.zinc;
}

export function formatRelativeTime(iso: string, locale: string): string {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const en = locale === "en";
  if (diffMin < 1) return en ? "Just now" : "Agora";
  if (diffMin < 60) return en ? `${diffMin} min ago` : `há ${diffMin} min`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return en ? `${diffH}h ago` : `há ${diffH}h`;
  const diffD = Math.floor(diffH / 24);
  if (diffD < 7) return en ? `${diffD}d ago` : `há ${diffD}d`;
  return date.toLocaleDateString(locale === "en" ? "en-GB" : "pt-AO", { day: "2-digit", month: "short" });
}

export const AUDIT_CATEGORIES: { id: AuditCategory; labelPt: string; labelEn: string }[] = [
  { id: "all", labelPt: "Todos", labelEn: "All" },
  { id: "reports", labelPt: "Relatórios", labelEn: "Reports" },
  { id: "budgets", labelPt: "Orçamentos", labelEn: "Budgets" },
  { id: "ingestion", labelPt: "Ingestão", labelEn: "Ingestion" },
  { id: "system", labelPt: "Sistema", labelEn: "System" },
  { id: "other", labelPt: "Outros", labelEn: "Other" },
];

export function groupAuditByDate(items: { created_at: string }[], locale: string) {
  const groups: { key: string; label: string; items: typeof items }[] = [];
  const map = new Map<string, typeof items>();
  for (const item of items) {
    const key = new Date(item.created_at).toDateString();
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(item);
  }
  for (const [key, groupItems] of map) {
    const label = new Intl.DateTimeFormat(locale === "en" ? "en-GB" : "pt-AO", {
      weekday: "long",
      day: "numeric",
      month: "long",
    }).format(new Date(key));
    groups.push({ key, label, items: groupItems });
  }
  return groups;
}

export type AuditDateRange = "today" | "7d" | "30d" | "all";

export function filterAuditByDateRange<T extends { created_at: string }>(
  items: T[],
  range: AuditDateRange,
): T[] {
  if (range === "all") return items;
  const now = Date.now();
  const cutoffs: Record<Exclude<AuditDateRange, "all">, number> = {
    today: 86400000,
    "7d": 7 * 86400000,
    "30d": 30 * 86400000,
  };
  const ms = cutoffs[range];
  return items.filter((i) => now - new Date(i.created_at).getTime() <= ms);
}

export type DailyActivity = { key: string; label: string; count: number };

export function buildDailyActivity(
  items: { created_at: string }[],
  locale: string,
  days = 7,
): DailyActivity[] {
  const result: DailyActivity[] = [];
  const map = new Map<string, number>();
  for (const item of items) {
    const d = new Date(item.created_at);
    const key = d.toISOString().slice(0, 10);
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    const label = d.toLocaleDateString(locale === "en" ? "en-GB" : "pt-AO", {
      weekday: "short",
      day: "numeric",
    });
    result.push({ key, label, count: map.get(key) ?? 0 });
  }
  return result;
}

export type CategoryBreakdown = { category: AuditCategory; count: number; pct: number };

export function buildCategoryBreakdown(items: { action?: string }[]): CategoryBreakdown[] {
  const counts = new Map<AuditCategory, number>();
  for (const item of items) {
    const cat = getAuditActionMeta(item.action).category;
    if (cat === "all") continue;
    counts.set(cat, (counts.get(cat) ?? 0) + 1);
  }
  const total = items.length || 1;
  const order: AuditCategory[] = ["reports", "budgets", "ingestion", "system", "other"];
  return order
    .filter((c) => (counts.get(c) ?? 0) > 0)
    .map((category) => ({
      category,
      count: counts.get(category) ?? 0,
      pct: Math.round(((counts.get(category) ?? 0) / total) * 100),
    }));
}

export type TopActor = { id: string; count: number; name: string; email?: string };

export function getTopActors(
  items: { actor_id?: string | null }[],
  resolveName: (id: string) => string,
  resolveEmail: (id: string) => string | undefined,
  limit = 5,
): TopActor[] {
  const map = new Map<string, number>();
  for (const item of items) {
    if (!item.actor_id) continue;
    map.set(item.actor_id, (map.get(item.actor_id) ?? 0) + 1);
  }
  return Array.from(map.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([id, count]) => ({
      id,
      count,
      name: resolveName(id),
      email: resolveEmail(id),
    }));
}

export function getSmartInsight(
  items: { action?: string; created_at: string }[],
  locale: string,
): string | null {
  if (items.length === 0) return null;
  const en = locale === "en";
  const breakdown = buildCategoryBreakdown(items);
  const top = breakdown[0];
  if (top && top.pct >= 40) {
    const catLabel = AUDIT_CATEGORIES.find((c) => c.id === top.category);
    const name = en ? catLabel?.labelEn : catLabel?.labelPt;
    return en
      ? `${name} account for ${top.pct}% of visible activity (${top.count} events).`
      : `${name} representam ${top.pct}% da actividade visível (${top.count} eventos).`;
  }
  const today = items.filter((i) => new Date(i.created_at).toDateString() === new Date().toDateString()).length;
  if (today >= 5) {
    return en
      ? `High activity today: ${today} events recorded so far.`
      : `Alta actividade hoje: ${today} eventos registados até agora.`;
  }
  const peakHour = getPeakHour(items);
  if (peakHour !== null) {
    return en
      ? `Peak activity around ${peakHour}:00 — consider scheduling heavy jobs outside this window.`
      : `Pico de actividade por volta das ${peakHour}:00 — considere agendar tarefas pesadas fora desta janela.`;
  }
  return null;
}

function getPeakHour(items: { created_at: string }[]): number | null {
  if (items.length < 8) return null;
  const hours = new Array(24).fill(0);
  for (const item of items) {
    hours[new Date(item.created_at).getHours()]++;
  }
  const max = Math.max(...hours);
  if (max < 3) return null;
  return hours.indexOf(max);
}

export function exportAuditCsv(
  items: AuditTrailEntry[],
  resolveActor: (id?: string | null) => string,
  locale: string,
): void {
  const en = locale === "en";
  const header = ["id", "created_at", "action", "entity_type", "entity_id", "actor", "project_id"].join(",");
  const rows = items.map((e) =>
    [
      e.id,
      e.created_at,
      e.action ?? "",
      e.entity_type ?? "",
      e.entity_id ?? "",
      `"${resolveActor(e.actor_id).replace(/"/g, '""')}"`,
      e.project_id ?? "",
    ].join(","),
  );
  const blob = new Blob([[header, ...rows].join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `audit-trail-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
