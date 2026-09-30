"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useI18n } from "@/components/providers/locale-provider";
import { clearAppSessionCaches } from "@/lib/cache/app-session-cache";
import { notifyError } from "@/lib/utils/toast";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi, resetProjectsApiCaches } from "@/lib/api/projects-api";
import {
  projectsListFingerprint,
  readProjectsListCache,
  writeProjectsListCache,
} from "@/lib/cache/projects-list-cache";
import type { Project } from "@/lib/types/project";

export type ProjectSortKey =
  | "name"
  | "company_name"
  | "sector_label"
  | "country_label"
  | "investment_amount"
  | "status_label"
  | "updated_at"
  | "created_at";

export type SortDir = "asc" | "desc";
export type OwnershipFilter = "all" | "owned" | "shared";

const PAGE_SIZES = [10, 25, 50] as const;
/** Máximo para filtros só no cliente — evita pedidos enormes ao backend. */
const CLIENT_MODE_CAP = 120;

function compareProjects(a: Project, b: Project, key: ProjectSortKey, dir: SortDir): number {
  let av: string | number = "";
  let bv: string | number = "";

  switch (key) {
    case "investment_amount":
      av = parseFloat(a.investment_amount || "0") || 0;
      bv = parseFloat(b.investment_amount || "0") || 0;
      break;
    case "updated_at":
    case "created_at":
      av = new Date(a[key]).getTime();
      bv = new Date(b[key]).getTime();
      break;
    default:
      av = String(a[key as keyof Project] ?? "").toLowerCase();
      bv = String(b[key as keyof Project] ?? "").toLowerCase();
  }

  if (av < bv) return dir === "asc" ? -1 : 1;
  if (av > bv) return dir === "asc" ? 1 : -1;
  return 0;
}

function matchesOwnership(project: Project, ownership: OwnershipFilter): boolean {
  if (ownership === "owned") return project.is_owner;
  if (ownership === "shared") return project.is_shared && !project.is_owner;
  return true;
}

export function useProjectsTable() {
  const { t } = useI18n();
  const tRef = useRef(t);
  tRef.current = t;

  const [rawItems, setRawItems] = useState<Project[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [country, setCountry] = useState("");
  const [sector, setSector] = useState("");
  const [currency, setCurrency] = useState("");
  const [ownership, setOwnership] = useState<OwnershipFilter>("all");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState<number>(PAGE_SIZES[1]);
  const [sortKey, setSortKey] = useState<ProjectSortKey>("updated_at");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const isFirstLoad = useRef(true);
  const cachePrimed = useRef(false);

  const clientMode = ownership !== "all" || Boolean(currency);

  useEffect(() => {
    if (cachePrimed.current) return;
    cachePrimed.current = true;
    clearAppSessionCaches();
    resetProjectsApiCaches();
  }, []);

  const load = useCallback(async () => {
    const initial = isFirstLoad.current;
    const fingerprint = projectsListFingerprint({
      search,
      status,
      country,
      sector,
      page,
      pageSize,
      clientMode,
    });

    if (initial) {
      const cached = readProjectsListCache(fingerprint);
      if (cached?.items?.length) {
        setRawItems(cached.items);
        setTotal(cached.total);
        setLoading(false);
      } else {
        setLoading(true);
      }
    } else {
      setRefreshing(true);
    }

    try {
      const response = await projectsApi.list({
        search: search || undefined,
        status: status || undefined,
        country: country || undefined,
        sector: sector || undefined,
        limit: clientMode ? CLIENT_MODE_CAP : pageSize,
        offset: clientMode ? 0 : (page - 1) * pageSize,
      });
      setRawItems(response.items ?? []);
      setTotal(response.total ?? 0);
      writeProjectsListCache(fingerprint, {
        items: response.items ?? [],
        total: response.total ?? 0,
      });
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : error instanceof Error && error.name === "TimeoutError"
            ? tRef.current("projects.timeoutError")
            : tRef.current("projects.loadError");
      notifyError(message);
    } finally {
      setLoading(false);
      setRefreshing(false);
      isFirstLoad.current = false;
    }
  }, [search, status, country, sector, page, pageSize, clientMode]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), search ? 320 : 0);
    return () => window.clearTimeout(timer);
  }, [load, search]);

  useEffect(() => {
    setPage(1);
    setSelectedIds(new Set());
  }, [search, status, country, sector, currency, ownership, pageSize]);

  const processed = useMemo(() => {
    let items = [...rawItems];
    if (currency) items = items.filter((p) => p.currency === currency);
    if (ownership !== "all") items = items.filter((p) => matchesOwnership(p, ownership));
    items.sort((a, b) => compareProjects(a, b, sortKey, sortDir));
    return items;
  }, [rawItems, currency, ownership, sortKey, sortDir]);

  const filteredTotal = clientMode ? processed.length : total;
  const pageCount = Math.max(1, Math.ceil(filteredTotal / pageSize));

  const pageItems = useMemo(() => {
    if (!clientMode) return processed;
    const start = (page - 1) * pageSize;
    return processed.slice(start, start + pageSize);
  }, [clientMode, processed, page, pageSize]);

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  function toggleSort(key: ProjectSortKey) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir(key === "name" || key === "company_name" ? "asc" : "desc");
    }
  }

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleSelectAll(visibleIds: string[]) {
    setSelectedIds((prev) => {
      const allSelected = visibleIds.every((id) => prev.has(id));
      if (allSelected) return new Set();
      return new Set(visibleIds);
    });
  }

  function clearFilters() {
    setSearch("");
    setStatus("");
    setCountry("");
    setSector("");
    setCurrency("");
    setOwnership("all");
    setPage(1);
  }

  const hasFilters = Boolean(search || status || country || sector || currency || ownership !== "all");

  return {
    items: pageItems,
    total: filteredTotal,
    loading,
    refreshing,
    search,
    setSearch,
    status,
    setStatus,
    country,
    setCountry,
    sector,
    setSector,
    currency,
    setCurrency,
    ownership,
    setOwnership,
    page,
    setPage,
    pageSize,
    setPageSize,
    pageSizes: PAGE_SIZES,
    pageCount,
    sortKey,
    sortDir,
    toggleSort,
    selectedIds,
    toggleSelect,
    toggleSelectAll,
    clearSelection: () => setSelectedIds(new Set()),
    clearFilters,
    hasFilters,
    refresh: load,
    clientMode,
  };
}
