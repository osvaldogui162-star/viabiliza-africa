"use client";

import { Suspense } from "react";
import { AuthShell } from "@/features/auth/components/auth-shell";
import { LoginForm } from "@/features/auth/components/login-form";
import { useI18n } from "@/components/providers/locale-provider";

function LoginFormFallback() {
  return <div className="h-48 animate-pulse rounded-xl bg-zinc-100" />;
}

export default function LoginPage() {
  const { locale } = useI18n();

  return (
    <AuthShell title={locale === "en" ? "Sign in" : "Entrar"}>
      <Suspense fallback={<LoginFormFallback />}>
        <LoginForm />
      </Suspense>
    </AuthShell>
  );
}
