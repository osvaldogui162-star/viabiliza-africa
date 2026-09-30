import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";

import { LandingPage } from "@/features/marketing/components/landing-page";

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
  title: "ViabilizA+ África | Estudos de viabilidade e investimento",
  description:
    "Plataforma SaaS angolana: modelação financeira, relatórios BFA/BDA, rastreabilidade SHA-256 e portal para financiadores.",
};

export default function HomePage() {
  return (
    <div className={`${inter.variable} ${poppins.variable} pricing-font-scope min-h-screen`}>
      <LandingPage />
    </div>
  );
}
