/** Caminhos públicos alinhados ao backend FinancingBank.logo_path */
export const BANK_LOGO_BY_CODE: Record<string, string> = {
  bfa: "/banks/bfa.svg",
  bai: "/banks/bai.svg",
  bic: "/banks/bic.svg",
  atl: "/banks/atl.png",
  sba: "/banks/sba.png",
  bpc: "/banks/bpc.png",
  bda: "/banks/bda.png",
  sol: "/banks/sol.svg",
  bni: "/banks/bni.svg",
  keve: "/banks/keve.png",
  bcga: "/banks/bcga.svg",
  bci: "/banks/bci.svg",
  economico: "/banks/economico.svg",
};

export function resolveBankLogo(code: string, fallbackPath?: string | null): string | null {
  if (fallbackPath) return fallbackPath;
  return BANK_LOGO_BY_CODE[code.toLowerCase()] ?? null;
}
