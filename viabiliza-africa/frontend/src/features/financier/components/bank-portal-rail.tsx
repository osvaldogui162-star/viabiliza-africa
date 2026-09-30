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
  { href: "/financiador", icon: LayoutDashboard, labelKey: "bankPortal.navDashboard", exact: true },
  { href: "/financiador/projectos", icon: FolderKanban, labelKey: "bankPortal.navProjects" },
  { href: "/financiador/integracao", icon: PlugZap, labelKey: "terminal.navIntegration" },
  { href: "/financiador/desembolsos", icon: Receipt, labelKey: "bankPortal.navDisbursements" },
  { href: "/financiador/alertas", icon: AlertTriangle, labelKey: "bankPortal.navAlerts" },
  { href: "/financiador/documentos", icon: FileText, labelKey: "bankPortal.navDocuments" },
  { href: "/financiador/actividade", icon: Activity, labelKey: "bankPortal.navActivity" },
  { href: "/financiador/relatorios", icon: Landmark, labelKey: "bankPortal.navReports" },
] as const;

export function BankPortalRail() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <aside className="bank-portal-rail" aria-label={t("bankPortal.navDashboard")}>
      <nav className="flex flex-col gap-1.5 p-1.5">
        {LINKS.map((link) => {
          const Icon = link.icon;
          const exact = "exact" in link && link.exact === true;
          const active = exact
            ? pathname === link.href
            : pathname === link.href || pathname.startsWith(`${link.href}/`);
          return (
            <Link
              key={link.href}
              href={link.href}
              title={t(link.labelKey)}
              className={cn("bank-portal-rail-btn", active && "bank-portal-rail-btn--active")}
            >
              <Icon className="h-5 w-5" strokeWidth={2.25} />
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
