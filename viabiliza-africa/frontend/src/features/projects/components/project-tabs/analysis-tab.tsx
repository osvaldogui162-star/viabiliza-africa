"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { BarChart3, Download, Play, TrendingUp } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { PageLoader } from "@/components/ui/spinner";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ProjectCallout } from "@/features/projects/components/project-callout";
import {
  CashFlowSparkline,
  MonteCarloChart,
  ScenarioCompareChart,
} from "@/features/projects/components/analysis-charts";
import { ProjectScrollPanel } from "@/features/projects/components/project-scroll-panel";
import {
  ProjectSectionNav,
  type ProjectSection,
} from "@/features/projects/components/project-section-nav";
import { ApiError } from "@/lib/api/http-client";
import { analysisApi } from "@/lib/api/analysis-api";
import type {
  BenchmarkComparison,
  FinancialAnalysis,
  MonteCarloResult,
  ScenarioAnalysisResult,
  SensitivityResult,
} from "@/lib/types/analysis";
import type { Project } from "@/lib/types/project";
import {
  getIndicatorItems,
  getSummaryEntries,
  groupIndicatorsByCategory,
} from "@/lib/utils/analysis-helpers";
import { formatIndicatorValue, formatNumber } from "@/lib/utils/format";
import { cn } from "@/lib/utils/cn";
import { useMySubscription } from "@/hooks/use-my-subscription";

const CATEGORY_LABELS: Record<string, string> = {
  rentabilidade: "rentabilidade",
  liquidez: "liquidez",
  endividamento: "endividamento",
  eficiencia: "eficiencia",
  valor: "valor",
  risco: "risco",
  outros: "outros",
};

const SUMMARY_ACCENTS = ["#2dd4bf", "#34d399", "#4ade80", "#14b8a6", "#22d3ee", "#a3e635"];

export function AnalysisTab({ project }: { project: Project }) {
  const { user } = useAuth();
  const { t, locale, intlLocale } = useI18n();
  const isAdmin = user?.role === "admin";
  const { capabilities } = useMySubscription(!isAdmin);
  const monteCarloAllowed = isAdmin || capabilities?.monte_carlo_enabled === true;
  const sensitivityAllowed = isAdmin || capabilities?.sensitivity_enabled === true;
  const mcIterationsMax = capabilities?.monte_carlo_iterations_limit ?? 10000;
  const [analyses, setAnalyses] = useState<FinancialAnalysis[]>([]);
  const [monteCarlo, setMonteCarlo] = useState<MonteCarloResult[]>([]);
  const [sensitivity, setSensitivity] = useState<SensitivityResult[]>([]);
  const [benchmarks, setBenchmarks] = useState<BenchmarkComparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [mcIterations, setMcIterations] = useState("10000");
  const [runningSensitivity, setRunningSensitivity] = useState(false);
  const [scenarios, setScenarios] = useState<ScenarioAnalysisResult | null>(null);
  const [runningScenarios, setRunningScenarios] = useState(false);
  const [section, setSection] = useState("summary");

  const canRun = user?.role === "admin" || (user?.role === "financial" && project.is_owner);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [aRes, mcRes, sensRes, benchRes] = await Promise.all([
        analysisApi.listAnalyses(project.id),
        analysisApi.listMonteCarlo(project.id),
        analysisApi.listSensitivity(project.id),
        analysisApi.getBenchmarks(project.id).catch(() => null),
      ]);
      setAnalyses(aRes.items);
      setMonteCarlo(mcRes.items ?? []);
      setSensitivity(sensRes.items ?? []);
      setBenchmarks(benchRes?.comparisons ?? []);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.loadError"));
    } finally {
      setLoading(false);
    }
  }, [project.id, t]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCalculate() {
    setCalculating(true);
    try {
      await analysisApi.calculateIndicators(project.id);
      toast.success(t("analysis.calculateSuccess"));
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.calculateError"));
    } finally {
      setCalculating(false);
    }
  }

  async function handleMonteCarlo() {
    setCalculating(true);
    try {
      const cap = isAdmin ? 50000 : mcIterationsMax;
      const iterations = Math.max(1000, Math.min(cap, parseInt(mcIterations, 10) || 10000));
      await analysisApi.runMonteCarlo(project.id, { iterations });
      toast.success(t("analysis.monteCarloSuccess"));
      void load();
      setSection("risk");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.monteCarloError"));
    } finally {
      setCalculating(false);
    }
  }

  async function handleSensitivity() {
    setRunningSensitivity(true);
    try {
      await analysisApi.runSensitivity(project.id);
      toast.success(t("analysis.sensitivitySuccess"));
      void load();
      setSection("risk");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.sensitivityError"));
    } finally {
      setRunningSensitivity(false);
    }
  }

  async function handleScenarios() {
    setRunningScenarios(true);
    try {
      const result = await analysisApi.runScenarios(project.id);
      setScenarios(result);
      toast.success(t("analysis.scenariosSuccess"));
      setSection("risk");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.scenariosError"));
    } finally {
      setRunningScenarios(false);
    }
  }

  async function handleExport(analysisId?: string) {
    try {
      const { blob, filename } = await analysisApi.exportIndicators(project.id, analysisId, locale);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("analysis.exportError"));
    }
  }

  const latest = analyses[0];
  const summaryEntries = useMemo(
    () => (latest ? getSummaryEntries(latest.indicators) : []),
    [latest],
  );
  const groupedIndicators = useMemo(
    () => (latest ? groupIndicatorsByCategory(latest.indicators) : {}),
    [latest],
  );
  const indicatorCount = latest
    ? (latest.indicators_count ?? getIndicatorItems(latest.indicators).length)
    : 0;

  const sections: ProjectSection[] = useMemo(
    () => [
      { id: "summary", label: t("projectTabs.overview"), count: indicatorCount || undefined },
      {
        id: "risk",
        label: locale === "en" ? "Risk & scenarios" : "Risco & cenários",
        count:
          monteCarlo.length + sensitivity.length + (scenarios ? 1 : 0) || undefined,
      },
      {
        id: "detail",
        label: locale === "en" ? "Tables" : "Tabelas",
        count:
          (latest?.cash_flows?.years?.length ? 1 : 0) + (benchmarks.length ? 1 : 0) || undefined,
      },
    ],
    [t, locale, indicatorCount, monteCarlo.length, sensitivity.length, scenarios, latest, benchmarks.length],
  );

  if (loading) return <PageLoader />;

  return (
    <div className="space-y-4">
      {canRun ? (
        <Card variant="panel" className="!p-4">
          <div className="flex flex-wrap items-end gap-2">
            <Button onClick={() => void handleCalculate()} loading={calculating} size="sm">
              <Play className="h-4 w-4" /> {t("analysis.calculate")}
            </Button>
            {monteCarloAllowed ? (
              <>
                <Input
                  label={t("analysis.mcIterations")}
                  type="number"
                  min={1000}
                  max={isAdmin ? 50000 : mcIterationsMax}
                  value={mcIterations}
                  onChange={(e) => setMcIterations(e.target.value)}
                  className="w-36"
                />
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => void handleMonteCarlo()}
                  loading={calculating}
                >
                  <BarChart3 className="h-4 w-4" /> Monte Carlo
                </Button>
              </>
            ) : null}
            {sensitivityAllowed ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => void handleSensitivity()}
                loading={runningSensitivity}
              >
                <TrendingUp className="h-4 w-4" /> Sensibilidade
              </Button>
            ) : null}
            {sensitivityAllowed ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => void handleScenarios()}
                loading={runningScenarios}
              >
                Cenários ±
              </Button>
            ) : null}
            {latest ? (
              <Button variant="outline" size="sm" onClick={() => void handleExport(latest.id)}>
                <Download className="h-4 w-4" /> {t("analysis.exportExcel")}
              </Button>
            ) : null}
          </div>
          {!monteCarloAllowed || !sensitivityAllowed ? (
            <p className="mt-3 text-xs text-amber-700">
              {locale === "en"
                ? "Some risk tools require a higher plan."
                : "Algumas ferramentas de risco exigem um plano superior."}{" "}
              <a href="/planos" className="underline">
                /planos
              </a>
            </p>
          ) : null}
        </Card>
      ) : (
        <ProjectCallout variant="info">
          {locale === "en"
            ? "You have view-only access. Financial analysis runs are performed by the project owner."
            : "Tem acesso de visualização. As análises financeiras são executadas pelo proprietário do projecto."}
        </ProjectCallout>
      )}

      <ProjectSectionNav sections={sections} active={section} onChange={setSection} />

      {section === "summary" ? (
        <Card variant="panel">
          <CardHeader
            eyebrow={t("projectTabs.analysis")}
            title={t("analysis.summaryTitle")}
            description={
              latest
                ? t("analysis.summaryDesc", { count: indicatorCount })
                : t("analysis.summaryDescEmpty")
            }
          />
          {!latest ? (
            <EmptyState
              compact
              title={t("analysis.empty")}
              description={t("analysis.emptyDescription")}
              action={
                canRun ? (
                  <Button size="sm" onClick={() => void handleCalculate()} loading={calculating}>
                    <Play className="h-4 w-4" /> {t("analysis.calculate")}
                  </Button>
                ) : undefined
              }
            />
          ) : (
            <>
              <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {summaryEntries.map(({ key, label, value }, index) => (
                  <article
                    key={key}
                    className="va-project-stat va-project-stat--0 rounded-xl p-3.5"
                    style={{
                      borderLeftColor: SUMMARY_ACCENTS[index % SUMMARY_ACCENTS.length],
                      animationDelay: `${index * 100}ms`,
                    }}
                  >
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">
                      {label}
                    </p>
                    <p className="mt-1 text-xl font-bold tabular-nums text-zinc-900">
                      {key === "is_viable" ? (
                        <Badge variant={value ? "success" : "default"}>
                          {value ? t("common.yes") : t("common.no")}
                        </Badge>
                      ) : key === "tir" ||
                          key === "roi" ||
                          key === "roe" ||
                          key === "ebitda_margin" ||
                          key === "discount_rate" ? (
                        formatIndicatorValue(value as number, "%", intlLocale)
                      ) : key === "vpl" || key === "initial_investment" ? (
                        formatIndicatorValue(value as number, project.currency, intlLocale)
                      ) : key === "payback_years" || key === "horizon_years" ? (
                        formatIndicatorValue(
                          value as number,
                          locale === "en" ? "years" : "anos",
                          intlLocale,
                        )
                      ) : (
                        formatNumber(value as number | string | null, undefined, intlLocale)
                      )}
                    </p>
                  </article>
                ))}
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                {Object.entries(groupedIndicators).map(([category, items]) => (
                  <div key={category} className="rounded-xl border border-zinc-100 bg-zinc-50/50 p-4">
                    <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-teal-800">
                      {t(`analysis.categories.${CATEGORY_LABELS[category] ?? "outros"}`)}
                    </h3>
                    <div className="grid gap-2 sm:grid-cols-2">
                      {items.map((item) => (
                        <div
                          key={item.key}
                          className="rounded-lg border border-white bg-white p-2.5 shadow-sm"
                        >
                          <p className="text-[10px] font-medium uppercase text-zinc-500">
                            {item.label}
                          </p>
                          <p className="mt-0.5 text-sm font-bold text-zinc-900">
                            {formatIndicatorValue(item.value, item.unit, intlLocale)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </Card>
      ) : null}

      {section === "risk" ? (
        <div className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-2">
            {scenarios ? <ScenarioCompareChart data={scenarios} /> : null}
            {monteCarlo.length > 0 ? <MonteCarloChart runs={monteCarlo} /> : null}
          </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {scenarios ? (
            <Card variant="panel">
              <CardHeader
                title={t("analysis.scenariosTitle")}
                description={t("analysis.scenariosDesc")}
              />
              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
                {scenarios.scenarios.map((scenario) => (
                  <div
                    key={scenario.code}
                    className={cn(
                      "rounded-xl border p-4",
                      scenario.code === "optimistic"
                        ? "border-emerald-200 bg-emerald-50/60"
                        : scenario.code === "pessimistic"
                          ? "border-amber-200 bg-amber-50/60"
                          : "border-zinc-200 bg-white",
                    )}
                  >
                    <p className="text-sm font-semibold">{scenario.label}</p>
                    <p className="mt-2 text-xl font-bold">
                      {formatIndicatorValue(scenario.npv, project.currency, intlLocale)}
                    </p>
                    <p className="text-xs text-zinc-500">VPL</p>
                    <p className="mt-2 text-sm">
                      TIR:{" "}
                      {scenario.irr !== null
                        ? formatIndicatorValue(scenario.irr, "%", intlLocale)
                        : "—"}
                    </p>
                    <p className="text-sm">
                      Payback:{" "}
                      {scenario.payback_years !== null
                        ? formatIndicatorValue(
                            scenario.payback_years,
                            locale === "en" ? "years" : "anos",
                            intlLocale,
                          )
                        : "—"}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          ) : (
            <Card variant="panel">
              <EmptyState
                compact
                title={locale === "en" ? "No scenarios yet" : "Sem cenários ainda"}
                description={
                  locale === "en"
                    ? "Run scenario analysis from the toolbar above."
                    : "Execute a análise de cenários na barra superior."
                }
              />
            </Card>
          )}

          {monteCarlo.length > 0 ? (
            <Card variant="panel">
              <CardHeader title={t("analysis.monteCarloTitle")} />
              {monteCarlo.map((mc) => {
                const stats = mc.results.statistics;
                const pct = mc.results.percentiles;
                return (
                  <div key={mc.id} className="grid gap-3 sm:grid-cols-3">
                    <div className="rounded-xl border border-blue-100 bg-blue-50/40 p-4">
                      <p className="text-xs font-semibold uppercase text-blue-900">VPL — Média</p>
                      <p className="mt-1 text-2xl font-bold text-zinc-900">
                        {formatIndicatorValue(stats.mean, project.currency, intlLocale)}
                      </p>
                      <p className="mt-2 text-xs text-zinc-500">
                        P5–P95: {formatIndicatorValue(pct.p5, project.currency, intlLocale)} —{" "}
                        {formatIndicatorValue(pct.p95, project.currency, intlLocale)}
                      </p>
                    </div>
                    <div className="rounded-xl border p-4">
                      <p className="text-xs font-semibold uppercase text-zinc-600">Mediana (P50)</p>
                      <p className="mt-1 text-xl font-semibold">
                        {formatIndicatorValue(pct.p50, project.currency, intlLocale)}
                      </p>
                      <p className="mt-2 text-xs text-zinc-500">
                        Desvio: {formatIndicatorValue(stats.std, project.currency, intlLocale)}
                      </p>
                    </div>
                    <div className="rounded-xl border p-4">
                      <p className="text-xs font-semibold uppercase text-zinc-600">
                        Prob. VPL positivo
                      </p>
                      <p className="mt-1 text-xl font-semibold text-emerald-700">
                        {formatNumber(mc.results.probability_npv_positive)}%
                      </p>
                      <p className="mt-2 text-xs text-zinc-500">
                        {mc.iterations.toLocaleString(intlLocale)} iterações
                      </p>
                    </div>
                  </div>
                );
              })}
            </Card>
          ) : null}

          {sensitivity.length > 0 ? (
            <Card variant="panel" className={scenarios && monteCarlo.length === 0 ? "" : "xl:col-span-2"}>
              <CardHeader
                title={t("analysis.sensitivityTitle")}
                description={t("analysis.sensitivityDesc")}
              />
              {sensitivity.map((s) => (
                <div key={s.id} className="space-y-2">
                  <p className="text-sm text-zinc-500">
                    VPL base: {formatIndicatorValue(s.results.base_npv, project.currency, intlLocale)}
                    {s.results.base_irr !== null
                      ? ` · TIR: ${formatIndicatorValue(s.results.base_irr, "%", intlLocale)}`
                      : ""}
                  </p>
                  <div className="space-y-2">
                    {s.results.tornado_npv.slice(0, 8).map((item) => {
                      const maxImpact = s.results.tornado_npv[0]?.impact ?? 1;
                      const width = Math.max(8, (item.impact / maxImpact) * 100);
                      return (
                        <div key={item.key} className="flex items-center gap-3 text-sm">
                          <span className="w-32 shrink-0 truncate text-zinc-600">{item.label}</span>
                          <div className="h-5 flex-1 rounded-full bg-zinc-100">
                            <div
                              className="h-full rounded-full bg-teal-500/75 transition-all"
                              style={{ width: `${width}%` }}
                            />
                          </div>
                          <span className="w-24 shrink-0 text-right text-xs font-semibold text-zinc-700">
                            {formatIndicatorValue(item.impact, project.currency, intlLocale)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </Card>
          ) : null}

          {!scenarios && monteCarlo.length === 0 && sensitivity.length === 0 ? (
            <Card variant="panel" className="xl:col-span-2">
              <EmptyState
                compact
                title={locale === "en" ? "No risk analyses yet" : "Sem análises de risco"}
                description={
                  locale === "en"
                    ? "Use Monte Carlo, sensitivity or scenarios from the toolbar."
                    : "Use Monte Carlo, sensibilidade ou cenários na barra superior."
                }
              />
            </Card>
          ) : null}
        </div>
        </div>
      ) : null}

      {section === "detail" ? (
        <div className="grid gap-4 xl:grid-cols-2">
          {latest?.cash_flows?.years?.length ? (
            <Card variant="panel">
              <CardHeader
                title={t("analysis.cashFlowTitle")}
                description={t("analysis.cashFlowDesc")}
              />
              <ProjectScrollPanel maxHeight="max-h-[min(48vh,440px)]">
                <table className="min-w-full text-xs">
                  <thead className="sticky top-0 bg-zinc-50 text-left">
                    <tr>
                      <th className="p-2">Ano</th>
                      <th className="p-2">Receita</th>
                      <th className="p-2">OPEX</th>
                      <th className="p-2">EBITDA</th>
                      <th className="p-2">FCF</th>
                    </tr>
                  </thead>
                  <tbody>
                    {latest.cash_flows.years.map((year, index) => (
                      <tr key={year} className="border-t border-zinc-100">
                        <td className="p-2 font-medium">
                          {year === 0 ? t("analysis.investment") : year}
                        </td>
                        <td className="p-2">
                          {formatIndicatorValue(
                            latest.cash_flows!.revenue[index],
                            project.currency,
                            intlLocale,
                          )}
                        </td>
                        <td className="p-2">
                          {formatIndicatorValue(
                            latest.cash_flows!.opex[index],
                            project.currency,
                            intlLocale,
                          )}
                        </td>
                        <td className="p-2">
                          {formatIndicatorValue(
                            latest.cash_flows!.ebitda[index],
                            project.currency,
                            intlLocale,
                          )}
                        </td>
                        <td className="p-2 font-semibold">
                          {formatIndicatorValue(
                            latest.cash_flows!.free_cash_flow[index],
                            project.currency,
                            intlLocale,
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ProjectScrollPanel>
            </Card>
          ) : null}

          {benchmarks.length > 0 ? (
            <Card variant="panel">
              <CardHeader
                title={t("analysis.benchmarksTitle")}
                description={t("analysis.benchmarksDesc")}
              />
              <ProjectScrollPanel maxHeight="max-h-[min(48vh,440px)]">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b text-left text-xs uppercase text-zinc-500">
                      <th className="pb-2 pr-3 font-semibold">Métrica</th>
                      <th className="pb-2 pr-3 font-semibold">Projeto</th>
                      <th className="pb-2 pr-3 font-semibold">Benchmark</th>
                      <th className="pb-2 font-semibold">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {benchmarks.map((b) => (
                      <tr key={b.metric_key} className="border-b border-zinc-50 last:border-0">
                        <td className="py-2.5 pr-3 text-sm">{b.metric_label}</td>
                        <td className="py-2.5 pr-3 font-semibold">
                          {b.project_value !== null
                            ? formatIndicatorValue(b.project_value, b.unit, intlLocale)
                            : "—"}
                        </td>
                        <td className="py-2.5 pr-3">
                          {formatIndicatorValue(b.benchmark_value, b.unit, intlLocale)}
                        </td>
                        <td className="py-2.5">
                          <BenchmarkStatus status={b.status} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ProjectScrollPanel>
            </Card>
          ) : null}

          {!latest?.cash_flows?.years?.length && benchmarks.length === 0 ? (
            <Card variant="panel" className="xl:col-span-2">
              <EmptyState
                compact
                title={locale === "en" ? "No detail tables" : "Sem tabelas detalhadas"}
                description={
                  locale === "en"
                    ? "Calculate indicators first to unlock cash flow and benchmarks."
                    : "Calcule os indicadores primeiro para desbloquear fluxo de caixa e benchmarks."
                }
              />
            </Card>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function BenchmarkStatus({ status }: { status: BenchmarkComparison["status"] }) {
  const map = {
    above: { label: "Acima", variant: "success" as const },
    below: { label: "Abaixo", variant: "default" as const },
    equal: { label: "Igual", variant: "default" as const },
    no_data: { label: "Sem dados", variant: "default" as const },
  };
  const { label, variant } = map[status];
  return <Badge variant={variant}>{label}</Badge>;
}
