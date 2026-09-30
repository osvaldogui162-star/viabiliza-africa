"use client";

import type { ReactNode } from "react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { AuthLocaleSelector } from "@/features/auth/components/auth-locale-selector";
import { CurrencySelector } from "@/components/layout/currency-selector";
import { AuthSlideshow, AuthSlideshowMobile } from "@/features/auth/components/auth-slideshow";

export function AuthShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <main className="grid min-h-dvh lg:h-dvh lg:max-h-dvh lg:grid-cols-2 lg:overflow-hidden">
      <div className="hidden lg:block lg:h-full lg:min-h-0 lg:overflow-hidden">
        <AuthSlideshow />
      </div>

      <section className="relative flex min-h-dvh flex-col overflow-y-auto overscroll-y-contain bg-white px-5 py-4 sm:px-7 sm:py-5 md:px-9 lg:h-full lg:max-h-dvh lg:px-12 lg:py-6">
        <header className="mb-5 flex shrink-0 flex-col gap-4 border-b border-zinc-100 pb-5 sm:mb-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex justify-center sm:justify-start">
            <BrandLogo
              variant="full"
              size="md"
              theme="light"
              href="/login"
              priority
              className="sm:hidden"
            />
            <BrandLogo
              variant="full"
              size="lg"
              theme="light"
              href="/login"
              priority
              className="hidden sm:inline-flex md:hidden"
            />
            <BrandLogo
              variant="full"
              size="xl"
              theme="light"
              href="/login"
              priority
              className="hidden md:inline-flex"
            />
          </div>
          <div className="flex items-center justify-center gap-2 sm:justify-end">
            <CurrencySelector />
            <AuthLocaleSelector />
          </div>
        </header>

        <div className="mx-auto flex w-full max-w-[440px] flex-1 flex-col justify-start sm:max-w-[460px] lg:justify-center">
          <AuthSlideshowMobile />

          <h1 className="shrink-0 font-[family-name:var(--font-auth-display)] text-[1.75rem] font-bold leading-tight text-[#0f172a] sm:text-[2rem] lg:text-[2.125rem]">
            {title}
          </h1>

          <div className="auth-form-area mt-4 min-h-0 shrink-0 pb-6 sm:mt-5 sm:pb-8">{children}</div>
        </div>
      </section>
    </main>
  );
}
