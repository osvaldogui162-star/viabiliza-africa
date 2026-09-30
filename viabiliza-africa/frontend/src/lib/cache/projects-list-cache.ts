import type { Project } from "@/lib/types/project";

const STORAGE_KEY = "va_projects_list_v1";
const MAX_AGE_MS = 5 * 60 * 1000;

type Entry = {
  fingerprint: string;
  items: Project[];
  total: number;
  savedAt: number;
};

function readStore(): Entry | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Entry;
    if (Date.now() - parsed.savedAt > MAX_AGE_MS) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function readProjectsListCache(fingerprint: string): Pick<Entry, "items" | "total"> | null {
  const entry = readStore();
  if (!entry || entry.fingerprint !== fingerprint) return null;
  return { items: entry.items, total: entry.total };
}

export function writeProjectsListCache(
  fingerprint: string,
  payload: { items: Project[]; total: number },
) {
  if (typeof window === "undefined") return;
  try {
    const entry: Entry = {
      fingerprint,
      items: payload.items,
      total: payload.total,
      savedAt: Date.now(),
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(entry));
  } catch {
    /* quota or private mode */
  }
}

export function projectsListFingerprint(params: {
  search: string;
  status: string;
  country: string;
  sector: string;
  page: number;
  pageSize: number;
  clientMode: boolean;
}) {
  return JSON.stringify(params);
}
