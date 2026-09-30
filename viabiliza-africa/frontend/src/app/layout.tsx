import type { Metadata } from "next";
import { Fraunces, Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppProviders } from "@/components/providers/app-providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const authDisplay = Fraunces({
  variable: "--font-auth-display",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});

import { BRAND_LOGO_PATH } from "@/lib/constants/brand-assets";

export const metadata: Metadata = {
  title: "ViabilizA+ África",
  description: "Plataforma de estudos de viabilidade e análise de investimento",
  icons: {
    icon: BRAND_LOGO_PATH,
    apple: BRAND_LOGO_PATH,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt"
      className={`${geistSans.variable} ${geistMono.variable} ${authDisplay.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-zinc-50 text-zinc-900">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
