"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";

import { BRAND_LOGO_PATH } from "@/lib/constants/brand-assets";

export function LandingCtaSection() {
  const reduce = useReducedMotion();

  return (
    <section className="landing-section-padding mx-auto max-w-7xl px-4 sm:px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 40 }}
        whileInView={{ opacity: 1, scale: 1, y: 0 }}
        viewport={{ once: true, amount: 0.35 }}
        transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#064e3b] via-[#047857] to-[#0a1a2e] px-8 py-14 text-center text-white shadow-2xl sm:px-16"
      >
        {!reduce && (
          <>
            <motion.div
              className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-emerald-400/20 blur-3xl"
              animate={{ x: [0, 30, 0], y: [0, -20, 0] }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div
              className="pointer-events-none absolute -bottom-16 -right-16 h-56 w-56 rounded-full bg-[#c6a43f]/20 blur-3xl"
              animate={{ x: [0, -25, 0], y: [0, 15, 0] }}
              transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
            />
          </>
        )}
        <div className="relative mx-auto flex max-w-lg flex-col items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
          >
            <Image src={BRAND_LOGO_PATH} alt="" width={180} height={70} className="mb-6 h-14 w-auto opacity-95" />
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.15 }}
            className="landing-heading-xl text-white"
          >
            Pronto para o seu próximo projecto?
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.25 }}
            className="mt-4 text-base text-emerald-50/90"
          >
            Crie a conta, escolha o plano e comece a modelar investimentos com credibilidade.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.35 }}
            className="mt-8 flex flex-wrap justify-center gap-3"
          >
            <motion.div whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.97 }}>
              <Link
                href="/signup"
                className="landing-cta-shine inline-block rounded-full bg-white px-8 py-3.5 text-sm font-bold text-[#064e3b] shadow-lg transition hover:bg-emerald-50"
              >
                Registar gratuitamente
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.03, y: -2 }} whileTap={{ scale: 0.98 }}>
              <Link
                href="/planos"
                className="inline-block rounded-full border border-white/40 px-8 py-3.5 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Comparar planos
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
