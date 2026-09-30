"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { toast } from "sonner";

import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { collaborationApi } from "@/lib/api/collaboration-api";
import { notificationsApi } from "@/lib/api/notifications-api";
import { projectsApi } from "@/lib/api/projects-api";
import { playChatNotificationSound } from "@/lib/chat/chat-notification-sound";
import {
  buildProjectChatMembers,
  type ProjectChatMember,
} from "@/lib/chat/project-members";
import { ApiError } from "@/lib/api/http-client";
import type { ChatMessage } from "@/lib/types/collaboration";
import type { Project, ProjectShare } from "@/lib/types/project";

const POLL_MS = 2500;
const STORAGE_OPEN = "va-chat-panel-open";
const STORAGE_PROJECT = "va-chat-active-project";

export type ChatContext = "dashboard" | "project" | "projects" | "admin" | "other";

function readLastRead(projectId: string): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(`va-chat-last-read-${projectId}`);
}

function writeLastRead(projectId: string, messageId: string) {
  sessionStorage.setItem(`va-chat-last-read-${projectId}`, messageId);
}

function extractRouteProjectId(pathname: string): string | null {
  const match = pathname.match(/^\/projects\/([^/]+)/);
  const id = match?.[1];
  if (!id || id === "new") return null;
  return id;
}

function detectContext(pathname: string): ChatContext {
  if (pathname.startsWith("/dashboard")) return "dashboard";
  if (pathname.match(/^\/projects\/[^/]+/)) return "project";
  if (pathname.startsWith("/projects")) return "projects";
  if (pathname.startsWith("/admin")) return "admin";
  return "other";
}

export function useFloatingProjectChat() {
  const pathname = usePathname();
  const { user } = useAuth();
  const { t, locale } = useI18n();

  const routeProjectId = extractRouteProjectId(pathname);
  const pageContext = detectContext(pathname);

  const [open, setOpenState] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [draft, setDraft] = useState("");
  const [unread, setUnread] = useState(0);
  const [isLive, setIsLive] = useState(true);
  const [justReceived, setJustReceived] = useState(false);
  const [projectShares, setProjectShares] = useState<ProjectShare[]>([]);
  const [membersLoading, setMembersLoading] = useState(false);

  const knownIdsRef = useRef<Set<string>>(new Set());
  const lastPollIdRef = useRef<string | null>(null);
  const initializedRef = useRef(false);
  const openRef = useRef(open);

  useEffect(() => {
    openRef.current = open;
  }, [open]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setOpenState(sessionStorage.getItem(STORAGE_OPEN) === "1");
    const stored = sessionStorage.getItem(STORAGE_PROJECT);
    if (stored) setActiveProjectId(stored);
  }, []);

  useEffect(() => {
    if (routeProjectId) {
      setActiveProjectId(routeProjectId);
      sessionStorage.setItem(STORAGE_PROJECT, routeProjectId);
      return;
    }
    if (projects.length === 1 && !activeProjectId) {
      setActiveProjectId(projects[0].id);
      sessionStorage.setItem(STORAGE_PROJECT, projects[0].id);
    }
  }, [routeProjectId, projects, activeProjectId]);

  const onProjectsListPage =
    pathname === "/projects" || (pathname.startsWith("/projects") && !routeProjectId);

  useEffect(() => {
    if (onProjectsListPage) {
      setProjects([]);
      return;
    }
    void projectsApi
      .list({ limit: 15 })
      .then((res) => setProjects(res.items ?? []))
      .catch(() => setProjects([]));
  }, [onProjectsListPage]);

  useEffect(() => {
    if (!activeProjectId || onProjectsListPage) {
      if (onProjectsListPage) setActiveProject(null);
      return;
    }
    const cached = projects.find((p) => p.id === activeProjectId);
    if (cached) setActiveProject(cached);
    void projectsApi
      .get(activeProjectId)
      .then(setActiveProject)
      .catch(() => {
        if (!cached) setActiveProject(null);
      });
  }, [activeProjectId, projects, onProjectsListPage]);

  useEffect(() => {
    if (!activeProjectId) {
      setProjectShares([]);
      return;
    }
    setMembersLoading(true);
    void projectsApi
      .listShares(activeProjectId)
      .then((res) => setProjectShares(res.items ?? []))
      .catch(() => setProjectShares([]))
      .finally(() => setMembersLoading(false));
  }, [activeProjectId]);

  const projectMembers = useMemo(
    (): ProjectChatMember[] =>
      buildProjectChatMembers(activeProject, projectShares, user?.id),
    [activeProject, projectShares, user?.id],
  );

  const contextHint = useMemo(() => {
    if (pageContext === "dashboard") return t("floatingChat.hintDashboard");
    if (pageContext === "project") return t("floatingChat.hintProject");
    if (pageContext === "projects") return t("floatingChat.hintProjects");
    return t("floatingChat.hintDefault");
  }, [pageContext, t]);

  const quickReplies = useMemo(() => {
    const en = locale === "en";
    if (pageContext === "project") {
      return en
        ? ["Budget update", "Pending review", "Report is ready", "Need team input"]
        : ["Actualização de orçamento", "Revisão pendente", "Relatório pronto", "Preciso de input"];
    }
    if (pageContext === "dashboard") {
      return en
        ? ["Weekly progress", "Need support", "All on track"]
        : ["Progresso semanal", "Preciso de apoio", "Tudo em dia"];
    }
    return en
      ? ["Hello team", "Quick update", "Can we sync?"]
      : ["Olá equipa", "Actualização rápida", "Podemos alinhar?"];
  }, [pageContext, locale]);

  const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;

  const markRead = useCallback((items: ChatMessage[]) => {
    if (!activeProjectId || items.length === 0) return;
    const newest = items[items.length - 1];
    if (newest?.id) {
      writeLastRead(activeProjectId, newest.id);
      void notificationsApi.markChatRead(activeProjectId, newest.id);
      setUnread(0);
    }
    knownIdsRef.current = new Set(items.map((m) => m.id));
  }, [activeProjectId]);

  const handleIncoming = useCallback(
    (items: ChatMessage[], isInitial: boolean) => {
      if (!user) {
        setMessages(items);
        return;
      }

      const prevIds = knownIdsRef.current;
      let shouldPlaySound = false;
      let addedUnread = 0;

      for (const msg of items) {
        if (prevIds.has(msg.id)) continue;

        if (msg.user_id !== user.id) {
          if (isInitial) {
            const lastRead = activeProjectId ? readLastRead(activeProjectId) : null;
            if (lastRead) {
              const lastReadIdx = items.findIndex((m) => m.id === lastRead);
              const msgIdx = items.findIndex((m) => m.id === msg.id);
              if (lastReadIdx >= 0 && msgIdx > lastReadIdx) addedUnread += 1;
              else if (lastReadIdx < 0) addedUnread += 1;
            }
          } else {
            addedUnread += 1;
            shouldPlaySound = true;
          }
        }
      }

      items.forEach((m) => knownIdsRef.current.add(m.id));
      setMessages(items);

      if (addedUnread > 0 && !openRef.current) {
        setUnread((n) => n + addedUnread);
        if (shouldPlaySound) {
          playChatNotificationSound();
          setJustReceived(true);
          window.setTimeout(() => setJustReceived(false), 2400);
        }
      } else if (openRef.current && items.length > 0) {
        markRead(items);
      }
    },
    [user, activeProjectId, markRead],
  );

  const fetchMessages = useCallback(
    async (isInitial = false) => {
      if (!activeProjectId) return;
      try {
        setIsLive(true);
        if (isInitial || !lastPollIdRef.current) {
          const res = await collaborationApi.listChatMessages(activeProjectId, 60);
          const items = res.items ?? [];
          if (items.length) lastPollIdRef.current = items[items.length - 1]?.id ?? null;
          handleIncoming(items, isInitial || !initializedRef.current);
          if (!initializedRef.current) initializedRef.current = true;
          return;
        }
        const poll = await notificationsApi.pollChat(
          activeProjectId,
          lastPollIdRef.current ?? undefined,
        );
        if (poll.messages.length) {
          setMessages((prev) => {
            const merged = [...prev];
            for (const m of poll.messages) {
              if (!knownIdsRef.current.has(m.id)) {
                merged.push(m as ChatMessage);
                knownIdsRef.current.add(m.id);
              }
            }
            handleIncoming(merged, false);
            return merged;
          });
          lastPollIdRef.current = poll.messages[poll.messages.length - 1]?.id ?? lastPollIdRef.current;
        }
      } catch {
        setIsLive(false);
        if (isInitial) setMessages([]);
      }
    },
    [activeProjectId, handleIncoming],
  );

  useEffect(() => {
    initializedRef.current = false;
    knownIdsRef.current = new Set();
    lastPollIdRef.current = null;
    setMessages([]);
    if (!activeProjectId || onProjectsListPage || !open) {
      setUnread(0);
      return;
    }

    setLoading(true);
    void fetchMessages(true).finally(() => setLoading(false));

    const timer = window.setInterval(() => void fetchMessages(false), POLL_MS);
    return () => window.clearInterval(timer);
  }, [activeProjectId, fetchMessages, onProjectsListPage, open]);

  useEffect(() => {
    if (open && messages.length > 0) markRead(messages);
  }, [open, messages, markRead]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "c") {
        e.preventDefault();
        setOpenState((prev) => {
          const next = !prev;
          sessionStorage.setItem(STORAGE_OPEN, next ? "1" : "0");
          return next;
        });
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function setOpen(next: boolean) {
    setOpenState(next);
    sessionStorage.setItem(STORAGE_OPEN, next ? "1" : "0");
    if (next && messages.length > 0) markRead(messages);
  }

  function selectProject(id: string) {
    setActiveProjectId(id);
    sessionStorage.setItem(STORAGE_PROJECT, id);
    initializedRef.current = false;
    setUnread(0);
  }

  async function sendMessage(content?: string) {
    const text = (content ?? draft).trim();
    if (!activeProjectId || !text) return;
    setSending(true);
    if (!content) setDraft("");
    try {
      await collaborationApi.sendChatMessage(activeProjectId, text);
      await fetchMessages(false);
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.sendError"));
      if (!content) setDraft(text);
    } finally {
      setSending(false);
    }
  }

  return {
    open,
    setOpen,
    activeProjectId,
    activeProject,
    projects,
    selectProject,
    messages,
    loading,
    sending,
    draft,
    setDraft,
    sendMessage,
    unread,
    routeProjectId,
    contextHint,
    quickReplies,
    lastMessage,
    isLive,
    justReceived,
    pageContext,
    projectMembers,
    membersLoading,
  };
}
