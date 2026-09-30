"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const STORAGE_KEY = "va-product-tour-v1";

export type TourStep = {
  id: string;
  target: string;
  titlePt: string;
  titleEn: string;
  bodyPt: string;
  bodyEn: string;
  route?: string;
  tab?: string;
};

export const PRODUCT_TOUR_STEPS: TourStep[] = [
  {
    id: "dashboard",
    target: '[data-tour="dashboard-hero"]',
    titlePt: "Bem-vindo ao ViabilizA+",
    titleEn: "Welcome to ViabilizA+",
    bodyPt: "O seu painel centraliza projectos, alertas de plano e actividade recente.",
    bodyEn: "Your dashboard centralizes projects, plan alerts and recent activity.",
    route: "/dashboard",
  },
  {
    id: "projects",
    target: '[data-tour="nav-projects"]',
    titlePt: "Projectos de viabilidade",
    titleEn: "Feasibility projects",
    bodyPt: "Crie estudos estruturados por sector, país e moeda.",
    bodyEn: "Create structured studies by sector, country and currency.",
    route: "/projects",
  },
  {
    id: "ingestion",
    target: '[data-tour="tab-ingestion"]',
    titlePt: "Ingestão rastreável",
    titleEn: "Traceable ingestion",
    bodyPt: "Importe Excel, faça scraping ou ingestão automática com hash SHA-256.",
    bodyEn: "Import Excel, scrape prices or run auto-ingestion with SHA-256 hashes.",
    route: "/projects",
    tab: "ingestion",
  },
  {
    id: "analysis",
    target: '[data-tour="tab-analysis"]',
    titlePt: "Análise financeira",
    titleEn: "Financial analysis",
    bodyPt: "Calcule 60+ indicadores, Monte Carlo e cenários comparáveis.",
    bodyEn: "Calculate 60+ indicators, Monte Carlo and comparable scenarios.",
    route: "/projects",
    tab: "analysis",
  },
  {
    id: "reports",
    target: '[data-tour="tab-reports"]',
    titlePt: "Relatórios institucionais",
    titleEn: "Institutional reports",
    bodyPt: "Gere PDF Internacional, BFA ou BDA com QR de verificação.",
    bodyEn: "Generate International, BFA or BDA PDFs with verification QR.",
    route: "/projects",
    tab: "reports",
  },
];

export function useProductTour() {
  const pathname = usePathname();
  const router = useRouter();
  const [active, setActive] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (localStorage.getItem(STORAGE_KEY)) return;
    const timer = window.setTimeout(() => setActive(true), 1200);
    return () => window.clearTimeout(timer);
  }, []);

  const step = PRODUCT_TOUR_STEPS[stepIndex];

  const goToStep = useCallback(
    (index: number) => {
      const s = PRODUCT_TOUR_STEPS[index];
      if (!s) return;
      setStepIndex(index);
      if (s.route && !pathname.startsWith(s.route)) {
        router.push(s.route);
      }
      if (s.tab && typeof window !== "undefined") {
        sessionStorage.setItem("va-tour-tab", s.tab);
      }
    },
    [pathname, router],
  );

  function next() {
    if (stepIndex >= PRODUCT_TOUR_STEPS.length - 1) {
      finish();
      return;
    }
    goToStep(stepIndex + 1);
  }

  function skip() {
    finish();
  }

  function finish() {
    localStorage.setItem(STORAGE_KEY, "1");
    setActive(false);
    sessionStorage.removeItem("va-tour-tab");
  }

  function restart() {
    localStorage.removeItem(STORAGE_KEY);
    setStepIndex(0);
    setActive(true);
    goToStep(0);
  }

  return { active, step, stepIndex, total: PRODUCT_TOUR_STEPS.length, next, skip, finish, restart, goToStep };
}
