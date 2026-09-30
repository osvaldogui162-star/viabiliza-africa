"use client";

import type { ReactNode } from "react";
import { Check } from "lucide-react";

import { cn } from "@/lib/utils/cn";

export interface FormStep {
  id: string;
  title: string;
  description: string;
  icon: ReactNode;
}

interface FormStepperProps {
  steps: FormStep[];
  currentStep: number;
  className?: string;
}

export function FormStepper({ steps, currentStep, className }: FormStepperProps) {
  const progress = steps.length > 1 ? (currentStep / (steps.length - 1)) * 100 : 100;

  return (
    <div className={cn("w-full", className)}>
      <div className="relative mb-8 hidden md:block">
        <div className="absolute left-0 right-0 top-5 h-0.5 bg-zinc-200" />
        <div
          className="absolute left-0 top-5 h-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
        <ol className="relative flex justify-between">
          {steps.map((step, index) => {
            const done = index < currentStep;
            const active = index === currentStep;
            return (
              <li key={step.id} className="flex flex-col items-center gap-2">
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-full border-2 bg-white shadow-sm transition-all duration-300",
                    done && "border-emerald-500 bg-emerald-500 text-white",
                    active && "border-emerald-500 bg-white text-emerald-700 ring-4 ring-emerald-100",
                    !done && !active && "border-zinc-200 text-zinc-400",
                  )}
                >
                  {done ? <Check className="h-5 w-5" /> : step.icon}
                </div>
                <div className="max-w-[120px] text-center">
                  <p
                    className={cn(
                      "text-xs font-semibold",
                      active ? "text-emerald-800" : done ? "text-zinc-700" : "text-zinc-400",
                    )}
                  >
                    {step.title}
                  </p>
                  <p className="mt-0.5 hidden text-[10px] leading-tight text-zinc-400 lg:block">
                    {step.description}
                  </p>
                </div>
              </li>
            );
          })}
        </ol>
      </div>

      <div className="mb-6 md:hidden">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-medium text-emerald-800">
            Passo {currentStep + 1} de {steps.length}
          </span>
          <span className="text-zinc-500">{steps[currentStep]?.title}</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-zinc-200">
          <div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
