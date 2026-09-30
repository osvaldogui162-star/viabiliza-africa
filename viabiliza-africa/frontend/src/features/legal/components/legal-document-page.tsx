"use client";

import Link from "next/link";
import { ArrowLeft, FileText, Shield } from "lucide-react";

import { AuthLocaleSelector } from "@/features/auth/components/auth-locale-selector";
import { AuthLogo } from "@/features/auth/components/auth-form-primitives";
import { useI18n } from "@/components/providers/locale-provider";
import type { LegalDocument } from "@/features/legal/legal-content";

export function LegalDocumentPage({
  document,
  kind,
}: {
  document: LegalDocument;
  kind: "terms" | "privacy";
}) {
  const { locale, t } = useI18n();
  const Icon = kind === "terms" ? FileText : Shield;
  const siblingHref = kind === "terms" ? "/privacidade" : "/termos";
  const siblingLabel =
    kind === "terms"
      ? locale === "en"
        ? "Privacy Policy"
        : "Política de Privacidade"
      : locale === "en"
        ? "Terms of Use"
        : "Termos de Utilização";

  return (
    <main className="min-h-dvh bg-gradient-to-b from-teal-50/40 via-white to-white">
      <div className="mx-auto max-w-3xl px-5 py-8 sm:px-8 sm:py-12">
        <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-4">
            <AuthLogo compact />
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-teal-700 hover:underline"
            >
              <ArrowLeft className="h-4 w-4" />
              {locale === "en" ? "Back to sign in" : "Voltar ao login"}
            </Link>
          </div>
          <AuthLocaleSelector />
        </header>

        <div className="rounded-2xl border border-teal-100/80 bg-white p-6 shadow-sm sm:p-8">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-teal-600 text-white shadow-md shadow-teal-900/15">
              <Icon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-teal-700">
                {t("legal.versionLabel", { version: document.version })}
              </p>
              <h1 className="mt-1 text-2xl font-bold tracking-tight text-zinc-900 sm:text-3xl">
                {document.title}
              </h1>
              <p className="mt-2 text-sm text-zinc-600">{document.subtitle}</p>
              <p className="mt-1 text-xs text-zinc-500">
                {t("legal.lastUpdated", { date: document.lastUpdated })}
              </p>
            </div>
          </div>

          <div className="prose prose-zinc mt-8 max-w-none prose-headings:text-zinc-900 prose-p:text-zinc-700 prose-p:leading-relaxed">
            {document.sections.map((section) => (
              <section key={section.title} className="mb-8 last:mb-0">
                <h2 className="text-base font-bold text-zinc-900">{section.title}</h2>
                {section.paragraphs.map((paragraph) => (
                  <p key={paragraph.slice(0, 40)} className="mt-2 text-sm leading-relaxed text-zinc-700">
                    {paragraph}
                  </p>
                ))}
              </section>
            ))}
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-zinc-500">
          <Link href={siblingHref} className="font-semibold text-teal-700 hover:underline">
            {siblingLabel}
          </Link>
          {" · "}
          <a href="mailto:comercial@viabiliza.africa" className="hover:underline">
            comercial@viabiliza.africa
          </a>
        </p>
      </div>
    </main>
  );
}
