"use client";

import { forwardRef, type InputHTMLAttributes } from "react";

import { Input } from "@/components/ui/input";
import { normalizeLocalPhone } from "@/lib/utils/angola-validation";

interface PhoneInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "onChange" | "value"> {
  label?: string;
  error?: string;
  value: string;
  onValueChange: (value: string) => void;
  hint?: string;
}

export const PhoneInput = forwardRef<HTMLInputElement, PhoneInputProps>(
  ({ label, error, value, onValueChange, hint, ...props }, ref) => (
    <div>
      <Input
        ref={ref}
        label={label}
        error={error}
        inputMode="numeric"
        maxLength={9}
        placeholder="9XXXXXXXX"
        value={value}
        onChange={(e) => onValueChange(normalizeLocalPhone(e.target.value))}
        {...props}
      />
      {hint ? <p className="mt-1 text-xs text-zinc-500">{hint}</p> : null}
    </div>
  ),
);
PhoneInput.displayName = "PhoneInput";
