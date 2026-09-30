"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  FileText,
  FolderKanban,
  Landmark,
  LayoutDashboard,
  Receipt,
  PlugZap,
} from "lucide-react";
import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";

const LINKS = [
  { href: "/financiador", labelKey: "bankPortal.navDashboard", icon: LayoutDashboard, exact: true },
  { href: "/financiador/projectos", labelKey: "bankPortal.navProjects", icon: FolderKanban },
  { href: "/financiador/integracao", labelKey: "terminal.navIntegration", icon: PlugZap },
  { href: "/financiador/desembolsos", labelKey: "bankPortal.navDisbursements", icon: Receipt },
  { href: "/financiador/alertas", labelKey: "bankPortal.navAlerts", icon: AlertTriangle },
  { href: "/financiador/documentos", labelKey: "bankPortal.navDocuments", icon: FileText },
  { href: "/financiador/actividade", labelKey: "bankPortal.navActivity", icon: Activity },
  { href: "/financiador/relatorios", labelKey: "bankPortal.navReports", icon: Landmark },
] as const;

export function BankPortalNav({ className }: { className?: string }) {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <nav className={cn("bank-portal-nav sticky top-[4.5rem] z-40", className)}>
      <div className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-4 py-2.5 sm:px-6 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {LINKS.map((link) => {
          const { href, labelKey, icon: Icon } = link;
          const exact = "exact" in link && link.exact === true;
          const active = exact
            ? pathname === href
            : pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              data-active={active ? "true" : "false"}
              className={cn(
                "bank-portal-nav-link inline-flex shrink-0 items-center gap-2 rounded-full px-3.5 py-2 text-xs font-semibold sm:text-sm",
                active
                  ? "bg-[var(--brand-navy)] text-white shadow-md"
                  : "text-[var(--foreground)] hover:bg-white hover:text-[var(--brand-navy)] hover:shadow-sm",
              )}
            >
              <Icon className="h-4 w-4 shrink-0" strokeWidth={2.25} />
              {t(labelKey)}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
