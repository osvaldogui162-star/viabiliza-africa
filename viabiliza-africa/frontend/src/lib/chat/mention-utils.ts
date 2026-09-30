export type MentionState = {
  query: string;
  start: number;
  end: number;
};

export function getActiveMention(text: string, cursor: number): MentionState | null {
  const before = text.slice(0, cursor);
  const match = before.match(/@([^\s@]*)$/);
  if (!match) return null;
  const token = match[1] ?? "";
  const start = cursor - token.length - 1;
  return { query: token, start, end: cursor };
}

export function insertMention(
  text: string,
  mention: MentionState,
  memberName: string,
): { next: string; cursor: number } {
  const handle = memberName.trim().replace(/\s+/g, "");
  const insertion = `@${handle} `;
  const next = `${text.slice(0, mention.start)}${insertion}${text.slice(mention.end)}`;
  return { next, cursor: mention.start + insertion.length };
}

export function buildMentionAllText(members: { mentionLabel: string }[]): string {
  const labels = members.map((m) => `@${m.mentionLabel}`).join(" ");
  return labels ? `${labels} ` : "";
}

/** Destaca @menções no texto renderizado (partes separadas). */
export function splitMessageMentions(content: string): Array<{ type: "text" | "mention"; value: string }> {
  const parts: Array<{ type: "text" | "mention"; value: string }> = [];
  const regex = /@[\w\u00C0-\u024F]+/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(content)) !== null) {
    if (match.index > last) {
      parts.push({ type: "text", value: content.slice(last, match.index) });
    }
    parts.push({ type: "mention", value: match[0] });
    last = match.index + match[0].length;
  }
  if (last < content.length) {
    parts.push({ type: "text", value: content.slice(last) });
  }
  return parts.length ? parts : [{ type: "text", value: content }];
}
