"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  CreditCard,
  FolderKanban,
  LayoutDashboard,
  ScrollText,
  Settings,
  Users,
  type LucideIcon,
} from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { Tooltip } from "@/components/ui/tooltip";
import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";
import type { User } from "@/lib/types/auth";

type NavItem = { href: string; label: string; icon: LucideIcon };

const STORAGE_KEY = "va-sidebar-collapsed";

export function AppSidebar({
  user,
  navItems,
  adminItems,
  isAdmin,
}: {
  user: User;
  navItems: NavItem[];
  adminItems: NavItem[];
  isAdmin: boolean;
}) {
  const { t } = useI18n();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "1") setCollapsed(true);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
    document.documentElement.style.setProperty("--sidebar-width", collapsed ? "72px" : "220px");
  }, [collapsed, mounted]);

  useEffect(() => {
    document.documentElement.style.setProperty("--sidebar-width", "220px");
    return () => {
      document.documentElement.style.removeProperty("--sidebar-width");
    };
  }, []);

  function toggle() {
    setCollapsed((c) => !c);
  }

  return (
    <aside
      className={cn(
        "va-sidebar fixed inset-y-0 left-0 z-30 hidden flex-col border-r border-slate-200 bg-white shadow-sm transition-[width] duration-300 ease-out lg:flex",
        collapsed ? "w-[72px]" : "w-[220px]",
        mounted && "va-sidebar-in",
      )}
    >
      <div className={cn("flex h-14 items-center border-b border-[var(--border)]", collapsed ? "justify-center px-2" : "px-3")}>
        <BrandLogo
          variant={collapsed ? "mark" : "full"}
          size={collapsed ? "md" : "sm"}
          theme="light"
          href="/dashboard"
          priority
        />
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto overflow-x-hidden px-2 py-3">
        {!collapsed ? (
          <p className="va-sidebar-label mb-1 px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            {t("nav.home")}
          </p>
        ) : null}
        {navItems.map((item) => (
          <SidebarLink key={item.href} item={item} pathname={pathname} collapsed={collapsed} />
        ))}

        {isAdmin ? (
          <>
            {!collapsed ? (
              <p className="va-sidebar-label mb-1 mt-5 px-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                {t("nav.admin")}
              </p>
            ) : null}
            {adminItems.map((item) => (
              <SidebarLink key={item.href} item={item} pathname={pathname} collapsed={collapsed} />
            ))}
          </>
        ) : null}
      </nav>

      <div className="border-t border-[var(--border)] p-2">
        {!collapsed ? (
          <div className="va-sidebar-label mb-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2.5">
            <p className="truncate text-xs font-semibold text-slate-900">{user.full_name}</p>
            <p className="truncate text-[11px] text-slate-600">{user.email}</p>
          </div>
        ) : null}
        <Tooltip label={collapsed ? t("nav.expand") : t("nav.collapse")}>
          <button
            type="button"
            onClick={toggle}
            className="va-btn-interactive flex w-full items-center justify-center gap-2 rounded-lg border border-[var(--border)] bg-white py-2 text-xs font-medium text-[var(--muted)] hover:bg-slate-50 hover:text-[var(--foreground)]"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            {!collapsed ? <span className="va-sidebar-label">{t("nav.collapse")}</span> : null}
          </button>
        </Tooltip>
      </div>
    </aside>
  );
}

function SidebarLink({
  item,
  pathname,
  collapsed,
}: {
  item: NavItem;
  pathname: string;
  collapsed: boolean;
}) {
  const active =
    item.href === "/admin"
      ? pathname === "/admin"
      : pathname === item.href || pathname.startsWith(`${item.href}/`);
  const Icon = item.icon;

  const link = (
    <Link
      href={item.href}
      data-tour={item.href === "/projects" ? "nav-projects" : undefined}
        className={cn(
          "flex items-center rounded-lg py-2.5 text-[13px] font-semibold transition-all duration-200",
        collapsed ? "justify-center px-2" : "gap-2.5 px-2.5",
        active
          ? "va-nav-active font-semibold text-teal-900"
          : "text-slate-700 hover:bg-teal-50/80 hover:text-slate-900",
      )}
    >
      <Icon className={cn("h-4 w-4 shrink-0", active ? "text-teal-700" : "text-slate-600")} />
      {!collapsed ? <span className="va-sidebar-label truncate">{item.label}</span> : null}
    </Link>
  );

  if (collapsed) {
    return <Tooltip label={item.label}>{link}</Tooltip>;
  }
  return link;
}
