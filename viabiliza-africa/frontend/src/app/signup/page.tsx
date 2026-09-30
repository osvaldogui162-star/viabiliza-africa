"use client";

import { Suspense } from "react";
import { AuthShell } from "@/features/auth/components/auth-shell";
import { SignupForm } from "@/features/auth/components/signup-form";
import { useI18n } from "@/components/providers/locale-provider";

function SignupFormFallback() {
  return <div className="h-48 animate-pulse rounded-xl bg-zinc-100" />;
}

export default function SignupPage() {
  const { locale } = useI18n();

  return (
    <AuthShell title={locale === "en" ? "Sign up" : "Cadastrar"}>
      <Suspense fallback={<SignupFormFallback />}>
        <SignupForm />
      </Suspense>
    </AuthShell>
  );
}
