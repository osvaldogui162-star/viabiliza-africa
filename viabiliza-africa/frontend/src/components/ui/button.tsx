import { forwardRef, type ButtonHTMLAttributes, type MouseEvent } from "react";
import { Loader2 } from "lucide-react";

import { spawnRipple } from "@/lib/utils/ripple";
import { cn } from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  ripple?: boolean;
}

const variants: Record<ButtonVariant, string> = {
  primary: "va-btn-primary va-btn-interactive text-white",
  secondary: "va-btn-secondary va-btn-interactive",
  outline: "va-btn-secondary va-btn-interactive bg-white",
  ghost: "va-btn-interactive hover:bg-slate-100 text-[var(--foreground)]",
  danger: "va-btn-interactive bg-rose-600 text-white hover:brightness-110",
};

const sizes: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-sm rounded-lg",
  md: "px-4 py-2 text-sm rounded-lg",
  lg: "px-5 py-3 text-base rounded-xl",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      loading,
      disabled,
      ripple = true,
      type = "button",
      children,
      onClick,
      ...props
    },
    ref,
  ) => {
    function handleClick(e: MouseEvent<HTMLButtonElement>) {
      if (ripple && !disabled && !loading) spawnRipple(e, variant === "danger" ? "va-ripple va-ripple-light" : "va-ripple");
      onClick?.(e);
    }

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || loading}
        onClick={handleClick}
        className={cn(
          "inline-flex items-center justify-center gap-2 font-semibold disabled:opacity-60",
          variants[variant],
          sizes[size],
          className,
        )}
        {...props}
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";
