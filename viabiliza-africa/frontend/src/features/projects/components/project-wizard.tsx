"use client";

import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  CheckCircle2,
  Eye,
  FileUp,
  Landmark,
  MapPin,
  Search,
  Sparkles,
  UserRound,
} from "lucide-react";

import { useAuth } from "@/components/providers/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FormStepper, type FormStep } from "@/components/ui/form-stepper";
import { Input } from "@/components/ui/input";
import { MoneyInput } from "@/components/ui/money-input";
import { PageLoader } from "@/components/ui/spinner";
import type { SearchableSelectOption } from "@/components/ui/searchable-select";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { Textarea } from "@/components/ui/textarea";
import { PhoneInput } from "@/components/ui/phone-input";
import { ProjectReviewModal } from "@/features/projects/components/project-review-modal";
import { ApiError } from "@/lib/api/http-client";
import { projectsApi } from "@/lib/api/projects-api";
import type { MetadataOption, Project, ProjectMetadata } from "@/lib/types/project";
import {
  formatBiInput,
  isValidBiFormat,
  isValidLocalPhone,
  normalizeBi,
  normalizeLocalPhone,
} from "@/lib/utils/angola-validation";
import { parseMoneyInput } from "@/lib/utils/format";

const wizardSchema = z.object({
  rep_full_name: z.string().min(2, "Mínimo 2 caracteres"),
  rep_email: z.string().email("Email inválido"),
  rep_id_number: z
    .string()
    .min(14, "BI incompleto")
    .max(14, "BI inválido")
    .refine((v) => isValidBiFormat(v), {
      message: "Formato inválido: 9 dígitos + 2 letras + 3 dígitos (ex: 006151112LA041)",
    }),
  rep_phone: z
    .string()
    .length(9, "Contacto deve ter 9 dígitos")
    .refine((v) => isValidLocalPhone(v), {
      message: "Contacto inválido: 9 dígitos numéricos começando por 9",
    }),
  rep_role: z.string().optional(),
  company_tax_id: z.string().optional(),
  company_name: z.string().min(2, "Mínimo 2 caracteres"),
  company_province: z.string().min(1, "Seleccione a província"),
  company_municipality: z.string().min(1, "Seleccione o município"),
  company_address: z.string().optional(),
  company_activity: z.string().optional(),
  company_phone: z
    .string()
    .optional()
    .refine((v) => !v || v.length === 0 || isValidLocalPhone(v), {
      message: "Telefone inválido: 9 dígitos numéricos começando por 9",
    }),
  company_email: z.union([z.string().email("Email inválido"), z.literal("")]).optional(),
  company_website: z
    .union([z.string().url("URL inválida (ex: https://empresa.co.ao)"), z.literal("")])
    .optional(),
  company_latitude: z.string().optional(),
  company_longitude: z.string().optional(),
  geocode_verified: z.boolean(),
  geocode_source: z.string().optional(),
  name: z.string().min(2, "Mínimo 2 caracteres"),
  description: z.string().optional(),
  sector: z.string().min(1, "Seleccione um sector"),
  country: z.string().min(1, "Seleccione um país"),
  currency: z.string().min(1, "Seleccione uma moeda"),
  investment_amount: z.string().min(1, "Valor obrigatório"),
  project_horizon_years: z.number().min(1).max(50),
  bank_code: z.string().optional(),
  financing_type: z.string().optional(),
  discount_rate: z.string().optional(),
  loan_term_months: z.preprocess((value) => {
    if (value === "" || value === null || value === undefined) return undefined;
    if (typeof value === "number" && (!Number.isFinite(value) || value <= 0)) return undefined;
    const parsed = typeof value === "number" ? value : Number(value);
    if (!Number.isFinite(parsed) || parsed <= 0) return undefined;
    return parsed;
  }, z.number().int().min(1).max(360).optional()),
  bank_branch: z.string().optional(),
  bank_rate_label: z.string().optional(),
  bank_rate_source_url: z.string().optional(),
});

type WizardValues = z.infer<typeof wizardSchema>;

const STEP_FIELDS: (keyof WizardValues)[][] = [
  ["rep_full_name", "rep_email", "rep_id_number", "rep_phone"],
  [
    "company_name",
    "company_province",
    "company_municipality",
    "company_email",
    "company_website",
  ],
  ["name", "sector", "country", "currency", "investment_amount", "project_horizon_years"],
  ["bank_code", "financing_type", "discount_rate", "bank_branch"],
];

const WIZARD_STEPS: FormStep[] = [
  {
    id: "representative",
    title: "Representante",
    description: "Dados pessoais do responsável",
    icon: <UserRound className="h-5 w-5" />,
  },
  {
    id: "company",
    title: "Empresa",
    description: "Localização e contactos",
    icon: <Building2 className="h-5 w-5" />,
  },
  {
    id: "project",
    title: "Projecto",
    description: "Investimento e sector",
    icon: <Sparkles className="h-5 w-5" />,
  },
  {
    id: "bank",
    title: "Banco",
    description: "Financiamento e taxas",
    icon: <Landmark className="h-5 w-5" />,
  },
];

function toSelectOptions(items: MetadataOption[]) {
  return items.map((item) => ({ value: item.value, label: item.label }));
}

interface ProjectWizardProps {
  project?: Project;
  onSuccess?: (project: Project) => void;
}

export function ProjectWizard({ project, onSuccess }: ProjectWizardProps) {
  const router = useRouter();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [metadata, setMetadata] = useState<ProjectMetadata | null>(null);
  const [municipalities, setMunicipalities] = useState<MetadataOption[]>([]);
  const [loadingMunicipalities, setLoadingMunicipalities] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [lookingUpNif, setLookingUpNif] = useState(false);
  const [loadingRate, setLoadingRate] = useState(false);
  const [loadingBranches, setLoadingBranches] = useState(false);
  const [bankBranches, setBankBranches] = useState<SearchableSelectOption[]>([]);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewValues, setReviewValues] = useState<WizardValues | null>(null);
  const [geocoding, setGeocoding] = useState(false);
  const [validatingBi, setValidatingBi] = useState(false);
  const [biVerified, setBiVerified] = useState(!!project?.rep_id_number);
  const [phoneOperator, setPhoneOperator] = useState<string | null>(null);
  const [rateInfo, setRateInfo] = useState<string | null>(
    project?.bank_rate_label
      ? `${project.bank_rate_label}${project.bank_rate_source_url ? ` · ${project.bank_rate_source_url}` : ""}`
      : null,
  );
  const [geoInfo, setGeoInfo] = useState<string | null>(
    project?.geocode_verified
      ? `Localização validada (${project.geocode_source === "google_maps" ? "Google Maps" : "INE"})`
      : null,
  );
  const documentFileRef = useRef<HTMLInputElement>(null);
  const [extractingDoc, setExtractingDoc] = useState(false);

  const form = useForm<WizardValues>({
    resolver: zodResolver(wizardSchema) as Resolver<WizardValues>,
    defaultValues: {
      rep_full_name: project?.rep_full_name ?? user?.full_name ?? "",
      rep_email: project?.rep_email ?? user?.email ?? "",
      rep_id_number: project?.rep_id_number ?? "",
      rep_phone: project?.rep_phone ?? "",
      rep_role: project?.rep_role ?? "",
      company_tax_id: project?.company_tax_id ?? "",
      company_name: project?.company_name ?? "",
      company_province: project?.company_province ?? "",
      company_municipality: project?.company_municipality ?? "",
      company_address: project?.company_address ?? "",
      company_activity: project?.company_activity ?? "",
      company_phone: project?.company_phone ?? "",
      company_email: project?.company_email ?? "",
      company_website: project?.company_website ?? "",
      company_latitude: project?.company_latitude ?? "",
      company_longitude: project?.company_longitude ?? "",
      geocode_verified: project?.geocode_verified ?? false,
      geocode_source: project?.geocode_source ?? "",
      name: project?.name ?? "",
      description: project?.description ?? "",
      sector: project?.sector ?? "",
      country: project?.country ?? "AO",
      currency: project?.currency ?? "AOA",
      investment_amount: project?.investment_amount ?? "",
      project_horizon_years: project?.project_horizon_years ?? 5,
      bank_code: project?.bank_code ?? "",
      financing_type: project?.financing_type ?? "",
      discount_rate: project?.discount_rate ?? "",
      loan_term_months: project?.loan_term_months ?? undefined,
      bank_branch: project?.bank_branch ?? "",
      bank_rate_label: project?.bank_rate_label ?? "",
      bank_rate_source_url: project?.bank_rate_source_url ?? "",
    },
    mode: "onTouched",
  });

  const province = form.watch("company_province");
  const selectedBankCode = form.watch("bank_code") || "";
  const bankBranchRaw = form.watch("bank_branch") || "";
  const branchesRequestRef = useRef(0);

  useEffect(() => {
    void projectsApi.metadata().then(setMetadata);
  }, []);

  useEffect(() => {
    if (!selectedBankCode || !province) {
      setBankBranches([]);
      setLoadingBranches(false);
      return;
    }

    const requestId = ++branchesRequestRef.current;
    setLoadingBranches(true);

    void projectsApi
      .getBankBranches(selectedBankCode, province)
      .then((result) => {
        if (requestId !== branchesRequestRef.current) return;

        const options: SearchableSelectOption[] = result.items.map((item) => ({
          value: item.value,
          label: item.label,
          description: item.description,
        }));

        const current = form.getValues("bank_branch");
        if (current && !options.some((o) => o.value === current || o.label === current)) {
          form.setValue("bank_branch", "");
        }

        setBankBranches(options);
      })
      .catch(() => {
        if (requestId === branchesRequestRef.current) setBankBranches([]);
      })
      .finally(() => {
        if (requestId === branchesRequestRef.current) setLoadingBranches(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload when bank or company province changes
  }, [selectedBankCode, province]);

  useEffect(() => {
    if (!province) {
      setMunicipalities([]);
      return;
    }
    setLoadingMunicipalities(true);
    void projectsApi
      .municipalities(province)
      .then((res) => setMunicipalities(res.municipalities))
      .catch(() => setMunicipalities([]))
      .finally(() => setLoadingMunicipalities(false));
  }, [province]);

  const banks = metadata?.banks ?? [];
  const selectedBank = banks.find((b) => b.value === selectedBankCode) ?? null;

  const handleLookupNif = useCallback(async () => {
    const nif = form.getValues("company_tax_id")?.trim();
    if (!nif) {
      toast.error("Indique o NIF da empresa");
      return;
    }
    setLookingUpNif(true);
    try {
      const result = await projectsApi.lookupNif(nif);
      form.setValue("company_name", result.company_name, { shouldValidate: true });
      if (result.address) form.setValue("company_address", result.address);
      if (result.activity) form.setValue("company_activity", result.activity);
      if (!form.getValues("name")?.trim()) {
        form.setValue("name", `Viabilidade — ${result.company_name}`, { shouldValidate: true });
      }
      toast.success(`Empresa encontrada na AGT: ${result.company_name}`);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Não foi possível consultar o NIF");
    } finally {
      setLookingUpNif(false);
    }
  }, [form]);

  const handleExtractDocument = useCallback(
    async (file: File) => {
      setExtractingDoc(true);
      try {
        const result = await projectsApi.extractCompanyDocument(file);
        const extracted = result.extracted;
        if (extracted.nif) form.setValue("company_tax_id", extracted.nif);
        if (extracted.company_name) {
          form.setValue("company_name", extracted.company_name, { shouldValidate: true });
        }
        if (extracted.address) form.setValue("company_address", extracted.address);
        if (extracted.activity) form.setValue("company_activity", extracted.activity);
        if (extracted.email) form.setValue("company_email", extracted.email);
        if (extracted.phone) form.setValue("company_phone", extracted.phone);
        toast.success(
          `${extracted.fields_found ?? 0} campo(s) extraído(s) do documento. Consulte a AGT para validar o NIF.`,
        );
        if (extracted.nif) {
          await handleLookupNif();
        }
      } catch (error) {
        toast.error(error instanceof ApiError ? error.message : "Erro ao ler documento");
      } finally {
        setExtractingDoc(false);
      }
    },
    [form, handleLookupNif],
  );

  const handleGeocode = useCallback(async () => {
    const prov = form.getValues("company_province");
    const mun = form.getValues("company_municipality");
    if (!prov || !mun) {
      toast.error("Seleccione província e município");
      return;
    }
    setGeocoding(true);
    try {
      const result = await projectsApi.geocode({
        province: prov,
        municipality: mun,
        address: form.getValues("company_address") || undefined,
      });
      form.setValue("company_latitude", result.latitude);
      form.setValue("company_longitude", result.longitude);
      form.setValue("geocode_verified", result.verified);
      form.setValue("geocode_source", result.source);
      if (result.formatted_address && !form.getValues("company_address")?.trim()) {
        form.setValue("company_address", result.formatted_address);
      }
      const sourceLabel = result.source === "google_maps" ? "Google Maps" : "Catálogo INE";
      setGeoInfo(`${result.formatted_address} · ${sourceLabel}`);
      toast.success(`Localização validada via ${sourceLabel}`);
    } catch (error) {
      setGeoInfo(null);
      form.setValue("geocode_verified", false);
      toast.error(error instanceof ApiError ? error.message : "Falha na geocodificação");
    } finally {
      setGeocoding(false);
    }
  }, [form]);

  const handleBankChange = useCallback(
    async (bankCode: string) => {
      form.setValue("bank_code", bankCode);
      form.setValue("bank_branch", "");
      if (!bankCode) {
        setRateInfo(null);
        setBankBranches([]);
        form.setValue("bank_rate_label", "");
        form.setValue("bank_rate_source_url", "");
        return;
      }
      setLoadingRate(true);
      try {
        const sector = form.getValues("sector") || undefined;
        const quote = await projectsApi.getBankDiscountRate(bankCode, sector);
        form.setValue("discount_rate", quote.discount_rate, { shouldValidate: true });
        form.setValue("bank_rate_label", quote.product_label);
        form.setValue("bank_rate_source_url", quote.source_url);
        setRateInfo(`${quote.product_label} · ${quote.source_url}`);
        toast.success(`Taxa ${quote.discount_rate}% obtida de ${quote.bank_name}`);
      } catch (error) {
        setRateInfo(null);
        toast.error(error instanceof ApiError ? error.message : "Não foi possível obter a taxa");
      } finally {
        setLoadingRate(false);
      }
    },
    [form],
  );

  const handleValidateBi = useCallback(async () => {
    const bi = normalizeBi(form.getValues("rep_id_number") || "");
    form.setValue("rep_id_number", formatBiInput(bi), { shouldValidate: true });
    if (!isValidBiFormat(bi)) {
      setBiVerified(false);
      toast.error("Formato de BI inválido");
      return false;
    }
    setValidatingBi(true);
    try {
      const result = await projectsApi.validateBi(bi);
      setBiVerified(true);
      if (result.normalized_value) {
        form.setValue("rep_id_number", result.normalized_value, { shouldValidate: true });
      }
      toast.success(result.message);
      return true;
    } catch (error) {
      setBiVerified(false);
      toast.error(error instanceof ApiError ? error.message : "BI inválido");
      return false;
    } finally {
      setValidatingBi(false);
    }
  }, [form]);

  const handleValidatePhone = useCallback(
    async (field: "rep_phone" | "company_phone", optional = false) => {
      const raw = form.getValues(field) || "";
      const phone = normalizeLocalPhone(raw);
      form.setValue(field, phone, { shouldValidate: true });
      if (!phone) {
        if (optional) return true;
        toast.error("Contacto é obrigatório");
        return false;
      }
      if (!isValidLocalPhone(phone)) {
        toast.error("Contacto inválido: 9 dígitos numéricos começando por 9");
        return false;
      }
      try {
        const result = await projectsApi.validatePhone(phone, optional);
        if (field === "rep_phone" && result.operator) {
          setPhoneOperator(result.operator);
        }
        return true;
      } catch (error) {
        toast.error(error instanceof ApiError ? error.message : "Telefone inválido");
        return false;
      }
    },
    [form],
  );

  async function goNext() {
    const fields = STEP_FIELDS[step];
    const valid = await form.trigger(fields);
    if (!valid) return;

    if (step === 0) {
      const phoneOk = await handleValidatePhone("rep_phone");
      if (!phoneOk) return;
      if (!biVerified) {
        const biOk = await handleValidateBi();
        if (!biOk) return;
      }
    }

    if (step === 1 && !form.getValues("geocode_verified")) {
      await handleGeocode();
      if (!form.getValues("geocode_verified")) {
        toast.error("Valide a localização da empresa antes de continuar");
        return;
      }
    }

    // Nunca submeter aqui — apenas avançar de passo
    setStep((s) => Math.min(s + 1, WIZARD_STEPS.length - 1));
  }

  function goBack() {
    setStep((s) => Math.max(s - 1, 0));
  }

  const lastStepIndex = WIZARD_STEPS.length - 1;
  const stepRef = useRef(step);
  stepRef.current = step;

  const submitProject = form.handleSubmit(async (values) => {
    // Só cria/actualiza no passo final (Dados bancários), nunca ao avançar
    if (stepRef.current !== lastStepIndex) {
      return;
    }

    setSubmitting(true);
    try {
      const optionalText = (value?: string) => {
        const trimmed = value?.trim();
        return trimmed ? trimmed : undefined;
      };
      const loanTerm =
        typeof values.loan_term_months === "number" &&
        Number.isFinite(values.loan_term_months) &&
        values.loan_term_months > 0
          ? values.loan_term_months
          : undefined;
      const branchCode = values.bank_branch?.trim();
      const branchLabel = branchCode
        ? bankBranches.find((b) => b.value === branchCode)?.label ?? branchCode
        : undefined;

      const payload = {
        name: values.name.trim(),
        description: optionalText(values.description),
        company_name: values.company_name.trim(),
        company_tax_id: optionalText(values.company_tax_id),
        sector: values.sector,
        country: values.country,
        currency: values.currency,
        investment_amount: parseMoneyInput(values.investment_amount) || values.investment_amount,
        project_horizon_years: values.project_horizon_years,
        discount_rate: optionalText(values.discount_rate),
        bank_code: optionalText(values.bank_code),
        bank_rate_label: optionalText(values.bank_rate_label),
        bank_rate_source_url: optionalText(values.bank_rate_source_url),
        rep_full_name: values.rep_full_name.trim(),
        rep_email: values.rep_email.trim(),
        rep_id_number: values.rep_id_number.trim(),
        rep_phone: values.rep_phone.trim(),
        rep_role: optionalText(values.rep_role),
        company_province: values.company_province,
        company_municipality: values.company_municipality,
        company_address: optionalText(values.company_address),
        company_activity: optionalText(values.company_activity),
        company_phone: optionalText(values.company_phone),
        company_email: optionalText(values.company_email),
        company_website: optionalText(values.company_website),
        company_latitude: optionalText(values.company_latitude),
        company_longitude: optionalText(values.company_longitude),
        geocode_verified: values.geocode_verified,
        geocode_source: optionalText(values.geocode_source),
        financing_type: optionalText(values.financing_type),
        loan_term_months: loanTerm,
        bank_branch: branchLabel,
      };

      const result = project
        ? await projectsApi.update(project.id, payload)
        : await projectsApi.create(payload);

      toast.success(project ? "Projeto actualizado" : "Projeto criado com sucesso");
      onSuccess?.(result);
      if (!project) router.push(`/projects/${result.id}`);
    } catch (error) {
      if (error instanceof ApiError) {
        const detailText = error.details
          ? Object.entries(error.details)
              .map(([field, messages]) => `${field}: ${messages.join(", ")}`)
              .join(" · ")
          : "";
        toast.error(detailText || error.message || "Erro ao guardar projeto");
      } else {
        toast.error("Erro ao guardar projeto");
      }
    } finally {
      setSubmitting(false);
    }
  });

  function handleFormSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (stepRef.current !== lastStepIndex) return;
    void submitProject();
  }

  function handleFormKeyDown(event: KeyboardEvent<HTMLFormElement>) {
    if (event.key !== "Enter") return;
    if (stepRef.current === lastStepIndex) return;
    const target = event.target as HTMLElement;
    if (target.tagName === "TEXTAREA") return;
    // Impede Enter de submeter o formulário nos passos intermédios
    event.preventDefault();
  }

  const provinceOptions = useMemo(
    () => toSelectOptions(metadata?.provinces ?? []),
    [metadata?.provinces],
  );
  const municipalityOptions = useMemo(
    () => toSelectOptions(municipalities),
    [municipalities],
  );

  const resolvedBankBranchValue = useMemo(() => {
    if (!bankBranchRaw) return "";
    const byValue = bankBranches.find((b) => b.value === bankBranchRaw);
    if (byValue) return bankBranchRaw;
    const byLabel = bankBranches.find((b) => b.label === bankBranchRaw);
    return byLabel?.value ?? bankBranchRaw;
  }, [bankBranchRaw, bankBranches]);

  function openReviewModal() {
    setReviewValues(form.getValues());
    setShowReviewModal(true);
  }

  if (!metadata) return <PageLoader message="A preparar formulário..." />;

  const isLastStep = step === WIZARD_STEPS.length - 1;

  return (
    <div className="project-wizard-shell rounded-2xl border border-zinc-200/80 p-6 shadow-sm md:p-8">
      <FormStepper steps={WIZARD_STEPS} currentStep={step} />

      <form onSubmit={handleFormSubmit} onKeyDown={handleFormKeyDown}>
        <div key={step} className="wizard-step-enter min-h-[420px]">
          {step === 0 ? (
            <section className="space-y-6">
              <header className="space-y-1">
                <h2 className="text-xl font-semibold text-zinc-900">Dados do representante</h2>
                <p className="text-sm text-zinc-500">
                  Identificação do responsável legal perante investidores e instituições financeiras.
                </p>
              </header>
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  label="Nome completo *"
                  placeholder="Ex: Maria João da Silva"
                  {...form.register("rep_full_name")}
                  error={form.formState.errors.rep_full_name?.message}
                />
                <Input
                  label="Email *"
                  type="email"
                  placeholder="representante@empresa.co.ao"
                  {...form.register("rep_email")}
                  error={form.formState.errors.rep_email?.message}
                />
                <div>
                  <Input
                    label="Número do BI *"
                    placeholder="Ex: 006151112LA041"
                    maxLength={14}
                    value={form.watch("rep_id_number")}
                    onChange={(e) => {
                      form.setValue("rep_id_number", formatBiInput(e.target.value), {
                        shouldValidate: true,
                      });
                      setBiVerified(false);
                    }}
                    error={form.formState.errors.rep_id_number?.message}
                  />
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      loading={validatingBi}
                      onClick={() => void handleValidateBi()}
                    >
                      Validar BI (Angola API)
                    </Button>
                    {biVerified ? (
                      <Badge className="gap-1 bg-emerald-100 text-emerald-800">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        BI confirmado
                      </Badge>
                    ) : null}
                  </div>
                  <p className="mt-1 text-xs text-zinc-500">
                    Formato: 9 dígitos + 2 letras + 3 dígitos
                  </p>
                </div>
                <PhoneInput
                  label="Contacto telefónico *"
                  value={form.watch("rep_phone")}
                  onValueChange={(raw) => {
                    form.setValue("rep_phone", raw, { shouldValidate: true });
                    setPhoneOperator(null);
                  }}
                  error={form.formState.errors.rep_phone?.message}
                  hint={
                    phoneOperator
                      ? `Operadora: ${phoneOperator} · 9 dígitos começando por 9`
                      : "9 dígitos numéricos começando por 9"
                  }
                />
                <div className="md:col-span-2">
                  <Input
                    label="Cargo / função"
                    placeholder="Ex: Director Geral, Gerente, Sócio-gerente"
                    {...form.register("rep_role")}
                  />
                </div>
              </div>
            </section>
          ) : null}

          {step === 1 ? (
            <section className="space-y-6">
              <header className="space-y-1">
                <h2 className="text-xl font-semibold text-zinc-900">Dados da empresa</h2>
                <p className="text-sm text-zinc-500">
                  Consulta AGT, localização administrativa (província/município) e contactos oficiais.
                </p>
              </header>

              <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-4 space-y-3">
                <div className="grid gap-4 md:grid-cols-[1fr_auto]">
                  <Input
                    label="NIF da empresa"
                    placeholder="Ex: 5000978702"
                    {...form.register("company_tax_id")}
                  />
                  <div className="flex items-end">
                    <Button
                      type="button"
                      variant="outline"
                      loading={lookingUpNif}
                      onClick={() => void handleLookupNif()}
                    >
                      <Search className="h-4 w-4" />
                      Buscar na AGT
                    </Button>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <Button
                    type="button"
                    variant="secondary"
                    loading={extractingDoc}
                    onClick={() => documentFileRef.current?.click()}
                  >
                    <FileUp className="h-4 w-4" />
                    Importar documento (PDF)
                  </Button>
                  <p className="text-xs text-zinc-600">
                    Carregue certidão ou alvará para preencher NIF, nome e contactos automaticamente.
                  </p>
                  <input
                    ref={documentFileRef}
                    type="file"
                    accept=".pdf,.txt"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) void handleExtractDocument(file);
                      e.target.value = "";
                    }}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <Input
                    label="Nome da empresa *"
                    {...form.register("company_name")}
                    error={form.formState.errors.company_name?.message}
                  />
                </div>
                {form.watch("company_activity") ? (
                  <div className="md:col-span-2 rounded-lg bg-zinc-50 px-3 py-2 text-sm text-zinc-600">
                    <span className="font-medium text-zinc-700">Actividade (AGT): </span>
                    {form.watch("company_activity")}
                  </div>
                ) : null}
                <SearchableSelect
                  label="Província *"
                  placeholder="Seleccionar província..."
                  searchPlaceholder="Pesquisar província..."
                  value={form.watch("company_province")}
                  onChange={(value) => {
                    form.setValue("company_province", value, { shouldValidate: true });
                    form.setValue("company_municipality", "");
                    form.setValue("bank_branch", "");
                    form.setValue("geocode_verified", false);
                    setGeoInfo(null);
                  }}
                  options={provinceOptions}
                  error={form.formState.errors.company_province?.message}
                />
                <SearchableSelect
                  label="Município *"
                  placeholder={
                    loadingMunicipalities
                      ? "A carregar municípios..."
                      : province
                        ? "Seleccionar município..."
                        : "Seleccione primeiro a província"
                  }
                  searchPlaceholder="Pesquisar município..."
                  value={form.watch("company_municipality")}
                  onChange={(value) => {
                    form.setValue("company_municipality", value, { shouldValidate: true });
                    form.setValue("geocode_verified", false);
                    setGeoInfo(null);
                  }}
                  options={municipalityOptions}
                  disabled={!province || loadingMunicipalities}
                  error={form.formState.errors.company_municipality?.message}
                />
                <div className="md:col-span-2">
                  <Textarea
                    label="Morada / endereço"
                    rows={2}
                    placeholder="Rua, bairro, número..."
                    {...form.register("company_address")}
                  />
                </div>
                <div className="md:col-span-2 flex flex-wrap items-center gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    loading={geocoding}
                    onClick={() => void handleGeocode()}
                    disabled={!province || !form.watch("company_municipality")}
                  >
                    <MapPin className="h-4 w-4" />
                    Validar localização
                  </Button>
                  {form.watch("geocode_verified") ? (
                    <Badge className="gap-1 bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      Geocodificação confirmada
                    </Badge>
                  ) : null}
                </div>
                {geoInfo ? (
                  <p className="md:col-span-2 text-xs text-emerald-700">{geoInfo}</p>
                ) : null}
                <PhoneInput
                  label="Telefone da empresa"
                  value={form.watch("company_phone") || ""}
                  onValueChange={(raw) =>
                    form.setValue("company_phone", raw, { shouldValidate: true })
                  }
                  error={form.formState.errors.company_phone?.message}
                  hint="Opcional · 9 dígitos começando por 9"
                />
                <Input
                  label="Email da empresa"
                  type="email"
                  placeholder="contacto@empresa.co.ao"
                  {...form.register("company_email")}
                  error={form.formState.errors.company_email?.message}
                />
                <div className="md:col-span-2">
                  <Input
                    label="Website"
                    placeholder="https://www.empresa.co.ao"
                    {...form.register("company_website")}
                    error={form.formState.errors.company_website?.message}
                  />
                </div>
              </div>
            </section>
          ) : null}

          {step === 2 ? (
            <section className="space-y-6">
              <header className="space-y-1">
                <h2 className="text-xl font-semibold text-zinc-900">Dados do projecto</h2>
                <p className="text-sm text-zinc-500">
                  Defina o investimento, sector de actividade e horizonte temporal do estudo.
                </p>
              </header>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <Input
                    label="Nome do projecto *"
                    {...form.register("name")}
                    error={form.formState.errors.name?.message}
                  />
                </div>
                <SearchableSelect
                  label="Sector *"
                  placeholder="Seleccionar sector..."
                  searchPlaceholder="Pesquisar sector..."
                  value={form.watch("sector")}
                  onChange={(value) => {
                    form.setValue("sector", value, { shouldValidate: true });
                    const bank = form.getValues("bank_code");
                    if (bank) void handleBankChange(bank);
                  }}
                  options={toSelectOptions(metadata.sectors)}
                  error={form.formState.errors.sector?.message}
                />
                <SearchableSelect
                  label="País *"
                  value={form.watch("country")}
                  onChange={(value) => form.setValue("country", value, { shouldValidate: true })}
                  options={toSelectOptions(metadata.countries)}
                  error={form.formState.errors.country?.message}
                />
                <SearchableSelect
                  label="Moeda *"
                  value={form.watch("currency")}
                  onChange={(value) => form.setValue("currency", value, { shouldValidate: true })}
                  options={toSelectOptions(metadata.currencies)}
                  error={form.formState.errors.currency?.message}
                />
                <MoneyInput
                  label="Investimento total *"
                  placeholder="Ex: 1.500.000"
                  value={form.watch("investment_amount")}
                  onValueChange={(raw) =>
                    form.setValue("investment_amount", raw, { shouldValidate: true, shouldDirty: true })
                  }
                  error={form.formState.errors.investment_amount?.message}
                />
                <Input
                  label="Horizonte (anos) *"
                  type="number"
                  {...form.register("project_horizon_years", { valueAsNumber: true })}
                  error={form.formState.errors.project_horizon_years?.message}
                />
                <div className="md:col-span-2">
                  <Textarea
                    label="Descrição do projecto"
                    rows={4}
                    placeholder="Descreva brevemente o objecto do investimento, mercado-alvo e diferenciais..."
                    {...form.register("description")}
                  />
                </div>
              </div>
            </section>
          ) : null}

          {step === 3 ? (
            <section className="space-y-6">
              <header className="space-y-1">
                <h2 className="text-xl font-semibold text-zinc-900">Dados bancários</h2>
                <p className="text-sm text-zinc-500">
                  Instituição financiadora, tipo de crédito e taxa de referência para análise de viabilidade.
                </p>
              </header>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1.5 md:col-span-2">
                  <div className="flex flex-col gap-3 md:flex-row md:items-end">
                    <div className="min-w-0 flex-1">
                      <SearchableSelect
                        label="Banco financiador"
                        placeholder="Seleccionar banco..."
                        searchPlaceholder="Pesquisar banco..."
                        value={selectedBankCode}
                        onChange={(value) => void handleBankChange(value)}
                        options={toSelectOptions(banks)}
                      />
                    </div>
                    {selectedBank?.logo ? (
                      <div className="flex h-[46px] w-full shrink-0 items-center justify-center rounded-xl border border-zinc-200 bg-white px-4 md:w-[140px]">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={selectedBank.logo}
                          alt={selectedBank.label}
                          className="max-h-9 max-w-full object-contain"
                          onError={(e) => {
                            e.currentTarget.style.display = "none";
                          }}
                        />
                      </div>
                    ) : null}
                  </div>
                  {selectedBank?.website ? (
                    <a
                      href={selectedBank.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-emerald-700 hover:underline"
                    >
                      Portal oficial: {selectedBank.website.replace(/^https?:\/\//, "")}
                    </a>
                  ) : null}
                </div>
                <SearchableSelect
                  label="Tipo de financiamento"
                  placeholder="Seleccionar tipo..."
                  searchPlaceholder="Pesquisar..."
                  value={form.watch("financing_type") || ""}
                  onChange={(value) => form.setValue("financing_type", value)}
                  options={toSelectOptions(metadata.financing_types ?? [])}
                />
                <Input
                  label="Taxa de desconto / juro (%)"
                  type="number"
                  step="0.001"
                  {...form.register("discount_rate")}
                  disabled={loadingRate}
                />
                <Input
                  label="Prazo do financiamento (meses)"
                  type="number"
                  min={1}
                  max={360}
                  placeholder="Opcional (1–360)"
                  value={
                    Number.isFinite(form.watch("loan_term_months"))
                      ? String(form.watch("loan_term_months"))
                      : ""
                  }
                  onChange={(event) => {
                    const raw = event.target.value.trim();
                    if (!raw) {
                      form.setValue("loan_term_months", undefined, { shouldValidate: true });
                      return;
                    }
                    const parsed = Number(raw);
                    form.setValue(
                      "loan_term_months",
                      Number.isFinite(parsed) ? parsed : undefined,
                      { shouldValidate: true },
                    );
                  }}
                  error={form.formState.errors.loan_term_months?.message}
                />
                <SearchableSelect
                  label="Agência bancária"
                  placeholder={
                    !province
                      ? "Seleccione primeiro a província da empresa"
                      : !selectedBankCode
                      ? "Seleccione primeiro o banco"
                      : loadingBranches
                        ? "A carregar agências..."
                        : "Seleccionar agência..."
                  }
                  searchPlaceholder="Pesquisar agência ou morada..."
                  value={resolvedBankBranchValue}
                  onChange={(value) => form.setValue("bank_branch", value, { shouldValidate: true })}
                  options={bankBranches}
                  disabled={!province || !selectedBankCode || loadingBranches}
                  emptyMessage={
                    !province
                      ? "Seleccione a província da empresa"
                      : selectedBankCode
                        ? "Este banco não possui agência disponível na província seleccionada"
                        : "Seleccione um banco"
                  }
                  error={form.formState.errors.bank_branch?.message}
                />
                {selectedBankCode && bankBranches.length > 0 && province ? (
                  <p className="text-xs text-emerald-700 md:col-span-2">
                    A mostrar exclusivamente agências disponíveis na província seleccionada.
                  </p>
                ) : null}
              </div>
              {loadingRate ? (
                <p className="text-xs text-zinc-500">A obter taxa real do site do banco...</p>
              ) : null}
              {rateInfo ? <p className="text-xs text-emerald-700">Fonte: {rateInfo}</p> : null}

              <div className="rounded-xl border border-dashed border-emerald-200 bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/50 p-4 text-sm text-emerald-900 shadow-sm">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="font-semibold">Resumo antes de criar</p>
                    <ul className="mt-2 space-y-1 text-emerald-800/90">
                      <li>
                        <strong>Empresa:</strong> {form.watch("company_name") || "—"}
                      </li>
                      <li>
                        <strong>Projecto:</strong> {form.watch("name") || "—"} ·{" "}
                        {metadata.sectors.find((s) => s.value === form.watch("sector"))?.label ??
                          "—"}
                      </li>
                      <li>
                        <strong>Investimento:</strong> {form.watch("investment_amount") || "—"}{" "}
                        {form.watch("currency")}
                      </li>
                    </ul>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    className="shrink-0 border-emerald-300 bg-white/90 text-emerald-800 hover:border-emerald-400 hover:bg-emerald-50"
                    onClick={openReviewModal}
                  >
                    <Eye className="h-4 w-4" />
                    Ver resumo completo
                  </Button>
                </div>
              </div>
            </section>
          ) : null}
        </div>

        <div className="mt-8 flex flex-col-reverse gap-3 border-t border-zinc-100 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            {step > 0 ? (
              <Button type="button" variant="outline" onClick={goBack}>
                <ArrowLeft className="h-4 w-4" />
                Anterior
              </Button>
            ) : project ? (
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancelar
              </Button>
            ) : null}
          </div>
          <div className="flex gap-3">
            {!isLastStep ? (
              <Button type="button" onClick={() => void goNext()}>
                Seguinte
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                type="button"
                loading={submitting}
                onClick={() => {
                  if (step !== lastStepIndex) return;
                  void submitProject();
                }}
              >
                {project ? "Guardar alterações" : "Criar projecto"}
              </Button>
            )}
          </div>
        </div>
      </form>

      <ProjectReviewModal
        open={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        values={reviewValues ?? form.getValues()}
        metadata={metadata}
        municipalities={municipalities}
        bankBranches={bankBranches}
        biVerified={biVerified}
        geoInfo={geoInfo}
        phoneOperator={phoneOperator}
        rateInfo={rateInfo}
        onEditStep={setStep}
      />
    </div>
  );
}
