import type { Metadata } from "next";
import { Suspense } from "react";
import { Inter, Poppins } from "next/font/google";

import { PricingPage } from "@/features/subscription/components/pricing-page";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Planos e Preços | ViabilizA+ África",
  description:
    "Starter, Business, Enterprise, Academia Institucional e Governo — facturação trimestral, semestral ou anual em AOA.",
};

export default function PlanosPage() {
  return (
    <div className={`${inter.variable} ${poppins.variable} pricing-font-scope min-h-screen`}>
      <Suspense fallback={<div className="flex min-h-screen items-center justify-center bg-white">A carregar planos…</div>}>
        <PricingPage />
      </Suspense>
    </div>
  );
}
