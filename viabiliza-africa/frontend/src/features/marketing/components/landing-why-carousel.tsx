"use client";

import { useCallback, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ChevronLeft, ChevronRight, Quote } from "lucide-react";

const REASONS = [
  {
    step: "01",
    title: "Dados angolanos reais",
    description:
      "Scraping, taxas bancárias e benchmarks locais — menos suposições genéricas, mais contexto para o comité em AOA.",
  },
  {
    step: "02",
    title: "Rigor verificável",
    description:
      "Hashes SHA-256, portal de verificação e trilha de auditoria: cada número no relatório tem origem demonstrável.",
  },
  {
    step: "03",
    title: "Ecossistema financiador",
    description:
      "Portal BFA/BDA, monitorização pós-desembolso e integração Terminal — viabilidade ligada à execução real.",
  },
];

export function LandingWhyCarousel() {
  const reduce = useReducedMotion();
  const [index, setIndex] = useState(0);
  const [dir, setDir] = useState(0);

  const go = useCallback(
    (next: number) => {
      setDir(next > index ? 1 : -1);
      setIndex(next);
    },
    [index],
  );

  const next = () => go((index + 1) % REASONS.length);
  const prev = () => go((index - 1 + REASONS.length) % REASONS.length);

  const item = REASONS[index];

  const variants = {
    enter: (d: number) => ({ x: d > 0 ? 80 : -80, opacity: 0, scale: 0.96 }),
    center: { x: 0, opacity: 1, scale: 1, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] } },
    exit: (d: number) => ({ x: d > 0 ? -80 : 80, opacity: 0, scale: 0.96, transition: { duration: 0.4 } }),
  };

  return (
    <section className="landing-section-padding overflow-hidden bg-[#f0f4f2]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto mb-12 max-w-3xl text-center"
        >
          <p className="landing-eyebrow mb-3">Porquê ViabilizA+</p>
          <h2 className="landing-heading-xl text-[#0a1a2e]">Feito para decisões de investimento</h2>
          <p className="mt-3 text-zinc-600">Três pilares que distinguem a plataforma de folhas isoladas.</p>
        </motion.div>

        <div className="relative mx-auto max-w-4xl">
          <motion.div
            whileHover={reduce ? undefined : { y: -4 }}
            transition={{ type: "spring", stiffness: 280, damping: 24 }}
            className="overflow-hidden rounded-2xl bg-white p-8 shadow-lg md:p-12"
          >
            <AnimatePresence mode="wait" custom={dir}>
              <motion.div
                key={index}
                custom={dir}
                variants={variants}
                initial="enter"
                animate="center"
                exit="exit"
              >
                <Quote className="mb-6 h-10 w-10 text-[#047857]/30" />
                <p className="mb-8 text-lg leading-relaxed text-zinc-700 md:text-xl">{item.description}</p>
                <div className="flex items-center justify-between border-t border-zinc-100 pt-6">
                  <div>
                    <motion.span
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="text-3xl font-bold text-[#047857]"
                    >
                      {item.step}
                    </motion.span>
                    <h3 className="mt-1 font-bold text-[#0a1a2e]">{item.title}</h3>
                  </div>
                  <div className="flex gap-2">
                    <motion.button
                      type="button"
                      onClick={prev}
                      whileHover={{ scale: 1.1, backgroundColor: "#047857", color: "#fff" }}
                      whileTap={{ scale: 0.95 }}
                      className="rounded-full border border-zinc-200 p-2.5"
                      aria-label="Anterior"
                    >
                      <ChevronLeft className="h-5 w-5" />
                    </motion.button>
                    <motion.button
                      type="button"
                      onClick={next}
                      whileHover={{ scale: 1.1, backgroundColor: "#047857", color: "#fff" }}
                      whileTap={{ scale: 0.95 }}
                      className="rounded-full border border-zinc-200 p-2.5"
                      aria-label="Próximo"
                    >
                      <ChevronRight className="h-5 w-5" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
          <div className="mt-6 flex justify-center gap-2">
            {REASONS.map((_, i) => (
              <button
                key={i}
                type="button"
                onClick={() => go(i)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  i === index ? "w-8 bg-[#047857]" : "w-2 bg-zinc-300 hover:bg-[#047857]/40"
                }`}
                aria-label={`Razão ${i + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
