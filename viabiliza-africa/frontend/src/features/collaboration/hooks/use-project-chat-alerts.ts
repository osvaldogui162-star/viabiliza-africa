"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { useAuth } from "@/components/providers/auth-provider";
import { notificationsApi } from "@/lib/api/notifications-api";
import { collaborationApi } from "@/lib/api/collaboration-api";
import { playChatNotificationSound } from "@/lib/chat/chat-notification-sound";
import type { ChatMessage } from "@/lib/types/collaboration";

const POLL_MS = 3000;

function readLastRead(projectId: string): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(`va-chat-last-read-${projectId}`);
}

function writeLastRead(projectId: string, messageId: string) {
  sessionStorage.setItem(`va-chat-last-read-${projectId}`, messageId);
}

/** Alertas de chat por projecto — funciona mesmo quando o separador Colaboração não está activo. */
export function useProjectChatAlerts(projectId: string, chatTabActive: boolean) {
  const { user } = useAuth();
  const [unread, setUnread] = useState(0);
  const lastMsgIdRef = useRef<string | null>(null);
  const knownIdsRef = useRef<Set<string>>(new Set());
  const chatTabActiveRef = useRef(chatTabActive);

  useEffect(() => {
    chatTabActiveRef.current = chatTabActive;
  }, [chatTabActive]);

  const markRead = useCallback(
    (messages: ChatMessage[]) => {
      if (!messages.length) return;
      const newest = messages[messages.length - 1];
      if (!newest?.id) return;
      writeLastRead(projectId, newest.id);
      void notificationsApi.markChatRead(projectId, newest.id);
      setUnread(0);
      knownIdsRef.current = new Set(messages.map((m) => m.id));
    },
    [projectId],
  );

  useEffect(() => {
    if (!projectId || !user) return;

    knownIdsRef.current = new Set();
    lastMsgIdRef.current = null;
    setUnread(0);

    let cancelled = false;

    const userId = user.id;

    async function bootstrap() {
      try {
        const res = await collaborationApi.listChatMessages(projectId, 40);
        if (cancelled) return;
        const items = res.items ?? [];
        items.forEach((m) => knownIdsRef.current.add(m.id));
        if (items.length) lastMsgIdRef.current = items[items.length - 1]?.id ?? null;

        if (chatTabActiveRef.current) {
          markRead(items);
          return;
        }

        const lastRead = readLastRead(projectId);
        let count = 0;
        for (const msg of items) {
          if (msg.user_id === userId) continue;
          if (!lastRead) {
            count += 1;
            continue;
          }
          const lastReadIdx = items.findIndex((m) => m.id === lastRead);
          const msgIdx = items.findIndex((m) => m.id === msg.id);
          if (lastReadIdx >= 0 && msgIdx > lastReadIdx) count += 1;
        }
        setUnread(count);
      } catch {
        /* silent */
      }
    }

    void bootstrap();

    const poll = async () => {
      try {
        const res = await notificationsApi.pollChat(projectId, lastMsgIdRef.current ?? undefined);
        if (cancelled || !res.messages.length) return;

        let added = 0;
        for (const raw of res.messages) {
          if (knownIdsRef.current.has(raw.id)) continue;
          knownIdsRef.current.add(raw.id);
          if (raw.user_id !== userId) added += 1;
        }
        lastMsgIdRef.current = res.messages[res.messages.length - 1]?.id ?? lastMsgIdRef.current;

        if (added > 0) {
          if (chatTabActiveRef.current) {
            markRead(res.messages as ChatMessage[]);
          } else {
            setUnread((n) => n + added);
            playChatNotificationSound();
          }
        }
      } catch {
        /* silent poll */
      }
    };

    void poll();
    const id = window.setInterval(() => void poll(), POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [projectId, user, markRead]);

  useEffect(() => {
    if (!chatTabActive || !projectId) return;
    void collaborationApi.listChatMessages(projectId, 10).then((res) => {
      if (res.items?.length) markRead(res.items);
    });
  }, [chatTabActive, projectId, markRead]);

  return { unread };
}
