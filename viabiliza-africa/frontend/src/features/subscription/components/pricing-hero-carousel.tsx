"use client";

import Image from "next/image";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Globe2,
  Leaf,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import {
  MARKETING_HERO_AFRICA,
  MARKETING_HERO_MULTISECTOR,
  MARKETING_HERO_TRACEABILITY,
  MARKETING_HERO_VIABILITY,
} from "@/lib/constants/brand-assets";

type Slide = {
  id: string;
  badge: string;
  title: string;
  highlight: string;
  description: string;
  icon: typeof TrendingUp;
  image: string;
  stats: { label: string; value: string }[];
  theme: "navy" | "emerald" | "ocean" | "gold";
};

const SLIDES: Slide[] = [
  {
    id: "viability",
    badge: "Análise de Viabilidade",
    title: "Transforme dados em",
    highlight: "decisões de investimento",
    description:
      "Modelação financeira rigorosa, cenários Monte Carlo e indicadores de retorno — tudo numa plataforma pensada para o mercado africano.",
    icon: TrendingUp,
    image: MARKETING_HERO_VIABILITY,
    stats: [
      { label: "Sectores", value: "6+" },
      { label: "Relatórios", value: "BFA · BDA · AIPEX" },
      { label: "Desde", value: "$15/mês" },
    ],
    theme: "navy",
  },
  {
    id: "traceability",
    badge: "Rastreabilidade Total",
    title: "Cada premissa com",
    highlight: "hash SHA-256 verificável",
    description:
      "Transparência absoluta em orçamentos, custos e relatórios. QR Code e trilha de auditoria para conformidade institucional.",
    icon: ShieldCheck,
    image: MARKETING_HERO_TRACEABILITY,
    stats: [
      { label: "Integridade", value: "100%" },
      { label: "Auditoria", value: "Completa" },
      { label: "Conformidade", value: "BNA · AIPEX" },
    ],
    theme: "emerald",
  },
  {
    id: "multisector",
    badge: "Multi-setorial",
    title: "Agricultura, Indústria,",
    highlight: "Infraestruturas e ESG",
    description:
      "DSSAT para 42+ culturas, Digital Twin industrial, análise de sensibilidade e relatórios ESG integrados num só ecossistema.",
    icon: Leaf,
    image: MARKETING_HERO_MULTISECTOR,
    stats: [
      { label: "Culturas DSSAT", value: "42+" },
      { label: "Digital Twin", value: "✓" },
      { label: "ESG / SROI", value: "Avançado" },
    ],
    theme: "ocean",
  },
  {
    id: "africa",
    badge: "Angola · África · SADC",
    title: "Software SaaS feito para",
    highlight: "a realidade africana",
    description:
      "Preços acessíveis, faturação em AOA, suporte em português e integração com bancos e instituições angolanas.",
    icon: Globe2,
    image: MARKETING_HERO_AFRICA,
    stats: [
      { label: "Moedas", value: "USD · AOA" },
      { label: "Desconto anual", value: "17%" },
      { label: "Suporte", value: "PT · 24–72h" },
    ],
    theme: "gold",
  },
];

const THEME_STYLES: Record<
  Slide["theme"],
  { overlay: string; accent: string; badge: string; panel: string }
> = {
  navy: {
    overlay: "from-[#0a1a2e]/95 via-[#0a1a2e]/75 to-[#0a1a2e]/40",
    accent: "text-[#c6a43f]",
    badge: "border-white/15 bg-white/10 text-emerald-100",
    panel: "from-[#0a1a2e] via-[#1a3a5c] to-[#0f2744]",
  },
  emerald: {
    overlay: "from-[#064e3b]/95 via-[#064e3b]/75 to-[#064e3b]/40",
    accent: "text-emerald-200",
    badge: "border-white/15 bg-white/10 text-emerald-50",
    panel: "from-[#064e3b] via-[#047857] to-[#065f46]",
  },
  ocean: {
    overlay: "from-[#0c4a6e]/95 via-[#0c4a6e]/75 to-[#0c4a6e]/40",
    accent: "text-cyan-200",
    badge: "border-white/15 bg-white/10 text-sky-50",
    panel: "from-[#0c4a6e] via-[#1e5a8a] to-[#1a3a5c]",
  },
  gold: {
    overlay: "from-[#1a1508]/95 via-[#1a1508]/75 to-[#1a1508]/40",
    accent: "text-[#e8c96a]",
    badge: "border-[#c6a43f]/30 bg-[#c6a43f]/10 text-[#f5e6b8]",
    panel: "from-[#1a1508] via-[#2d2410] to-[#0a1a2e]",
  },
};

const INTERVAL_MS = 6000;

export function PricingHeroCarousel({ currentPlanBanner }: { currentPlanBanner?: ReactNode }) {
  const [active, setActive] = useState(0);
  const [direction, setDirection] = useState<"next" | "prev">("next");
  const [paused, setPaused] = useState(false);
  const [animKey, setAnimKey] = useState(0);

  const goTo = useCallback((index: number, dir: "next" | "prev" = "next") => {
    setDirection(dir);
    setAnimKey((k) => k + 1);
    setActive((index + SLIDES.length) % SLIDES.length);
  }, []);

  const next = useCallback(() => goTo(active + 1, "next"), [active, goTo]);
  const prev = useCallback(() => goTo(active - 1, "prev"), [active, goTo]);

  useEffect(() => {
    if (paused) return;
    const timer = setInterval(next, INTERVAL_MS);
    return () => clearInterval(timer);
  }, [paused, next]);

  const slide = SLIDES[active];
  const theme = THEME_STYLES[slide.theme];
  const Icon = slide.icon;

  return (
    <div
      className="w-full"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      aria-roledescription="carousel"
      aria-label="Destaques ViabilizA+ África"
    >
      <div className="pricing-hero-slide relative w-full overflow-hidden rounded-2xl shadow-[0_32px_80px_-24px_rgba(10,26,46,0.45)] sm:rounded-3xl">
        {/* Background image full bleed */}
        <div className="absolute inset-0">
          <Image
            key={slide.image}
            src={slide.image}
            alt=""
            fill
            priority={active === 0}
            className="pricing-hero-image object-cover object-center transition-transform duration-[1200ms] ease-out"
            sizes="(max-width: 1280px) 100vw, 1280px"
          />
          <div className={`absolute inset-0 bg-gradient-to-r ${theme.overlay}`} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-black/10" />
          <div className="pricing-hero-grid absolute inset-0 opacity-[0.06]" aria-hidden />
        </div>

        {/* Content — full width grid */}
        <div
          key={`${slide.id}-${animKey}`}
          className={`relative z-10 grid min-h-[480px] w-full grid-cols-1 lg:min-h-[520px] lg:grid-cols-[1.1fr_0.9fr] ${
            direction === "next" ? "pricing-slide-enter-next" : "pricing-slide-enter-prev"
          }`}
        >
          <div className="flex flex-col justify-between px-6 py-10 sm:px-10 sm:py-12 lg:px-12 lg:py-14">
            <div className="flex items-start justify-between gap-4">
              <span
                className={`pricing-slide-badge inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.2em] backdrop-blur-sm ${theme.badge}`}
              >
                <Sparkles className="h-3.5 w-3.5" />
                {slide.badge}
              </span>
              <span className="hidden items-center gap-1.5 rounded-full border border-white/10 bg-black/30 px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-white/70 backdrop-blur-sm sm:inline-flex">
                <BarChart3 className="h-3 w-3" />
                Plano de Preços v1.0
              </span>
            </div>

            <div className="my-6 max-w-2xl lg:my-8">
              <div className="pricing-slide-icon mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/20 bg-black/25 backdrop-blur-md">
                <Icon className={`h-7 w-7 ${theme.accent}`} />
              </div>
              <h1 className="font-[family-name:var(--font-poppins)] text-3xl font-bold leading-[1.1] tracking-tight text-white sm:text-4xl lg:text-[2.75rem] xl:text-5xl">
                <span className="pricing-slide-line block">{slide.title}</span>
                <span className={`pricing-slide-line pricing-slide-highlight mt-1 block ${theme.accent}`}>
                  {slide.highlight}
                </span>
              </h1>
              <p className="pricing-slide-desc mt-4 max-w-xl text-base leading-relaxed text-white/80 sm:text-lg">
                {slide.description}
              </p>
            </div>

            <div className="flex flex-wrap items-end justify-between gap-4">
              <div className="flex flex-wrap gap-3">
                {slide.stats.map((stat, i) => (
                  <div
                    key={stat.label}
                    className="pricing-slide-stat rounded-2xl border border-white/15 bg-black/30 px-4 py-3 backdrop-blur-md"
                    style={{ animationDelay: `${200 + i * 80}ms` }}
                  >
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-white/55">
                      {stat.label}
                    </p>
                    <p className="mt-0.5 font-[family-name:var(--font-poppins)] text-base font-bold text-white sm:text-lg">
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={prev}
                  aria-label="Slide anterior"
                  className="flex h-11 w-11 items-center justify-center rounded-full border border-white/25 bg-black/30 text-white backdrop-blur-sm transition hover:bg-white/20"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                  type="button"
                  onClick={next}
                  aria-label="Próximo slide"
                  className="flex h-11 w-11 items-center justify-center rounded-full border border-white/25 bg-black/30 text-white backdrop-blur-sm transition hover:bg-white/20"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Visual accent panel — desktop only */}
          <div className="relative hidden lg:block">
            <div className={`absolute inset-4 rounded-2xl bg-gradient-to-br opacity-20 ${theme.panel}`} />
            <div className="absolute inset-4 overflow-hidden rounded-2xl border border-white/10 shadow-2xl">
              <Image
                src={slide.image}
                alt={slide.badge}
                fill
                className="object-cover object-center"
                sizes="560px"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 z-20 h-1 bg-black/30">
          <div
            key={`progress-${active}-${animKey}`}
            className={`pricing-hero-progress h-full bg-gradient-to-r from-[#c6a43f] to-emerald-400 ${paused ? "pricing-hero-progress-paused" : ""}`}
          />
        </div>
      </div>

      <div className="mt-6 flex flex-col items-center gap-5">
        <div className="flex items-center gap-2" role="tablist" aria-label="Slides">
          {SLIDES.map((s, i) => (
            <button
              key={s.id}
              type="button"
              role="tab"
              aria-selected={i === active}
              aria-label={`Slide ${i + 1}: ${s.badge}`}
              onClick={() => goTo(i, i > active ? "next" : "prev")}
              className={`rounded-full transition-all duration-500 ${
                i === active ? "h-2.5 w-8 bg-[#0a1a2e]" : "h-2.5 w-2.5 bg-zinc-300 hover:bg-zinc-400"
              }`}
            />
          ))}
        </div>
        {currentPlanBanner}
      </div>
    </div>
  );
}
