"use client";

import { LogOut } from "lucide-react";

import { BrandLogo } from "@/components/brand/brand-logo";
import { BankLogoBadge } from "@/features/financier/components/bank-logo-badge";
import { BankPortalNav } from "@/features/financier/components/bank-portal-nav";
import { useI18n } from "@/components/providers/locale-provider";
import type { User } from "@/lib/types/auth";
import { resolveBankLogo } from "@/lib/banks/bank-brand";
import { findAngolanBank } from "@/lib/data/angolan-banks";

export function BankPortalShell({
  user,
  onLogout,
  children,
}: {
  user: User;
  onLogout: () => void;
  children: React.ReactNode;
}) {
  const { t } = useI18n();
  const bankCode = user.bank_code ?? "bfa";
  const meta = findAngolanBank(bankCode);
  const bank = {
    code: bankCode,
    label_pt: meta?.labelPt ?? bankCode.toUpperCase(),
    label_en: meta?.labelPt ?? bankCode.toUpperCase(),
    logo_path: resolveBankLogo(bankCode, null),
  };

  return (
    <div className="bank-portal bank-portal--financial">
      <header className="bank-portal-fin-header sticky top-0 z-50">
        <div className="mx-auto flex min-h-[5rem] max-w-[1560px] flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <div className="flex min-w-0 items-center gap-3 sm:gap-5">
            <div className="bank-portal-logo-well bank-logo-enter shrink-0">
              <BrandLogo variant="full" size="lg" surface="onDark" href="/financiador" priority />
            </div>
            <div className="hidden min-w-0 sm:block">
              <p className="text-xs font-medium text-[var(--muted)]">{t("financier.portalTag")}</p>
              <h1 className="font-[family-name:var(--font-poppins)] text-xl font-bold leading-tight text-[var(--brand-navy)] lg:text-2xl">
                {t("terminal.dashboardTitle")}
              </h1>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <BankLogoBadge bank={bank} size="md" />
            <span className="hidden max-w-[160px] truncate text-sm font-medium text-[var(--brand-navy)] md:inline">
              {user.full_name}
            </span>
            <button
              type="button"
              onClick={() => void onLogout()}
              className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-white px-3 py-2 text-sm font-semibold text-[var(--brand-navy)] shadow-sm transition hover:border-[var(--brand-teal)] hover:bg-[var(--accent-soft)]"
            >
              <LogOut className="h-4 w-4" strokeWidth={2.25} />
              <span className="hidden sm:inline">{t("userMenu.logout")}</span>
            </button>
          </div>
        </div>
        <p className="bank-portal-fin-header-mobile-title px-4 pb-2 text-center font-[family-name:var(--font-poppins)] text-lg font-bold text-[var(--brand-navy)] sm:hidden">
          {t("terminal.dashboardTitle")}
        </p>
      </header>
      <BankPortalNav className="lg:hidden" />
      <main className="relative">{children}</main>
    </div>
  );
}
