"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo } from "react";
import {
  CreditCard,
  Briefcase,
  FolderKanban,
  Landmark,
  LayoutDashboard,
  Megaphone,
  ScrollText,
  Settings,
  Users,
} from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { AppHeaderActions } from "@/components/layout/app-header-actions";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { FloatingProjectChat } from "@/features/collaboration/components/floating-project-chat";
import { AccountWelcomeCelebration } from "@/features/onboarding/components/account-welcome-celebration";
import { ProductTour } from "@/features/onboarding/components/product-tour";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { BankPortalShell } from "@/features/financier/components/bank-portal-shell";
import { PageLoader } from "@/components/ui/spinner";
import { cn } from "@/lib/utils/cn";

export default function ProtectedLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const { t } = useI18n();
  const pathname = usePathname();
  const router = useRouter();

  const navItems = useMemo(() => {
    if (user?.role === "bank") {
      return [{ href: "/financiador", label: t("nav.financier"), icon: Landmark }];
    }
    const items = [
      { href: "/dashboard", label: t("nav.dashboard"), icon: LayoutDashboard },
      { href: "/projects", label: t("nav.projects"), icon: FolderKanban },
    ];
    if (user?.role === "financial") {
      items.push({ href: "/escritorio", label: t("nav.myOffice"), icon: Briefcase });
    }
    if (user?.role === "admin" || user?.role === "financial") {
      items.push({ href: "/financiador", label: t("nav.financier"), icon: Landmark });
    }
    items.push({ href: "/conta/assinatura", label: t("nav.subscription"), icon: CreditCard });
    return items;
  }, [t, user?.role]);

  const adminItems = useMemo(
    () => [
      { href: "/admin", label: t("nav.adminConsole"), icon: Settings },
      { href: "/admin/promocoes", label: t("nav.promotions"), icon: Megaphone },
      { href: "/admin/utilizadores", label: t("nav.users"), icon: Users },
      { href: "/admin/escritorios", label: t("nav.offices"), icon: Briefcase },
      { href: "/admin/access-logs", label: t("nav.accessLogs"), icon: ScrollText },
      { href: "/admin/instituicoes", label: t("nav.bankInstitutions"), icon: Landmark },
    ],
    [t],
  );

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const search = typeof window !== "undefined" ? window.location.search : "";
      const returnTo = `${pathname}${search}`;
      router.replace(`/login?redirect=${encodeURIComponent(returnTo)}`);
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  useEffect(() => {
    if (!isLoading && user?.role === "bank" && pathname === "/dashboard") {
      router.replace("/financiador");
    }
  }, [isLoading, user?.role, pathname, router]);

  if (isLoading || !user) {
    return (
      <main className="min-h-screen bg-[var(--background)]">
        <PageLoader message={t("common.loadingSession")} layout="fullscreen" />
      </main>
    );
  }

  const isAdmin = user.role === "admin";
  const isBankPortal = user.role === "bank";

  if (isBankPortal) {
    return (
      <BankPortalShell user={user} onLogout={() => void logout()}>
        {children}
        <AccountWelcomeCelebration />
      </BankPortalShell>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <AppSidebar user={user} navItems={navItems} adminItems={adminItems} isAdmin={isAdmin} />

      <div className="relative flex min-h-screen flex-col transition-[padding] duration-300 ease-out lg:pl-[var(--sidebar-width,220px)]">
        <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--card)]/95 backdrop-blur-sm">
          <div className="flex h-14 items-center justify-between gap-3 px-4 lg:px-5">
            <BrandLogo variant="mark" size="sm" theme="light" href="/dashboard" className="lg:hidden" />
            <div className="hidden flex-1 lg:block" />
            <AppHeaderActions user={user} onLogout={logout} />
          </div>

          <nav className="flex gap-1 overflow-x-auto border-t border-[var(--border)] px-3 py-1.5 lg:hidden">
            {[...navItems, ...(isAdmin ? adminItems : [])].map((item) => (
              <MobileNavLink key={item.href} item={item} pathname={pathname} />
            ))}
          </nav>
        </header>

        <main className="relative flex-1 px-4 py-4 lg:px-5 lg:py-5">{children}</main>
        <AccountWelcomeCelebration />
        <ProductTour />
        {pathname !== "/projects" ? <FloatingProjectChat /> : null}
      </div>
    </div>
  );
}

function MobileNavLink({
  item,
  pathname,
}: {
  item: { href: string; label: string; icon: React.ComponentType<{ className?: string }> };
  pathname: string;
}) {
  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      className={cn(
        "inline-flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-all duration-200",
        active ? "va-nav-pill-active" : "bg-slate-100 text-[var(--muted)] hover:bg-slate-200/70",
      )}
    >
      <Icon className="h-3.5 w-3.5" />
      {item.label}
    </Link>
  );
}
