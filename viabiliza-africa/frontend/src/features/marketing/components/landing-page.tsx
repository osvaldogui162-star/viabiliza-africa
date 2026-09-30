"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  BarChart3,
  Building2,
  Leaf,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import { LandingHeroBanner } from "@/features/marketing/components/landing-hero-banner";
import { MarketingShell } from "@/features/marketing/components/marketing-shell";
import { BRAND_LOGO_PATH } from "@/lib/constants/brand-assets";

const FEATURES = [
  {
    icon: TrendingUp,
    title: "Modelação financeira",
    description: "VPL, TIR, payback, cenários e Monte Carlo — indicadores prontos para comités de investimento.",
    image: "/subscription/hero-viability.png",
  },
  {
    icon: ShieldCheck,
    title: "Rastreabilidade SHA-256",
    description: "Orçamentos e relatórios com hash verificável, QR Code e trilha de auditoria completa.",
    image: "/subscription/hero-traceability.png",
  },
  {
    icon: Leaf,
    title: "Multi-setorial & ESG",
    description: "Agricultura (DSSAT), indústria, infraestruturas, Digital Twin e relatórios ESG integrados.",
    image: "/subscription/hero-multisector.png",
  },
  {
    icon: Building2,
    title: "Angola · África",
    description: "Relatórios BFA/BDA, faturação em AOA, AppyPay e portal para instituições financiadoras.",
    image: "/subscription/hero-africa.png",
  },
];

const BANK_LOGOS = [
  { src: "/banks/bfa.svg", alt: "BFA" },
  { src: "/banks/bda.png", alt: "BDA" },
  { src: "/banks/bai.svg", alt: "BAI" },
  { src: "/banks/bic.svg", alt: "BIC" },
  { src: "/banks/bci.svg", alt: "BCI" },
  { src: "/banks/bni.svg", alt: "BNI" },
  { src: "/banks/bpc.png", alt: "BPC" },
  { src: "/banks/sol.svg", alt: "SOL" },
];

function useInView(threshold = 0.12) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) setVisible(true);
      },
      { threshold },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return { ref, visible };
}

function RevealSection({
  children,
  className = "",
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  const { ref, visible } = useInView();
  return (
    <div
      ref={ref}
      className={`landing-reveal ${visible ? "landing-reveal-visible" : ""} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export function LandingPage() {
  return (
    <MarketingShell>
      <LandingHeroBanner />

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 sm:py-20">
        <RevealSection className="text-center">
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">Porquê ViabilizA+</p>
          <h2 className="mt-3 font-[family-name:var(--font-poppins)] text-3xl font-bold tracking-tight text-[#0a1a2e] sm:text-4xl">
            Do Excel à decisão bancária
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-zinc-600">
            Plataforma angolana de viabilidade com ingestão de custos, análise avançada e relatórios alinhados a
            instituições financeiras.
          </p>
        </RevealSection>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: BarChart3, label: "Indicadores", value: "40+" },
            { icon: Sparkles, label: "Sectores", value: "6+" },
            { icon: ShieldCheck, label: "Integridade", value: "SHA-256" },
            { icon: TrendingUp, label: "Pagamentos", value: "AppyPay" },
          ].map((stat, i) => (
            <RevealSection key={stat.label} delay={i * 80}>
              <div className="landing-stat-card group rounded-2xl border border-zinc-200/80 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
                <stat.icon className="h-8 w-8 text-teal-600 transition group-hover:scale-110" />
                <p className="mt-4 font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#0a1a2e]">
                  {stat.value}
                </p>
                <p className="mt-1 text-sm font-medium text-zinc-500">{stat.label}</p>
              </div>
            </RevealSection>
          ))}
        </div>
      </section>

      <section id="funcionalidades" className="bg-white py-16 sm:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <RevealSection>
            <h2 className="font-[family-name:var(--font-poppins)] text-3xl font-bold text-[#0a1a2e] sm:text-4xl">
              Funcionalidades em imagem real
            </h2>
            <p className="mt-3 max-w-xl text-zinc-600">
              Campanhas e visuais oficiais ViabilizA+ — a mesma identidade que vê na plataforma e nos planos.
            </p>
          </RevealSection>

          <div className="mt-12 space-y-16">
            {FEATURES.map((f, i) => (
              <RevealSection key={f.title} delay={100}>
                <article
                  className={`grid items-center gap-8 lg:grid-cols-2 lg:gap-12 ${
                    i % 2 === 1 ? "lg:[direction:rtl]" : ""
                  }`}
                >
                  <div className={`${i % 2 === 1 ? "lg:[direction:ltr]" : ""}`}>
                    <div className="landing-feature-icon mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
                      <f.icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-[family-name:var(--font-poppins)] text-2xl font-bold text-[#0a1a2e]">
                      {f.title}
                    </h3>
                    <p className="mt-3 text-base leading-relaxed text-zinc-600">{f.description}</p>
                  </div>
                  <div
                    className={`landing-image-frame relative aspect-[16/10] overflow-hidden rounded-2xl border border-zinc-200 shadow-xl ${
                      i % 2 === 1 ? "lg:[direction:ltr]" : ""
                    }`}
                  >
                    <Image
                      src={f.image}
                      alt={f.title}
                      fill
                      className="object-cover object-center transition duration-700 hover:scale-105"
                      sizes="(max-width: 1024px) 100vw, 560px"
                    />
                    <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#0a1a2e]/25 to-transparent" />
                  </div>
                </article>
              </RevealSection>
            ))}
          </div>
        </div>
      </section>

      <section id="sectores" className="border-y border-zinc-200 bg-[#0a1a2e] py-14 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <RevealSection className="text-center">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-300/90">Parceiros financeiros</p>
            <h2 className="mt-2 font-[family-name:var(--font-poppins)] text-2xl font-bold sm:text-3xl">
              Integração com o ecossistema bancário angolano
            </h2>
          </RevealSection>
          <div className="landing-marquee-mask relative mt-10 overflow-hidden">
            <div className="landing-marquee flex w-max gap-12">
              {[...BANK_LOGOS, ...BANK_LOGOS].map((bank, i) => (
                <div
                  key={`${bank.alt}-${i}`}
                  className="flex h-16 w-36 shrink-0 items-center justify-center rounded-xl bg-white/95 px-4 py-3 shadow-md"
                >
                  <Image src={bank.src} alt={bank.alt} width={120} height={48} className="max-h-10 w-auto object-contain" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <RevealSection>
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#064e3b] via-[#047857] to-[#0a1a2e] px-8 py-14 text-center text-white shadow-2xl sm:px-16">
            <div className="landing-orb landing-orb-1 pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-emerald-400/20 blur-3xl" />
            <div className="landing-orb landing-orb-2 pointer-events-none absolute -bottom-16 -right-16 h-56 w-56 rounded-full bg-[#c6a43f]/20 blur-3xl" />
            <div className="relative mx-auto flex max-w-lg flex-col items-center">
              <Image
                src={BRAND_LOGO_PATH}
                alt=""
                width={180}
                height={70}
                className="mb-6 h-14 w-auto opacity-95"
              />
              <h2 className="font-[family-name:var(--font-poppins)] text-3xl font-bold sm:text-4xl">
                Pronto para o seu próximo projecto?
              </h2>
              <p className="mt-4 text-base text-emerald-50/90">
                Crie a conta, escolha o plano e comece a modelar investimentos com credibilidade.
              </p>
              <div className="mt-8 flex flex-wrap justify-center gap-3">
                <Link
                  href="/signup"
                  className="landing-cta-shine rounded-full bg-white px-8 py-3.5 text-sm font-bold text-[#064e3b] shadow-lg transition hover:bg-emerald-50"
                >
                  Registar gratuitamente
                </Link>
                <Link
                  href="/planos"
                  className="rounded-full border border-white/40 px-8 py-3.5 text-sm font-semibold text-white transition hover:bg-white/10"
                >
                  Comparar planos
                </Link>
              </div>
            </div>
          </div>
        </RevealSection>
      </section>
    </MarketingShell>
  );
}
