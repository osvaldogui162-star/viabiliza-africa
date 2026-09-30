"use client";

import { useCallback, useEffect, useState } from "react";
import { Pencil, Play, RefreshCw, Save } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { IntegrationSetting } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

const INTEGRATION_FIELDS: Record<string, { key: string; label: string; secret?: boolean }[]> = {
  bfa: [
    { key: "api_url", label: "API URL" },
    { key: "api_key", label: "API Key", secret: true },
  ],
  bda: [
    { key: "api_url", label: "API URL" },
    { key: "api_key", label: "API Key", secret: true },
  ],
  smtp: [
    { key: "host", label: "Host" },
    { key: "port", label: "Port" },
    { key: "user", label: "User" },
    { key: "password", label: "Password", secret: true },
    { key: "from_email", label: "From email" },
    { key: "from_name", label: "From name" },
  ],
  trello: [
    { key: "api_key", label: "API Key", secret: true },
    { key: "token", label: "Token", secret: true },
  ],
};

export function AdminIntegrationsPanel() {
  const { locale, intlLocale } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<IntegrationSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
  const [editing, setEditing] = useState<IntegrationSetting | null>(null);
  const [form, setForm] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listIntegrations();
      setItems(res.items ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load" : "Erro ao carregar");
    } finally {
      setLoading(false);
    }
  }, [en]);

  useEffect(() => {
    void load();
  }, [load]);

  function openEdit(item: IntegrationSetting) {
    setEditing(item);
    const fields = INTEGRATION_FIELDS[item.integration_key] ?? [];
    const initial: Record<string, string> = {};
    for (const f of fields) {
      const val = item.settings?.[f.key];
      initial[f.key] = val != null ? String(val) : "";
    }
    setForm(initial);
  }

  async function handleSave() {
    if (!editing) return;
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(form)) {
        if (v && v !== "••••••••") payload[k] = v;
      }
      await adminApi.updateIntegration(editing.integration_key, { settings: payload, is_active: editing.is_active });
      toast.success(en ? "Integration updated" : "Integração actualizada");
      setEditing(null);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Save failed" : "Falha ao guardar");
    } finally {
      setSaving(false);
    }
  }

  async function handleTest(key: string) {
    setTesting(key);
    try {
      const res = await adminApi.testIntegration(key);
      toast[res.success ? "success" : "error"](res.message);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Test failed" : "Teste falhou");
    } finally {
      setTesting(null);
    }
  }

  if (loading) return <PageLoader message={en ? "Loading integrations..." : "A carregar integrações..."} />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{en ? "Integrations" : "Integrações"}</h2>
          <p className="text-sm text-zinc-500">{en ? "Secure credential editor + connection test" : "Editor de credenciais + teste de ligação"}</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void load()}>
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((item) => (
          <Card key={item.integration_key} className="p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="font-semibold uppercase">{item.integration_key}</h3>
                <p className="text-xs text-zinc-500">{formatDateTime(item.updated_at, intlLocale)}</p>
              </div>
              <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", item.is_active ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200")}>
                {item.is_active ? (en ? "Active" : "Activa") : en ? "Inactive" : "Inactiva"}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <Button size="sm" variant="outline" onClick={() => openEdit(item)}>
                <Pencil className="h-3.5 w-3.5" />
                {en ? "Edit" : "Editar"}
              </Button>
              <Button size="sm" variant="outline" disabled={testing === item.integration_key} onClick={() => void handleTest(item.integration_key)}>
                <Play className="h-3.5 w-3.5" />
                {en ? "Test" : "Testar"}
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <Modal
        open={!!editing}
        onClose={() => setEditing(null)}
        title={editing ? `${en ? "Edit" : "Editar"} ${editing.integration_key.toUpperCase()}` : ""}
        footer={
          <Button onClick={() => void handleSave()} disabled={saving}>
            <Save className="h-4 w-4" />
            {en ? "Save" : "Guardar"}
          </Button>
        }
      >
        {editing ? (
          <div className="space-y-3">
            {(INTEGRATION_FIELDS[editing.integration_key] ?? Object.keys(editing.settings ?? {}).map((k) => ({ key: k, label: k }))).map((field) => (
              <Input
                key={field.key}
                label={field.label}
                type={"secret" in field && field.secret ? "password" : "text"}
                value={form[field.key] ?? ""}
                onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                placeholder={"secret" in field && field.secret ? "••••••••" : undefined}
              />
            ))}
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
