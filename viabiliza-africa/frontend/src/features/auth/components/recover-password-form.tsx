"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, Mail } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

import {
  AuthField,
  AuthFormFooter,
  AuthSubmitButton,
} from "@/features/auth/components/auth-form-primitives";
import { ApiError } from "@/lib/api/http-client";
import { authApi } from "@/lib/api/auth-api";
import { useI18n } from "@/components/providers/locale-provider";

const schema = z.object({
  email: z.email("Email inválido"),
});

type FormValues = z.infer<typeof schema>;

export function RecoverPasswordForm() {
  const { locale, t } = useI18n();
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [sentEmail, setSentEmail] = useState("");

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await authApi.recoverPassword(values.email);
      setSentEmail(values.email);
      setSent(true);
      toast.success(t("auth.recoverEmailSent"));
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : locale === "en"
            ? "Recovery request failed"
            : "Erro ao solicitar recuperação";

      if (error instanceof ApiError && error.status === 400) {
        form.setError("email", { message });
      } else {
        toast.error(message);
      }
    } finally {
      setSubmitting(false);
    }
  });

  if (sent) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
          <CheckCircle2 className="h-8 w-8" />
        </div>
        <div className="space-y-2">
          <p className="text-lg font-bold text-zinc-900">{t("auth.recoverEmailSentTitle")}</p>
          <p className="text-base leading-relaxed text-zinc-600 sm:text-[1.05rem]">
            {t("auth.recoverEmailSentBody", { email: sentEmail })}
          </p>
        </div>
        <Link href="/login" className="inline-flex text-base font-semibold text-sky-600 hover:underline sm:text-[1.05rem]">
          {locale === "en" ? "Back to sign in" : "Voltar ao login"}
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <AuthField
        label={locale === "en" ? "Account email" : "Email da conta"}
        type="email"
        autoComplete="email"
        placeholder={locale === "en" ? "Enter your email" : "Insira o seu email"}
        icon={<Mail className="h-5 w-5" strokeWidth={1.75} />}
        error={form.formState.errors.email?.message}
        {...form.register("email")}
      />

      <AuthSubmitButton loading={submitting}>
        {locale === "en" ? "Send instructions" : "Enviar instruções"}
      </AuthSubmitButton>

      <AuthFormFooter
        prompt={locale === "en" ? "Remember your password?" : "Lembrou-se da palavra-passe?"}
        linkHref="/login"
        linkLabel={locale === "en" ? "Sign in" : "Entrar"}
      />
    </form>
  );
}
