"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Building2, FileCheck, Layers, Users } from "lucide-react";

import { fadeUp, staggerContainer } from "@/features/marketing/lib/landing-motion";

const STATS = [
  { value: 40, suffix: "+", label: "Indicadores financeiros", icon: Layers },
  { value: 6, suffix: "+", label: "Sectores modelados", icon: Building2 },
  { value: 100, suffix: "%", label: "Rastreabilidade", icon: FileCheck },
  { value: 24, suffix: "/7", label: "Plataforma cloud", icon: Users },
];

function StatCounter({
  value,
  suffix,
  label,
  icon: Icon,
  index,
}: {
  value: number;
  suffix: string;
  label: string;
  icon: typeof Layers;
  index: number;
}) {
  const reduce = useReducedMotion();
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (reduce) {
      setCount(value);
      return;
    }
    const obs = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setStarted(true);
          obs.disconnect();
        }
      },
      { threshold: 0.4 },
    );
    const el = document.getElementById(`landing-stat-${index}`);
    if (el) obs.observe(el);
    return () => obs.disconnect();
  }, [index, reduce, value]);

  useEffect(() => {
    if (!started || reduce) return;
    const t0 = performance.now();
    const frame = (now: number) => {
      const p = Math.min((now - t0) / 2200, 1);
      const eased = 1 - (1 - p) ** 4;
      setCount(Math.floor(eased * value));
      if (p < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }, [started, value, reduce]);

  return (
    <motion.div
      id={`landing-stat-${index}`}
      variants={fadeUp}
      custom={index}
      whileHover={reduce ? undefined : { scale: 1.05 }}
      className="text-center"
    >
      <motion.div
        animate={started && !reduce ? { rotate: [0, 6, -6, 0] } : undefined}
        transition={{ duration: 0.6, delay: 0.25 }}
        className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-white/10 text-[#c6a43f] ring-1 ring-white/10"
      >
        <Icon className="h-7 w-7" />
      </motion.div>
      <div className="flex items-baseline justify-center gap-0.5">
        <span className="text-4xl font-bold text-white md:text-5xl">{count}</span>
        <span className="text-2xl font-bold text-[#c6a43f]">{suffix}</span>
      </div>
      <p className="mt-2 text-xs font-medium uppercase tracking-wide text-white/65">{label}</p>
    </motion.div>
  );
}

export function LandingStatsSection() {
  const reduce = useReducedMotion();

  return (
    <section className="relative overflow-hidden bg-[#0a1a2e] py-16 md:py-20">
      {!reduce && (
        <motion.div
          className="absolute inset-0 opacity-25"
          animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
          transition={{ duration: 14, repeat: Infinity, ease: "linear" }}
          style={{
            backgroundImage:
              "linear-gradient(90deg, transparent, rgba(4,120,87,0.45), transparent, rgba(198,164,63,0.35), transparent)",
            backgroundSize: "200% 100%",
          }}
        />
      )}
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-12 text-center"
        >
          <p className="landing-eyebrow-light mb-2 text-[#c6a43f]">Números que importam</p>
          <h2 className="landing-heading-lg text-white">Credibilidade em cada indicador</h2>
        </motion.div>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer(0.12)}
          className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4"
        >
          {STATS.map((s, i) => (
            <StatCounter key={s.label} {...s} index={i} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
