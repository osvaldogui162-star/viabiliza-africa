"use client";

import { useI18n } from "@/components/providers/locale-provider";
import { LegalDocumentPage } from "@/features/legal/components/legal-document-page";
import { PRIVACY_EN, PRIVACY_PT } from "@/features/legal/legal-content";

export default function PrivacidadePage() {
  const { locale } = useI18n();
  const document = locale === "en" ? PRIVACY_EN : PRIVACY_PT;
  return <LegalDocumentPage document={document} kind="privacy" />;
}
