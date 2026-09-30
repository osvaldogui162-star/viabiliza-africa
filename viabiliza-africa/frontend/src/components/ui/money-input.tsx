"use client";

import { forwardRef, useEffect, useState, type InputHTMLAttributes } from "react";

import { Input } from "@/components/ui/input";
import { formatMoneyInput, maskMoneyTyping, parseMoneyInput } from "@/lib/utils/format";

type NativeInputProps = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "type" | "value" | "onChange" | "defaultValue"
>;

export interface MoneyInputProps extends NativeInputProps {
  label?: string;
  error?: string;
  /** Valor bruto para API, ex: "1500000.5" */
  value?: string;
  /** Chamado com o valor bruto (sem formatação) */
  onValueChange?: (rawValue: string) => void;
  maxDecimals?: number;
}

/**
 * Input de valores monetários com separador de milhares (formato AO/PT).
 * Exibição: 1.500.000,50 — valor emitido: 1500000.50
 */
export const MoneyInput = forwardRef<HTMLInputElement, MoneyInputProps>(
  (
    {
      label,
      error,
      value = "",
      onValueChange,
      maxDecimals = 2,
      onBlur,
      onFocus,
      ...props
    },
    ref,
  ) => {
    const [display, setDisplay] = useState(() => formatMoneyInput(value, { maxDecimals }));
    const [focused, setFocused] = useState(false);

    useEffect(() => {
      if (!focused) {
        setDisplay(formatMoneyInput(value, { maxDecimals }));
      }
    }, [value, maxDecimals, focused]);

    return (
      <Input
        {...props}
        ref={ref}
        label={label}
        error={error}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        value={display}
        onFocus={(e) => {
          setFocused(true);
          onFocus?.(e);
        }}
        onChange={(e) => {
          const masked = maskMoneyTyping(e.target.value, maxDecimals);
          setDisplay(masked);
          onValueChange?.(parseMoneyInput(masked));
        }}
        onBlur={(e) => {
          setFocused(false);
          const raw = parseMoneyInput(display);
          const normalized = formatMoneyInput(raw, { maxDecimals });
          setDisplay(normalized);
          onValueChange?.(raw);
          onBlur?.(e);
        }}
      />
    );
  },
);
MoneyInput.displayName = "MoneyInput";
