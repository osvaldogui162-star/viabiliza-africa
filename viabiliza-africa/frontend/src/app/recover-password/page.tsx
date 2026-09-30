"use client";

import { AuthShell } from "@/features/auth/components/auth-shell";
import { RecoverPasswordForm } from "@/features/auth/components/recover-password-form";
import { useI18n } from "@/components/providers/locale-provider";

export default function RecoverPasswordPage() {
  const { locale } = useI18n();

  return (
    <AuthShell title={locale === "en" ? "Recover password" : "Recuperar palavra-passe"}>
      <RecoverPasswordForm />
    </AuthShell>
  );
}
