"use client";

import { motion, useReducedMotion } from "framer-motion";

const ITEMS = [
  "BFA",
  "BDA",
  "Monte Carlo",
  "Sensibilidade",
  "ESG",
  "AppyPay",
  "SHA-256",
  "Portal financiador",
  "Angola",
  "África",
];

export function LandingTrustMarquee() {
  const reduce = useReducedMotion();
  const loop = [...ITEMS, ...ITEMS];

  if (reduce) {
    return (
      <div className="border-y border-white/10 bg-[#0a1a2e] py-3.5">
        <p className="text-center text-xs font-semibold tracking-[0.2em] text-white/60 uppercase">
          {ITEMS.join(" · ")}
        </p>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden border-y border-white/10 bg-[#0a1a2e] py-3.5">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-[#0a1a2e] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-[#0a1a2e] to-transparent" />
      <motion.div
        className="flex w-max gap-10 whitespace-nowrap"
        animate={{ x: ["0%", "-50%"] }}
        transition={{ x: { type: "tween", repeat: Infinity, duration: 32, ease: "linear" } }}
      >
        {loop.map((label, i) => (
          <motion.span
            key={`${label}-${i}`}
            animate={{ opacity: [0.45, 1, 0.45] }}
            transition={{ duration: 3, repeat: Infinity, delay: 0.12 * (i % ITEMS.length) }}
            className="inline-flex items-center gap-10 text-xs font-semibold tracking-[0.2em] text-white/55 uppercase"
          >
            <motion.span
              className="h-1.5 w-1.5 rounded-full bg-[#c6a43f]"
              animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.15 * (i % ITEMS.length) }}
            />
            {label}
          </motion.span>
        ))}
      </motion.div>
    </div>
  );
}
