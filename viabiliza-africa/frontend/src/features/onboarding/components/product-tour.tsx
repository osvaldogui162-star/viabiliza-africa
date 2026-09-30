"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/components/providers/locale-provider";
import { useProductTour } from "@/features/onboarding/hooks/use-product-tour";
import { cn } from "@/lib/utils/cn";

export function ProductTour() {
  const { locale } = useI18n();
  const en = locale === "en";
  const { active, step, stepIndex, total, next, skip } = useProductTour();
  const [rect, setRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    if (!active || !step) return;
    const update = () => {
      const el = document.querySelector(step.target);
      setRect(el?.getBoundingClientRect() ?? null);
    };
    update();
    const id = window.setInterval(update, 400);
    window.addEventListener("resize", update);
    window.addEventListener("scroll", update, true);
    return () => {
      window.clearInterval(id);
      window.removeEventListener("resize", update);
      window.removeEventListener("scroll", update, true);
    };
  }, [active, step]);

  if (!active || !step) return null;

  const isSidebarTarget = step.target.includes("nav-");

  return (
    <div className="fixed inset-0 z-[100] pointer-events-none">
      {/* Overlay só sobre o conteúdo principal — sidebar fica sempre legível em desktop */}
      <div
        className={cn(
          "pointer-events-auto absolute inset-0 bg-slate-950/50 backdrop-blur-[1px]",
          isSidebarTarget && "lg:left-[var(--sidebar-width,220px)]",
        )}
        onClick={skip}
        aria-hidden
      />
      {rect ? (
        <div
          className="pointer-events-none absolute z-[101] rounded-xl ring-4 ring-teal-400 ring-offset-2 ring-offset-white transition-all duration-300"
          style={{
            top: rect.top - 6,
            left: rect.left - 6,
            width: rect.width + 12,
            height: rect.height + 12,
            ...(isSidebarTarget
              ? {}
              : { boxShadow: "0 0 0 9999px rgba(15, 23, 42, 0.5)" }),
          }}
        />
      ) : null}

      <div
        className="pointer-events-auto absolute z-[102] w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-white/20 bg-gradient-to-br from-slate-900 to-teal-950 p-5 text-white shadow-2xl bottom-6 right-4 left-4 mx-auto sm:left-auto sm:mx-0"
      >
        <div className="mb-3 flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-teal-300">
            <Sparkles className="h-4 w-4" />
            {en ? "Guided tour" : "Tour guiado"} · {stepIndex + 1}/{total}
          </div>
          <button type="button" onClick={skip} className="rounded-lg p-1 text-white/60 hover:bg-white/10">
            <X className="h-4 w-4" />
          </button>
        </div>
        <h3 className="text-lg font-bold">{en ? step.titleEn : step.titlePt}</h3>
        <p className="mt-2 text-sm text-white/80">{en ? step.bodyEn : step.bodyPt}</p>
        <div className="mt-4 flex gap-2">
          <Button variant="outline" className="border-white/20 bg-white/10 text-white hover:bg-white/20" onClick={skip}>
            {en ? "Skip" : "Saltar"}
          </Button>
          <Button className="flex-1 gap-1 bg-teal-500 hover:bg-teal-400" onClick={next}>
            {stepIndex >= total - 1 ? (en ? "Finish" : "Concluir") : en ? "Next" : "Seguinte"}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="mt-3 flex gap-1">
          {Array.from({ length: total }).map((_, i) => (
            <span key={i} className={cn("h-1 flex-1 rounded-full", i <= stepIndex ? "bg-teal-400" : "bg-white/20")} />
          ))}
        </div>
      </div>
    </div>
  );
}
