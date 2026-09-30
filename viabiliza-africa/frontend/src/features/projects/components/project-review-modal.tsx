"use client";

import { useEffect, type ReactNode } from "react";
import {
  Building2,
  CheckCircle2,
  Landmark,
  MapPin,
  Pencil,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SearchableSelectOption } from "@/components/ui/searchable-select";
import type { MetadataOption, ProjectMetadata } from "@/lib/types/project";
import { cn } from "@/lib/utils/cn";

type ReviewValues = Record<string, string | number | boolean | undefined>;

function labelOf(options: MetadataOption[] | undefined, value: string | undefined) {
  if (!value) return "—";
  return options?.find((o) => o.value === value)?.label ?? value;
}

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border border-white/60 bg-white/70 px-3 py-2.5 backdrop-blur-sm">
      <p className="text-[11px] font-medium uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-0.5 text-sm font-medium text-zinc-900">{value || "—"}</p>
    </div>
  );
}

function ReviewSection({
  step,
  title,
  subtitle,
  icon,
  accent,
  onEdit,
  children,
}: {
  step: number;
  title: string;
  subtitle: string;
  icon: ReactNode;
  accent: string;
  onEdit: (step: number) => void;
  children: ReactNode;
}) {
  return (
    <article className="overflow-hidden rounded-2xl border border-zinc-200/80 bg-white shadow-sm">
      <div className={cn("flex items-start justify-between gap-3 px-5 py-4", accent)}>
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/90 text-emerald-700 shadow-sm">
            {icon}
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-900">{title}</h3>
            <p className="text-xs text-zinc-600">{subtitle}</p>
          </div>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="shrink-0 border-white/80 bg-white/90 hover:bg-white"
          onClick={() => onEdit(step)}
        >
          <Pencil className="h-3.5 w-3.5" />
          Editar
        </Button>
      </div>
      <div className="grid gap-2 p-4 sm:grid-cols-2">{children}</div>
    </article>
  );
}

interface ProjectReviewModalProps {
  open: boolean;
  onClose: () => void;
  values: ReviewValues;
  metadata: ProjectMetadata;
  municipalities: MetadataOption[];
  bankBranches: SearchableSelectOption[];
  biVerified: boolean;
  geoInfo: string | null;
  phoneOperator: string | null;
  rateInfo: string | null;
  onEditStep: (step: number) => void;
}

export function ProjectReviewModal({
  open,
  onClose,
  values,
  metadata,
  municipalities,
  bankBranches,
  biVerified,
  geoInfo,
  phoneOperator,
  rateInfo,
  onEditStep,
}: ProjectReviewModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  const branchLabel =
    bankBranches.find((b) => b.value === values.bank_branch)?.label ??
    (values.bank_branch as string) ??
    "—";
  const selectedBank = metadata.banks.find((bank) => bank.value === values.bank_code);

  const handleEdit = (step: number) => {
    onClose();
    onEditStep(step);
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center sm:items-center sm:p-6">
      <div
        className="absolute inset-0 bg-gradient-to-br from-emerald-950/50 via-zinc-900/40 to-teal-950/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />

      <div
        role="dialog"
        aria-modal
        aria-labelledby="review-modal-title"
        className="relative z-10 flex max-h-[92vh] w-full max-w-4xl flex-col overflow-hidden rounded-t-3xl border border-emerald-100/80 bg-gradient-to-b from-white to-emerald-50/30 shadow-2xl shadow-emerald-900/20 sm:rounded-3xl"
      >
        <header className="relative overflow-hidden border-b border-emerald-100/80 px-6 py-5">
          <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-emerald-200/40 blur-2xl" />
          <div className="pointer-events-none absolute -left-6 bottom-0 h-24 w-24 rounded-full bg-teal-200/30 blur-2xl" />
          <div className="relative flex items-start justify-between gap-4">
            <div>
              <Badge variant="success" className="mb-2">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                Revisão final
              </Badge>
              <h2 id="review-modal-title" className="text-xl font-bold tracking-tight text-zinc-900 sm:text-2xl">
                Resumo completo do projecto
              </h2>
              <p className="mt-1 max-w-xl text-sm text-zinc-600">
                Confira todos os dados antes de criar. Pode editar qualquer secção directamente.
              </p>
            </div>
            <Button type="button" variant="ghost" size="sm" onClick={onClose} aria-label="Fechar">
              <X className="h-5 w-5" />
            </Button>
          </div>
        </header>

        <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-6">
          <ReviewSection
            step={0}
            title="Representante legal"
            subtitle="Responsável pela submissão"
            icon={<UserRound className="h-5 w-5" />}
            accent="bg-gradient-to-r from-sky-50 to-emerald-50/80"
            onEdit={handleEdit}
          >
            <Field label="Nome completo" value={values.rep_full_name as string} />
            <Field label="Email" value={values.rep_email as string} />
            <Field
              label="Bilhete de identidade"
              value={
                <span className="inline-flex items-center gap-2">
                  {values.rep_id_number as string}
                  {biVerified ? (
                    <Badge variant="success" className="text-[10px]">
                      Validado
                    </Badge>
                  ) : null}
                </span>
              }
            />
            <Field
              label="Contacto"
              value={
                phoneOperator
                  ? `${values.rep_phone} · ${phoneOperator}`
                  : (values.rep_phone as string)
              }
            />
            <Field label="Função / cargo" value={values.rep_role as string} />
          </ReviewSection>

          <ReviewSection
            step={1}
            title="Empresa"
            subtitle="Localização e contactos comerciais"
            icon={<Building2 className="h-5 w-5" />}
            accent="bg-gradient-to-r from-amber-50/90 to-orange-50/60"
            onEdit={handleEdit}
          >
            <Field label="NIF" value={values.company_tax_id as string} />
            <Field label="Denominação" value={values.company_name as string} />
            <Field
              label="Província"
              value={labelOf(metadata.provinces, values.company_province as string)}
            />
            <Field
              label="Município"
              value={labelOf(municipalities, values.company_municipality as string)}
            />
            <Field label="Morada" value={values.company_address as string} />
            <Field label="Actividade" value={values.company_activity as string} />
            <Field label="Telefone" value={values.company_phone as string} />
            <Field label="Email" value={values.company_email as string} />
            <Field label="Website" value={values.company_website as string} />
            {(values.geocode_verified as boolean) || geoInfo ? (
              <div className="sm:col-span-2">
                <Field
                  label="Geolocalização"
                  value={
                    <span className="inline-flex items-center gap-2 text-emerald-800">
                      <MapPin className="h-3.5 w-3.5 shrink-0" />
                      {geoInfo ||
                        `${values.company_latitude}, ${values.company_longitude}`}
                    </span>
                  }
                />
              </div>
            ) : null}
          </ReviewSection>

          <ReviewSection
            step={2}
            title="Projecto de investimento"
            subtitle="Sector, montante e horizonte"
            icon={<Sparkles className="h-5 w-5" />}
            accent="bg-gradient-to-r from-violet-50/80 to-fuchsia-50/50"
            onEdit={handleEdit}
          >
            <Field label="Nome do projecto" value={values.name as string} />
            <Field label="Sector" value={labelOf(metadata.sectors, values.sector as string)} />
            <Field label="País" value={labelOf(metadata.countries, values.country as string)} />
            <Field label="Moeda" value={labelOf(metadata.currencies, values.currency as string)} />
            <Field
              label="Investimento total"
              value={`${values.investment_amount} ${values.currency}`}
            />
            <Field
              label="Horizonte"
              value={`${values.project_horizon_years} anos`}
            />
            {values.description ? (
              <div className="sm:col-span-2">
                <Field label="Descrição" value={values.description as string} />
              </div>
            ) : null}
          </ReviewSection>

          <ReviewSection
            step={3}
            title="Dados bancários"
            subtitle="Instituição, taxa e agência de atendimento"
            icon={<Landmark className="h-5 w-5" />}
            accent="bg-gradient-to-r from-emerald-50 to-teal-50/80"
            onEdit={handleEdit}
          >
            {selectedBank?.logo ? (
              <div className="relative overflow-hidden rounded-xl border border-emerald-100 bg-gradient-to-r from-white via-emerald-50/50 to-teal-50 p-4 sm:col-span-2">
                <div className="pointer-events-none absolute -right-8 -top-12 h-28 w-28 rounded-full bg-emerald-200/40 blur-2xl" />
                <div className="relative flex flex-col items-center justify-between gap-4 sm:flex-row">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-700">
                      Instituição financiadora
                    </p>
                    <p className="mt-1 text-lg font-bold text-zinc-900">{selectedBank.label}</p>
                    {selectedBank.website ? (
                      <p className="mt-0.5 text-xs text-zinc-500">
                        {selectedBank.website.replace(/^https?:\/\//, "")}
                      </p>
                    ) : null}
                  </div>
                  <div className="flex h-20 w-full items-center justify-center rounded-xl border border-white bg-white px-6 shadow-sm sm:w-52">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedBank.logo}
                      alt={`Logótipo ${selectedBank.label}`}
                      className="max-h-14 max-w-full object-contain"
                      onError={(event) => {
                        event.currentTarget.style.display = "none";
                      }}
                    />
                  </div>
                </div>
              </div>
            ) : null}
            <Field label="Banco" value={labelOf(metadata.banks, values.bank_code as string)} />
            <Field
              label="Tipo de financiamento"
              value={labelOf(metadata.financing_types, values.financing_type as string)}
            />
            <Field
              label="Taxa de desconto / juro"
              value={values.discount_rate ? `${values.discount_rate}%` : "—"}
            />
            <Field
              label="Prazo"
              value={values.loan_term_months ? `${values.loan_term_months} meses` : "—"}
            />
            <div className="sm:col-span-2">
              <Field label="Agência bancária" value={branchLabel} />
            </div>
            {rateInfo ? (
              <div className="sm:col-span-2">
                <Field label="Fonte da taxa" value={rateInfo} />
              </div>
            ) : null}
          </ReviewSection>
        </div>

        <footer className="flex flex-col-reverse gap-3 border-t border-emerald-100/80 bg-white/80 px-4 py-4 backdrop-blur sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p className="text-center text-xs text-zinc-500 sm:text-left">
            Todos os campos podem ser ajustados antes de submeter.
          </p>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Fechar
            </Button>
            <Button type="button" onClick={() => handleEdit(3)}>
              <Pencil className="h-4 w-4" />
              Editar banco
            </Button>
          </div>
        </footer>
      </div>
    </div>
  );
}
