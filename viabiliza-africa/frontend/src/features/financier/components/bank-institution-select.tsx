"use client";

import Image from "next/image";
import { Select } from "@/components/ui/select";
import { ANGOLAN_BANKS, angolanBankLogo } from "@/lib/data/angolan-banks";

type BankInstitutionSelectProps = {
  label: string;
  value: string;
  onChange: (code: string) => void;
  hint?: string;
};

export function BankInstitutionSelect({ label, value, onChange, hint }: BankInstitutionSelectProps) {
  const logo = angolanBankLogo(value);

  return (
    <div className="space-y-2">
      <Select label={label} value={value} onChange={(e) => onChange(e.target.value)}>
        {ANGOLAN_BANKS.map((bank) => (
          <option key={bank.code} value={bank.code}>
            {bank.labelPt}
          </option>
        ))}
      </Select>
      {hint ? <p className="text-xs text-zinc-500">{hint}</p> : null}
      {logo ? (
        <div className="flex items-center gap-2 rounded-lg border border-zinc-100 bg-zinc-50 px-3 py-2">
          <Image src={logo} alt="" width={64} height={28} className="h-7 w-auto object-contain" />
          <span className="text-xs text-zinc-500">{ANGOLAN_BANKS.find((b) => b.code === value)?.labelPt}</span>
        </div>
      ) : null}
    </div>
  );
}
