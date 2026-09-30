"use client";

import { useI18n } from "@/components/providers/locale-provider";
import { LegalDocumentPage } from "@/features/legal/components/legal-document-page";
import { TERMS_EN, TERMS_PT } from "@/features/legal/legal-content";

export default function TermosPage() {
  const { locale } = useI18n();
  const document = locale === "en" ? TERMS_EN : TERMS_PT;
  return <LegalDocumentPage document={document} kind="terms" />;
}
