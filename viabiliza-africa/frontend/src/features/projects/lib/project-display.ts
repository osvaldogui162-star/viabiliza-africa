/** Remove prefixo repetitivo e trunca para exibição compacta. */
export function compactProjectLabel(name: string, max = 52): string {
  const cleaned = name.replace(/^Viabilidade\s*[—–-]\s*/i, "").trim() || name;
  if (cleaned.length <= max) return cleaned;
  return `${cleaned.slice(0, max - 1).trim()}…`;
}

export function projectNamesMatch(a: string, b: string): boolean {
  const norm = (s: string) =>
    s
      .replace(/^Viabilidade\s*[—–-]\s*/i, "")
      .trim()
      .toLowerCase();
  return norm(a) === norm(b);
}
