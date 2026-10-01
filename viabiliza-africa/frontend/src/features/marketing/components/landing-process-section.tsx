"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { Play } from "lucide-react";

import { fadeUp, staggerContainer } from "@/features/marketing/lib/landing-motion";
import { MARKETING_HERO_VIABILITY } from "@/lib/constants/brand-assets";

const STEPS = [
  {
    title: "Cadastrar projecto",
    description: "Empresa promotora, sector, localização e equipa — base auditável desde o primeiro passo.",
  },
  {
    title: "Ingerir & analisar",
    description: "Custos, scraping Angola, indicadores, cenários e simulações num fluxo integrado.",
  },
  {
    title: "Relatório & financiamento",
    description: "PDF BFA/BDA, verificação pública e submissão ao portal do financiador quando aplicável.",
  },
];

export function LandingProcessSection() {
  const reduce = useReducedMotion();

  return (
    <section className="landing-section-padding overflow-hidden bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto mb-14 max-w-3xl text-center"
        >
          <p className="landing-eyebrow mb-3">Como funciona</p>
          <h2 className="landing-heading-xl text-[#0a1a2e]">Do dossier ao comité em três fases</h2>
        </motion.div>

        <motion.div
          variants={staggerContainer(0.12)}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.15 }}
          className="relative grid gap-8 md:grid-cols-3"
        >
          <div
            className="pointer-events-none absolute top-8 right-[16.66%] left-[16.66%] hidden h-0.5 bg-gradient-to-r from-transparent via-[#047857]/35 to-transparent md:block"
            aria-hidden
          >
            <motion.div
              className="h-full origin-left bg-[#047857]"
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>
          {STEPS.map((step, i) => (
            <motion.div
              key={step.title}
              variants={fadeUp}
              custom={i}
              whileHover={reduce ? undefined : { y: -12, scale: 1.02 }}
              className="group relative overflow-hidden rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm"
            >
              <motion.div
                animate={reduce ? undefined : { rotate: [0, 4, -4, 0] }}
                transition={{ duration: 4, repeat: Infinity, delay: 0.4 * i }}
                className="relative mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#047857] text-2xl font-bold text-white shadow-md transition-transform group-hover:scale-110"
              >
                {i + 1}
              </motion.div>
              <h3 className="mb-3 text-xl font-bold text-[#0a1a2e]">{step.title}</h3>
              <p className="text-sm leading-relaxed text-zinc-600">{step.description}</p>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.15, duration: 0.75 }}
          className="mt-16 overflow-hidden rounded-2xl bg-[#0a1a2e]"
        >
          <div className="grid items-center lg:grid-cols-2">
            <div className="relative min-h-[260px] lg:min-h-[340px]">
              <Image
                src={MARKETING_HERO_VIABILITY}
                alt="Análise de viabilidade"
                fill
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
              <div className="absolute inset-0 bg-[#0a1a2e]/45" />
              <motion.div
                whileHover={{ scale: 1.12 }}
                whileTap={{ scale: 0.95 }}
                className="absolute inset-0 flex items-center justify-center"
              >
                <Link
                  href="/signup"
                  aria-label="Ver demonstração"
                  className="flex h-20 w-20 items-center justify-center rounded-full bg-[#047857] text-white shadow-2xl ring-4 ring-white/20"
                >
                  <Play className="h-8 w-8 fill-white" />
                </Link>
              </motion.div>
            </div>
            <div className="p-8 lg:p-12">
              <h3 className="landing-heading-lg mb-4 text-white">Plataforma pensada para analistas</h3>
              <p className="leading-relaxed text-white/75">
                Escritório de viabilidade, equipa, permissões por projecto e relatórios com assinatura
                institucional — o mesmo rigor que o comité espera, sem folhas Excel dispersas.
              </p>
              <Link
                href="/signup"
                className="mt-6 inline-flex rounded-md bg-white px-5 py-2.5 text-sm font-semibold text-[#0a1a2e] transition hover:bg-emerald-50"
              >
                Experimentar agora
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
