"use client";

import { useCallback, useEffect, useState } from "react";
import { Eye, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { useI18n } from "@/components/providers/locale-provider";
import { adminApi } from "@/lib/api/admin-api";
import { ApiError } from "@/lib/api/http-client";
import type { BudgetTemplate } from "@/lib/types/admin";
import { cn } from "@/lib/utils/cn";

export function AdminTemplatesPanel() {
  const { locale } = useI18n();
  const en = locale === "en";
  const [items, setItems] = useState<BudgetTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [preview, setPreview] = useState<BudgetTemplate | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminApi.listBudgetTemplates();
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

  async function setDefault(id: string) {
    try {
      await adminApi.setDefaultTemplate(id);
      toast.success(en ? "Default template set" : "Template predefinido actualizado");
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed" : "Falha");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm(en ? "Delete template?" : "Remover template?")) return;
    try {
      await adminApi.deleteBudgetTemplate(id);
      toast.success(en ? "Deleted" : "Removido");
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Delete failed" : "Falha ao remover");
    }
  }

  if (loading) return <PageLoader message={en ? "Loading templates..." : "A carregar templates..."} />;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{en ? "Budget templates" : "Templates de orçamento"}</h2>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((tpl) => (
          <Card key={tpl.id} className="overflow-hidden p-0">
            <div className="border-b border-zinc-100 bg-gradient-to-r from-zinc-50 to-teal-50/40 px-4 py-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-semibold">{tpl.name}</h3>
                  <p className="text-xs text-zinc-500">{tpl.code} · {tpl.template_type}</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  {tpl.is_default ? (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                      {en ? "Default" : "Predefinido"}
                    </span>
                  ) : null}
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-semibold", tpl.is_active ? "bg-emerald-100 text-emerald-700" : "bg-zinc-200")}>
                    {tpl.is_active ? (en ? "Active" : "Activo") : en ? "Inactive" : "Inactivo"}
                  </span>
                </div>
              </div>
            </div>
            <div className="p-4">
              <pre className="max-h-24 overflow-auto rounded-lg bg-zinc-900 p-2 text-[10px] text-emerald-300">
                {JSON.stringify({ code: tpl.code, type: tpl.template_type, default: tpl.is_default }, null, 2)}
              </pre>
              <div className="mt-3 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => setPreview(tpl)}>
                  <Eye className="h-3.5 w-3.5" />
                  {en ? "Preview" : "Pré-visualizar"}
                </Button>
                {!tpl.is_default ? (
                  <>
                    <Button size="sm" variant="outline" onClick={() => void setDefault(tpl.id)}>
                      <Star className="h-3.5 w-3.5" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => void handleDelete(tpl.id)}>
                      <Trash2 className="h-3.5 w-3.5 text-rose-600" />
                    </Button>
                  </>
                ) : null}
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Modal
        open={!!preview}
        onClose={() => setPreview(null)}
        title={preview?.name ?? ""}
        footer={<Button variant="outline" onClick={() => setPreview(null)}>{en ? "Close" : "Fechar"}</Button>}
      >
        {preview ? (
          <div className="space-y-3">
            <div className="rounded-xl border border-dashed border-zinc-200 bg-zinc-50 p-6 text-center">
              <p className="text-xs font-bold uppercase tracking-wide text-zinc-400">{preview.template_type}</p>
              <p className="mt-2 text-lg font-bold text-zinc-800">{preview.name}</p>
              <p className="mt-1 text-sm text-zinc-500">{en ? "Budget document preview" : "Pré-visualização do documento de orçamento"}</p>
            </div>
            <pre className="max-h-64 overflow-auto rounded-xl bg-slate-900 p-3 text-[10px] text-emerald-300">
              {JSON.stringify(preview, null, 2)}
            </pre>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
