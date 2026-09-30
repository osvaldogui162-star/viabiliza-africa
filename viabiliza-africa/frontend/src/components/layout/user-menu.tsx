"use client";

import Link from "next/link";
import { ChevronDown, CreditCard, LogOut, Shield } from "lucide-react";
import { useMemo, useRef, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { AnchoredPanel } from "@/components/ui/anchored-panel";
import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";
import type { User, UserRole } from "@/lib/types/auth";

function getInitials(fullName: string) {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 1).toUpperCase();
  return `${parts[0].slice(0, 1)}${parts[parts.length - 1].slice(0, 1)}`.toUpperCase();
}

interface UserMenuProps {
  user: User;
  onLogout: () => void | Promise<void>;
  className?: string;
}

export function UserMenu({ user, onLogout, className }: UserMenuProps) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const initials = useMemo(() => getInitials(user.full_name), [user.full_name]);

  const roleLabels: Record<UserRole, string> = useMemo(
    () => ({
      admin: t("roles.admin"),
      financial: t("roles.financial"),
      user: t("roles.user"),
      bank: t("roles.bank"),
    }),
    [t],
  );

  return (
    <div className={cn("relative", className)}>
      <button
        ref={buttonRef}
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "va-btn-interactive inline-flex h-10 max-w-[240px] items-center gap-2.5 rounded-full border border-zinc-200/90 bg-white py-1.5 pl-1.5 pr-3 shadow-sm",
          "hover:border-zinc-300 hover:bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-emerald-100",
          open && "border-emerald-200 bg-emerald-50/30 ring-2 ring-emerald-100",
        )}
      >
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-zinc-100 to-zinc-200 text-xs font-semibold text-zinc-700 ring-1 ring-white">
          {initials}
        </span>
        <span className="truncate text-sm font-medium text-zinc-800">{user.full_name}</span>
        <ChevronDown
          className={cn("h-3.5 w-3.5 shrink-0 text-zinc-400 transition", open && "rotate-180")}
        />
      </button>

      <AnchoredPanel
        open={open}
        onClose={() => setOpen(false)}
        anchorRef={buttonRef}
        className="w-[min(18rem,calc(100vw-1.5rem))] overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-2xl shadow-zinc-300/40"
      >
        <div role="menu" className="max-h-[min(70vh,22rem)] overflow-y-auto">
          <div className="border-b border-zinc-100 bg-gradient-to-r from-zinc-50 to-emerald-50/40 px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white text-sm font-semibold text-zinc-700 shadow-sm ring-1 ring-zinc-200">
                {initials}
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-zinc-900">{user.full_name}</p>
                <p className="truncate text-xs text-zinc-500">{user.email}</p>
              </div>
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <Badge variant="success">{roleLabels[user.role]}</Badge>
              <span className="inline-flex items-center gap-1 text-xs text-zinc-500">
                <Shield className="h-3.5 w-3.5" />
                {t("userMenu.activeSession")}
              </span>
            </div>
          </div>

          <div className="p-2">
            <Link
              href="/conta/assinatura"
              role="menuitem"
              onClick={() => setOpen(false)}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-zinc-700 transition hover:bg-zinc-50"
            >
              <CreditCard className="h-4 w-4 text-zinc-400" />
              {t("userMenu.profile")}
            </Link>
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false);
                void onLogout();
              }}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm text-red-600 transition hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              {t("userMenu.logout")}
            </button>
          </div>
        </div>
      </AnchoredPanel>
    </div>
  );
}
