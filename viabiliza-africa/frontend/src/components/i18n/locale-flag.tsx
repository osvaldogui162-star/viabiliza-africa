import { cn } from "@/lib/utils/cn";

import type { LocaleOption } from "./locale-config";

type LocaleFlagProps = {
  flag: LocaleOption["flag"];
  className?: string;
  title?: string;
};

/** Bandeiras circulares compactas para PT (Portugal) e EN (Reino Unido) */
export function LocaleFlag({ flag, className, title }: LocaleFlagProps) {
  return (
    <span
      className={cn(
        "inline-flex h-5 w-5 shrink-0 overflow-hidden rounded-full ring-1 ring-black/10 sm:h-[1.35rem] sm:w-[1.35rem]",
        className,
      )}
      aria-hidden={title ? undefined : true}
      title={title}
    >
      {flag === "pt" ? <PortugalFlag /> : <UkFlag />}
    </span>
  );
}

function PortugalFlag() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full" role="img" aria-label="Portugal">
      <rect width="13" height="32" fill="#006600" />
      <rect x="13" width="19" height="32" fill="#FF0000" />
      <circle cx="13" cy="16" r="6.2" fill="#FFD700" stroke="#FFFFFF" strokeWidth="0.6" />
      <circle cx="13" cy="16" r="4.2" fill="#FF0000" stroke="#FFFFFF" strokeWidth="0.5" />
      <rect x="11.2" y="14.8" width="3.6" height="2.4" rx="0.3" fill="#FFFFFF" />
      <rect x="12" y="13.6" width="2" height="4.8" rx="0.3" fill="#FFFFFF" />
    </svg>
  );
}

function UkFlag() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full" role="img" aria-label="United Kingdom">
      <rect width="32" height="32" fill="#012169" />
      <path d="M0 0 L32 32 M32 0 L0 32" stroke="#FFFFFF" strokeWidth="6" />
      <path d="M0 0 L32 32 M32 0 L0 32" stroke="#C8102E" strokeWidth="3" />
      <path d="M16 0 V32 M0 16 H32" stroke="#FFFFFF" strokeWidth="10" />
      <path d="M16 0 V32 M0 16 H32" stroke="#C8102E" strokeWidth="6" />
    </svg>
  );
}
