"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import {
  AuthField,
  AuthFormFooter,
  AuthSubmitButton,
} from "@/features/auth/components/auth-form-primitives";
import { ApiError } from "@/lib/api/http-client";
import { authApi } from "@/lib/api/auth-api";
import { useI18n } from "@/components/providers/locale-provider";

export function ResetPasswordForm() {
  const { locale } = useI18n();
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const schema = z
    .object({
      new_password: z.string().min(8, locale === "en" ? "Minimum 8 characters" : "Mínimo de 8 caracteres"),
      confirm_password: z
        .string()
        .min(8, locale === "en" ? "Confirm your password" : "Confirme a palavra-passe"),
    })
    .refine((data) => data.new_password === data.confirm_password, {
      message: locale === "en" ? "Passwords do not match" : "As palavras-passe não coincidem",
      path: ["confirm_password"],
    });

  type FormValues = z.infer<typeof schema>;

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { new_password: "", confirm_password: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    if (!token) {
      toast.error(
        locale === "en"
          ? "Invalid or expired link. Request a new recovery email."
          : "Link inválido ou expirado. Solicite uma nova recuperação.",
      );
      return;
    }

    setSubmitting(true);
    try {
      await authApi.resetPassword(token, values.new_password);
      toast.success(
        locale === "en" ? "Password reset successfully" : "Palavra-passe redefinida com sucesso",
      );
      router.push("/login");
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.message
          : locale === "en"
            ? "Failed to reset password"
            : "Erro ao redefinir palavra-passe",
      );
    } finally {
      setSubmitting(false);
    }
  });

  if (!token) {
    return (
      <div className="space-y-5 text-center">
        <p className="text-base leading-relaxed text-zinc-600 sm:text-[1.05rem]">
          {locale === "en"
            ? "The recovery link is invalid or expired. Request a new recovery email."
            : "O link de recuperação é inválido ou expirou. Solicite um novo email de recuperação."}
        </p>
        <Link href="/recover-password" className="inline-flex text-base font-semibold text-sky-600 hover:underline sm:text-[1.05rem]">
          {locale === "en" ? "Request new recovery" : "Solicitar nova recuperação"}
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <AuthField
        label={locale === "en" ? "New password" : "Nova senha"}
        type={showPassword ? "text" : "password"}
        autoComplete="new-password"
        placeholder={locale === "en" ? "Minimum 8 characters" : "Mínimo 8 caracteres"}
        icon={<LockKeyhole className="h-5 w-5" strokeWidth={1.75} />}
        error={form.formState.errors.new_password?.message}
        rightElement={
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            className="text-zinc-400 transition hover:text-zinc-600"
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        }
        {...form.register("new_password")}
      />

      <AuthField
        label={locale === "en" ? "Confirm password" : "Confirmar Senha"}
        type={showConfirm ? "text" : "password"}
        autoComplete="new-password"
        placeholder={locale === "en" ? "Repeat your password" : "Repita a palavra-passe"}
        icon={<LockKeyhole className="h-5 w-5" strokeWidth={1.75} />}
        error={form.formState.errors.confirm_password?.message}
        rightElement={
          <button
            type="button"
            onClick={() => setShowConfirm((v) => !v)}
            className="text-zinc-400 transition hover:text-zinc-600"
          >
            {showConfirm ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        }
        {...form.register("confirm_password")}
      />

      <AuthSubmitButton loading={submitting}>
        {locale === "en" ? "Reset password" : "Redefinir palavra-passe"}
      </AuthSubmitButton>

      <AuthFormFooter
        linkHref="/login"
        linkLabel={locale === "en" ? "Back to sign in" : "Voltar ao login"}
      />
    </form>
  );
}
