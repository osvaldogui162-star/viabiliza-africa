const WELCOME_PENDING = "va-account-welcome-pending";
const WELCOME_SEEN = "va-account-welcome-seen";

/** Marca boas-vindas para o primeiro acesso efectivo (inclui registo com aprovação pendente). */
export function markAccountWelcomePending(): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(WELCOME_PENDING, "1");
  sessionStorage.removeItem(WELCOME_SEEN);
}

export function shouldShowAccountWelcome(urlHasWelcomeFlag: boolean): boolean {
  if (typeof window === "undefined") return urlHasWelcomeFlag;
  if (sessionStorage.getItem(WELCOME_SEEN) === "1") return false;
  return urlHasWelcomeFlag || localStorage.getItem(WELCOME_PENDING) === "1";
}

export function completeAccountWelcome(): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(WELCOME_SEEN, "1");
  localStorage.removeItem(WELCOME_PENDING);
  window.dispatchEvent(new CustomEvent("va-welcome-complete"));
}

export function isAccountWelcomePending(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(WELCOME_PENDING) === "1";
}
