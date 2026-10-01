"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Building2, Leaf, ShieldCheck, TrendingUp } from "lucide-react";

import { slideFromLeft, slideFromRight, staggerContainer } from "@/features/marketing/lib/landing-motion";
import {
  MARKETING_HERO_AFRICA,
  MARKETING_HERO_MULTISECTOR,
  MARKETING_HERO_TRACEABILITY,
  MARKETING_HERO_VIABILITY,
} from "@/lib/constants/brand-assets";

const FEATURES = [
  {
    icon: TrendingUp,
    title: "Modelação financeira",
    description: "VPL, TIR, payback, cenários e Monte Carlo — indicadores prontos para comités de investimento.",
    image: MARKETING_HERO_VIABILITY,
  },
  {
    icon: ShieldCheck,
    title: "Rastreabilidade SHA-256",
    description: "Orçamentos e relatórios com hash verificável, QR Code e trilha de auditoria completa.",
    image: MARKETING_HERO_TRACEABILITY,
  },
  {
    icon: Leaf,
    title: "Multi-setorial & ESG",
    description: "Agricultura (DSSAT), indústria, infraestruturas, Digital Twin e relatórios ESG integrados.",
    image: MARKETING_HERO_MULTISECTOR,
  },
  {
    icon: Building2,
    title: "Angola · África",
    description: "Relatórios BFA/BDA, faturação em AOA, AppyPay e portal para instituições financiadoras.",
    image: MARKETING_HERO_AFRICA,
  },
];

export function LandingServicesSection() {
  const reduce = useReducedMotion();

  return (
    <section id="funcionalidades" className="landing-section-padding bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-xl"
        >
          <p className="landing-eyebrow mb-3">Serviços</p>
          <h2 className="landing-heading-xl text-[#0a1a2e]">Funcionalidades em imagem real</h2>
          <p className="mt-3 text-zinc-600">
            Campanhas e visuais oficiais ViabilizA+ — a mesma identidade que vê na plataforma e nos planos.
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer(0.15)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.12 }}
          className="mt-14 space-y-20"
        >
          {FEATURES.map((f, i) => {
            const textVariant = i % 2 === 0 ? slideFromLeft : slideFromRight;
            const imageVariant = i % 2 === 0 ? slideFromRight : slideFromLeft;
            return (
              <article key={f.title} className="grid items-center gap-8 lg:grid-cols-2 lg:gap-14">
                <motion.div variants={textVariant}>
                  <motion.div
                    whileHover={reduce ? undefined : { rotate: [0, -6, 6, 0], scale: 1.08 }}
                    transition={{ duration: 0.5 }}
                    className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-[#047857]"
                  >
                    <f.icon className="h-6 w-6" />
                  </motion.div>
                  <h3 className="landing-heading-lg text-[#0a1a2e]">{f.title}</h3>
                  <p className="mt-3 text-base leading-relaxed text-zinc-600">{f.description}</p>
                </motion.div>
                <motion.div
                  variants={imageVariant}
                  whileHover={reduce ? undefined : { scale: 1.02, y: -6 }}
                  className="landing-glow-border relative aspect-[16/10] overflow-hidden rounded-2xl border border-zinc-200 shadow-xl"
                >
                  <Image
                    src={f.image}
                    alt={f.title}
                    fill
                    className="object-cover object-center transition duration-700 hover:scale-105"
                    sizes="(max-width: 1024px) 100vw, 560px"
                  />
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#0a1a2e]/30 to-transparent" />
                </motion.div>
              </article>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
