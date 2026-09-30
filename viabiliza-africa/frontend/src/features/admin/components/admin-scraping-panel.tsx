"use client";

import { useCallback, useEffect, useState } from "react";
import { History, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { ScrapingSource } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";
import { formatDateTime } from "@/lib/utils/format";

export function AdminScrapingPanel() {
  const { locale, intlLocale } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<ScrapingSource[]>([]);
  const [logs, setLogs] = useState<Array<{ action?: string; created_at: string; entity_type?: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editItem, setEditItem] = useState<ScrapingSource | null>(null);
  const [form, setForm] = useState({ code: "", name: "", base_url: "", country: "AO" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [srcRes, auditRes] = await Promise.all([
        adminApi.listScrapingSources(),
        adminApi.auditTrail({ limit: 30, action: "scraping_completed" }),
      ]);
      setItems(srcRes.items ?? []);
      setLogs(auditRes.items ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed to load" : "Erro ao carregar");
    } finally {
      setLoading(false);
    }
  }, [en]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCreate() {
    try {
      await adminApi.createScrapingSource(form);
      toast.success(en ? "Source created" : "Fonte criada");
      setOpen(false);
      setForm({ code: "", name: "", base_url: "", country: "AO" });
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Create failed" : "Falha ao criar");
    }
  }

  async function handleUpdate() {
    if (!editItem) return;
    try {
      await adminApi.updateScrapingSource(editItem.id, form);
      toast.success(en ? "Updated" : "Actualizado");
      setEditItem(null);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Update failed" : "Falha");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm(en ? "Delete source?" : "Remover fonte?")) return;
    try {
      await adminApi.deleteScrapingSource(id);
      toast.success(en ? "Deleted" : "Removida");
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Delete failed" : "Falha ao remover");
    }
  }

  if (loading) return <PageLoader message={en ? "Loading..." : "A carregar..."} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{en ? "Scraping sources" : "Fontes de scraping"}</h2>
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" />
          {en ? "Add source" : "Adicionar fonte"}
        </Button>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((src) => (
          <Card key={src.id} className="p-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold">{src.name}</h3>
                <p className="text-xs text-zinc-500">{src.code} · {src.country}</p>
                <p className="mt-1 truncate text-sm text-teal-700">{src.base_url}</p>
              </div>
              <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", src.is_active ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200")}>
                {src.is_active ? (en ? "Active" : "Activa") : en ? "Inactive" : "Inactivo"}
              </span>
            </div>
            <div className="mt-3 flex gap-2">
              <Button size="sm" variant="outline" onClick={() => { setEditItem(src); setForm({ code: src.code, name: src.name, base_url: src.base_url, country: src.country }); }}>
                <Pencil className="h-3.5 w-3.5" />
              </Button>
              <Button size="sm" variant="outline" onClick={() => void handleDelete(src.id)}>
                <Trash2 className="h-3.5 w-3.5 text-rose-600" />
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <Card className="p-4">
        <h3 className="mb-3 flex items-center gap-2 text-sm font-bold text-zinc-800">
          <History className="h-4 w-4" />
          {en ? "Recent scraping activity" : "Actividade recente de scraping"}
        </h3>
        {logs.length === 0 ? (
          <p className="text-sm text-zinc-500">{en ? "No logs yet" : "Sem registos"}</p>
        ) : (
          <ul className="divide-y divide-zinc-100 text-sm">
            {logs.map((log) => (
              <li key={log.created_at + (log.action ?? "")} className="flex justify-between py-2">
                <span className="font-medium text-zinc-700">{log.action ?? "scraping"}</span>
                <span className="text-xs text-zinc-400">{formatDateTime(log.created_at, intlLocale)}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Modal open={open} onClose={() => setOpen(false)} title={en ? "New source" : "Nova fonte"} footer={<Button onClick={() => void handleCreate()}>{en ? "Create" : "Criar"}</Button>}>
        <div className="space-y-3">
          <Input label={en ? "Code" : "Código"} value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
          <Input label={en ? "Name" : "Nome"} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label="URL" value={form.base_url} onChange={(e) => setForm({ ...form, base_url: e.target.value })} />
        </div>
      </Modal>

      <Modal open={!!editItem} onClose={() => setEditItem(null)} title={en ? "Edit source" : "Editar fonte"} footer={<Button onClick={() => void handleUpdate()}>{en ? "Save" : "Guardar"}</Button>}>
        <div className="space-y-3">
          <Input label={en ? "Name" : "Nome"} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label="URL" value={form.base_url} onChange={(e) => setForm({ ...form, base_url: e.target.value })} />
        </div>
      </Modal>
    </div>
  );
}
