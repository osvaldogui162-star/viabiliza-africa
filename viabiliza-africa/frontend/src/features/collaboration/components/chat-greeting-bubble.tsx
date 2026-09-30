"use client";

import { Sparkles, UserRound } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import { cn } from "@/lib/utils/cn";

type ChatGreetingBubbleProps = {
  visible: boolean;
  variant?: "representative" | "creator";
  representativeName?: string | null;
  onOpen: () => void;
  onDismiss: () => void;
};

export function ChatGreetingBubble({
  visible,
  variant = "representative",
  representativeName,
  onOpen,
  onDismiss,
}: ChatGreetingBubbleProps) {
  const { t } = useI18n();

  if (!visible) return null;

  const isCreator = variant === "creator";
  const name =
    representativeName?.trim() ||
    (isCreator ? t("onboarding.welcomeFallback") : t("floatingChat.greetingFallback"));

  return (
    <div
      className={cn(
        "va-chat-greeting-wrap pointer-events-auto relative max-w-[min(100vw-5rem,16rem)]",
        isCreator && "va-chat-greeting-wrap--creator",
      )}
    >
      <button
        type="button"
        onClick={onOpen}
        className={cn(
          "va-chat-greeting-bubble group w-full rounded-2xl border-2 px-3.5 py-2.5 text-left shadow-xl transition hover:scale-[1.03]",
          isCreator
            ? "border-teal-300/80 bg-gradient-to-br from-white via-teal-50 to-emerald-50 shadow-teal-900/15"
            : "border-amber-300/80 bg-gradient-to-br from-white via-amber-50 to-violet-50 shadow-violet-900/15",
        )}
      >
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "va-chat-greeting-emoji flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-lg shadow-md ring-2",
              isCreator
                ? "bg-gradient-to-br from-teal-600 to-emerald-600 ring-teal-200"
                : "bg-violet-600 ring-amber-300",
            )}
          >
            👤
          </span>
          <div className="min-w-0">
            <p
              className={cn(
                "flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide",
                isCreator ? "text-teal-700" : "text-violet-600",
              )}
            >
              {isCreator ? (
                <>
                  <Sparkles className="h-3 w-3" />
                  {t("floatingChat.creatorEyebrow")}
                </>
              ) : (
                t("floatingChat.greetingEyebrow")
              )}
            </p>
            <p className="truncate text-sm font-bold text-zinc-900">
              {isCreator
                ? t("floatingChat.creatorHello", { name })
                : t("floatingChat.greetingHello", { name })}
            </p>
          </div>
        </div>
        <p
          className={cn(
            "mt-1.5 text-[10px] font-medium leading-snug",
            isCreator ? "text-teal-800/80" : "text-violet-700/80",
          )}
        >
          {isCreator ? t("floatingChat.creatorSub") : null}
        </p>
        <p
          className={cn(
            "mt-1 flex items-center gap-1 text-[10px] font-medium",
            isCreator ? "text-teal-700/90" : "text-violet-700/80",
          )}
        >
          <UserRound className="h-3 w-3" />
          {isCreator ? t("floatingChat.creatorTap") : t("floatingChat.greetingTap")}
        </p>
      </button>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onDismiss();
        }}
        className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-zinc-800 text-[10px] text-white opacity-0 shadow transition group-hover:opacity-100"
        aria-label={t("common.close")}
      >
        ×
      </button>
      <span
        className={cn(
          "va-chat-greeting-tail pointer-events-none absolute -bottom-2 right-8 h-3 w-3 rotate-45 border-b-2 border-r-2",
          isCreator ? "border-teal-300/80 bg-teal-50" : "border-amber-300/80 bg-amber-50",
        )}
      />
    </div>
  );
}
