/** Limpa caches de sessão que podem deixar a UI presa em estados antigos. */
export function clearAppSessionCaches() {
  if (typeof window === "undefined") return;
  const keysToRemove: string[] = [];
  for (let i = 0; i < sessionStorage.length; i += 1) {
    const key = sessionStorage.key(i);
    if (!key) continue;
    if (
      key.startsWith("va_projects_list") ||
      key.startsWith("va-chat-") ||
      key === "va-chat-panel-open" ||
      key === "va-chat-active-project"
    ) {
      keysToRemove.push(key);
    }
  }
  for (const key of keysToRemove) {
    sessionStorage.removeItem(key);
  }
}
