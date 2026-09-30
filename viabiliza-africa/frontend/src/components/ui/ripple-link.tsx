"use client";

import Link from "next/link";
import { useCallback, type ComponentProps, type ReactNode } from "react";

import { spawnRipple } from "@/lib/utils/ripple";
import { cn } from "@/lib/utils/cn";

type RippleLinkProps = ComponentProps<typeof Link> & {
  variant?: "primary" | "secondary" | "ghost";
  children: ReactNode;
};

const variants = {
  primary: "va-btn-primary va-btn-interactive",
  secondary: "va-btn-secondary va-btn-interactive",
  ghost: "va-btn-interactive rounded-lg px-3 py-2 text-sm font-medium text-[var(--muted)] hover:bg-slate-100 hover:text-[var(--foreground)]",
};

export function RippleLink({ variant = "primary", className, children, onClick, ...props }: RippleLinkProps) {
  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLAnchorElement>) => {
      spawnRipple(e);
      onClick?.(e);
    },
    [onClick],
  );

  return (
    <Link {...props} onClick={handleClick} className={cn(variants[variant], "inline-flex items-center justify-center gap-2", className)}>
      {children}
    </Link>
  );
}
