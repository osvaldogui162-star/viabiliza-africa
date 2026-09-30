"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Building2, Landmark, UserPlus } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { PageLoader } from "@/components/ui/spinner";
import { RegisterBankUserModal } from "@/features/admin/components/register-bank-user-modal";
import { useI18n } from "@/components/providers/locale-provider";
import { usersApi } from "@/lib/api/users-api";
import { ApiError } from "@/lib/api/http-client";
import type { User } from "@/lib/types/auth";
import { FinancierStatusPill } from "@/features/financier/components/financier-status-pill";

export function AdminBankInstitutionsPanel() {
  const { t, locale } = useI18n();
  const en = locale === "en";
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [registerOpen, setRegisterOpen] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await usersApi.list({ role: "bank", limit: 200 });
      setUsers(res.items);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    void load();
  }, [load]);

  const byBank = useMemo(() => {
    const map = new Map<string, User[]>();
    for (const u of users) {
      const code = (u.bank_code ?? "—").toLowerCase();
      if (!map.has(code)) map.set(code, []);
      map.get(code)!.push(u);
    }
    return map;
  }, [users]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-2xl border border-teal-100 bg-gradient-to-br from-teal-50 to-white p-6">
        <div>
          <h2 className="flex items-center gap-2 font-[family-name:var(--font-poppins)] text-xl font-bold text-[#011636]">
            <Landmark className="h-6 w-6 text-[#00777f]" />
            {t("adminBank.title")}
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-zinc-600">{t("adminBank.subtitle")}</p>
        </div>
        <Button onClick={() => setRegisterOpen(true)} className="gap-2">
          <UserPlus className="h-4 w-4" />
          {t("adminBank.createAccess")}
        </Button>
      </div>

      {loading ? (
        <PageLoader layout="section" message={t("common.loading")} />
      ) : users.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-200 px-6 py-12 text-center text-sm text-zinc-500">
          {t("adminBank.empty")}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from(byBank.entries()).map(([code, list]) => (
            <section
              key={code}
              className="rounded-2xl border border-zinc-100 bg-white p-5 shadow-sm"
            >
              <div className="mb-4 flex items-center gap-3">
                <BankLogoBadge
                  bank={{
                    code,
                    label_pt: code.toUpperCase(),
                    label_en: code.toUpperCase(),
                    logo_path: null,
                  }}
                  size="lg"
                />
                <div>
                  <p className="font-semibold text-[#011636]">{code.toUpperCase()}</p>
                  <p className="text-xs text-zinc-500">
                    {list.length} {en ? "portal user(s)" : "acesso(s) ao portal"}
                  </p>
                </div>
              </div>
              <ul className="space-y-2">
                {list.map((u) => (
                  <li
                    key={u.id}
                    className="flex items-center justify-between rounded-lg bg-zinc-50 px-3 py-2 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium text-zinc-900">{u.full_name}</p>
                      <p className="truncate text-xs text-zinc-500">{u.email}</p>
                    </div>
                    <FinancierStatusPill
                      status={u.is_active ? "on_track" : "critical"}
                      label={u.is_active ? (en ? "Active" : "Activo") : en ? "Inactive" : "Inactivo"}
                    />
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}

      <div className="flex items-start gap-3 rounded-xl border border-zinc-100 bg-zinc-50 p-4 text-sm text-zinc-600">
        <Building2 className="mt-0.5 h-5 w-5 shrink-0 text-[#00777f]" />
        <p>{t("adminBank.hint")}</p>
      </div>

      <RegisterBankUserModal open={registerOpen} onClose={() => setRegisterOpen(false)} onSuccess={() => void load()} />
    </div>
  );
}
