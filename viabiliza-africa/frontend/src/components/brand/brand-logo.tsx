"use client";

import Image from "next/image";
import Link from "next/link";

import {
  BRAND_LOGO_LIGHT_PATH,
  BRAND_LOGO_NAVY_TEXT_PATH,
  BRAND_LOGO_ON_DARK_PATH,
  BRAND_LOGO_PATH,
  BRAND_LOGO_WHITE_PATH,
  BRAND_MARK_ORANGE_PATH,
  BRAND_MARK_TEAL_PATH,
  BRAND_MARK_WHITE_PATH,
} from "@/lib/constants/brand-assets";
import { cn } from "@/lib/utils/cn";

const FULL_HEIGHT_CLASS = {
  sm: "h-9",
  md: "h-11",
  lg: "h-[3.25rem]",
  xl: "h-[3.625rem]",
} as const;

const MARK_SIZE_CLASS = {
  sm: "h-9 w-9",
  md: "h-10 w-10",
  lg: "h-12 w-12",
  xl: "h-14 w-14",
} as const;

export type BrandLogoSurface =
  | "light"
  | "dark"
  | "onDark"
  | "navyText"
  | "markTeal"
  | "markWhite"
  | "markOrange";

type BrandLogoProps = {
  variant?: "full" | "mark";
  size?: keyof typeof FULL_HEIGHT_CLASS;
  /** @deprecated use `surface` */
  theme?: "light" | "dark";
  surface?: BrandLogoSurface;
  className?: string;
  href?: string;
  priority?: boolean;
};

function resolveSrc(variant: "full" | "mark", surface: BrandLogoSurface): string {
  if (variant === "mark") {
    if (surface === "markWhite" || surface === "onDark" || surface === "dark") return BRAND_MARK_WHITE_PATH;
    if (surface === "markOrange") return BRAND_MARK_ORANGE_PATH;
    return BRAND_MARK_TEAL_PATH;
  }
  switch (surface) {
    case "onDark":
      return BRAND_LOGO_ON_DARK_PATH;
    case "dark":
      return BRAND_LOGO_WHITE_PATH;
    case "navyText":
      return BRAND_LOGO_NAVY_TEXT_PATH;
    case "light":
      return BRAND_LOGO_LIGHT_PATH;
    default:
      return BRAND_LOGO_PATH;
  }
}

export function BrandLogo({
  variant = "full",
  size = "md",
  theme,
  surface,
  className,
  href,
  priority = false,
}: BrandLogoProps) {
  const resolvedSurface: BrandLogoSurface =
    surface ?? (theme === "dark" ? "onDark" : theme === "light" ? "light" : "light");
  const src = resolveSrc(variant, resolvedSurface);

  const inner = (
    <span
      className={cn(
        "brand-logo inline-flex shrink-0 items-center",
        variant === "mark" && cn("overflow-hidden rounded-xl", MARK_SIZE_CLASS[size]),
        className,
      )}
    >
      <Image
        src={src}
        alt="ViabilizA+ África"
        width={variant === "mark" ? 512 : 1024}
        height={variant === "mark" ? 512 : 393}
        unoptimized
        priority={priority}
        draggable={false}
        className={cn(
          "select-none object-contain",
          variant === "full"
            ? cn(
                "w-auto max-w-[min(100vw-2rem,20rem)] object-left object-contain",
                FULL_HEIGHT_CLASS[size],
              )
            : "h-full w-full object-center",
        )}
      />
    </span>
  );

  if (!href) return inner;

  return (
    <Link
      href={href}
      className="inline-flex rounded-md outline-offset-2 transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--brand-teal)]"
      aria-label="ViabilizA+ África"
    >
      {inner}
    </Link>
  );
}
