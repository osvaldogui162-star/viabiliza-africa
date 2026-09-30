"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { officeApi } from "@/lib/api/office-api";
import { useI18n } from "@/components/providers/locale-provider";
import type { AdminOfficeSummary } from "@/lib/types/office";
import { PageLoader } from "@/components/ui/spinner";

export default function AdminOfficesPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<AdminOfficeSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void officeApi.adminListOffices().then((r) => setItems(r.items)).finally(() => setLoading(false));
  }, []);

  if (loading) return <PageLoader layout="section" message={t("common.loading")} />;

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <h1 className="font-[family-name:var(--font-poppins)] text-2xl font-bold text-[#011636]">
        {t("office.adminTitle")}
      </h1>
      <p className="text-sm text-zinc-600">{t("office.adminHint")}</p>
      <ul className="divide-y divide-zinc-100 rounded-xl border border-zinc-100 bg-white">
        {items.map((row) => (
          <li key={row.owner_id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div>
              <p className="font-semibold text-zinc-900">{row.owner_name}</p>
              <p className="text-sm text-zinc-500">{row.owner_email}</p>
              <p className="text-xs text-zinc-500">
                {row.projects_count} {t("office.statProjects")} · {row.active_members} {t("office.statTeam")}
              </p>
            </div>
            <Link
              href={`/escritorio?owner_id=${row.owner_id}`}
              className="text-sm font-semibold text-[#00777f] hover:underline"
            >
              {t("office.inspectOffice")}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
