import { tokenStore } from "@/lib/auth/token-store";
import type { ApiErrorShape } from "@/lib/types/auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.trim() || "/api/v1";

export class ApiError extends Error {
  status: number;
  code?: string;
  email?: string;
  details?: Record<string, string[]>;

  constructor(
    message: string,
    status: number,
    details?: Record<string, string[]>,
    code?: string,
    email?: string,
  ) {
    super(message);
    this.status = status;
    this.details = details;
    this.code = code;
    this.email = email;
  }
}

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

let refreshPromise: Promise<boolean> | null = null;

const REQUEST_TIMEOUT_MS = 60_000;

function isTimeoutError(error: unknown): boolean {
  return (
    error instanceof DOMException && error.name === "TimeoutError"
  ) || (error instanceof Error && error.name === "TimeoutError");
}

function fetchWithTimeout(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  if (typeof AbortSignal !== "undefined" && "timeout" in AbortSignal) {
    return fetch(input, {
      ...init,
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    }).catch((error) => {
      if (isTimeoutError(error)) {
        throw new ApiError(
          "O servidor demorou demasiado a responder. Confirme que o backend (porta 5000) está activo.",
          408,
        );
      }
      throw error;
    });
  }
  return fetch(input, init);
}

async function parseJsonSafe(response: Response) {
  try {
    return (await response.json()) as ApiErrorShape | Record<string, unknown>;
  } catch {
    return {};
  }
}

function buildHeaders(withAuth: boolean, contentType?: string): HeadersInit {
  const headers: HeadersInit = {};
  if (contentType) headers["Content-Type"] = contentType;
  if (withAuth) {
    const accessToken = tokenStore.getAccessToken();
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return headers;
}

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = tokenStore.getRefreshToken();
  if (!refreshToken) return false;

  if (!refreshPromise) {
    refreshPromise = fetchWithTimeout(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("refresh failed");
        const data = (await response.json()) as {
          access_token: string;
          refresh_token: string;
        };
        const role = tokenStore.getRole() ?? "user";
        tokenStore.setSession(data.access_token, data.refresh_token, role);
        return true;
      })
      .catch(() => {
        tokenStore.clear();
        if (typeof window !== "undefined") {
          const redirect = encodeURIComponent(
            `${window.location.pathname}${window.location.search}`,
          );
          window.location.href = `/login?redirect=${redirect}`;
        }
        return false;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

async function handleResponse<T>(response: Response): Promise<T> {
  const data = await parseJsonSafe(response);
  if (!response.ok) {
    const err = (data as ApiErrorShape).error;
    const fallback =
      response.status === 503
        ? "Serviço temporariamente indisponível. Tente novamente em instantes."
        : response.status === 500
          ? "Erro interno no servidor. Confirme migrations Supabase e o backend."
          : `Erro HTTP ${response.status}`;
    const message = err?.message ?? err?.code ?? fallback;
    throw new ApiError(message, response.status, err?.details, err?.code, err?.email);
  }
  return data as T;
}

export async function apiRequest<T>(
  path: string,
  method: HttpMethod,
  body?: unknown,
  withAuth = true,
  retried = false,
): Promise<T> {
  let response: Response;
  try {
    response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
      method,
      headers: buildHeaders(withAuth, body ? "application/json" : undefined),
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (isTimeoutError(error)) {
      throw new ApiError(
        "O servidor demorou demasiado a responder. Confirme que o backend (porta 5000) está activo.",
        408,
      );
    }
    throw error;
  }

  if (response.status === 401 && withAuth && !retried) {
    const refreshed = await tryRefreshToken();
    if (refreshed) return apiRequest<T>(path, method, body, withAuth, true);
  }

  return handleResponse<T>(response);
}

export async function apiUpload<T>(
  path: string,
  formData: FormData,
  method: "POST" | "PATCH" = "POST",
  retried = false,
): Promise<T> {
  const headers: HeadersInit = {};
  const accessToken = tokenStore.getAccessToken();
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: formData,
    cache: "no-store",
  });

  if (response.status === 401 && !retried) {
    const refreshed = await tryRefreshToken();
    if (refreshed) return apiUpload<T>(path, formData, method, true);
  }

  return handleResponse<T>(response);
}

export async function apiBlob(
  path: string,
  retried = false,
): Promise<{ blob: Blob; filename: string }> {
  const headers: HeadersInit = {};
  const accessToken = tokenStore.getAccessToken();
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers,
    cache: "no-store",
  });

  if (response.status === 401 && !retried) {
    const refreshed = await tryRefreshToken();
    if (refreshed) return apiBlob(path, true);
  }

  if (!response.ok) {
    const data = await parseJsonSafe(response);
    const message =
      (data as ApiErrorShape).error?.message ??
      (data as ApiErrorShape).error?.code ??
      `Erro HTTP ${response.status}`;
    throw new ApiError(message, response.status);
  }

  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match?.[1] ?? "download";

  return { blob: await response.blob(), filename };
}

export function buildQuery(params: Record<string, string | number | boolean | undefined | null>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}
