"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, Eye, EyeOff, LockKeyhole, Mail, Radio } from "lucide-react";
import { toast } from "sonner";

import {
  AuthField,
  AuthFormFooter,
  AuthSubmitButton,
} from "@/features/auth/components/auth-form-primitives";
import { AuthSocialSection } from "@/features/auth/components/google-auth-button";
import { useApprovalStatusPoll } from "@/features/auth/hooks/use-approval-status-poll";
import { ApiError } from "@/lib/api/http-client";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";

type LoginFormValues = { email: string; password: string };

export function LoginForm() {
  const { login } = useAuth();
  const { t, locale } = useI18n();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") ?? undefined;
  const emailParam = searchParams.get("email") ?? "";
  const approvedParam = searchParams.get("approved") === "1";
  const [approvedLive, setApprovedLive] = useState(approvedParam);
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useApprovalStatusPoll(emailParam, {
    enabled: !!emailParam && !approvedLive,
    redirectOnApprove: false,
    onApproved: () => setApprovedLive(true),
  });

  const loginSchema = useMemo(
    () =>
      z.object({
        email: z.email(t("auth.invalidEmail")),
        password: z.string().min(1, t("auth.passwordRequired")),
      }),
    [t],
  );

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: emailParam, password: "" },
  });

  useEffect(() => {
    if (emailParam) form.setValue("email", emailParam);
  }, [emailParam, form]);

  useEffect(() => {
    if (approvedParam) setApprovedLive(true);
  }, [approvedParam]);

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await login(values.email, values.password, redirectTo);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : t("auth.loginFailed");
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  });

  const signupHref = redirectTo
    ? `/signup?redirect=${encodeURIComponent(redirectTo)}`
    : "/signup";

  return (
    <div className="space-y-4">
      {approvedLive ? (
        <div className="flex items-start gap-2.5 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-3 text-sm text-emerald-900">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
          <p>{t("auth.approvedBanner")}</p>
        </div>
      ) : emailParam ? (
        <p className="flex items-center gap-2 text-xs text-zinc-500">
          <Radio className="h-3.5 w-3.5 animate-pulse text-teal-600" />
          {t("auth.pendingPolling")}
        </p>
      ) : null}

      <AuthSocialSection redirectTo={redirectTo} />

      <form onSubmit={onSubmit} className="space-y-4">
      <AuthField
        label={t("common.email")}
        type="email"
        autoComplete="email"
        placeholder={locale === "en" ? "Enter your email" : "Insira o seu email"}
        icon={<Mail className="h-5 w-5" strokeWidth={1.75} />}
        error={form.formState.errors.email?.message}
        {...form.register("email")}
      />

      <AuthField
        label={t("common.password")}
        type={showPassword ? "text" : "password"}
        autoComplete="current-password"
        placeholder={locale === "en" ? "Enter your password" : "Insira a sua senha"}
        icon={<LockKeyhole className="h-5 w-5" strokeWidth={1.75} />}
        error={form.formState.errors.password?.message}
        rightElement={
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="text-zinc-400 transition hover:text-zinc-600"
            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        }
        {...form.register("password")}
      />

      <p className="text-right text-base sm:text-[1.05rem]">
        <a href="/recover-password" className="font-medium text-sky-600 hover:underline">
          {t("auth.forgotPassword")}
        </a>
      </p>

      <AuthSubmitButton loading={submitting}>{t("auth.loginButton")}</AuthSubmitButton>

      <AuthFormFooter
        prompt={locale === "en" ? "Don't have an account?" : "Não tem uma conta?"}
        linkHref={signupHref}
        linkLabel={locale === "en" ? "Sign up" : "Cadastrar"}
      />
      </form>
    </div>
  );
}
