"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Card, CardHeader } from "@/components/ui/card";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi, type AccessLog } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import { formatDateTime } from "@/lib/utils/format";

export default function AccessLogsPage() {
  const { t, locale, intlLocale } = useI18n();
  const [logs, setLogs] = useState<AccessLog[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void adminApi
      .accessLogs({ limit: 100 })
      .then((res) => {
        setLogs(res.items);
        setTotal(res.total);
      })
      .catch((error) => {
        toast.error(
          error instanceof ApiError
            ? error.message
            : locale === "en"
              ? "Failed to load logs"
              : "Erro ao carregar logs",
        );
      })
      .finally(() => setLoading(false));
  }, [locale]);

  if (loading) {
    return (
      <PageLoader message={locale === "en" ? "Loading logs..." : "A carregar logs..."} />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{t("nav.accessLogs")}</h1>
        <p className="text-sm text-zinc-500">
          {locale === "en"
            ? `${total} audit record(s)`
            : `${total} registo(s) de auditoria`}
        </p>
      </div>

      <Card>
        <CardHeader
          title={locale === "en" ? "Recent activity" : "Actividade recente"}
          description={
            locale === "en"
              ? "Platform access history"
              : "Histórico de acessos à plataforma"
          }
        />
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-zinc-50 text-left">
              <tr>
                <th className="p-3">{t("common.date")}</th>
                <th className="p-3">{locale === "en" ? "User" : "Utilizador"}</th>
                <th className="p-3">{locale === "en" ? "Action" : "Acção"}</th>
                <th className="p-3">IP</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-t">
                  <td className="p-3 whitespace-nowrap">
                    {formatDateTime(log.created_at, intlLocale)}
                  </td>
                  <td className="p-3">
                    <p className="font-medium">{log.user_name}</p>
                    <p className="text-zinc-500">{log.user_email}</p>
                  </td>
                  <td className="p-3">{log.action}</td>
                  <td className="p-3 text-zinc-500">{log.ip_address ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
