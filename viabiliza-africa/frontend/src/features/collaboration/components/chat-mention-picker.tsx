"use client";

import { AtSign, Crown, User, Users } from "lucide-react";

import { useI18n } from "@/components/providers/locale-provider";
import type { ProjectChatMember } from "@/lib/chat/project-members";
import { cn } from "@/lib/utils/cn";

const ROLE_ICON = {
  owner: Crown,
  representative: User,
  collaborator: Users,
  you: User,
};

const ROLE_CLASS = {
  owner: "text-amber-600 bg-amber-50",
  representative: "text-violet-700 bg-violet-50",
  collaborator: "text-indigo-600 bg-indigo-50",
  you: "text-zinc-500 bg-zinc-100",
};

type ChatMentionPickerProps = {
  members: ProjectChatMember[];
  activeIndex: number;
  onSelect: (member: ProjectChatMember) => void;
  onHover: (index: number) => void;
};

export function ChatMentionPicker({
  members,
  activeIndex,
  onSelect,
  onHover,
}: ChatMentionPickerProps) {
  const { t } = useI18n();

  if (members.length === 0) {
    return (
      <div className="rounded-xl border border-violet-200 bg-white px-3 py-2 text-xs text-zinc-500 shadow-lg">
        {t("floatingChat.mentionEmpty")}
      </div>
    );
  }

  return (
    <div
      className="max-h-44 overflow-y-auto rounded-xl border border-violet-200 bg-white py-1 shadow-xl"
      role="listbox"
    >
      <p className="px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-violet-500">
        {t("floatingChat.mentionTitle")}
      </p>
      {members.map((member, index) => {
        const Icon = ROLE_ICON[member.role];
        return (
          <button
            key={member.id}
            type="button"
            role="option"
            aria-selected={index === activeIndex}
            onMouseEnter={() => onHover(index)}
            onClick={() => onSelect(member)}
            className={cn(
              "flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition",
              index === activeIndex ? "bg-violet-100 text-violet-950" : "hover:bg-violet-50",
            )}
          >
            <span
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
                ROLE_CLASS[member.role],
              )}
            >
              <Icon className="h-3.5 w-3.5" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate font-semibold">{member.name}</span>
              {member.email ? (
                <span className="block truncate text-[10px] text-zinc-500">{member.email}</span>
              ) : null}
            </span>
            <span className="shrink-0 rounded-md bg-violet-100 px-1.5 py-0.5 font-mono text-[10px] text-violet-700">
              @{member.mentionLabel}
            </span>
          </button>
        );
      })}
    </div>
  );
}
