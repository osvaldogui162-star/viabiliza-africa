"use client";

import { Suspense } from "react";

import { AuthShell } from "@/features/auth/components/auth-shell";
import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";
import { useI18n } from "@/components/providers/locale-provider";

function ResetPasswordFormFallback() {
  return <div className="h-48 animate-pulse rounded-xl bg-zinc-100" />;
}

export default function ResetPasswordPage() {
  const { locale } = useI18n();

  return (
    <AuthShell title={locale === "en" ? "New password" : "Nova palavra-passe"}>
      <Suspense fallback={<ResetPasswordFormFallback />}>
        <ResetPasswordForm />
      </Suspense>
    </AuthShell>
  );
}
