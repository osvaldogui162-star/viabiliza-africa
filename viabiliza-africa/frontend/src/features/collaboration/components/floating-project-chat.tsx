"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  AtSign,
  Bot,
  ChevronDown,
  MessageCircle,
  Minimize2,
  Send,
  Users,
  Zap,
} from "lucide-react";

import { PageLoader } from "@/components/ui/spinner";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ChatGreetingBubble } from "@/features/collaboration/components/chat-greeting-bubble";
import { ChatMentionPicker } from "@/features/collaboration/components/chat-mention-picker";
import { useFloatingProjectChat } from "@/features/collaboration/hooks/use-floating-project-chat";
import {
  buildMentionAllText,
  getActiveMention,
  insertMention,
  splitMessageMentions,
} from "@/lib/chat/mention-utils";
import type { ProjectChatMember } from "@/lib/chat/project-members";
import { isAccountWelcomePending } from "@/lib/auth/welcome-session";
import { formatDateTime } from "@/lib/utils/format";
import { cn } from "@/lib/utils/cn";

const GREETING_STORAGE = "va-chat-greeting-dismissed";

function readGreetingDismissed(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(GREETING_STORAGE) === "1";
}

export function FloatingProjectChat() {
  const { user } = useAuth();
  const { t, intlLocale } = useI18n();
  const {
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
    contextHint,
    quickReplies,
    lastMessage,
    isLive,
    justReceived,
    projectMembers,
    membersLoading,
  } = useFloatingProjectChat();

  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const [cursorPos, setCursorPos] = useState(0);
  const [mentionIndex, setMentionIndex] = useState(0);
  const [greetingDismissed, setGreetingDismissed] = useState(true);
  const [greetingVisible, setGreetingVisible] = useState(false);
  const [creatorWelcome, setCreatorWelcome] = useState(false);

  useEffect(() => {
    setGreetingDismissed(readGreetingDismissed());
    setCreatorWelcome(isAccountWelcomePending());
    const onWelcomeComplete = () => setCreatorWelcome(false);
    window.addEventListener("va-welcome-complete", onWelcomeComplete);
    return () => window.removeEventListener("va-welcome-complete", onWelcomeComplete);
  }, []);

  useEffect(() => {
    if (open || unread > 0) {
      setGreetingVisible(false);
      return;
    }
    if (creatorWelcome) {
      setGreetingVisible(true);
      const timer = window.setTimeout(() => setGreetingVisible(false), 16000);
      return () => window.clearTimeout(timer);
    }
    if (greetingDismissed || !activeProjectId) {
      setGreetingVisible(false);
      return;
    }
    setGreetingVisible(true);
    const timer = window.setTimeout(() => setGreetingVisible(false), 12000);
    return () => window.clearTimeout(timer);
  }, [open, greetingDismissed, activeProjectId, unread, creatorWelcome]);

  useEffect(() => {
    if (open && listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [open, messages, sending]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open, activeProjectId]);

  const mentionState = useMemo(
    () => getActiveMention(draft, cursorPos),
    [draft, cursorPos],
  );

  const filteredMembers = useMemo(() => {
    if (!mentionState) return [];
    const q = mentionState.query.trim().toLowerCase();
    if (!q) return projectMembers;
    return projectMembers.filter(
      (m) =>
        m.name.toLowerCase().includes(q) ||
        m.mentionLabel.toLowerCase().includes(q) ||
        (m.email?.toLowerCase().includes(q) ?? false),
    );
  }, [mentionState, projectMembers]);

  const showMentionPicker = Boolean(mentionState && activeProjectId);

  useEffect(() => {
    setMentionIndex(0);
  }, [mentionState?.query]);

  const syncCursor = useCallback(() => {
    const el = inputRef.current;
    if (el) setCursorPos(el.selectionStart ?? draft.length);
  }, [draft.length]);

  const handleSelectMember = useCallback(
    (member: ProjectChatMember) => {
      if (!mentionState) {
        const handle = `@${member.mentionLabel} `;
        setDraft((prev) => `${prev}${handle}`);
        return;
      }
      const { next, cursor } = insertMention(draft, mentionState, member.name);
      setDraft(next);
      setCursorPos(cursor);
      requestAnimationFrame(() => {
        const el = inputRef.current;
        if (!el) return;
        el.focus();
        el.selectionStart = cursor;
        el.selectionEnd = cursor;
      });
    },
    [draft, mentionState, setDraft],
  );

  const insertAtCursor = useCallback(
    (text: string) => {
      const el = inputRef.current;
      const start = el?.selectionStart ?? draft.length;
      const end = el?.selectionEnd ?? start;
      const next = `${draft.slice(0, start)}${text}${draft.slice(end)}`;
      const cursor = start + text.length;
      setDraft(next);
      setCursorPos(cursor);
      requestAnimationFrame(() => {
        if (!el) return;
        el.focus();
        el.selectionStart = cursor;
        el.selectionEnd = cursor;
      });
    },
    [draft, setDraft],
  );

  function dismissGreeting() {
    setGreetingDismissed(true);
    setGreetingVisible(false);
    sessionStorage.setItem(GREETING_STORAGE, "1");
  }

  function openFromGreeting() {
    dismissGreeting();
    setOpen(true);
  }

  const groupedMessages = useMemo(() => {
    const result: { msg: (typeof messages)[0]; showDate: boolean; dateLabel: string }[] = [];
    let lastDate = "";
    for (const msg of messages) {
      const dateKey = new Date(msg.created_at).toDateString();
      const showDate = dateKey !== lastDate;
      if (showDate) lastDate = dateKey;
      result.push({
        msg,
        showDate,
        dateLabel: new Intl.DateTimeFormat(intlLocale, { dateStyle: "medium" }).format(
          new Date(msg.created_at),
        ),
      });
    }
    return result;
  }, [messages, intlLocale]);

  if (!user) return null;

  const preview =
    lastMessage && !open
      ? `${lastMessage.user_name}: ${lastMessage.content.slice(0, 72)}${lastMessage.content.length > 72 ? "…" : ""}`
      : null;

  const representativeName =
    activeProject?.rep_full_name?.trim() ||
    activeProject?.owner?.full_name ||
    user.full_name;

  const greetingName = creatorWelcome ? user.full_name : representativeName;

  function renderMessageContent(content: string, isMine: boolean) {
    return splitMessageMentions(content).map((part, i) =>
      part.type === "mention" ? (
        <span
          key={i}
          className={cn(
            "va-chat-mention rounded px-0.5 font-semibold",
            isMine ? "bg-white/20 text-amber-200" : "bg-amber-100 text-violet-800",
          )}
        >
          {part.value}
        </span>
      ) : (
        <span key={i}>{part.value}</span>
      ),
    );
  }

  return (
    <div className="va-floating-chat va-floating-chat-orbit pointer-events-none fixed bottom-4 right-4 z-[45] flex flex-col items-end gap-2 sm:bottom-6 sm:right-6">
      {!open && preview && unread > 0 ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="va-chat-preview pointer-events-auto max-w-[min(100vw-5rem,18rem)] rounded-2xl border border-violet-200/80 bg-white/95 px-3.5 py-2.5 text-left shadow-xl shadow-violet-900/15 backdrop-blur-md transition hover:scale-[1.02]"
        >
          <p className="text-[10px] font-bold uppercase tracking-wide text-violet-600">
            {t("floatingChat.newMessage")}
          </p>
          <p className="mt-0.5 line-clamp-2 text-xs leading-snug text-zinc-700">{preview}</p>
        </button>
      ) : null}

      {!open && greetingVisible ? (
        <ChatGreetingBubble
          visible
          variant={creatorWelcome ? "creator" : "representative"}
          representativeName={greetingName}
          onOpen={openFromGreeting}
          onDismiss={dismissGreeting}
        />
      ) : null}

      {open ? (
        <div
          className="va-floating-chat-panel pointer-events-auto flex w-[min(100vw-2rem,26rem)] flex-col overflow-hidden rounded-2xl border-2 border-violet-300/50 bg-white shadow-2xl shadow-violet-900/20 sm:w-[26rem]"
          role="dialog"
          aria-label={t("floatingChat.title")}
        >
          <header className="va-chat-header relative overflow-hidden px-4 py-3.5 text-white">
            <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-amber-400/25 blur-2xl" />
            <div className="pointer-events-none absolute -bottom-6 left-0 h-24 w-24 rounded-full bg-fuchsia-400/20 blur-2xl" />

            <div className="relative flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-white/15 ring-1 ring-white/25">
                    <Bot className="h-4 w-4 text-amber-300" />
                  </span>
                  <div>
                    <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-violet-100">
                      {t("floatingChat.title")}
                      <span
                        className={cn(
                          "inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[9px] font-semibold",
                          isLive ? "bg-emerald-400/25 text-emerald-100" : "bg-white/15 text-white/70",
                        )}
                      >
                        <span
                          className={cn(
                            "h-1.5 w-1.5 rounded-full",
                            isLive ? "va-live-dot bg-emerald-300" : "bg-zinc-400",
                          )}
                        />
                        {isLive ? t("floatingChat.live") : "…"}
                      </span>
                    </p>
                    <p className="truncate text-sm font-bold">
                      {activeProject?.name ?? t("floatingChat.selectProject")}
                    </p>
                  </div>
                </div>
                {activeProject?.company_name ? (
                  <p className="mt-1 truncate pl-10 text-xs text-violet-100/90">
                    {activeProject.company_name}
                  </p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-xl border border-white/20 bg-white/10 p-2 transition hover:bg-white/20"
                aria-label={t("floatingChat.minimize")}
              >
                <Minimize2 className="h-4 w-4" />
              </button>
            </div>

            {projectMembers.length > 0 ? (
              <div className="relative mt-2 flex flex-wrap gap-1">
                {projectMembers.slice(0, 6).map((member) => (
                  <button
                    key={member.id}
                    type="button"
                    title={t("floatingChat.mentionMember", { name: member.name })}
                    onClick={() => handleSelectMember(member)}
                    className="flex max-w-[7rem] items-center gap-1 rounded-full border border-white/20 bg-white/10 px-2 py-0.5 text-[10px] font-semibold text-violet-50 transition hover:border-amber-300/50 hover:bg-white/20"
                  >
                    <span className="truncate">@{member.mentionLabel}</span>
                  </button>
                ))}
                {projectMembers.length > 6 ? (
                  <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-violet-100">
                    +{projectMembers.length - 6}
                  </span>
                ) : null}
              </div>
            ) : membersLoading ? (
              <p className="relative mt-2 text-[10px] text-violet-200/80">
                {t("floatingChat.membersLoading")}
              </p>
            ) : null}

            <p className="relative mt-2 flex items-start gap-1.5 rounded-lg border border-white/15 bg-white/10 px-2.5 py-1.5 text-[11px] leading-snug text-violet-50">
              <Zap className="mt-0.5 h-3 w-3 shrink-0 text-amber-300" />
              {contextHint}
            </p>

            {projects.length > 1 ? (
              <div className="relative mt-2">
                <label className="sr-only" htmlFor="va-chat-project-select">
                  {t("floatingChat.selectProject")}
                </label>
                <div className="relative">
                  <select
                    id="va-chat-project-select"
                    value={activeProjectId ?? ""}
                    onChange={(e) => selectProject(e.target.value)}
                    className="w-full appearance-none rounded-xl border border-white/25 bg-slate-900/30 py-2 pl-3 pr-9 text-xs font-semibold text-white backdrop-blur-sm outline-none focus:border-amber-300/50"
                  >
                    <option value="" disabled className="text-zinc-900">
                      {t("floatingChat.selectProject")}
                    </option>
                    {projects.map((p) => (
                      <option key={p.id} value={p.id} className="text-zinc-900">
                        {p.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-white/80" />
                </div>
              </div>
            ) : null}
          </header>

          {activeProjectId && quickReplies.length > 0 ? (
            <div className="flex gap-1.5 overflow-x-auto border-b border-violet-100 bg-violet-50/60 px-3 py-2">
              {quickReplies.map((reply) => (
                <button
                  key={reply}
                  type="button"
                  disabled={sending}
                  onClick={() => void sendMessage(reply)}
                  className="shrink-0 rounded-full border border-violet-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-violet-800 shadow-sm transition hover:border-amber-300 hover:bg-amber-50 hover:text-violet-900 disabled:opacity-50"
                >
                  {reply}
                </button>
              ))}
            </div>
          ) : null}

          <div
            ref={listRef}
            className="va-chat-messages flex max-h-[min(44vh,380px)] min-h-[220px] flex-1 flex-col gap-2 overflow-y-auto bg-[linear-gradient(180deg,#faf5ff_0%,#ffffff_45%)] p-3"
          >
            {!activeProjectId ? (
              <div className="flex flex-1 flex-col items-center justify-center px-4 text-center">
                <MessageCircle className="mb-2 h-10 w-10 text-violet-300" />
                <p className="text-sm font-semibold text-violet-900">{t("floatingChat.selectProject")}</p>
                {projects.length === 0 ? (
                  <p className="mt-1 text-xs text-zinc-500">{t("floatingChat.noProjects")}</p>
                ) : null}
              </div>
            ) : loading && messages.length === 0 ? (
              <div className="flex flex-1 items-center justify-center">
                <PageLoader message={t("floatingChat.syncing")} layout="embedded" />
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-1 flex-col items-center justify-center px-4 text-center">
                <Bot className="mb-2 h-10 w-10 text-violet-400" />
                <p className="text-sm font-medium text-zinc-700">{t("floatingChat.emptyTitle")}</p>
                <p className="mt-1 text-xs text-zinc-500">{t("floatingChat.sendHint")}</p>
                <p className="mt-2 text-[11px] font-medium text-violet-600">{t("floatingChat.mentionHint")}</p>
              </div>
            ) : (
              groupedMessages.map(({ msg, showDate, dateLabel }, index) => {
                const isMine = msg.user_id === user.id;
                return (
                  <div
                    key={msg.id}
                    className="va-chat-message-in"
                    style={{ animationDelay: `${Math.min(index, 8) * 40}ms` }}
                  >
                    {showDate ? (
                      <p className="my-1 text-center text-[10px] font-medium text-violet-400">
                        {dateLabel}
                      </p>
                    ) : null}
                    <div className={cn("flex gap-2", isMine ? "flex-row-reverse" : "flex-row")}>
                      <span
                        className={cn(
                          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ring-2 ring-white",
                          isMine
                            ? "bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white"
                            : "bg-gradient-to-br from-amber-100 to-violet-100 text-violet-800",
                        )}
                      >
                        {msg.user_name.charAt(0).toUpperCase()}
                      </span>
                      <div
                        className={cn(
                          "max-w-[80%] rounded-2xl px-3 py-2 text-sm shadow-md",
                          isMine
                            ? "rounded-tr-md bg-gradient-to-br from-violet-600 to-indigo-600 text-white"
                            : "rounded-tl-md border border-violet-100 bg-white text-zinc-800",
                        )}
                        style={!isMine ? { borderLeftWidth: 3, borderLeftColor: "#f59e0b" } : undefined}
                      >
                        {!isMine ? (
                          <p className="mb-0.5 text-[10px] font-bold text-violet-700">{msg.user_name}</p>
                        ) : null}
                        <p className="leading-relaxed whitespace-pre-wrap break-words">
                          {renderMessageContent(msg.content, isMine)}
                        </p>
                        <p className={cn("mt-1 text-[10px]", isMine ? "text-violet-200" : "text-zinc-400")}>
                          {formatDateTime(msg.created_at, intlLocale)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
            {sending ? (
              <div className="flex gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-100 text-[10px] font-bold text-violet-700">
                  …
                </span>
                <div className="rounded-2xl rounded-tl-md border border-violet-100 bg-white px-3 py-2">
                  <div className="flex gap-1">
                    <span className="va-chat-typing-dot h-2 w-2 rounded-full bg-violet-400" />
                    <span className="va-chat-typing-dot h-2 w-2 rounded-full bg-violet-400 [animation-delay:0.15s]" />
                    <span className="va-chat-typing-dot h-2 w-2 rounded-full bg-violet-400 [animation-delay:0.3s]" />
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          <footer className="border-t border-violet-100 bg-white p-3">
            {showMentionPicker ? (
              <div className="relative mb-2">
                <ChatMentionPicker
                  members={filteredMembers}
                  activeIndex={mentionIndex}
                  onSelect={handleSelectMember}
                  onHover={setMentionIndex}
                />
              </div>
            ) : null}

            <div className="mb-2 flex items-center gap-1.5">
              <button
                type="button"
                disabled={!activeProjectId || projectMembers.length === 0}
                onClick={() => insertAtCursor("@")}
                className="flex h-8 w-8 items-center justify-center rounded-lg border border-violet-200 bg-violet-50 text-violet-700 transition hover:bg-violet-100 disabled:opacity-40"
                title={t("floatingChat.mentionHint")}
                aria-label={t("floatingChat.mentionHint")}
              >
                <AtSign className="h-4 w-4" />
              </button>
              <button
                type="button"
                disabled={!activeProjectId || projectMembers.length === 0 || sending}
                onClick={() => insertAtCursor(buildMentionAllText(projectMembers))}
                className="flex items-center gap-1 rounded-lg border border-violet-200 bg-violet-50 px-2 py-1 text-[10px] font-bold text-violet-700 transition hover:bg-violet-100 disabled:opacity-40"
              >
                <Users className="h-3 w-3" />
                {t("floatingChat.mentionAll")}
              </button>
            </div>

            <div className="flex items-end gap-2">
              <textarea
                ref={inputRef}
                rows={1}
                value={draft}
                onChange={(e) => {
                  setDraft(e.target.value);
                  setCursorPos(e.target.selectionStart ?? e.target.value.length);
                }}
                onClick={syncCursor}
                onKeyUp={syncCursor}
                onSelect={syncCursor}
                onKeyDown={(e) => {
                  if (showMentionPicker && filteredMembers.length > 0) {
                    if (e.key === "ArrowDown") {
                      e.preventDefault();
                      setMentionIndex((i) => Math.min(i + 1, filteredMembers.length - 1));
                      return;
                    }
                    if (e.key === "ArrowUp") {
                      e.preventDefault();
                      setMentionIndex((i) => Math.max(i - 1, 0));
                      return;
                    }
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSelectMember(filteredMembers[mentionIndex]!);
                      return;
                    }
                    if (e.key === "Escape") {
                      e.preventDefault();
                      insertAtCursor(" ");
                      return;
                    }
                  }
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void sendMessage();
                  }
                }}
                disabled={!activeProjectId || sending}
                placeholder={t("collaboration.messagePlaceholder")}
                className="max-h-24 min-h-[2.75rem] flex-1 resize-none rounded-xl border-2 border-violet-100 bg-violet-50/40 px-3 py-2 text-sm outline-none transition focus:border-violet-400 focus:bg-white focus:ring-2 focus:ring-violet-400/20 disabled:opacity-50"
              />
              <button
                type="button"
                disabled={!activeProjectId || !draft.trim() || sending}
                onClick={() => void sendMessage()}
                className={cn(
                  "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-white shadow-lg transition",
                  draft.trim()
                    ? "va-chat-send-ready bg-gradient-to-br from-amber-500 to-orange-500 shadow-amber-500/30 hover:from-amber-400 hover:to-orange-400"
                    : "bg-violet-300 shadow-none",
                  "disabled:cursor-not-allowed disabled:opacity-40",
                )}
                aria-label={t("floatingChat.send")}
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-1.5 text-center text-[10px] text-zinc-400">
              {t("floatingChat.shortcut")} · {t("floatingChat.mentionHint")}
            </p>
          </footer>
        </div>
      ) : null}

      <button
        type="button"
        onClick={() => {
          dismissGreeting();
          setOpen(!open);
        }}
        className={cn(
          "va-floating-chat-fab pointer-events-auto relative flex h-[3.75rem] w-[3.75rem] items-center justify-center rounded-full text-white transition-all duration-300 hover:scale-110 active:scale-95",
          open
            ? "bg-slate-800 shadow-lg hover:bg-slate-900"
            : "va-floating-chat-fab--idle bg-gradient-to-br from-violet-600 via-indigo-600 to-fuchsia-600 shadow-xl shadow-violet-900/40",
          unread > 0 && !open && "va-floating-chat-fab--pulse",
          justReceived && !open && "va-floating-chat-fab--bounce",
        )}
        aria-label={open ? t("floatingChat.minimize") : t("floatingChat.open")}
        aria-expanded={open}
      >
        {!open ? (
          <span className="pointer-events-none absolute inset-0 rounded-full ring-2 ring-amber-400/70 ring-offset-2 ring-offset-transparent" />
        ) : null}
        <MessageCircle className={cn("h-7 w-7", !open && unread > 0 && "va-chat-icon-wiggle")} />
        {!open ? (
          <span className="pointer-events-none absolute -bottom-1 left-1/2 -translate-x-1/2 rounded-full bg-amber-400 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider text-slate-900 shadow">
            Chat
          </span>
        ) : null}
        {unread > 0 && !open ? (
          <span className="absolute -right-1 -top-1 flex h-6 min-w-6 animate-bounce items-center justify-center rounded-full border-2 border-white bg-gradient-to-br from-rose-500 to-orange-500 px-1.5 text-[11px] font-black tabular-nums shadow-lg">
            {unread > 9 ? "9+" : unread}
          </span>
        ) : null}
      </button>
    </div>
  );
}
