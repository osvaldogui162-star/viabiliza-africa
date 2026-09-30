"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError } from "@/lib/api/http-client";
import { notificationsApi } from "@/lib/api/notifications-api";
import { playChatNotificationSound } from "@/lib/chat/chat-notification-sound";
import type { AppNotification } from "@/lib/types/notifications";

const POLL_VISIBLE_MS = 15_000;
const POLL_HIDDEN_MS = 45_000;

function isChatNotification(n: AppNotification) {
  return n.type === "chat_message" || n.type === "chat_mention";
}

export function useNotifications(enabled = true) {
  const [items, setItems] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const knownIdsRef = useRef<Set<string>>(new Set());
  const bootstrappedRef = useRef(false);

  const refresh = useCallback(async () => {
    if (!enabled) return;
    try {
      const res = await notificationsApi.list({ limit: 30 });
      setItems(res.items);
      setUnreadCount(res.unread_count);

      if (!bootstrappedRef.current) {
        res.items.forEach((n) => knownIdsRef.current.add(n.id));
        bootstrappedRef.current = true;
        return;
      }

      for (const n of res.items) {
        if (knownIdsRef.current.has(n.id)) continue;
        knownIdsRef.current.add(n.id);
        if (!n.is_read && isChatNotification(n) && document.visibilityState === "visible") {
          playChatNotificationSound();
        }
      }
    } catch (error) {
      if (error instanceof ApiError && (error.status === 401 || error.status >= 500)) {
        return;
      }
      if (error instanceof ApiError && error.status === 408) {
        return;
      }
      console.warn("[notifications] refresh failed", error);
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    void refresh();
    if (!enabled) return;

    let timer: number;

    function schedule() {
      const ms = document.visibilityState === "visible" ? POLL_VISIBLE_MS : POLL_HIDDEN_MS;
      timer = window.setTimeout(async () => {
        await refresh();
        schedule();
      }, ms);
    }

    schedule();

    function onVisibility() {
      window.clearTimeout(timer);
      if (document.visibilityState === "visible") void refresh();
      schedule();
    }

    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [refresh, enabled]);

  async function markRead(id: string) {
    const res = await notificationsApi.markRead(id);
    setUnreadCount(res.unread_count);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
  }

  async function markAllRead() {
    await notificationsApi.markAllRead();
    setUnreadCount(0);
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
  }

  const chatUnreadCount = items.filter((n) => !n.is_read && isChatNotification(n)).length;

  return { items, unreadCount, chatUnreadCount, loading, refresh, markRead, markAllRead };
}
