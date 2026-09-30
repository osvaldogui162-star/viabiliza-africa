import { BANK_LOGO_BY_CODE } from "@/lib/banks/bank-brand";

/** Alinhado a `FinancingBank` no backend (projecto + portal financiador). */
export type AngolanBankOption = {
  code: string;
  labelPt: string;
  website?: string;
};

export const ANGOLAN_BANKS: AngolanBankOption[] = [
  { code: "bfa", labelPt: "Banco de Fomento Angola (BFA)", website: "https://www.bfa.ao" },
  { code: "bai", labelPt: "Banco Angolano de Investimentos (BAI)", website: "https://www.bancobai.ao" },
  { code: "bic", labelPt: "Banco BIC", website: "https://www.bancobic.ao" },
  { code: "atl", labelPt: "Banco Millennium Atlântico (BMA)", website: "https://www.atlantico.ao" },
  { code: "sba", labelPt: "Standard Bank Angola (SBA)", website: "https://www.standardbank.co.ao" },
  { code: "bpc", labelPt: "Banco de Poupança e Crédito (BPC)", website: "https://www.bpc.ao" },
  { code: "bda", labelPt: "Banco de Desenvolvimento de Angola (BDA)", website: "https://www.bda.ao" },
  { code: "sol", labelPt: "Banco Sol", website: "https://www.bancosol.ao" },
  { code: "bni", labelPt: "Banco de Negócios Internacional (BNI)", website: "https://www.bni.ao" },
  { code: "keve", labelPt: "Banco Keve", website: "https://www.bancokeve.ao" },
  { code: "bcga", labelPt: "Banco Caixa Geral Angola (BCGA)", website: "https://www.caixaangola.ao" },
  { code: "bci", labelPt: "Banco de Comércio e Indústria (BCI)", website: "https://www.bci.ao" },
  { code: "economico", labelPt: "Banco Económico", website: "https://www.bancoeconomico.ao" },
];

export function angolanBankLogo(code: string): string | null {
  return BANK_LOGO_BY_CODE[code.toLowerCase()] ?? null;
}

export function findAngolanBank(code: string | null | undefined): AngolanBankOption | undefined {
  if (!code) return undefined;
  return ANGOLAN_BANKS.find((b) => b.code === code.toLowerCase());
}

export const ANGOLAN_BANK_CODES = ANGOLAN_BANKS.map((b) => b.code) as [string, ...string[]];
