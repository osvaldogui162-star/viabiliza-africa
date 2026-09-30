"use client";

import type { InputHTMLAttributes, ReactNode } from "react";
import Link from "next/link";
import { Loader2 } from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { cn } from "@/lib/utils/cn";

export function AuthLogo({ className, compact }: { className?: string; compact?: boolean }) {
  return (
    <BrandLogo
      variant="full"
      size={compact ? "sm" : "md"}
      theme="light"
      className={className}
      priority
    />
  );
}

export function AuthField({
  label,
  error,
  icon,
  rightElement,
  inputClassName,
  ...props
}: {
  label: string;
  error?: string;
  icon?: ReactNode;
  rightElement?: ReactNode;
  inputClassName?: string;
} & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block">
      <span className="mb-2 block text-base font-semibold text-[#1e293b]">{label}</span>
      <div
        className={cn(
          "flex min-h-[3rem] items-center gap-3 rounded-xl border border-zinc-200 bg-white px-3.5 py-3 shadow-sm transition sm:min-h-[3.125rem] sm:px-4 sm:py-3.5",
          "focus-within:border-sky-400 focus-within:ring-2 focus-within:ring-sky-100",
        )}
      >
        {icon ? (
          <span className="shrink-0 text-zinc-400 [&>svg]:h-5 [&>svg]:w-5 sm:[&>svg]:h-[1.35rem] sm:[&>svg]:w-[1.35rem]">
            {icon}
          </span>
        ) : null}
        <input
          {...props}
          className={cn(
            "min-w-0 flex-1 bg-transparent text-base text-zinc-800 outline-none placeholder:text-zinc-400",
            inputClassName,
          )}
        />
        {rightElement ? (
          <span className="shrink-0 [&>button>svg]:h-5 [&>button>svg]:w-5 sm:[&>button>svg]:h-[1.35rem] sm:[&>button>svg]:w-[1.35rem]">
            {rightElement}
          </span>
        ) : null}
      </div>
      {error ? <p className="mt-2 text-sm text-red-500">{error}</p> : null}
    </label>
  );
}

export function AuthSubmitButton({
  children,
  loading,
  disabled,
}: {
  children: ReactNode;
  loading?: boolean;
  disabled?: boolean;
}) {
  return (
    <button type="submit" disabled={disabled || loading} className="auth-submit-btn">
      <span className="auth-submit-btn-bg" aria-hidden />
      <span className="auth-submit-btn-shine" aria-hidden />
      <span className="auth-submit-btn-label">
        {loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden /> : null}
        {children}
      </span>
    </button>
  );
}

export function AuthFormFooter({
  prompt,
  linkHref,
  linkLabel,
}: {
  prompt?: string;
  linkHref: string;
  linkLabel: string;
}) {
  return (
    <p className="pt-1 text-center text-base text-zinc-600 sm:text-[1.05rem]">
      {prompt ? <span>{prompt} </span> : null}
      <Link href={linkHref} className="font-semibold text-[#00777f] hover:text-[#ffa900] hover:underline">
        {linkLabel}
      </Link>
    </p>
  );
}
