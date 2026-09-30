import type { Project, ProjectShare } from "@/lib/types/project";

export type ProjectChatMember = {
  id: string;
  name: string;
  email?: string;
  role: "owner" | "collaborator" | "representative" | "you";
  mentionLabel: string;
};

function slugMention(name: string): string {
  return name.trim().replace(/\s+/g, "");
}

export function buildProjectChatMembers(
  project: Project | null,
  shares: ProjectShare[],
  currentUserId?: string,
): ProjectChatMember[] {
  if (!project) return [];

  const map = new Map<string, ProjectChatMember>();

  if (project.owner) {
    map.set(project.owner.id, {
      id: project.owner.id,
      name: project.owner.full_name,
      email: project.owner.email,
      role: project.owner.id === currentUserId ? "you" : "owner",
      mentionLabel: slugMention(project.owner.full_name),
    });
  }

  if (project.rep_full_name?.trim()) {
    const repKey = `rep:${project.rep_full_name}`;
    if (![...map.values()].some((m) => m.name === project.rep_full_name)) {
      map.set(repKey, {
        id: repKey,
        name: project.rep_full_name.trim(),
        email: project.rep_email ?? undefined,
        role: "representative",
        mentionLabel: slugMention(project.rep_full_name),
      });
    }
  }

  for (const share of shares) {
    if (map.has(share.user_id)) continue;
    map.set(share.user_id, {
      id: share.user_id,
      name: share.user_full_name,
      email: share.user_email,
      role: share.user_id === currentUserId ? "you" : "collaborator",
      mentionLabel: slugMention(share.user_full_name),
    });
  }

  return [...map.values()].sort((a, b) => {
    const order = { owner: 0, representative: 1, collaborator: 2, you: 3 };
    return order[a.role] - order[b.role] || a.name.localeCompare(b.name, "pt");
  });
}

export function filterMembersByQuery(members: ProjectChatMember[], query: string): ProjectChatMember[] {
  const q = query.trim().toLowerCase();
  if (!q) return members;
  return members.filter(
    (m) =>
      m.name.toLowerCase().includes(q) ||
      m.mentionLabel.toLowerCase().includes(q) ||
      (m.email?.toLowerCase().includes(q) ?? false),
  );
}
