"use client";

import { AdminUsersPanel } from "@/features/admin/components/admin-users-panel";
import { useI18n } from "@/components/providers/locale-provider";

export default function AdminUtilizadoresPage() {
  const { t } = useI18n();

  return (
    <main className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900">{t("adminUsers.title")}</h1>
        <p className="mt-1 text-sm text-zinc-600">{t("adminUsers.subtitle")}</p>
      </div>
      <AdminUsersPanel />
    </main>
  );
}
