"use client";

import {
  BrandPageLoader,
  type BrandLoaderLayout,
  type BrandLoaderTheme,
} from "@/components/brand/brand-page-loader";
import { cn } from "@/lib/utils/cn";

/** Loader compacto (secções pequenas). */
export function Spinner({
  className,
  theme = "light",
  message,
}: {
  className?: string;
  theme?: BrandLoaderTheme;
  message?: string;
}) {
  return (
    <BrandPageLoader
      message={message}
      theme={theme}
      layout="compact"
      className={cn("w-full", className)}
    />
  );
}

export function PageLoader({
  message,
  theme = "light",
  layout = "section",
  className,
}: {
  message?: string;
  theme?: BrandLoaderTheme;
  layout?: BrandLoaderLayout;
  className?: string;
}) {
  return (
    <BrandPageLoader
      message={message}
      theme={theme}
      layout={layout}
      className={className}
      priority={layout === "fullscreen"}
    />
  );
}
