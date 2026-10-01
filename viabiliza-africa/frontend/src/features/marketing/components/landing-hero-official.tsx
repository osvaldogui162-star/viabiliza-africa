"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";

import {
  BRAND_BANNER_APP,
  BRAND_BANNER_CONFIANCA,
  BRAND_BANNER_INVESTIMENTO,
} from "@/lib/constants/brand-assets";
import { heroTextItem, heroTextStagger, floatLoop, pulseGlow } from "@/features/marketing/lib/landing-motion";

const SLIDES = [
  {
    id: "investimento",
    image: BRAND_BANNER_INVESTIMENTO,
    focal: "32% 38%",
    tagline: "Viabilidade de investimento",
    title: "Decisões de crédito com rigor bancário",
    description:
      "Modelação VPL, TIR e cenários alinhados a comités BFA, BDA e instituições financiadoras em Angola.",
    cta: "Ver planos",
    href: "/planos",
    secondaryHref: "/#funcionalidades",
  },
  {
    id: "app",
    image: BRAND_BANNER_APP,
    focal: "26% 34%",
    tagline: "Plataforma SaaS",
    title: "Do Excel ao relatório auditável",
    description:
      "Ingestão de custos, análise avançada, colaboração e relatórios num único fluxo digital.",
    cta: "Começar grátis",
    href: "/signup",
    secondaryHref: "/login",
  },
  {
    id: "confianca",
    image: BRAND_BANNER_CONFIANCA,
    focal: "34% 44%",
    tagline: "Confiança & integridade",
    title: "SHA-256, QR Code e trilha completa",
    description:
      "Cada orçamento e relatório verificável — transparência para promotores, bancos e auditores.",
    cta: "Criar conta",
    href: "/signup",
    secondaryHref: "/planos",
  },
] as const;

const INTERVAL_MS = 7000;
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  id: i,
  left: `${8 + ((i * 17) % 84)}%`,
  top: `${12 + ((i * 23) % 72)}%`,
  size: 2 + (i % 3),
  delay: 0.25 * i,
}));

export function LandingHeroOfficial() {
  const reduce = useReducedMotion();
  const [index, setIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  const next = useCallback(() => setIndex((i) => (i + 1) % SLIDES.length), []);
  const prev = useCallback(() => setIndex((i) => (i - 1 + SLIDES.length) % SLIDES.length), []);
  const go = useCallback((i: number) => setIndex(i), []);

  useEffect(() => {
    if (reduce) return;
    const start = Date.now();
    const tick = setInterval(() => {
      setProgress(Math.min((Date.now() - start) / INTERVAL_MS, 1));
    }, 40);
    return () => clearInterval(tick);
  }, [index, reduce]);

  useEffect(() => {
    if (reduce) return;
    setProgress(0);
    const timer = setInterval(next, INTERVAL_MS);
    return () => clearInterval(timer);
  }, [next, reduce, index]);

  const slide = SLIDES[index];

  return (
    <section
      id="home"
      className="landing-hero-official relative left-1/2 w-screen max-w-[100vw] -translate-x-1/2 overflow-hidden"
    >
      <div className="relative h-[min(56vh,32rem)] min-h-[320px] max-h-[560px] sm:min-h-[380px]">
        {SLIDES.map((s, i) => (
          <motion.div
            key={s.id}
            className="absolute inset-0"
            initial={false}
            animate={{ opacity: i === index ? 1 : 0, scale: i === index ? 1 : 1.06 }}
            transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
            style={{ zIndex: i === index ? 2 : 1 }}
            aria-hidden={i !== index}
          >
            <motion.div
              className="absolute inset-0"
              animate={i === index && !reduce ? { scale: [1, 1.08] } : { scale: 1.06 }}
              transition={
                i === index && !reduce
                  ? { duration: INTERVAL_MS / 1000, ease: "linear" }
                  : { duration: 0.3 }
              }
            >
              <Image
                src={s.image}
                alt=""
                fill
                priority={i === 0}
                className="object-cover brightness-[0.68] saturate-[0.95]"
                style={{ objectPosition: s.focal }}
                sizes="100vw"
              />
            </motion.div>
            <div className="absolute inset-0 bg-gradient-to-r from-[#0a1a2e]/94 via-[#0a1a2e]/78 to-[#064e3b]/35" />
            <div className="landing-hero-grid absolute inset-0 opacity-[0.08]" aria-hidden />
          </motion.div>
        ))}

        {!reduce && (
          <>
            <motion.div
              className="pointer-events-none absolute -top-16 right-[12%] z-[3] h-72 w-72 rounded-full bg-emerald-500/25 blur-3xl"
              animate={floatLoop(9)}
            />
            <motion.div
              className="pointer-events-none absolute bottom-8 left-[8%] z-[3] h-56 w-56 rounded-full bg-[#c6a43f]/15 blur-3xl"
              animate={floatLoop(11, 0.5)}
            />
            {PARTICLES.map((p) => (
              <motion.span
                key={p.id}
                className="pointer-events-none absolute z-[5] rounded-full bg-white/35"
                style={{ left: p.left, top: p.top, width: p.size, height: p.size }}
                animate={{ y: [0, -22, 0], opacity: [0.15, 0.75, 0.15] }}
                transition={{ duration: 4 + p.delay, repeat: Infinity, delay: p.delay }}
              />
            ))}
          </>
        )}

        <div className="relative z-10 flex h-full items-center pb-24 pt-20 sm:pb-28 sm:pt-24">
          <div className="mx-auto w-full max-w-7xl px-4 sm:px-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={slide.id}
                variants={heroTextStagger}
                initial="hidden"
                animate="visible"
                exit="hidden"
                className="max-w-2xl"
              >
                <motion.p variants={heroTextItem} className="landing-eyebrow-light mb-3">
                  {slide.tagline}
                </motion.p>
                <motion.h1 variants={heroTextItem} className="landing-text-shimmer text-3xl font-bold leading-tight sm:text-4xl lg:text-[2.65rem]">
                  {slide.title}
                </motion.h1>
                <motion.p variants={heroTextItem} className="mt-4 max-w-xl text-sm leading-relaxed text-white/82 sm:text-base">
                  {slide.description}
                </motion.p>
                <motion.div variants={heroTextItem} className="mt-7 flex flex-wrap gap-3">
                  <motion.div animate={reduce ? undefined : pulseGlow()} whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.97 }}>
                    <Link
                      href={slide.href}
                      className="inline-flex items-center gap-2 rounded-md bg-[#047857] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-900/40"
                    >
                      {slide.cta}
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.03, y: -2 }} whileTap={{ scale: 0.98 }}>
                    <Link
                      href={slide.secondaryHref}
                      className="inline-flex items-center gap-2 rounded-md border border-white/30 bg-white/10 px-6 py-3 text-sm font-semibold text-white backdrop-blur-sm"
                    >
                      Explorar
                    </Link>
                  </motion.div>
                </motion.div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        <div className="absolute bottom-[4.5rem] left-1/2 z-20 flex -translate-x-1/2 gap-2 sm:bottom-20">
          {SLIDES.map((_, i) => (
            <button
              key={i}
              type="button"
              onClick={() => go(i)}
              className="group relative h-1 w-12 overflow-hidden rounded-full bg-white/25 sm:w-16"
              aria-label={`Slide ${i + 1}`}
            >
              <motion.span
                className="absolute inset-y-0 left-0 bg-[#c6a43f]"
                animate={{ width: i === index ? `${progress * 100}%` : i < index ? "100%" : "0%" }}
                transition={{ duration: 0.08 }}
              />
            </button>
          ))}
        </div>

        <motion.a
          href="#funcionalidades"
          className="absolute bottom-4 left-1/2 z-20 hidden -translate-x-1/2 flex-col items-center gap-1 text-white/50 sm:flex"
          animate={reduce ? undefined : { y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          aria-label="Scroll"
        >
          <span className="text-[10px] font-medium uppercase tracking-widest">Descer</span>
          <ChevronDown className="h-4 w-4" />
        </motion.a>

        <button
          type="button"
          onClick={prev}
          className="absolute left-3 top-1/2 z-20 hidden -translate-y-1/2 rounded-full border border-white/15 bg-white/10 p-2.5 text-white backdrop-blur-md hover:bg-white/20 sm:flex"
          aria-label="Anterior"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={next}
          className="absolute right-3 top-1/2 z-20 hidden -translate-y-1/2 rounded-full border border-white/15 bg-white/10 p-2.5 text-white backdrop-blur-md hover:bg-white/20 sm:flex"
          aria-label="Próximo"
        >
          <ChevronRight className="h-5 w-5" />
        </button>

        <div className="landing-hero-controls absolute inset-x-0 bottom-0 z-30">
          <div className="landing-hero-controls-bar border-t border-white/10">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5 text-[11px] text-white/70 sm:px-6">
              <span>
                Campanha {String(index + 1).padStart(2, "0")} / {String(SLIDES.length).padStart(2, "0")} — {slide.tagline}
              </span>
              <span className="hidden sm:inline">ViabilizA+ África · Estudos de viabilidade</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
