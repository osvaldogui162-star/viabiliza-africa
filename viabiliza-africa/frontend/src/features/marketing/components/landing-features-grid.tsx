"use client";

import { motion, useReducedMotion } from "framer-motion";
import { BarChart3, Leaf, ShieldCheck, TrendingUp } from "lucide-react";

import { fadeUp, staggerContainer } from "@/features/marketing/lib/landing-motion";

const ITEMS = [
  {
    icon: TrendingUp,
    title: "Modelação financeira",
    description: "VPL, TIR, payback, Monte Carlo e sensibilidade para comités de investimento.",
  },
  {
    icon: ShieldCheck,
    title: "Integridade SHA-256",
    description: "Orçamentos e relatórios com hash verificável, QR Code e auditoria completa.",
  },
  {
    icon: Leaf,
    title: "Multi-setorial & ESG",
    description: "Agricultura, indústria, infraestruturas, Digital Twin e relatórios ESG.",
  },
  {
    icon: BarChart3,
    title: "Angola · África",
    description: "Relatórios BFA/BDA, AOA, AppyPay e portal para financiadores.",
  },
];

export function LandingFeaturesGrid() {
  const reduce = useReducedMotion();

  return (
    <section className="relative z-10 -mt-8 pb-4 sm:-mt-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.25 }}
          variants={staggerContainer(0.08)}
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {ITEMS.map((item, i) => (
            <motion.div
              key={item.title}
              variants={fadeUp}
              custom={i}
              whileHover={reduce ? undefined : { y: -10, transition: { type: "spring", stiffness: 320, damping: 22 } }}
              className="landing-glow-border group border border-zinc-200/90 bg-white p-6 shadow-sm sm:p-7"
            >
              <motion.div
                initial={reduce ? false : { scale: 0, rotate: -120 }}
                whileInView={{ scale: 1, rotate: 0 }}
                viewport={{ once: true }}
                transition={{ type: "spring", stiffness: 200, damping: 16, delay: 0.06 * i }}
                whileHover={reduce ? undefined : { scale: 1.12, rotate: 6 }}
                className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-[#047857] transition-colors group-hover:bg-[#047857] group-hover:text-white"
              >
                <item.icon className="h-6 w-6" />
              </motion.div>
              <h2 className="mb-2 text-base font-bold text-[#0a1a2e]">{item.title}</h2>
              <p className="text-sm leading-relaxed text-zinc-600">{item.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
