"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Download, Link2, RefreshCw, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/spinner";
import {
  erpBillingApi,
  type ErpBillingConnection,
  type ErpProvider,
  type FiscalDocumentRow,
} from "@/lib/api/erp-billing-api";
import { ApiError } from "@/lib/api/http-client";
import { tokenStore } from "@/lib/auth/token-store";
import type { PlanCapabilities } from "@/lib/types/subscription";

export function ErpBillingPanel({ capabilities }: { capabilities: PlanCapabilities | null }) {
  const enabled = Boolean(capabilities?.erp_billing_integration);
  const autoAllowed = Boolean(capabilities?.erp_auto_fiscal_invoice);

  const [providers, setProviders] = useState<ErpProvider[]>([]);
  const [connection, setConnection] = useState<ErpBillingConnection | null>(null);
  const [documents, setDocuments] = useState<FiscalDocumentRow[]>([]);
  const [providerCode, setProviderCode] = useState("agt_export");
  const [config, setConfig] = useState<Record<string, string>>({});
  const [autoFiscal, setAutoFiscal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const selected = useMemo(
    () => providers.find((p) => p.code === providerCode),
    [providers, providerCode],
  );

  const load = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const [prov, mine] = await Promise.all([
        erpBillingApi.listProviders(),
        erpBillingApi.getMine(),
      ]);
      setProviders(prov.items);
      setConnection(mine.connection);
      setDocuments(mine.fiscal_documents);
      if (mine.connection?.provider_code) {
        setProviderCode(mine.connection.provider_code);
        setConfig(mine.connection.config ?? {});
        setAutoFiscal(mine.connection.auto_fiscal_on_payment ?? false);
      }
    } catch (e) {
      if (e instanceof ApiError && e.status === 403) return;
      toast.error(e instanceof ApiError ? e.message : "Erro ao carregar ERP");
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    setBusy(true);
    try {
      const res = await erpBillingApi.save({
        provider_code: providerCode,
        config,
        auto_fiscal_on_payment: autoAllowed ? autoFiscal : false,
      });
      setConnection(res.connection);
      toast.success("Configuração ERP guardada");
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Erro ao guardar");
    } finally {
      setBusy(false);
    }
  }

  async function testConn() {
    setBusy(true);
    try {
      const res = await erpBillingApi.test({ provider_code: providerCode, config });
      setConnection(res.connection);
      toast.success("Ligação ERP validada");
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Teste falhou");
    } finally {
      setBusy(false);
    }
  }

  async function downloadAgt(docId: string) {
    const token = tokenStore.getAccessToken();
    const url = erpBillingApi.agtExportUrl(docId);
    const res = await fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: "include",
    });
    if (!res.ok) {
      toast.error("Download indisponível");
      return;
    }
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `agt-export-${docId}.xml`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  if (!enabled) {
    return (
      <section className="rounded-2xl border border-zinc-200 bg-white p-6">
        <h2 className="font-[family-name:var(--font-poppins)] text-lg font-bold text-zinc-900">
          ERP de facturação
        </h2>
        <p className="mt-2 text-sm text-zinc-600">
          Disponível em planos pagos (Starter e superiores), após confirmação de pagamento AppyPay.
          Actualize em{" "}
          <a href="/planos" className="font-semibold text-emerald-700 hover:underline">
            /planos
          </a>
          .
        </p>
      </section>
    );
  }

  if (loading) return <PageLoader layout="section" />;

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2 font-[family-name:var(--font-poppins)] text-lg font-bold text-zinc-900">
            <Link2 className="h-5 w-5 text-emerald-700" />
            ERP de facturação (Angola & África)
          </h2>
          <p className="mt-1 text-sm text-zinc-600">
            APIs abertas: Odoo, Zoho Books, export AGT, webhook genérico. Factura automática de
            assinatura no Business+ após pagamento confirmado.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={busy}>
          <RefreshCw className="mr-1.5 h-4 w-4" />
          Actualizar
        </Button>
      </div>

      {connection ? (
        <p className="mt-3 text-xs text-zinc-500">
          Estado:{" "}
          <span className="font-semibold text-zinc-800">{connection.connection_status}</span>
          {connection.last_error ? (
            <span className="text-red-600"> — {connection.last_error}</span>
          ) : null}
        </p>
      ) : null}

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
            Fornecedor
          </label>
          <select
            className="mt-1 w-full rounded-xl border border-zinc-200 px-3 py-2.5 text-sm"
            value={providerCode}
            onChange={(e) => {
              setProviderCode(e.target.value);
              setConfig({});
            }}
          >
            {providers.map((p) => (
              <option key={p.code} value={p.code}>
                {p.name}
                {p.agt_certified ? " · AGT" : ""}
                {p.free_tier ? " · API free" : ""}
              </option>
            ))}
          </select>
          {selected ? (
            <p className="mt-2 text-xs text-zinc-500">{selected.notes_pt}</p>
          ) : null}
        </div>

        {autoAllowed ? (
          <label className="flex items-center gap-2 self-end text-sm text-zinc-700">
            <input
              type="checkbox"
              checked={autoFiscal}
              onChange={(e) => setAutoFiscal(e.target.checked)}
            />
            Emitir factura automaticamente após pagamento AppyPay
          </label>
        ) : (
          <p className="self-end text-xs text-amber-800">
            Plano Starter: use export AGT manual ou actualize para Business para emissão automática.
          </p>
        )}
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {(selected?.config_fields ?? []).map((field) => (
          <div key={field.key}>
            <label className="text-xs font-medium text-zinc-600">{field.label_pt}</label>
            <Input
              type={field.secret ? "password" : "text"}
              className="mt-1"
              placeholder={field.default}
              value={config[field.key] ?? ""}
              onChange={(e) => setConfig((c) => ({ ...c, [field.key]: e.target.value }))}
            />
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={() => void save()} disabled={busy}>
          Guardar
        </Button>
        <Button variant="outline" onClick={() => void testConn()} disabled={busy}>
          Testar ligação
        </Button>
      </div>

      {documents.length > 0 ? (
        <div className="mt-6 border-t border-zinc-100 pt-4">
          <h3 className="flex items-center gap-1.5 text-sm font-bold text-zinc-800">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            Documentos fiscais (assinatura)
          </h3>
          <ul className="mt-2 space-y-2">
            {documents.map((d) => (
              <li
                key={d.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-zinc-50 px-3 py-2 text-sm"
              >
                <span>
                  {d.provider_code} · {d.status}
                  {d.external_ref ? ` · ref ${d.external_ref}` : ""}
                </span>
                {d.has_agt_export ? (
                  <Button variant="outline" size="sm" onClick={() => void downloadAgt(d.id)}>
                    <Download className="mr-1 h-3.5 w-3.5" />
                    Export AGT
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
