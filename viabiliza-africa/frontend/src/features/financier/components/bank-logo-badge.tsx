"use client";

import Image from "next/image";
import { resolveBankLogo } from "@/lib/banks/bank-brand";
import type { BankBrand } from "@/lib/types/financier";
import { cn } from "@/lib/utils/cn";

export function BankLogoBadge({
  bank,
  size = "md",
  className,
}: {
  bank: BankBrand;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const logo = resolveBankLogo(bank.code, bank.logo_path);
  const box =
    size === "lg" ? "h-14 w-28" : size === "sm" ? "h-8 w-16" : "h-10 w-20";

  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-xl border border-white/20 bg-white/95 px-2 shadow-sm ring-1 ring-zinc-200/60",
        box,
        className,
      )}
      title={bank.label_pt}
    >
      {logo ? (
        <Image
          src={logo}
          alt={bank.label_pt}
          width={size === "lg" ? 100 : 72}
          height={size === "lg" ? 40 : 28}
          className="max-h-[85%] w-auto object-contain"
        />
      ) : (
        <span className="text-xs font-bold uppercase tracking-wide text-[#011636]">{bank.code}</span>
      )}
    </div>
  );
}
