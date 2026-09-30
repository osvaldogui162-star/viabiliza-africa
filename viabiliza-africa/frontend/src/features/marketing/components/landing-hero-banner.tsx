"use client";

import Image from "next/image";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type TouchEvent } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

import {
  BRAND_BANNER_APP,
  BRAND_BANNER_CONFIANCA,
  BRAND_BANNER_INVESTIMENTO,
} from "@/lib/constants/brand-assets";

type HeroSlide = {
  id: string;
  image: string;
  alt: string;
  label: string;
  href: string;
  /** object-position — subjecto (rosto) visível em cover full-bleed */
  focal: string;
};

const SLIDES: HeroSlide[] = [
  {
    id: "investimento",
    image: BRAND_BANNER_INVESTIMENTO,
    alt: "ViabilizA+ África — viabilidade e decisões de investimento",
    label: "Investimento",
    href: "/planos",
    focal: "32% 38%",
  },
  {
    id: "app",
    image: BRAND_BANNER_APP,
    alt: "ViabilizA+ África — plataforma SaaS de análise",
    label: "Plataforma",
    href: "/signup",
    focal: "26% 34%",
  },
  {
    id: "confianca",
    image: BRAND_BANNER_CONFIANCA,
    alt: "ViabilizA+ África — confiança e rastreabilidade",
    label: "Confiança",
    href: "/planos",
    focal: "34% 44%",
  },
];

const INTERVAL_MS = 8000;
const TRANSITION_MS = 1000;

/**
 * Largura 100% + altura proporcional ao banner (1024×794), com tecto em desktop.
 * object-cover preenche a faixa (sem barras laterais); no mobile a proporção coincide ~1:1.
 */
const HERO_CANVAS =
  "landing-hero-canvas w-full min-h-[13.5rem] h-[min(calc(100vw*794/1024),26rem)] sm:min-h-[14.5rem] sm:h-[min(calc(100vw*794/1024),27rem)] lg:h-[min(calc(100vw*794/1024),28rem)]";

export function LandingHeroBanner() {
  const [active, setActive] = useState(0);
  const [leaving, setLeaving] = useState<number | null>(null);
  const [direction, setDirection] = useState<1 | -1>(1);
  const [paused, setPaused] = useState(false);
  const [animKey, setAnimKey] = useState(0);
  const leaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const touchStartX = useRef<number | null>(null);

  const goTo = useCallback(
    (index: number, dir?: 1 | -1) => {
      const nextIndex = (index + SLIDES.length) % SLIDES.length;
      if (nextIndex === active) return;

      const resolvedDir =
        dir ??
        (nextIndex > active || (active === SLIDES.length - 1 && nextIndex === 0) ? 1 : -1);

      if (leaveTimerRef.current) clearTimeout(leaveTimerRef.current);

      setDirection(resolvedDir);
      setLeaving(active);
      setActive(nextIndex);
      setAnimKey((k) => k + 1);

      leaveTimerRef.current = setTimeout(() => {
        setLeaving(null);
        leaveTimerRef.current = null;
      }, TRANSITION_MS);
    },
    [active],
  );

  const next = useCallback(() => goTo(active + 1, 1), [active, goTo]);
  const prev = useCallback(() => goTo(active - 1, -1), [active, goTo]);

  useEffect(() => {
    if (paused) return;
    const timer = setInterval(next, INTERVAL_MS);
    return () => clearInterval(timer);
  }, [paused, next]);

  useEffect(
    () => () => {
      if (leaveTimerRef.current) clearTimeout(leaveTimerRef.current);
    },
    [],
  );

  const slide = SLIDES[active];

  function onTouchStart(e: TouchEvent) {
    touchStartX.current = e.touches[0]?.clientX ?? null;
  }

  function onTouchEnd(e: TouchEvent) {
    const start = touchStartX.current;
    if (start == null) return;
    const end = e.changedTouches[0]?.clientX ?? start;
    const delta = end - start;
    touchStartX.current = null;
    if (Math.abs(delta) < 48) return;
    if (delta < 0) next();
    else prev();
  }

  return (
    <section
      className="relative left-1/2 w-screen max-w-[100vw] -translate-x-1/2"
      aria-roledescription="carousel"
      aria-label="Campanhas ViabilizA+ África"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
    >
      <div className={`landing-hero-frame group relative w-full overflow-hidden ${HERO_CANVAS}`}>
        <div className="landing-hero-backdrop pointer-events-none absolute inset-0" aria-hidden />

        {SLIDES.map((s, i) => {
          const isActive = i === active;
          const isLeaving = i === leaving;
          if (!isActive && !isLeaving) return null;

          const motionClass = isActive
            ? direction === 1
              ? "landing-hero-enter-next"
              : "landing-hero-enter-prev"
            : direction === 1
              ? "landing-hero-exit-next"
              : "landing-hero-exit-prev";

          const media = (
            <div className={`landing-hero-motion absolute inset-0 ${motionClass}`}>
              <div className="landing-hero-img-scale absolute inset-0">
                <Image
                  src={s.image}
                  alt={s.alt}
                  fill
                  priority={i === 0}
                  draggable={false}
                  className="landing-hero-banner-img object-cover"
                  style={{ objectPosition: s.focal }}
                  sizes="100vw"
                />
              </div>
            </div>
          );

          if (isActive) {
            return (
              <Link
                key={s.id}
                href={s.href}
                className="absolute inset-0 z-20 block"
                aria-label={s.alt}
              >
                {media}
              </Link>
            );
          }

          return (
            <div key={`${s.id}-leave`} className="pointer-events-none absolute inset-0 z-10" aria-hidden>
              {media}
            </div>
          );
        })}

        <div className="landing-hero-dim pointer-events-none absolute inset-0 z-[6]" aria-hidden />
        <div className="landing-hero-vignette pointer-events-none absolute inset-0 z-[6]" aria-hidden />
        <div className="landing-hero-shimmer pointer-events-none absolute inset-0 z-[7]" aria-hidden />
        <div className="landing-hero-gold-line pointer-events-none absolute bottom-0 left-0 right-0 z-[8] h-px" aria-hidden />

        <div className="landing-hero-controls absolute inset-x-0 bottom-0 z-30">
          <div className="landing-hero-controls-progress-track" aria-hidden>
            <div
              key={`progress-${active}-${animKey}`}
              className={`landing-hero-progress h-full ${paused ? "landing-hero-progress-paused" : ""}`}
            />
          </div>

          <div className="landing-hero-controls-bar">
            <div className="mx-auto flex max-w-7xl items-stretch justify-between gap-4 px-4 py-3 sm:px-6 sm:py-3.5">
              <div className="flex min-w-0 flex-1 flex-col justify-center gap-1 sm:gap-1.5">
                <p className="landing-hero-controls-eyebrow">
                  Campanha {String(active + 1).padStart(2, "0")} / {String(SLIDES.length).padStart(2, "0")}
                </p>
                <p className="truncate font-[family-name:var(--font-poppins)] text-sm font-semibold tracking-tight text-white sm:text-[15px]">
                  {slide.label}
                </p>
              </div>

              <div
                className="hidden items-center gap-1 border-l border-white/10 pl-4 sm:flex"
                role="tablist"
                aria-label="Seleccionar banner"
              >
                {SLIDES.map((s, i) => (
                  <button
                    key={s.id}
                    type="button"
                    role="tab"
                    aria-selected={i === active}
                    aria-label={s.label}
                    onClick={() => goTo(i, i > active ? 1 : -1)}
                    className={`landing-hero-segment ${i === active ? "landing-hero-segment-active" : ""}`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-3 sm:border-l sm:border-white/10 sm:pl-4">
                <div className="flex items-center gap-1.5 sm:hidden" role="presentation">
                  {SLIDES.map((s, i) => (
                    <button
                      key={`m-${s.id}`}
                      type="button"
                      aria-label={s.label}
                      aria-current={i === active ? "true" : undefined}
                      onClick={() => goTo(i, i > active ? 1 : -1)}
                      className={`landing-hero-tick ${i === active ? "landing-hero-tick-active" : ""}`}
                    />
                  ))}
                </div>
                <div className="landing-hero-nav-group flex">
                  <button type="button" onClick={prev} aria-label="Banner anterior" className="landing-hero-nav-btn">
                    <ChevronLeft className="h-4 w-4" strokeWidth={2.25} />
                  </button>
                  <button type="button" onClick={next} aria-label="Próximo banner" className="landing-hero-nav-btn">
                    <ChevronRight className="h-4 w-4" strokeWidth={2.25} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
