"use client";

import { useMemo, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, KeyRound, LockKeyhole, Mail, UserRound } from "lucide-react";
import { toast } from "sonner";

import {
  AuthField,
  AuthFormFooter,
  AuthSubmitButton,
} from "@/features/auth/components/auth-form-primitives";
import { AuthSocialSection } from "@/features/auth/components/google-auth-button";
import { AuthTermsCheckbox, useRegistrationConfig } from "@/features/auth/components/auth-terms-checkbox";
import { ApiError } from "@/lib/api/http-client";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";

type SignupFormValues = {
  email: string;
  full_name: string;
  password: string;
  confirm_password: string;
};

type OtpFormValues = { code: string };

export function SignupForm() {
  const { requestSignupOtp, verifySignupOtp, resendSignupOtp } = useAuth();
  const { t, locale } = useI18n();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") ?? undefined;

  const [step, setStep] = useState<"details" | "otp">("details");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const regConfig = useRegistrationConfig();

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = window.setTimeout(() => setResendCooldown((s) => s - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [resendCooldown]);

  const signupSchema = useMemo(
    () =>
      z
        .object({
          email: z.email(t("auth.invalidEmail")),
          full_name: z.string().min(2, t("auth.signupPasswordHint")),
          password: z.string().min(8, t("auth.signupPasswordHint")),
          confirm_password: z.string().min(8, t("auth.signupPasswordHint")),
        })
        .refine((data) => data.password === data.confirm_password, {
          message: t("auth.passwordsMismatch"),
          path: ["confirm_password"],
        }),
    [t],
  );

  const otpSchema = useMemo(
    () =>
      z.object({
        code: z
          .string()
          .length(6, t("auth.otpRequired"))
          .regex(/^\d{6}$/, t("auth.otpRequired")),
      }),
    [t],
  );

  const detailsForm = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { email: "", full_name: "", password: "", confirm_password: "" },
  });

  const otpForm = useForm<OtpFormValues>({
    resolver: zodResolver(otpSchema),
    defaultValues: { code: "" },
  });

  const onRequestOtp = detailsForm.handleSubmit(async (values) => {
    if (!termsAccepted) {
      toast.error(t("auth.termsRequired"));
      return;
    }
    setSubmitting(true);
    try {
      const result = await requestSignupOtp({
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        terms_accepted: true,
        terms_version: regConfig?.terms_version,
      });
      setEmail(values.email.trim().toLowerCase());
      setStep("otp");
      setResendCooldown(60);
      toast.success(t("auth.signupOtpSent"));
      if (result.dev_otp) {
        toast.message(t("auth.signupDevOtp", { code: result.dev_otp }));
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  });

  const onVerifyOtp = otpForm.handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await verifySignupOtp(email, values.code, redirectTo, {
        terms_accepted: true,
        terms_version: regConfig?.terms_version,
      });
      toast.success(t("auth.signupSuccess"));
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  });

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    try {
      const result = await resendSignupOtp(email);
      setResendCooldown(60);
      toast.success(result.message);
      if (result.dev_otp) {
        toast.message(t("auth.signupDevOtp", { code: result.dev_otp }));
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    }
  };

  const loginHref = redirectTo
    ? `/login?redirect=${encodeURIComponent(redirectTo)}`
    : "/login";

  if (step === "otp") {
    return (
      <form onSubmit={onVerifyOtp} className="space-y-4">
        <p className="text-base leading-relaxed text-zinc-600 sm:text-[1.05rem]">
          {t("auth.signupVerifySubtitle", { email })}
        </p>

        <AuthField
          label="OTP"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          placeholder="000000"
          icon={<KeyRound className="h-5 w-5" strokeWidth={1.75} />}
          inputClassName="text-center text-lg tracking-[0.35em] font-semibold"
          error={otpForm.formState.errors.code?.message}
          {...otpForm.register("code")}
        />

        <AuthSubmitButton loading={submitting}>{t("auth.signupVerifyButton")}</AuthSubmitButton>

        <p className="text-center text-base text-zinc-500 sm:text-[1.05rem]">
          <button
            type="button"
            disabled={resendCooldown > 0}
            onClick={() => void handleResend()}
            className="font-semibold text-sky-600 hover:underline disabled:opacity-50"
          >
            {resendCooldown > 0
              ? t("auth.signupResendWait", { seconds: resendCooldown })
              : t("auth.signupResend")}
          </button>
        </p>

        <p className="text-center text-base text-zinc-500 sm:text-[1.05rem]">
          <button
            type="button"
            onClick={() => setStep("details")}
            className="font-medium text-zinc-600 hover:underline"
          >
            ← {t("common.cancel")}
          </button>
        </p>
      </form>
    );
  }

  return (
    <div className="space-y-4">
      <AuthTermsCheckbox checked={termsAccepted} onChange={setTermsAccepted} />

      <AuthSocialSection
        redirectTo={redirectTo}
        requireTerms
        termsAccepted={termsAccepted}
        termsVersion={regConfig?.terms_version}
      />

      <form onSubmit={onRequestOtp} className="space-y-4">
      <AuthField
        label={locale === "en" ? "Name" : "Nome"}
        type="text"
        autoComplete="name"
        placeholder={locale === "en" ? "Enter your name" : "Insira seu nome"}
        icon={<UserRound className="h-5 w-5" strokeWidth={1.75} />}
        error={detailsForm.formState.errors.full_name?.message}
        {...detailsForm.register("full_name")}
      />

      <AuthField
        label={t("common.email")}
        type="email"
        autoComplete="email"
        placeholder={locale === "en" ? "Enter your email" : "seu@email.com"}
        icon={<Mail className="h-5 w-5" strokeWidth={1.75} />}
        error={detailsForm.formState.errors.email?.message}
        {...detailsForm.register("email")}
      />

      <AuthField
        label={locale === "en" ? "Password" : "Senha"}
        type={showPassword ? "text" : "password"}
        autoComplete="new-password"
        placeholder={locale === "en" ? "Enter your password" : "Insira sua senha"}
        icon={<LockKeyhole className="h-5 w-5" strokeWidth={1.75} />}
        error={detailsForm.formState.errors.password?.message}
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
        {...detailsForm.register("password")}
      />

      <AuthField
        label={locale === "en" ? "Confirm password" : "Confirmar Senha"}
        type={showConfirm ? "text" : "password"}
        autoComplete="new-password"
        placeholder={locale === "en" ? "Repeat your password" : "Confirme sua senha"}
        icon={<LockKeyhole className="h-5 w-5" strokeWidth={1.75} />}
        error={detailsForm.formState.errors.confirm_password?.message}
        rightElement={
          <button
            type="button"
            onClick={() => setShowConfirm((v) => !v)}
            className="text-zinc-400 transition hover:text-zinc-600"
            aria-label={showConfirm ? "Ocultar senha" : "Mostrar senha"}
          >
            {showConfirm ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        }
        {...detailsForm.register("confirm_password")}
      />

      <AuthSubmitButton loading={submitting}>
        {locale === "en" ? "Create account" : "Criar Conta"}
      </AuthSubmitButton>

      <AuthFormFooter
        prompt={locale === "en" ? "Already have an account?" : "Já tem uma conta?"}
        linkHref={loginHref}
        linkLabel={locale === "en" ? "Sign in" : "Entrar"}
      />
      </form>
    </div>
  );
}
