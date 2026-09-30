"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ExternalLink, FileSpreadsheet, FileText, Pencil, Plus, QrCode, Search, Sparkles, Trash2, Upload } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { MoneyInput } from "@/components/ui/money-input";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { Select } from "@/components/ui/select";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { AutoIngestionPreviewModal } from "@/features/projects/components/auto-ingestion-preview-modal";
import { ProjectCallout } from "@/features/projects/components/project-callout";
import { ProjectScrollPanel } from "@/features/projects/components/project-scroll-panel";
import {
  ProjectSectionNav,
  type ProjectSection,
} from "@/features/projects/components/project-section-nav";
import type { AppLocale } from "@/i18n";
import { ApiError } from "@/lib/api/http-client";
import { ingestionApi } from "@/lib/api/ingestion-api";
import { projectsApi } from "@/lib/api/projects-api";
import { subscriptionApi } from "@/lib/api/subscription-api";
import { parseMoneyInput } from "@/lib/utils/format";
import type {
  AuditTrailEntry,
  AutoIngestionPreview,
  Budget,
  CostItem,
  ProformaInvoice,
  ScrapingJob,
  ScrapingResult,
  ScrapingSource,
  TransparencyDocument,
} from "@/lib/types/ingestion";
import type { CompanyNifLookup, Project } from "@/lib/types/project";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

const SOURCE_CHANNEL_LABEL: Record<string, string> = {
  manual: "Manual",
  excel: "Excel",
  scraping: "Scraping",
};

const MARKETPLACE_LABEL: Record<string, string> = {
  jumia: "Jumia Angola",
  jiji: "Jiji Angola",
  kikolo: "Kikolo Online",
  socia: "Socia.ao",
  praca_digital: "Praça Digital",
  facebook_marketplace: "Facebook Marketplace",
  referencia_sectorial: "Referência setorial",
};

function formatCostItemSource(item: CostItem): string {
  if (item.source_label?.trim()) return item.source_label;

  const meta = (item.metadata ?? {}) as Record<string, unknown>;
  if (typeof meta.source_display === "string" && meta.source_display.trim()) {
    return meta.source_display.trim();
  }

  const priceSource = meta.price_source ?? meta.scraping_source;
  if (typeof priceSource === "string" && priceSource.trim()) {
    const code = priceSource.trim();
    return MARKETPLACE_LABEL[code] ?? code.replace(/_/g, " ");
  }

  // Auto-ingestão / scraping: preferir nome do fornecedor ao canal genérico
  if (item.supplier_name?.trim() && (meta.auto_ingestion || item.source === "scraping")) {
    return item.supplier_name.trim();
  }

  return SOURCE_CHANNEL_LABEL[item.source] ?? item.source;
}

function formatMoney(
  amount: string | number | undefined,
  currency = "AOA",
  intlLocale = "pt-AO",
) {
  const value = typeof amount === "number" ? amount : parseFloat(String(amount ?? "0"));
  try {
    return new Intl.NumberFormat(intlLocale, {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(Number.isFinite(value) ? value : 0);
  } catch {
    return `${amount ?? "0"} ${currency}`;
  }
}

async function copyVerifyLink(url: string, locale: AppLocale) {
  try {
    await navigator.clipboard.writeText(url);
    toast.success(
      locale === "en"
        ? "Link copied — paste in Chrome on your phone"
        : "Link copiado — cole no Chrome do telemóvel",
    );
  } catch {
    toast.error(
      locale === "en"
        ? "Could not copy. Select the link manually."
        : "Não foi possível copiar. Seleccione o link manualmente.",
    );
  }
}

function downloadQrPng(base64: string, filename: string, locale: AppLocale) {
  const a = document.createElement("a");
  a.href = `data:image/png;base64,${base64}`;
  a.download = filename;
  a.click();
  toast.success(
    locale === "en"
      ? "QR image saved — open on your phone and use Google Lens"
      : "Imagem QR guardada — abra no telemóvel e use o Google Lens",
  );
}

function QrScanTips({ url }: { url: string | null }) {
  const { locale } = useI18n();
  if (!url) return null;
  const isLan = /192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\./.test(url);
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50/80 p-3 text-xs text-amber-950">
      <p className="font-semibold">
        {locale === "en" ? "Android tips" : "Dicas para Android"}
      </p>
      <ul className="mt-2 list-disc space-y-1 pl-4">
        <li>
          {locale === "en" ? (
            <>Phone and PC on the <strong>same Wi‑Fi</strong> (no VPN).</>
          ) : (
            <>Telemóvel e PC na <strong>mesma Wi‑Fi</strong> (sem VPN).</>
          )}
        </li>
        <li>
          {locale === "en" ? (
            <>If the camera does not detect: use <strong>Copy link</strong> and open in Chrome.</>
          ) : (
            <>Se a câmara não detectar: use <strong>Copiar link</strong> e abra no Chrome.</>
          )}
        </li>
        <li>
          {locale === "en" ? (
            <>Or download the PNG and open with <strong>Google Lens</strong>.</>
          ) : (
            <>Ou descarregue o PNG e abra com <strong>Google Lens</strong>.</>
          )}
        </li>
        <li>
          {locale === "en"
            ? "Screen brightness at maximum; large QR (not too close)."
            : "Brilho do ecrã ao máximo; QR grande (não demasiado perto)."}
        </li>
        {isLan ? (
          <li>
            {locale === "en" ? "Link uses local IP — confirm on phone: " : "O link usa IP local — confirme no telemóvel: "}
            <span className="font-mono">{url.split("/verify")[0]}</span>
          </li>
        ) : null}
      </ul>
    </div>
  );
}

export function IngestionTab({
  project,
  onCostsChanged,
  onProjectUpdated,
}: {
  project: Project;
  onCostsChanged?: () => void;
  onProjectUpdated?: () => void;
}) {
  const { user } = useAuth();
  const { t, locale, intlLocale } = useI18n();
  const fileRef = useRef<HTMLInputElement>(null);

  function budgetStatusLabel(status: string): string {
    if (status === "draft") return t("ingestion.draft");
    if (status === "approved") return t("ingestion.approved");
    if (status === "superseded") return t("ingestion.superseded");
    return status;
  }

  const fmtMoney = (amount: string | number | undefined, currency?: string) =>
    formatMoney(amount, currency || project.currency, intlLocale);
  const [items, setItems] = useState<CostItem[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [proformas, setProformas] = useState<ProformaInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [addModal, setAddModal] = useState(false);
  const [lookingUpNif, setLookingUpNif] = useState(false);
  const [supplierInfo, setSupplierInfo] = useState<CompanyNifLookup | null>(null);
  const [newItem, setNewItem] = useState({
    item_type: "capex",
    category: "",
    description: "",
    quantity: "1",
    unit_price: "",
    supplier_nif: "",
  });

  const [scrapingSources, setScrapingSources] = useState<ScrapingSource[]>([]);
  const [scrapeQuery, setScrapeQuery] = useState("");
  const [selectedSource, setSelectedSource] = useState("");
  const [scrapingJobs, setScrapingJobs] = useState<ScrapingJob[]>([]);
  const [jobModal, setJobModal] = useState<{
    job: ScrapingJob;
    results: ScrapingResult[];
  } | null>(null);
  const [selectingId, setSelectingId] = useState<string | null>(null);
  const [auditModal, setAuditModal] = useState(false);
  const [auditEntries, setAuditEntries] = useState<AuditTrailEntry[]>([]);
  const [autoRunning, setAutoRunning] = useState(false);
  const [autoPreview, setAutoPreview] = useState<AutoIngestionPreview | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [transparency, setTransparency] = useState<TransparencyDocument | null>(null);
  const [autoSelections, setAutoSelections] = useState<
    Record<string, { quantity: string; include: boolean }>
  >({});
  const [editItem, setEditItem] = useState<CostItem | null>(null);
  const [editForm, setEditForm] = useState({
    category: "",
    description: "",
    quantity: "",
    unit_price: "",
  });
  const [savingEdit, setSavingEdit] = useState(false);
  const [qrBudget, setQrBudget] = useState<Budget | null>(null);
  const [qrProforma, setQrProforma] = useState<ProformaInvoice | null>(null);
  const [generatingProformaId, setGeneratingProformaId] = useState<string | null>(null);
  const [generatingInsights, setGeneratingInsights] = useState(false);
  const [mySubscription, setMySubscription] = useState<MySubscriptionResponse | null>(null);
  const [section, setSection] = useState("items");

  const canEdit = user?.role === "admin" || (user?.role === "financial" && project.is_owner);
  const autoIngestionAllowed =
    user?.role === "admin" || mySubscription?.capabilities?.auto_ingestion_enabled === true;
  const scrapingAllowed =
    user?.role === "admin" || mySubscription?.capabilities?.scraping_enabled === true;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [costRes, budgetRes, proformaRes] = await Promise.all([
        ingestionApi.listCostItems(project.id),
        ingestionApi.listBudgets(project.id),
        ingestionApi.listProformas(project.id).catch(() => ({ items: [], total: 0 })),
      ]);
      setItems(Array.isArray(costRes.items) ? costRes.items : []);
      setBudgets(Array.isArray(budgetRes.items) ? budgetRes.items : []);
      setProformas(Array.isArray(proformaRes.items) ? proformaRes.items : []);
      try {
        const res = await ingestionApi.listScrapingSources();
        setScrapingSources(Array.isArray(res.items) ? res.items : []);
      } catch {
        setScrapingSources([]);
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.loadError"));
    } finally {
      setLoading(false);
    }
  }, [project.id, t]);

  function notifyBalance() {
    onCostsChanged?.();
  }

  async function reloadAfterMutation() {
    await load();
    notifyBalance();
  }

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (user?.role === "admin") return;
    void subscriptionApi
      .getMySubscription()
      .then(setMySubscription)
      .catch(() => setMySubscription(null));
  }, [user?.role]);

  async function handleUpload(file: File) {
    setUploading(true);
    try {
      const result = await ingestionApi.importExcel(project.id, file);
      toast.success(
        locale === "en"
          ? `${result.imported} item(s) imported`
          : `${result.imported} item(ns) importado(s)`,
      );
      void reloadAfterMutation();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.importError"));
    } finally {
      setUploading(false);
    }
  }

  async function handleLookupSupplierNif() {
    const nif = newItem.supplier_nif.trim();
    if (!nif) {
      toast.error(t("ingestion.nifRequired"));
      return;
    }
    setLookingUpNif(true);
    try {
      const result = await projectsApi.lookupNif(nif);
      setSupplierInfo(result);
      setNewItem((p) => ({ ...p, supplier_nif: result.nif }));
      toast.success(
        locale === "en"
          ? `Supplier found: ${result.company_name}`
          : `Fornecedor encontrado: ${result.company_name}`,
      );
    } catch (error) {
      setSupplierInfo(null);
      toast.error(
        error instanceof ApiError ? error.message : t("ingestion.nifLookupFail"),
      );
    } finally {
      setLookingUpNif(false);
    }
  }

  function resetAddForm() {
    setNewItem({
      item_type: "capex",
      category: "",
      description: "",
      quantity: "1",
      unit_price: "",
      supplier_nif: "",
    });
    setSupplierInfo(null);
  }

  async function handleAddItem() {
    const unitPrice = parseMoneyInput(newItem.unit_price);
    const quantity = parseMoneyInput(newItem.quantity) || "1";
    const nif = newItem.supplier_nif.trim();
    if (!newItem.category.trim() || !newItem.description.trim() || !unitPrice) {
      toast.error(t("ingestion.fillRequired"));
      return;
    }
    if (!nif) {
      toast.error(t("ingestion.nifConsultRequired"));
      return;
    }
    if (!supplierInfo) {
      toast.error(t("ingestion.nifBeforeAdd"));
      return;
    }
    try {
      await ingestionApi.createCostItem(project.id, {
        item_type: newItem.item_type,
        category: newItem.category,
        description: newItem.description,
        quantity,
        unit_price: unitPrice,
        supplier_nif: nif,
        supplier_name: supplierInfo.company_name,
      });
      toast.success(t("ingestion.itemAdded"));
      setAddModal(false);
      resetAddForm();
      void reloadAfterMutation();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.addError"));
    }
  }

  async function handleDelete(itemId: string) {
    try {
      await ingestionApi.deleteCostItem(project.id, itemId);
      toast.success(t("ingestion.itemRemoved"));
      setItems((prev) => prev.filter((i) => i.id !== itemId));
      notifyBalance();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.removeError"));
    }
  }

  function openEditItem(item: CostItem) {
    setEditItem(item);
    setEditForm({
      category: item.category,
      description: item.description,
      quantity: item.quantity,
      unit_price: item.unit_price,
    });
  }

  async function handleSaveEdit() {
    if (!editItem) return;
    const unitPrice = parseMoneyInput(editForm.unit_price);
    const quantity = parseMoneyInput(editForm.quantity);
    if (!editForm.category.trim() || !editForm.description.trim() || !unitPrice || !quantity) {
      toast.error(t("ingestion.fillEdit"));
      return;
    }
    setSavingEdit(true);
    try {
      await ingestionApi.updateCostItem(project.id, editItem.id, {
        category: editForm.category,
        description: editForm.description,
        quantity,
        unit_price: unitPrice,
      });
      toast.success(t("ingestion.itemUpdated"));
      setEditItem(null);
      void reloadAfterMutation();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.updateError"));
    } finally {
      setSavingEdit(false);
    }
  }

  async function handleGenerateInsights() {
    setGeneratingInsights(true);
    try {
      await projectsApi.generateStrategicInsights(project.id);
      toast.success(t("ingestion.insightsGenerated"));
      onProjectUpdated?.();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.insightsError"));
    } finally {
      setGeneratingInsights(false);
    }
  }

  async function handleGenerateBudget() {
    if (items.length === 0) {
      toast.error(t("ingestion.needItemsBudget"));
      return;
    }
    try {
      await ingestionApi.generateBudget(project.id);
      toast.success(t("ingestion.budgetGenerated"));
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.budgetError"));
    }
  }

  async function handleApprove(budgetId: string) {
    try {
      await ingestionApi.approveBudget(project.id, budgetId);
      toast.success(t("ingestion.budgetApproved"));
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.approveError"));
    }
  }

  async function handleGenerateProforma(budgetId: string) {
    setGeneratingProformaId(budgetId);
    try {
      const result = await ingestionApi.generateProforma(project.id, budgetId, {
        client_name: project.company_name ?? undefined,
        client_tax_id: project.company_tax_id ?? undefined,
      });
      toast.success(
        locale === "en"
          ? `Proforma invoice ${result.invoice_number} generated`
          : `Fatura proforma ${result.invoice_number} gerada`,
      );
      void load();
      setQrProforma(result);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.proformaError"));
    } finally {
      setGeneratingProformaId(null);
    }
  }

  async function handleStartScraping() {
    if (!scrapeQuery.trim()) {
      toast.error(t("ingestion.searchRequired"));
      return;
    }
    setScraping(true);
    try {
      const sources = selectedSource ? [selectedSource] : undefined;
      const res = await ingestionApi.startScraping(project.id, scrapeQuery.trim(), sources);
      const job = res.job;
      const results = Array.isArray(res.results) ? res.results : [];
      toast.success(
        results.length > 0
          ? locale === "en"
            ? `Scraping complete: ${results.length} result(s)`
            : `Scraping concluído: ${results.length} resultado(s)`
          : t("ingestion.scrapingEmpty"),
      );
      setScrapingJobs((prev) => [job, ...prev.filter((j) => j.id !== job.id)]);
      setJobModal({ job, results });
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.scrapingError"));
    } finally {
      setScraping(false);
    }
  }

  async function openJob(jobId: string) {
    try {
      const res = await ingestionApi.getScrapingJob(project.id, jobId);
      setJobModal({
        job: res.job,
        results: Array.isArray(res.results) ? res.results : [],
      });
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.jobError"));
    }
  }

  async function handleSelectResult(result: ScrapingResult) {
    setSelectingId(result.id);
    try {
      await ingestionApi.selectScrapingResult(project.id, result.id, {
        item_type: "capex",
        category: locale === "en" ? "Supplier (scraping)" : "Fornecedor (scraping)",
        quantity: "1",
      });
      toast.success(t("ingestion.supplierSelected"));
      setJobModal((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.map((r) =>
                r.id === result.id ? { ...r, is_selected: true } : r,
              ),
            }
          : prev,
      );
      void reloadAfterMutation();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("ingestion.selectSupplierError"));
    } finally {
      setSelectingId(null);
    }
  }

  async function handleOpenAudit() {
    try {
      const res = await ingestionApi.getAuditTrail(project.id);
      setAuditEntries(Array.isArray(res.items) ? res.items : []);
      setAuditModal(true);
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : locale === "en"
            ? "Failed to fetch audit trail"
            : "Erro ao obter audit trail",
      );
    }
  }

  async function handlePreviewAuto() {
    try {
      const preview = await ingestionApi.previewAutoIngestion(project.id);
      setAutoPreview(preview);
      const initial: Record<string, { quantity: string; include: boolean }> = {};
      for (const item of preview.items) {
        initial[item.key] = { quantity: item.quantity || "1", include: true };
      }
      setAutoSelections(initial);
      setPreviewOpen(true);
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : locale === "en"
            ? "Failed to preview catalogue"
            : "Erro ao pré-visualizar catálogo",
      );
    }
  }

  async function handleRunAuto(replaceExisting: boolean) {
    if (!autoPreview) return;
    const payloadItems = autoPreview.items.map((item) => {
      const sel = autoSelections[item.key];
      return {
        key: item.key,
        quantity: sel?.quantity || item.quantity || "1",
        include: sel?.include !== false,
      };
    });
    if (!payloadItems.some((i) => i.include)) {
      toast.error(
        locale === "en"
          ? "Select at least one item with quantity"
          : "Seleccione pelo menos um item com quantidade",
      );
      return;
    }
    setAutoRunning(true);
    try {
      const result = await ingestionApi.runAutoIngestion(project.id, {
        replace_existing: replaceExisting,
        generate_proforma: true,
        items: payloadItems,
      });
      setTransparency(result.transparency_document);
      setPreviewOpen(false);
      toast.success(
        locale === "en"
          ? `Auto ingestion: ${result.items_count} items, budget and proforma generated`
          : `Ingestão automática: ${result.items_count} itens, orçamento e proforma gerados`,
      );
      void reloadAfterMutation();
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : locale === "en"
            ? "Auto ingestion failed"
            : "Erro na ingestão automática";
      if (message.toLowerCase().includes("já tem itens") || message.toLowerCase().includes("already has items")) {
        const ok = window.confirm(
          locale === "en"
            ? "This project already has items. Replace them with auto-ingestion items?"
            : "O projecto já tem itens. Substituir pelos itens da ingestão automática?",
        );
        if (ok) {
          setAutoRunning(false);
          await handleRunAuto(true);
          return;
        }
      }
      toast.error(message);
    } finally {
      setAutoRunning(false);
    }
  }

  if (loading) return <PageLoader />;

  const ingestionSections: ProjectSection[] = [
    { id: "items", label: t("ingestion.costItems"), count: items.length || undefined },
    {
      id: "sources",
      label: locale === "en" ? "Sources" : "Fontes",
      count: scrapingJobs.length || undefined,
    },
    {
      id: "documents",
      label: locale === "en" ? "Documents" : "Documentos",
      count: budgets.length + proformas.length || undefined,
    },
    { id: "insights", label: t("ingestion.insights") },
  ];

  const toolbar = canEdit ? (
    <Card variant="panel" className="!p-3">
      <div className="flex flex-wrap gap-2">
        <Button size="sm" onClick={() => setAddModal(true)}>
          <Plus className="h-4 w-4" /> {locale === "en" ? "Add item" : "Adicionar item"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => fileRef.current?.click()} loading={uploading}>
          <Upload className="h-4 w-4" /> {locale === "en" ? "Import Excel" : "Importar Excel"}
        </Button>
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx,.xls"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void handleUpload(file);
            e.target.value = "";
          }}
        />
        <Button variant="secondary" size="sm" onClick={() => void handleGenerateBudget()}>
          <FileSpreadsheet className="h-4 w-4" /> {locale === "en" ? "Generate budget" : "Gerar orçamento"}
        </Button>
        <Button
          size="sm"
          onClick={() => {
            setSection("sources");
            void handlePreviewAuto();
          }}
          loading={autoRunning}
          disabled={!autoIngestionAllowed}
        >
          <Sparkles className="h-4 w-4" /> {locale === "en" ? "Auto ingestion" : "Ingestão automática"}
        </Button>
        {canEdit ? (
          <Button variant="ghost" size="sm" onClick={() => void handleOpenAudit()}>
            {locale === "en" ? "Audit trail" : "Audit trail"}
          </Button>
        ) : null}
      </div>
    </Card>
  ) : (
    <ProjectCallout variant="info">
      {locale === "en"
        ? "You have view-only access. Data ingestion is done by the project owner."
        : "Tem acesso de visualização. A ingestão de dados é feita pelo proprietário."}
    </ProjectCallout>
  );

  return (
    <div className="space-y-3">
      {toolbar}

      {canEdit && !autoIngestionAllowed ? (
        <ProjectCallout variant="warning" title={locale === "en" ? "Plan limitation" : "Limitação do plano"}>
          {locale === "en" ? (
            <>
              Automatic ingestion is not included in your plan. Starter includes 50 scraping items/month.{" "}
              <a href="/planos" className="font-semibold text-teal-800 underline">
                Upgrade at /planos
              </a>
            </>
          ) : (
            <>
              Ingestão automática não incluída no plano Starter (50 itens scraping/mês).{" "}
              <a href="/planos" className="font-semibold text-teal-800 underline">
                Actualize em /planos
              </a>
            </>
          )}
        </ProjectCallout>
      ) : null}

      <ProjectSectionNav sections={ingestionSections} active={section} onChange={setSection} dense />

      {section === "items" ? (
        <Card variant="panel">
          <CardHeader
            compact
            title={t("ingestion.costItems")}
            description={t("ingestion.costItemsDesc", { count: items.length })}
          />
          {items.length === 0 ? (
            <EmptyState
              compact
              title={t("ingestion.noCostItems")}
              description={t("ingestion.noCostItemsDesc")}
              action={
                canEdit ? (
                  <Button size="sm" onClick={() => setAddModal(true)}>
                    <Plus className="h-4 w-4" /> {locale === "en" ? "Add item" : "Adicionar item"}
                  </Button>
                ) : undefined
              }
            />
          ) : (
            <ProjectScrollPanel maxHeight="max-h-[min(56vh,540px)]">
              <table className="min-w-full text-sm">
                <thead className="sticky top-0 bg-zinc-50 text-left text-xs uppercase text-zinc-500">
                  <tr>
                    <th className="p-2">{locale === "en" ? "Type" : "Tipo"}</th>
                    <th className="p-2">{t("ingestion.category")}</th>
                    <th className="p-2">{t("ingestion.description")}</th>
                    <th className="p-2">{t("ingestion.quantity")}</th>
                    <th className="p-2">{t("ingestion.unitPrice")}</th>
                    <th className="p-2">{locale === "en" ? "Total" : "Total"}</th>
                    <th className="p-2">{locale === "en" ? "Supplier" : "Fornecedor"}</th>
                    {canEdit ? <th className="p-2" /> : null}
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.id} className="border-t border-zinc-100 hover:bg-zinc-50/60">
                      <td className="p-2">
                        <Badge variant={item.item_type === "capex" ? "info" : "default"}>
                          {item.item_type.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="p-2">{item.category}</td>
                      <td className="max-w-xs truncate p-2">{item.description}</td>
                      <td className="p-2 tabular-nums">{item.quantity}</td>
                      <td className="p-2 tabular-nums">
                        {formatMoney(item.unit_price, item.currency || project.currency, intlLocale)}
                      </td>
                      <td className="p-2 font-semibold tabular-nums">
                        {formatMoney(item.total_amount, item.currency || project.currency, intlLocale)}
                      </td>
                      <td className="max-w-[10rem] p-2">
                        {item.supplier_name ? (
                          <div className="leading-tight">
                            <p className="truncate font-medium">{item.supplier_name}</p>
                            {item.supplier_nif ? (
                              <p className="text-xs text-zinc-500">NIF {item.supplier_nif}</p>
                            ) : null}
                          </div>
                        ) : (
                          <span className="text-zinc-400">—</span>
                        )}
                      </td>
                      {canEdit ? (
                        <td className="p-2">
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => openEditItem(item)}>
                              <Pencil className="h-4 w-4 text-zinc-600" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => void handleDelete(item.id)}>
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </div>
                        </td>
                      ) : null}
                    </tr>
                  ))}
                </tbody>
              </table>
            </ProjectScrollPanel>
          )}
        </Card>
      ) : null}

      {section === "sources" ? (
        <div className="grid gap-4 xl:grid-cols-2">
          {canEdit ? (
            <Card variant="panel">
              <CardHeader
                compact
                title={t("ingestion.autoIngestTitle")}
                description={
                  locale === "en"
                    ? "Sector catalogue → market prices → budget + proforma"
                    : "Catálogo setorial → preços de mercado → orçamento + proforma"
                }
              />
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  onClick={() => void handlePreviewAuto()}
                  loading={autoRunning}
                  disabled={!autoIngestionAllowed}
                >
                  <Sparkles className="h-4 w-4" />{" "}
                  {locale === "en" ? "View catalogue" : "Ver catálogo"}
                </Button>
                {transparency ? (
                  <Button variant="outline" size="sm" onClick={() => setTransparency({ ...transparency })}>
                    {locale === "en" ? "Transparency doc" : "Doc. transparência"}
                  </Button>
                ) : null}
              </div>
            </Card>
          ) : null}

          <Card variant="panel" className={canEdit ? "" : "xl:col-span-2"}>
            <CardHeader compact title={t("ingestion.scrapingTitle")} description={t("ingestion.scrapingDesc")} />
            <div className="space-y-3">
              {canEdit ? (
                <>
                  <Input
                    placeholder={
                      locale === "en" ? "Search (e.g. cement 50kg)" : "Pesquisar (ex: cimento 50kg)"
                    }
                    value={scrapeQuery}
                    onChange={(e) => setScrapeQuery(e.target.value)}
                  />
                  <Select
                    label={locale === "en" ? "Source" : "Fonte"}
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                  >
                    <option value="">
                      {locale === "en" ? "All active sources" : "Todas as fontes activas"}
                    </option>
                    {scrapingSources
                      .slice()
                      .sort((a, b) => a.name.localeCompare(b.name, locale === "en" ? "en" : "pt"))
                      .map((s) => (
                        <option key={s.code} value={s.code}>
                          {s.name}
                          {s.categories?.length ? ` · ${s.categories[0]}` : ""}
                        </option>
                      ))}
                  </Select>
                  <Button
                    size="sm"
                    onClick={() => void handleStartScraping()}
                    loading={scraping}
                    disabled={!scrapingAllowed}
                  >
                    {locale === "en" ? "Start scraping" : "Iniciar scraping"}
                  </Button>
                  {!scrapingAllowed ? (
                    <p className="text-xs text-amber-700">
                      {locale === "en" ? "Requires Starter plan or higher." : "Requer plano Starter ou superior."}{" "}
                      <a href="/planos" className="underline">
                        /planos
                      </a>
                    </p>
                  ) : null}
                </>
              ) : null}

              {scrapingJobs.length > 0 ? (
                <ProjectScrollPanel maxHeight="max-h-[min(36vh,320px)]">
                  <ul className="divide-y divide-zinc-100">
                    {scrapingJobs.map((job) => (
                      <li key={job.id} className="flex items-center justify-between gap-2 px-3 py-2.5">
                        <div className="min-w-0">
                          <p className="truncate font-medium">{job.search_query}</p>
                          <p className="text-xs text-zinc-500">
                            {job.status} · {job.results_count ?? 0}{" "}
                            {locale === "en" ? "result(s)" : "resultado(s)"}
                          </p>
                        </div>
                        <Button size="sm" variant="outline" onClick={() => void openJob(job.id)}>
                          {locale === "en" ? "View" : "Ver"}
                        </Button>
                      </li>
                    ))}
                  </ul>
                </ProjectScrollPanel>
              ) : (
                <EmptyState
                  compact
                  title={
                    locale === "en" ? "No scraping jobs" : "Sem jobs de scraping"
                  }
                  description={
                    canEdit
                      ? locale === "en"
                        ? "Search a product to start."
                        : "Pesquise um produto para iniciar."
                      : undefined
                  }
                />
              )}
            </div>
          </Card>
        </div>
      ) : null}

      {section === "documents" ? (
        <div className="grid gap-4 xl:grid-cols-2">
          <Card variant="panel">
            <CardHeader
              compact
              title={t("ingestion.budgets")}
              description={t("ingestion.budgetsDesc", { count: budgets.length })}
            />
            {budgets.length === 0 ? (
              <EmptyState compact title={t("ingestion.noBudgets")} description={t("ingestion.noBudgetsDesc")} />
            ) : (
              <ul className="space-y-2">
                {budgets.map((budget) => (
                  <li
                    key={budget.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-zinc-100 bg-zinc-50/50 px-3 py-2.5 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="font-semibold">
                        {budget.budget_number || budget.title} —{" "}
                        {formatMoney(budget.total_amount, budget.currency || project.currency, intlLocale)}
                      </p>
                      <p className="text-xs text-zinc-500">{budgetStatusLabel(budget.status)}</p>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <Badge variant={budget.status === "approved" ? "success" : "default"}>
                        {budgetStatusLabel(budget.status)}
                      </Badge>
                      {budget.qr_code_image ? (
                        <Button size="sm" variant="outline" onClick={() => setQrBudget(budget)}>
                          <QrCode className="h-4 w-4" />
                        </Button>
                      ) : null}
                      {canEdit && budget.status === "approved" ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          loading={generatingProformaId === budget.id}
                          onClick={() => void handleGenerateProforma(budget.id)}
                        >
                          <FileText className="h-4 w-4" />
                        </Button>
                      ) : null}
                      {canEdit && budget.status !== "approved" ? (
                        <Button size="sm" onClick={() => void handleApprove(budget.id)}>
                          {locale === "en" ? "Approve" : "Aprovar"}
                        </Button>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card variant="panel">
            <CardHeader
              compact
              title={t("ingestion.proformas")}
              description={
                locale === "en"
                  ? `${proformas.length} invoice(s) · UC17`
                  : `${proformas.length} fatura(s) · UC17`
              }
            />
            {proformas.length === 0 ? (
              <EmptyState compact title={t("ingestion.noProformas")} description={t("ingestion.noProformasDesc")} />
            ) : (
              <ul className="space-y-2">
                {proformas.map((invoice) => (
                  <li
                    key={invoice.id}
                    className="flex items-center justify-between gap-2 rounded-xl border border-zinc-100 px-3 py-2.5 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-semibold">
                        {invoice.invoice_number} — {invoice.client_name}
                      </p>
                      <p className="text-xs text-zinc-500">
                        {fmtMoney(invoice.total_amount, invoice.currency || project.currency)} ·{" "}
                        {new Date(invoice.issued_at).toLocaleDateString(intlLocale)}
                      </p>
                    </div>
                    {invoice.qr_code_image ? (
                      <Button size="sm" variant="outline" onClick={() => setQrProforma(invoice)}>
                        <QrCode className="h-4 w-4" />
                      </Button>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      ) : null}

      {section === "insights" ? (
        <Card variant="panel">
          <CardHeader compact title={t("ingestion.insights")} description={t("ingestion.insightsDesc")} />
          <div className="space-y-4">
            {canEdit ? (
              <Button loading={generatingInsights} size="sm" onClick={() => void handleGenerateInsights()}>
                <Sparkles className="h-4 w-4" /> {t("common.generate")}
              </Button>
            ) : null}
            {project.mission || project.vision ? (
              <div className="grid gap-3 md:grid-cols-2">
                {project.mission ? (
                  <div className="rounded-xl border border-teal-100 bg-teal-50/40 p-4">
                    <p className="text-[10px] font-bold uppercase text-teal-800">
                      {locale === "en" ? "Mission" : "Missão"}
                    </p>
                    <p className="mt-2 text-sm leading-relaxed">{project.mission}</p>
                  </div>
                ) : null}
                {project.vision ? (
                  <div className="rounded-xl border border-teal-100 bg-teal-50/40 p-4">
                    <p className="text-[10px] font-bold uppercase text-teal-800">
                      {locale === "en" ? "Vision" : "Visão"}
                    </p>
                    <p className="mt-2 text-sm leading-relaxed">{project.vision}</p>
                  </div>
                ) : null}
              </div>
            ) : (
              <EmptyState
                compact
                title={locale === "en" ? "No insights yet" : "Sem insights ainda"}
                description={
                  locale === "en"
                    ? "Generate Mission, Vision, SWOT and risks automatically."
                    : "Gere Missão, Visão, SWOT e riscos automaticamente."
                }
              />
            )}
            {(project.core_values?.length ?? 0) > 0 ? (
              <ul className="grid gap-2 sm:grid-cols-2">
                {project.core_values!.map((value) => (
                  <li key={value} className="rounded-lg border bg-zinc-50/80 px-3 py-2 text-sm">
                    {value}
                  </li>
                ))}
              </ul>
            ) : null}
            {project.swot_analysis && Object.keys(project.swot_analysis).length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {(["strengths", "weaknesses", "opportunities", "threats"] as const).map((key) => {
                  const labels =
                    locale === "en"
                      ? {
                          strengths: "Strengths",
                          weaknesses: "Weaknesses",
                          opportunities: "Opportunities",
                          threats: "Threats",
                        }
                      : {
                          strengths: "Forças",
                          weaknesses: "Fraquezas",
                          opportunities: "Oportunidades",
                          threats: "Ameaças",
                        };
                  const swotItems = project.swot_analysis?.[key] ?? [];
                  if (!swotItems.length) return null;
                  return (
                    <div key={key} className="rounded-xl border bg-white p-3 shadow-sm">
                      <p className="text-[10px] font-bold uppercase text-zinc-600">{labels[key]}</p>
                      <ul className="mt-2 list-disc space-y-1 pl-4 text-sm">
                        {swotItems.map((entry) => (
                          <li key={entry}>{entry}</li>
                        ))}
                      </ul>
                    </div>
                  );
                })}
              </div>
            ) : null}
            {(project.risk_register?.length ?? 0) > 0 ? (
              <ProjectScrollPanel maxHeight="max-h-[240px]">
                <ul className="space-y-2 p-2">
                  {project.risk_register!.map((risk) => (
                    <li key={risk.code} className="rounded-lg border bg-white p-3 text-sm">
                      <p className="font-semibold">{risk.title}</p>
                      <p className="text-xs text-zinc-500">{risk.severity}</p>
                      <p className="mt-1 text-zinc-700">{risk.mitigation}</p>
                    </li>
                  ))}
                </ul>
              </ProjectScrollPanel>
            ) : null}
            {(project.aipex_incentives?.length ?? 0) > 0 ? (
              <ul className="grid gap-2 sm:grid-cols-2">
                {project.aipex_incentives!.map((inc) => (
                  <li
                    key={inc.code}
                    className="rounded-xl border border-teal-100 bg-teal-50/40 p-3 text-sm"
                  >
                    <p className="font-semibold">{inc.title}</p>
                    <p className="mt-1 text-zinc-700">{inc.description}</p>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        </Card>
      ) : null}

      <Modal
        open={editItem !== null}
        onClose={() => setEditItem(null)}
        title={t("ingestion.editCostItem")}
        size="md"
        footer={
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setEditItem(null)}>
              {t("common.cancel")}
            </Button>
            <Button loading={savingEdit} onClick={() => void handleSaveEdit()}>
              {t("common.save")}
            </Button>
          </div>
        }
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <Input
            label={t("ingestion.category")}
            value={editForm.category}
            onChange={(e) => setEditForm((p) => ({ ...p, category: e.target.value }))}
            className="sm:col-span-2"
          />
          <Input
            label={t("ingestion.description")}
            value={editForm.description}
            onChange={(e) => setEditForm((p) => ({ ...p, description: e.target.value }))}
            className="sm:col-span-2"
          />
          <MoneyInput
            label={t("ingestion.quantity")}
            value={editForm.quantity}
            maxDecimals={4}
            onValueChange={(raw) => setEditForm((p) => ({ ...p, quantity: raw || "1" }))}
          />
          <MoneyInput
            label={t("ingestion.unitPrice")}
            value={editForm.unit_price}
            onValueChange={(raw) => setEditForm((p) => ({ ...p, unit_price: raw }))}
          />
        </div>
      </Modal>

      <Modal
        open={qrBudget !== null}
        onClose={() => setQrBudget(null)}
        title={locale === "en" ? "Traceable budget" : "Orçamento rastreável"}
      >
        {qrBudget ? (
          <div className="space-y-4 text-sm">
            <p>
              <span className="font-medium">{qrBudget.budget_number}</span> ·{" "}
              {fmtMoney(qrBudget.total_amount, qrBudget.currency || project.currency)}
            </p>
            {qrBudget.qr_code_image ? (
              <div className="rounded-xl border bg-white p-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`data:image/png;base64,${qrBudget.qr_code_image}`}
                  alt={locale === "en" ? "Verification QR Code" : "QR Code de verificação"}
                  className="mx-auto h-72 w-72 max-w-full object-contain"
                />
              </div>
            ) : null}
            {qrBudget.qr_code_data ? (
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => void copyVerifyLink(qrBudget.qr_code_data!, locale)}
                >
                  {locale === "en" ? "Copy link" : "Copiar link"}
                </Button>
                {qrBudget.qr_code_image ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      downloadQrPng(
                        qrBudget.qr_code_image!,
                        `orcamento-${qrBudget.budget_number || "qr"}.png`,
                        locale,
                      )
                    }
                  >
                    {t("common.download")} QR (PNG)
                  </Button>
                ) : null}
              </div>
            ) : null}
            {qrBudget.qr_code_data ? (
              <a
                href={qrBudget.qr_code_data}
                target="_blank"
                rel="noopener noreferrer"
                className="block break-all text-emerald-700 underline"
              >
                {qrBudget.qr_code_data}
              </a>
            ) : null}
            <QrScanTips url={qrBudget.qr_code_data} />
            {qrBudget.verification_hash ? (
              <p className="font-mono text-xs text-zinc-500 break-all">
                Hash: {qrBudget.verification_hash}
              </p>
            ) : null}
          </div>
        ) : null}
      </Modal>

      <Modal
        open={qrProforma !== null}
        onClose={() => setQrProforma(null)}
        title={t("ingestion.proformas")}
      >
        {qrProforma ? (
          <div className="space-y-4 text-sm">
            <p>
              <span className="font-medium">{qrProforma.invoice_number}</span> ·{" "}
              {qrProforma.client_name} ·{" "}
              {fmtMoney(qrProforma.total_amount, qrProforma.currency || project.currency)}
            </p>
            {qrProforma.qr_code_image ? (
              <div className="rounded-xl border bg-white p-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`data:image/png;base64,${qrProforma.qr_code_image}`}
                  alt={
                    locale === "en"
                      ? "Proforma invoice QR Code"
                      : "QR Code da fatura proforma"
                  }
                  className="mx-auto h-72 w-72 max-w-full object-contain"
                />
              </div>
            ) : null}
            {qrProforma.qr_code_data ? (
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => void copyVerifyLink(qrProforma.qr_code_data!, locale)}
                >
                  {locale === "en" ? "Copy link" : "Copiar link"}
                </Button>
                {qrProforma.qr_code_image ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      downloadQrPng(
                        qrProforma.qr_code_image!,
                        `proforma-${qrProforma.invoice_number}.png`,
                        locale,
                      )
                    }
                  >
                    {t("common.download")} QR (PNG)
                  </Button>
                ) : null}
              </div>
            ) : null}
            {qrProforma.qr_code_data ? (
              <a
                href={qrProforma.qr_code_data}
                target="_blank"
                rel="noopener noreferrer"
                className="block break-all text-emerald-700 underline"
              >
                {qrProforma.qr_code_data}
              </a>
            ) : null}
            <QrScanTips url={qrProforma.qr_code_data} />
            {qrProforma.verification_hash ? (
              <p className="font-mono text-xs text-zinc-500 break-all">
                Hash: {qrProforma.verification_hash}
              </p>
            ) : null}
          </div>
        ) : null}
      </Modal>

      <Modal
        open={addModal}
        onClose={() => {
          setAddModal(false);
          resetAddForm();
        }}
        title={locale === "en" ? "Add cost item" : "Adicionar item de custo"}
        description={
          locale === "en"
            ? "Consult supplier NIF on AGT before adding."
            : "Consulte o NIF do fornecedor na AGT antes de adicionar."
        }
        size="lg"
        footer={
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setAddModal(false);
                resetAddForm();
              }}
            >
              {t("common.cancel")}
            </Button>
            <Button onClick={() => void handleAddItem()}>
              {locale === "en" ? "Add" : "Adicionar"}
            </Button>
          </div>
        }
      >
        <div className="grid gap-3 sm:grid-cols-2">
          <Select
            label={locale === "en" ? "Type" : "Tipo"}
            value={newItem.item_type}
            onChange={(e) => setNewItem((p) => ({ ...p, item_type: e.target.value }))}
          >
            <option value="capex">CAPEX</option>
            <option value="opex">OPEX</option>
          </Select>
          <Input
            label={t("ingestion.category")}
            value={newItem.category}
            onChange={(e) => setNewItem((p) => ({ ...p, category: e.target.value }))}
          />
          <Input
            label={t("ingestion.description")}
            value={newItem.description}
            onChange={(e) => setNewItem((p) => ({ ...p, description: e.target.value }))}
            className="sm:col-span-2"
          />
          <MoneyInput
            label={t("ingestion.quantity")}
            value={newItem.quantity}
            maxDecimals={4}
            onValueChange={(raw) => setNewItem((p) => ({ ...p, quantity: raw || "1" }))}
          />
          <MoneyInput
            label={t("ingestion.unitPrice")}
            placeholder="Ex: 250.000"
            value={newItem.unit_price}
            onValueChange={(raw) => setNewItem((p) => ({ ...p, unit_price: raw }))}
          />
          <Input
            label={locale === "en" ? "Supplier NIF *" : "NIF do fornecedor *"}
            placeholder="Ex: 5410003284"
            value={newItem.supplier_nif}
            onChange={(e) => {
              setSupplierInfo(null);
              setNewItem((p) => ({ ...p, supplier_nif: e.target.value }));
            }}
          />
          <div className="flex items-end">
            <Button
              type="button"
              variant="outline"
              className="w-full"
              loading={lookingUpNif}
              onClick={() => void handleLookupSupplierNif()}
            >
              <Search className="h-4 w-4" />
              {locale === "en" ? "AGT lookup" : "Buscar AGT"}
            </Button>
          </div>
          {supplierInfo ? (
            <div className="sm:col-span-2 rounded-xl border border-teal-200 bg-teal-50/60 p-3 text-sm text-teal-950">
              <p className="font-semibold">{supplierInfo.company_name}</p>
              <p className="mt-1 text-xs">NIF {supplierInfo.nif}</p>
            </div>
          ) : (
            <p className="sm:col-span-2 text-xs text-zinc-500">
              {locale === "en"
                ? "Look up the NIF on the AGT/MINFIN portal to auto-fill supplier details."
                : "Consulte o NIF no portal AGT/MINFIN para preencher automaticamente os dados do fornecedor."}
            </p>
          )}
        </div>
      </Modal>

      <Modal
        open={jobModal !== null}
        onClose={() => setJobModal(null)}
        title={locale === "en" ? "Scraping results" : "Resultados do scraping"}
      >
        {jobModal ? (
          <div className="space-y-4 text-sm">
            <div>
              <p>
                <span className="font-medium">
                  {locale === "en" ? "Search:" : "Pesquisa:"}
                </span>{" "}
                {jobModal.job.search_query}
              </p>
              <p>
                <span className="font-medium">{t("common.status")}:</span> {jobModal.job.status}
              </p>
              <p>
                <span className="font-medium">
                  {locale === "en" ? "Results:" : "Resultados:"}
                </span>{" "}
                {jobModal.results.length}
              </p>
            </div>

            {jobModal.results.length === 0 ? (
              <p className="text-zinc-500">
                {locale === "en"
                  ? "No products found. Try another term or source."
                  : "Nenhum produto encontrado. Tente outro termo ou outra fonte."}
              </p>
            ) : (
              <ul className="max-h-80 space-y-2 overflow-y-auto">
                {jobModal.results.map((result) => (
                  <li key={result.id} className="rounded-lg border p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium">{result.product_name}</p>
                        <p className="text-zinc-500">
                          {result.supplier_name} · {result.source}
                        </p>
                        <p className="mt-1 font-semibold text-emerald-700">
                          {fmtMoney(result.price, result.currency || project.currency)}
                        </p>
                        {result.product_url ? (
                          <a
                            href={result.product_url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-1 inline-flex items-center gap-1 text-xs text-emerald-700 hover:underline"
                          >
                            {locale === "en" ? "View on site" : "Ver no site"}{" "}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : null}
                      </div>
                      {canEdit ? (
                        <Button
                          size="sm"
                          disabled={result.is_selected}
                          loading={selectingId === result.id}
                          onClick={() => void handleSelectResult(result)}
                        >
                          {result.is_selected
                            ? locale === "en"
                              ? "Selected"
                              : "Seleccionado"
                            : locale === "en"
                              ? "Use"
                              : "Usar"}
                        </Button>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </Modal>

      <Modal
        open={auditModal}
        onClose={() => setAuditModal(false)}
        title={locale === "en" ? "Audit trail" : "Audit trail"}
      >
        {auditEntries.length === 0 ? (
          <p className="text-sm text-zinc-500">
            {locale === "en" ? "No records found." : "Nenhum registo encontrado."}
          </p>
        ) : (
          <ul className="max-h-80 space-y-2 overflow-y-auto text-sm">
            {auditEntries.map((entry) => (
              <li key={entry.id} className="rounded-lg border p-3">
                <p className="font-medium">{entry.action}</p>
                <p className="text-zinc-500">
                  {entry.entity_type} · {new Date(entry.created_at).toLocaleString(intlLocale)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </Modal>

      <AutoIngestionPreviewModal
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        preview={autoPreview}
        selections={autoSelections}
        onSelectionsChange={setAutoSelections}
        running={autoRunning}
        locale={locale}
        t={t}
        onRun={() => void handleRunAuto(false)}
      />

      <Modal
        open={transparency !== null}
        onClose={() => setTransparency(null)}
        title={
          locale === "en"
            ? "Price transparency document"
            : "Documento de transparência de preços"
        }
      >
        {transparency ? (
          <div className="space-y-4 text-sm">
            <p className="text-xs text-zinc-600">{transparency.methodology}</p>
            <p className="text-xs">
              {locale === "en" ? "Sources consulted" : "Fontes consultadas"}:{" "}
              {transparency.sources_consulted.join(", ")}
            </p>
            <div className="max-h-72 overflow-auto">
              <table className="min-w-full text-xs">
                <thead className="bg-zinc-50 text-left">
                  <tr>
                    <th className="p-2">{locale === "en" ? "Item" : "Item"}</th>
                    <th className="p-2">{locale === "en" ? "Price" : "Preço"}</th>
                    <th className="p-2">{locale === "en" ? "Source" : "Fonte"}</th>
                  </tr>
                </thead>
                <tbody>
                  {transparency.lines.map((line, index) => (
                    <tr
                      key={line.item_id ?? `${line.item_type}-${line.description}-${index}`}
                      className="border-t"
                    >
                      <td className="p-2">
                        <p className="font-medium">{line.description}</p>
                        <p className="text-zinc-500">
                          {line.item_type.toUpperCase()} · {line.quantity} {line.unit}
                        </p>
                      </td>
                      <td className="p-2 whitespace-nowrap">
                        {fmtMoney(line.unit_price, line.currency)}
                      </td>
                      <td className="p-2">
                        <p>{line.source}</p>
                        {line.source_url ? (
                          <a
                            href={line.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 text-emerald-700 hover:underline"
                          >
                            {locale === "en" ? "Open" : "Abrir"}{" "}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : null}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="rounded-lg bg-emerald-50 p-3 text-emerald-900">
              <p>CAPEX: {fmtMoney(transparency.totals.capex, transparency.currency)}</p>
              <p>OPEX: {fmtMoney(transparency.totals.opex, transparency.currency)}</p>
              <p className="font-semibold">
                {locale === "en" ? "Total" : "Total"}:{" "}
                {fmtMoney(transparency.totals.grand_total, transparency.currency)}
              </p>
            </div>
            <ol className="list-decimal space-y-1 pl-4 text-xs text-zinc-600">
              {transparency.next_steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
