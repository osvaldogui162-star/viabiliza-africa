"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  Bell,
  CheckCheck,
  CreditCard,
  FileText,
  MessageSquare,
  Share2,
  Sparkles,
} from "lucide-react";

import { useAuth } from "@/components/providers/auth-provider";
import { useNotifications } from "@/hooks/use-notifications";
import { AnchoredPanel } from "@/components/ui/anchored-panel";
import { useI18n } from "@/components/providers/locale-provider";
import { useDocumentUnreadTitle } from "@/hooks/use-document-unread-title";
import { unlockChatNotificationSound } from "@/lib/chat/chat-notification-sound";
import type { AppNotification, NotificationType } from "@/lib/types/notifications";
import { cn } from "@/lib/utils/cn";
import { formatRelativeTime } from "@/features/admin/lib/admin-audit-utils";

const ICONS: Record<NotificationType, typeof Bell> = {
  chat_message: MessageSquare,
  chat_mention: MessageSquare,
  report_ready: FileText,
  project_shared: Share2,
  payment_confirmed: CreditCard,
  subscription_expiring: Sparkles,
  system: Bell,
};

export function NotificationCenter() {
  const { user } = useAuth();
  const { locale } = useI18n();
  const en = locale === "en";
  const notificationsEnabled = Boolean(user?.id && user.id !== "session");
  const { items, unreadCount, markRead, markAllRead } = useNotifications(notificationsEnabled);
  const [open, setOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useDocumentUnreadTitle(unreadCount);

  useEffect(() => {
    function unlock() {
      unlockChatNotificationSound();
    }
    window.addEventListener("pointerdown", unlock, { once: true });
    window.addEventListener("keydown", unlock, { once: true });
    return () => {
      window.removeEventListener("pointerdown", unlock);
      window.removeEventListener("keydown", unlock);
    };
  }, []);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-white text-zinc-600 transition hover:bg-zinc-50"
        aria-label={en ? "Notifications" : "Notificações"}
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 ? (
          <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        ) : null}
      </button>

      <AnchoredPanel
        open={open}
        onClose={() => setOpen(false)}
        anchorRef={buttonRef}
        className="w-[min(22rem,calc(100vw-1.5rem))] overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-2xl shadow-zinc-300/40"
      >
        <div className="max-h-[min(70vh,24rem)] overflow-y-auto">
          <div className="flex items-center justify-between border-b border-zinc-100 px-4 py-3">
            <p className="text-sm font-bold text-zinc-900">{en ? "Notifications" : "Notificações"}</p>
            {unreadCount > 0 ? (
              <button
                type="button"
                onClick={() => void markAllRead()}
                className="flex items-center gap-1 text-xs font-semibold text-teal-700 hover:underline"
              >
                <CheckCheck className="h-3.5 w-3.5" />
                {en ? "Mark all read" : "Marcar lidas"}
              </button>
            ) : null}
          </div>
          <div>
            {items.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-zinc-500">
                {en ? "No notifications yet" : "Sem notificações"}
              </p>
            ) : (
              items.map((n) => (
                <NotificationRow
                  key={n.id}
                  item={n}
                  locale={locale}
                  onRead={() => void markRead(n.id)}
                  onNavigate={() => setOpen(false)}
                />
              ))
            )}
          </div>
        </div>
      </AnchoredPanel>
    </div>
  );
}

function NotificationRow({
  item,
  locale,
  onRead,
  onNavigate,
}: {
  item: AppNotification;
  locale: string;
  onRead: () => void;
  onNavigate: () => void;
}) {
  const Icon = ICONS[item.type] ?? Bell;
  const inner = (
    <div
      className={cn(
        "flex gap-3 px-4 py-3 transition hover:bg-zinc-50",
        !item.is_read && "bg-teal-50/50",
      )}
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-zinc-100 text-zinc-600">
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-zinc-900">{item.title}</p>
        {item.body ? <p className="mt-0.5 line-clamp-2 text-xs text-zinc-600">{item.body}</p> : null}
        <p className="mt-1 text-[10px] text-zinc-400">{formatRelativeTime(item.created_at, locale)}</p>
      </div>
    </div>
  );

  if (item.href) {
    return (
      <Link
        href={item.href}
        onClick={() => {
          if (!item.is_read) onRead();
          onNavigate();
        }}
      >
        {inner}
      </Link>
    );
  }

  return (
    <button type="button" className="w-full text-left" onClick={() => !item.is_read && onRead()}>
      {inner}
    </button>
  );
}
