"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";

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

export function LandingBanksMarquee() {
  const reduce = useReducedMotion();
  const loop = [...BANK_LOGOS, ...BANK_LOGOS];

  return (
    <section id="sectores" className="overflow-hidden border-y border-white/10 bg-[#0a1a2e] py-14 text-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <p className="landing-eyebrow-light mb-2 text-emerald-300/90">Parceiros financeiros</p>
          <h2 className="landing-heading-lg text-white">Ecossistema bancário angolano</h2>
        </motion.div>
      </div>
      <div className="landing-marquee-mask relative mt-10 overflow-hidden">
        {reduce ? (
          <div className="flex flex-wrap justify-center gap-4 px-4">
            {BANK_LOGOS.map((bank) => (
              <div
                key={bank.alt}
                className="flex h-16 w-36 items-center justify-center rounded-xl bg-white/95 px-4 py-3 shadow-md"
              >
                <Image src={bank.src} alt={bank.alt} width={120} height={48} className="max-h-10 w-auto object-contain" />
              </div>
            ))}
          </div>
        ) : (
          <motion.div
            className="flex w-max gap-10 px-4"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ x: { type: "tween", repeat: Infinity, duration: 36, ease: "linear" } }}
          >
            {loop.map((bank, i) => (
              <motion.div
                key={`${bank.alt}-${i}`}
                whileHover={{ scale: 1.08, y: -4 }}
                className="flex h-16 w-36 shrink-0 items-center justify-center rounded-xl bg-white/95 px-4 py-3 shadow-md"
              >
                <Image src={bank.src} alt={bank.alt} width={120} height={48} className="max-h-10 w-auto object-contain" />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </section>
  );
}
