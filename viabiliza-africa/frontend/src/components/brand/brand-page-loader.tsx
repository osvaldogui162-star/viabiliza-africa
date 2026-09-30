"use client";

import { BrandLogo } from "@/components/brand/brand-logo";
import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";

export type BrandLoaderTheme = "light" | "dark";
export type BrandLoaderLayout = "fullscreen" | "section" | "compact" | "embedded";

export function BrandPageLoader({
  message,
  theme = "light",
  layout = "section",
  className,
  priority,
}: {
  message?: string;
  theme?: BrandLoaderTheme;
  layout?: BrandLoaderLayout;
  className?: string;
  priority?: boolean;
}) {
  const { t } = useI18n();
  const label = message ?? t("common.loading");
  const logoTheme = theme === "dark" ? "dark" : "light";

  const isFullscreen = layout === "fullscreen";

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      aria-label={label}
      className={cn(
        "relative flex flex-col items-center justify-center gap-5",
        isFullscreen && "fixed inset-0 z-[200] min-h-screen w-full",
        layout === "section" && "min-h-[min(420px,55vh)] w-full py-16",
        layout === "compact" && "py-10",
        layout === "embedded" && "py-6",
        theme === "dark"
          ? isFullscreen
            ? "bg-gradient-to-br from-[var(--brand-navy)] via-[#023048] to-[var(--brand-teal)] text-teal-50"
            : "text-teal-100"
          : isFullscreen
            ? "bg-[var(--background)] text-[var(--muted)]"
            : "text-zinc-500",
        className,
      )}
    >
      {isFullscreen && theme === "dark" ? (
        <>
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_0%,rgba(45,212,191,0.12),transparent)]"
          />
          <div
            aria-hidden
            className="brand-loader-glow pointer-events-none absolute left-1/2 top-1/3 h-64 w-64 -translate-x-1/2 rounded-full bg-teal-500/10 blur-3xl"
          />
        </>
      ) : null}

      <div className="relative flex flex-col items-center gap-4">
        <div className="relative">
          <div
            aria-hidden
            className={cn(
              "brand-loader-ring absolute inset-0 rounded-full",
              theme === "dark" ? "border-teal-400/25" : "border-teal-600/20",
            )}
          />
          <div className="brand-loader-logo relative rounded-2xl px-2 py-1">
            <BrandLogo variant="full" size="lg" theme={logoTheme} priority={priority ?? isFullscreen} />
          </div>
        </div>

        <div className="flex w-full max-w-[220px] flex-col items-center gap-2">
          <div
            className={cn(
              "h-1 w-full overflow-hidden rounded-full",
              theme === "dark" ? "bg-white/10" : "bg-zinc-200",
            )}
          >
            <div
              className={cn(
                "brand-loader-bar h-full w-1/3 rounded-full",
                theme === "dark" ? "bg-teal-400" : "bg-teal-600",
              )}
            />
          </div>
          <p
            className={cn(
              "text-center text-sm font-medium tracking-wide",
              theme === "dark" ? "text-teal-100/85" : "text-zinc-600",
            )}
          >
            {label}
          </p>
        </div>
      </div>
    </div>
  );
}
