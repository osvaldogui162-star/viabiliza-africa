"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { MarketingHeader } from "@/features/marketing/components/marketing-header";
import { BrandLogo } from "@/components/brand/brand-logo";

export function MarketingShell({ children }: { children: ReactNode }) {
  return (
    <div className="landing-page min-h-screen bg-[#f8faf9] font-[family-name:var(--font-inter)] text-zinc-900">
      <MarketingHeader />
      <main>{children}</main>
      <footer className="landing-footer border-t border-zinc-200 bg-white">
        <div className="landing-footer-accent" aria-hidden />
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
          <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-sm">
              <BrandLogo variant="full" size="sm" theme="light" href="/" />
              <p className="mt-4 text-sm leading-relaxed text-zinc-500">
                Estudos de viabilidade com rigor bancário, rastreabilidade SHA-256 e relatórios BFA/BDA
                para Angola e África.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-zinc-400">Produto</p>
                <ul className="mt-3 space-y-2 text-sm font-medium text-zinc-600">
                  <li>
                    <Link href="/#funcionalidades" className="transition hover:text-[#047857]">
                      Funcionalidades
                    </Link>
                  </li>
                  <li>
                    <Link href="/planos" className="transition hover:text-[#047857]">
                      Planos
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-zinc-400">Conta</p>
                <ul className="mt-3 space-y-2 text-sm font-medium text-zinc-600">
                  <li>
                    <Link href="/login" className="transition hover:text-[#047857]">
                      Entrar
                    </Link>
                  </li>
                  <li>
                    <Link href="/signup" className="transition hover:text-[#047857]">
                      Registar
                    </Link>
                  </li>
                </ul>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <p className="text-xs font-bold uppercase tracking-wider text-zinc-400">Contacto</p>
                <p className="mt-3 text-sm text-zinc-600">
                  <a href="mailto:comercial@viabiliza.africa" className="transition hover:text-[#047857]">
                    comercial@viabiliza.africa
                  </a>
                </p>
              </div>
            </div>
          </div>
          <p className="mt-10 border-t border-zinc-100 pt-6 text-center text-xs text-zinc-400">
            © {new Date().getFullYear()} ViabilizA+ África. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </div>
  );
}
