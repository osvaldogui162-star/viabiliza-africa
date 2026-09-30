"use client";

import { UserMenu } from "@/components/layout/user-menu";
import { CurrencySelector } from "@/components/layout/currency-selector";
import { LocaleSelector } from "@/components/layout/locale-selector";
import { NotificationCenter } from "@/components/layout/notification-center";
import type { User } from "@/lib/types/auth";

interface AppHeaderActionsProps {
  user: User;
  onLogout: () => void | Promise<void>;
}

export function AppHeaderActions({ user, onLogout }: AppHeaderActionsProps) {
  return (
    <div className="flex items-center gap-2 sm:gap-2.5">
      <NotificationCenter />
      <CurrencySelector />
      <LocaleSelector />
      <UserMenu user={user} onLogout={onLogout} />
    </div>
  );
}
