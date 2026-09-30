"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Menu, X } from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { useAuth } from "@/components/providers/auth-provider";
import { cn } from "@/lib/utils/cn";

const NAV = [
  { href: "/#funcionalidades", label: "Funcionalidades" },
  { href: "/#sectores", label: "Parceiros" },
  { href: "/planos", label: "Planos", routeMatch: "/planos" },
] as const;

function NavLink({
  href,
  label,
  active,
  onClick,
  className,
}: {
  href: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        "group landing-nav-link relative block py-2 text-[13px] font-semibold tracking-wide transition-colors sm:text-sm",
        active ? "text-[#047857]" : "text-zinc-600 hover:text-[#0a1a2e]",
        className,
      )}
      aria-current={active ? "page" : undefined}
    >
      {label}
      <span
        className={cn(
          "absolute bottom-0 left-0 h-0.5 rounded-full bg-gradient-to-r from-[#047857] to-[#c6a43f] transition-all duration-300",
          active ? "w-full opacity-100" : "w-0 opacity-0 group-hover:w-full group-hover:opacity-100",
        )}
        aria-hidden
      />
    </Link>
  );
}

export function MarketingHeader() {
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const closeMobile = useCallback(() => setMobileOpen(false), []);

  return (
    <>
      <header
        className={cn(
          "landing-header sticky top-0 z-50 transition-[box-shadow,background] duration-300",
          scrolled
            ? "landing-header-scrolled border-b border-zinc-200/90 bg-white/95 shadow-[0_8px_30px_-12px_rgba(10,26,46,0.12)] backdrop-blur-xl"
            : "border-b border-zinc-200/60 bg-white/80 backdrop-blur-lg",
        )}
      >
        <div className="landing-header-accent" aria-hidden />
        <div
          className={cn(
            "mx-auto flex w-full max-w-7xl items-center justify-between gap-3 px-4 sm:px-6",
            scrolled ? "py-2.5" : "py-3.5",
          )}
        >
          <BrandLogo variant="full" size="md" theme="light" href="/" priority />

          <nav className="hidden items-center md:flex lg:gap-1" aria-label="Navegação principal">
            {NAV.map((item) => (
              <div key={item.href} className="px-3 lg:px-4">
                <NavLink
                  href={item.href}
                  label={item.label}
                  active={"routeMatch" in item && pathname.startsWith(item.routeMatch)}
                />
              </div>
            ))}
          </nav>

          <div className="hidden items-center gap-2.5 md:flex">
            {!isLoading && isAuthenticated ? (
              <>
                <Link
                  href="/conta/assinatura"
                  className="rounded-full px-4 py-2 text-sm font-medium text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-900"
                >
                  Assinatura
                </Link>
                <Link href="/dashboard" className="landing-header-cta-primary">
                  Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-full border border-zinc-200 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-700 transition hover:border-zinc-300 hover:bg-zinc-50"
                >
                  Entrar
                </Link>
                <Link href="/signup" className="landing-header-cta-primary">
                  Começar grátis
                </Link>
              </>
            )}
          </div>

          <button
            type="button"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-zinc-200 bg-white text-zinc-800 shadow-sm transition hover:bg-zinc-50 md:hidden"
            aria-expanded={mobileOpen}
            aria-controls="landing-mobile-nav"
            aria-label={mobileOpen ? "Fechar menu" : "Abrir menu"}
            onClick={() => setMobileOpen((o) => !o)}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      <div
        id="landing-mobile-nav"
        className={cn(
          "fixed inset-0 z-40 md:hidden",
          mobileOpen ? "pointer-events-auto" : "pointer-events-none",
        )}
        aria-hidden={!mobileOpen}
      >
        <button
          type="button"
          className={cn(
            "absolute inset-0 bg-[#0a1a2e]/45 backdrop-blur-sm transition-opacity duration-300",
            mobileOpen ? "opacity-100" : "opacity-0",
          )}
          aria-label="Fechar menu"
          onClick={closeMobile}
        />
        <div
          className={cn(
            "landing-mobile-panel absolute left-0 right-0 top-16 border-b border-zinc-200 bg-white px-4 pb-6 pt-3 shadow-xl transition-all duration-300 ease-out",
            mobileOpen ? "translate-y-0 opacity-100" : "-translate-y-3 opacity-0",
          )}
        >
          <nav className="flex flex-col gap-0.5" aria-label="Navegação móvel">
            {NAV.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                label={item.label}
                active={"routeMatch" in item && pathname.startsWith(item.routeMatch)}
                onClick={closeMobile}
                className="rounded-xl px-3 py-3.5 hover:bg-emerald-50/60"
              />
            ))}
          </nav>
          <div className="mt-4 flex flex-col gap-2 border-t border-zinc-100 pt-4">
            {!isLoading && isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="landing-header-cta-primary text-center"
                  onClick={closeMobile}
                >
                  Dashboard
                </Link>
                <Link
                  href="/conta/assinatura"
                  className="rounded-full border border-zinc-200 py-3 text-center text-sm font-semibold text-zinc-700"
                  onClick={closeMobile}
                >
                  Minha assinatura
                </Link>
              </>
            ) : (
              <>
                <Link href="/signup" className="landing-header-cta-primary text-center" onClick={closeMobile}>
                  Começar grátis
                </Link>
                <Link
                  href="/login"
                  className="rounded-full border border-zinc-200 py-3 text-center text-sm font-semibold text-zinc-700"
                  onClick={closeMobile}
                >
                  Entrar
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
